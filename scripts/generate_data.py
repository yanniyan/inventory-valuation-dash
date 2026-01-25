import numpy as np 
import pandas as pd
import os
np.random.seed(42)

# Core definitions - SKU + Locations 
months = pd.period_range("2024-01", periods=12, freq="M").astype(str)

flavours = [
    "Matcha",
    "Acai",
    "Coconut",
    "Turmeric",
    "Ginger Lemon",
    "Berry Fusion",
    "Cacao",
    "Vanilla Chai",
    "Raspberry",
    "Pistachio",
]

variations = ["Original", "Plus"]

finished_skus = [
    f"{flavour} {variation}"
    for flavour in flavours
    for variation in variations
]

raw_materials = ["RM_Original", "RM_Plus"]
packaging_skus = ["Pack_Small", "Pack_Large"]

locations = [
    "EU_North",
    "EU_Central",
    "EU_South",
    "EU_West",
    "EU_East",
    "Amazon_FBA",
    "TikTok_FBT",
    "Shopify_FC",
    "Factory_A",
    "Factory_B",
    "Inbound_Transit",
    "Interwarehouse_Transit",
]

# Cost structure
raw_costs = {"RM_Original": 7.0, "RM_Plus": 9.0}
pack_costs = {"Pack_Small": 0.55, "Pack_Large": 0.95}

# Finished goods unit cost assumptions (simplified)
# Assume Original uses RM_Original + Pack_Small, Plus uses RM_Plus + Pack_Large
finished_unit_cost = {}
for sku in finished_skus:
    if "Original" in sku:
        finished_unit_cost[sku] = 8.5  # e.g. 8.5 EUR per unit
    else:
        finished_unit_cost[sku] = 11.0  # e.g. 11 EUR per unit

# -------------------------
# Behaviour weights (top / mid / slow movers)
# -------------------------
top_sellers = ["Matcha", "Berry Fusion", "Vanilla Chai"]
slow_movers = ["Turmeric", "Ginger Lemon", "Pistachio"]

def sku_demand_profile(sku_name: str):
    flavour = sku_name.split()[0]  # crude but works for our naming
    if any(flavour in f for f in top_sellers):
        base = np.random.randint(2500, 4500)
    elif any(flavour in f for f in slow_movers):
        base = np.random.randint(300, 900)
    else:
        base = np.random.randint(1200, 2500)
    return base

# -------------------------
# Generate finished goods inventory
# -------------------------
rows = []

for month in months:
    # seasonality factor (Jan–Mar high, summer dip, Q4 ramp)
    m = int(month.split("-")[1])
    if m in [1, 2, 3]:
        season_factor = 1.2
    elif m in [6, 7, 8]:
        season_factor = 0.85
    elif m in [11, 12]:
        season_factor = 1.15
    else:
        season_factor = 1.0

    for sku in finished_skus:
        base_units = sku_demand_profile(sku)
        # add some month-to-month noise
        monthly_units = int(base_units * season_factor * np.random.uniform(0.7, 1.3))

        # distribute across locations (warehouses + marketplaces + transit)
        loc_weights = np.random.dirichlet(np.ones(len(locations)), size=1)[0]
        for loc, w in zip(locations, loc_weights):
            units = int(monthly_units * w * np.random.uniform(0.8, 1.2))
            if units <= 0:
                continue

            unit_cost = finished_unit_cost[sku]
            value = units * unit_cost

            rows.append(
                {
                    "month": month,
                    "sku": sku,
                    "variation": "Original" if "Original" in sku else "Plus",
                    "category": "Finished",
                    "location": loc,
                    "inventory_units": units,
                    "unit_cost": round(unit_cost, 2),
                    "inventory_value": round(value, 2),
                }
            )
# Generate raw materials inventory
for month in months:
    for rm in raw_materials:
        for loc in ["Factory_A", "Factory_B", "Inbound_Transit"]:
            # raw stock in kg
            base_stock = np.random.randint(2000, 8000)
            units = int(base_stock * np.random.uniform(0.7, 1.3))
            unit_cost = raw_costs[rm]
            value = units * unit_cost

            rows.append(
                {
                    "month": month,
                    "sku": rm,
                    "variation": None,
                    "category": "Raw",
                    "location": loc,
                    "inventory_units": units,
                    "unit_cost": round(unit_cost, 2),
                    "inventory_value": round(value, 2),
                }
            )
# Generate packaging inventory
for month in months:
    for pack in packaging_skus:
        for loc in ["Factory_A", "Factory_B"]:
            base_stock = np.random.randint(10000, 40000)
            units = int(base_stock * np.random.uniform(0.7, 1.3))
            unit_cost = pack_costs[pack]
            value = units * unit_cost

            rows.append(
                {
                    "month": month,
                    "sku": pack,
                    "variation": None,
                    "category": "Packaging",
                    "location": loc,
                    "inventory_units": units,
                    "unit_cost": round(unit_cost, 2),
                    "inventory_value": round(value, 2),
                }
            )
# Build DataFrame and check total valuation
df = pd.DataFrame(rows)

total_valuation = df["inventory_value"].sum()
print(f"Total valuation: €{total_valuation:,.0f}")

# Save to CSV
os.makedirs("data", exist_ok=True)
df.to_csv("../data/inventory_valuation_12m.csv", index=False)
df.head()
