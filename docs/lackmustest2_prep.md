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
> Hey [Name], ich arbeite gerade an etwas, das dich interessieren könnte: Ich teste, wie zuverlässig KI-Coding-Agenten (Claude Code, Cursor usw.) auf echtem Code wirklich sind — genauer: ob die Tests, die einen Fix als "korrekt" durchwinken, überhaupt streng genug sind. An 4 Beispielaufgaben hab ich das schon durchgezogen und echte Lücken gefunden (z. B. ein Fix, der eine Sache korrekt löst, aber unbemerkt was anderes kaputt macht, das kein Test prüft). Setzt ihr bei Arcium KI-Agenten im Code ein? Falls ja, würde ich das gerne mal an ein paar echten Fällen von euch ausprobieren. Hast du 15 Min?

### For Arcium (personal contact) — English
> Hey [Name], I'm working on something that might interest you: I test how reliable AI coding agents (Claude Code, Cursor, etc.) actually are on real code — specifically, whether the tests that approve a fix as "correct" are actually strict enough. I've already run this on 4 example tasks and found real gaps (e.g. a fix that correctly solves one thing but silently breaks something else that no test catches). Does Arcium use AI agents in your codebase? If so, I'd love to try this on a few real cases from your repo. Got 15 min?

### Für Kaltakquise (kein persönlicher Kontakt) — Deutsch
> Hi, kurze Frage: Setzt ihr bei [Firma] KI-Coding-Agenten produktiv ein? Ich baue ein Tool, das prüft, ob die Tests, die einen Agenten-Fix als "korrekt" bewerten, tatsächlich streng genug sind — oder ob sie auch einen plausiblen, aber falschen Fix durchwinken würden. An 4 Testaufgaben schon nachgewiesen (Code + Ergebnisse öffentlich). Würde das gerne an ein paar echten Fällen aus eurem Repo testen. Interesse an 15 Minuten?

### For cold outreach (no personal contact) — English
> Hi, quick question: does [Company] use AI coding agents in production? I'm building a tool that checks whether the tests approving an agent's fix as "correct" are actually strict enough — or whether they'd wave through a plausible-but-wrong fix too. Already demonstrated on 4 example tasks (code + results public). Would like to try this on a few real cases from your repo. Up for 15 minutes?

## 3. Das Pilot-Angebot

**Wichtig — Reihenfolge der Formulierung:** Nicht mit dem Aufwand für den Kunden anfangen ("schickt uns eure alten Bugs"), sondern mit dem **Ergebnis, das sie bekommen**. Die alten, gelösten Aufgaben sind nur das Rohmaterial, das wir technisch brauchen — nicht der Wert für sie. Der Wert:

1. **Ein Härtetest ihrer eigenen Testsuite, unabhängig von jedem Agenten:** Würden ihre eigenen Tests auch einen plausiblen, aber falschen Fix durchwinken? (Bei unseren 4 öffentlichen Beispielen: 2 von 8.)
2. **Live-Agenten-Performance auf ihrem eigenen Code**, nicht auf einem generischen Leaderboard, das nichts über ihre Codebasis aussagt (optional, falls gewünscht).
3. **Ein wiederverwendbares Ergebnis:** 5–10 fertige, deterministische Prüfaufgaben aus ihrem eigenen Repo, die sie später erneut gegen neue Modelle laufen lassen können.

**Der einzige Aufwand auf ihrer Seite:** Lesezugriff auf 5–10 bereits gemergte PRs (alte, gelöste Bugs — die haben schon einen "Gold Patch": den echten, damals gemergten Fix). Das ist die technische Voraussetzung, nicht die Gegenleistung.

**Ablauf** (in etwa einer Woche machbar — das Muster ist heute schon bewiesen):

1. 5–10 echte, bereits gelöste Aufgaben aus dem eigenen Repo des Kunden erhalten
2. Daraus deterministische Eval-Tasks bauen — exakt das Phase-0-Muster, nur auf ihrem statt einem öffentlichen Repo
3. QS-Gauntlet drauf (Leak-Scan + Mutationstesting) — zeigt, ob ihre eigene Testsuite dieselben Lücken hat wie die heute gefundenen (requests/sympy)
4. Optional: ein echter Coding-Agent läuft gegen ein paar dieser Aufgaben — wie gut löst er *ihren* Code wirklich?
5. Ein Bericht am Ende (Stil wie die Phase-0-Berichte): X Aufgaben zuverlässig, Y mit gefundenen Testlücken, Agenten-Performance falls getestet

**Preis:** €500–1.500 — echtes Geld (Zahlungssignal-Test bleibt bestehen), aber niedrig genug für eine Entscheidung ohne Freigabeprozess. Ausdrücklich ein **Pilot-Preis**, nicht der spätere reguläre Preis (die €1–3k/Monat-Annahme aus `CLAUDE.md` war für ein laufendes Abo, anderes Produkt).

**Während des Pilots protokollieren:** Zeit pro Aufgabe fürs Onboarding — beantwortet die zweite Lackmustest-Frage direkt.

**Offener Punkt vor dem ersten echten Pilot:** Unser Harness wurde bisher nur gegen saubere, selbst gebaute Patches getestet (Gold Patches, handgebaute Mutanten) — nie gegen echten, möglicherweise unordentlichen Agenten-Output. Ein kleiner interner Testlauf (1 Agent, 1 Aufgabe, ~10–30€) vorher wäre sinnvoll, um grobe Überraschungen selbst zu finden statt beim Kunden.

## 4. Der Spickzettel

**1. Was wir machen (ein Satz):**
"Wir prüfen, ob ein KI-Coding-Agent ein Problem *wirklich* gelöst hat — oder ob eure eigenen Tests nur zu schwach sind, um den Unterschied zu merken."

**2. Was wir bisher bewiesen haben (konkret, nachprüfbar):**
"An 4 öffentlichen Beispielaufgaben: unsere Prüfmethode liefert bei zehn Wiederholungen zehnmal exakt dasselbe Ergebnis — und mit gezielten falschen Lösungsversuchen haben wir 2 echte Lücken in deren Testsuiten gefunden, die ein normaler Blick nicht gesehen hätte. Alles öffentlich auf GitHub."

**3. Warum das relevant ist:**
"82% der Firmen hatten laut einer aktuellen Studie in den letzten 6 Monaten einen Produktionsausfall durch KI-generierten Code. Das Problem ist nicht nur 'schreibt der Agent guten Code', sondern 'merkt ihr überhaupt, wenn er es nicht tut'."

**4. Das Angebot (Ergebnis zuerst, Aufwand danach):**
"Ich zeige euch, ob eure eigene Testsuite einen fehlerhaften Fix durchwinken würde — und optional, wie gut ein echter Agent auf eurem Code performt. Der einzige Aufwand für euch: Lesezugriff auf 5–10 bereits gemergte PRs. Für €500–1.500, fertig in etwa einer Woche, und am Ende gehören euch die fertigen Prüfaufgaben."

**5. Ehrlich zum Firmenstand:**
"Wir sind wenige Wochen alt. Ich baue das mit KI-gestützter technischer Unterstützung, aber jeden Schritt verstehe und verantworte ich selbst. Deshalb ist der Pilot-Preis niedrig — ihr wärt einer unserer ersten echten Kunden."

**6. Abgrenzung zu AI-Code-Reviewern (CodeRabbit, Copilot Review, Greptile & Co.):**
"Ein AI-Code-Reviewer liest einen Diff und gibt eine *Meinung* ab — 'das sieht riskant aus'. Das ist eine subjektive Einschätzung, von einer KI erzeugt — dieselbe Art Unzuverlässigkeit wie beim Agenten selbst. Wir haben keine Meinung. Wir lassen den Code tatsächlich laufen, gegen echte Tests, in einer isolierten, wiederholbaren Umgebung, und berichten Fakten: bestanden oder nicht, zehnmal identisch. Und wir prüfen zusätzlich, ob die Tests selbst streng genug sind, um das überhaupt zu bedeuten. Vertraut nicht unserer Meinung — rechnet es selbst nach."

**7. Abgrenzung zu anderen Benchmarks (SWE-bench, Scale AI, AIUC, METR):**
"Wir behaupten nicht, eine geheime Technik zu haben — Determinismus-Prüfung und Mutationstesting sind bekanntes Handwerk. Der Unterschied ist, dass wir das konsequent auf *eurem eigenen* Code anwenden, nicht auf einem öffentlichen Leaderboard, das nichts über eure spezifische Codebasis aussagt."

**8. Warum extern besser als intern (mit Zahlen, Recherche vom 20.07.2026):**
"Unabhängige Audits haben nachweislich **25% niedrigere Fehlerquoten als interne Selbstprüfung** ([Sensiba](https://sensiba.com/resources/insights/the-7-benefits-of-outsourcing-internal-audit-and-sox-compliance/)). Das ist kein Einzelfall: Der Pentest-Markt wächst 2026 auf $2,7–6,4 Mrd. und weiter mit 8–15% pro Jahr — **obwohl** die Werkzeuge dafür komplett kostenlos sind (Metasploit, OWASP ZAP). Grund: 95% der Firmen haben laut Studien intern Personalengpässe in genau diesem Spezialbereich ([Bright Defense](https://www.brightdefense.com/resources/penetration-testing-statistics/), [Fortune Business Insights](https://www.fortunebusinessinsights.com/penetration-testing-market-108434)). Der Software-Testing-Outsourcing-Markt insgesamt wird bis 2033 auf $129 Mrd. geschätzt, unter anderem wegen eines erwarteten 25%igen Fachkräftemangels bei Quality Engineering ([Coherent Market Insights](https://www.coherentmarketinsights.com/industry-reports/software-testing-and-qa-services-market)). Dasselbe Muster gilt für uns: Die Technik ist nicht geheim — aber sie konsequent, unabhängig und ohne blinden Fleck anzuwenden, macht kaum eine Firma für sich selbst."

**Schwierige Fragen, ehrlich beantwortet:**

| Frage | Antwort |
|---|---|
| "Warum soll ich einer neuen Firma vertrauen?" | "Genau deshalb ist der Preis niedrig und alles auf GitHub einsehbar — prüft es selbst, bevor ihr zahlt." |
| "Warum nicht einfach selbst mit Docker + mutmut prüfen?" | "Könnt ihr — die Werkzeuge sind frei. Aber genau das macht laut Studien kaum jemand konsequent selbst: unabhängige Audits haben 25% niedrigere Fehlerquoten als Selbstprüfung, und der Pentest-Markt wächst trotz kostenloser Tools weiter, weil intern Zeit und Fokus fehlen (siehe Punkt 8)." |
| "Was macht ihr anders als eure eigene Testsuite laufen zu lassen?" | "Eure Tests sagen nur 'grün oder rot'. Wir prüfen zusätzlich, ob 'grün' überhaupt bedeutet, dass die Lösung wirklich richtig ist." |
| "Ist das nicht einfach ein besseres KI-Modell nutzen?" | "Nein — das Problem betrifft jedes Modell. Auch der beste Agent kann durch eine zu schwache Testsuite falsch validiert werden." |
| "Warum kein AI-Code-Reviewer-Tool?" | Siehe Punkt 6 oben — Meinung vs. nachrechenbare Fakten. |
| "Habt ihr das schon bei einer echten Firma gemacht?" | "Noch nicht — ihr wärt der Erste. Genau deshalb der reduzierte Pilot-Preis." |
| "Warum sollte ich euch für meine eigenen alten Bugs bezahlen?" | "Ihr bezahlt nicht für die Bugs — die sind nur das Rohmaterial. Ihr bezahlt für das Ergebnis: zu wissen, ob eure Tests einen fehlerhaften Fix erkennen würden, und wie ein Agent auf eurem echten Code performt. Der Lesezugriff auf ein paar alte PRs ist der einzige Aufwand, den wir von euch brauchen." |

## Referenzmaterial zum Zeigen

- Code + Git-Historie: `github.com/louisklaff-cell/Truvent` (privat, Zugriff bei Bedarf gewähren) — **enthält absichtlich nur 4 Aufgaben** (django/requests/pytest/sympy, BSD/MIT/Apache-lizenziert). Die fünfte, GPL-2.0-lizenzierte pylint-Aufgabe wurde am 20.07.2026 per `git-filter-repo` komplett aus der Historie entfernt (Lizenzvorsicht bei kommerzieller Nutzung, siehe `CLAUDE.md`) — bleibt nur intern auf der eigenen Festplatte, nie kundenbezogen verwenden.
- Bericht Deutsch: https://claude.ai/code/artifact/95465702-56f3-4a18-a85e-65e8502d1085
- Bericht Englisch: https://claude.ai/code/artifact/ff432e0c-9aa2-4015-b796-32ce282531ac
