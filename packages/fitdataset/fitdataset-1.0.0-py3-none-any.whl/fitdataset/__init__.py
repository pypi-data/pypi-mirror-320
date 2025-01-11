from __future__ import annotations

__docformat__ = "restructuredtext"

from fitdataset import (
    constantes_parser_dataset as constant,
    interfaces as itf,
    parser as _parserdataset,
    dataset as _processdataset,
    utils
)


_ctx = _processdataset.Dataset()


def __get_meal_item(key: itf.LiteralMealNames):
    return _ctx[key]


def get(item: itf.LiteralMealNames):
    return __get_meal_item(item)


def ctx() -> _processdataset.Dataset:
    return _ctx


frame = _ctx.frame
meal = _ctx.meal
breakfast = _ctx.breakfast
lunch = _ctx.lunch
snack = _ctx.snack
dinner = _ctx.dinner


__all__ = [
    "constant",
    "itf",
    "_parserdataset",
    "_processdataset",
    "utils",
    "_ctx",
    'get',
    'ctx',
    'frame',
    'meal',
    "breakfast",
    "lunch",
    "snack",
    "dinner"
]
