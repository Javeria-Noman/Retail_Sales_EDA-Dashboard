# Retail_Sales_EDA-Dashboard
Exploratory Data Analysis of electronics retail sales (Sep 2023 - Sep 2024) with an interactive Streamlit dashboard.

**Live dashboard:** [https://retailsaleseda-dashboard-cqgequdtyksu56u3dgwxvw.streamlit.app/]

## Objective
Understand sales trends, customer behaviour, product performance and relationships between variables, and turn them into business recommendations.

## Tech stack
Python, pandas, matplotlib, seaborn, Jupyter Notebook, Streamlit

## Dataset
Electronic Sales Sep 2023 - Sep 2024 (Kaggle, synthetic data): 20,000 orders, 16 columns.

## Project contents
- `- `Dashboard/Electronic Retail Sales Data.ipynb` - full analysis (inspection, cleaning, statistics, time series, demographics, products, correlation, cancellations)
- `Dashboard/app.py` - interactive dashboard
- `Dashboard/Electronic_sales_Sep2023-Sep2024.csv` - dataset
## Key findings
- 13,432 of 20,000 orders were completed, generating 42.63M in revenue from 9,466 customers (average order value 3,173.74, median 2,534.49).
- Revenue stepped up from 1.31M in Dec 2023 to 4.52M in Jan 2024, driven mostly by order volume, then stayed stable.
- Smartphone, Smartwatch and Laptop generate 75.4% of revenue.
- Average order value is almost identical across age groups and genders.
- 32.84% of orders were cancelled (worth about 49.2% of completed revenue), at similar rates across products, payment methods and shipping types.

## Recommendations
1. Investigate and reduce order cancellations.
2. Prioritise inventory and promotion for top revenue categories.
3. Judge products by revenue, and test bundling low-price items with higher-priced devices.
4. Identify what drove the January 2024 step-up.
5. Segment by product and behaviour rather than age or gender.

## Limitations
Synthetic dataset; first and last months are partial; one SKU has an unusually low unit price that should be verified; correlations do not show causation.           ## Run locally
```bash
cd Dashboard
pip install -r requirements.txt
streamlit run app.py
```
## Author
[Javeria Noman] - [https://www.linkedin.com/in/javeria-noman-88b4462a4/]                                                                                                                                                                                                                                                          






   
