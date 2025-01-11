from typing import TypedDict, Literal, Optional, List
import pandas as pd


class Meal(TypedDict):
    breakfast: pd.DataFrame
    lunch: pd.DataFrame
    snack: pd.DataFrame
    dinner: pd.DataFrame


class MainMealFood(TypedDict):
    composed_dishes: List[str]
    meats_and_fish: List[str]
    starchy_foods: List[str]


class DessertFoodLunch(TypedDict):
    cheeses: List[str]
    product_dairy: List[str]
    fruits: List[str]
    cakes: List[str]


class SortedFoodLunch(TypedDict):
    entries: List[str]
    main_meal: MainMealFood
    dessert: DessertFoodLunch
    drinks: List[str]
    bread: List[str]


class MiddleBreakfast(TypedDict):
    toast: List[str]
    bread_toast: List[str]
    cookies: List[str]
    cereal: List[str]
    fruits: List[str]


class SortedBreakfast(TypedDict):
    start: List[str]
    middle: MiddleBreakfast
    end: List[str]


class DessertFoodDinner(TypedDict):
    cheeses: List[str]
    product_dairy: List[str]
    fruits: List[str]
    cakes: List[str]
    ice_creams: List[str]


class SortedFoodDinner(TypedDict):
    entries: List[str]
    main_meal: MainMealFood
    dessert: DessertFoodDinner
    drinks: List[str]
    bread: List[str]


LiteralMealNames = Literal["breakfast", "lunch", "snack", "dinner"]


__all__ = [
    "SortedFoodDinner",
    "DessertFoodDinner",
    "SortedBreakfast",
    "MiddleBreakfast",
    "SortedFoodLunch",
    "DessertFoodLunch",
    "MainMealFood",
    "Meal",
    "LiteralMealNames"
]
