# Business Understanding: Retail Supply Chain & Inventory Health Analytics

**Final Capstone Project — Zindua School Data Analytics**  
**Student:** Denis Urodho | **Date:** 23 November 2026  
**Datasets:**
- [Retail Store Inventory Dataset (Kaggle)](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset) — *73,100 daily store-level sales & stock records*
- [Inventory Supply Chain Dataset (Kaggle)](https://www.kaggle.com/datasets/akalyanbce/inventory-supply-chain-dataset) — *1,200 multi-year supplier & warehouse replenishment orders*

---

## 1. What Problem Are We Solving?

Every shopper knows the frustration of walking into a retail store to buy an everyday item only to find an empty shelf—and walking out to buy from a competitor instead. Behind that empty shelf, however, the retailer is often suffering the exact opposite problem in its backroom warehouses: millions in working capital trapped inside slow-moving products that are not selling.

Multi-region retail chains manage thousands of daily transactions across categories (*Groceries, Clothing, Electronics, Furniture, Accessories,* and *Toys*), supplied by external vendors with unpredictable delivery schedules. Because store managers, warehouse teams, and procurement officers usually look at disconnected spreadsheets, they suffer from **three costly operational blind spots**:

1. **Silent Shelf Stock-Outs:** Fast-moving products drop below 2 days of stock without any early-warning alert, causing immediate lost sales and unhappy customers.
2. **Trapped Working Capital:** Slow-moving categories accumulate inside regional warehouses, tying up cash and inflating storage and transportation costs.
3. **Unaccountable Supplier Delays:** Late deliveries, order inaccuracies, cancellations, and backorders disrupt store replenishment, yet managers lack objective evidence on which suppliers are causing the bottleneck.

---

## 2. What Tools Did We Use & How Did We Get the Answer?

To solve this strictly through diagnostic **Data Analytics**—without relying on out-of-scope machine learning models—this project uses a four-layer analytics pipeline:

| Tool / Technology | Role in Pipeline | How It Produces the Answer |
| :--- | :--- | :--- |
| **Python (`pandas`, `numpy`)** | Data Cleaning, Validation & Feature Engineering | Standardizes multi-year date formats across 73,100 daily store records and 1,200 warehouse orders; verifies zero nulls/duplicates; engineers `effective_price`, `net_revenue`, and rule-based `near_stockout_flag` columns. |
| **SQL (`Google BigQuery` / `PostgreSQL` / `SQLite`)** | Relational Modeling & KPI Verification | Uses `GROUP BY`, `CASE WHEN` threshold rules, and aggregations to compute **Days of Supply**, **Stock-Out Risk %**, **Inventory Turnover**, **Warehouse Capacity Utilization %**, and **Supplier Backorder Scorecards**. |
| **Power BI (`Star Schema` & `DAX`)** | Interactive 4-Dimension Dashboard | Connects store and warehouse tables via shared `Dim_Region` and `Dim_Date` tables; powers conditional risk heatmaps, stacked capital-efficiency columns, seasonal trend lines, and dynamic **Top N / Bottom N** slicers. |
| **Git / GitHub & Technical Article** | Reproducibility & Data Storytelling | Documents the end-to-end Python cleaning code, verified SQL scripts, dashboard architecture, and business recommendations. |

---

## 3. What Insights (“Aha!” Moments) & Solutions Do We Offer?

A dashboard alone does not solve a business problem—the operational discoveries and actions unlocked by the data do. SQL exploration of the 73,100 store records and 1,200 supply chain orders uncovers **three major “Aha!” moments**:

> **Aha! #1 — The 2-Day Shelf Buffer vs. 16-Day Lead-Time Trap**  
> Retail shelves operate on a razor-thin average buffer of **2.01 Days of Supply**, and **6,799 store-product days (9.30%)** come within 10% of complete stock depletion—especially in *East Region Groceries and Furniture (>11.2% risk)*. Yet supplier replenishment takes **15.2 to 16.2 days** on average. Without automated early reorder flags, any small demand spike guarantees empty shelves.

> **Aha! #2 — The 73% Supplier Backorder Gap**  
> Overall order accuracy looks healthy on the surface (~91%), hiding severe vendor disparities. Disaggregating by supplier reveals **Supplier D has a 12.21% backorder rate—73% worse than Supplier A (7.05%)**—while **Supplier C** drops below 90% order accuracy (**89.45%**) and **30.2% of all orders** sit *Pending* (248) or *Canceled* (114).

> **Aha! #3 — Misallocated Warehouse Capital**  
> Overall warehouse capacity sits around **34% utilization**, yet pockets like *West Clothing in Warehouse 2 (44.5% utilization)* tie up heavy inventory while high-velocity store SKUs (*e.g., `P0004` Furniture and `P0009` Clothing*) repeatedly trigger priority stock-out warnings.

### Actionable Solutions Offered
1. **Automated Rule-Based Reorder Triggers (`< 1.95 Days of Supply`):** Flags every SKU-store pair as `Priority Reorder`, `Watch Buffer`, or `Healthy` so buyers reorder *before* shelves empty.
2. **Evidence-Based Vendor SLA Re-allocation:** Gives procurement hard data to shift critical replenishment volume toward **Supplier A** and enforce lead-time/backorder penalties on **Supplier D** and **Supplier B**.
3. **Seasonal Buffer Rebalancing:** Aligns warehouse dispatches with historical **Autumn and Winter** demand peaks instead of over-stocking low-velocity categories.

### Do Businesses Actually Need These Solutions?
**Yes.** Supermarkets, FMCG distributors, and multi-branch retailers—especially growing retail chains in Kenya and East Africa—operate on tight net margins of **3%–8%** and rarely have expensive enterprise AI systems. Practical, transparent **SQL + Power BI** diagnostics solve daily lost-sales and cash-flow pain points immediately using data they already collect.

---

## 4. How Would a Business Benefit? (Real Value)

| Value Pillar | Operational Mechanism | Concrete Business Impact |
| :--- | :--- | :--- |
| **1. Money Saved & Revenue Protected** | Prevents stock-outs across the **9.3% at-risk store-days**; cuts avoidable backorders and canceled shipments out of **$9.27M** in logistics spend; unlocks cash trapped in slow-moving stock. | Protects millions in at-risk retail sales, frees working capital for Finance, and lowers emergency freight costs. |
| **2. Processes Improved** | Replaces manual weekly spreadsheet checks across 5 stores and 3 warehouses with automated SQL KPI views and DAX reorder alerts. | Cuts stock-reconciliation and reporting time from hours to seconds while eliminating manual formula errors. |
| **3. Better, Faster Decisions** | Role-ready interactive slicers allow Procurement, Warehouse Ops, Finance, and Store Managers to spot root causes in **under 60 seconds**. | Procurement renegotiates vendor SLAs with hard numbers; Store Managers protect peak-season stock; Finance curbs excess buying. |

---

## 5. Dashboard Specification: The 4 Dimensions of Supply Chain Health

Structured around four diagnostic dimensions (with self-service interactive filters):

### 1. Stock Availability — *Are enough products on the shelf in every region and store when customers want them?*
- **Metrics & Data:** Days of Supply (`Inventory Level ÷ Avg Daily Units Sold`), Stock-Out Risk %, Net Revenue ([Retail Store Inventory Dataset](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset) + [Inventory Supply Chain Dataset](https://www.kaggle.com/datasets/akalyanbce/inventory-supply-chain-dataset)).
- **Visualization:** Regional Coverage Map/Grid + `Region × Store` Risk Heatmap + Priority Reorder Action Table.
- **Interactive Slicers:** Filter by `Region` (*North, South, East, West*), `Category`, and `Store ID` (*S001–S005*).

### 2. Inventory Capital Efficiency — *Where is working capital productive versus tied up in excess stock and logistics?*
- **Metrics & Data:** Active Sold COGS vs. Estimated Holding Stock Value & Transportation Cost, Inventory Turnover Index, Warehouse Capacity Utilization % ([Inventory Supply Chain Dataset](https://www.kaggle.com/datasets/akalyanbce/inventory-supply-chain-dataset)).
- **Visualization:** **Stacked Column Chart** by Category paired with Warehouse Utilization (`Warehouse 1–3`) & Order Status bars.
- **Interactive Slicers:** Filter by `Region`, `Warehouse`, and `Category`.

### 3. Demand & Replenishment Stability — *Are product demand, stock buffers, and effective selling prices stable across months and seasons?*
- **Metrics & Data:** 24-month historical Units Sold vs. Average On-Hand Stock Level and Net Selling Price after discounts ([Retail Store Inventory Dataset](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset)).
- **Visualization:** **Multi-Year Dual-Line Trend Chart** + Seasonal Summary Cards (*Autumn, Winter, Spring, Summer*).
- **Interactive Slicers:** Slice by `SKU` (*P0001–P0020*), `Category`, `Season`, and `Region`.

### 4. Supplier & SKU Reliability — *Which specific products and suppliers strengthen or bottleneck operations the most?*
- **Metrics & Data:** Average Supplier Lead Time (Days), Backorder Rate %, Order Accuracy %, Order Cancellation %, and SKU Stock-Out Risk % ([Inventory Supply Chain Dataset](https://www.kaggle.com/datasets/akalyanbce/inventory-supply-chain-dataset) + [Retail Store Inventory Dataset](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset)).
- **Visualization:** Dynamic **Top N / Bottom N Horizontal Bar Chart** (*Top/Bottom 5, 8, or 10 SKUs*) + Supplier Audit Scorecard.
- **Interactive Slicers:** Toggle `Top N` vs. `Bottom N`, switch ranking metric (`Stock-Out Risk %`, `Net Revenue`, `Days of Supply`), and filter by `Supplier` & `Region`.

---

## 6. Core KPI Definitions

| KPI | Formula / Definition | Business Decision Supported |
| :--- | :--- | :--- |
| **Days of Supply (DoS)** | `AVG(Inventory Level) ÷ AVG(Daily Units Sold)` | Triggers `Priority Reorder` when stock buffer drops below threshold |
| **Stock-Out Risk Rate (%)** | `% of store-days where Inventory Level <= 1.10 × Daily Units Sold` | Pinpoints high-risk stores and categories losing shelf sales |
| **Inventory Turnover** | `SUM(COGS) ÷ SUM(Average Inventory)` | Measures how efficiently inventory capital converts into sales |
| **Warehouse Utilization (%)** | `AVG(Inventory Level) ÷ AVG(Warehouse Capacity) × 100` | Identifies over-utilized vs. under-utilized storage facilities |
| **Supplier Lead Time & Backorder %** | `AVG(Lead Time Days)` & `% of orders on Backorder` | Supports vendor contract audits and procurement allocation |

---

## 7. Scope, Assumptions & Limitations

- **In Scope:** End-to-end descriptive and diagnostic analytics across 73,100 store records and 1,200 warehouse orders using Python, SQL, and Power BI. **Out of Scope:** Predictive machine-learning demand forecasting models, keeping the project 100% aligned with Data Analytics best practices.
- **Assumptions:** Historical daily demand velocity serves as a reliable benchmark for Days of Supply; rule-based thresholds (`< 1.95 Days of Supply` or `>= 12.5%` near-depletion rate) act as transparent operational reorder triggers.
- **Limitations:** Public Kaggle datasets use anonymized SKU/supplier identifiers and do not record batch-level expiry dates for perishable goods or external macroeconomic shocks.