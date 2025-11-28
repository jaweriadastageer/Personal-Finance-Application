import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

# backend functions/classes
from finance_utils import (
    Income, Expense, Investment,
    save_transaction, load_transactions,
    calculate_totals, get_insights, string_analysis
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Personal Finance Application",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (sidebar background + white font) ---
st.markdown(
    """
    <style>
    .main { background-color: #ffffff; }

    section[data-testid="stSidebar"] {
        background-color: #006400 !important;
        color: white !important;
    }

    /* only change labels, keep button DEFAULT */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stText,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }

    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2331/2331940.png", width=90)
with col2:
    st.title("Personal Finance Application")
    st.markdown("### *Track, Analyze, and Plan Your Finances*")

st.markdown("---")

# --- Sidebar: Transaction Input ---
st.sidebar.title("Add New Transaction")
st.sidebar.markdown("Record income / expenses / investments here.")

with st.sidebar.form("transaction_form", clear_on_submit=True):
    t_type = st.selectbox("Type", ["Income", "Expense", "Investment"])
    t_date = st.date_input("Date", date.today())
    t_amount = st.number_input("Amount ($)", min_value=0.0, step=10.0, format="%.2f")
    t_category = st.text_input("Category (e.g., Salary, Rent, Groceries)")
    t_note = st.text_area("Note (optional)")
    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        if t_amount > 0 and t_category.strip():
            if t_type == "Income":
                txn = Income(str(t_date), float(t_amount), t_category.strip(), t_note.strip())
            elif t_type == "Expense":
                txn = Expense(str(t_date), float(t_amount), t_category.strip(), t_note.strip())
            else:
                txn = Investment(str(t_date), float(t_amount), t_category.strip(), t_note.strip())

            save_transaction(txn)
            st.sidebar.success("Transaction added successfully!")
        else:
            st.sidebar.error("Please provide a positive amount and a category.")

# --- Load transactions ---
transactions = load_transactions()

if not transactions:
    st.info("No transactions found — add your first transaction from the sidebar.")
    st.stop()

# --- Financial Calculations ---
totals = calculate_totals(transactions)
total_income = totals["Total Income"]
total_expense = totals["Total Expense"]
total_investment = totals["Total Investment"]
net_balance = totals["Net Balance"]

if total_income > 0:
    savings_amount = max(0.0, total_income - total_expense)
    savings_pct = (savings_amount / total_income) * 100
else:
    savings_amount = 0.0
    savings_pct = 0.0

# --- Summary Metrics ---
st.subheader("Financial Overview")
m1, m2, m3, m4, m5 = st.columns([1,1,1,1,1])
m1.metric("Total Income", f"${total_income:,.2f}")
m2.metric("Total Expenses", f"${total_expense:,.2f}")
m3.metric("Total Investment", f"${total_investment:,.2f}")
m4.metric("Net Balance", f"${net_balance:,.2f}")
m5.metric("Savings %", f"{savings_pct:.2f}%")

st.markdown("---")

# --- Goal Evaluation (SLIDER MOVED HERE) ---
st.subheader("Goal Evaluation")

goal_pct = st.slider("Monthly savings goal (%)", min_value=0, max_value=100, value=20)

if total_income <= 0:
    st.info("No income recorded yet — cannot evaluate savings goal.")
else:
    if savings_pct >= goal_pct:
        if savings_pct >= goal_pct + 10:
            st.success(f"Excellent — you're surpassing your goal by {savings_pct - goal_pct:.2f} percentage points!")
        else:
            st.success(f"Good — you've met your goal (by {savings_pct - goal_pct:.2f} percentage points). Keep it up.")
    else:
        if savings_pct >= goal_pct * 0.75:
            st.warning(f"Close — you're at {savings_pct:.2f}% which is slightly below your {goal_pct}% goal. Try trimming expenses.")
        else:
            st.error(f"Below goal — you're at {savings_pct:.2f}% vs target {goal_pct}%. Consider boosting income or cutting expenses.")

st.markdown("---")

# --- Analytics ---
insights = get_insights(transactions)

st.subheader("Analytics & Insights")
st.write(f"**Highest spending category:** {insights['highest_spending_category']}")
st.write(f"**Most frequent category:** {insights['most_frequent_category']}")
st.write(f"**Unique categories ({len(insights['unique_categories'])}):** {', '.join(sorted(insights['unique_categories']))}")

st.markdown("---")

# --- Charts Tabs ---
tab1, tab2 = st.tabs(["Charts", "Transactions & String Analysis"])

with tab1:
    st.markdown("### Graphs")
    c1, c2 = st.columns(2)

    # Bar Chart (Expenses)
    with c1:
        st.write("**Spending by Category**")
        cat_totals = insights["category_totals"]
        expense_totals = {k: v for k, v in cat_totals.items() if any(isinstance(t, Expense) and t.category == k for t in transactions)}

        if expense_totals:
            df_bar = pd.DataFrame(list(expense_totals.items()), columns=["Category", "Amount"]).sort_values("Amount", ascending=False)
            bar = alt.Chart(df_bar).mark_bar(cornerRadius=4, color="#90ee90").encode(
                x=alt.X("Category:N", sort='-y'),
                y=alt.Y("Amount:Q"),
                tooltip=["Category", "Amount"]
            ).properties(height=350)
            st.altair_chart(bar, use_container_width=True)
        else:
            st.info("No expense data to show.")

    # Line Chart (Income vs Expense)
    with c2:
        st.write("**Income vs Expense Over Time**")
        df_trend = pd.DataFrame([t.to_dict() for t in transactions])

        if not df_trend.empty:
            df_trend.rename(columns={c: c.strip() for c in df_trend.columns}, inplace=True)
            if "Date" in df_trend.columns:
                df_trend["Date"] = pd.to_datetime(df_trend["Date"])
                trend = alt.Chart(df_trend).mark_line(point=True).encode(
                    x=alt.X("Date:T"),
                    y=alt.Y("Amount:Q"),
                    color=alt.Color("Type:N"),
                    tooltip=["Date", "Type", "Amount", "Category"]
                ).properties(height=350).interactive()
                st.altair_chart(trend, use_container_width=True)
            else:
                st.info("No date column found.")

with tab2:
    st.subheader("All Transactions")
    df_all = pd.DataFrame([t.to_dict() for t in transactions])
    cols_order = [c for c in ["Date", "Type", "Category", "Amount", "Note"] if c in df_all.columns]
    st.dataframe(df_all[cols_order].sort_values("Date", ascending=False).reset_index(drop=True), use_container_width=True)

    st.markdown("---")
    st.subheader("String Analysis (Categories)")
    categories_list = [t.category for t in transactions]
    joined_upper, count_a = string_analysis(categories_list)
    st.write("**Joined (UPPERCASE):**")
    st.code(joined_upper)
    st.metric("Count of letter 'A' in joined string", count_a)

st.markdown("---")
st.caption("Tip: Use the sidebar to add new transactions.")
