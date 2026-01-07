from soil_health.rules import compute_grade

def test_low_p_low_oc_combo():
    sample = {"N": 120, "P": 8, "K": 85, "pH": 5.8, "OC": 0.45}
    grade, problems, plan, explain = compute_grade(sample)
    assert "Low P" in problems
    assert "Low OC" in problems
    assert any("P/ha" in p or "phosphate" in p.lower() for p in plan)
    assert any("farmyard" in p.lower() or "compost" in p.lower() for p in plan)

def test_good_sample():
    sample = {"N": 600, "P": 30, "K": 300, "pH": 6.5, "OC": 1.0}
    grade, problems, plan, explain = compute_grade(sample)
    assert grade == "Good"
    assert problems == []
