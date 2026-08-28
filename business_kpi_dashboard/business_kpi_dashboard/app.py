import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Customer Churn KPI Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("customer_churn_cleaned.csv")
    df["ChurnFlag"] = df["Churn"].eq("Yes")
    df["TenureBand"] = pd.cut(
        df["TenureMonths"],
        bins=[-1, 6, 12, 24, float("inf")],
        labels=["0–6 months", "7–12 months", "13–24 months", "25+ months"]
    )
    return df

df = load_data()

st.title("📊 Business KPI Dashboard")
st.caption("Customer churn, retention, revenue risk and customer segments")

# Sidebar filters
st.sidebar.header("Filters")

contract_options = sorted(df["ContractType"].dropna().unique())
payment_options = sorted(df["PaymentMethod"].dropna().unique())

selected_contracts = st.sidebar.multiselect(
    "Contract Type",
    contract_options,
    default=contract_options
)

selected_payments = st.sidebar.multiselect(
    "Payment Method",
    payment_options,
    default=payment_options
)

min_tenure = int(df["TenureMonths"].min())
max_tenure = int(df["TenureMonths"].max())
tenure_range = st.sidebar.slider(
    "Tenure (months)",
    min_value=min_tenure,
    max_value=max_tenure,
    value=(min_tenure, max_tenure)
)

filtered = df[
    df["ContractType"].isin(selected_contracts)
    & df["PaymentMethod"].isin(selected_payments)
    & df["TenureMonths"].between(tenure_range[0], tenure_range[1])
].copy()

if filtered.empty:
    st.warning("No customers match the selected filters. Please widen the filters.")
    st.stop()

# KPI definitions
total_customers = len(filtered)
churned = int(filtered["ChurnFlag"].sum())
churn_rate = churned / total_customers if total_customers else 0
retention_rate = 1 - churn_rate
revenue_at_risk = filtered.loc[filtered["ChurnFlag"], "MonthlyCharges"].sum()
avg_tenure = filtered["TenureMonths"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Customers", f"{total_customers:,}")
c2.metric("Churn Rate", f"{churn_rate:.1%}")
c3.metric("Retention Rate", f"{retention_rate:.1%}")
c4.metric("Revenue at Risk", f"₹{revenue_at_risk:,.2f}")
c5.metric("Avg. Tenure", f"{avg_tenure:.1f} mo")

st.divider()

# Main charts
left, right = st.columns(2)

with left:
    contract = (
        filtered.groupby("ContractType", as_index=False)
        .agg(Customers=("CustomerID", "count"),
             Churned=("ChurnFlag", "sum"))
    )
    contract["Churn Rate"] = contract["Churned"] / contract["Customers"]
    fig = px.bar(
        contract,
        x="ContractType",
        y="Churn Rate",
        text="Churn Rate",
        title="Churn Rate by Contract Type",
        labels={"Churn Rate": "Churn Rate", "ContractType": "Contract Type"},
        color="Churn Rate",
        color_continuous_scale="Viridis"
    )
    fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig.update_yaxes(tickformat=".0%", range=[0, max(1, contract["Churn Rate"].max() * 1.2)])
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    payment = (
        filtered.groupby("PaymentMethod", as_index=False)
        .agg(RevenueAtRisk=("MonthlyCharges", lambda s: s[filtered.loc[s.index, "ChurnFlag"]].sum()))
        .sort_values("RevenueAtRisk", ascending=False)
    )
    fig = px.bar(
        payment,
        x="PaymentMethod",
        y="RevenueAtRisk",
        title="Monthly Revenue at Risk by Payment Method",
        labels={"RevenueAtRisk": "Revenue at Risk (₹)", "PaymentMethod": "Payment Method"},
        text_auto=".2f"
    )
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    tenure = (
        filtered.groupby("TenureBand", observed=False, as_index=False)
        .agg(Customers=("CustomerID", "count"),
             Churned=("ChurnFlag", "sum"))
    )
    tenure["Churn Rate"] = tenure["Churned"] / tenure["Customers"]
    fig = px.bar(
        tenure,
        x="TenureBand",
        y="Churn Rate",
        text="Churn Rate",
        title="Churn Rate by Tenure Segment",
        labels={"Churn Rate": "Churn Rate", "TenureBand": "Tenure Segment"},
        color="Churn Rate",
        color_continuous_scale="Plasma"
    )
    fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig.update_yaxes(tickformat=".0%", range=[0, max(1, tenure["Churn Rate"].max() * 1.2)])
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    segment = (
        filtered.groupby("SubscriptionType", as_index=False)
        .agg(Customers=("CustomerID", "count"),
             Churned=("ChurnFlag", "sum"),
             Revenue=("MonthlyCharges", "sum"))
    )
    segment["Churn Rate"] = segment["Churned"] / segment["Customers"]
    fig = px.scatter(
        segment,
        x="Customers",
        y="Revenue",
        size="Churned",
        hover_name="SubscriptionType",
        text="SubscriptionType",
        title="Customer Segments: Size vs Monthly Revenue",
        labels={"Customers": "Customers", "Revenue": "Monthly Revenue (₹)"}
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

# Insights
st.subheader("💡 Key Insights")

top_contract = contract.sort_values("Churn Rate", ascending=False).iloc[0]
top_payment = payment.iloc[0]
top_tenure = tenure.sort_values("Churn Rate", ascending=False).iloc[0]

insights = [
    f"**Highest churn segment:** {top_contract['ContractType']} has a churn rate of {top_contract['Churn Rate']:.1%}.",
    f"**Largest revenue risk:** {top_payment['PaymentMethod']} contributes ₹{top_payment['RevenueAtRisk']:,.2f} in monthly revenue at risk.",
    f"**Tenure risk:** the {top_tenure['TenureBand']} segment has a churn rate of {top_tenure['Churn Rate']:.1%}.",
    f"**Retention:** {retention_rate:.1%} of filtered customers are retained."
]
for item in insights:
    st.markdown(f"- {item}")

st.subheader("Customer Detail")
display_cols = [
    "CustomerID", "Gender", "Age", "TenureMonths", "SubscriptionType",
    "MonthlyCharges", "TotalCharges", "ContractType",
    "SupportTickets", "PaymentMethod", "Churn"
]
st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

st.caption(
    "Definitions: Churn Rate = churned customers ÷ total customers. "
    "Retention Rate = 1 − churn rate. Revenue at Risk = monthly charges from churned customers. "
    "Tenure KPI = average customer tenure in months."
)