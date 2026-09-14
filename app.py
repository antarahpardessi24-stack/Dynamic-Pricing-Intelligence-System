import streamlit as st
import pandas as pd
import joblib
import os

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Dynamic Pricing Intelligence System",
    page_icon="💰",
    layout="wide"
)

# =========================================================
# FILE PATHS
# =========================================================
DATA_PATH = "pricing_data_processed.csv"
MODEL_PATH = "best_pricing_model.pkl"
FEATURES_PATH = "model_features.pkl"

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        st.error(
            f"Missing file: {DATA_PATH}. "
            "Upload this file to the same GitHub repository as app.py."
        )
        st.stop()

    df = pd.read_csv(DATA_PATH)
    return df


@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        st.error(
            f"Missing file: {MODEL_PATH}. "
            "Upload the trained model to the same GitHub repository as app.py."
        )
        st.stop()

    model = joblib.load(MODEL_PATH)

    features = None
    if os.path.exists(FEATURES_PATH):
        features = joblib.load(FEATURES_PATH)

    return model, features


df = load_data()
model, model_features = load_model()

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def money(value):
    return f"₹{value:,.2f}"


def get_store_data(store_id):
    return df[df["Store"] == int(store_id)]


def store_summary(store_id):
    data = get_store_data(store_id)

    if data.empty:
        return None

    return {
        "sales": data["Sales"].sum(),
        "avg_sales": data["Sales"].mean(),
        "customers": data["Customers"].sum(),
        "avg_customers": data["Customers"].mean(),
        "records": len(data)
    }


def best_store():
    result = df.groupby("Store")["Sales"].sum().sort_values(ascending=False)
    return int(result.index[0]), result.iloc[0]


def lowest_store():
    result = df.groupby("Store")["Sales"].sum().sort_values()
    return int(result.index[0]), result.iloc[0]


def promotion_analysis():
    promo = df.loc[df["Promo"] == 1, "Sales"].mean()
    non_promo = df.loc[df["Promo"] == 0, "Sales"].mean()

    difference = ((promo - non_promo) / non_promo) * 100

    return promo, non_promo, difference


def predict_store_sales(store_id):
    data = get_store_data(store_id)

    if data.empty:
        return None

    row = data.iloc[0].copy()

    # The model was trained without Date and Sales.
    feature_columns = [
        "Store",
        "DayOfWeek",
        "Customers",
        "Open",
        "Promo",
        "StateHoliday",
        "SchoolHoliday",
        "StoreType",
        "Assortment",
        "CompetitionDistance",
        "CompetitionOpenSinceMonth",
        "CompetitionOpenSinceYear",
        "Promo2",
        "Promo2SinceWeek",
        "Promo2SinceYear",
        "PromoInterval"
    ]

    missing = [c for c in feature_columns if c not in row.index]

    if missing:
        return None

    X = pd.DataFrame([[row[c] for c in feature_columns]], columns=feature_columns)

    try:
        prediction = model.predict(X)[0]
        return prediction
    except Exception:
        return None


def pricing_recommendation(store_id, current_price):
    prediction = predict_store_sales(store_id)

    if prediction is None:
        return None

    # Simulated pricing scenario.
    # Historical product-price data is not available in the dataset.
    recommended_price = current_price * 1.10

    simulated_demand = prediction * 1.10
    simulated_revenue = recommended_price * simulated_demand

    return {
        "current_price": current_price,
        "recommended_price": recommended_price,
        "predicted_demand": simulated_demand,
        "simulated_revenue": simulated_revenue
    }


def chatbot_response(question):
    q = question.lower().strip()

    # -----------------------------------------------------
    # GREETING
    # -----------------------------------------------------
    if any(word in q for word in ["hello", "hi", "hey", "hii"]):
        return (
            "👋 Hello! I am the Dynamic Pricing Intelligence chatbot. "
            "Ask me about store sales, customers, promotions, predictions, "
            "or pricing recommendations."
        )

    # -----------------------------------------------------
    # HELP
    # -----------------------------------------------------
    if "help" in q or "what can you do" in q:
        return (
            "I can answer questions such as:\n\n"
            "• What are the sales of Store 10?\n"
            "• How many customers did Store 10 have?\n"
            "• Give me a summary of Store 10.\n"
            "• Which store has the highest sales?\n"
            "• Do promotions increase sales?\n"
            "• Predict sales for Store 10.\n"
            "• Recommend a price for Store 10 at ₹100."
        )

    # -----------------------------------------------------
    # BEST STORE
    # -----------------------------------------------------
    if (
        ("highest" in q or "best" in q or "top" in q)
        and "sales" in q
    ):
        store, sales = best_store()
        return (
            f"🏆 Store {store} has the highest total sales: "
            f"{money(sales)}."
        )

    # -----------------------------------------------------
    # LOWEST STORE
    # -----------------------------------------------------
    if (
        ("lowest" in q or "worst" in q)
        and "sales" in q
    ):
        store, sales = lowest_store()
        return (
            f"📉 Store {store} has the lowest total sales: "
            f"{money(sales)}."
        )

    # -----------------------------------------------------
    # PROMOTION
    # -----------------------------------------------------
    if "promo" in q or "promotion" in q:
        promo, non_promo, difference = promotion_analysis()

        return (
            f"🎯 Promotion analysis:\n\n"
            f"• Average sales with promotion: {money(promo)}\n"
            f"• Average sales without promotion: {money(non_promo)}\n"
            f"• Difference: {difference:.2f}% higher during promotions."
        )

    # -----------------------------------------------------
    # FIND STORE NUMBER
    # -----------------------------------------------------
    import re

    match = re.search(r"store\s*(\d+)", q)

    if match:
        store_id = int(match.group(1))
        summary = store_summary(store_id)

        if summary is None:
            return f"❌ Store {store_id} was not found in the dataset."

        # -------------------------------------------------
        # PRICING RECOMMENDATION
        # -------------------------------------------------
        if "price" in q or "pricing" in q:
            price_match = re.search(
                r"(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)",
                q
            )

            if price_match:
                current_price = float(price_match.group(1))
            else:
                current_price = 100.0

            result = pricing_recommendation(
                store_id,
                current_price
            )

            if result is None:
                return "⚠️ Unable to generate a pricing recommendation."

            return (
                f"💰 Pricing recommendation for Store {store_id}:\n\n"
                f"• Current price: {money(result['current_price'])}\n"
                f"• Recommended price: {money(result['recommended_price'])}\n"
                f"• Predicted demand: {result['predicted_demand']:,.0f}\n"
                f"• Simulated revenue: {money(result['simulated_revenue'])}\n\n"
                "⚠️ Pricing scenarios are simulated because the dataset "
                "does not contain historical product prices."
            )

        # -------------------------------------------------
        # SALES PREDICTION
        # -------------------------------------------------
        if "predict" in q or "prediction" in q or "forecast" in q:
            prediction = predict_store_sales(store_id)

            if prediction is None:
                return (
                    "⚠️ Prediction could not be generated. "
                    "Please check the model and feature files."
                )

            return (
                f"🤖 Predicted sales for Store {store_id}: "
                f"{money(prediction)}."
            )

        # -------------------------------------------------
        # STORE SUMMARY
        # -------------------------------------------------
        if "summary" in q or "overview" in q:
            return (
                f"🏪 Store {store_id} summary:\n\n"
                f"• Total sales: {money(summary['sales'])}\n"
                f"• Average daily sales: {money(summary['avg_sales'])}\n"
                f"• Total customers: {summary['customers']:,.0f}\n"
                f"• Average customers: {summary['avg_customers']:,.2f}\n"
                f"• Records: {summary['records']:,}"
            )

        # -------------------------------------------------
        # CUSTOMERS
        # -------------------------------------------------
        if "customer" in q:
            return (
                f"👥 Store {store_id} had "
                f"{summary['customers']:,.0f} total customers "
                f"with an average of "
                f"{summary['avg_customers']:,.2f} customers per record."
            )

        # -------------------------------------------------
        # SALES
        # -------------------------------------------------
        if "sale" in q or "revenue" in q:
            return (
                f"💰 Store {store_id} generated "
                f"{money(summary['sales'])} in total sales. "
                f"Its average sales per record were "
                f"{money(summary['avg_sales'])}."
            )

    # -----------------------------------------------------
    # GENERAL DATASET QUESTIONS
    # -----------------------------------------------------
    if "average sales" in q or "mean sales" in q:
        return (
            f"📊 Average sales across the dataset are "
            f"{money(df['Sales'].mean())}."
        )

    if "number of stores" in q or "how many stores" in q:
        return (
            f"🏪 The dataset contains "
            f"{df['Store'].nunique():,} unique stores."
        )

    if "average customer" in q:
        return (
            f"👥 Average customers per record are "
            f"{df['Customers'].mean():,.2f}."
        )

    # -----------------------------------------------------
    # FALLBACK
    # -----------------------------------------------------
    return (
        "🤔 I couldn't understand that question.\n\n"
        "Try asking:\n"
        "• What are the sales of Store 10?\n"
        "• Give me a summary of Store 10.\n"
        "• Which store has the highest sales?\n"
        "• Do promotions increase sales?\n"
        "• Predict sales for Store 10.\n"
        "• Recommend a price for Store 10 at ₹100."
    )


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("💰 Dynamic Pricing")
st.sidebar.markdown(
    "**Dynamic Pricing Intelligence System**"
)
st.sidebar.divider()

st.sidebar.metric(
    "Stores",
    f"{df['Store'].nunique():,}"
)

st.sidebar.metric(
    "Records",
    f"{len(df):,}"
)

st.sidebar.metric(
    "Avg Sales",
    money(df["Sales"].mean())
)

# =========================================================
# MAIN HEADER
# =========================================================
st.title("💰 Dynamic Pricing Intelligence System")

st.markdown(
    "### 🤖 Interactive Pricing Intelligence Chatbot"
)

st.caption(
    "Ask questions about sales, customers, promotions, "
    "machine learning predictions and pricing scenarios."
)

st.divider()

# =========================================================
# KPI CARDS
# =========================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total Sales",
        money(df["Sales"].sum())
    )

with col2:
    st.metric(
        "📊 Average Sales",
        money(df["Sales"].mean())
    )

with col3:
    st.metric(
        "👥 Total Customers",
        f"{df['Customers'].sum():,.0f}"
    )

with col4:
    st.metric(
        "🏪 Stores",
        f"{df['Store'].nunique():,}"
    )

st.divider()

# =========================================================
# CHATBOT
# =========================================================
st.subheader("💬 Ask the Pricing Assistant")

question = st.text_input(
    "Ask a question",
    placeholder="Example: What are the sales of Store 10?"
)

if question:
    answer = chatbot_response(question)

    st.markdown("### 🤖 Assistant")
    st.info(answer)

# =========================================================
# EXAMPLE QUESTIONS
# =========================================================
st.subheader("💡 Try these questions")

examples = [
    "What are the sales of Store 10?",
    "How many customers did Store 10 have?",
    "Give me a summary of Store 10.",
    "Which store has the highest sales?",
    "Which store has the lowest sales?",
    "Do promotions increase sales?",
    "Predict sales for Store 10.",
    "Recommend a price for Store 10 at ₹100."
]

cols = st.columns(2)

for i, example in enumerate(examples):
    with cols[i % 2]:
        st.markdown(f"• {example}")

# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "Dynamic Pricing Intelligence System | "
    "Machine Learning • Data Analytics • Streamlit"
)
