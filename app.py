import io
import os
import urllib.request
import zipfile
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="East Africa Retail Supply Chain Analytics",
    layout="wide",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_FILE = os.path.join(BASE_DIR, "sql", "supply_chain_analytics_queries.sql")

KAGGLE_STORE_URL = (
    "https://www.kaggle.com/api/v1/datasets/download/"
    "anirudhchauhan/retail-store-inventory-forecasting-dataset"
)
KAGGLE_ORDERS_URL = (
    "https://www.kaggle.com/api/v1/datasets/download/"
    "akalyanbce/inventory-supply-chain-dataset"
)

# Standardise benchmark codes to our 4-country East African retail network
REGION_MAP = {
    "South": "Kenya",
    "North": "Uganda",
    "East": "Tanzania",
    "West": "Rwanda",
}
ISO_MAP = {
    "Kenya": "KEN",
    "Uganda": "UGA",
    "Tanzania": "TZA",
    "Rwanda": "RWA",
}
WH_MAP = {
    "Warehouse 1": "Mombasa Port Hub",
    "Warehouse 2": "Nairobi Central Hub",
    "Warehouse 3": "Kampala Regional Hub",
}
SEASON_MAP = {
    "Autumn": "Q4 Festive (Oct-Dec)",
    "Winter": "Q1 Back-to-School (Jan-Mar)",
    "Spring": "Q2 Long Rains (Apr-Jun)",
    "Summer": "Q3 Mid-Year Dry (Jul-Sep)",
}


def find_local_csv(candidate_names):
    lower_targets = {name.lower() for name in candidate_names}
    for root, _, files in os.walk(BASE_DIR):
        if "venv" in root or ".git" in root:
            continue
        for fname in files:
            if fname.lower() in lower_targets:
                return os.path.join(root, fname)
    return None


def download_csv_from_kaggle(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        zip_bytes = io.BytesIO(resp.read())
    with zipfile.ZipFile(zip_bytes) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        with zf.open(csv_names[0]) as csv_file:
            return pd.read_csv(csv_file)


@st.cache_data
def load_data():
    # 1. Load daily retail store inventory data
    store_path = find_local_csv(
        ["retail_store_inventory.csv", "clean_store_inventory.csv"]
    )
    if store_path:
        store_df = pd.read_csv(store_path)
    else:
        store_df = download_csv_from_kaggle(KAGGLE_STORE_URL)

    if "Demand Forecast" in store_df.columns:
        store_df = store_df.drop(columns=["Demand Forecast"])

    store_df["Region"] = store_df["Region"].replace(REGION_MAP)
    store_df["Seasonality"] = store_df["Seasonality"].replace(SEASON_MAP)
    store_df["ISO_Code"] = store_df["Region"].map(ISO_MAP)
    store_df["Date"] = pd.to_datetime(store_df["Date"])
    store_df["YearMonth"] = store_df["Date"].dt.to_period("M").astype(str)
    store_df["Net_Price"] = store_df["Price"] * (1.0 - store_df["Discount"] / 100.0)
    store_df["Net_Revenue"] = store_df["Units Sold"] * store_df["Net_Price"]
    store_df["Near_Stockout"] = (
        store_df["Inventory Level"] <= store_df["Units Sold"] * 1.10
    ).astype(int)

    # 2. Load warehouse and supplier order data
    orders_path = find_local_csv(
        [
            "supply_chain_orders.csv",
            "inventory supply chain dataset.csv",
            "clean_supply_chain_orders.csv",
        ]
    )
    if orders_path:
        orders_df = pd.read_csv(orders_path)
    else:
        orders_df = download_csv_from_kaggle(KAGGLE_ORDERS_URL)

    orders_df["Region"] = orders_df["Region"].replace(REGION_MAP)
    orders_df["Warehouse"] = orders_df["Warehouse"].replace(WH_MAP)
    orders_df["Order_Date"] = pd.to_datetime(orders_df["Date"], dayfirst=True)
    orders_df["Holding_Stock_Est"] = orders_df["Inventory Level"] * (
        orders_df["Cost of Goods Sold (COGS)"]
        / (orders_df["Units Sold"] + orders_df["Inventory Level"])
    )

    return store_df, orders_df


store_df, orders_df = load_data()

# Page Header
st.title("East Africa Retail Supply Chain and Inventory Analytics")
st.caption(
    "Capstone Project | Zindua School Data Analytics | Student: Denis Urodho | "
    "Operations Across Kenya, Uganda, Tanzania & Rwanda (Consolidated in USD)"
)

# Sidebar Filters
st.sidebar.header("Filter Dashboard")

countries = ["All"] + sorted(store_df["Region"].unique().tolist())
selected_country = st.sidebar.selectbox("Country Market", countries)

store_categories = ["All"] + sorted(store_df["Category"].unique().tolist())
selected_store_cat = st.sidebar.selectbox("Store Product Category", store_categories)

stores = ["All"] + sorted(store_df["Store ID"].unique().tolist())
selected_store = st.sidebar.selectbox("Branch Store ID", stores)

seasons = ["All"] + sorted(store_df["Seasonality"].unique().tolist())
selected_season = st.sidebar.selectbox("Retail Quarter / Season", seasons)

st.sidebar.divider()
st.sidebar.subheader("Logistics Hub & Supplier Filters")

warehouses = ["All"] + sorted(orders_df["Warehouse"].unique().tolist())
selected_warehouse = st.sidebar.selectbox("Regional Warehouse Hub", warehouses)

suppliers = ["All"] + sorted(orders_df["Supplier"].unique().tolist())
selected_supplier = st.sidebar.selectbox("Supplier", suppliers)

# Apply filters to Store dataframe
f_store = store_df.copy()
if selected_country != "All":
    f_store = f_store[f_store["Region"] == selected_country]
if selected_store_cat != "All":
    f_store = f_store[f_store["Category"] == selected_store_cat]
if selected_store != "All":
    f_store = f_store[f_store["Store ID"] == selected_store]
if selected_season != "All":
    f_store = f_store[f_store["Seasonality"] == selected_season]

# Apply filters to Orders dataframe
f_orders = orders_df.copy()
if selected_country != "All":
    f_orders = f_orders[f_orders["Region"] == selected_country]
if selected_store_cat in ["Clothing", "Electronics", "Furniture"]:
    f_orders = f_orders[f_orders["Category"] == selected_store_cat]
if selected_warehouse != "All":
    f_orders = f_orders[f_orders["Warehouse"] == selected_warehouse]
if selected_supplier != "All":
    f_orders = f_orders[f_orders["Supplier"] == selected_supplier]

# Top KPI Summary Row
total_rev = f_store["Net_Revenue"].sum()
avg_dos = (
    f_store["Inventory Level"].mean() / f_store["Units Sold"].mean()
    if len(f_store) > 0 and f_store["Units Sold"].mean() > 0
    else 0
)
risk_rate = f_store["Near_Stockout"].mean() * 100 if len(f_store) > 0 else 0
avg_lead = f_orders["Lead Time (Days)"].mean() if len(f_orders) > 0 else 0
backorder_rate = f_orders["Backorder"].mean() * 100 if len(f_orders) > 0 else 0
wh_util = (
    (f_orders["Inventory Level"].mean() / f_orders["Warehouse Capacity"].mean()) * 100
    if len(f_orders) > 0 and f_orders["Warehouse Capacity"].mean() > 0
    else 0
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Net Retail Sales", f"${total_rev / 1e6:,.2f}M")
k2.metric("Days of Supply", f"{avg_dos:.2f} days")
k3.metric("Stock-Out Risk Rate", f"{risk_rate:.2f}%")
k4.metric("Hub Capacity Used", f"{wh_util:.1f}%")
k5.metric("Avg Corridor Lead Time", f"{avg_lead:.1f} days")
k6.metric("Backorder Rate", f"{backorder_rate:.2f}%")

st.divider()

# Four Analytical Dimensions in Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "1. Stock Availability",
        "2. Capital Efficiency",
        "3. Demand Stability",
        "4. Supplier & SKU Reliability",
        "SQL Queries",
    ]
)

# -------------------------------------------------------------------------
# TAB 1: STOCK AVAILABILITY
# -------------------------------------------------------------------------
with tab1:
    st.subheader("1. Stock Availability Across East Africa")
    st.write("Question: Are enough products on the shelf across Kenya, Uganda, Tanzania, and Rwanda when customers want them?")

    col_left, col_right = st.columns([1.1, 1])

    with col_left:
        if len(f_store) > 0:
            map_df = (
                f_store.groupby(["Region", "ISO_Code"], as_index=False)
                .agg(
                    Risk_Pct=("Near_Stockout", "mean"),
                    Avg_Stock=("Inventory Level", "mean"),
                    Avg_Sales=("Units Sold", "mean"),
                    Net_Revenue=("Net_Revenue", "sum"),
                )
            )
            map_df["Risk_Pct"] = (map_df["Risk_Pct"] * 100).round(2)
            map_df["Days_of_Supply"] = (map_df["Avg_Stock"] / map_df["Avg_Sales"]).round(2)

            fig_map = px.choropleth(
                map_df,
                locations="ISO_Code",
                color="Risk_Pct",
                hover_name="Region",
                hover_data={"ISO_Code": False, "Risk_Pct": True, "Days_of_Supply": True},
                color_continuous_scale="YlOrRd",
                scope="africa",
                title="East Africa Stock-Out Risk (%) by Country Market",
                labels={"Risk_Pct": "Risk %"},
            )
            fig_map.update_geos(
                lataxis_range=[-12.5, 5.5],
                lonaxis_range=[28.0, 42.5],
                showcountries=True,
                countrycolor="#cbd5e1",
            )
            fig_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=340)
            st.plotly_chart(fig_map, width="stretch")

            pivot_risk = (
                f_store.groupby(["Region", "Store ID"])["Near_Stockout"]
                .mean()
                .mul(100)
                .round(2)
                .unstack("Store ID")
            )
            fig_heat = px.imshow(
                pivot_risk,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="YlOrRd",
                title="Stock-Out Risk (%) by Country and Branch Store",
                labels={"color": "Risk %", "y": "Country"},
            )
            st.plotly_chart(fig_heat, width="stretch")

    with col_right:
        st.markdown("**High-Risk Products and Priority Reorder Flags**")
        if len(f_store) > 0:
            sku_store = (
                f_store.groupby(["Product ID", "Category", "Store ID", "Region"], as_index=False)
                .agg(
                    Avg_Stock=("Inventory Level", "mean"),
                    Avg_Daily_Sales=("Units Sold", "mean"),
                    Risk_Pct=("Near_Stockout", "mean"),
                )
            )
            sku_store["Days_of_Supply"] = (
                sku_store["Avg_Stock"] / sku_store["Avg_Daily_Sales"]
            ).round(2)
            sku_store["Risk_Pct"] = (sku_store["Risk_Pct"] * 100).round(2)

            def get_reorder_status(row):
                if row["Risk_Pct"] >= 12.5 or row["Days_of_Supply"] < 1.92:
                    return "Priority Reorder"
                elif row["Risk_Pct"] >= 10.5 or row["Days_of_Supply"] < 2.02:
                    return "Watch Buffer"
                return "Healthy"

            sku_store["Action"] = sku_store.apply(get_reorder_status, axis=1)
            sku_store = sku_store.rename(columns={"Region": "Country"}).sort_values(
                "Risk_Pct", ascending=False
            ).head(16)
            st.dataframe(
                sku_store[
                    [
                        "Product ID",
                        "Category",
                        "Store ID",
                        "Country",
                        "Days_of_Supply",
                        "Risk_Pct",
                        "Action",
                    ]
                ],
                width="stretch",
                hide_index=True,
            )

# -------------------------------------------------------------------------
# TAB 2: INVENTORY CAPITAL EFFICIENCY
# -------------------------------------------------------------------------
with tab2:
    st.subheader("2. Inventory Capital Efficiency Across Regional Hubs")
    st.write("Question: Where is working capital productive versus tied up in holding stock and corridor transport costs?")

    c1, c2 = st.columns([1.15, 1])

    with c1:
        if len(f_orders) > 0:
            cat_cap = (
                f_orders.groupby("Category", as_index=False)
                .agg(
                    Active_COGS=("Cost of Goods Sold (COGS)", "sum"),
                    Est_Holding_Stock=("Holding_Stock_Est", "sum"),
                    Transport_Cost=("Transportation Cost", "sum"),
                )
            )
            cat_melted = cat_cap.melt(
                id_vars="Category",
                value_vars=["Active_COGS", "Est_Holding_Stock", "Transport_Cost"],
                var_name="Cost_Component",
                value_name="USD_Amount",
            )
            cat_melted["Cost_Component"] = cat_melted["Cost_Component"].replace(
                {
                    "Active_COGS": "Sold COGS",
                    "Est_Holding_Stock": "Estimated Holding Stock",
                    "Transport_Cost": "Corridor Transport Cost",
                }
            )
            fig_stack = px.bar(
                cat_melted,
                x="Category",
                y="USD_Amount",
                color="Cost_Component",
                barmode="stack",
                title="Stacked Capital Breakdown by Supply Chain Category (USD)",
                labels={"USD_Amount": "Amount (USD)", "Cost_Component": "Component"},
            )
            st.plotly_chart(fig_stack, width="stretch")
        else:
            st.info("No warehouse order rows match the selected category filter.")

    with c2:
        if len(f_orders) > 0:
            wh_summary = (
                f_orders.groupby("Warehouse", as_index=False)
                .agg(
                    Avg_Inventory=("Inventory Level", "mean"),
                    Avg_Capacity=("Warehouse Capacity", "mean"),
                    Total_COGS=("Cost of Goods Sold (COGS)", "sum"),
                    Orders=("Date", "count"),
                )
            )
            wh_summary["Utilisation_Pct"] = (
                wh_summary["Avg_Inventory"] / wh_summary["Avg_Capacity"] * 100
            ).round(2)

            fig_wh = px.bar(
                wh_summary,
                x="Utilisation_Pct",
                y="Warehouse",
                orientation="h",
                text="Utilisation_Pct",
                title="Regional Hub Capacity Utilisation (%)",
                labels={"Utilisation_Pct": "Capacity Used (%)", "Warehouse": "Hub"},
            )
            st.plotly_chart(fig_wh, width="stretch")

            status_counts = (
                f_orders.groupby(["Warehouse", "Order Status"])
                .size()
                .unstack(fill_value=0)
                .reset_index()
            )
            st.markdown("**Order Fulfilment Breakdown by Regional Hub**")
            st.dataframe(status_counts, width="stretch", hide_index=True)

# -------------------------------------------------------------------------
# TAB 3: DEMAND AND REPLENISHMENT STABILITY
# -------------------------------------------------------------------------
with tab3:
    st.subheader("3. Demand and Price Stability Over Time")
    st.write("Question: How do sales, stock levels, and net selling prices shift across months, East African retail quarters, and promotions?")

    sku_options = ["All Products"] + sorted(store_df["Product ID"].unique().tolist())
    chosen_sku = st.selectbox("Filter Trend by Product ID (SKU)", sku_options)

    trend_source = f_store[f_store["Date"] < "2024-01-01"].copy()
    if chosen_sku != "All Products":
        trend_source = trend_source[trend_source["Product ID"] == chosen_sku]

    if len(trend_source) > 0:
        monthly = (
            trend_source.groupby("YearMonth", as_index=False)
            .agg(
                Units_Sold=("Units Sold", "sum"),
                Avg_Inventory=("Inventory Level", "mean"),
                Avg_Net_Price=("Net_Price", "mean"),
            )
            .sort_values("YearMonth")
        )
        monthly["Avg_Inventory"] = monthly["Avg_Inventory"].round(1)
        monthly["Avg_Net_Price"] = monthly["Avg_Net_Price"].round(2)

        fig_line = px.line(
            monthly,
            x="YearMonth",
            y="Units_Sold",
            markers=True,
            title="Monthly Units Sold Trend (Jan 2022 to Dec 2023)",
            labels={"YearMonth": "Month", "Units_Sold": "Total Units Sold"},
        )
        st.plotly_chart(fig_line, width="stretch")

        sc1, sc2 = st.columns(2)
        with sc1:
            season_df = (
                trend_source.groupby("Seasonality", as_index=False)
                .agg(
                    Total_Units=("Units Sold", "sum"),
                    Avg_Daily_Units=("Units Sold", "mean"),
                    Avg_Net_Price=("Net_Price", "mean"),
                )
                .sort_values("Total_Units", ascending=False)
            )
            season_df["Avg_Daily_Units"] = season_df["Avg_Daily_Units"].round(1)
            season_df["Avg_Net_Price"] = season_df["Avg_Net_Price"].round(2)
            fig_season = px.bar(
                season_df,
                x="Seasonality",
                y="Total_Units",
                text="Total_Units",
                title="Total Units Sold by East African Retail Quarter",
                labels={"Seasonality": "Retail Quarter"},
            )
            st.plotly_chart(fig_season, width="stretch")

        with sc2:
            st.markdown("**Promotion vs Normal Day Comparison**")
            promo_summary = (
                trend_source.groupby("Holiday/Promotion", as_index=False)
                .agg(
                    Store_Days=("Units Sold", "count"),
                    Avg_Units_Sold=("Units Sold", "mean"),
                    Avg_Discount_Pct=("Discount", "mean"),
                    Avg_Net_Price=("Net_Price", "mean"),
                )
            )
            promo_summary["Day_Type"] = promo_summary["Holiday/Promotion"].map(
                {0: "Normal Day", 1: "Promotion / Holiday"}
            )
            promo_summary["Avg_Units_Sold"] = promo_summary["Avg_Units_Sold"].round(1)
            promo_summary["Avg_Discount_Pct"] = promo_summary["Avg_Discount_Pct"].round(1)
            promo_summary["Avg_Net_Price"] = promo_summary["Avg_Net_Price"].round(2)
            st.dataframe(
                promo_summary[
                    ["Day_Type", "Store_Days", "Avg_Units_Sold", "Avg_Discount_Pct", "Avg_Net_Price"]
                ],
                width="stretch",
                hide_index=True,
            )
            st.caption(
                "Insight: Average discounts stay around 10% on both normal and promo days, "
                "which explains why promotions did not lift average daily unit sales."
            )

# -------------------------------------------------------------------------
# TAB 4: SUPPLIER AND SKU RELIABILITY
# -------------------------------------------------------------------------
with tab4:
    st.subheader("4. Supplier and Product Reliability")
    st.write("Question: Which products and suppliers help or bottleneck East African operations the most?")

    ctl1, ctl2, ctl3 = st.columns(3)
    rank_direction = ctl1.radio("Ranking View", ["Top N", "Bottom N"], horizontal=True)
    rank_metric_label = ctl2.selectbox(
        "Rank Products By",
        ["Stock-Out Risk (%)", "Net Revenue ($)", "Days of Supply"],
    )
    rank_n = ctl3.selectbox("Number of Products (N)", [5, 8, 10], index=1)

    r_left, r_right = st.columns([1.05, 1])

    with r_left:
        if len(f_store) > 0:
            sku_perf = (
                f_store.groupby(["Product ID", "Category"], as_index=False)
                .agg(
                    Net_Revenue=("Net_Revenue", "sum"),
                    Avg_Stock=("Inventory Level", "mean"),
                    Avg_Sales=("Units Sold", "mean"),
                    Risk_Pct=("Near_Stockout", "mean"),
                )
            )
            sku_perf["Days_of_Supply"] = (sku_perf["Avg_Stock"] / sku_perf["Avg_Sales"]).round(2)
            sku_perf["Risk_Pct"] = (sku_perf["Risk_Pct"] * 100).round(2)
            sku_perf["Net_Revenue"] = sku_perf["Net_Revenue"].round(0)

            col_map = {
                "Stock-Out Risk (%)": "Risk_Pct",
                "Net Revenue ($)": "Net_Revenue",
                "Days of Supply": "Days_of_Supply",
            }
            target_col = col_map[rank_metric_label]
            ascending_flag = rank_direction == "Bottom N"
            ranked_df = sku_perf.sort_values(target_col, ascending=ascending_flag).head(rank_n)

            fig_rank = px.bar(
                ranked_df.iloc[::-1],
                x=target_col,
                y="Product ID",
                color="Category",
                orientation="h",
                text=target_col,
                title=f"{rank_direction} ({rank_n}) Products by {rank_metric_label}",
            )
            st.plotly_chart(fig_rank, width="stretch")

    with r_right:
        st.markdown("**Supplier Reliability Scorecard**")
        if len(f_orders) > 0:
            sup_df = (
                f_orders.groupby("Supplier", as_index=False)
                .agg(
                    Orders=("Date", "count"),
                    Avg_Lead_Days=("Lead Time (Days)", "mean"),
                    Accuracy_Pct=("Order Accuracy", "mean"),
                    Backorder_Pct=("Backorder", "mean"),
                    Cancelled_Orders=("Order Status", lambda s: (s == "Canceled").sum()),
                )
            )
            sup_df["Avg_Lead_Days"] = sup_df["Avg_Lead_Days"].round(2)
            sup_df["Accuracy_Pct"] = (sup_df["Accuracy_Pct"] * 100).round(2)
            sup_df["Backorder_Pct"] = (sup_df["Backorder_Pct"] * 100).round(2)
            sup_df["Cancelled_Pct"] = (
                sup_df["Cancelled_Orders"] / sup_df["Orders"] * 100
            ).round(2)
            sup_df = sup_df.sort_values("Backorder_Pct", ascending=False)

            st.dataframe(
                sup_df[
                    [
                        "Supplier",
                        "Orders",
                        "Avg_Lead_Days",
                        "Accuracy_Pct",
                        "Backorder_Pct",
                        "Cancelled_Pct",
                    ]
                ],
                width="stretch",
                hide_index=True,
            )
            st.caption(
                "Supplier D has the highest backorder rate (12.21%), Supplier B has the slowest "
                "lead time (16.17 days), and Supplier C has the highest cancellation rate (10.91%)."
            )

# -------------------------------------------------------------------------
# TAB 5: SQL QUERIES REFERENCE
# -------------------------------------------------------------------------
with tab5:
    st.subheader("SQL Verification Queries")
    st.write("These SQL queries compute the same KPIs directly on the relational tables.")
    sql_path = find_local_csv(["supply_chain_analytics_queries.sql"]) or SQL_FILE
    if os.path.exists(sql_path):
        with open(sql_path, "r", encoding="utf-8") as f:
            st.code(f.read(), language="sql")
    else:
        st.info("Add sql/supply_chain_analytics_queries.sql to your GitHub repo to display the SQL code here.")
