import pandas as pd
from fitdataset.constantes_parser_dataset import BREAKFAST, LUNCH, SNACK, DINNER
from typing import Literal


class ParserDatasetNutritional:
    def __init__(
        self,
        frame: pd.DataFrame,
        meal: Literal["breakfast", "lunch", "snack", "dinner"],
    ) -> None:
        if meal not in ("breakfast", "lunch", "snack", "dinner"):
            raise ValueError(
                "Must be params 'meal': 'breakfast', 'lunch', 'snack', 'dinner'"
            )
        self.frame = frame
        self.meal: Literal["breakfast", "lunch", "snack", "dinner"] = meal

    def _parser_breakfast(self) -> pd.DataFrame:
        df = self.frame
        sous_groupe_del = [
            "crèmes et spécialités à base de crème",
            "huiles de poissons",
            "huiles et graisses végétales",
            "autres matières grasses",
            "margarines",
            "confiseries non chocolatées",
            "gâteaux et pâtisseries",
            "fromages et assimilés",
            "pâtes, riz et céréales",
            "biscuits apéritifs",
        ]
        for col in sous_groupe_del:
            df = df[~(df["sous_groupe"] == col)]
        none_breakfast_elements = BREAKFAST.ELEMENTS_TARGET_DELETED
        elements_target = BREAKFAST.ELEMENTS_TARGET
        for none_element in none_breakfast_elements:
            df = df[~(df["nom_aliment"] == none_element.strip())]
            for key, value in elements_target.items():
                df = self.__select_element(df, value, key)
        return df

    def _parser_lunch(self) -> pd.DataFrame:
        df = self.frame
        sous_groupe_del = [
            "substitus de produits carnés",
            "beurres",
            "huiles et graisses végétales",
            "margarines",
            "huiles de poissons",
            "autres matières grasses",
            "légumes",
            "pommes de terre et autres tubercules",
            "légumineuses",
            "crèmes et spécialités à base de crème",
            "laits",
            "chocolats et produits à base de chocolat",
            "confitures et assimilés",
            "viennoiseries",
            "biscuits sucrés",
            "céréales de petit-déjeuner",
            "barres céréalières",
            "confiseries non chocolatées",
            "sucres, miels et assimilés",
        ]
        for col in sous_groupe_del:
            df = df[~(df["sous_groupe"] == col)]
        elements_target = LUNCH.ELEMENTS_TARGET
        none_elements_lunch = LUNCH.ELEMENT_DEL
        for none_element in none_elements_lunch:
            df = df[~(df["nom_aliment"] == none_element.strip())]

        for key, values in elements_target.items():
            df = self.__select_element(df, values, key)
        return df

    def _parser_snack(self) -> pd.DataFrame:
        df = self.frame
        sous_groupe_del = [
            "fromages et assimilés",
            "crèmes et spécialités à base de crème",
            "confiseries non chocolatées",
            "glaces",
            "sorbets",
            "desserts glacés",
        ]
        for col in sous_groupe_del:
            df = df[~(df["sous_groupe"] == col)]

        elements_target = SNACK.ELEMENT_TARGET
        for key, value in elements_target.items():
            df = self.__select_element(df, value, key)

        df.dropna(subset=["sous_groupe"], inplace=True)
        return df

    def _parser_dinner(self) -> pd.DataFrame:
        df = self.frame
        sous_groupe_del = [
            "substitus de produits carnés",
            "beurres",
            "huiles et graisses végétales",
            "margarines",
            "huiles de poissons",
            "autres matières grasses",
            "légumes",
            "pommes de terre et autres tubercules",
            "légumineuses",
            "crèmes et spécialités à base de crème",
            "laits",
            "chocolats et produits à base de chocolat",
            "confitures et assimilés",
            "viennoiseries",
            "biscuits sucrés",
            "céréales de petit-déjeuner",
            "barres céréalières",
            "confiseries non chocolatées",
            "sucres, miels et assimilés",
            "mollusques et crustacés cuits",
            "mollusques et crustacés crus",
            "produits à base de poissons et produits de la mer",
        ]
        for col in sous_groupe_del:
            df = df[~(df["sous_groupe"] == col)]

        elements_target = DINNER.ELEMENTS_TARGET
        none_elements_dinner = DINNER.ELEMENT_DEL
        for key, value in elements_target.items():
            df = self.__select_element(df, value, key)

        for none_element in none_elements_dinner:
            df = df[~(df["nom_aliment"] == none_element.strip())]
        df.dropna(subset=["sous_groupe"], inplace=True)
        return df

    def __select_element(
        self, df: pd.DataFrame, list_elements: list, key: str
    ) -> pd.DataFrame:
        new_df = df.copy()
        fruits_to_keep = df[
            (df["sous_groupe"] == key) & (
                df["nom_aliment"].isin(list_elements))
        ]
        new_df = df[df["sous_groupe"] != key]
        complete_df = pd.concat([new_df, fruits_to_keep], ignore_index=True)

        return complete_df

    @property
    def breakfast(self) -> pd.DataFrame:
        if self.meal == "breakfast":
            return self._parser_breakfast()
        raise ValueError(
            f"You can't select breakfast: value meal -> {self.meal}")

    @property
    def lunch(self) -> pd.DataFrame:
        if self.meal == "lunch":
            return self._parser_lunch()
        raise ValueError(f"You can't select lunch: value meal -> {self.meal}")

    @property
    def snack(self) -> pd.DataFrame:
        if self.meal == "snack":
            return self._parser_snack()
        raise ValueError(f"You can't select snack: value meal -> {self.meal}")

    @property
    def dinner(self) -> pd.DataFrame:
        if self.meal == "dinner":
            return self._parser_dinner()
        raise ValueError(f"You can't select dinner: value meal -> {self.meal}")


__all__ = ["ParserDatasetNutrional"]
