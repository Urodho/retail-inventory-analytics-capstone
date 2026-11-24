-- ============================================================================
-- Zindua School Data Analytics Capstone Project
-- Retail Supply Chain & Inventory Health Analytics (SQL KPI Queries)
-- Student: Denis Urodho
-- Datasets:
--   1. retail_store_inventory (Kaggle: anirudhchauhan/retail-store-inventory-forecasting-dataset)
--   2. supply_chain_orders    (Kaggle: akalyanbce/inventory-supply-chain-dataset)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- DIMENSION 1: STOCK AVAILABILITY
-- Business Question: Are the right products on the shelf when customers want them?
-- KPIs: Days of Supply, Stock-out Risk Rate (<1.2 days of cover), Net Revenue
-- ----------------------------------------------------------------------------
SELECT
    Region,
    Category,
    "Store ID" AS Store_ID,
    COUNT(*) AS Total_Observations,
    SUM("Units Sold") AS Total_Units_Sold,
    ROUND(SUM("Units Sold" * Price * (1.0 - Discount / 100.0)), 2) AS Net_Revenue,
    ROUND(AVG("Inventory Level"), 1) AS Avg_Inventory_Units,
    ROUND(AVG("Units Sold"), 1) AS Avg_Daily_Demand,
    ROUND(AVG("Inventory Level") / NULLIF(AVG("Units Sold"), 0), 2) AS Avg_Days_Of_Supply,
    ROUND(
        100.0 * SUM(CASE WHEN "Inventory Level" <= "Units Sold" * 1.10 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS Stockout_Risk_Rate_Pct
FROM retail_store_inventory
GROUP BY Region, Category, "Store ID"
ORDER BY Stockout_Risk_Rate_Pct DESC;


-- ----------------------------------------------------------------------------
-- DIMENSION 2: INVENTORY CAPITAL EFFICIENCY
-- Business Question: Where is cash tied up in excess stock vs. active sales?
-- KPIs: Inventory Turnover Ratio, COGS vs. Holding Stock Value, Warehouse Utilization
-- ----------------------------------------------------------------------------
SELECT
    Region,
    Category,
    Warehouse,
    COUNT(*) AS Total_Orders,
    SUM("Units Sold") AS Units_Sold,
    ROUND(SUM("Cost of Goods Sold (COGS)"), 2) AS Total_COGS,
    ROUND(SUM("Transportation Cost"), 2) AS Total_Transport_Cost,
    ROUND(AVG("Inventory Level"), 1) AS Avg_OnHand_Units,
    ROUND(AVG("Warehouse Capacity"), 1) AS Avg_Warehouse_Capacity,
    ROUND(100.0 * AVG("Inventory Level") / NULLIF(AVG("Warehouse Capacity"), 0), 2) AS Warehouse_Utilization_Pct,
    ROUND(SUM("Cost of Goods Sold (COGS)") / NULLIF(SUM("Average Inventory"), 0), 2) AS Inventory_Turnover_Index
FROM supply_chain_orders
GROUP BY Region, Category, Warehouse
ORDER BY Warehouse_Utilization_Pct DESC;


-- ----------------------------------------------------------------------------
-- DIMENSION 3: DEMAND & REPLENISHMENT STABILITY
-- Business Question: When does demand rise and fall across months, seasons & promotions?
-- KPIs: Monthly Demand, Avg Inventory Level, Effective Selling Price, Promo Lift
-- ----------------------------------------------------------------------------
SELECT
    SUBSTR(Date, 1, 7) AS Year_Month,
    Category,
    Seasonality,
    SUM("Units Sold") AS Monthly_Units_Sold,
    ROUND(AVG("Inventory Level"), 1) AS Avg_Inventory_Level,
    ROUND(AVG(Price * (1.0 - Discount / 100.0)), 2) AS Avg_Effective_Price,
    SUM(CASE WHEN "Holiday/Promotion" = 1 THEN "Units Sold" ELSE 0 END) AS Promo_Units_Sold,
    ROUND(SUM("Units Sold" * Price * (1.0 - Discount / 100.0)), 2) AS Monthly_Net_Revenue
FROM retail_store_inventory
GROUP BY Year_Month, Category, Seasonality
ORDER BY Year_Month ASC, Category ASC;


-- ----------------------------------------------------------------------------
-- DIMENSION 4A: SUPPLIER RELIABILITY SCORECARD
-- Business Question: Which suppliers deliver late, inaccurately, or cause backorders?
-- KPIs: Avg Lead Time (Days), Order Accuracy %, Backorder Rate %, Cancel/Pending %
-- ----------------------------------------------------------------------------
SELECT
    Supplier,
    Region,
    COUNT(*) AS Total_Orders,
    ROUND(AVG("Lead Time (Days)"), 2) AS Avg_Lead_Time_Days,
    ROUND(100.0 * AVG(CASE WHEN "Order Accuracy" = 1 THEN 1.0 ELSE 0.0 END), 2) AS Order_Accuracy_Pct,
    ROUND(100.0 * AVG(CASE WHEN Backorder = 1 THEN 1.0 ELSE 0.0 END), 2) AS Backorder_Rate_Pct,
    ROUND(100.0 * SUM(CASE WHEN "Order Status" = 'Fulfilled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Fulfilled_Pct,
    ROUND(100.0 * SUM(CASE WHEN "Order Status" = 'Canceled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Canceled_Pct,
    ROUND(AVG("Transportation Cost"), 2) AS Avg_Transport_Cost
FROM supply_chain_orders
GROUP BY Supplier, Region
ORDER BY Backorder_Rate_Pct DESC, Avg_Lead_Time_Days DESC;


-- ----------------------------------------------------------------------------
-- DIMENSION 4B: TOP N / BOTTOM N SKU STOCK-OUT RISK & REORDER ACTION LIST
-- Business Question: Which specific products need urgent reorder vs. stock reduction?
-- ----------------------------------------------------------------------------
SELECT
    "Product ID" AS Product_ID,
    Category,
    SUM("Units Sold") AS Total_Units_Sold,
    ROUND(SUM("Units Sold" * Price * (1.0 - Discount / 100.0)), 2) AS Total_Net_Revenue,
    ROUND(AVG("Inventory Level"), 1) AS Avg_Stock_On_Hand,
    ROUND(AVG("Units Sold"), 1) AS Avg_Daily_Sales,
    ROUND(AVG("Inventory Level") / NULLIF(AVG("Units Sold"), 0), 2) AS Days_Of_Supply,
    ROUND(
        100.0 * SUM(CASE WHEN "Inventory Level" <= "Units Sold" * 1.10 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS Stockout_Risk_Pct,
    CASE
        WHEN AVG("Inventory Level") / NULLIF(AVG("Units Sold"), 0) < 1.95 THEN 'HIGH RISK - Priority Reorder'
        WHEN AVG("Inventory Level") / NULLIF(AVG("Units Sold"), 0) < 2.02 THEN 'WATCH - Monitor Buffer'
        ELSE 'HEALTHY / CHECK OVERSTOCK'
    END AS Reorder_Action
FROM retail_store_inventory
GROUP BY "Product ID", Category
ORDER BY Stockout_Risk_Pct DESC;
