import sys; sys.path.insert(0, ".")
import snapstudy as s
T = open("samples/lecture.txt").read()
def test_summary(): assert 1 <= len(s.summarize(T, 4)) <= 4
def test_cards():
    c = s.flashcards(T); assert len(c) >= 4 and all(x["q"] and x["a"] for x in c)
def test_definition_card(): assert any(x["q"].startswith("What is") for x in s.flashcards(T))
def test_report_offline():
    md, d = s.report(T, "lecture.txt"); assert "## Flashcards" in md and d["nlp_ms"] >= 0
