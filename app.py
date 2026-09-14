import re
import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dynamic Pricing Intelligence System",
    page_icon="💰",
    layout="centered"
)


# ============================================================
# FILE PATH
# ============================================================

DATA_PATH = "store_summary.csv"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


df = load_data()


# ============================================================
# HEADER
# ============================================================

st.title("💰 Dynamic Pricing Intelligence System")

st.write(
    "An interactive analytics assistant for exploring "
    "store sales, customers, and business performance."
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_store_number(question):
    """
    Extracts a store number from questions such as:
    'What are the sales of Store 10?'
    """

    match = re.search(r"store\s*(\d+)", question.lower())

    if match:
        return int(match.group(1))

    return None


def get_store(store_number):
    """
    Returns information about a particular store.
    """

    if store_number is None:
        return None

    result = df[df["Store"] == store_number]

    if result.empty:
        return None

    return result.iloc[0]


def get_best_store():
    """
    Finds the store with the highest total sales.
    """

    row = df.loc[df["Total_Sales"].idxmax()]

    return int(row["Store"]), row["Total_Sales"]


def get_lowest_store():
    """
    Finds the store with the lowest total sales.
    """

    row = df.loc[df["Total_Sales"].idxmin()]

    return int(row["Store"]), row["Total_Sales"]


# ============================================================
# USER INPUT
# ============================================================

question = st.text_input(
    "💬 Ask your question:",
    placeholder="Example: What are the sales of Store 10?"
)


# ============================================================
# CHATBOT LOGIC
# ============================================================

if question:

    q = question.lower().strip()

    store_number = get_store_number(q)

    store = get_store(store_number)


    # --------------------------------------------------------
    # GREETING
    # --------------------------------------------------------

    if q in {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    }:

        st.success(
            "Hello! 👋 I am your Dynamic Pricing Intelligence Assistant."
        )

        st.write(
            "I can answer questions about store sales, "
            "customers, and performance."
        )


    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    elif q in {
        "help",
        "what can you do",
        "what do you do"
    }:

        st.subheader("💡 Example Questions")

        examples = [
            "What are the sales of Store 10?",
            "What are the average sales?",
            "How many customers did Store 10 have?",
            "Give me a summary of Store 10",
            "Which store has the highest sales?",
            "Which store has the lowest sales?",
            "Show top 10 stores",
            "How many stores are there?"
        ]

        for item in examples:
            st.write(f"• {item}")


    # --------------------------------------------------------
    # TOP 10 STORES
    # --------------------------------------------------------

    elif (
        "top 10" in q
        or "top ten" in q
        or "best 10" in q
    ):

        st.subheader("🏆 Top 10 Stores by Total Sales")

        top10 = df.nlargest(
            10,
            "Total_Sales"
        )[[
            "Store",
            "Total_Sales"
        ]].copy()

        top10["Store"] = top10["Store"].astype(int)

        top10["Total_Sales"] = top10[
            "Total_Sales"
        ].map(
            lambda x: f"₹{x:,.0f}"
        )

        st.dataframe(
            top10,
            use_container_width=True,
            hide_index=True
        )


    # --------------------------------------------------------
    # NUMBER OF STORES
    # --------------------------------------------------------

    elif (
        "number of stores" in q
        or "how many stores" in q
        or "total stores" in q
        or "store count" in q
    ):

        st.subheader("🏪 Store Count")

        total_stores = df["Store"].nunique()

        st.write(
            f"There are **{total_stores:,} stores** "
            "in the dataset."
        )


    # --------------------------------------------------------
    # HIGHEST PERFORMING STORE
    # --------------------------------------------------------

    elif (
        "highest sales" in q
        or "highest selling" in q
        or "best store" in q
        or "best performing" in q
        or "top performing" in q
    ):

        store_id, sales = get_best_store()

        st.subheader("🏆 Best Performing Store")

        st.write(f"**Store:** {store_id}")

        st.write(
            f"**Total Sales:** ₹{sales:,.0f}"
        )


    # --------------------------------------------------------
    # LOWEST PERFORMING STORE
    # --------------------------------------------------------

    elif (
        "lowest sales" in q
        or "lowest selling" in q
        or "worst store" in q
        or "lowest performing" in q
    ):

        store_id, sales = get_lowest_store()

        st.subheader("📉 Lowest Performing Store")

        st.write(f"**Store:** {store_id}")

        st.write(
            f"**Total Sales:** ₹{sales:,.0f}"
        )


    # --------------------------------------------------------
    # AVERAGE SALES
    # --------------------------------------------------------

    elif (
        "average sales" in q
        or "mean sales" in q
        or "typical sales" in q
    ):

        st.subheader("📊 Average Sales")

        average_sales = df["Average_Sales"].mean()

        st.write(
            f"**Average Daily Sales:** "
            f"₹{average_sales:,.2f}"
        )


    # --------------------------------------------------------
    # STORE CUSTOMER INFORMATION
    # --------------------------------------------------------

    elif (
        store is not None
        and (
            "customer" in q
            or "customers" in q
        )
    ):

        st.subheader(
            f"👥 Store {store_number} Customers"
        )

        st.write(
            f"**Total Customers:** "
            f"{store['Total_Customers']:,.0f}"
        )

        st.write(
            f"**Average Daily Customers:** "
            f"{store['Average_Customers']:,.2f}"
        )


    # --------------------------------------------------------
    # STORE SUMMARY
    # --------------------------------------------------------

    elif (
        store is not None
        and (
            "summary" in q
            or "insight" in q
            or "details" in q
            or "information" in q
        )
    ):

        st.subheader(
            f"🏪 Store {store_number} Summary"
        )

        st.write(
            f"**Total Sales:** "
            f"₹{store['Total_Sales']:,.0f}"
        )

        st.write(
            f"**Average Daily Sales:** "
            f"₹{store['Average_Sales']:,.2f}"
        )

        st.write(
            f"**Total Customers:** "
            f"{store['Total_Customers']:,.0f}"
        )

        st.write(
            f"**Average Daily Customers:** "
            f"{store['Average_Customers']:,.2f}"
        )


    # --------------------------------------------------------
    # STORE SALES
    # --------------------------------------------------------

    elif (
        store is not None
        and (
            "sales" in q
            or "revenue" in q
        )
    ):

        st.subheader(
            f"📊 Store {store_number} Sales"
        )

        st.write(
            f"**Total Sales:** "
            f"₹{store['Total_Sales']:,.0f}"
        )

        st.write(
            f"**Average Daily Sales:** "
            f"₹{store['Average_Sales']:,.2f}"
        )


    # --------------------------------------------------------
    # STORE NOT FOUND
    # --------------------------------------------------------

    elif (
        store_number is not None
        and store is None
    ):

        st.error(
            f"Store {store_number} was not found "
            "in the dataset."
        )


    # --------------------------------------------------------
    # UNKNOWN QUESTION
    # --------------------------------------------------------

    else:

        st.warning(
            "I couldn't understand that question. "
            "Type **help** to see example questions."
        )


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Data source: store-level summary generated "
    "from the project dataset."
)
