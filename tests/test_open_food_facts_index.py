from scripts.build_open_food_facts_index import _calories, _is_irish, _normalise


def test_irish_country_tag_is_exact():
    assert _is_irish({"countries_tags": "en:ireland,en:united-kingdom"})
    assert not _is_irish({"countries_tags": "en:northern-ireland"})


def test_kj_fallback_converts_to_kcal():
    assert _calories({"energy-kcal_100g": "", "energy_100g": "418.4"}) == 100.0


def test_normalise_keeps_only_needed_fields():
    product = _normalise(
        {
            "code": "5390000000000",
            "product_name": "Example Irish Food",
            "brands": "Example",
            "quantity": "100 g",
            "serving_size": "25 g",
            "energy-kcal_100g": "200",
            "energy_100g": "836.8",
            "proteins_100g": "10",
            "carbohydrates_100g": "30",
            "fat_100g": "5",
            "fiber_100g": "4",
            "sugars_100g": "8",
            "salt_100g": "0.5",
            "last_modified_t": "1700000000",
        }
    )
    assert product == {
        "code": "5390000000000",
        "name": "Example Irish Food",
        "kcal_100g": 200.0,
        "brand": "Example",
        "quantity": "100 g",
        "serving_size": "25 g",
        "protein_100g": 10.0,
        "carbs_100g": 30.0,
        "fat_100g": 5.0,
        "fibre_100g": 4.0,
        "sugars_100g": 8.0,
        "salt_100g": 0.5,
        "last_modified": 1700000000,
    }
