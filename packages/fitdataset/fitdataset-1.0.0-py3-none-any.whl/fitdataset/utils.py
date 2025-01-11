import pandas as pd
from pandas import DataFrame

COL_TYPES = {
    "groupe_aliment": str,
    "sous_groupe": str,
    "categorie": str,
    "nom_aliment": str,
    "Energie, Règlement UE N° 1169/2011 (kcal/100 g)": float,
    "Eau (g/100 g)": float,
    "Protéines, N x facteur de Jones (g/100 g)": float,
    "Glucides (g/100 g)": float,
    "Lipides (g/100 g)": float,
    "Sucres (g/100 g)": float,
    "Fibres alimentaires (g/100 g)": float,
    "Alcool (g/100 g)": float,
}


def convert_float(df: DataFrame, key: str) -> DataFrame:
    df[key] = df[key].apply(lambda x: str(x).strip().replace(",", "."))
    return df


def define_types(df: DataFrame, **types: dict[str, type]) -> DataFrame:
    """
    Converts specified columns in a DataFrame to the given types.

    Args:
        df (DataFrame): The DataFrame to modify.
        **types (dict[str, type]): A mapping of column names to target types (int, float, str).

    Returns:
        DataFrame: The DataFrame with columns converted to the specified types.

    Raises:
        Exception: If a specified column is not found in the DataFrame.
        ValueError: If a column cannot be converted to the specified type.
    """
    for col, typecol in types.items():
        if col not in df.columns:
            raise Exception(f"Column '{col}' not found in the DataFrame.")
        if typecol in (int, float):
            try:
                df = convert_float(df, col)
                df[col] = pd.to_numeric(df[col], errors="coerce")
                df.fillna(0, inplace=True)
            except Exception as e:
                raise ValueError(f"Error converting column '{
                                 col}' to {typecol}: {e}")

        elif typecol == str:
            df[col] = df[col].astype(str)
            df.fillna("", inplace=True)

    return df


COL_PROPORTIONS = {
    "energie": "Energie, Règlement UE N° 1169/2011 (kcal/100 g)",
    "protein": "Protéines, N x facteur de Jones (g/100 g)",
    "carbs": "Glucides (g/100 g)",
    "fat": "Lipides (g/100 g)",
    "fibers": "Fibres alimentaires (g/100 g)",
}


def calc_kcal(**macros: dict[str, float]):
    kcal = (
        (macros["protein"] * 4) +
        (macros["carbs"] * 4) +
        (macros["fat"] * 9) +
        (macros["fibers"] * 2)
    )
    return round(kcal, 2)


def patch_value_kcal(frame: DataFrame) -> DataFrame:
    """
    Recalculate and update the 'Energie' column for rows where its value is 0.0.

    Args:
        frame (DataFrame): The DataFrame to process.

    Returns:
        DataFrame: The modified DataFrame with recalculated 'Energie' values.
    """
    energie_zero = frame[frame[COL_PROPORTIONS["energie"]] == 0.0]
    for index, row in energie_zero.iterrows():
        _patch_value(row, frame, index)
    return frame


def _patch_value(row: pd.Series, frame: DataFrame, index: int):
    """
    Recalculate and patch the 'Energie' value for a single row.

    Args:
        row (pd.Series): The current row with 'Energie' = 0.0.
        frame (DataFrame): The DataFrame being updated.
        index (int): The index of the current row.
    """
    required_cols = ["protein", "carbs", "fat", "fibers"]
    if all(row[COL_PROPORTIONS[col]] == 0.0 for col in required_cols):
        return False
    values = {
        "protein": row[COL_PROPORTIONS["protein"]],
        "carbs": row[COL_PROPORTIONS["carbs"]],
        "fat": row[COL_PROPORTIONS["fat"]],
        "fibers": row[COL_PROPORTIONS["fibers"]],
    }
    kcal = calc_kcal(**values)
    frame.at[index, COL_PROPORTIONS["energie"]] = kcal

    return True
