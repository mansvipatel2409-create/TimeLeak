import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ============================================================
# TimeLeak - Human Time Waste Intelligence Dashboard
# Python-only Streamlit dashboard
# ============================================================

st.set_page_config(
    page_title="TimeLeak",
    page_icon="⏳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Course-specific keywords
# -----------------------------
COURSE_KEYWORDS = {
    "IT": [
        "python", "java", "javascript", "coding", "programming", "database",
        "sql", "html", "css", "react", "node", "algorithm", "data structure",
        "cybersecurity", "machine learning", "ai", "web development",
        "software", "computer", "tutorial", "course", "exam", "study",
        "scholarship", "facts"
    ],
    "Mechanical": [
        "thermodynamics", "mechanics", "cad", "solidworks", "autocad",
        "machine design", "manufacturing", "fluid mechanics", "automobile",
        "engineering", "tutorial", "course", "exam", "study",
        "scholarship", "facts"
    ],
    "Commerce": [
        "accounting", "finance", "economics", "business", "marketing",
        "tax", "gst", "stock", "investment", "management", "commerce",
        "tutorial", "course", "exam", "study", "scholarship", "facts"
    ],
    "Medical": [
        "medicine", "anatomy", "physiology", "pharmacology", "pathology",
        "biology", "medical", "nursing", "clinical", "mbbs", "health",
        "tutorial", "course", "exam", "study", "scholarship", "facts"
    ],
}

PRODUCTIVE_KEYWORDS = [
    "scholarship", "exam", "study", "facts", "tutorial", "course",
    "lecture", "assignment", "project", "education", "learning",
    "research", "notes", "revision", "career", "internship", "job",
    "coding", "programming", "python", "java", "sql", "database",
    "algorithm", "machine learning", "artificial intelligence",
    "cybersecurity", "finance", "accounting", "economics", "medicine",
    "anatomy", "thermodynamics", "mechanics", "cad"
]

WASTED_KEYWORDS = [
    "funny", "meme", "memes", "prank", "pranks", "gossip", "timepass",
    "time pass", "joke", "jokes", "comedy", "reels", "shorts",
    "celebrity gossip", "random chat", "fun video", "entertainment",
    "roast", "viral", "trend", "clickbait"
]

# App defaults are used only when no keyword matches.
APP_DEFAULTS = {
    "Snapchat": "Wasted",
    "Instagram": "Wasted",
    "TikTok": "Wasted",
    "YouTube": "Neutral",
    "LinkedIn": "Productive",
    "Google": "Productive",
    "Coursera": "Productive",
    "Udemy": "Productive",
    "GitHub": "Productive",
    "Khan Academy": "Productive",
    "WhatsApp": "Neutral",
    "Telegram": "Neutral",
    "Chrome": "Neutral",
}

# -----------------------------
# Demo data generator
# -----------------------------
def generate_demo_data(days=14, seed=42):
    random.seed(seed)

    apps = [
        "Instagram", "Snapchat", "YouTube", "LinkedIn",
        "WhatsApp", "Coursera", "GitHub", "Google", "Chrome"
    ]

    titles = [
        "Python tutorial for beginners",
        "GTU exam preparation",
        "Scholarship application guide",
        "Machine learning course",
        "Funny memes compilation",
        "Best prank videos",
        "Celebrity gossip",
        "Random timepass chat",
        "Coding interview questions",
        "Study facts for students",
        "College assignment tutorial",
        "Trending reels",
        "Career opportunities for students",
        "Web development tutorial",
        "Weekend comedy shorts",
    ]

    rows = []
    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for day in range(days):
        current_day = start - timedelta(days=days - 1 - day)
        # 10-18 usage records per day
        for _ in range(random.randint(10, 18)):
            hour = random.choices(
                range(7, 24),
                weights=[
                    2, 2, 3, 4, 5, 5, 4, 3, 3, 4, 5, 6, 7, 8, 7, 6, 5
                ],
                k=1,
            )[0]

            minute = random.randint(0, 59)
            timestamp = current_day + timedelta(hours=hour, minutes=minute)

            app = random.choice(apps)
            title = random.choice(titles)

            # Make app/title combinations reasonably realistic.
            if app in ["Coursera", "GitHub", "LinkedIn"]:
                title = random.choice([
                    "Python tutorial for beginners",
                    "Coding interview questions",
                    "Career opportunities for students",
                    "Web development tutorial",
                    "Machine learning course",
                ])
            elif app in ["Instagram", "Snapchat"]:
                title = random.choice([
                    "Funny memes compilation",
                    "Best prank videos",
                    "Celebrity gossip",
                    "Trending reels",
                    "Weekend comedy shorts",
                    "Random timepass chat",
                ])

            minutes = random.randint(3, 45)

            rows.append({
                "timestamp": timestamp,
                "app": app,
                "content title": title,
                "minutes": minutes,
            })

    return pd.DataFrame(rows)


# -----------------------------
# Classification engine
# -----------------------------
def classify_item(row, course):
    title = str(row["content title"]).lower()
    app = str(row["app"]).strip()

    course_words = [word.lower() for word in COURSE_KEYWORDS[course]]

    matched_productive = []
    matched_wasted = []

    for keyword in PRODUCTIVE_KEYWORDS + course_words:
        if keyword in title:
            matched_productive.append(keyword)

    for keyword in WASTED_KEYWORDS:
        if keyword in title:
            matched_wasted.append(keyword)

    # Wasted keywords take priority if both somehow match.
    if matched_wasted:
        return "Wasted", f"Keyword match: {matched_wasted[0]}"

    if matched_productive:
        return "Productive", f"Keyword match: {matched_productive[0]}"

    # No keyword matched -> use app default.
    default_label = APP_DEFAULTS.get(app, "Neutral")
    return default_label, f"App default: {app} → {default_label}"


def prepare_data(df, course):
    required = {"timestamp", "app", "content title", "minutes"}

    # Make column names predictable.
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(sorted(missing))
        )

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["minutes"] = pd.to_numeric(df["minutes"], errors="coerce")

    df = df.dropna(subset=["timestamp", "app", "content title", "minutes"])
    df = df[df["minutes"] > 0].copy()

    classifications = df.apply(
        lambda row: classify_item(row, course), axis=1
    )

    df["classification"] = classifications.apply(lambda x: x[0])
    df["classification_reason"] = classifications.apply(lambda x: x[1])

    df["date"] = df["timestamp"].dt.date
    df["weekday"] = df["timestamp"].dt.day_name()
    df["hour"] = df["timestamp"].dt.hour

    return df.sort_values("timestamp")


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("⏳ TimeLeak")
st.sidebar.caption("Human Time Waste Intelligence Dashboard")

course = st.sidebar.selectbox(
    "Select your course",
    ["IT", "Mechanical", "Commerce", "Medical"],
)

st.sidebar.divider()

data_source = st.sidebar.radio(
    "Phone usage data",
    ["Generate Demo Data", "Upload CSV"],
)

if data_source == "Generate Demo Data":
    demo_days = st.sidebar.slider("Demo data days", 3, 30, 14)
    daily_limit = st.sidebar.number_input(
        "Daily usage limit (minutes)",
        min_value=30,
        max_value=1440,
        value=240,
        step=15,
    )
    raw_df = generate_demo_data(days=demo_days)
else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV",
        type=["csv"],
        help="Required columns: timestamp, app, content title, minutes",
    )
    daily_limit = st.sidebar.number_input(
        "Daily usage limit (minutes)",
        min_value=30,
        max_value=1440,
        value=240,
        step=15,
    )

    if uploaded_file is not None:
        raw_df = pd.read_csv(uploaded_file)
    else:
        st.info(
            "Upload a CSV file from the sidebar, or select "
            "'Generate Demo Data' to explore TimeLeak."
        )
        st.stop()

try:
    df = prepare_data(raw_df, course)
except ValueError as error:
    st.error(str(error))
    st.stop()

if df.empty:
    st.warning("No valid usage records found.")
    st.stop()

# -----------------------------
# KPI calculations
# -----------------------------
total_time = df["minutes"].sum()
productive_time = df.loc[df["classification"] == "Productive", "minutes"].sum()
wasted_time = df.loc[df["classification"] == "Wasted", "minutes"].sum()
neutral_time = df.loc[df["classification"] == "Neutral", "minutes"].sum()

productivity_score = (
    productive_time / total_time * 100 if total_time > 0 else 0
)

waste_percentage = (
    wasted_time / total_time * 100 if total_time > 0 else 0
)

# -----------------------------
# Header
# -----------------------------
st.title("⏳ TimeLeak")
st.markdown(
    f"### Human Time Waste Intelligence Dashboard — **{course}**"
)
st.caption(
    "Rule-based analysis of phone usage to identify productive time, "
    "wasted time, and neutral usage."
)

# -----------------------------
# KPI cards
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Time", f"{total_time:,.0f} min")
c2.metric("Productive Time", f"{productive_time:,.0f} min")
c3.metric("Wasted Time", f"{wasted_time:,.0f} min")
c4.metric("Productivity Score", f"{productivity_score:.1f}%")

st.divider()

# -----------------------------
# Daily limit alert
# -----------------------------
daily_usage = (
    df.groupby("date", as_index=False)["minutes"]
    .sum()
    .rename(columns={"minutes": "daily_minutes"})
)

days_over_limit = daily_usage[daily_usage["daily_minutes"] > daily_limit]

if len(days_over_limit) > 0:
    st.warning(
        f"⚠️ Daily limit alert: usage exceeded your "
        f"{daily_limit}-minute limit on **{len(days_over_limit)} day(s)**."
    )
else:
    st.success(
        f"✅ Great! Daily phone usage stayed within the "
        f"{daily_limit}-minute limit for all recorded days."
    )

# -----------------------------
# Auto-generated insights
# -----------------------------
st.subheader("💡 TimeLeak Insights")

app_waste = (
    df[df["classification"] == "Wasted"]
    .groupby("app")["minutes"]
    .sum()
    .sort_values(ascending=False)
)

top_waste_app = app_waste.index[0] if not app_waste.empty else "None"
top_waste_minutes = app_waste.iloc[0] if not app_waste.empty else 0

hour_waste = (
    df[df["classification"] == "Wasted"]
    .groupby("hour")["minutes"]
    .sum()
)

peak_hour = int(hour_waste.idxmax()) if not hour_waste.empty else 0
peak_hour_minutes = hour_waste.max() if not hour_waste.empty else 0

saved_hours = wasted_time * 0.30 / 60

i1, i2, i3 = st.columns(3)

i1.info(
    f"**Top time-leak app**\n\n"
    f"{top_waste_app} — {top_waste_minutes:.0f} minutes wasted"
)

i2.info(
    f"**Peak waste hour**\n\n"
    f"{peak_hour:02d}:00–{(peak_hour + 1) % 24:02d}:00 — "
    f"{peak_hour_minutes:.0f} minutes wasted"
)

i3.info(
    f"**30% waste reduction**\n\n"
    f"You could save approximately **{saved_hours:.1f} hours**."
)

# -----------------------------
# Charts
# -----------------------------
st.subheader("📊 Usage Overview")

chart1, chart2 = st.columns(2)

# Pie chart
category_totals = pd.DataFrame({
    "Category": ["Productive", "Wasted", "Neutral"],
    "Minutes": [productive_time, wasted_time, neutral_time],
})

fig_pie = px.pie(
    category_totals,
    names="Category",
    values="Minutes",
    title="Time Distribution",
    hole=0.45,
)
fig_pie.update_layout(legend_title_text="Classification")
chart1.plotly_chart(fig_pie, use_container_width=True)

# App-wise bar chart
app_totals = (
    df.groupby(["app", "classification"], as_index=False)["minutes"]
    .sum()
)

fig_app = px.bar(
    app_totals,
    x="app",
    y="minutes",
    color="classification",
    barmode="stack",
    title="App-wise Time Usage",
    labels={"minutes": "Minutes", "app": "App"},
)
fig_app.update_xaxes(tickangle=-35)
chart2.plotly_chart(fig_app, use_container_width=True)

# -----------------------------
# Daily trend
# -----------------------------
daily_category = (
    df.groupby(["date", "classification"], as_index=False)["minutes"]
    .sum()
)

fig_daily = px.line(
    daily_category,
    x="date",
    y="minutes",
    color="classification",
    markers=True,
    title="Daily Time Trend",
    labels={"date": "Date", "minutes": "Minutes"},
)
st.plotly_chart(fig_daily, use_container_width=True)

# -----------------------------
# Weekday x hour heatmap
# -----------------------------
st.subheader("🔥 Wasted Time Heatmap")

weekday_order = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]

wasted = df[df["classification"] == "Wasted"].copy()

if not wasted.empty:
    heatmap = (
        wasted.groupby(["weekday", "hour"])["minutes"]
        .sum()
        .reset_index()
    )

    heatmap_pivot = (
        heatmap.pivot(index="weekday", columns="hour", values="minutes")
        .reindex(weekday_order)
        .fillna(0)
    )

    # Make sure every hour 0-23 is represented.
    heatmap_pivot = heatmap_pivot.reindex(
        columns=range(24), fill_value=0
    )

    fig_heat = go.Figure(
        data=go.Heatmap(
            z=heatmap_pivot.values,
            x=[f"{h:02d}:00" for h in range(24)],
            y=heatmap_pivot.index,
            hovertemplate=(
                "Day: %{y}<br>"
                "Hour: %{x}<br>"
                "Wasted: %{z:.0f} min"
                "<extra></extra>"
            ),
            colorbar_title="Minutes",
        )
    )

    fig_heat.update_layout(
        title="Wasted Time by Weekday and Hour",
        xaxis_title="Hour",
        yaxis_title="Weekday",
    )

    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("No wasted-time records are available for the heatmap.")

# -----------------------------
# Classification details
# -----------------------------
with st.expander("🔎 Show how each item was classified"):
    display_df = df[
        [
            "timestamp",
            "app",
            "content title",
            "minutes",
            "classification",
            "classification_reason",
        ]
    ].copy()

    display_df.columns = [
        "Timestamp",
        "App",
        "Content Title",
        "Minutes",
        "Classification",
        "Why?",
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

# -----------------------------
# CSV export
# -----------------------------
st.divider()

st.subheader("⬇️ Export Analysis")

csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Classified CSV",
    data=csv_data,
    file_name="timeleak_classified_usage.csv",
    mime="text/csv",
)

st.caption(
    "TimeLeak uses a transparent rule-based classifier. "
    "Keyword matches are checked first; if there is no match, "
    "the configured app default is used."
)
