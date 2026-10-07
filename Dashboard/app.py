import io
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ---------- Page setup ----------
st.set_page_config(page_title="Electronics Sales Dashboard", page_icon="📊", layout="wide")

# Change this path if your CSV is somewhere else
DATA_PATH = Path(__file__).parent / "Electronic_sales_Sep2023-Sep2024.csv"

AGE_LABELS = ["Young Adult (18-29)", "Adult (30-44)", "Middle-aged (45-59)", "Senior (60+)"]

# One consistent colour palette for the whole dashboard
PALETTE = ["#6C63FF", "#00C2A8", "#FF8A5B", "#FFC857", "#E85D75"]


# ---------- Theme helpers (charts follow Streamlit's light/dark theme) ----------
def current_theme():
    try:
        theme_type = st.context.theme.type
        if theme_type in ("light", "dark"):
            return theme_type
    except Exception:
        pass
    base = st.get_option("theme.base")
    return base if base in ("light", "dark") else "light"


THEME = current_theme()
TEXT_COLOR = "#E8E8F0" if THEME == "dark" else "#2B2D42"
GRID_COLOR = "#3A3F55" if THEME == "dark" else "#E3E6F0"

sns.set_theme(
    style="whitegrid",
    rc={
        "text.color": TEXT_COLOR,
        "axes.labelcolor": TEXT_COLOR,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
        "axes.edgecolor": GRID_COLOR,
        "grid.color": GRID_COLOR,
        "axes.facecolor": "none",
        "figure.facecolor": "none",
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlepad": 12,
        "font.size": 10,
    },
)

# ---------- Custom CSS ----------
st.markdown(
    """
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
footer {visibility: hidden;}
.hero {background: linear-gradient(120deg, #6C63FF 0%, #00C2A8 100%); padding: 1.6rem 2rem; border-radius: 18px; margin-bottom: 1.2rem; box-shadow: 0 8px 24px rgba(108, 99, 255, 0.25);}
.hero h1 {margin: 0; font-size: 2rem; color: white !important; padding: 0;}
.hero p {margin: 0.3rem 0 0 0; color: white; opacity: 0.92;}
.kpi {border-radius: 16px; padding: 1rem 1.2rem; color: white; box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);}
.kpi .label {font-size: 0.85rem; opacity: 0.92; letter-spacing: 0.3px;}
.kpi .value {font-size: 1.8rem; font-weight: 700; margin-top: 0.2rem;}
.stTabs [data-baseweb="tab"] {font-size: 1rem; font-weight: 600;}
span[data-baseweb="tag"] {background-color: #6C63FF !important;}
</style>
""",
    unsafe_allow_html=True,
)


# ---------- Load + clean data (same steps as the notebook) ----------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["Purchase Date"] = pd.to_datetime(df["Purchase Date"])
    df["Payment Method"] = df["Payment Method"].replace({"Paypal": "PayPal"})
    df["Gender"] = df["Gender"].fillna("Unknown")
    df["Add-ons Purchased"] = df["Add-ons Purchased"].fillna("None")
    df["Product"] = df["Product Type"] + " (" + df["SKU"] + ")"
    df["Age Group"] = pd.cut(df["Age"], bins=[17, 29, 44, 59, 80], labels=AGE_LABELS)
    df["Year-Month"] = df["Purchase Date"].dt.to_period("M").astype(str)
    return df


# ---------- Small helpers ----------
def kpi_card(column, icon, label, value, color_from, color_to):
    column.markdown(
        f'<div class="kpi" style="background: linear-gradient(135deg, {color_from}, {color_to});">'
        f'<div class="label">{icon} {label}</div><div class="value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def draw_bars(ax, labels, values, colors, fmt, horizontal=False):
    labels = [str(label) for label in labels]
    if horizontal:
        bars = ax.barh(labels, values, color=colors)
        ax.invert_yaxis()
        ax.grid(axis="y", visible=False)
    else:
        bars = ax.bar(labels, values, color=colors)
        ax.grid(axis="x", visible=False)
    ax.bar_label(bars, fmt=fmt, padding=3, color=TEXT_COLOR, fontsize=9)
    sns.despine(ax=ax, left=True)


def show(fig):
    # Save as a transparent PNG so the chart blends with light and dark themes
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", transparent=True, dpi=200, bbox_inches="tight")
    st.image(buffer)
    plt.close(fig)


df = load_data(DATA_PATH)

# ---------- Sidebar filters ----------
st.sidebar.markdown("## 🎛️ Filters")

min_date = df["Purchase Date"].min().date()
max_date = df["Purchase Date"].max().date()
date_range = st.sidebar.date_input(
    "Purchase date", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
if len(date_range) != 2:
    st.info("Select both a start and an end date in the sidebar.")
    st.stop()

all_types = sorted(df["Product Type"].unique())
all_genders = sorted(df["Gender"].unique())
selected_types = st.sidebar.multiselect("Product Type", all_types, default=all_types)
selected_genders = st.sidebar.multiselect("Gender", all_genders, default=all_genders)
st.sidebar.caption("Tip: switch Light/Dark from the ⋮ menu (top right) → Settings.")

filtered = df[
    (df["Purchase Date"] >= pd.Timestamp(date_range[0]))
    & (df["Purchase Date"] <= pd.Timestamp(date_range[1]))
    & (df["Product Type"].isin(selected_types))
    & (df["Gender"].isin(selected_genders))
]
completed = filtered[filtered["Order Status"] == "Completed"]

# ---------- Hero banner ----------
st.markdown(
    '<div class="hero"><h1>📊 Electronics Retail Sales Dashboard</h1>'
    "<p>Completed orders drive all revenue figures · Cancelled orders are analysed separately · "
    f"{len(filtered):,} orders in current selection</p></div>",
    unsafe_allow_html=True,
)

if completed.empty:
    st.warning("No completed orders match the current filters.")
    st.stop()

# ---------- KPI cards ----------
cancel_rate = (filtered["Order Status"] == "Cancelled").mean() * 100

c1, c2, c3, c4, c5 = st.columns(5)
kpi_card(c1, "💰", "Revenue", f"{completed['Total Price'].sum() / 1_000_000:.2f}M", "#6C63FF", "#8E7DFF")
kpi_card(c2, "🧾", "Completed orders", f"{len(completed):,}", "#00A896", "#02C39A")
kpi_card(c3, "🛒", "Avg order value", f"{completed['Total Price'].mean():,.0f}", "#FF8A5B", "#FFB45B")
kpi_card(c4, "👥", "Unique customers", f"{completed['Customer ID'].nunique():,}", "#3A86FF", "#5FA8FF")
kpi_card(c5, "❌", "Cancellation rate", f"{cancel_rate:.1f}%", "#E85D75", "#FF8FA3")

st.write("")

# ---------- Tabs ----------
tab_time, tab_customers, tab_products, tab_cancel = st.tabs(
    ["📈 Sales Trend", "👥 Customers", "📦 Products", "❌ Cancellations"]
)

# ----- Sales trend -----
with tab_time:
    st.subheader("Monthly revenue")
    monthly = completed.groupby("Year-Month")["Total Price"].sum() / 1_000_000
    positions = list(range(len(monthly)))
    dataset_edges = {df["Year-Month"].min(), df["Year-Month"].max()}
    partial_positions = [i for i, month in enumerate(monthly.index) if month in dataset_edges]

    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(positions, monthly.values, marker="o", color=PALETTE[0], linewidth=2.5)
    ax.fill_between(positions, monthly.values, alpha=0.15, color=PALETTE[0])
    if partial_positions:
        ax.scatter(
            partial_positions,
            monthly.values[partial_positions],
            color=PALETTE[2],
            s=80,
            zorder=5,
            label="Partial month",
        )
        ax.legend(frameon=False)
    ax.set_xticks(positions)
    ax.set_xticklabels(monthly.index, rotation=45, ha="right")
    ax.set_title("Monthly Revenue (Completed Orders)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (millions)")
    ax.grid(axis="x", visible=False)
    sns.despine(ax=ax, left=True)
    show(fig)
    st.caption(
        "The first and last months of the dataset are partial "
        "(data runs from 24 Sep 2023 to 23 Sep 2024), so they look lower."
    )

    st.subheader("Monthly orders and average order value")
    monthly_table = completed.groupby("Year-Month").agg(
        revenue=("Total Price", "sum"),
        orders=("Total Price", "count"),
        avg_order_value=("Total Price", "mean"),
    ).round(2)
    st.dataframe(monthly_table)

# ----- Customers -----
with tab_customers:
    left, right = st.columns(2)

    with left:
        st.subheader("Age groups")
        age_summary = completed.groupby("Age Group", observed=True).agg(
            orders=("Total Price", "count"),
            avg_order_value=("Total Price", "mean"),
        )
        age_metric = st.radio("Show", ["orders", "avg_order_value"], horizontal=True, key="age_metric")
        age_title = age_metric.replace("_", " ").title()

        fig, ax = plt.subplots(figsize=(6, 4.2))
        draw_bars(
            ax,
            age_summary.index,
            age_summary[age_metric],
            PALETTE[: len(age_summary)],
            "%d" if age_metric == "orders" else "%.0f",
        )
        ax.set_title(f"{age_title} by Age Group")
        ax.set_xlabel("Age Group")
        ax.set_ylabel(age_title)
        ax.tick_params(axis="x", rotation=20)
        show(fig)

    with right:
        st.subheader("Gender")
        gender_summary = completed.groupby("Gender").agg(
            orders=("Total Price", "count"),
            avg_order_value=("Total Price", "mean"),
        )
        gender_metric = st.radio("Show", ["orders", "avg_order_value"], horizontal=True, key="gender_metric")
        gender_title = gender_metric.replace("_", " ").title()

        fig, ax = plt.subplots(figsize=(6, 4.2))
        draw_bars(
            ax,
            gender_summary.index,
            gender_summary[gender_metric],
            [PALETTE[1], PALETTE[0], PALETTE[3]][: len(gender_summary)],
            "%d" if gender_metric == "orders" else "%.0f",
        )
        ax.set_title(f"{gender_title} by Gender")
        ax.set_xlabel("Gender")
        ax.set_ylabel(gender_title)
        show(fig)

# ----- Products -----
with tab_products:
    left, right = st.columns(2)

    product_summary = completed.groupby("Product").agg(
        units_sold=("Quantity", "sum"),
        revenue=("Total Price", "sum"),
    )

    with left:
        st.subheader("Top products")
        product_metric = st.radio("Rank by", ["revenue", "units_sold"], horizontal=True, key="product_metric")
        max_n = min(10, len(product_summary))
        if max_n > 3:
            top_n = st.slider("How many products", 3, max_n, max_n)
        else:
            top_n = max_n
        top_products = product_summary.sort_values(product_metric, ascending=False).head(top_n)

        is_revenue = product_metric == "revenue"
        values = top_products[product_metric] / (1_000_000 if is_revenue else 1)

        fig, ax = plt.subplots(figsize=(6, 5))
        draw_bars(
            ax,
            top_products.index,
            values,
            [PALETTE[0]] * len(top_products),
            "%.2f" if is_revenue else "%d",
            horizontal=True,
        )
        ax.set_title(f"Top {top_n} Products by {product_metric.replace('_', ' ').title()}")
        ax.set_xlabel("Revenue (millions)" if is_revenue else "Units Sold")
        ax.set_ylabel("Product")
        show(fig)

    with right:
        st.subheader("Revenue by Product Type")
        category_summary = (
            completed.groupby("Product Type")["Total Price"].sum().sort_values(ascending=False) / 1_000_000
        )
        fig, ax = plt.subplots(figsize=(6, 5))
        draw_bars(
            ax,
            category_summary.index,
            category_summary.values,
            PALETTE[: len(category_summary)],
            "%.2f",
        )
        ax.set_title("Revenue by Product Type (Completed Orders)")
        ax.set_xlabel("Product Type")
        ax.set_ylabel("Revenue (millions)")
        ax.tick_params(axis="x", rotation=20)
        show(fig)

# ----- Cancellations -----
with tab_cancel:
    st.subheader("Cancellation rate")
    group_col = st.selectbox("Break down by", ["Product Type", "Payment Method", "Shipping Type", "Age Group"])

    rate = (
        filtered.assign(cancelled=(filtered["Order Status"] == "Cancelled"))
        .groupby(group_col, observed=True)["cancelled"]
        .mean()
        * 100
    ).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 4.2))
    draw_bars(ax, rate.index, rate.values, [PALETTE[4]] * len(rate), "%.1f%%")
    ax.axhline(cancel_rate, color=TEXT_COLOR, linestyle="--", linewidth=1.2, label="Overall rate")
    ax.set_title(f"Cancellation Rate by {group_col}")
    ax.set_xlabel(group_col)
    ax.set_ylabel("Cancellation Rate (%)")
    ax.tick_params(axis="x", rotation=20)
    ax.legend(frameon=False)
    show(fig)
    st.caption("The axis starts at 0 on purpose: small differences should look small.")

st.divider()
st.caption("Data: Electronic Sales Sep 2023 - Sep 2024 (synthetic, Kaggle) · Built with Python, pandas, seaborn and Streamlit.")