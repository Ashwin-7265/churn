# Business KPI Dashboard

An interactive beginner-friendly dashboard for customer churn, retention, revenue risk, tenure, and customer segments.

## Dataset

`customer_churn_cleaned.csv`

Rows: **15**  
Columns: **11**

## KPIs

- **Churn Rate** = Churned customers / Total customers
- **Retention Rate** = 1 − Churn Rate
- **Revenue at Risk** = Sum of MonthlyCharges for churned customers
- **Tenure** = Average TenureMonths

## Dashboard filters

- Contract Type
- Tenure in months
- Payment Method

## Visuals

1. Churn Rate by Contract Type
2. Monthly Revenue at Risk by Payment Method
3. Churn Rate by Tenure Segment
4. Customer Segments: customer count vs monthly revenue
5. Filterable customer detail table
6. Automatic written insights beside the dashboard visuals

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Portfolio / submission

Upload this folder to GitHub and deploy `app.py` with Streamlit Community Cloud.  
Use the deployed app URL as the single public/view-only submission link, and keep the dataset and README in the same repository.
