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


# ============================================================
# DEMO AUTHENTICATION + ONBOARDING (NO DATABASE)
# Accounts exist only in this Streamlit browser session.
# This is for demonstration, NOT production authentication.
# ============================================================
import hashlib

if "demo_users" not in st.session_state:
    st.session_state.demo_users = {}
if "logged_in_email" not in st.session_state:
    st.session_state.logged_in_email = None
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "Welcome"
if "profiles" not in st.session_state:
    st.session_state.profiles = {}

def _password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def _logout():
    st.session_state.logged_in_email = None
    st.session_state.auth_page = "Welcome"
    st.rerun()

def _show_auth():
    st.title("⏳ TimeLeak")
    st.subheader("Understand your time. Improve your habits.")
    st.caption("Python-only demo: accounts are temporary and are not saved permanently.")

    left, right = st.columns([1, 1])
    with left:
        st.markdown("### Welcome to TimeLeak")
        st.write("Track productive, wasted and neutral time using demo data or a CSV file.")
        st.info("Without a database, demo accounts are stored only in the current app session. They may disappear when the session restarts.")
    with right:
        page = st.radio("Choose an option", ["Login", "Create account"], horizontal=True,
                        index=0 if st.session_state.auth_page == "Login" else 1 if st.session_state.auth_page == "Create account" else 0)
        st.session_state.auth_page = page

        if page == "Create account":
            with st.form("signup_form", clear_on_submit=False):
                name = st.text_input("Your name")
                email = st.text_input("Email address").strip().lower()
                password = st.text_input("Create password", type="password")
                confirm = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("Create account", use_container_width=True)
            if submitted:
                if not name.strip() or not email or "@" not in email:
                    st.error("Enter your name and a valid email address.")
                elif len(password) < 8:
                    st.error("Use a password with at least 8 characters.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif email in st.session_state.demo_users:
                    st.error("This email already has an account in this session. Please log in.")
                else:
                    st.session_state.demo_users[email] = {
                        "name": name.strip(),
                        "password_hash": _password_hash(password),
                    }
                    st.session_state.logged_in_email = email
                    st.session_state.profiles[email] = {"onboarding_complete": False}
                    st.success("Account created for this demo. Let's set up your profile.")
                    st.rerun()
        else:
            with st.form("login_form"):
                email = st.text_input("Email address", key="login_email").strip().lower()
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                user = st.session_state.demo_users.get(email)
                if user and user["password_hash"] == _password_hash(password):
                    st.session_state.logged_in_email = email
                    st.rerun()
                else:
                    st.error("Account not found in this session, or password is incorrect. Create a demo account first.")

if not st.session_state.logged_in_email:
    _show_auth()
    st.stop()

current_email = st.session_state.logged_in_email
current_user = st.session_state.demo_users.get(current_email, {})
current_profile = st.session_state.profiles.setdefault(current_email, {"onboarding_complete": False})

if not current_profile.get("onboarding_complete"):
    st.title("👋 Let's personalize your TimeLeak")
    st.write("Answer these six questions so the dashboard can use your goals and profile.")
    with st.form("profile_form"):
        role = st.selectbox("1. What is your role?", ["Student", "Teacher", "Working professional", "Other"])
        if role == "Student":
            education_place = st.selectbox("2. Where do you study?", ["School", "College", "Other"])
            field = st.selectbox("3. Which stream or field?", [
                "Information Technology", "Computer Engineering", "Other Engineering",
                "Commerce", "Science", "Arts", "Medical", "Other"
            ])
        elif role == "Teacher":
            education_place = st.selectbox("2. Where do you teach?", ["School", "College", "Training institute", "Other"])
            field = st.selectbox("3. Which subject or field do you teach?", [
                "IT / Computer", "Engineering", "Commerce", "Science", "Arts", "Medical", "Other"
            ])
        else:
            education_place = st.selectbox("2. Which setting best describes you?", ["School", "College", "Workplace", "Other"])
            field = st.text_input("3. Which field are you in?", placeholder="e.g. IT, business, design")
        goal = st.selectbox("4. What is your main goal?", [
            "Reduce wasted time", "Improve study productivity", "Balance work and personal life"
        ])
        daily_phone = st.selectbox("5. How much time do you use your phone daily?", [
            "Under 2 hours", "2–4 hours", "4–6 hours", "Over 6 hours"
        ])
        apps_used = st.multiselect("6. Which apps do you use most?", [
            "Instagram", "YouTube", "WhatsApp", "Snapchat", "Chrome",
            "LinkedIn", "GitHub", "Telegram", "Coursera", "Other apps"
        ])
        save_profile = st.form_submit_button("Save profile and open dashboard", use_container_width=True)
    if save_profile:
        current_profile.update({
            "name": current_user.get("name", ""),
            "role": role,
            "education_place": education_place,
            "field": field,
            "goal": goal,
            "daily_phone": daily_phone,
            "apps_used": apps_used,
            "onboarding_complete": True,
        })
        st.rerun()
    st.stop()

with st.sidebar:
    st.markdown("---")
    st.write(f"Signed in as **{current_user.get('name', 'User')}**")
    st.caption(f"{current_profile.get('role', 'User')} · {current_profile.get('field', '')}")
    if st.button("Log out", use_container_width=True):
        _logout()


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

profile_field = current_profile.get("field", "IT")
course_options = ["IT", "Mechanical", "Commerce", "Medical"]
default_course = "IT"
if "Commerce" in profile_field:
    default_course = "Commerce"
elif "Medical" in profile_field:
    default_course = "Medical"
elif "Mechanical" in profile_field or "Engineering" in profile_field:
    default_course = "Mechanical"
course = st.sidebar.selectbox(
    "Select your course",
    course_options,
    index=course_options.index(default_course),
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
    f"Personalized for {current_user.get('name', 'User')} · "
    f"Goal: {current_profile.get('goal', 'Improve productivity')} · "
    f"Profile: {current_profile.get('role', 'User')}"
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
