import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dynamic Pricing Intelligence System",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("store_summary.csv")
    return df

df = load_data()

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.title("📊 Dynamic Pricing Intelligence System")
st.markdown(
    "### Store Performance & Pricing Intelligence Dashboard"
)
st.caption(
    "Machine Learning • Data Analytics • Business Intelligence"
)

st.divider()

# ---------------------------------------------------------
# SIDEBAR FILTER
# ---------------------------------------------------------
st.sidebar.header("🔎 Dashboard Filters")

store_list = sorted(df["Store"].unique())

selected_store = st.sidebar.selectbox(
    "Select Store",
    ["All Stores"] + store_list
)

# Filter
if selected_store == "All Stores":
    filtered_df = df.copy()
else:
    filtered_df = df[df["Store"] == selected_store].copy()

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
total_sales = filtered_df["Total_Sales"].sum()
avg_sales = filtered_df["Average_Sales"].mean()
total_customers = filtered_df["Total_Customers"].sum()
avg_customers = filtered_df["Average_Customers"].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total Sales",
        f"₹{total_sales:,.0f}"
    )

with col2:
    st.metric(
        "📈 Average Sales",
        f"₹{avg_sales:,.0f}"
    )

with col3:
    st.metric(
        "👥 Total Customers",
        f"{total_customers:,.0f}"
    )

with col4:
    st.metric(
        "🛒 Avg Customers",
        f"{avg_customers:,.0f}"
    )

st.divider()

# ---------------------------------------------------------
# SELECTED STORE DETAILS
# ---------------------------------------------------------
if selected_store != "All Stores":
    store = filtered_df.iloc[0]

    st.subheader(f"🏪 Store {selected_store} Performance")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Total Sales",
            f"₹{store['Total_Sales']:,.0f}"
        )

    with c2:
        st.metric(
            "Average Sales",
            f"₹{store['Average_Sales']:,.0f}"
        )

    with c3:
        st.metric(
            "Total Customers",
            f"{store['Total_Customers']:,.0f}"
        )

    with c4:
        st.metric(
            "Average Customers",
            f"{store['Average_Customers']:,.0f}"
        )

    st.divider()

# ---------------------------------------------------------
# TOP STORES
# ---------------------------------------------------------
st.subheader("🏆 Top 10 Stores by Total Sales")

top_stores = (
    df[["Store", "Total_Sales"]]
    .sort_values("Total_Sales", ascending=False)
    .head(10)
    .set_index("Store")
)

st.bar_chart(top_stores)

# ---------------------------------------------------------
# BOTTOM STORES
# ---------------------------------------------------------
st.subheader("📉 Bottom 10 Stores by Total Sales")

bottom_stores = (
    df[["Store", "Total_Sales"]]
    .sort_values("Total_Sales", ascending=True)
    .head(10)
    .set_index("Store")
)

st.bar_chart(bottom_stores)

st.divider()

# ---------------------------------------------------------
# SALES VS CUSTOMERS
# ---------------------------------------------------------
st.subheader("💡 Sales vs Customer Relationship")

relationship_df = df[
    ["Store", "Total_Sales", "Total_Customers"]
].set_index("Store")

st.line_chart(relationship_df)

st.caption(
    "Stores with higher customer volumes generally generate higher total sales."
)

st.divider()

# ---------------------------------------------------------
# AVERAGE SALES ANALYSIS
# ---------------------------------------------------------
st.subheader("📊 Average Sales by Store")

avg_sales_chart = (
    df[["Store", "Average_Sales"]]
    .sort_values("Average_Sales", ascending=False)
    .head(15)
    .set_index("Store")
)

st.bar_chart(avg_sales_chart)

st.divider()

# ---------------------------------------------------------
# BUSINESS INSIGHTS
# ---------------------------------------------------------
st.subheader("🧠 Business Insights")

best_store = df.loc[df["Total_Sales"].idxmax()]
lowest_store = df.loc[df["Total_Sales"].idxmin()]

sales_customer_corr = df["Total_Sales"].corr(
    df["Total_Customers"]
)

i1, i2 = st.columns(2)

with i1:
    st.info(
        f"🏆 **Best Performing Store:** Store "
        f"{int(best_store['Store'])} generated "
        f"₹{best_store['Total_Sales']:,.0f} in total sales."
    )

    st.warning(
        f"📉 **Lowest Performing Store:** Store "
        f"{int(lowest_store['Store'])} generated "
        f"₹{lowest_store['Total_Sales']:,.0f} in total sales."
    )

with i2:
    st.success(
        f"👥 **Customer-Sales Correlation:** "
        f"{sales_customer_corr:.2f}"
    )

    st.info(
        "💡 **Pricing Insight:** Customer traffic is an "
        "important business driver of sales. Pricing decisions "
        "should therefore consider expected customer demand."
    )

st.divider()

# ---------------------------------------------------------
# STORE RANKING TABLE
# ---------------------------------------------------------
st.subheader("📋 Store Performance Ranking")

ranking_df = df.copy()
ranking_df["Sales_Rank"] = (
    ranking_df["Total_Sales"]
    .rank(method="min", ascending=False)
    .astype(int)
)

ranking_df = ranking_df.sort_values("Sales_Rank")

display_df = ranking_df[
    [
        "Sales_Rank",
        "Store",
        "Total_Sales",
        "Average_Sales",
        "Total_Customers",
        "Average_Customers"
    ]
].head(20)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()

st.caption(
    "Dynamic Pricing Intelligence System | "
    "Machine Learning • Data Analytics • Streamlit"
)
