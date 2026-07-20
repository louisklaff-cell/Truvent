"""Truvent-Kanarienvogel: feste, immer mitgefuehrte Zusatztests, um
grobe/undifferenzierte Manipulation der Testauswertung zu erkennen (z.B.
ein Patch, der unittest.TestCase.assertTrue global lahmlegt). Bewusst
KEIN Schutz gegen einen gezielten Angriff, der nur den bekannten
Ziel-Testnamen manipuliert und alles andere ehrlich laesst -- das haben
zwei unabhaengige Audit-Agenten empirisch gezeigt (21.07.2026, Details in
Claude-Memory truvent-oracle-isolation-research). Exerciert bewusst BEIDE
Assertion-Mechaniken (unittest.TestCase UND nacktes assert), weil ein
Kanarienvogel, der nur die eine Mechanik nutzt, eine Manipulation der
jeweils ANDEREN Mechanik nicht erkennen wuerde (ebenfalls ein Fund der
Audit-Agenten).
"""
import unittest


class TruventCanary(unittest.TestCase):
    def test_truvent_canary_must_pass(self):
        self.assertTrue(True)

    def test_truvent_canary_must_fail(self):
        self.assertTrue(False)


def test_truvent_canary_bare_must_pass():
    assert True


def test_truvent_canary_bare_must_fail():
    assert False
