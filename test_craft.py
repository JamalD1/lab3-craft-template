import pytest
from unittest.mock import patch
from recipes import CAPACITY, RECIPES

RECIPES["тест_зелье"] = {
    "ingredients": {"трава": 2},
    "result": "зелье",
    "level_req": 3,
    "fail_chance": 0.3
}

def item(name, quality=3, equipped=False):
    thing = {"name": name, "quality": quality}
    if equipped:
        thing["equipped"] = True
    return thing

def test_torch(impl):
    inventory = [item("палка", 2), item("смола", 4), item("кожа")]
    torch = impl.craft(inventory, "факел", 1)
    assert torch == {"name": "факел", "quality": 2}
    assert inventory == [item("кожа"), torch]

def test_happy_path(impl):
    inv = [item("трава", 5), item("трава", 1)]
    with patch("random.random", return_value=0.0):
        res = impl.craft(inv, "тест_зелье", 5)
        assert res == {"name": "зелье", "quality": 5}
        assert inv == [res]

def test_not_enough_ingredients(impl):
    inv = [item("трава", 1)]
    with pytest.raises(ValueError):
        impl.craft(inv, "тест_зелье", 5)
    assert inv == [item("трава", 1)]

def test_empty_inventory(impl):
    inv = []
    with pytest.raises(ValueError):
        impl.craft(inv, "тест_зелье", 5)

def test_ingredients_quality_priority(impl):
    inv = [item("трава", 1), item("трава", 5), item("трава", 4)]
    with patch("random.random", return_value=0.0):
        res = impl.craft(inv, "тест_зелье", 5)
        assert inv == [item("трава", 1), res]

def test_atomicity_on_fail(impl):
    inv = [item("трава", 5), item("трава", 5)]
    with patch("random.random", return_value=0.9):
        res = impl.craft(inv, "тест_зелье", 5)
        assert res is None
        assert inv == []

def test_valera_burn_bug(impl):
    RECIPES["комплексный"] = {"ingredients": {"железо": 1, "уголь": 1}, "result": "сталь", "level_req": 1, "fail_chance": 0.0}
    inv = [item("железо", 1)]
    with pytest.raises(ValueError):
        impl.craft(inv, "комплексный", 1)
    assert inv == [item("железо", 1)]

def test_deterministic_random(impl):
    inv = [item("трава", 5), item("трава", 5)]
    with patch("random.random", return_value=0.0), patch("valera_craft.random.random", return_value=0.0, create=True):
        assert impl.craft(inv, "тест_зелье", 5) is not None

def test_level_validation(impl):
    inv = [item("трава", 5), item("трава", 5)]
    for bad_lvl in (True, -5, "10"):
        with pytest.raises(ValueError):
            impl.craft(inv, "тест_зелье", bad_lvl)
