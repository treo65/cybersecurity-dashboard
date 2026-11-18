import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cybersecurity Threat Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark professional theme ───────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .block-container { padding-top: 1.5rem; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    [data-testid="stSidebar"] .stMarkdown h2 { color: #58a6ff; }

    .kpi-card {
        background: linear-gradient(135deg, #1f2937, #111827);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        margin-bottom: 8px;
    }
    .kpi-label { font-size: 12px; color: #8b949e; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 6px; }
    .kpi-value { font-size: 38px; font-weight: 700; }
    .kpi-high   { color: #f85149; }
    .kpi-medium { color: #f0883e; }
    .kpi-low    { color: #3fb950; }
    .kpi-total  { color: #58a6ff; }

    h2, h3 { color: #58a6ff !important; }
    .stTextInput input { background-color: #161b22; color: #e0e0e0; border: 1px solid #30363d; border-radius: 6px; }
    .stDownloadButton button {
        background-color: #238636; color: white; border: none;
        border-radius: 6px; padding: 8px 20px; font-weight: 600;
    }
    .stDownloadButton button:hover { background-color: #2ea043; }
    div[data-testid="metric-container"] { background-color: #161b22; border-radius: 8px; padding: 10px; }
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("cybersecurity_threats.csv")
    df["Date_first_widely_reported"] = pd.to_datetime(df["Date_first_widely_reported"])
    df["Year"] = df["Date_first_widely_reported"].dt.year
    return df

df = load_data()

RISK_COLORS = {"High": "#f85149", "Medium": "#f0883e", "Low": "#3fb950"}
RISK_ORDER   = ["High", "Medium", "Low"]


# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ Filters")
    st.markdown("---")

    selected_risk = st.multiselect(
        "Risk Level",
        options=RISK_ORDER,
        default=RISK_ORDER,
    )
    selected_category = st.multiselect(
        "Threat Category",
        options=sorted(df["Threat_category"].unique()),
        default=sorted(df["Threat_category"].unique()),
    )
    year_min = int(df["Year"].min())
    year_max = int(df["Year"].max())
    year_range = st.slider("Year Range", min_value=year_min, max_value=year_max, value=(year_min, year_max))
    st.markdown("---")
    search_term = st.text_input("🔍 Search threat name", placeholder="e.g. Phishing")
    st.markdown("---")
    st.markdown(f"<small style='color:#8b949e'>Data: {year_min}–{year_max}</small>", unsafe_allow_html=True)


# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = df[
    df["Risk_level"].isin(selected_risk) &
    df["Threat_category"].isin(selected_category) &
    df["Year"].between(year_range[0], year_range[1])
]
if search_term:
    filtered = filtered[filtered["Threat_name"].str.contains(search_term, case=False, na=False)]


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🛡️ Cybersecurity Threat Intelligence Dashboard")
st.markdown(
    f"<span style='color:#8b949e'>Showing **{len(filtered)}** of **{len(df)}** threats &nbsp;|&nbsp; "
    f"Updated: {datetime.now().strftime('%d %b %Y')}</span>",
    unsafe_allow_html=True,
)
st.markdown("---")


# ── KPI Cards ─────────────────────────────────────────────────────────────────
total  = len(filtered)
high   = int((filtered["Risk_level"] == "High").sum())
medium = int((filtered["Risk_level"] == "Medium").sum())
low    = int((filtered["Risk_level"] == "Low").sum())
cats   = filtered["Threat_category"].nunique()

k1, k2, k3, k4, k5 = st.columns(5)
for col, label, value, css in [
    (k1, "Total Threats",  total,  "kpi-total"),
    (k2, "🔴 High Risk",   high,   "kpi-high"),
    (k3, "🟠 Medium Risk", medium, "kpi-medium"),
    (k4, "🟢 Low Risk",    low,    "kpi-low"),
    (k5, "Categories",     cats,   "kpi-total"),
]:
    col.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value {css}">{value}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ── Row 1: Risk bar + Category bar ────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown("### Threats by Risk Level")
    risk_counts = (
        filtered["Risk_level"].value_counts()
        .reindex(RISK_ORDER, fill_value=0).reset_index()
    )
    risk_counts.columns = ["Risk_level", "Count"]
    fig_risk = px.bar(
        risk_counts, x="Risk_level", y="Count", color="Risk_level",
        text="Count", color_discrete_map=RISK_COLORS,
        category_orders={"Risk_level": RISK_ORDER}, template="plotly_dark",
    )
    fig_risk.update_traces(textposition="outside", marker_line_width=0)
    fig_risk.update_layout(showlegend=False, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                           margin=dict(t=20, b=20), yaxis=dict(gridcolor="#21262d"))
    st.plotly_chart(fig_risk, use_container_width=True)

with c2:
    st.markdown("### Threats by Category")
    cat_counts = filtered["Threat_category"].value_counts().reset_index()
    cat_counts.columns = ["Threat_category", "Count"]
    fig_cat = px.bar(
        cat_counts, x="Threat_category", y="Count",
        color="Threat_category", text="Count", template="plotly_dark",
    )
    fig_cat.update_traces(textposition="outside", marker_line_width=0)
    fig_cat.update_layout(showlegend=False, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                          margin=dict(t=20, b=20), xaxis=dict(tickangle=-30),
                          yaxis=dict(gridcolor="#21262d"))
    st.plotly_chart(fig_cat, use_container_width=True)


# ── Row 2: Pie + Year trend ───────────────────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    st.markdown("### Risk Level Distribution")
    fig_pie = px.pie(
        risk_counts, names="Risk_level", values="Count",
        color="Risk_level", color_discrete_map=RISK_COLORS,
        hole=0.45, template="plotly_dark",
    )
    fig_pie.update_traces(textinfo="percent+label", pull=[0.05, 0.05, 0.05])
    fig_pie.update_layout(paper_bgcolor="#0e1117", margin=dict(t=20, b=20),
                          legend=dict(bgcolor="#0e1117"))
    st.plotly_chart(fig_pie, use_container_width=True)

with c4:
    st.markdown("### Threats Reported Per Year")
    year_counts = filtered.groupby("Year").size().reset_index(name="Count")
    fig_year = px.area(
        year_counts, x="Year", y="Count",
        template="plotly_dark", color_discrete_sequence=["#58a6ff"],
    )
    fig_year.update_traces(fill="tozeroy", line_width=2)
    fig_year.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                           margin=dict(t=20, b=20),
                           yaxis=dict(gridcolor="#21262d"), xaxis=dict(gridcolor="#21262d"))
    st.plotly_chart(fig_year, use_container_width=True)


# ── Timeline scatter ──────────────────────────────────────────────────────────
st.markdown("### Timeline — First Widely Reported Threats")
timeline_df = filtered.sort_values("Date_first_widely_reported")
fig_timeline = px.scatter(
    timeline_df,
    x="Date_first_widely_reported", y="Threat_name",
    color="Risk_level", symbol="Threat_category",
    hover_data=["Threat_category", "Common_impact", "Standard_mitigation"],
    color_discrete_map=RISK_COLORS, template="plotly_dark",
)
fig_timeline.update_traces(marker=dict(size=14, line=dict(width=1, color="#30363d")))
fig_timeline.update_layout(
    plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
    margin=dict(t=20, b=20),
    xaxis=dict(gridcolor="#21262d", title="Date First Reported"),
    yaxis=dict(gridcolor="#21262d", title=""),
    height=520, legend=dict(bgcolor="#0e1117"),
)
st.plotly_chart(fig_timeline, use_container_width=True)


# ── Heatmap: Category × Risk ──────────────────────────────────────────────────
st.markdown("### Category vs Risk Level Heatmap")
heatmap_data = (
    filtered.groupby(["Threat_category", "Risk_level"]).size()
    .unstack(fill_value=0).reindex(columns=RISK_ORDER, fill_value=0)
)
fig_heat = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns.tolist(),
    y=heatmap_data.index.tolist(),
    colorscale=[[0.0, "#0e1117"], [0.3, "#1f4068"], [0.6, "#f0883e"], [1.0, "#f85149"]],
    text=heatmap_data.values, texttemplate="%{text}", showscale=True,
))
fig_heat.update_layout(template="plotly_dark", paper_bgcolor="#0e1117",
                       plot_bgcolor="#0e1117", margin=dict(t=20, b=20), height=320)
st.plotly_chart(fig_heat, use_container_width=True)


# ── Data table ────────────────────────────────────────────────────────────────
st.markdown("### Full Dataset")
display_cols = ["Threat_name", "Threat_category", "Date_first_widely_reported",
                "Risk_level", "Common_impact", "Standard_mitigation"]
st.dataframe(filtered[display_cols].sort_values("Date_first_widely_reported"),
             use_container_width=True, height=380)


# ── Download ──────────────────────────────────────────────────────────────────
st.markdown("---")
csv_bytes = filtered[display_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️  Download Filtered Data as CSV",
    data=csv_bytes,
    file_name="filtered_cybersecurity_threats.csv",
    mime="text/csv",
)
st.markdown(
    "<br><center><small style='color:#30363d'>Cybersecurity Threat Intelligence Dashboard — Streamlit + Plotly</small></center>",
    unsafe_allow_html=True,
)
