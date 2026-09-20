import streamlit as st
import pandas as pd
from ai_analyzer import analyze_question
from data_loader import load_data

# Page configuration
st.set_page_config(
    page_title="AI Customer Support Analyzer",
    page_icon="🤖",
    layout="wide"
)

df=load_data()
# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("🤖 About This Project")

    st.write(
        "AI-powered customer support ticket analysis "
        "using Python, Pandas and Groq."
    )

    st.divider()

    st.subheader("📊 Dataset")

    st.write(f"Total Tickets: {len(df)}")
    st.write(f"Categories: {df['category'].nunique()}")
    st.write(f"Agents: {df['agent_id'].nunique()}")

    st.divider()

    st.subheader("📥 Download Data")

    csv_data = df.to_csv(index=False)

    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="support_tickets.csv",
        mime="text/csv"
    )

# Load dataset
df = load_data()

# Title
st.title("🤖 AI Customer Support Analyzer")
st.write(
    "Analyze customer support tickets."
)

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

total_tickets = len(df)

open_tickets = len(
    df[df["status"].str.lower() == "open"]
)

unresolved_tickets = len(
    df[df["status"].str.lower() != "resolved"]
)

average_response_time = df["response_time_hrs"].mean()

# Create 4 columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🎫 Total Tickets",
        value=total_tickets
    )

with col2:
    st.metric(
        label="🔴 Open Tickets",
        value=open_tickets
    )

with col3:
    st.metric(
        label="⚠️ Unresolved Tickets",
        value=unresolved_tickets
    )

with col4:
    st.metric(
        label="⏱️ Avg Response Time",
        value=f"{average_response_time:.2f} hrs"
    )

# --------------------------------------------------
# STATUS & CUSTOMER RATING
# --------------------------------------------------

st.divider()

st.subheader("📈 Support Performance")

status_col, rating_col = st.columns(2)

# Status chart
with status_col:

    status_counts = (
        df["status"]
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Tickets")
    )

    st.write("### Tickets by Status")

    st.bar_chart(
        status_counts,
        x="Status",
        y="Tickets"
    )


# Customer rating chart
with rating_col:

    rating_counts = (
        df["customer_rating"]
        .value_counts()
        .sort_index()
        .rename_axis("Rating")
        .reset_index(name="Tickets")
    )

    st.write("### Customer Rating Distribution")

    st.bar_chart(
        rating_counts,
        x="Rating",
        y="Tickets"
    )
# --------------------------------------------------
# AGENT PERFORMANCE
# --------------------------------------------------

st.divider()

st.subheader("👨‍💻 Agent Performance")

agent_counts = (
    df["agent_id"]
    .value_counts()
    .rename_axis("Agent")
    .reset_index(name="Tickets")
)

st.bar_chart(
    agent_counts,
    x="Agent",
    y="Tickets"
)
# --------------------------------------------------
# RECENT SUPPORT TICKETS
# --------------------------------------------------

st.divider()

st.subheader("🎫 Recent Support Tickets")

recent_tickets = df.copy()

recent_tickets["created_at"] = pd.to_datetime(
    recent_tickets["created_at"]
)

recent_tickets = recent_tickets.sort_values(
    by="created_at",
    ascending=False
).head(10)

st.dataframe(
    recent_tickets[
        [
            "ticket_id",
            "created_at",
            "category",
            "priority",
            "status",
            "agent_id",
            "issue_summary"
        ]
    ],
    use_container_width=True
)
# --------------------------------------------------
# DATASET SUMMARY
# --------------------------------------------------

st.divider()

st.subheader("📋 Dataset Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:

    st.write("### Categories")

    st.write(
        ", ".join(
            df["category"].unique()
        )
    )

with summary_col2:

    st.write("### Priorities")

    st.write(
        ", ".join(
            df["priority"].unique()
        )
    )

with summary_col3:

    st.write("### Agents")

    st.write(
        f"{df['agent_id'].nunique()} agents"
    )
# --------------------------------------------------
# AI QUESTION SECTION
# --------------------------------------------------
# --------------------------------------------------
# DATASET VISUALIZATIONS
# --------------------------------------------------

st.divider()

st.subheader("📊 Ticket Overview")

chart_col1, chart_col2 = st.columns(2)

# Category chart
with chart_col1:

    category_counts = (
        df["category"]
        .value_counts()
        .rename_axis("Category")
        .reset_index(name="Tickets")
    )

    st.write("### Tickets by Category")

    st.bar_chart(
        category_counts,
        x="Category",
        y="Tickets"
    )


# Priority chart
with chart_col2:

    priority_counts = (
        df["priority"]
        .value_counts()
        .rename_axis("Priority")
        .reset_index(name="Tickets")
    )

    st.write("### Tickets by Priority")

    st.bar_chart(
        priority_counts,
        x="Priority",
        y="Tickets"
    )
st.divider()

st.subheader("💬 Ask Your Data")

example_questions = [
    "How many unresolved tickets are there?",
    "Which category has the most tickets?",
    "Which agent handles the most tickets?",
    "What is the average response time for technical tickets?",
    "Which high priority technical tickets have the longest response times?",
    "How many unresolved billing tickets are handled by each agent?"
]

selected_question = st.selectbox(
    "💡 Try an example question:",
    ["Select a question"] + example_questions
)

question = st.text_input(
    "Or type your own question:"
)

if selected_question != "Select a question":
    question = selected_question

if st.button("🔍 Analyze"):

    if question.strip():

        with st.spinner("Analyzing your question..."):

            answer = analyze_question(question)

        st.subheader("🤖 AI Answer")

        st.write(answer)

    else:

        st.warning(
            "Please enter a question."
        )