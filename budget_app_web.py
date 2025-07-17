import streamlit as st
import json
import os
import plotly.express as px
import pandas as pd

# --------------------- Helper Functions ---------------------
def add_expense(expenses, description, amount):
    expenses.append({"description": description, "amount": amount})

def get_total_expenses(expenses):
    return sum(expense['amount'] for expense in expenses)

def get_balance(budget, expenses):
    return budget - get_total_expenses(expenses)

def load_budget_data(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                return data.get('initial_budget', 0), data.get('expenses', [])
        except json.JSONDecodeError:
            return 0, []
    return 0, []

def save_budget_data(filepath, initial_budget, expenses):
    data = {
        'initial_budget': initial_budget,
        'expenses': expenses
    }
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

# --------------------- Streamlit App UI ---------------------

st.set_page_config(page_title="💰 Budget Tracker", page_icon="💸", layout="centered")
st.title("💰 Personal Budget Tracker App")
st.markdown("Keep track of your expenses and stay within your budget. Simple, visual, and interactive!")

# Filepath for storing data
filepath = 'budget_data.json'

# Load existing budget and expenses
initial_budget, expenses = load_budget_data(filepath)

# Use Streamlit session state to persist data
if 'expenses' not in st.session_state:
    st.session_state.expenses = expenses
if 'budget' not in st.session_state:
    st.session_state.budget = initial_budget

# Sidebar for setting the budget
st.sidebar.header("📌 Setup Your Budget")
st.sidebar.markdown("Set your total budget for the month:")
if 'budget' not in st.session_state or not isinstance(st.session_state.budget, (int, float)):
    st.session_state.budget = 0.0
# Ensure budget is initialized properly
if 'budget' not in st.session_state or not isinstance(st.session_state.budget, (int, float)):
    st.session_state.budget = 0.0

budget_input = st.sidebar.number_input(
    "💼 Enter Initial Budget",
    min_value=0.0,
    max_value=float(1e9),  # Optional, just to ensure consistent types
    value=float(st.session_state.budget),
    step=100.0,
    format="%.2f"
)


st.session_state.budget = budget_input



# Expense Input Form
st.subheader("➕ Add a New Expense")
with st.form("expense_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        description = st.text_input("📝 Expense Description")
    with col2:
        amount = st.number_input("💵 Expense Amount", min_value=0.0, format="%.2f")

    submitted = st.form_submit_button("Add Expense")
    if submitted:
        if description and amount > 0:
            add_expense(st.session_state.expenses, description, amount)
            save_budget_data(filepath, st.session_state.budget, st.session_state.expenses)
            st.success(f"✅ Added: {description} - ₹{amount:.2f}")
        else:
            st.warning("⚠️ Please enter both a description and a valid amount.")

# Budget Summary
st.subheader("📊 Budget Summary")
total_spent = get_total_expenses(st.session_state.expenses)
balance = get_balance(st.session_state.budget, st.session_state.expenses)

col1, col2, col3 = st.columns(3)
col1.metric("💼 Total Budget", f"₹{st.session_state.budget:.2f}")
col2.metric("💸 Total Spent", f"₹{total_spent:.2f}")
col3.metric("💰 Remaining", f"₹{balance:.2f}", delta=f"{balance:.2f}")

# Expense List
st.subheader("📋 All Expenses")
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    st.table(df)
else:
    st.info("No expenses added yet. Start tracking now!")

# Charts Section
st.subheader("📈 Visual Expense Insights")
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)

    pie_chart = px.pie(df, names='description', values='amount', title='🔵 Expense Distribution')
    st.plotly_chart(pie_chart, use_container_width=True)

    bar_chart = px.bar(df, x='description', y='amount', title='🟦 Expense Amounts by Category', color='description')
    st.plotly_chart(bar_chart, use_container_width=True)
else:
    st.info("Add some expenses to see the charts.")

# Footer
st.markdown("---")
st.markdown("🧠 Made with ❤️ using Streamlit | [GitHub](https://github.com/SaiNehaa/Budget_tracker_app)")
