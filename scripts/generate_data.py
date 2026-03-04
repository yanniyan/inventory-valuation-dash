import pandas as pd
import numpy as np

np.random.seed(42)

# ---------------------------------------------------
# SKU + VARIATION CONFIGURATION
# ---------------------------------------------------

# Top movers
top_skus = [
    "classic",
    "wild_berry_burst",
    "tropical_citrus"
]

# Mid-tier SKUs
other_skus = [
    "peach_hibiscus",
    "apple_elderflower",
    "mango_passion",
    "raspberry_lime",
    "pineapple_ginger"
]

skus = top_skus + other_skus
variations = ["original", "plus"]

# Category (all beverages for now)
category = "beverage"

# Unit costs (COGS, not sales price)
unit_cost_map = {
    "original": 10,
    "plus": 12,
}

# ---------------------------------------------------
# LOCATION CONFIGURATION
# ---------------------------------------------------

factories = ["factory_a", "factory_b"]
tpls = ["3pl_north", "3pl_south"]
marketplaces = ["amazon", "tiktok", "dtc"]
transit = ["in_transit"]

all_locations = factories + tpls + marketplaces + transit

def location_type(loc):
    if loc in factories:
        return "factory"
    if loc in tpls:
        return "3pl"
    if loc in marketplaces:
        return "marketplace"
    if loc in transit:
        return "transit"
    return "other"

# ---------------------------------------------------
# DATE RANGE
# ---------------------------------------------------

start = "2022-01-01"
end = pd.Timestamp.today().replace(day=1)
months = pd.date_range(start=start, end=end, freq="MS")

# Growth curve
growth_factor = []
for date in months:
    if date.year < 2024:
        growth_factor.append(0.75)
    elif date.year == 2024:
        growth_factor.append(1.0)
    else:
        growth_factor.append(1.25)

# ---------------------------------------------------
# BASE UNITS BY LOCATION TYPE
# ---------------------------------------------------

def base_units_for_location(loc_type):
    if loc_type == "3pl":
        return np.random.randint(3000, 5000)
    if loc_type == "factory":
        return np.random.randint(1000, 2000)
    if loc_type == "marketplace":
        return np.random.randint(300, 700)
    if loc_type == "transit":
        return np.random.randint(150, 400)
    return np.random.randint(500, 1500)

# ---------------------------------------------------
# DATA GENERATION
# ---------------------------------------------------

rows = []

for sku in skus:
    for variation in variations:
        cost = unit_cost_map[variation]

        for loc in all_locations:
            loc_type = location_type(loc)
            base_units = base_units_for_location(loc_type)

            # Velocity multipliers
            if sku == "classic" and variation == "original":
                base_units *= 1.6
            elif sku == "classic" and variation == "plus":
                base_units *= 1.4
            elif sku in ["wild_berry_burst", "tropical_citrus"]:
                base_units *= 1.25

            for i, date in enumerate(months):
                units = int(
                    base_units *
                    growth_factor[i] *
                    np.random.uniform(0.9, 1.1)
                )
                value = units * cost

                rows.append([
                    date,
                    sku,
                    variation,
                    category,
                    loc,
                    units,
                    cost,
                    value
                ])

df = pd.DataFrame(
    rows,
    columns=[
        "month",
        "sku",
        "variation",
        "category",
        "location",
        "inventory_units",
        "unit_cost",
        "inventory_value",
    ],
)

df.to_csv("data/inventory_valuation.csv", index=False)

# ---------------------------------------------------
# SANITY CHECK
# ---------------------------------------------------

latest = df["month"].max()
total_value = df[df["month"] == latest]["inventory_value"].sum()
print(f"Latest month: {latest}")
print(f"Total inventory value: €{total_value:,.0f}")
