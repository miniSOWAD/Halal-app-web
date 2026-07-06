from app.analysis import calculate_health, normalize, split_ingredients


def test_split_ingredients_keeps_nested_items_together():
    text = "Sugar, chocolate chips (cocoa, lecithin), gelatin, E471"
    assert split_ingredients(text) == [
        "Sugar",
        "chocolate chips (cocoa, lecithin)",
        "gelatin",
        "E471",
    ]


def test_normalize_e_number():
    assert normalize("E-471") == "e471"


def test_health_high_sugar_is_penalized():
    result = calculate_health([], {"sugars_100g": 30, "saturated_fat_100g": 8})
    assert result["status"] == "UNHEALTHY"
    assert result["score"] < 50
