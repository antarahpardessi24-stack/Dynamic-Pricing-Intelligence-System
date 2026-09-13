import streamlit as st
import pandas as pd
import joblib
import re


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Dynamic Pricing Intelligence",
    page_icon="🤖",
    layout="centered"
)


# =========================================================
# 2. FILE PATHS
# =========================================================

DATA_PATH = "pricing_data_processed.csv"
MODEL_PATH = "best_pricing_model.pkl"
FEATURES_PATH = "model_features.pkl"


# =========================================================
# 3. LOAD DATA AND MODEL
# =========================================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


@st.cache_resource
def load_model():
    model = joblib.load(MODEL_PATH)
    features = joblib.load(FEATURES_PATH)
    return model, features


pricing_df = load_data()
pricing_model, model_features = load_model()


# =========================================================
# 4. TITLE
# =========================================================

st.title("🤖 Dynamic Pricing Intelligence Assistant")

st.write(
    "Ask questions about sales, customers, promotions, "
    "store performance, predictions and pricing."
)


# =========================================================
# 5. HELPER FUNCTIONS
# =========================================================

def get_store_data(store_number):

    return pricing_df[
        pricing_df["Store"] == store_number
    ]


def get_store_summary(store_number):

    data = get_store_data(store_number)

    if data.empty:
        return None

    return {
        "total_sales": data["Sales"].sum(),
        "average_sales": data["Sales"].mean(),
        "total_customers": data["Customers"].sum(),
        "average_customers": data["Customers"].mean(),
        "maximum_customers": data["Customers"].max(),
        "records": len(data)
    }


def predict_store_sales(store_number):

    data = get_store_data(store_number)

    if data.empty:
        return None

    input_data = data.iloc[[0]].copy()

    input_data = input_data.drop(
        columns=["Sales", "Date"]
    )

    input_data = input_data[model_features]

    prediction = pricing_model.predict(
        input_data
    )[0]

    return prediction


def get_promotion_insight():

    promo_sales = pricing_df[
        pricing_df["Promo"] == 1
    ]["Sales"].mean()

    non_promo_sales = pricing_df[
        pricing_df["Promo"] == 0
    ]["Sales"].mean()

    difference = promo_sales - non_promo_sales

    percentage = (
        difference / non_promo_sales
    ) * 100

    return promo_sales, non_promo_sales, percentage


def get_best_store():

    store_sales = pricing_df.groupby(
        "Store"
    )["Sales"].sum()

    best_store = store_sales.idxmax()

    best_sales = store_sales.max()

    return best_store, best_sales


def get_pricing_recommendation(
    store_number,
    current_price
):

    data = get_store_data(store_number)

    if data.empty:
        return None

    input_data = data.iloc[[0]].copy()

    input_data = input_data.drop(
        columns=["Sales", "Date"]
    )

    input_data = input_data[model_features]

    base_prediction = pricing_model.predict(
        input_data
    )[0]

    scenarios = {
        "10% Lower": current_price * 0.90,
        "Current Price": current_price,
        "10% Higher": current_price * 1.10
    }

    results = []

    for scenario, price in scenarios.items():

        if scenario == "10% Lower":
            demand_factor = 1.05

        elif scenario == "10% Higher":
            demand_factor = 0.95

        else:
            demand_factor = 1.00

        predicted_demand = (
            base_prediction * demand_factor
        )

        simulated_revenue = (
            price * predicted_demand
        )

        results.append({
            "Scenario": scenario,
            "Price": price,
            "Demand": predicted_demand,
            "Revenue": simulated_revenue
        })

    result_df = pd.DataFrame(results)

    return result_df.loc[
        result_df["Revenue"].idxmax()
    ]


# =========================================================
# 6. USER QUESTION
# =========================================================

question = st.text_input(
    "💬 Ask your question:",
    placeholder="Example: What are the sales of Store 10?"
)


# =========================================================
# 7. CHATBOT LOGIC
# =========================================================

if question:

    q = question.lower().strip()

    # Extract store number
    store_match = re.search(
        r"store\s*(\d+)",
        q
    )

    if store_match:
        store_number = int(
            store_match.group(1)
        )
    else:
        store_number = None


    # =====================================================
    # GREETING
    # =====================================================

    if q in [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]:

        st.success(
            "Hello! 👋 I am your Dynamic Pricing "
            "Intelligence Assistant."
        )

        st.write(
            "I can help you analyze sales, customers, "
            "promotions, store performance, ML predictions "
            "and pricing recommendations."
        )


    # =====================================================
    # HELP
    # =====================================================

    elif q in [
        "help",
        "what can you do"
    ]:

        st.subheader("💡 Example Questions")

        questions = [
            "What are the sales of Store 10?",
            "What are the average sales?",
            "How many customers did Store 10 have?",
            "Give me a summary of Store 10",
            "Which store has the highest sales?",
            "Do promotions increase sales?",
            "Predict sales for Store 10",
            "Recommend a price for Store 10 at ₹100"
        ]

        for item in questions:
            st.write(f"• {item}")


    # =====================================================
    # AVERAGE SALES
    # =====================================================

    elif (
        "average sales" in q
        or "mean sales" in q
        or "typical sales" in q
        or "average of sales" in q
    ):

        average_sales = pricing_df[
            "Sales"
        ].mean()

        st.subheader("📊 Average Sales")

        st.write(
            f"**Average Daily Sales:** "
            f"₹{average_sales:,.2f}"
        )


    # =====================================================
    # BEST STORE
    # =====================================================

    elif (
        "highest sales" in q
        or "best store" in q
        or "best performing store" in q
        or "best performing" in q
        or "top performing store" in q
        or "top performing" in q
        or "performs best" in q
        or "most successful store" in q
    ):

        best_store, best_sales = get_best_store()

        st.subheader("🏆 Best Performing Store")

        st.write(
            f"**Store:** {best_store}"
        )

        st.write(
            f"**Total Sales:** "
            f"₹{best_sales:,.0f}"
        )


    # =====================================================
    # PROMOTION ANALYSIS
    # =====================================================

    elif (
        "promotion" in q
        or "promotions" in q
        or "promo" in q
    ):

        promo, non_promo, percentage = (
            get_promotion_insight()
        )

        st.subheader("📈 Promotion Analysis")

        st.write(
            f"**Average Sales During Promotions:** "
            f"₹{promo:,.2f}"
        )

        st.write(
            f"**Average Sales Without Promotions:** "
            f"₹{non_promo:,.2f}"
        )

        st.write(
            f"**Difference:** "
            f"{percentage:.2f}%"
        )

        if percentage > 0:

            st.success(
                f"Sales are {percentage:.2f}% higher "
                "on average during promotion days."
            )


    # =====================================================
    # PRICE RECOMMENDATION
    # =====================================================

    elif (
        "price" in q
        and (
            "recommend" in q
            or "recommended" in q
            or "best" in q
            or "suggest" in q
            or "optimal" in q
            or "ideal" in q
        )
    ):

        if store_number is None:

            st.warning(
                "Please specify a store number."
            )

        else:

            price_match = re.search(
                r"(?:at|price)\s*"
                r"(?:₹|rs\.?|inr|\$)?\s*"
                r"(\d+(?:\.\d+)?)",
                q,
                re.IGNORECASE
            )

            if price_match is None:

                st.warning(
                    "Please provide the current price."
                )

            else:

                current_price = float(
                    price_match.group(1)
                )

                result = get_pricing_recommendation(
                    store_number,
                    current_price
                )

                if result is None:

                    st.error(
                        "Store not found."
                    )

                else:

                    st.subheader(
                        "💰 Pricing Recommendation"
                    )

                    st.write(
                        f"**Current Price:** "
                        f"₹{current_price:,.2f}"
                    )

                    st.write(
                        f"**Recommended Price:** "
                        f"₹{result['Price']:,.2f}"
                    )

                    st.write(
                        f"**Scenario:** "
                        f"{result['Scenario']}"
                    )

                    st.write(
                        f"**Predicted Demand:** "
                        f"{result['Demand']:,.2f}"
                    )

                    st.write(
                        f"**Simulated Revenue:** "
                        f"₹{result['Revenue']:,.2f}"
                    )

                    st.caption(
                        "Note: Pricing scenarios are simulated "
                        "because the dataset does not contain "
                        "historical product prices."
                    )


    # =====================================================
    # ML SALES PREDICTION
    # =====================================================

    elif (
        "predict" in q
        or "forecast" in q
        or "expected sales" in q
        or "sales prediction" in q
        or "sales forecast" in q
        or "estimate sales" in q
    ):

        if store_number is None:

            st.warning(
                "Please specify a store number."
            )

        else:

            prediction = predict_store_sales(
                store_number
            )

            if prediction is None:

                st.error(
                    "Store not found."
                )

            else:

                st.subheader(
                    "🔮 ML Sales Prediction"
                )

                st.write(
                    f"**Store:** {store_number}"
                )

                st.write(
                    f"**Predicted Sales:** "
                    f"₹{prediction:,.2f}"
                )


    # =====================================================
    # STORE SUMMARY
    # =====================================================

    elif (
        store_number is not None
        and (
            "summary" in q
            or "insight" in q
        )
    ):

        data = get_store_summary(
            store_number
        )

        if data is None:

            st.error(
                "Store not found."
            )

        else:

            st.subheader(
                f"🏪 Store {store_number} Summary"
            )

            st.write(
                f"**Total Sales:** "
                f"₹{data['total_sales']:,.0f}"
            )

            st.write(
                f"**Average Daily Sales:** "
                f"₹{data['average_sales']:,.2f}"
            )

            st.write(
                f"**Total Customers:** "
                f"{data['total_customers']:,.0f}"
            )

            st.write(
                f"**Average Daily Customers:** "
                f"{data['average_customers']:,.2f}"
            )

            st.write(
                f"**Records:** "
                f"{data['records']:,}"
            )


    # =====================================================
    # STORE CUSTOMERS
    # =====================================================

    elif (
        store_number is not None
        and (
            "customer" in q
            or "customers" in q
        )
    ):

        data = get_store_summary(
            store_number
        )

        if data is None:

            st.error(
                "Store not found."
            )

        else:

            st.subheader(
                f"👥 Store {store_number} Customers"
            )

            st.write(
                f"**Total Customers:** "
                f"{data['total_customers']:,.0f}"
            )

            st.write(
                f"**Average Daily Customers:** "
                f"{data['average_customers']:,.2f}"
            )


    # =====================================================
    # STORE SALES
    # =====================================================

    elif (
        store_number is not None
        and "sales" in q
    ):

        data = get_store_summary(
            store_number
        )

        if data is None:

            st.error(
                "Store not found."
            )

        else:

            st.subheader(
                f"📊 Store {store_number} Sales"
            )

            st.write(
                f"**Total Sales:** "
                f"₹{data['total_sales']:,.0f}"
            )

            st.write(
                f"**Average Daily Sales:** "
                f"₹{data['average_sales']:,.2f}"
            )


    # =====================================================
    # UNKNOWN QUESTION
    # =====================================================

    else:

        st.info(
            "🤔 I don't understand that question yet."
        )

        st.write("Try asking:")

        st.write(
            "• What are the sales of Store 10?"
        )

        st.write(
            "• What are the average sales?"
        )

        st.write(
            "• How many customers did Store 10 have?"
        )

        st.write(
            "• Give me a summary of Store 10"
        )

        st.write(
            "• Which store has the highest sales?"
        )

        st.write(
            "• Do promotions increase sales?"
        )

        st.write(
            "• Predict sales for Store 10"
        )

        st.write(
            "• Recommend a price for Store 10 at ₹100"
        )