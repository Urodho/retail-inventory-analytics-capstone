# Business Understanding: East Africa Retail Supply Chain and Inventory Analytics

**Capstone Project, Zindua School Data Analytics**  
**Student:** Denis Urodho | **Date:** 23 November 2026  
**Datasets Used:**
- [Retail Store Inventory Dataset (Kaggle)](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset) (73,100 daily store sales and inventory rows across 5 branches, 20 products, and 4 East African country markets: Kenya, Uganda, Tanzania, and Rwanda)
- [Inventory Supply Chain Dataset (Kaggle)](https://www.kaggle.com/datasets/akalyanbce/inventory-supply-chain-dataset) (1,200 replenishment order rows across 4 suppliers and 3 regional logistics hubs: Mombasa Port Hub, Nairobi Central Hub, and Kampala Regional Hub)

---

## 1. What Problem Am I Solving?

A regional retail chain operating across East Africa (Kenya, Uganda, Tanzania, and Rwanda) makes money when products are on the shelf at the moment a customer wants to buy them. At the same time, the company cannot afford to hold too much stock across its branches and regional hubs because unsold inventory ties up working capital, uses up warehouse space, and increases cross-border transport costs.

Supply chain and inventory management therefore sits at the centre of retail profitability. In day-to-day East African operations, two things make this hard to get right:
1. Customer demand shifts across retail quarters (such as Q4 Festive shopping and Q1 Back-to-School) and across country branches, so fast-moving items run low in one market while other categories pile up in a central hub.
2. Suppliers and freight corridors do not all perform at the same level. Long delivery lead times, inaccurate shipments, backorders, and cancelled orders make branch stock-outs much worse when procurement, hub, and store managers only check separate spreadsheets once a week.

Instead of building a machine learning forecast model (which goes outside the scope of this analytics project), I am solving this visibility problem using SQL analysis, Tableau dashboards, and a live Streamlit web app. The goal is to show managers where shelf stock is running low, where cash is stuck in slow-moving hub inventory, how demand behaves across retail quarters, and which suppliers are slowing operations down.

---

## 2. What Tools Did I Use and How Did I Get the Answers?

I used four main tools to take the raw Kaggle CSV files all the way to verified business answers:

- **Python (`pandas` and `numpy`):** Used to clean both CSV files, remove the pre-generated `Demand Forecast` column from the 73,100 store rows, standardise dates (`YYYY-MM-DD`), map benchmark region/warehouse/season codes to our 4-country East African retail network, calculate net selling price after discount (`Price * (1 - Discount / 100)`), and create a `near_stockout_flag` whenever `Inventory Level` fell within 10% of daily `Units Sold`.
- **SQL (SQLite / PostgreSQL / BigQuery syntax):** Loaded the cleaned tables into a relational database and wrote `GROUP BY` and `CASE WHEN` queries to verify every KPI before building charts.
- **Tableau and Streamlit (`plotly.express`):** Built interactive 4-dimension dashboards featuring a geographic East Africa risk map, conditional branch heatmaps, stacked capital breakdown charts, seasonal trend lines, and Top N / Bottom N product rankings, deployed publicly on Streamlit Community Cloud and Tableau Public.
- **VS Code and Git/GitHub:** Used to organise the Python code, SQL scripts, cleaned datasets, and project documentation.

---

## 3. Business Questions and How Our Data Answers Each One

Below are the 5 core business questions from my project plan, the analytical method used, and what our data actually shows:

| # | Business Question | Analytical Method Used | Data Columns Used & What the Data Actually Shows |
| :- | :--- | :--- | :--- |
| **1** | **Are the right products available across East African countries and branches, and which SKUs face immediate stock-out risk?** | SQL KPI aggregation, Days-of-Supply & safety-threshold rules | Using `Region` (Country), `Store ID`, `Product ID`, `Inventory Level`, and `Units Sold`: branches hold an average of only **2.01 Days of Supply** (`274.5` units on hand vs `136.5` sold per day). Out of 73,100 branch-days, **6,799 days (9.30%)** came within 10% of running out. **Tanzania** has the highest overall stock-out risk (**9.62%**), followed by **Uganda (9.52%)**, **Rwanda (9.07%)**, and **Kenya (8.99%)**. Combinations like *Tanzania Groceries in Branch S001 (11.37%)* and *SKU P0004 Furniture (1.91 Days of Supply)* require priority reorder flags. |
| **2** | **Where is working capital tied up in excess stock, high warehouse utilisation, or corridor transport costs?** | Inventory turnover, COGS vs. holding analysis & stacked comparisons | Using `Category`, `Warehouse`, `Cost of Goods Sold (COGS)`, `Inventory Level`, `Warehouse Capacity`, and `Transportation Cost`: total COGS is **$71.24M** (consolidated in USD across the 4 countries) with **$9.27M** spent on corridor transport. Overall hub capacity use is moderate (**33.4% at Kampala Regional Hub, 33.8% at Mombasa Port Hub, and 35.1% at Nairobi Central Hub**), yet stock is unevenly placed. For example, *Rwanda Clothing held at Nairobi Central Hub* sits at **44.51% capacity utilisation** (`3,238` avg units), tying up cash while Tanzania and Uganda branches run low. |
| **3** | **How do demand, stock levels, and effective prices fluctuate across months, retail quarters, and promotions?** | Historical time-series trend analysis & quarterly slicing (no ML) | Using `Date`, `Seasonality`, `Holiday/Promotion`, `Price`, `Discount`, and `Units Sold` from Jan 2022 to Dec 2023: sales are highest in **Q4 Festive Oct-Dec (2.51M units, 137.8/day)** and **Q1 Back-to-School Jan-Mar (2.50M units, 136.8/day)** compared to **Q3 Mid-Year Dry Jul-Sep (2.48M units, 135.4/day)**. Checking `Holiday/Promotion` also revealed a key finding: promo days averaged **136.4 units sold** vs **136.5 units** on normal days, because average discounts stayed flat at **10.0%** across both groups. |
| **4** | **Which suppliers deliver late, cancel orders, or generate high backorder and inaccuracy rates?** | Supplier lead-time & fulfilment scorecard (SQL & BI) | Using `Supplier`, `Lead Time (Days)`, `Order Status`, `Order Accuracy`, and `Backorder` across 1,200 hub orders: **Supplier D** has the worst backorder rate at **12.21%** (vs **7.05%** for Supplier A). **Supplier B** is the slowest to deliver at **16.17 days** on average, while **Supplier C** has the highest order cancellation rate (**10.91%**) and lowest order accuracy (**89.45%**). Overall, **362 out of 1,200 orders (30.2%)** sit Pending (`248`) or Cancelled (`114`). |
| **5** | **Which Top N / Bottom N products and categories drive profitability vs. operational bottlenecks?** | Ranked Top N / Bottom N Pareto & reorder priority views | Using net revenue (`Units Sold * Net Price`) and risk rates across all 20 SKUs and categories: **Furniture ($100.23M)** and **Groceries ($99.95M)** lead retail net sales, while **Electronics ($97.39M)** is lowest in branch sales yet highest in corridor transport spend (**$2.52M**). At SKU level, **P0020 ($25.50M)** and **P0011 ($25.46M)** generate the highest sales, while **P0012 ($24.11M)** and **P0002 ($24.17M)** sit at the bottom. Top earner **P0020** also carries an above-average stock-out risk (**9.71%**), making it a top priority to protect. |

---

## 4. Main Insights ("Aha!" Moments) and Practical Solutions

1. **A 2-day branch buffer cannot absorb a 16-day corridor lead time:** Country branches keep roughly 2 days of stock on the shelf, while supplier deliveries into Mombasa, Nairobi, and Kampala hubs take 15 to 16 days. Without an early reorder warning, any port or border delay turns straight into empty shelves in Tanzania and Uganda.
2. **Supplier bottlenecks show up in different ways:** Looking only at delivery speed would hide that **Supplier C** cancels **10.91%** of orders and gets over **10%** of shipments wrong, while **Supplier D** drives the highest backorders (**12.21%**).
3. **Flat 10% year-round discounts waste margin:** Promotions did not lift daily unit sales because non-promo days already carried the same 10% average discount.

### Practical Solutions Proposed
- **Automated Reorder Flag Table:** Flag any branch-SKU pair dropping below `1.95 Days of Supply` (or exceeding `12.5%` risk days) as `Priority Reorder`, protecting top earners like `P0020` and fast-moving `P0004`.
- **Supplier SLA Re-allocation:** Route urgent cross-border replenishment through **Supplier A** (`92.31%` accuracy, `7.05%` backorders, `15.23-day` lead time) and renegotiate penalties with **Supplier D** and **Supplier C**.
- **Pre-Festive & Back-to-School Stock Positioning:** Replace flat year-round discounts with targeted clearance markdowns on overstocked hub lines (such as *Rwanda Clothing in Nairobi Central Hub*), and build branch safety stock ahead of **Q4 Festive** and **Q1 Back-to-School** peaks.

**Do East African retailers actually need these solutions?** Yes. Regional supermarkets, FMCG distributors, and multi-country chains across Kenya, Uganda, Tanzania, and Rwanda work on thin net margins of 3% to 8%, deal with real Mombasa-Nairobi-Kampala-Kigali corridor delays, and rarely have large data science teams. A clear weekly reorder and supplier scorecard solves their exact Monday-morning problem.

---

## 5. How Would a Business Benefit from This Work?

- **Money Saved and Sales Protected:** Protects top-selling SKUs during the **9.3% of branch-days** at risk of stocking out, curbs margin leakage from flat `10%` discounts and `114` cancelled orders, and frees cash tied up in slow-moving hub stock.
- **Better Day-to-Day Processes:** Procurement, Mombasa/Nairobi/Kampala hub managers, and country store managers work from one shared set of SQL-verified KPIs instead of disconnected spreadsheets.
- **Faster Decisions:** Any regional manager can filter by Country, Branch, or Hub and spot the main operational bottleneck in under one minute.

---

## 6. Dashboard Layout: The 4 Dimensions of Supply Chain Health

1. **Stock Availability: *Are enough products on the shelf across Kenya, Uganda, Tanzania, and Rwanda?***
   - **Visualisation:** East Africa **choropleth map** of Stock-Out Risk %, `Country x Branch` conditional risk heatmap, and Priority Reorder table (filter by `Country`, `Category`, and `Branch Store ID`).
2. **Inventory Capital Efficiency: *Where is working capital productive vs. tied up in hub stock and corridor transport?***
   - **Visualisation:** **Stacked column chart** comparing Sold COGS, Estimated Holding Stock, and Corridor Transport Cost by category, plus utilisation bars across *Mombasa Port Hub, Nairobi Central Hub,* and *Kampala Regional Hub*.
3. **Demand and Price Stability: *How do sales, stock buffers, and net prices change across months and East African retail quarters?***
   - **Visualisation:** **Multi-year monthly trend line** (2022 to 2023), Retail Quarter bar chart (`Q4 Festive, Q1 Back-to-School, Q2 Long Rains, Q3 Mid-Year Dry`), and Promo vs Normal Day comparison table (slice by `SKU P0001-P0020`, `Category`, `Quarter`, and `Country`).
4. **Supplier and Product Reliability: *Which products and suppliers help or bottleneck East African operations the most?***
   - **Visualisation:** Interactive **Top N / Bottom N horizontal bar chart** (`5, 8, or 10` products by Risk %, Revenue, or Days of Supply) alongside the Supplier Reliability Scorecard.

---

## 7. Key Performance Indicators (KPIs)

| KPI | Definition / Formula | Why It Matters |
| :--- | :--- | :--- |
| **Net Retail Sales (USD)** | Units sold multiplied by net price after discount (consolidated in USD) | Compares revenue across Kenya, Uganda, Tanzania, and Rwanda on one currency |
| **Days of Supply** | Average on-hand branch stock divided by average daily units sold | Shows how many days shelf stock will last before running out |
| **Stock-Out Risk Rate (%)** | Share of branch-days where stock falls within 10% of daily demand | Early warning rule flag for lost sales |
| **Hub Utilisation & Turnover** | `Inventory Level / Warehouse Capacity` and `COGS / Average Inventory` | Tracks hub space usage across Mombasa, Nairobi, and Kampala |
| **Corridor Lead Time & Backorder %** | Mean days from order to delivery; % of orders delayed on backorder | Measures supplier speed and cross-border fulfilment reliability |

---

## 8. Scope, Assumptions, and Limitations

- **In Scope:** Cleaning, SQL KPI verification, Tableau visualisation, and Streamlit Cloud deployment across 73,100 daily branch records and 1,200 hub replenishment orders. Machine learning demand forecasting is excluded to stay focused on core data analytics.
- **Regional Mapping Note:** Because real East African retail chains keep SKU-level stock-out and vendor cost records confidential, public Kaggle retail and supply chain benchmark datasets were used. Anonymised region codes, warehouses, and seasonal labels were mapped consistently to a 4-country East African network (`Kenya, Uganda, Tanzania, Rwanda`; `Mombasa, Nairobi, Kampala` hubs; `Q1-Q4` East African retail quarters) consolidated in USD while preserving 100% of the original numerical volumes and ratios.
- **Limitations:** Product IDs (`P0001-P0020`) and supplier names (`Supplier A-D`) remain anonymised, and batch-level expiry dates for perishable groceries are not recorded.
