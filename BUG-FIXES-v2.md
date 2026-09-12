# v2.2 correctness fixes

- Maps API `amount` to trained feature `TransactionAmt` before all model and SHAP preprocessing.
- Replaces process-random Python category hashing with exact LabelEncoder artifacts.
- Includes a one-time encoder builder using the original training CSV.
- Stops rule count from being added directly to model probability.
- Uses configurable model threshold for the final fraud flag.
- Keeps high-value rules as analyst evidence rather than automatic fraud labels.
- Makes the demo transaction feed opt-in instead of mutating the database whenever the dashboard opens.
- Dashboard totals now use database-wide aggregate metrics, not only the latest 50 rows.
- Corrects average score calculation.
- Orders monitoring chart points chronologically.
- Removes the false GNN ACTIVE card; model cards now come from backend health.
- Makes system online status, model count and latency dynamic.
- Removes current frontend lint warnings and stale test.
