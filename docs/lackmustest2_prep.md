# Lackmustest 2 — Vorbereitung: zahlender Design-Partner

> Stand: 20.07.2026. Ziel: ein zahlender Pilotkunde, der uns 5–10 echte Aufgaben aus seinem eigenen Repo gibt. Testfragen: (1) zahlt überhaupt jemand? (2) wie lange dauert das Onboarding pro Kunde (kurz = leicht kopierbares Feature, lang = echter Burggraben)? Siehe `CLAUDE.md` Abschnitt 9.

## 1. Zielprofil (Ideal Customer Profile für den Pilot)

Nicht der spätere Idealkunde aus `CLAUDE.md` Abschnitt 7 (Compliance-getrieben, größere Firma) — für **diesen ersten Test** realistischer:

- Kleines bis mittleres Tech-Startup, kein Konzern (Einkaufsfreigabe bei großen Firmen dauert Monate)
- Nutzt bereits erkennbar KI-Coding-Agenten (Claude Code, Cursor, GitHub Copilot, Devin)
- Gründer oder Tech Lead kann selbst entscheiden, ohne Einkaufsprozess
- Muss für den Pilot NICHT compliance-getrieben sein — natürlicherer Aufhänger: Neugier ("wie zuverlässig ist mein Agent auf meinem eigenen Code wirklich?")

**Kandidat 1:** Arcium — persönlicher Kontakt vorhanden, unklar ob sie KI-Agenten nutzen, trotzdem anfragen.

**Falls das nicht klappt — Kanäle für Kaltstart bei null Netzwerk:**
- GitHub durchsuchen: Commits/PRs, die "Claude", "Copilot", "Cursor" erwähnen → zeigt echte Nutzer, keine Vermutung
- X/Twitter: Leute/Firmen, die öffentlich über Coding-Agenten-Erfahrung posten
- HackerNews "Who's hiring"-Threads: manche Postings nennen den KI-Tool-Stack
- Crypto/Web3-Startups generell: schnelllebig, viel KI-Agenten-Einsatz, Gründer direkt erreichbar (unabhängig davon, dass Truvent selbst die Krypto-Schicht zurückstellt — andere Frage als "wer sind gute Kunden")

## 2. Anfrage-Nachricht

Bewusst **ohne Preisnennung** — der Preis kommt erst im Gespräch als konkretes Pilot-Angebot, nicht in der Kaltnachricht (würde die Antwortquote killen, bevor Vertrauen da ist).

### Für Arcium (persönlicher Kontakt) — Deutsch
> Hey [Name], ich arbeite gerade an etwas, das dich interessieren könnte: Ich teste, wie zuverlässig KI-Coding-Agenten (Claude Code, Cursor usw.) auf echtem Code wirklich sind — genauer: ob die Tests, die einen Fix als "korrekt" durchwinken, überhaupt streng genug sind. An 5 Beispielaufgaben hab ich das schon durchgezogen und echte Lücken gefunden (z. B. ein Fix, der eine Sache korrekt löst, aber unbemerkt was anderes kaputt macht, das kein Test prüft). Setzt ihr bei Arcium KI-Agenten im Code ein? Falls ja, würde ich das gerne mal an ein paar echten Fällen von euch ausprobieren. Hast du 15 Min?

### For Arcium (personal contact) — English
> Hey [Name], I'm working on something that might interest you: I test how reliable AI coding agents (Claude Code, Cursor, etc.) actually are on real code — specifically, whether the tests that approve a fix as "correct" are actually strict enough. I've already run this on 5 example tasks and found real gaps (e.g. a fix that correctly solves one thing but silently breaks something else that no test catches). Does Arcium use AI agents in your codebase? If so, I'd love to try this on a few real cases from your repo. Got 15 min?

### Für Kaltakquise (kein persönlicher Kontakt) — Deutsch
> Hi, kurze Frage: Setzt ihr bei [Firma] KI-Coding-Agenten produktiv ein? Ich baue ein Tool, das prüft, ob die Tests, die einen Agenten-Fix als "korrekt" bewerten, tatsächlich streng genug sind — oder ob sie auch einen plausiblen, aber falschen Fix durchwinken würden. An 5 Testaufgaben schon nachgewiesen (Code + Ergebnisse öffentlich). Würde das gerne an ein paar echten Fällen aus eurem Repo testen. Interesse an 15 Minuten?

### For cold outreach (no personal contact) — English
> Hi, quick question: does [Company] use AI coding agents in production? I'm building a tool that checks whether the tests approving an agent's fix as "correct" are actually strict enough — or whether they'd wave through a plausible-but-wrong fix too. Already demonstrated on 5 example tasks (code + results public). Would like to try this on a few real cases from your repo. Up for 15 minutes?

## 3. Das Pilot-Angebot

**Umfang** (in etwa einer Woche machbar — das Muster ist heute schon bewiesen):

1. 5–10 echte, bereits gelöste Aufgaben aus dem eigenen Repo des Kunden (vergangene PRs/Issues — haben schon einen "Gold Patch": den echten, gemergten Fix)
2. Daraus deterministische Eval-Tasks bauen — exakt das Phase-0-Muster, nur auf ihrem statt einem öffentlichen Repo
3. QS-Gauntlet drauf (Leak-Scan + Mutationstesting) — zeigt, ob ihre eigene Testsuite dieselben Lücken hat wie die heute gefundenen (requests/pylint/sympy)
4. Optional: ein echter Coding-Agent läuft gegen ein paar dieser Aufgaben — wie gut löst er *ihren* Code wirklich?
5. Ein Bericht am Ende (Stil wie die Phase-0-Berichte): X Aufgaben zuverlässig, Y mit gefundenen Testlücken, Agenten-Performance falls getestet

**Preis:** €500–1.500 — echtes Geld (Zahlungssignal-Test bleibt bestehen), aber niedrig genug für eine Entscheidung ohne Freigabeprozess. Ausdrücklich ein **Pilot-Preis**, nicht der spätere reguläre Preis (die €1–3k/Monat-Annahme aus `CLAUDE.md` war für ein laufendes Abo, anderes Produkt).

**Während des Pilots protokollieren:** Zeit pro Aufgabe fürs Onboarding — beantwortet die zweite Lackmustest-Frage direkt.

## 4. Der Spickzettel

**1. Was wir machen (ein Satz):**
"Wir prüfen, ob ein KI-Coding-Agent ein Problem *wirklich* gelöst hat — oder ob eure eigenen Tests nur zu schwach sind, um den Unterschied zu merken."

**2. Was wir bisher bewiesen haben (konkret, nachprüfbar):**
"An 5 öffentlichen Beispielaufgaben: unsere Prüfmethode liefert bei zehn Wiederholungen zehnmal exakt dasselbe Ergebnis — und mit gezielten falschen Lösungsversuchen haben wir 3 echte Lücken in deren Testsuiten gefunden, die ein normaler Blick nicht gesehen hätte. Alles öffentlich auf GitHub."

**3. Warum das relevant ist:**
"82% der Firmen hatten laut einer aktuellen Studie in den letzten 6 Monaten einen Produktionsausfall durch KI-generierten Code. Das Problem ist nicht nur 'schreibt der Agent guten Code', sondern 'merkt ihr überhaupt, wenn er es nicht tut'."

**4. Das Angebot:**
"Ich nehme 5–10 echte, bereits gelöste Aufgaben aus eurem Repo, baue daraus denselben Test, zeige euch, wo eure Testsuite Lücken hat — für €500–1.500, fertig in etwa einer Woche."

**5. Ehrlich zum Firmenstand:**
"Wir sind wenige Wochen alt. Ich baue das mit KI-gestützter technischer Unterstützung, aber jeden Schritt verstehe und verantworte ich selbst. Deshalb ist der Pilot-Preis niedrig — ihr wärt einer unserer ersten echten Kunden."

**6. Abgrenzung zu AI-Code-Reviewern (CodeRabbit, Copilot Review, Greptile & Co.):**
"Ein AI-Code-Reviewer liest einen Diff und gibt eine *Meinung* ab — 'das sieht riskant aus'. Das ist eine subjektive Einschätzung, von einer KI erzeugt — dieselbe Art Unzuverlässigkeit wie beim Agenten selbst. Wir haben keine Meinung. Wir lassen den Code tatsächlich laufen, gegen echte Tests, in einer isolierten, wiederholbaren Umgebung, und berichten Fakten: bestanden oder nicht, zehnmal identisch. Und wir prüfen zusätzlich, ob die Tests selbst streng genug sind, um das überhaupt zu bedeuten. Vertraut nicht unserer Meinung — rechnet es selbst nach."

**7. Abgrenzung zu anderen Benchmarks (SWE-bench, Scale AI, AIUC, METR):**
"Wir behaupten nicht, eine geheime Technik zu haben — Determinismus-Prüfung und Mutationstesting sind bekanntes Handwerk. Der Unterschied ist, dass wir das konsequent auf *eurem eigenen* Code anwenden, nicht auf einem öffentlichen Leaderboard, das nichts über eure spezifische Codebasis aussagt."

**Schwierige Fragen, ehrlich beantwortet:**

| Frage | Antwort |
|---|---|
| "Warum soll ich einer neuen Firma vertrauen?" | "Genau deshalb ist der Preis niedrig und alles auf GitHub einsehbar — prüft es selbst, bevor ihr zahlt." |
| "Was macht ihr anders als eure eigene Testsuite laufen zu lassen?" | "Eure Tests sagen nur 'grün oder rot'. Wir prüfen zusätzlich, ob 'grün' überhaupt bedeutet, dass die Lösung wirklich richtig ist." |
| "Ist das nicht einfach ein besseres KI-Modell nutzen?" | "Nein — das Problem betrifft jedes Modell. Auch der beste Agent kann durch eine zu schwache Testsuite falsch validiert werden." |
| "Warum kein AI-Code-Reviewer-Tool?" | Siehe Punkt 6 oben — Meinung vs. nachrechenbare Fakten. |
| "Habt ihr das schon bei einer echten Firma gemacht?" | "Noch nicht — ihr wärt der Erste. Genau deshalb der reduzierte Pilot-Preis." |

## Referenzmaterial zum Zeigen

- Code + Git-Historie: `github.com/louisklaff-cell/Truvent` (privat, Zugriff bei Bedarf gewähren)
- Bericht Deutsch: https://claude.ai/code/artifact/95465702-56f3-4a18-a85e-65e8502d1085
- Bericht Englisch: https://claude.ai/code/artifact/ff432e0c-9aa2-4015-b796-32ce282531ac
