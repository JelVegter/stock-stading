import pandas as pd


def calculcate_returns_percentage(
    df: pd.DataFrame, wide_form: bool = True
) -> pd.DataFrame:
    if wide_form:
        for col in df.columns:
            if col == "Date":
                continue
            df[col] = df[col].pct_change(1) * 100
    else:

        df = (
            df.groupby(by=["Date"])
            .mean(numeric_only=True)
            .reset_index()
            .sort_values(by="Date")
        )
        df["returns_percentage"] = df["price_close"].pct_change(1) * 100
    return df
