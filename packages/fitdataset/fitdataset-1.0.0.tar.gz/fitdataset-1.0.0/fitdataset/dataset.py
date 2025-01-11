from fitdataset.dataset_nutritional import DatasetNutritional
from fitdataset.utils import define_types, COL_TYPES, patch_value_kcal
from fitdataset.interfaces import Meal
from typing import Literal, Optional, Tuple, List
from pathlib import Path
import pandas as pd


class DatasetProcessor:
    MEAL_FILENAMES = ["breakfast.csv", "lunch.csv", "snack.csv", "dinner.csv"]
    DF_TOTAL_FILENAME = "dataset.csv"

    def __init__(self, path_database: str):
        self._path_database = Path(path_database)

        self.__parser = DatasetNutritional(
            self._path_database.joinpath('.processor').as_posix())
        meal, df = self.__setup()
        self.__meal = meal
        self.__df = df

    def __setup(self) -> Tuple[Meal, pd.DataFrame]:
        meal, df = self.__setup_dataset()
        return meal, df

    def __setup_dataset(self) -> Tuple[Meal, pd.DataFrame]:
        meal = self.__install_meal()
        df = self.__setup_dataset_frame(meal)
        return meal, df

    def __create_dataset_meal(self, filename: str) -> Tuple[str, pd.DataFrame]:
        file = self._path_database.joinpath(filename).as_posix()
        key = filename.split(".csv")[0]
        df: pd.DataFrame = self.__parser.meal[key]
        df = define_types(df, **COL_TYPES)
        df = patch_value_kcal(df)
        df.to_csv(file, index=False)
        return key, df

    def __read_dataset_meal(self, filename: str) -> Optional[Tuple[str, pd.DataFrame]]:
        file = self._path_database.joinpath(filename)
        key = filename.split(".csv")[0]
        if file.exists():
            df = pd.read_csv(file.as_posix(), index_col=False)
            return key, df
        return None

    def __install_meal(self) -> Meal:
        meal: Meal = {}
        for filename in self.MEAL_FILENAMES:
            element = self.__read_dataset_meal(filename)
            if element is None:
                key, frame = self.__create_dataset_meal(filename)
            else:
                key, frame = element
            meal[key] = frame

        return meal

    def __install_meal_total_dataset(self, filename: str, meal: Meal) -> pd.DataFrame:
        file = self._path_database.joinpath(filename).as_posix()
        meal_values: List[pd.DataFrame] = [v for k, v in meal.items()]
        df = pd.concat(meal_values, ignore_index=True)
        df.to_csv(file, index=False)
        return df

    def __setup_dataset_frame(self, meal: Meal) -> pd.DataFrame:
        filename = self._path_database.joinpath(
            self.DF_TOTAL_FILENAME).as_posix()
        element = self.__read_dataset_meal(filename)
        if element is not None:
            _, frame = element
        else:
            frame = self.__install_meal_total_dataset(filename, meal)
        return frame

    @property
    def meal(self) -> Meal:
        return self.__meal

    @property
    def breakfast(self) -> pd.DataFrame:
        return self.meal["breakfast"]

    @property
    def lunch(self) -> pd.DataFrame:
        return self.meal["lunch"]

    @property
    def snack(self) -> pd.DataFrame:
        return self.meal["snack"]

    @property
    def dinner(self) -> pd.DataFrame:
        return self.meal["dinner"]

    @property
    def frame(self) -> pd.DataFrame:
        return self.__df


class Dataset(DatasetProcessor):
    def __init__(self):
        path_database = Path(__file__).parent.joinpath(".database")
        path_database.mkdir(exist_ok=True, parents=True)
        super().__init__(path_database)

    def __getitem__(self, key: Literal['breakfast', 'lunch', 'snack', 'dinner']) -> pd.DataFrame:
        if key not in ['breakfast', 'lunch', 'snack', 'dinner']:
            raise KeyError(
                f"{key} no in ['breakfast', 'lunch', 'snack', 'dinner']")
        return self.meal[key]


__all__ = ["DatasetProcessor", "Dataset"]
