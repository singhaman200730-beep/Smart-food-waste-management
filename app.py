import streamlit as st
import pandas as pd
import altair as alt

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Food Waste Management",
    page_icon="🍽️",
    layout="wide"
)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div style="
    background: linear-gradient(135deg, #1f4e5f, #2c7a7b);
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 25px;
">
    <h1 style="color:white; margin:0;">
        🍽️ Smart Food Waste Management System
    </h1>
    <p style="color:white; font-size:18px; margin:8px 0 0 0;">
        Hostel Mess Food Waste Monitoring & Analysis Dashboard
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# LOAD EXCEL FILE
# =========================================================

file_path = "food_waste.xlsx"

try:
    sheets = pd.read_excel(
        file_path,
        sheet_name=None
    )

    df = pd.concat(
        sheets.values(),
        ignore_index=True
    )

except Exception as e:
    st.error(f"❌ Error loading Excel file: {e}")
    st.stop()

# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)

# =========================================================
# IMPORTANT:
# YOUR EXCEL HAS "MENU ITEMS", NOT "FOOD ITEM"
# =========================================================

if "Food Item" not in df.columns and "Menu Items" in df.columns:

    df = df.rename(
        columns={
            "Menu Items": "Food Item"
        }
    )

# =========================================================
# CREATE MONTH COLUMN IF REQUIRED
# =========================================================

if "Date" in df.columns:

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

if "Month" not in df.columns:

    df["Month"] = df["Date"].dt.month_name()

# =========================================================
# CONVERT NUMERIC COLUMNS
# =========================================================

numeric_columns = [
    "Prepared (kg)",
    "Consumed (kg)",
    "Wasted (kg)",
    "Students Served",
    "Cost Loss (₹)"
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)

# =========================================================
# REQUIRED COLUMNS CHECK
# =========================================================

required_columns = [
    "Date",
    "Month",
    "Meal",
    "Food Item",
    "Prepared (kg)",
    "Consumed (kg)",
    "Wasted (kg)",
    "Students Served",
    "Cost Loss (₹)"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "❌ Missing columns in Excel file: "
        + ", ".join(missing_columns)
    )

    st.write(
        "Columns found in your Excel file:"
    )

    st.write(
        df.columns.tolist()
    )

    st.stop()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

# ---------------------------------------------------------
# MONTH FILTER
# ---------------------------------------------------------

month_order = [
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
    "January",
    "February",
    "March",
    "April",
    "May"
]

available_months = [
    month
    for month in month_order
    if month in df["Month"].dropna().unique()
]

# Add any other month values
for month in df["Month"].dropna().unique():

    if month not in available_months:

        available_months.append(month)

selected_month = st.sidebar.selectbox(
    "📅 Select Month",
    ["All"] + available_months
)

# ---------------------------------------------------------
# MEAL FILTER
# ---------------------------------------------------------

available_meals = sorted(
    df["Meal"]
    .dropna()
    .unique()
    .tolist()
)

selected_meal = st.sidebar.selectbox(
    "🍛 Select Meal",
    ["All"] + available_meals
)

# ---------------------------------------------------------
# FOOD ITEM FILTER
# ---------------------------------------------------------

available_foods = sorted(
    df["Food Item"]
    .dropna()
    .unique()
    .tolist()
)

selected_food = st.sidebar.selectbox(
    "🍴 Select Food Item",
    ["All"] + available_foods
)

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

if selected_month != "All":

    filtered_df = filtered_df[
        filtered_df["Month"] == selected_month
    ]

if selected_meal != "All":

    filtered_df = filtered_df[
        filtered_df["Meal"] == selected_meal
    ]

if selected_food != "All":

    filtered_df = filtered_df[
        filtered_df["Food Item"] == selected_food
    ]

# =========================================================
# CHECK EMPTY DATA
# =========================================================

if filtered_df.empty:

    st.warning(
        "⚠️ No data available for the selected filters."
    )

    st.stop()

# =========================================================
# MAIN CALCULATIONS
# =========================================================

total_prepared = filtered_df[
    "Prepared (kg)"
].sum()

total_consumed = filtered_df[
    "Consumed (kg)"
].sum()

total_wasted = filtered_df[
    "Wasted (kg)"
].sum()

total_cost = filtered_df[
    "Cost Loss (₹)"
].sum()

total_students = filtered_df[
    "Students Served"
].sum()

# Waste percentage

if total_prepared > 0:

    waste_rate = (
        total_wasted /
        total_prepared
    ) * 100

else:

    waste_rate = 0

# Consumption percentage

if total_prepared > 0:

    consumption_rate = (
        total_consumed /
        total_prepared
    ) * 100

else:

    consumption_rate = 0

# =========================================================
# DASHBOARD OVERVIEW
# =========================================================

st.subheader("📊 Food Waste Overview")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:

    st.metric(
        "🍚 Food Prepared",
        f"{total_prepared:,.1f} kg"
    )

with col2:

    st.metric(
        "🍽️ Food Consumed",
        f"{total_consumed:,.1f} kg"
    )

with col3:

    st.metric(
        "🗑️ Food Wasted",
        f"{total_wasted:,.1f} kg"
    )

with col4:

    st.metric(
        "⚠️ Waste Rate",
        f"{waste_rate:.1f}%"
    )

with col5:

    st.metric(
        "💰 Cost Loss",
        f"₹{total_cost:,.0f}"
    )

with col6:

    st.metric(
        "👥 Students Served",
        f"{total_students:,.0f}"
    )

# =========================================================
# SECTION 1
# MONTHLY WASTE ANALYSIS
# =========================================================

st.markdown("---")

st.subheader(
    "📅 Monthly Food Waste Analysis"
)

monthly = (
    filtered_df
    .groupby("Month")
    .agg(
        Prepared=("Prepared (kg)", "sum"),
        Consumed=("Consumed (kg)", "sum"),
        Wasted=("Wasted (kg)", "sum"),
        Cost=("Cost Loss (₹)", "sum")
    )
    .reset_index()
)

monthly["Waste Rate"] = (
    monthly["Wasted"] /
    monthly["Prepared"] *
    100
).fillna(0)

monthly["Month"] = pd.Categorical(
    monthly["Month"],
    categories=month_order,
    ordered=True
)

monthly = monthly.sort_values("Month")

chart_month = (
    alt.Chart(monthly)
    .mark_bar(
        cornerRadiusTopLeft=7,
        cornerRadiusTopRight=7
    )
    .encode(

        x=alt.X(
            "Month:N",
            title="Month"
        ),

        y=alt.Y(
            "Wasted:Q",
            title="Food Waste (kg)"
        ),

        tooltip=[

            alt.Tooltip(
                "Month:N",
                title="Month"
            ),

            alt.Tooltip(
                "Prepared:Q",
                title="Prepared (kg)",
                format=".1f"
            ),

            alt.Tooltip(
                "Consumed:Q",
                title="Consumed (kg)",
                format=".1f"
            ),

            alt.Tooltip(
                "Wasted:Q",
                title="Wasted (kg)",
                format=".1f"
            ),

            alt.Tooltip(
                "Waste Rate:Q",
                title="Waste Rate (%)",
                format=".1f"
            ),

            alt.Tooltip(
                "Cost:Q",
                title="Cost Loss (₹)",
                format=",.0f"
            )
        ]
    )
    .properties(
        height=380
    )
)

st.altair_chart(
    chart_month,
    use_container_width=True
)

# =========================================================
# SECTION 2
# WASTE RATE BY MEAL
# =========================================================

st.subheader(
    "🍛 Waste Rate by Meal"
)

meal = (
    filtered_df
    .groupby("Meal")
    .agg(
        Prepared=("Prepared (kg)", "sum"),
        Consumed=("Consumed (kg)", "sum"),
        Wasted=("Wasted (kg)", "sum"),
        Cost=("Cost Loss (₹)", "sum")
    )
    .reset_index()
)

meal["Waste Rate"] = (
    meal["Wasted"] /
    meal["Prepared"] *
    100
).fillna(0)

meal = meal.sort_values(
    "Waste Rate",
    ascending=False
)

chart_meal = (
    alt.Chart(meal)
    .mark_bar(
        cornerRadiusTopRight=7,
        cornerRadiusBottomRight=7
    )
    .encode(

        y=alt.Y(
            "Meal:N",
            sort="-x",
            title="Meal"
        ),

        x=alt.X(
            "Waste Rate:Q",
            title="Waste Rate (%)"
        ),

        tooltip=[

            alt.Tooltip(
                "Meal:N",
                title="Meal"
            ),

            alt.Tooltip(
                "Prepared:Q",
                title="Prepared (kg)",
                format=".1f"
            ),

            alt.Tooltip(
                "Consumed:Q",
                title="Consumed (kg)",
                format=".1f"
            ),

            alt.Tooltip(
                "Wasted:Q",
                title="Wasted (kg)",
                format=".1f"
            ),

            alt.Tooltip(
                "Waste Rate:Q",
                title="Waste Rate (%)",
                format=".1f"
            ),

            alt.Tooltip(
                "Cost:Q",
                title="Cost Loss (₹)",
                format=",.0f"
            )
        ]
    )
    .properties(
        height=300
    )
)

st.altair_chart(
    chart_meal,
    use_container_width=True
)

# =========================================================
# SECTION 3
# DAILY WASTE TREND
# =========================================================

st.subheader(
    "📈 Daily Food Waste Trend"
)

daily = (
    filtered_df
    .groupby("Date")
    .agg(
        Wasted=("Wasted (kg)", "sum")
    )
    .reset_index()
    .sort_values("Date")
)

daily["7-Day Average"] = (
    daily["Wasted"]
    .rolling(
        window=7,
        min_periods=1
    )
    .mean()
)

# Actual waste

actual_line = (
    alt.Chart(daily)
    .mark_line(
        point=True
    )
    .encode(

        x=alt.X(
            "Date:T",
            title="Date"
        ),

        y=alt.Y(
            "Wasted:Q",
            title="Waste (kg)"
        ),

        tooltip=[

            alt.Tooltip(
                "Date:T",
                title="Date",
                format="%d %b %Y"
            ),

            alt.Tooltip(
                "Wasted:Q",
                title="Waste (kg)",
                format=".1f"
            )
        ]
    )
)

# 7-day average

average_line = (
    alt.Chart(daily)
    .mark_line(
        strokeDash=[6, 4]
    )
    .encode(

        x="Date:T",

        y=alt.Y(
            "7-Day Average:Q",
            title="Waste (kg)"
        ),

        tooltip=[

            alt.Tooltip(
                "Date:T",
                title="Date",
                format="%d %b %Y"
            ),

            alt.Tooltip(
                "7-Day Average:Q",
                title="7-Day Average",
                format=".1f"
            )
        ]
    )
)

st.altair_chart(
    actual_line + average_line,
    use_container_width=True
)

st.caption(
    "The solid line shows actual daily waste. "
    "The dashed line shows the 7-day average trend."
)

# =========================================================
# SECTION 4
# TOP 10 FOOD ITEMS
# =========================================================

st.subheader(
    "🏆 Top 10 Food Items by Waste"
)

food = (
    filtered_df
    .groupby("Food Item")
    .agg(
        Wasted=("Wasted (kg)", "sum"),
        Prepared=("Prepared (kg)", "sum"),
        Cost=("Cost Loss (₹)", "sum")
    )
    .reset_index()
)

food["Waste Rate"] = (
    food["Wasted"] /
    food["Prepared"] *
    100
).fillna(0)

food = (
    food
    .sort_values(
        "Wasted",
        ascending=False
    )
    .head(10)
)

chart_food = (
    alt.Chart(food)
    .mark_bar(
        cornerRadiusTopRight=7,
        cornerRadiusBottomRight=7
    )
    .encode(

        y=alt.Y(
            "Food Item:N",
            sort="-x",
            title="Food Item"
        ),

        x=alt.X(
            "Wasted:Q",
            title="Waste (kg)"
        ),

        tooltip=[

            alt.Tooltip(
                "Food Item:N",
                title="Food Item"
            ),

            alt.Tooltip(
                "Wasted:Q",
                title="Waste (kg)",
                format=".1f"
            ),

            alt.Tooltip(
                "Prepared:Q",
                title="Prepared (kg)",
                format=".1f"
            ),

            alt.Tooltip(
                "Waste Rate:Q",
                title="Waste Rate (%)",
                format=".1f"
            ),

            alt.Tooltip(
                "Cost:Q",
                title="Cost Loss (₹)",
                format=",.0f"
            )
        ]
    )
    .properties(
        height=450
    )
)

st.altair_chart(
    chart_food,
    use_container_width=True
)

# =========================================================
# SECTION 5
# FOOD UTILIZATION
# =========================================================

st.subheader(
    "🔄 Prepared vs Consumed vs Wasted"
)

utilization = pd.DataFrame({

    "Category": [
        "Prepared",
        "Consumed",
        "Wasted"
    ],

    "Quantity": [
        total_prepared,
        total_consumed,
        total_wasted
    ]
})

chart_utilization = (
    alt.Chart(utilization)
    .mark_bar(
        cornerRadiusTopLeft=7,
        cornerRadiusTopRight=7
    )
    .encode(

        x=alt.X(
            "Category:N",
            title="Food Status"
        ),

        y=alt.Y(
            "Quantity:Q",
            title="Quantity (kg)"
        ),

        tooltip=[

            alt.Tooltip(
                "Category:N",
                title="Category"
            ),

            alt.Tooltip(
                "Quantity:Q",
                title="Quantity (kg)",
                format=".1f"
            )
        ]
    )
    .properties(
        height=350
    )
)

st.altair_chart(
    chart_utilization,
    use_container_width=True
)

# =========================================================
# SECTION 6
# COST LOSS BY FOOD ITEM
# =========================================================

st.subheader(
    "💰 Top Food Items by Cost Loss"
)

cost_food = (
    filtered_df
    .groupby("Food Item")
    .agg(
        Cost_Loss=("Cost Loss (₹)", "sum"),
        Waste=("Wasted (kg)", "sum")
    )
    .reset_index()
    .sort_values(
        "Cost_Loss",
        ascending=False
    )
    .head(10)
)

chart_cost = (
    alt.Chart(cost_food)
    .mark_bar(
        cornerRadiusTopRight=7,
        cornerRadiusBottomRight=7
    )
    .encode(

        y=alt.Y(
            "Food Item:N",
            sort="-x",
            title="Food Item"
        ),

        x=alt.X(
            "Cost_Loss:Q",
            title="Cost Loss (₹)"
        ),

        tooltip=[

            alt.Tooltip(
                "Food Item:N",
                title="Food Item"
            ),

            alt.Tooltip(
                "Cost_Loss:Q",
                title="Cost Loss (₹)",
                format=",.0f"
            ),

            alt.Tooltip(
                "Waste:Q",
                title="Waste (kg)",
                format=".1f"
            )
        ]
    )
    .properties(
        height=450
    )
)

st.altair_chart(
    chart_cost,
    use_container_width=True
)

# =========================================================
# SECTION 7
# WASTE DISTRIBUTION
# =========================================================

st.subheader(
    "🍽️ Waste Distribution by Meal"
)

meal_pie = (
    filtered_df
    .groupby("Meal")["Wasted (kg)"]
    .sum()
    .reset_index()
)

pie_chart = (
    alt.Chart(meal_pie)
    .mark_arc(
        innerRadius=65
    )
    .encode(

        theta=alt.Theta(
            "Wasted (kg):Q"
        ),

        color=alt.Color(
            "Meal:N",
            title="Meal"
        ),

        tooltip=[

            alt.Tooltip(
                "Meal:N",
                title="Meal"
            ),

            alt.Tooltip(
                "Wasted (kg):Q",
                title="Waste (kg)",
                format=".1f"
            )
        ]
    )
    .properties(
        height=400
    )
)

st.altair_chart(
    pie_chart,
    use_container_width=True
)
# =========================================================
# WASTE STATUS
# =========================================================

st.markdown("---")
st.subheader("🚦 Current Waste Status")

if waste_rate < 10:
    status = "🟢 LOW WASTE"
    status_message = "Food waste is under control."
elif waste_rate < 15:
    status = "🟡 MODERATE WASTE"
    status_message = "Waste should be monitored and reduced."
else:
    status = "🔴 HIGH WASTE"
    status_message = "Immediate action is recommended to reduce food waste."

status_col1, status_col2 = st.columns([1, 2])

with status_col1:
    st.metric(
        "Waste Status",
        status
    )

with status_col2:
    st.info(
        f"Current waste rate: **{waste_rate:.1f}%**  \n"
        f"{status_message}"
    )
    # =========================================================
# MEAL PERFORMANCE COMPARISON
# =========================================================

st.markdown("---")

st.subheader("🍛 Meal Performance Comparison")

meal_performance = (
    filtered_df
    .groupby("Meal")
    .agg(
        Prepared=("Prepared (kg)", "sum"),
        Consumed=("Consumed (kg)", "sum"),
        Wasted=("Wasted (kg)", "sum"),
        Cost_Loss=("Cost Loss (₹)", "sum")
    )
    .reset_index()
)

meal_performance["Waste Rate (%)"] = (
    meal_performance["Wasted"]
    / meal_performance["Prepared"]
    * 100
).fillna(0)

meal_performance = meal_performance.sort_values(
    "Waste Rate (%)",
    ascending=False
)

st.dataframe(
    meal_performance.style.format({
        "Prepared": "{:.1f}",
        "Consumed": "{:.1f}",
        "Wasted": "{:.1f}",
        "Cost_Loss": "₹{:,.0f}",
        "Waste Rate (%)": "{:.1f}%"
    }),
    use_container_width=True,
    hide_index=True
)
# =========================================================
# SECTION 8
# SMART INSIGHTS
# =========================================================

st.markdown("---")

st.subheader(
    "🧠 Smart Insights"
)

# Highest waste food

if not food.empty:

    highest_food = food.iloc[0]["Food Item"]

    highest_food_waste = food.iloc[0]["Wasted"]

else:

    highest_food = "N/A"

    highest_food_waste = 0

# Highest waste meal

if not meal.empty:

    highest_meal = meal.iloc[0]["Meal"]

    highest_meal_rate = meal.iloc[0]["Waste Rate"]

else:

    highest_meal = "N/A"

    highest_meal_rate = 0

# Insight cards

i1, i2, i3 = st.columns(3)

with i1:

    st.info(
        f"""
        🏆 **Most Wasted Food**

        **{highest_food}**

        {highest_food_waste:.1f} kg wasted
        """
    )

with i2:

    st.warning(
        f"""
        🍛 **Highest Waste Meal**

        **{highest_meal}**

        {highest_meal_rate:.1f}% waste rate
        """
    )

with i3:

    st.info(
        f"""
        💰 **Financial Impact**

        Total estimated loss

        **₹{total_cost:,.0f}**
        """
    )

# =========================================================
# SMART RECOMMENDATION
# =========================================================

st.subheader(
    "💡 Smart Recommendation"
)

if waste_rate >= 20:

    st.error(
        """
        🚨 **High Waste Alert**

        Food waste is significantly high.

        Recommended actions:

        • Reduce preparation quantity for high-waste meals  
        • Monitor portion sizes  
        • Review frequently wasted food items  
        • Compare prepared quantity with actual consumption
        """
    )

elif waste_rate >= 10:

    st.warning(
        """
        ⚠️ **Moderate Waste Level**

        Waste should be monitored carefully.

        Recommended action:

        Adjust preparation quantities according to
        actual consumption patterns.
        """
    )

else:

    st.success(
        """
        ✅ **Waste Level Under Control**

        Current food utilization is relatively efficient.

        Continue monitoring daily waste and
        high-waste food items.
        """
    )

# =========================================================
# WASTE REDUCTION TARGET
# =========================================================

st.subheader(
    "🎯 Waste Reduction Target"
)

target = 10

target_col1, target_col2 = st.columns(2)

with target_col1:

    if waste_rate <= target:

        st.success(
            f"""
            ✅ **Target Achieved**

            Current waste rate:
            **{waste_rate:.1f}%**

            Target:
            **{target}%**
            """
        )

    else:

        st.warning(
            f"""
            ⚠️ **Target Not Achieved**

            Current waste rate:
            **{waste_rate:.1f}%**

            Target:
            **{target}%**
            """
        )

with target_col2:

    if waste_rate > target:

        reduction_needed = (
            waste_rate - target
        )

        st.metric(
            "Reduction Needed",
            f"{reduction_needed:.1f}%"
        )

    else:

        st.metric(
            "Target Status",
            "Achieved ✅"
        )

# =========================================================
# DATA TABLE
# =========================================================

st.markdown("---")

st.subheader(
    "📋 Filtered Food Waste Data"
)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# DOWNLOAD DATA
# =========================================================

st.subheader(
    "📥 Download Filtered Data"
)

csv = filtered_df.to_csv(
    index=False
)

st.download_button(
    label="⬇️ Download CSV",
    data=csv,
    file_name="food_waste_filtered.csv",
    mime="text/csv"
)

# =========================================================
# SIDEBAR PROJECT INFORMATION
# =========================================================

st.sidebar.markdown("---")

st.sidebar.subheader(
    "📌 Project Information"
)

st.sidebar.write(
    "🍽️ Smart Food Waste Management"
)

st.sidebar.write(
    "🏫 Hostel Mess Food Waste Analysis"
)

st.sidebar.write(
    "📊 Data-driven monitoring"
)

st.sidebar.write(
    "💡 Waste reduction support"
)

st.sidebar.markdown("---")

st.sidebar.success(
    "Dashboard Ready ✅"
)