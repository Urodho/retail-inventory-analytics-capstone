# Business Understanding: Retail Supply Chain and Inventory Analytics

**Capstone Project, Zindua School Data Analytics**  
**Student:** Denis Urodho | **Date:** 23 November 2026  
**Datasets Used:**
- [Retail Store Inventory Dataset (Kaggle)](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset) (73,100 daily store sales and inventory rows across 5 stores, 20 products, and 4 regions)
- [Inventory Supply Chain Dataset (Kaggle)](https://www.kaggle.com/datasets/akalyanbce/inventory-supply-chain-dataset) (1,200 warehouse and supplier order rows across 4 suppliers, 3 warehouses, and 4 regions)

---

## 1. What Problem Am I Solving?

A retail company makes money when products are on the shelf at the moment a customer wants to buy them. At the same time, the company cannot afford to keep too much stock in its stores and warehouses because unsold inventory ties up cash, uses up storage space, and increases transport costs.

Supply chain and inventory management therefore sits at the centre of retail profitability. In day-to-day operations, two things make this hard to get right:
1. Customer demand changes across seasons, months, and store locations, so some fast-moving items run low while other categories pile up.
2. Suppliers do not all perform at the same level. Late deliveries, inaccurate shipments, backorders, and cancelled orders make store stock-outs much worse, especially when procurement and store teams only check separate spreadsheets once a week.

Instead of building a machine learning forecast model (which goes outside the scope of this analytics project), I am solving this visibility problem using SQL data analysis and an interactive dashboard. The goal is to show managers where stock is running low, where cash is stuck in slow-moving inventory, how demand behaves across seasons, and which suppliers are slowing operations down.

---

## 2. What Tools Did I Use and How Did I Get the Answers?

I used four main tools to take the raw Kaggle CSV files all the way to verified business answers:

- **Python (`pandas` and `numpy`):** I used Python in Jupyter Notebook to inspect and clean both CSV files. In the store dataset (`73,100` rows), I dropped the pre-generated `Demand Forecast` column so that all analysis relies on actual recorded figures. I standardised date formats (`YYYY-MM-DD`) across both files, checked for missing values and duplicate rows, calculated net selling price after discount (`Price * (1 - Discount / 100)`), and added a rule flag (`near_stockout_flag`) whenever `Inventory Level` fell within 10% of that day's `Units Sold`.
- **SQL (SQLite / PostgreSQL / BigQuery syntax):** I loaded the cleaned tables into a relational database and wrote SQL `GROUP BY` and `CASE WHEN` queries to calculate every KPI before building any charts. Doing the maths in SQL first made it easy to check that the dashboard totals matched the raw tables.
- **Power BI (Data Modelling and DAX):** I connected both cleaned tables in Power BI using shared `Region` (`North, South, East, West`) and `Date` lookup tables, wrote DAX measures for Days of Supply, Stock-Out Risk %, Warehouse Utilisation %, and Backorder Rate %, and built an interactive 4-part dashboard with slicers.
- **VS Code and Git/GitHub:** Used to organise the project folder, SQL scripts, Python cleaning notebook, and project documentation.

---

## 3. Business Questions and How Our Data Answers Each One

Below are the 5 core business questions from my project plan, the analytical method used, and how each question was answered using the columns available in our two datasets:

| # | Business Question | Analytical Method Used | Data Columns Used & What the Data Actually Shows |
| :- | :--- | :--- | :--- |
| **1** | **Are the right products available across regions and stores, and which SKUs face immediate stock-out risk?** | SQL KPI aggregation, Days-of-Supply & safety-threshold rules | Using `Region`, `Store ID`, `Product ID`, `Inventory Level`, and `Units Sold` in the store dataset: stores hold an average of only **2.01 Days of Supply** (`274.5` units on hand vs `136.5` sold per day). Out of 73,100 store-days, **6,799 days (9.30%)** came within 10% of running out. **East Region** has the highest overall risk (**9.62%**), with specific combinations like *East Groceries in Store S001 (11.37%)* and *SKU P0004 Furniture (1.91 Days of Supply)* needing priority reorder flags. |
| **2** | **Where is working capital tied up in excess stock, high warehouse utilisation, or logistics costs?** | Inventory turnover, COGS vs. holding analysis & stacked comparisons | Using `Category`, `Warehouse`, `Cost of Goods Sold (COGS)`, `Inventory Level`, `Warehouse Capacity`, and `Transportation Cost` in the supply chain dataset: total COGS is **$71.24M** with **$9.27M** spent on transport. Average warehouse capacity use is moderate (**33.4% to 35.1%**), meaning warehouses are not full overall, yet stock is unevenly placed. For example, *West Clothing in Warehouse 2* sits at **44.51% capacity utilisation** (`3,238` avg units on hand), tying up cash while certain retail stores run short. |
| **3** | **How do demand, stock levels, and effective prices fluctuate across months, seasons, and promotions?** | Historical time-series trend analysis & seasonal slicing (no ML) | Using `Date`, `Seasonality`, `Holiday/Promotion`, `Price`, `Discount`, and `Units Sold` from Jan 2022 to Dec 2023: sales are highest in **Autumn (2.51M units, 137.8/day)** and **Winter (2.50M units, 136.8/day)** compared to **Summer (2.48M units, 135.4/day)**. Looking closely at `Holiday/Promotion` also showed a surprising result: promo days averaged **136.4 units sold** vs **136.5 units** on normal days, because the average discount stayed flat at **10.0%** across both groups. |
| **4** | **Which suppliers deliver late, cancel orders, or generate high backorder and inaccuracy rates?** | Supplier lead-time & fulfilment scorecard (SQL & BI) | Using `Supplier`, `Lead Time (Days)`, `Order Status`, `Order Accuracy`, and `Backorder` across 1,200 orders: **Supplier D** has the worst backorder rate at **12.21%** (compared to **7.05%** for Supplier A). **Supplier B** is the slowest to deliver at **16.17 days** on average, while **Supplier C** has the highest order cancellation rate (**10.91%**) and the lowest order accuracy (**89.45%**). Overall, **362 out of 1,200 orders (30.2%)** were either Pending (`248`) or Cancelled (`114`). |
| **5** | **Which Top N / Bottom N products and categories drive profitability vs. operational bottlenecks?** | Ranked Top N / Bottom N Pareto & reorder priority views | Using net revenue (`Units Sold * Net Price`) and risk rates across all 20 SKUs and categories: **Furniture ($100.23M)** and **Groceries ($99.95M)** generate the highest store net revenue, while **Electronics ($97.39M)** is lowest in store sales yet highest in supply chain transport spend (**$2.52M**). At SKU level, **P0020 ($25.50M)** and **P0011 ($25.46M)** bring in the most revenue, while **P0012 ($24.11M)** and **P0002 ($24.17M)** sit at the bottom. Notably, top seller **P0020** also carries an above-average stock-out risk (**9.71%**), making it a high-priority item to protect. |

---

## 4. Main Insights and Practical Solutions

Looking across all five answers together gave three main "aha" moments that go beyond just putting charts on a screen:

1. **A 2-day store buffer does not match a 16-day supplier lead time:** Stores keep roughly 2 days of stock on hand, yet suppliers take 15 to 16 days to deliver warehouse orders. Without an early reorder warning, any delay at the warehouse quickly turns into an empty store shelf.
2. **Supplier problems come in different forms:** If a manager only looked at average lead time, Supplier C (`15.54 days`) would look fine, hiding the fact that Supplier C cancels **10.91%** of orders and gets over **10%** of shipments wrong. Meanwhile, Supplier D creates the most backorders (**12.21%**).
3. **Blanket 10% discounts are wasting margin:** Running promotions did not lift daily unit sales because non-promotion days already had the same 10% average discount.

### Practical Solutions I Am Proposing
- **Rule-Based Reorder Table:** Flag any store-product pair dropping below `1.95 Days of Supply` (or exceeding `12.5%` risk days) as `Priority Reorder`, especially top revenue earners like `P0020` and fast-moving `P0004`.
- **Supplier Scorecards Before Ordering:** Shift urgent orders toward **Supplier A** (`92.31%` accuracy, `7.05%` backorders, `15.23-day` lead time) and review contract terms with **Supplier D** (backorders) and **Supplier C** (cancellations and accuracy).
- **Targeted Seasonal Promotions:** Stop offering flat year-round discounts that do not move extra units, and instead use targeted discounts to clear overstocked warehouse pockets (such as *West Clothing in Warehouse 2*) while building stock ahead of **Autumn and Winter**.

**Do retail teams actually need these solutions?** Yes. Most mid-sized supermarkets, wholesalers, and retail chains in Kenya and across East Africa work on tight profit margins and do not have data science teams running complex forecasting code. What their procurement and store managers actually need every Monday morning is a clear list of what is about to run out, where cash is stuck, and which supplier is letting them down.

---

## 5. How Would a Business Benefit from This Work?

- **Money Saved and Sales Protected:** Protecting top-selling SKUs (like `P0020`) during the **9.3% of days** when stock runs dangerously low prevents lost customer sales. Reviewing cancelled orders (`114` orders) and rethinking flat `10%` discounts directly protects gross margin, while shifting slow warehouse stock frees up cash for Finance.
- **Better Day-to-Day Processes:** Instead of Procurement, Warehouse, and Store managers arguing from different Excel sheets, everyone works from one shared set of SQL-checked numbers and clear reorder rules (`Priority Reorder`, `Watch Buffer`, `Healthy`).
- **Faster Decisions:** A manager can open the dashboard, filter by their Region or Store in under one minute, and immediately see which SKU to reorder and which supplier to follow up with.

---

## 6. Dashboard Layout: The 4 Dimensions of Supply Chain Health

Following the structure of a 4-pillar analytical dashboard, the visuals are organised around four plain-English questions:

1. **Stock Availability: *Are enough products on the shelf in every region and store?***
   - **KPIs & Data:** Days of Supply, Stock-Out Risk %, Net Revenue ([Retail Store Inventory Dataset](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset)).
   - **Visualisation:** Regional coverage grid, `Region x Store` conditional risk heatmap, and a Priority Reorder table. User can filter by `Region`, `Category`, and `Store ID`.
2. **Inventory Capital Efficiency: *Where is cash productive vs. tied up in stock and transport?***
   - **KPIs & Data:** Sold COGS, Holding Stock Value, Transport Cost, Warehouse Capacity Utilisation % ([Inventory Supply Chain Dataset](https://www.kaggle.com/datasets/akalyanbce/inventory-supply-chain-dataset)).
   - **Visualisation:** **Stacked column chart** comparing COGS, holding stock, and transport cost by category, plus warehouse utilisation bars (`Warehouse 1 to 3`). User can filter by `Region`, `Warehouse`, and `Category`.
3. **Demand and Price Stability: *How do sales, stock levels, and net prices change over time?***
   - **KPIs & Data:** Monthly Units Sold, Average Inventory Level, and Net Selling Price from 2022 to 2024 ([Retail Store Inventory Dataset](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset)).
   - **Visualisation:** **Multi-year trend line chart** and seasonal summary cards (`Autumn, Winter, Spring, Summer`). User can slice by `SKU (P0001-P0020)`, `Category`, `Season`, and `Region`.
4. **Supplier and Product Reliability: *Which products and suppliers help or hurt operations the most?***
   - **KPIs & Data:** Supplier Lead Time, Backorder %, Order Accuracy %, Cancellation %, and SKU Risk % (both Kaggle datasets).
   - **Visualisation:** **Top N / Bottom N bar chart** (`Top 5/8/10` vs `Bottom 5/8/10` SKUs by Risk, Revenue, or Days of Supply) alongside a Supplier Scorecard table. User can filter by `Supplier`, `Region`, and `Category`.

---

## 7. Key Performance Indicators (KPIs)

| KPI | Definition / Formula | Why It Matters |
| :--- | :--- | :--- |
| **Total Sales & Net Revenue** | Units sold and revenue after discount by product, category, and period | Shows which categories and stores bring in the most income |
| **Days of Supply** | Average on-hand stock divided by average daily units sold | Shows how many days current stock will last |
| **Stock-Out Risk Rate (%)** | Share of days where store stock is within 10% of daily demand | Early warning flag for lost sales |
| **Inventory Turnover & Utilisation** | `COGS / Average Inventory` and `Inventory Level / Warehouse Capacity` | Shows how quickly stock sells and how full each warehouse is |
| **Average Lead Time** | Average days between placing an order and receiving delivery | Measures supplier delivery speed |
| **Backorder & Accuracy Rate** | % of orders delayed on backorder vs % delivered accurately | Measures whether a supplier can be trusted |

---

## 8. Scope, Assumptions, and Limitations

- **In Scope:** Cleaning, SQL analysis, and interactive dashboard reporting across the 73,100 daily store records and 1,200 warehouse order records. Predictive demand forecasting models are left out so the project stays focused on core data analytics.
- **Assumptions:** Recent average daily sales give a practical baseline for calculating Days of Supply, and both datasets represent the same four regional divisions (`North, South, East, West`).
- **Limitations:** Because both datasets come from public Kaggle sources, product codes (`P0001-P0020`) and supplier names (`Supplier A-D`) are anonymised, and product expiry dates for perishable groceries are not recorded in the store file. Therefore, findings show how the analytical workflow operates rather than proprietary figures from one named Kenyan retailer.