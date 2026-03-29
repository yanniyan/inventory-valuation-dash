import pandas as pd

# ---------------------------------------------------
# FILTERING & NORMALIZATION
# ---------------------------------------------------

def normalize_filters(selected_skus, selected_locations, df):
    """Ensure filters are never empty by falling back to full dataset."""
    if not selected_skus:
        selected_skus = df["sku"].unique()
    if not selected_locations:
        selected_locations = df["location"].unique()
    return selected_skus, selected_locations


def filter_df(df, skus, locations):
    """Apply SKU + location filters once and return a clean copy."""
    return df[
        df["sku"].isin(skus) &
        df["location"].isin(locations)
    ].copy()


# ---------------------------------------------------
# TIME SPLITTING
# ---------------------------------------------------

def split_latest_previous(df_filtered):
    """Return df_latest and df_previous based on the most recent month."""
    latest_month = df_filtered["date"].max()
    df_latest = df_filtered[df_filtered["date"] == latest_month].copy()

    previous_month = df_filtered[df_filtered["date"] < latest_month]["date"].max()
    df_previous = (
        df_filtered[df_filtered["date"] == previous_month].copy()
        if pd.notna(previous_month)
        else pd.DataFrame()
    )

    return df_latest, df_previous


# ---------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------

def compute_inventory_kpis(df_latest, df_previous):
    """Return total_value, total_units, sku_count, change_text."""
    total_value = df_latest["value"].sum()
    total_units = df_latest["quantity"].sum()
    sku_count = df_latest["sku"].nunique()

    previous_value = df_previous["value"].sum() if not df_previous.empty else 0
    change = total_value - previous_value

    if change > 0:
        change_text = f"+€{change:,.0f}"
    elif change < 0:
        change_text = f"-€{abs(change):,.0f}"
    else:
        change_text = "€0"

    return total_value, total_units, sku_count, change_text


def compute_turnover(df_latest, df_previous, mode):
    """Return formatted turnover KPI."""
    units_latest = df_latest["quantity"].sum()
    units_previous = df_previous["quantity"].sum() if not df_previous.empty else 0

    units_moved = max(0, units_previous - units_latest)
    avg_units = (units_previous + units_latest) / 2 if (units_previous + units_latest) > 0 else 0

    ratio = units_moved / avg_units if avg_units > 0 else 0

    if mode == "percent":
        return f"{ratio * 100:.1f}%"
    return f"{ratio:.2f} turns/month"


def compute_top_location(df_filtered):
    """Return location with highest total value."""
    if df_filtered.empty:
        return "N/A"
    return df_filtered.groupby("location")["value"].sum().idxmax()


# ---------------------------------------------------
# AGGREGATIONS FOR CHARTS & TABLES
# ---------------------------------------------------

def aggregate_valuation(df_filtered):
    """Return aggregated valuation for the line chart."""
    return (
        df_filtered.groupby("date", as_index=False)["value"]
        .sum()
        .sort_values("date")
    )


def prepare_monthly_summary(df_filtered):
    """Return summary table data for the dashboard."""
    df_filtered = df_filtered.copy()
    df_filtered["month"] = df_filtered["date"].dt.strftime("%Y-%m")

    summary = (
        df_filtered.groupby(["month", "location"])
        .agg(
            total_value=("value", "sum"),
            units=("quantity", "sum"),
            sku_count=("sku", "nunique"),
        )
        .reset_index()
        .sort_values(["month", "location"])
    )

    return summary.to_dict("records")


# ---------------------------------------------------
# EXPORT TABLE (UNITS + VALUE PER LOCATION)
# ---------------------------------------------------

def prepare_export_table(df_filtered):
    """
    Create a pivot table with months as rows and locations as columns,
    showing BOTH units and value per location.
    Output format example:
        month | Berlin_units | Berlin_value | Munich_units | Munich_value | ...
    """
    df_filtered = df_filtered.copy()
    df_filtered["month"] = df_filtered["date"].dt.strftime("%Y-%m")

    # Pivot for units
    units_pivot = df_filtered.pivot_table(
        index="month",
        columns="location",
        values="quantity",
        aggfunc="sum",
        fill_value=0
    )

    # Pivot for value
    value_pivot = df_filtered.pivot_table(
        index="month",
        columns="location",
        values="value",
        aggfunc="sum",
        fill_value=0
    )

    # Rename columns to distinguish units/value
    units_pivot = units_pivot.add_suffix("_units")
    value_pivot = value_pivot.add_suffix("_value")

    # Merge into one export table
    export_df = units_pivot.join(value_pivot, how="outer").reset_index()

    return export_df
