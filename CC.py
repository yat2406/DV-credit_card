import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Loan & Credit Card Payment Simulator",
    page_icon="💳",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("💳 Loan & Credit Card Payment Simulator")

st.write(
    "Explore how different repayment strategies affect your "
    "payment schedule, interest, total cost, and payoff time."
)

st.divider()


# ============================================================
# FUNCTIONS
# ============================================================

def calculate_payment(principal, annual_rate, months):
    """
    Calculate the normal monthly payment using
    the standard loan payment formula.
    """

    monthly_rate = annual_rate / 100 / 12

    if monthly_rate == 0:
        return principal / months

    payment = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** months
        / ((1 + monthly_rate) ** months - 1)
    )

    return payment


def simulate_payment(
    principal,
    annual_rate,
    term_months,
    monthly_payment,
    behavior
):
    """
    Simulate loan / credit card repayment.

    Behaviors:
    - On-time: normal monthly payment
    - Early: pays 25% more than normal payment
    - Late: pays 25% less than normal payment and
            occasionally misses payments
    """

    monthly_rate = annual_rate / 100 / 12

    balance = principal
    month = 0
    total_interest = 0
    total_paid = 0

    records = []

    # Safety limit to prevent infinite simulation
    max_months = max(term_months * 5, 120)

    while balance > 0.01 and month < max_months:

        month += 1

        # ----------------------------------------------------
        # Calculate interest
        # ----------------------------------------------------

        interest = balance * monthly_rate

        # ----------------------------------------------------
        # Determine payment based on behavior
        # ----------------------------------------------------

        if behavior == "On-time":
            payment = monthly_payment
            payment_type = "Normal Payment"

        elif behavior == "Early":
            payment = monthly_payment * 1.25
            payment_type = "Extra Payment"

        else:
            # Late payment behavior
            # Every 6th month is treated as a missed payment
            if month % 6 == 0:
                payment = 0
                payment_type = "Missed Payment"
            else:
                payment = monthly_payment * 0.75
                payment_type = "Reduced Payment"

        # ----------------------------------------------------
        # Add interest to balance
        # ----------------------------------------------------

        balance_before_payment = balance

        balance += interest

        # ----------------------------------------------------
        # Prevent overpayment
        # ----------------------------------------------------

        actual_payment = min(payment, balance)

        balance -= actual_payment

        # ----------------------------------------------------
        # Accumulate totals
        # ----------------------------------------------------

        total_interest += interest
        total_paid += actual_payment

        # ----------------------------------------------------
        # Store monthly data
        # ----------------------------------------------------

        records.append({
            "Month": month,
            "Beginning Balance": balance_before_payment,
            "Interest": interest,
            "Payment": actual_payment,
            "Ending Balance": max(balance, 0),
            "Payment Type": payment_type
        })

    df = pd.DataFrame(records)

    return df, total_interest, total_paid, month


# ============================================================
# SIDEBAR - USER INPUT
# ============================================================

st.sidebar.header("⚙️ Simulation Settings")

loan_type = st.sidebar.selectbox(
    "Select Borrowing Type",
    [
        "Loan",
        "Credit Card"
    ]
)


principal = st.sidebar.number_input(
    "Loan / Credit Card Amount (RM)",
    min_value=100.0,
    max_value=1000000.0,
    value=10000.0,
    step=500.0
)


annual_rate = st.sidebar.number_input(
    "Annual Interest Rate (%)",
    min_value=0.0,
    max_value=100.0,
    value=8.0,
    step=0.5
)


term_unit = st.sidebar.selectbox(
    "Loan Term Unit",
    [
        "Months",
        "Years"
    ]
)


if term_unit == "Years":

    term_value = st.sidebar.number_input(
        "Loan Term (Years)",
        min_value=1,
        max_value=50,
        value=5,
        step=1
    )

    term_months = term_value * 12

else:

    term_value = st.sidebar.number_input(
        "Loan Term (Months)",
        min_value=1,
        max_value=600,
        value=60,
        step=1
    )

    term_months = term_value


# ============================================================
# CALCULATE NORMAL PAYMENT
# ============================================================

normal_payment = calculate_payment(
    principal,
    annual_rate,
    term_months
)


st.sidebar.write("---")

st.sidebar.subheader("💰 Monthly Payment")

st.sidebar.metric(
    "Required Monthly Payment",
    f"RM {normal_payment:,.2f}"
)


# ============================================================
# PAYMENT BEHAVIOR
# ============================================================

behavior = st.sidebar.selectbox(
    "Payment Behavior",
    [
        "On-time",
        "Early",
        "Late"
    ]
)


# ============================================================
# SIMULATE SELECTED STRATEGY
# ============================================================

selected_df, selected_interest, selected_total, selected_months = (
    simulate_payment(
        principal,
        annual_rate,
        term_months,
        normal_payment,
        behavior
    )
)


# ============================================================
# SIMULATE ALL THREE STRATEGIES
# ============================================================

on_time_df, on_time_interest, on_time_total, on_time_months = (
    simulate_payment(
        principal,
        annual_rate,
        term_months,
        normal_payment,
        "On-time"
    )
)


early_df, early_interest, early_total, early_months = (
    simulate_payment(
        principal,
        annual_rate,
        term_months,
        normal_payment,
        "Early"
    )
)


late_df, late_interest, late_total, late_months = (
    simulate_payment(
        principal,
        annual_rate,
        term_months,
        normal_payment,
        "Late"
    )
)


# ============================================================
# EXTRA COST / SAVINGS
# ============================================================

if behavior == "On-time":

    difference = 0

elif behavior == "Early":

    difference = on_time_total - early_total

else:

    difference = late_total - on_time_total


# ============================================================
# SUMMARY
# ============================================================

st.header("📊 Simulation Summary")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Interest",
        f"RM {selected_interest:,.2f}"
    )


with col2:

    st.metric(
        "Total Amount Repaid",
        f"RM {selected_total:,.2f}"
    )


with col3:

    st.metric(
        "Time to Payoff",
        f"{selected_months} months"
    )


with col4:

    if behavior == "Early":

        st.metric(
            "Savings",
            f"RM {difference:,.2f}"
        )

    elif behavior == "Late":

        st.metric(
            "Extra Cost",
            f"RM {difference:,.2f}"
        )

    else:

        st.metric(
            "Difference",
            "RM 0.00"
        )


st.divider()


# ============================================================
# VIEW 1
# PAYMENT SCHEDULE
# ============================================================

st.header("📈 View 1: Payment Schedule")

st.write(
    f"Showing the remaining balance for the **{behavior}** "
    f"payment strategy."
)


fig1, ax1 = plt.subplots(figsize=(10, 5))

ax1.plot(
    selected_df["Month"],
    selected_df["Ending Balance"],
    marker="o",
    markersize=2
)

ax1.set_title(
    f"Remaining Balance Over Time - {behavior}"
)

ax1.set_xlabel("Month")

ax1.set_ylabel("Remaining Balance (RM)")

ax1.grid(True, alpha=0.3)

st.pyplot(fig1)


# ============================================================
# PAYMENT SCHEDULE TABLE
# ============================================================

with st.expander("📋 View Monthly Payment Schedule"):

    display_df = selected_df.copy()

    display_df["Beginning Balance"] = (
        display_df["Beginning Balance"].map(
            lambda x: f"RM {x:,.2f}"
        )
    )

    display_df["Interest"] = (
        display_df["Interest"].map(
            lambda x: f"RM {x:,.2f}"
        )
    )

    display_df["Payment"] = (
        display_df["Payment"].map(
            lambda x: f"RM {x:,.2f}"
        )
    )

    display_df["Ending Balance"] = (
        display_df["Ending Balance"].map(
            lambda x: f"RM {x:,.2f}"
        )
    )

    st.dataframe(
        display_df,
        use_container_width=True
    )


st.divider()


# ============================================================
# VIEW 2
# INTEREST & COST COMPARISON
# ============================================================

st.header("💹 View 2: Total Interest & Cost Comparison")

comparison_df = pd.DataFrame({

    "Strategy": [
        "On-time",
        "Early",
        "Late"
    ],

    "Total Interest": [
        on_time_interest,
        early_interest,
        late_interest
    ],

    "Total Repaid": [
        on_time_total,
        early_total,
        late_total
    ],

    "Payoff Time (Months)": [
        on_time_months,
        early_months,
        late_months
    ]
})


col1, col2 = st.columns(2)


# ============================================================
# INTEREST CHART
# ============================================================

with col1:

    fig2, ax2 = plt.subplots(figsize=(7, 5))

    ax2.bar(
        comparison_df["Strategy"],
        comparison_df["Total Interest"]
    )

    ax2.set_title("Total Interest by Payment Strategy")

    ax2.set_xlabel("Payment Strategy")

    ax2.set_ylabel("Total Interest (RM)")

    ax2.grid(
        axis="y",
        alpha=0.3
    )

    st.pyplot(fig2)


# ============================================================
# TOTAL COST CHART
# ============================================================

with col2:

    fig3, ax3 = plt.subplots(figsize=(7, 5))

    ax3.bar(
        comparison_df["Strategy"],
        comparison_df["Total Repaid"]
    )

    ax3.set_title("Total Amount Repaid by Strategy")

    ax3.set_xlabel("Payment Strategy")

    ax3.set_ylabel("Total Repaid (RM)")

    ax3.grid(
        axis="y",
        alpha=0.3
    )

    st.pyplot(fig3)


# ============================================================
# COMPARISON TABLE
# ============================================================

st.subheader("📋 Strategy Comparison")

formatted_comparison = comparison_df.copy()

formatted_comparison["Total Interest"] = (
    formatted_comparison["Total Interest"]
    .map(lambda x: f"RM {x:,.2f}")
)

formatted_comparison["Total Repaid"] = (
    formatted_comparison["Total Repaid"]
    .map(lambda x: f"RM {x:,.2f}")
)

st.dataframe(
    formatted_comparison,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# VIEW 3 - OPTIONAL
# PRINCIPAL VS INTEREST
# ============================================================

st.header("📊 View 3: Principal vs Interest")

principal_interest = pd.DataFrame({

    "Category": [
        "Principal",
        "Interest"
    ],

    "Amount": [
        principal,
        selected_interest
    ]
})


fig4, ax4 = plt.subplots(figsize=(7, 5))

ax4.pie(
    principal_interest["Amount"],
    labels=principal_interest["Category"],
    autopct="%1.1f%%",
    startangle=90
)

ax4.set_title(
    f"Principal vs Interest - {behavior}"
)

st.pyplot(fig4)


# ============================================================
# INTERPRETATION
# ============================================================

st.divider()

st.header("📝 Simulation Interpretation")


if behavior == "On-time":

    st.info(
        f"""
        **On-time Payment**

        The borrower pays the required monthly payment of
        approximately **RM {normal_payment:,.2f}**.

        Total interest paid:
        **RM {selected_interest:,.2f}**

        Total amount repaid:
        **RM {selected_total:,.2f}**

        Payoff time:
        **{selected_months} months**
        """
    )


elif behavior == "Early":

    st.success(
        f"""
        **Early Payment**

        The borrower pays 25% more than the normal monthly
        payment.

        Monthly payment:
        **RM {normal_payment * 1.25:,.2f}**

        Total interest paid:
        **RM {selected_interest:,.2f}**

        Total amount repaid:
        **RM {selected_total:,.2f}**

        Payoff time:
        **{selected_months} months**

        Compared with the normal strategy, this results in
        approximately **RM {difference:,.2f} in savings**.
        """
    )


else:

    st.warning(
        f"""
        **Late Payment**

        The borrower pays less than the required amount and
        occasionally misses a payment.

        Total interest paid:
        **RM {selected_interest:,.2f}**

        Total amount repaid:
        **RM {selected_total:,.2f}**

        Payoff time:
        **{selected_months} months**

        Compared with the normal strategy, this results in
        approximately **RM {difference:,.2f} in additional cost**.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Loan & Credit Card Payment Simulator | "
    "Interactive Streamlit Dashboard"
)