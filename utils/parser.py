import pandas as pd

SALES_REQUIRED = {"дата", "sku", "название_товара", "категория", "продано_штук", "выручка", "сессии"}
RETURNS_REQUIRED = {"дата", "sku", "количество_возвратов", "причина_возврата"}
STOCK_REQUIRED = {"sku", "остаток", "склад"}


def _check_columns(df: pd.DataFrame, required: set, name: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Отсутствуют обязательные колонки: {', '.join(sorted(missing))}")


def parse_sales(file) -> pd.DataFrame:
    try:
        df = pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"Не удалось прочитать CSV: {e}")
    _check_columns(df, SALES_REQUIRED, "sales.csv")
    try:
        df["дата"] = pd.to_datetime(df["дата"], format="%Y-%m-%d")
        df["продано_штук"] = pd.to_numeric(df["продано_штук"], errors="raise").astype(int)
        df["выручка"] = pd.to_numeric(df["выручка"], errors="raise").astype(float)
        df["сессии"] = pd.to_numeric(df["сессии"], errors="raise").astype(int)
    except Exception as e:
        raise ValueError(f"Ошибка типов данных: {e}")
    return df


def parse_returns(file) -> pd.DataFrame:
    try:
        df = pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"Не удалось прочитать CSV: {e}")
    _check_columns(df, RETURNS_REQUIRED, "returns.csv")
    try:
        df["дата"] = pd.to_datetime(df["дата"], format="%Y-%m-%d")
        df["количество_возвратов"] = pd.to_numeric(df["количество_возвратов"], errors="raise").astype(int)
    except Exception as e:
        raise ValueError(f"Ошибка типов данных: {e}")
    return df


def parse_stock(file) -> pd.DataFrame:
    try:
        df = pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"Не удалось прочитать CSV: {e}")
    _check_columns(df, STOCK_REQUIRED, "stock.csv")
    try:
        df["остаток"] = pd.to_numeric(df["остаток"], errors="raise").astype(int)
    except Exception as e:
        raise ValueError(f"Ошибка типов данных: {e}")
    return df
