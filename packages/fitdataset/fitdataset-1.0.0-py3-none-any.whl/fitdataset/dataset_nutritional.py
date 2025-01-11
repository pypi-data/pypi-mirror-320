import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Literal
from fitdataset.interfaces import Meal
from fitdataset.parser import ParserDatasetNutritional



class DatasetNutritional:
    def __init__(self, path_database: str) -> None:
        if not Path(path_database).exists():
            Path(path_database).mkdir(exist_ok=True, parents=True)
        self.path_database = path_database
        self._filename = "dataset_brut.xls"
        self._filename_output = "dataset.csv"
        self.url = "https://ciqual.anses.fr/cms/sites/default/files/inline-files/Table%20Ciqual%202020_FR_2020%2007%2007.xls"
        self.__df = self.get_dataset()

    @property
    def df(self) -> pd.DataFrame:
        return self.__df

    def fetch(self) -> pd.DataFrame:
        path = Path(self.path_database)
        file_path = path.joinpath(self._filename)
        fileoutput = path.joinpath(self._filename_output)

        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            df = pd.read_excel(file_path)
            df = self.clear_df(df)
            df.to_csv(fileoutput, index=False)
            return df
        except requests.exceptions.RequestException as e:
            raise e

    def read_file_csv(self) -> pd.DataFrame:
        path = Path(self.path_database).joinpath(self._filename_output)
        df = pd.read_csv(path)
        return df

    def get_dataset(self) -> pd.DataFrame:
        path = Path(self.path_database).joinpath(self._filename_output)
        if not path.exists():
            df = self.fetch()
        else:
            df = self.read_file_csv()
        return df

    def __remove_cols(self, df=pd.DataFrame) -> pd.DataFrame:
        columns_to_remove = [
            "Energie, N x facteur Jones, avec fibres  (kcal/100 g)",
            "Energie, N x facteur Jones, avec fibres  (kJ/100 g)",
            "Protéines, N x 6.25 (g/100 g)",
            "Fructose (g/100 g)",
            "Galactose (g/100 g)",
            "Glucose (g/100 g)",
            "Lactose (g/100 g)",
            "Maltose (g/100 g)",
            "Saccharose (g/100 g)",
            "Amidon (g/100 g)",
            "Polyols totaux (g/100 g)",
            "AG 4:0, butyrique (g/100 g)",
            "AG 6:0, caproïque (g/100 g)",
            "AG 8:0, caprylique (g/100 g)",
            "AG 10:0, caprique (g/100 g)",
            "AG 12:0, laurique (g/100 g)",
            "AG 14:0, myristique (g/100 g)",
            "AG 16:0, palmitique (g/100 g)",
            "AG 18:0, stéarique (g/100 g)",
            "AG 18:1 9c (n-9), oléique (g/100 g)",
            "AG 18:2 9c,12c (n-6), linoléique (g/100 g)",
            "AG 18:3 c9,c12,c15 (n-3), alpha-linolénique (g/100 g)",
            "AG 20:4 5c,8c,11c,14c (n-6), arachidonique (g/100 g)",
            "AG 20:5 5c,8c,11c,14c,17c (n-3) EPA (g/100 g)",
            "AG 22:6 4c,7c,10c,13c,16c,19c (n-3) DHA (g/100 g)",
            "Cendres (g/100 g)",
            "Acides organiques (g/100 g)",
            "Chlorure (mg/100 g)",
            "Iode (µg/100 g)",
            "Sodium (mg/100 g)",
            "Cholestérol (mg/100 g)"
        ]
        other_columns_to_remove = [
            'alim_grp_code', 'alim_ssgrp_code', 'alim_ssssgrp_code',
            'alim_code', 'alim_nom_sci',
            'Energie, Règlement UE N° 1169/2011 (kJ/100 g)',
            'Rétinol (µg/100 g)', 'Beta-Carotène (µg/100 g)',
            'AG saturés (g/100 g)',
            'AG monoinsaturés (g/100 g)', 'AG polyinsaturés (g/100 g)',
            'Sel chlorure de sodium (g/100 g)', 'Calcium (mg/100 g)',
            'Cuivre (mg/100 g)', 'Fer (mg/100 g)', 'Magnésium (mg/100 g)',
            'Manganèse (mg/100 g)', 'Phosphore (mg/100 g)', 'Potassium (mg/100 g)',
            'Sélénium (µg/100 g)', 'Zinc (mg/100 g)', 'Vitamine D (µg/100 g)',
            'Vitamine E (mg/100 g)', 'Vitamine K1 (µg/100 g)',
            'Vitamine K2 (µg/100 g)', 'Vitamine C (mg/100 g)',
            'Vitamine B1 ou Thiamine (mg/100 g)',
            'Vitamine B2 ou Riboflavine (mg/100 g)',
            'Vitamine B3 ou PP ou Niacine (mg/100 g)',
            'Vitamine B5 ou Acide pantothénique (mg/100 g)',
            'Vitamine B6 (mg/100 g)', 'Vitamine B9 ou Folates totaux (µg/100 g)',
            'Vitamine B12 (µg/100 g)'
        ]

        df.drop(columns=columns_to_remove, inplace=True)
        df.drop(columns=other_columns_to_remove, inplace=True)
        return df

    def __rename_col(self, df: pd.DataFrame) -> pd.DataFrame:
        columns_to_rename = {
            'alim_grp_nom_fr': 'groupe_aliment',
            'alim_ssgrp_nom_fr': 'sous_groupe',
            'alim_ssssgrp_nom_fr': 'categorie',
            'alim_nom_fr': 'nom_aliment'
        }
        df.rename(columns=columns_to_rename, inplace=True)
        return df

    def clear_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.__remove_cols(df)
        df = self.__rename_col(df)
        # supprimer tout les alims contenant de l'alcool
        df = df[df["Alcool (g/100 g)"] == "0"]
        df = self.__del_porc_vin_alcool(df)
        df = self.__clear_value(df)
        df = self.__clear_value_col_float(df)
        return df

    def __del_porc_vin_alcool(self, df: pd.DataFrame) -> pd.DataFrame:
        columns_to_check = ["nom_aliment"]
        for col in columns_to_check:
            if col not in df.columns:
                raise KeyError(
                    f"La colonne '{col}' est introuvable dans le DataFrame.")

        pattern = r"\b(?:porc|vin|alcool|bacon|bière|jambon|charcuterie)\b"

        mask = df[columns_to_check].apply(
            lambda row: row.astype(str).str.contains(
                pattern, case=False, na=False, regex=True)
        ).any(axis=1)

        df_cleaned = df[~mask].reset_index(drop=True)

        return df_cleaned

    def get_porc_vin_alcool(self):
        """
        Récupère toutes les lignes contenant les mots-clés
        'porc', 'vin', 'alcool', 'bacon', ou 'bière' dans les colonnes
        'groupe_aliment', 'sous_groupe', 'categorie', ou 'nom_aliment'.
        """
        columns_to_check = ["nom_aliment"]
        for col in columns_to_check:
            if col not in self.df.columns:
                raise KeyError(
                    f"La colonne '{col}' est introuvable dans le DataFrame.")

        # Expression régulière pour détecter les mots-clés
        pattern = r"\b(?:porc|vin|alcool|bacon|bière)\b"

        # Vérifier dans toutes les colonnes spécifiées
        filtered = self.df[
            self.df[columns_to_check].apply(
                lambda row: row.astype(str).str.contains(
                    pattern, case=False, na=False, regex=True)
            ).any(axis=1)
        ]
        return filtered

    def __clear_value(self, df: pd.DataFrame) -> pd.DataFrame:
        df.replace(to_replace="-", value="None", inplace=True)
        return df

    def __clear_value_col_float(self, df: pd.DataFrame) -> pd.DataFrame:
        columns_to_clean = [
            'Energie, Règlement UE N° 1169/2011 (kcal/100 g)',
            'Eau (g/100 g)',
            'Protéines, N x facteur de Jones (g/100 g)',
            'Glucides (g/100 g)',
            'Lipides (g/100 g)',
            'Sucres (g/100 g)',
            'Fibres alimentaires (g/100 g)',
            'Alcool (g/100 g)'
        ]
        for col in columns_to_clean:
            df[col] = (df[col]
                       .astype(str)
                       .str
                       .replace(r"[<>]\s*", "", regex=True)
                       .replace("traces", "0")
                       .replace("None", np.nan)
                       .replace("", np.nan)
                       )
        return df

    def _filter_by_drink(self, df: pd.DataFrame, sorted_filter: Literal["breakfast/snack", "lunch/dinner"]):
        """
        Filtre les boissons en fonction de la catégorie cible.

        Args:
            df (pd.DataFrame): DataFrame contenant les données alimentaires.
            sorted_filter (Literal["breakfast/snack", "lunch/dinner"]): 
                - "breakfast/snack": Boissons pour le petit-déjeuner ou les collations.
                - "lunch/dinner": Boissons pour le déjeuner ou le dîner.

        Returns:
            pd.DataFrame: Les lignes filtrées en fonction de la catégorie de boisson.
        """
        # Filtrage des boissons uniquement
        newdf = df[df["groupe_aliment"] == "eaux et autres boissons"]

        # Listes de boissons par catégorie
        sorted_b_s = ["café", "lait", "chocolat",
                      "nectar", "jus", "thé", "eau", "cacao"]
        sorted_l_d = ["eau minérale", "eau du robinet",
                      "jus", "nectar", "gazeux", "cola", "limonade"]

        # Liste des boissons à exclure
        del_values_if = [
            "Boisson cacaotée ou au chocolat, instantanée, sucrée, prête à boire (reconstituée avec du lait demi-écrémé standard)",
            "Boisson cacaotée ou au chocolat, instantanée, sucrée, enrichie en vitamines, prête à boire (reconstituée avec du lait demi-écrémé standard)",
            "Poudre cacaotée ou au chocolat pour boisson, sucrée",
            "Poudre maltée, cacaotée ou au chocolat pour boisson, sucrée, enrichie en vitamines et minéraux",
            "Café au lait ou cappuccino au chocolat, poudre soluble",
            "Poudre cacaotée ou au chocolat sucrée pour boisson, enrichie en vitamines et minéraux",
            "Poudre cacaotée ou au chocolat pour boisson, sucrée, enrichie en vitamines"
        ]

        if sorted_filter == "breakfast/snack":
            return newdf[newdf["nom_aliment"].str.lower().str.contains('|'.join(sorted_b_s))]

        elif sorted_filter == "lunch/dinner":
            filtered_newdf = newdf[newdf["nom_aliment"].str.lower(
            ).str.contains('|'.join(sorted_l_d))]

            filtered_df = filtered_newdf[~filtered_newdf["nom_aliment"].str.lower().isin(
                [val.lower() for val in del_values_if])]
            return filtered_df

        else:
            raise ValueError(
                "sorted_filter must be 'breakfast/snack' or 'lunch/dinner'")

    def _filter_by_fruits_and_vegetables(self, df: pd.DataFrame, target: Literal["fruits", "legumes", "all"] = "all"):
        """
        Filtre les fruits et légumes spécifiques des sous-catégories.

        Args:
            df (pd.DataFrame): DataFrame contenant les données alimentaires.
            target (Literal["fruits", "legumes", "all"]): Type de sous-catégorie à filtrer.
                - "fruits": Renvoie les fruits seulement.
                - "legumes": Renvoie les légumes seulement.
                - "all": Renvoie les fruits et légumes.

        Returns:
            pd.DataFrame: Les lignes filtrées en fonction de la catégorie.
        """
        sorted_values_fruits = [
            'fruits', 'fruits à coque et graines oléagineuses']
        sorted_values_vegetables = [
            'légumes', 'pommes de terre et autres tubercules', 'légumineuses']
        newdf = df[df["groupe_aliment"] ==
                   "fruits, légumes, légumineuses et oléagineux"]

        if target == "all":
            return newdf
        elif target == "fruits":
            return newdf[newdf["sous_groupe"].isin(sorted_values_fruits)]
        elif target == "legumes":
            return newdf[newdf["sous_groupe"].isin(sorted_values_vegetables)]
        else:
            raise ValueError("Target must be 'all', 'fruits', or 'legumes'.")

    @property
    def breakfast(self):
        """
        Filtre les aliments appropriés pour le petit-déjeuner.

        - Supprime les fruits et légumes généraux.
        - Ajoute uniquement les fruits au DataFrame du petit-déjeuner.

        Returns:
            pd.DataFrame: DataFrame filtrée pour le petit-déjeuner.
        """
        categories = [
            "produits laitiers et assimilés",
            "fruits, légumes, légumineuses et oléagineux",
            "matières grasses",
            "produits sucrés",
            "produits céréaliers",
            "eaux et autres boissons"
        ]
        breakfast = self.df[self.df["groupe_aliment"].isin(categories)].copy()
        breakfast = breakfast[~(
            breakfast["groupe_aliment"] == "fruits, légumes, légumineuses et oléagineux")]
        fruits = self._filter_by_fruits_and_vegetables(self.df, "fruits")
        breakfast = breakfast[~(
            breakfast["groupe_aliment"] == "eaux et autres boissons"
        )]
        drinks = self._filter_by_drink(self.df, "breakfast/snack")
        breakfast = pd.concat([breakfast, fruits, drinks], ignore_index=True)
        df_breakfast = ParserDatasetNutritional(
            breakfast, "breakfast").breakfast
        return df_breakfast

    @property
    def lunch(self):
        """Filtre les aliments appropriés pour le déjeuner."""
        categories = [
            "produits laitiers et assimilés",
            "produits sucrés",
            "viandes, œufs, poissons et assimilés",
            "fruits, légumes, légumineuses et oléagineux",
            "produits céréaliers",
            "matières grasses",
            "entrées et plats composés",
            "eaux et autres boissons"
        ]
        lunch = self.df[self.df["groupe_aliment"].isin(categories)].copy()
        lunch = lunch[~(
            lunch["groupe_aliment"] == "fruits, légumes, légumineuses et oléagineux"
        )]
        fruits_vegetables = self._filter_by_fruits_and_vegetables(
            self.df, "all")
        drinks = self._filter_by_drink(self.df, "lunch/dinner")
        lunch = lunch[~(
            lunch["groupe_aliment"] == "eaux et autres boissons"
        )]
        lunch = pd.concat(
            [lunch, fruits_vegetables, drinks], ignore_index=True)
        df_lunch = ParserDatasetNutritional(lunch, "lunch").lunch
        return df_lunch

    @property
    def snack(self):
        """Filtre les aliments appropriés pour la collation de l'après-midi (goûter)."""
        categories = [
            "produits sucrés",
            "produits laitiers et assimilés",
            "fruits, légumes, légumineuses et oléagineux",
            "glaces et sorbets",
            "eaux et autres boissons"
        ]
        snack = self.df[self.df["groupe_aliment"].isin(categories)].copy()
        snack = snack[~(
            snack["groupe_aliment"] == "fruits, légumes, légumineuses et oléagineux"
        )]
        fruits = self._filter_by_fruits_and_vegetables(self.df, "fruits")
        drinks = self._filter_by_drink(self.df, "breakfast/snack")
        snack = snack[~(
            snack["groupe_aliment"] == "eaux et autres boissons"
        )]
        snack = pd.concat([snack, fruits, drinks], ignore_index=True)
        df_snack = ParserDatasetNutritional(snack, "snack").snack
        return df_snack

    @property
    def dinner(self):
        """Filtre les aliments appropriés pour le dîner."""
        categories = [
            "produits laitiers et assimilés",
            "produits sucrés",
            "viandes, œufs, poissons et assimilés",
            "fruits, légumes, légumineuses et oléagineux",
            "produits céréaliers",
            "entrées et plats composés",
            "glaces et sorbets",
            "eaux et autres boissons"
        ]
        dinner = self.df[self.df["groupe_aliment"].isin(categories)].copy()
        dinner = dinner[~(
            dinner["groupe_aliment"] == "fruits, légumes, légumineuses et oléagineux"
        )]
        fruits_vegetables = self._filter_by_fruits_and_vegetables(
            self.df, "all")
        drinks = self._filter_by_drink(self.df, "lunch/dinner")
        dinner = dinner[~(
            dinner["groupe_aliment"] == "eaux et autres boissons"
        )]
        dinner = pd.concat(
            [dinner, fruits_vegetables, drinks], ignore_index=True)
        df_dinner = ParserDatasetNutritional(dinner, "dinner").dinner
        return df_dinner

    @property
    def meal(self) -> Meal:
        return {
            "breakfast": self.breakfast,
            "lunch": self.lunch,
            "snack": self.snack,
            "dinner": self.dinner
        }

__all__ = ["DatasetNutritional"]


