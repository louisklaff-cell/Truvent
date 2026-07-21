"""Phase 0, Schritt 2/4: eine Aufgabe, ein Lauf, Ergebnis parsen.

Jedes Repo hat seinen eigenen Testrunner und sein eigenes Ausgabeformat.
REPO_CONFIGS kapselt das pro Repo: wie die Testliste fuer die Kommandozeile
gebaut wird, welcher Shell-Befehl im Container laeuft, und wie die
Ausgabe zurueck in {test_id: status} geparst wird.
"""
import json
import re
import shlex
import subprocess
import sys
import uuid
from pathlib import Path

TASKS_DIR = Path(__file__).parent.parent / "tasks"

# Django: "test_count (aggregation.tests.AggregateTestCase) ... ok"
DJANGO_RESULT_LINE = re.compile(r"^(.+?) \((.+?)\) \.\.\. (ok|FAIL|ERROR)$", re.MULTILINE)
# pytest -v: "test_requests.py::RequestsTestCase::test_x PASSED [ 16%]"
# Datei-Praefix als \S* (nicht \S+): fuer Dateien ausserhalb des rootdir
# (siehe Kanarienvogel-Mechanismus) meldet pytest bei manchen Repos einen
# LEEREN Praefix ("::test_x PASSED" statt "datei.py::test_x PASSED") --
# insbesondere bei pytest-dev/pytest selbst, weil die Aufgabe pytests
# eigenes rootdir-/Pfad-Handling exerciert. Mit \S+ waere so eine Zeile
# still unter den Tisch gefallen (0 Zeichen vor "::" -> kein Match) --
# faellt zwar durch die bestehende fail-closed-Logik nicht als falsches
# "ok" auf, haette aber echte Testergebnisse verschluckt. Empirisch
# gefunden beim Kanarienvogel-Einbau, 21.07.2026.
PYTEST_RESULT_LINE = re.compile(r"^(\S*::\S+)\s+(PASSED|FAILED|ERROR)\b", re.MULTILINE)
PYTEST_STATUS_MAP = {"PASSED": "ok", "FAILED": "FAIL", "ERROR": "ERROR"}


def _django_labels(meta):
    labels = []
    for t in meta["FAIL_TO_PASS"] + meta["PASS_TO_PASS"]:
        name, cls = t.rsplit(" (", 1)
        labels.append(f"{cls.rstrip(')')}.{name}")
    return labels


# Ein Nodeid, das mehr als einmal im Output auftaucht (egal ob mit
# gleichem oder widerspruechlichem Status), ist verdaechtig -- ein echter
# Testlauf unserer Aufgaben druckt jedes Ergebnis genau einmal. Mehrfache
# Zeilen sind genau der Mechanismus, mit dem einer der beiden unabhaengigen
# Audit-Agenten eine spaete, gefaelschte "PASSED"-Zeile einschleuste (die
# alte "letzte Zeile gewinnt"-Logik haette die echte FAILED-Zeile
# ueberschrieben). TRUVENT_CONFLICT ist absichtlich kein "ok" -- faellt
# automatisch in die bestehenden fail-closed-Pfade (check/check_mutant/
# check_determinism werten alles ausser "ok" als nicht bestanden).
def _dict_with_conflict_detection(pairs):
    from collections import Counter
    counts = Counter(label for label, _ in pairs)
    return {
        label: ("TRUVENT_CONFLICT" if counts[label] > 1 else status)
        for label, status in pairs
    }


def _django_parse(output, expected):
    pairs = [(f"{cls}.{name}", status) for name, cls, status in DJANGO_RESULT_LINE.findall(output)]
    return _dict_with_conflict_detection(pairs)


def _pytest_labels(meta):
    return meta["FAIL_TO_PASS"] + meta["PASS_TO_PASS"]


def _pytest_parse(output, expected):
    pairs = [(nodeid, PYTEST_STATUS_MAP[status]) for nodeid, status in PYTEST_RESULT_LINE.findall(output)]
    return _dict_with_conflict_detection(pairs)


# sympy: "test_issue_11617 ok" -- kein Datei-/Klassenbezug im Namen selbst.
SYMPY_RESULT_LINE = re.compile(r"^(test_\S+)\s+(ok|F|E)\b", re.MULTILINE)
SYMPY_STATUS_MAP = {"ok": "ok", "F": "FAIL", "E": "ERROR"}


def _sympy_labels(meta):
    # Bare Namen, wie sie auch in FAIL_TO_PASS/PASS_TO_PASS stehen --
    # welche Datei das ist, wird separat aus test.patch ermittelt.
    return meta["FAIL_TO_PASS"] + meta["PASS_TO_PASS"]


def _sympy_parse(output, expected):
    # `python bin/test -v {test_file}` laeuft ueber die GANZE Testdatei,
    # nicht nur ueber die in FAIL_TO_PASS/PASS_TO_PASS genannten Tests --
    # anders als bei django/pytest gibt es hier keine Moeglichkeit, gezielt
    # nur einzelne Testnamen anzugeben. Ohne Filter landen zusaetzliche,
    # fuer diese Aufgabe irrelevante Tests aus derselben Datei im Ergebnis
    # (bei sympy__sympy-11618 z.B. 7 statt der erwarteten 5) -- das koennte
    # ein sonst deterministisches/korrektes Ergebnis verfaelschen, wenn
    # einer dieser fremden Tests instabil waere. Deshalb hart auf die
    # erwartete Menge filtern. Fund eines unabhaengigen Audits am 21.07.2026.
    pairs = [(name, SYMPY_STATUS_MAP[s]) for name, s in SYMPY_RESULT_LINE.findall(output)]
    parsed = _dict_with_conflict_detection(pairs)
    return {name: status for name, status in parsed.items() if name in expected}


def _files_from_patch(patch_path):
    text = patch_path.read_text()
    return re.findall(r"^diff --git a/(\S+) b/\S+", text, re.MULTILINE)


# Test-Infrastruktur, die ein Kandidaten-Patch (gold.patch/Mutant/Agenten-
# Patch) NICHT anfassen darf. Ergaenzt die bestehende W2-Absicherung (die
# nur die von test.patch selbst beruehrten Dateien nach dem Kandidaten
# zuruecksetzt) um Dateien, die Testerkennung/-ausfuehrung beeinflussen
# koennen, ohne dass test.patch sie je beruehrt -- z.B. eine neue
# conftest.py mit einem Hook, der Testergebnisse faelscht. Bewusstes
# Sperrliste statt strikter Positivliste (nur gold.patch-Dateien erlaubt):
# eine Positivliste wuerde legitime alternative Fix-Orte verbieten.
# Schliesst zwei von drei durch zwei unabhaengige Audit-Agenten gezeigten
# Angriffen (beide legten eine neue conftest.py an), NICHT den dritten
# (Manipulation direkt in einer legitim editierbaren Quelldatei) -- dafuer
# gibt es keinen kleinen Fix, siehe Claude-Memory
# truvent-oracle-isolation-research und CLAUDE.md.
#
# WICHTIG: diese Pruefung wird auf die TATSAECHLICH veraenderten Dateien
# angewendet (siehe touched_files()), NICHT mehr auf den rohen Diff-Text
# von gold.patch. Ein unabhaengiger Audit-Agent (21.07.2026) zeigte
# empirisch, dass die urspruengliche, auf _files_from_patch() (dem
# "diff --git a/... b/..."-Header) basierende Pruefung sich mit einem
# kopflosen Unified-Diff (kein "diff --git"-Header -- git apply akzeptiert
# das trotzdem) oder einer Umbenennung (nur die ALTE Seite des Headers
# wurde erkannt) umgehen liess -- eine neue conftest.py schluepfte so
# unbemerkt durch die Sperrliste und faelschte den Verdikt (FALSE_ACCEPT).
_FORBIDDEN_INFRA_PATTERNS = [
    re.compile(r"(^|/)conftest\.py$"),
    re.compile(r"(^|/)pytest\.ini$"),
    re.compile(r"(^|/)setup\.cfg$"),
    re.compile(r"(^|/)tox\.ini$"),
    re.compile(r"(^|/)pyproject\.toml$"),
    re.compile(r"(^|/)sitecustomize\.py$"),
    re.compile(r"(^|/)usercustomize\.py$"),
    re.compile(r"\.pth$"),
]


def _parse_git_status_porcelain(text):
    """Porcelain-v1-Zeilenformat: 'XY PFAD' oder bei Umbenennungen
    'XY ALT -> NEU' (die ersten 3 Zeichen sind Statuscode + Leerzeichen)."""
    files = []
    for line in text.splitlines():
        if len(line) < 4:
            continue
        rest = line[3:]
        if " -> " in rest:
            rest = rest.split(" -> ", 1)[1]
        files.append(rest.strip())
    return files


def touched_files(output, nonce):
    """Extrahiert die Liste der vom Kandidaten-Patch (gold.patch) TATSAECHLICH
    veraenderten/neu angelegten Dateien -- als VORHER/NACHHER-Differenz
    zweier `git status --porcelain --ignored --untracked-files=all`-
    Aufnahmen (siehe _apply_patches_cmd(): einmal vor, einmal direkt nach
    dem Anwenden von gold.patch). Gibt None zurueck, wenn eines der vier
    Marker-Paare fehlt -- z.B. weil schon das Anwenden von gold.patch
    scheiterte, bevor die zweite Aufnahme je lief.

    `nonce` MUSS derselbe (pro Aufruf zufaellig erzeugte) Wert sein, mit
    dem _apply_patches_cmd() die Marker fuer GENAU DIESEN Container-Lauf
    gebaut hat (siehe dort fuer den Grund: Marker-Injection-Fund eines
    unabhaengigen Audits, 22.07.2026).

    WICHTIG, zwei weitere Gruende fuer --ignored und den Vorher/Nachher-
    Vergleich statt einer einzigen Aufnahme (Fund eines unabhaengigen
    Audits, 21.07.2026): (1) `git status --porcelain` OHNE --ignored
    uebersieht per .gitignore ignorierte Dateien komplett -- ein
    Kandidaten-Patch konnte in EINEM Schritt .gitignore um "conftest.py"
    erweitern UND eine bösartige conftest.py anlegen; pytest laedt eine
    Projektstamm-conftest.py trotzdem automatisch, unsere Pruefung sah
    sie aber nie. (2) --untracked-files=all verhindert, dass eine ganz
    NEUE Unterverzeichnis-Struktur zu einer einzigen kollabierten Zeile
    ("neuerordner/" statt der einzelnen Dateien darin) zusammengefasst
    wird. Der Vorher/Nachher-Vergleich (statt einfach --ignored auf eine
    einzelne Aufnahme draufzusetzen) verhindert, dass bereits im Image
    vorhandener Muell (__pycache__/*.pyc, *.egg-info/, die bei JEDER
    Aufgabe vorkommen) faelschlich als "vom Kandidaten beruehrt" gilt --
    nur was NEU zwischen den beiden Aufnahmen erscheint, zaehlt."""
    baseline_start, baseline_end, touched_start, touched_end, _ = _marker_strings(nonce)
    markers = (baseline_start, baseline_end, touched_start, touched_end)
    if not all(m in output for m in markers):
        return None
    baseline_section = output.split(baseline_start, 1)[1].split(baseline_end, 1)[0]
    after_section = output.split(touched_start, 1)[1].split(touched_end, 1)[0]
    baseline_lines = set(l for l in baseline_section.splitlines() if l.strip())
    after_lines = [l for l in after_section.splitlines() if l.strip()]
    new_lines = [l for l in after_lines if l not in baseline_lines]
    return _parse_git_status_porcelain("\n".join(new_lines))


def forbidden_infra_files(candidate_files, exempt=()):
    """exempt: Dateien, die der ECHTE Gold-Patch dieser Aufgabe selbst
    beruehrt -- z.B. braucht der echte pylint-Fix legitim setup.cfg (fuegt
    die appdirs-Abhaengigkeit hinzu). Eine reine Positivliste waere zu
    starr; stattdessen wird nur verboten, was der bekannte, echte Fix
    dieser Aufgabe NIE braucht."""
    return [
        f for f in candidate_files
        if f not in exempt and any(p.search(f) for p in _FORBIDDEN_INFRA_PATTERNS)
    ]


def _test_file_from_patch(task_dir):
    """sympys FAIL_TO_PASS/PASS_TO_PASS nennen keine Datei -- wir nehmen die
    Datei, die test.patch selbst aendert (dort werden die Tests definiert)."""
    return _files_from_patch(task_dir / "test.patch")[0]


# TRUVENT_APPLY_OK ist ein Marker, kein Fehlertext-Rateversuch: Wir pruefen
# spaeter nur, ob diese Zeile in der Ausgabe steht, statt bekannte
# git-apply-Fehlermeldungen zu erraten (die je nach git-Version/Locale/
# Fehlerart variieren koennen). Fehlt der Marker, ist EGAL welcher Fehler
# beim Patchen aufgetreten ist -- der Patch hat nicht angewendet.
#
# Reihenfolge bewusst: KANDIDAT zuerst (gold.patch -- das kann auch ein
# Mutant oder ein Agenten-Patch sein), DANACH werden genau die Dateien,
# die test.patch aendert, per `git checkout --` hart auf den base_commit-
# Stand zurueckgesetzt, BEVOR test.patch frisch angewendet wird. Grund:
# ein Kandidaten-Patch koennte -- versehentlich oder absichtlich -- die
# Testdatei selbst mit anfassen (z.B. eine Assertion abschwaechen oder
# einen Test loeschen) und so die eigentliche Pruefung aushebeln. Mit der
# alten Reihenfolge (test.patch zuerst, Kandidat danach) haette so eine
# Aenderung ueberlebt, weil sie NACH test.patch kam und nichts sie mehr
# zurueckgesetzt haette. Fund eines unabhaengigen Audits am 21.07.2026.
# Fuer alle 4 aktuellen Aufgaben aendert das am Erfolgspfad nichts: dort
# ruehren gold.patch und test.patch ohnehin komplett unterschiedliche
# Dateien an (gepr. Quellcode vs. Testdatei), git-apply-Kontextzeilen
# haengen nicht von der Reihenfolge ab, wenn die Dateien disjunkt sind.
# _TOUCHED_FILES_START/_END umschliessen die `git status --porcelain`-
# Ausgabe UNMITTELBAR nach dem Anwenden von gold.patch (dem Kandidaten) --
# das ist die Dateisystem-WAHRHEIT darueber, was der Kandidat tatsaechlich
# veraendert/angelegt hat, unabhaengig vom Diff-Format (siehe
# forbidden_infra_files()-Kommentar oben). Wird fuer JEDEN Lauf mit
# eingebettet (auch run_once() fuer den vertrauenswuerdigen Gold-Patch) --
# ein paar zusaetzliche Zeilen Ausgabe, aber einheitliche Logik statt
# zwei verschiedene Codepfade.
#
# KRITISCH, per NONCE statt fester Strings (Fund eines unabhaengigen
# Audits, 22.07.2026): die Marker standen zuvor als FESTE, dem Angreifer
# im Voraus bekannte Zeichenketten im selben Textstrom wie die vom
# Kandidaten-Patch kontrollierten Dateinamen (aus `git status`). Ein
# Kandidat konnte einfach eine Datei anlegen, die GENAU SO HEISST wie ein
# Marker (z.B. "TRUVENT_TOUCHED_FILES_END") -- beim Heraustrennen des
# Textes (`output.split(marker, 1)`) wurde dann am DATEINAMEN statt am
# echten, spaeter echoten Marker geschnitten, die erkannte Dateiliste
# wurde leer, und `forbidden_infra_files()` sah nichts mehr. Verifiziert:
# eine bösartige conftest.py + diese eine leere Trick-Datei ergab einen
# echten FALSE_ACCEPT trotz ungefixtem Bug. Fix: jeder Marker bekommt
# einen pro Lauf FRISCH ZUFAELLIG erzeugten Anhang (`uuid.uuid4().hex`,
# kryptografisch sicher via os.urandom) -- der Kandidaten-Patch wird
# OFFLINE geschrieben, BEVOR der Nonce ueberhaupt existiert, kann also
# unmoeglich eine passende Datei vorbereiten. Betrifft auch TRUVENT_APPLY_OK
# (dieselbe Schwaeche, separat gefunden) -- deshalb ebenfalls genoncet.
def _marker_strings(nonce):
    return (
        f"TRUVENT_BASELINE_STATUS_START_{nonce}",
        f"TRUVENT_BASELINE_STATUS_END_{nonce}",
        f"TRUVENT_TOUCHED_FILES_START_{nonce}",
        f"TRUVENT_TOUCHED_FILES_END_{nonce}",
        f"TRUVENT_APPLY_OK_{nonce}",
    )


def new_nonce():
    return uuid.uuid4().hex


# --ignored --untracked-files=all: siehe touched_files()-Docstring fuer
# den Grund (sonst uebersehene .gitignore'te Dateien / kollabierte
# Unterverzeichnisse).
_STATUS_CMD = "git status --porcelain --ignored --untracked-files=all"


def _apply_patches_cmd(nonce):
    """Enthaelt absichtlich noch das unaufgeloeste "{restore_cmd}" --
    wird zusammen mit labels/test_file in EINEM finalen .format()-Aufruf
    in render_inner_cmd() ersetzt. Wuerde restore_cmd HIER schon per
    .format() eingesetzt, wuerden literale geschweifte Klammern in seinem
    WERT nicht mehr als Platzhalter erkannt (Python formatiert eingesetzte
    Werte nicht rekursiv) -- deshalb bewusst nur String-Verkettung hier,
    kein .format()."""
    baseline_start, baseline_end, touched_start, touched_end, apply_ok = _marker_strings(nonce)
    return (
        "cd /testbed && "
        f"echo {baseline_start} && {_STATUS_CMD} && echo {baseline_end} && "
        "git apply /patches/gold.patch && "
        f"echo {touched_start} && {_STATUS_CMD} && echo {touched_end} && "
        "{restore_cmd} && "
        f"git apply /patches/test.patch && echo {apply_ok}"
    )


_ACTIVATE = "source /opt/miniconda3/etc/profile.d/conda.sh && conda activate testbed"

# Kanarienvogel: feste, immer mitgefuehrte Zusatztests (scripts/
# truvent_canary_test.py), die grobe/undifferenzierte Manipulation der
# Testauswertung erkennen (z.B. eine testsuite-weite assertTrue-
# Neutralisierung) -- NICHT einen gezielten Angriff auf den bekannten
# Zielnamen, siehe Modul-Docstring der Datei selbst und Claude-Memory
# truvent-oracle-isolation-research. Nur fuer pytest-basierte Repos
# umgesetzt (django/sympy haben eigene Testrunner ohne einfache
# Moeglichkeit, eine zusaetzliche Datei generisch einzubinden -- bewusste,
# dokumentierte Einschraenkung).
_CANARY_FILE = Path(__file__).parent / "truvent_canary_test.py"
_CANARY_MOUNT_PATH = "/truvent_canary/truvent_canary_test.py"
# Nur das Suffix nach dem Datei-Pfad wird geprueft, nicht der volle
# Nodeid: der Pfad-Teil, den pytest fuer eine ausserhalb von /testbed
# gemountete Datei meldet, variiert je nach Repo (empirisch festgestellt,
# 21.07.2026 -- pytest-dev/pytest selbst, weil es sein EIGENES rootdir-/
# Pfad-Handling exerciert, meldet z.B. "::TruventCanary::..." ganz ohne
# Pfad-Praefix, waehrend andere Repos "../truvent_canary/....py::...
# TruventCanary::..." melden). Ein Suffix-Vergleich ist robust gegen
# diese Repo-Eigenheiten, ohne die Sicherheit zu schwaechen -- die
# Klassen-/Funktionsnamen selbst sind fest und eindeutig.
_CANARY_EXPECTED_SUFFIXES = {
    "TruventCanary::test_truvent_canary_must_pass": "ok",
    "TruventCanary::test_truvent_canary_must_fail": "not_ok",
    "test_truvent_canary_bare_must_pass": "ok",
    "test_truvent_canary_bare_must_fail": "not_ok",
}
_CANARY_SUPPORTED_REPOS = {"psf/requests", "pylint-dev/pylint", "pytest-dev/pytest"}


def canary_violation(actual, repo):
    """Prueft, ob die vier festen Kanarienvogel-Tests wie erwartet
    ausgefallen sind. Gibt bei Verletzung eine kurze Beschreibung zurueck,
    sonst None. Repos ausserhalb von _CANARY_SUPPORTED_REPOS werden nicht
    geprueft (kein Kanarienvogel mitgefuehrt)."""
    if repo not in _CANARY_SUPPORTED_REPOS:
        return None
    for suffix, expected_status in _CANARY_EXPECTED_SUFFIXES.items():
        matches = [status for nodeid, status in actual.items() if nodeid.endswith(suffix)]
        if not matches:
            return f"Kanarienvogel '{suffix}' fehlt in der Ausgabe"
        status = matches[0]
        if expected_status == "ok" and status != "ok":
            return f"Kanarienvogel '{suffix}' sollte bestehen, war aber {status!r}"
        if expected_status == "not_ok" and status == "ok":
            return f"Kanarienvogel '{suffix}' sollte fehlschlagen, war aber 'ok'"
    return None


# -p no:randomly / -p no:xdist erzwingen feste Reihenfolge und keine
# Parallelitaet, AUCH wenn das Zielrepo diese Plugins selbst per
# pytest.ini/setup.cfg (addopts) aktiviert haette -- ohne diesen Zwang
# wuerden wir uns nur darauf verlassen, dass kein Repo das tut. Sicher
# auch wenn die Plugins gar nicht installiert sind (pytest ignoriert
# "no:X" fuer nicht registrierte Plugins).
#
# -o addopts=<TRUSTED_WERT>: ueberschreibt die "addopts"-Zeile aus
# setup.cfg/pytest.ini/pyproject.toml mit einem FEST HINTERLEGTEN,
# vertrauenswuerdigen Wert -- NIEMALS mit dem, was aktuell in der
# (moeglicherweise vom Kandidaten veraenderten) Datei steht. Grund (Fund
# eines unabhaengigen Audits, 21.07.2026): setup.cfg/pyproject.toml/
# tox.ini stehen zwar auf der Sperrliste (forbidden_infra_files), aber
# die AUSNAHME fuer Dateien, die der ECHTE Gold-Patch legitim beruehrt
# (z.B. pylints echter Fix aendert setup.cfg), oeffnet einen Seitenkanal:
# ein Kandidat darf setup.cfg aendern und dort per
# `addopts = -p evilplugin` ein beliebiges neues Python-Modul als
# pytest-Plugin registrieren -- das neue Modul selbst (z.B. evilplugin.py)
# steht auf KEINER Sperrliste (waere sonst zu restriktiv fuer legitime
# neue Hilfsdateien eines Agenten-Fixes). Das Plugin kann dann gezielt
# nur das eine bekannte Testergebnis faelschen (Kanarienvogel sieht
# nichts). Ein einfaches `-o addopts=` (LEER) haette pytest-dev/pytest
# selbst kaputt gemacht -- diese Aufgabe braucht legitim `-p pytester`
# aus ihrer eigenen pyproject.toml (das eigene "pytester"-Plugin, das
# pytest zum Testen von SICH SELBST mitbringt). Deshalb: pro Repo der
# TATSAECHLICHE, zum Zeitpunkt der Aufgaben-Erstellung geprueft-
# vertrauenswuerdige Ausgangswert (siehe _TRUSTED_ADDOPTS), hart codiert,
# NICHT zur Laufzeit aus der (potenziell manipulierten) Datei gelesen.
# Verifiziert: ohne Fix FALSE_ACCEPT trotz ungefixtem Bug, mit Fix korrekt
# abgelehnt, UND pytest-dev/pytest laeuft weiterhin fehlerfrei.
_TRUSTED_ADDOPTS = {
    "psf/requests": "",
    "pylint-dev/pylint": '-m "not acceptance"',
    "pytest-dev/pytest": "-rfEX -p pytester --strict-markers",
}


def _pytest_cmd(repo):
    addopts_flag = shlex.quote(f"addopts={_TRUSTED_ADDOPTS.get(repo, '')}")
    return (
        f"pytest -o {addopts_flag} -p no:randomly -p no:xdist -p no:cacheprovider "
        f"{{labels}} {_CANARY_MOUNT_PATH} -v"
    )

# "test_cmd" ist NUR der Teil NACH _apply_patches_cmd()+_ACTIVATE -- der
# volle Befehl wird erst in render_inner_cmd() pro Aufruf zusammengebaut,
# weil _apply_patches_cmd() jetzt einen pro Lauf FRISCHEN Nonce braucht
# (siehe _marker_strings()-Kommentar) und deshalb nicht mehr einmalig
# beim Modul-Laden fest eingebacken werden kann.
REPO_CONFIGS = {
    "django/django": {
        "labels": _django_labels,
        "parse": _django_parse,
        "test_cmd": "python tests/runtests.py --settings=test_sqlite --parallel 1 -v 2 {labels}",
    },
    "psf/requests": {
        "labels": _pytest_labels,
        "parse": _pytest_parse,
        "test_cmd": _pytest_cmd("psf/requests"),
    },
    "pylint-dev/pylint": {
        "labels": _pytest_labels,
        "parse": _pytest_parse,
        "test_cmd": _pytest_cmd("pylint-dev/pylint"),
    },
    "pytest-dev/pytest": {
        "labels": _pytest_labels,
        "parse": _pytest_parse,
        "test_cmd": _pytest_cmd("pytest-dev/pytest"),
    },
    "sympy/sympy": {
        "labels": _sympy_labels,
        "parse": _sympy_parse,
        # --no-subprocess: bin/test startet sonst einen Subprozess, der
        # Hash-Randomisierung wieder aktivieren kann -- widerspricht unserem
        # PYTHONHASHSEED=0-Pin.
        "test_cmd": "python bin/test --no-subprocess -v {test_file}",
    },
}

# Instanzen, deren offizielles SWE-bench-Image eine fehlende Abhaengigkeit
# hatte. Einmalig lokal gefixt (siehe git-Commit-Message) und als eigenes
# Image commited -- entspricht dem Pin "Image einmal bauen, dann nur laufen
# lassen" aus phase0.md.
IMAGE_OVERRIDES = {
    "pylint-dev__pylint-4661": "truvent/sweb.eval.x86_64.pylint-dev_1776_pylint-4661.fixed",
}

# Digest-Pins: garantieren ein WIRKLICH unveraenderliches Image. Der
# :latest-Tag allein reicht nicht -- wuerde der Anbieter (oder wir selbst,
# lokal) das Tag jemals neu veroeffentlichen, wuerden wir stillschweigend
# ein anderes Image bekommen, ohne es zu merken. Digest ermittelt via
# `docker images --digests`. Fehlt ein Eintrag hier (z.B. bei neuen
# Aufgaben), faellt image_name() auf :latest zurueck -- das Fehlen wird
# absichtlich sichtbar geloggt, nicht stillschweigend akzeptiert.
IMAGE_DIGESTS = {
    "django__django-10880": "sha256:dee440908552bf57c2d43c0bc83b244c37488b9b6ef6ef45df5733760aae74e1",
    "psf__requests-1142": "sha256:9b0b13a4a762e809a60424f8fd9ba40b45f87874de87479a771e4e673f937d59",
    "pylint-dev__pylint-4661": "sha256:7efff2a21c38735b8dee7780701e45b27a81208cc108dc536a208d4062295661",  # neu gebaut mit appdirs==1.4.4 gepinnt (W1-Fix, 21.07.2026)
    "pytest-dev__pytest-10051": "sha256:46de1ca632c3caa994438bb74a500fe78f9aa05c1cc7e8becba34f98d785fd7c",
    "sympy__sympy-11618": "sha256:12f3a6f64bb8ca17304839d3d5ca69b00e1e8d0b9034b72bb773b374e80d4307",
}


def load_meta(instance_id):
    with open(TASKS_DIR / instance_id / "meta.json") as f:
        return json.load(f)


def image_name(instance_id):
    base = IMAGE_OVERRIDES.get(instance_id)
    if base is None:
        suffix = instance_id.replace("__", "_1776_")
        base = f"swebench/sweb.eval.x86_64.{suffix}"

    digest = IMAGE_DIGESTS.get(instance_id)
    if digest is None:
        print(f"WARNUNG: kein Digest-Pin fuer {instance_id} -- falle auf :latest zurueck (nicht garantiert unveraenderlich)", file=sys.stderr)
        return f"{base}:latest"
    return f"{base}@{digest}"


def expected_labels(meta):
    return REPO_CONFIGS[meta["repo"]]["labels"](meta)


def parse_results(output, meta):
    expected = set(expected_labels(meta))
    return REPO_CONFIGS[meta["repo"]]["parse"](output, expected)


def render_inner_cmd(meta, labels, test_file, restore_files, nonce):
    """Baut den Shell-Befehl aus repo-spezifischem Template + Testnamen/
    Dateipfad zusammen -- mit shlex.quote() pro Wert, nicht durch simple
    String-Interpolation. Testnamen und Dateipfad stammen aus test.patch/
    meta.json, die zwar aktuell nur unsere eigenen kuratierten SWE-bench-
    Daten sind, aber sobald echter Agenten- oder Kundencode verarbeitet
    wird (Lackmustest 2+), koennten darin Shell-Metazeichen stecken --
    ohne Escaping waere das eine Command-Injection-Luecke innerhalb des
    Containers (durch --network none zwar eingedaemmt, aber trotzdem ein
    echtes Risiko, kein hypothetisches).

    nonce: pro Aufruf frisch erzeugter Zufallswert (siehe new_nonce()),
    macht die _apply_patches_cmd()-Marker fuer den Kandidaten-Patch nicht
    vorhersagbar (siehe dortiger Kommentar).

    restore_files: die Dateien, die test.patch aendert -- werden nach dem
    Kandidaten-Patch per `git checkout <base_commit> --` zurueckgesetzt
    (siehe _apply_patches_cmd()), damit ein Kandidaten-Patch die Testdatei
    nicht manipulieren kann. Leere Liste -> "true" (No-Op), statt ein
    `git checkout --` ohne Pfade abzusetzen (das waere ein Fehler).

    WICHTIG: explizit `git checkout meta["base_commit"] -- DATEI`, NICHT
    das bare `git checkout -- DATEI` (das implizit von der INDEX-/HEAD-
    Version restauriert, nicht zwingend von base_commit). Fund eines
    unabhaengigen Audits (22.07.2026): meta.json fuehrt einen
    `base_commit`-Wert, den zuvor KEIN Skript je auslas -- die Restore-
    Logik verliess sich stillschweigend darauf, dass der Image-HEAD
    inhaltlich mit base_commit uebereinstimmt (was fuer alle 5 aktuellen
    Aufgaben zufaellig stimmt: SWE-bench haengt in der Regel noch einen
    eigenen Scaffolding-Commit an, der aber bei unseren Aufgaben keine
    Testdatei beruehrt). Ohne diesen Fix haette ein zukuenftiges Image
    (oder eine Kunden-Umgebung), dessen HEAD von base_commit abweicht,
    STILL die falsche Baseline wiederhergestellt -- ohne Fehlermeldung.
    Jetzt ist base_commit die einzige Quelle der Wahrheit, unabhaengig
    vom Ambient-Zustand des Images.

    Pro Datei einzeln mit Fallback statt eines einzigen `git checkout --
    f1 f2 f3`: falls test.patch eine NEUE Testdatei anlegt (die es im
    base_commit noch nicht gibt), schlaegt `git checkout` fuer genau
    diese Datei fehl ("did not match any file(s)") und haette wegen der
    "&&"-Verkettung die GESAMTE Kette abgebrochen -- ein gueltiger
    Kandidaten-Patch waere faelschlich als MUTANT_UNGUELTIG gewertet
    worden. Kein Sicherheitsloch (Fail-Richtung ist zu restriktiv, nicht
    zu freizuegig), aber ein Korrektheitsfehler, der bei echten SWE-bench-
    Aufgaben mit neu angelegten Testdateien (in Phase 1 haeufig) zuschlagen
    wuerde -- unsere aktuellen 5 Aufgaben aendern alle nur bestehende
    Testdateien, daher bisher nicht aufgefallen. Fund eines unabhaengigen
    Audits, 21.07.2026. Fallback: existiert die Datei nicht im base_commit,
    wird sie stattdessen geloescht (rm -f) -- test.patch legt sie danach
    frisch an."""
    config = REPO_CONFIGS[meta["repo"]]
    quoted_labels = " ".join(shlex.quote(l) for l in labels)
    quoted_test_file = shlex.quote(test_file) if test_file else ""
    quoted_base_commit = shlex.quote(meta["base_commit"])
    if restore_files:
        per_file = " && ".join(
            f"( git checkout {quoted_base_commit} -- {shlex.quote(f)} 2>/dev/null || rm -f {shlex.quote(f)} )"
            for f in restore_files
        )
        restore_cmd = per_file
    else:
        restore_cmd = "true"
    # _apply_patches_cmd(nonce) enthaelt noch das unaufgeloeste
    # "{restore_cmd}" -- wird HIER, zusammen mit labels/test_file, in
    # einem einzigen .format()-Aufruf auf der VOLLSTAENDIGEN Befehlskette
    # ersetzt (nicht vorher separat), siehe _apply_patches_cmd()-Docstring.
    full_template = f"{_apply_patches_cmd(nonce)} && {_ACTIVATE} && {config['test_cmd']}"
    return full_template.format(
        labels=quoted_labels, test_file=quoted_test_file, restore_cmd=restore_cmd
    )


# Sandbox-Haertung: wir fuehren fremden, nicht vertrauenswuerdigen Code
# aus (KI-Agenten-Patches, spaeter Kundencode in Lackmustest 2+) --
# --network none allein reicht nicht. Getestet, dass unsere Aufgaben
# damit weiterhin fehlerfrei laufen (identisches Ergebnis wie ohne):
#   --pids-limit: verhindert Fork-Bomben
#   --memory/--memory-swap: verhindert Speicher-Erschoepfung
#   --cap-drop ALL: entzieht alle Linux-Capabilities, die git/python
#     /pytest fuer normalen Betrieb nicht brauchen
#   --security-opt no-new-privileges: verhindert Rechteausweitung
#     ueber setuid-Binaries im Image
#   --cpus: verhindert, dass ein Kandidaten-Patch die volle Host-CPU
#     fuer die gesamte Timeout-Dauer blockiert (Fund eines unabhaengigen
#     Audits, 21.07.2026). 2 Kerne reichen fuer unsere Testsuiten reichlich;
#     getestet, dass alle 4 Aufgaben damit weiterhin identisch/fehlerfrei
#     laufen.
HARDENING_FLAGS = [
    "--pids-limit", "512",
    "--memory", "2g",
    "--memory-swap", "2g",
    "--cpus", "2",
    "--cap-drop", "ALL",
    "--security-opt", "no-new-privileges",
]


# Deckel gegen Host-Speicher-Erschoepfung: ein boesartiger Kandidaten-
# Patch koennte versuchen, den Host mit unbegrenzter Ausgabe zu fluten --
# verifizierter Fund eines unabhaengigen Audit-Agenten (21.07.2026): 150MB
# Ausgabe in < 1s liess den Host-Python-Prozess auf 533MB RSS springen,
# --memory in HARDENING_FLAGS begrenzt nur den CONTAINER, nicht den
# Host-seitigen Pipe-Puffer, den subprocess.run() haelt. Der Deckel wird
# INNERHALB des Containers per `head -c` durchgesetzt (ganzer Befehl in
# eine Subshell gepackt, damit die Begrenzung fuer die GESAMTE Kette
# gilt, nicht nur den letzten Teilbefehl) -- so muss der Host nie mehr
# als _MAX_OUTPUT_BYTES puffern, unabhaengig davon, wie viel der
# Container intern produziert.
_MAX_OUTPUT_BYTES = 80 * 1024 * 1024  # 80 MB


def run_docker_with_cleanup(docker_cmd, timeout=300):
    """Fuehrt einen `docker run --rm ...`-Befehl aus, mit garantiertem
    Aufraeumen bei Timeout. --rm allein reicht nicht: killt Python den
    docker-CLI-Prozess bei Ablauf des Timeouts (subprocess.run sendet
    SIGKILL), kann der Container selbst verwaist im Hintergrund weiter-
    laufen, weil --rm nur beim Container-Ende greift, nicht beim Tod
    des CLI-Clients. Deshalb: expliziter Name + aktives `docker kill`
    bei Timeout, statt eine unbehandelte Exception hochzureichen.

    Erwartet docker_cmd im Format
    ["docker", "run", "--rm", ...rest, "bash", "-c", inner_cmd] --
    die letzten drei Elemente werden fuer den Ausgabe-Deckel umgebaut.
    """
    container_name = f"truvent-{uuid.uuid4().hex[:12]}"
    capped_inner_cmd = f"({docker_cmd[-1]}) 2>&1 | head -c {_MAX_OUTPUT_BYTES}"
    docker_cmd = docker_cmd[:-1] + [capped_inner_cmd]
    full_cmd = docker_cmd[:3] + ["--name", container_name] + HARDENING_FLAGS + docker_cmd[3:]
    try:
        # text=False + explizites Decodieren mit errors="replace" statt
        # subprocess.run(text=True) (strenges UTF-8, wirft bei ungueltigen
        # Bytes eine unabgefangene UnicodeDecodeError): der Byte-Deckel
        # oben (head -c) kann ein Mehrbyte-UTF-8-Zeichen genau am Schnitt
        # zerteilen, UND ein boesartiger Kandidaten-Patch kann absichtlich
        # ungueltige Bytes ausgeben -- beides fuehrte vorher zu einem
        # Absturz, der einen ganzen Batch (check_determinism/
        # reverify_agent_patches/run_agent_harness) abbrechen konnte.
        # errors="replace" ist deterministisch (dieselben Bytes -> dieselben
        # U+FFFD-Ersetzungen) und unschaedlich, weil alle geparsten
        # Ergebniszeilen ohnehin reines ASCII sind. Fund eines unabhaengigen
        # Audits, 21.07.2026.
        result = subprocess.run(full_cmd, capture_output=True, timeout=timeout)
        output = (
            result.stdout.decode("utf-8", errors="replace")
            + result.stderr.decode("utf-8", errors="replace")
        )
        if len(output.encode("utf-8", errors="ignore")) >= _MAX_OUTPUT_BYTES:
            return (
                f"TRUVENT_OUTPUT_OVERFLOW: Ausgabe erreichte den Deckel von "
                f"{_MAX_OUTPUT_BYTES} Bytes, vermutlich abgeschnitten (Name: {container_name})"
            )
        return output
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "kill", container_name], capture_output=True, timeout=30)
        return f"TRUVENT_TIMEOUT: Container nach {timeout}s abgebrochen und aufgeraeumt (Name: {container_name})"


def run_once(instance_id):
    meta = load_meta(instance_id)
    task_dir = TASKS_DIR / instance_id
    labels = expected_labels(meta)
    test_file = _test_file_from_patch(task_dir)
    restore_files = _files_from_patch(task_dir / "test.patch")
    # Keine Sperrlisten-Pruefung hier: run_once()/check() verifizieren den
    # ECHTEN, vertrauenswuerdigen Gold-Patch dieser Aufgabe selbst -- die
    # Sperrliste (forbidden_infra_files) schuetzt gegen MUTANTEN/Agenten-
    # Patches in mutation_test.py, wo der Kandidat nicht vertrauenswuerdig
    # ist. Der Nonce wird trotzdem gebraucht, weil _apply_patches_cmd()
    # jetzt immer einen verlangt -- touched_files()/TRUVENT_APPLY_OK
    # werden hier aber nicht ausgewertet.
    nonce = new_nonce()
    inner_cmd = render_inner_cmd(meta, labels, test_file, restore_files, nonce)

    docker_cmd = [
        "docker", "run", "--rm",
        "--platform", "linux/amd64",
        "--network", "none",
        "-e", "PYTHONHASHSEED=0",
        "-e", "PYTHONIOENCODING=UTF-8",
        "-e", "LC_ALL=C.UTF-8",
        "-e", "LANG=C.UTF-8",
        "-e", "TZ=UTC",
        "-e", "OMP_NUM_THREADS=1",
        "-e", "OPENBLAS_NUM_THREADS=1",
        "-e", "MKL_NUM_THREADS=1",
        "-v", f"{task_dir.resolve()}:/patches:ro",
    ]
    if meta["repo"] in _CANARY_SUPPORTED_REPOS:
        docker_cmd += ["-v", f"{_CANARY_FILE.resolve()}:{_CANARY_MOUNT_PATH}:ro"]
    docker_cmd += [
        image_name(instance_id),
        "bash", "-c", inner_cmd,
    ]

    output = run_docker_with_cleanup(docker_cmd, timeout=300)
    return output, meta


def check(instance_id):
    output, meta = run_once(instance_id)
    expected = expected_labels(meta)
    actual = parse_results(output, meta)

    violation = canary_violation(actual, meta["repo"])
    if violation:
        print(f"{instance_id}: KANARIENVOGEL VERLETZT -- {violation}")
        return False

    missing = [l for l in expected if l not in actual]
    failed = [l for l in expected if actual.get(l) not in (None, "ok")]

    print(f"{instance_id}: {len(actual)} Tests erfasst, {len(expected)} erwartet")
    if missing:
        print(f"  FEHLEND (kein Ergebnis geparst): {missing}")
    if failed:
        print(f"  FEHLGESCHLAGEN: {[(l, actual[l]) for l in failed]}")
    if not missing and not failed:
        print("  ALLE TESTS OK")
    return not missing and not failed


if __name__ == "__main__":
    instance_id = sys.argv[1] if len(sys.argv) > 1 else "django__django-10880"
    ok = check(instance_id)
    sys.exit(0 if ok else 1)
