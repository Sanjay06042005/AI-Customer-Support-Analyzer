import os
import re
import pandas as pd
from dotenv import load_dotenv
from groq import Groq,RateLimitError

from data_loader import load_data

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=api_key)
def generate_answer(question, analysis):
    prompt = f"""
You are an AI customer support data analyst.

User question:
{question}

Python analyzed the actual support ticket dataset and produced:

{analysis}

Answer the user's question clearly.

IMPORTANT:
- Use only the information provided by Python.
- Never invent numbers.
- Never invent ticket details.
- If the analysis does not contain enough information, say so.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        return response.choices[0].message.content

    except RateLimitError:
        return (
            "Groq API limit reached.\n\n"
            "The exact dataset analysis was calculated successfully "
            "by Python/Pandas:\n\n"
            f"{analysis}"
        )

    except Exception as e:
        return (
            "The dataset analysis was completed, but the AI response "
            f"could not be generated.\n\n"
            f"Python analysis:\n{analysis}\n\n"
            f"Error: {e}"
        )

def apply_filters(df, filters):
    filtered_df = df.copy()

    category = filters.get("category")
    priority = filters.get("priority")
    status = filters.get("status")
    agent_id = filters.get("agent_id")

    # Filter by category
    if category:
        filtered_df = filtered_df[
            filtered_df["category"].str.lower() == category.lower()
        ]

    # Filter by priority
    if priority:
        filtered_df = filtered_df[
            filtered_df["priority"].str.lower() == priority.lower()
        ]

    # Filter by status
    if status:
        if status.lower() == "unresolved":
            filtered_df = filtered_df[
                filtered_df["status"].str.lower() != "resolved"
            ]
        else:
            filtered_df = filtered_df[
                filtered_df["status"].str.lower() == status.lower()
            ]

    # Filter by agent
    if agent_id:
        filtered_df = filtered_df[
            filtered_df["agent_id"].str.lower() == agent_id.lower()
        ]

    return filtered_df

def extract_date_range(question):
    pattern = r"(\d{4}-\d{2}-\d{2})\s*(?:to|and|-)\s*(\d{4}-\d{2}-\d{2})"

    match = re.search(pattern, question)

    if match:
        start_date = match.group(1)
        end_date = match.group(2)

        return start_date, end_date

    return None, None

def extract_month_range(question):
    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12
    }

    pattern = r"\b(" + "|".join(months.keys()) + r")\s+(\d{4})\b"

    match = re.search(pattern, question.lower())

    if match:
        month_name = match.group(1)
        year = int(match.group(2))
        month = months[month_name]

        start_date = pd.Timestamp(
            year=year,
            month=month,
            day=1
        )

        end_date = (
            start_date
            + pd.offsets.MonthEnd(1)
        )

        return (
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )

    return None, None


def detect_operation_local(question):
    q = question.lower()

    # Response time
    if "average response time" in q or "mean response time" in q:
        return "average_response_time"

    if (
        ("highest" in q or "longest" in q or "slowest" in q)
        and "response time" in q
    ):
        return "highest_response_time"

    if (
        ("fastest" in q or "shortest" in q or "quickest" in q)
        and "response time" in q
    ):
        return "fastest_response_time"

    # Resolution time
    if "average resolution time" in q or "mean resolution time" in q:
        return "average_resolution_time"

    if (
        ("highest" in q or "longest" in q or "slowest" in q)
        and "resolution time" in q
    ):
        return "highest_resolution_time"

    if (
        ("fastest" in q or "shortest" in q or "quickest" in q)
        and "resolution time" in q
    ):
        return "fastest_resolution_time"



        # Customer rating
    if (
        "which category has the highest average customer rating" in q
        or "which category has the best customer rating" in q
        or "customer rating by category" in q
        or "customer ratings by category" in q
    ):
        return "rating_by_category"

    if (
        "which priority has the highest average customer rating" in q
        or "which priority has the best customer rating" in q
        or "customer rating by priority" in q
        or "customer ratings by priority" in q
    ):
        return "rating_by_priority"

    if (
        "which agent has the highest average customer rating" in q
        or "which agent has the best customer rating" in q
        or "customer rating by agent" in q
        or "customer ratings by agent" in q
    ):
        return "rating_by_agent"

    if (
        "average customer rating" in q
        or "mean customer rating" in q
        or "average rating" in q
        or "mean rating" in q
        or "customer satisfaction rating" in q
    ):
        return "average_customer_rating"




    
    # Common issues
    if (
        "most common issues" in q
        or "common issues" in q
        or "top issue types" in q
        or "which issues occur most frequently" in q
        or "issue frequency" in q
    ):
        if "category" in q or any(
            word in q for word in ["technical", "billing", "general"]
        ):
            return "issue_analysis"

        return "top_issue_types"

    # Unresolved summary
    if (
        "summary of unresolved tickets" in q
        or "summarize unresolved tickets" in q
        or "unresolved ticket summary" in q
        or "unresolved ticket overview" in q
    ):
        return "unresolved_summary"

    # Daily analysis
    if (
        "each day" in q
        or "by day" in q
        or "daily ticket count" in q
        or "daily ticket counts" in q
        or "daily ticket trends" in q
        or "which day had the most tickets" in q
    ):
        return "daily_ticket_analysis"

    # Monthly analysis
    if (
        "each month" in q
        or "by month" in q
        or "monthly ticket count" in q
        or "monthly ticket counts" in q
        or "monthly ticket trends" in q
        or "which month had the most tickets" in q
        or "which month had the most" in q
    ):
        return "monthly_ticket_analysis"

    # List must come before generic count
    if (
        "show me" in q
        or "list" in q
        or "display" in q
        or "give me the tickets" in q
        or "show all" in q
    ):
        return "list"

    # Agent analysis
    if (
        "which agent handles the most tickets" in q
        or "which agent handled the most tickets" in q
        or "which agent has the most tickets" in q
        or "tickets handled by each agent" in q
        or "agent performance" in q
    ):
        return "agent_analysis"

    # Category analysis
    if (
        "which category has the most tickets" in q
        or "how many tickets are in each category" in q
        or "show ticket counts by category" in q
        or "category-wise ticket analysis" in q
    ):
        return "category_analysis"

    # Priority analysis
    if (
        "how many tickets are there for each priority" in q
        or "which priority has the most tickets" in q
        or "how many tickets are in each priority" in q
        or "show ticket counts by priority" in q
        or "priority-wise ticket analysis" in q
    ):
        return "priority_analysis"

    # Date/month summary
    if (
        "summary" in q
        and (
            "between" in q
            or " in january " in f" {q} "
            or " in february " in f" {q} "
            or " in march " in f" {q} "
            or " in april " in f" {q} "
            or " in may " in f" {q} "
            or " in june " in f" {q} "
            or " in july " in f" {q} "
            or " in august " in f" {q} "
            or " in september " in f" {q} "
            or " in october " in f" {q} "
            or " in november " in f" {q} "
            or " in december " in f" {q} "
        )
    ):
        return "date_range_analysis"

    # Explicit date/month + how many
    if (
        "how many" in q
        and (
            "between " in q
            or re.search(
                r"\b(january|february|march|april|may|june|july|"
                r"august|september|october|november|december)\s+\d{4}\b",
                q
            )
        )
    ):
        return "date_range_analysis"

    # Generic count
    if (
        "how many" in q
        or "number of tickets" in q
        or "total tickets" in q
    ):
        return "count"

    return "general"

def extract_filters_local(question):
    q = question.lower()

    filters = {
        "category": None,
        "priority": None,
        "status": None,
        "agent_id": None
    }

    # Category
    if "technical" in q:
        filters["category"] = "Technical"
    elif "billing" in q:
        filters["category"] = "Billing"
    elif "general" in q:
        filters["category"] = "General"

    # Priority
    if "critical" in q:
        filters["priority"] = "Critical"
    elif "high priority" in q or "high-priority" in q:
        filters["priority"] = "High"
    elif "medium priority" in q or "medium-priority" in q:
        filters["priority"] = "Medium"
    elif "low priority" in q or "low-priority" in q:
        filters["priority"] = "Low"

    # Status
    if "unresolved" in q:
        filters["status"] = "Unresolved"
    elif "escalated" in q:
        filters["status"] = "Escalated"
    elif "open" in q:
        filters["status"] = "Open"
    elif "resolved" in q:
        filters["status"] = "Resolved"

    # Agent
    match = re.search(r"\bAGT-\d+\b", question.upper())

    if match:
        filters["agent_id"] = match.group(0)

    return filters

def analyze_question(question):
    df = load_data()

    # Detect what the user wants
    operation = detect_operation_local(question)
    # Extract filters from the question
    filters = extract_filters_local(question)

    #operation = detect_operation_local(question)
    start_date, end_date = extract_date_range(question)
    month_start, month_end = extract_month_range(question)

    if not start_date and month_start:
        start_date = month_start
        end_date = month_end
    # Check for a specific ticket ID
    match = re.search(r"TKT-\d+", question.upper())

    if match:
        ticket_id = match.group(0)

        result = df[
            df["ticket_id"].str.upper() == ticket_id
        ]

        if result.empty:
            return f"Ticket {ticket_id} was not found in the dataset."

        ticket = result.iloc[0]

        analysis = f"""
Ticket ID: {ticket["ticket_id"]}
Category: {ticket["category"]}
Priority: {ticket["priority"]}
Status: {ticket["status"]}
Response time: {ticket["response_time_hrs"]} hours
Resolution time: {ticket["resolution_time_hrs"]} hours
Agent ID: {ticket["agent_id"]}
Customer rating: {ticket["customer_rating"]}
Issue summary: {ticket["issue_summary"]}
"""

        return generate_answer(question, analysis)

    # Apply filters
    filtered_df = apply_filters(df, filters)
    date_filtered_df = filtered_df.copy()

    if start_date and end_date:
        date_filtered_df["created_at"] = pd.to_datetime(
            date_filtered_df["created_at"]
        )

        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        date_filtered_df = date_filtered_df[
            (date_filtered_df["created_at"] >= start)
            & (date_filtered_df["created_at"] <= end)
        ]
    # COUNT operation
    if operation == "count":

        analysis = f"""
Matching tickets: {len(filtered_df)}
Filters applied: {filters}
"""

    # LIST operation
    elif operation == "list":

        if "all" in question.lower():
            sample = date_filtered_df[
                [
                    "ticket_id",
                    "created_at",
                    "category",
                    "priority",
                    "status",
                    "agent_id",
                    "issue_summary"
                ]
            ]
        else:
            sample = date_filtered_df[
                [
                    "ticket_id",
                    "category",
                    "priority",
                    "status",
                    "agent_id",
                    "issue_summary"
                ]
            ].head(10)

        analysis = f"""
    Matching tickets: {len(date_filtered_df)}

    Matching ticket details:

    {sample.to_string(index=False)}
    """
    # AVERAGE RESPONSE TIME
    elif operation == "average_response_time":
        if date_filtered_df.empty:
            analysis = "No tickets matched the requested filters."
        else:
            average = date_filtered_df["response_time_hrs"].mean()

            analysis = f"""
    Matching tickets: {len(date_filtered_df)}

    Average response time:
    {average:.2f} hours

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}
    """

            # HIGHEST RESPONSE TIME
    elif operation == "highest_response_time":
        analysis_df = date_filtered_df

        if analysis_df.empty:
            analysis = "No tickets matched the requested filters."
        else:
            result = analysis_df.sort_values(
                by="response_time_hrs",
                ascending=False
            ).head(10)

            analysis = f"""
    Matching tickets: {len(analysis_df)}

    Tickets with the highest response times for the selected filters:

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}

    {result[
        [
            "ticket_id",
            "created_at",
            "category",
            "priority",
            "status",
            "response_time_hrs",
            "agent_id",
            "issue_summary"
        ]
    ].to_string(index=False)}
    """
        # FASTEST RESOLUTION TIME
    elif operation == "fastest_resolution_time":

        if filtered_df.empty:
            analysis = "No tickets matched the requested filters."

        else:
            result = filtered_df.dropna(
                subset=["resolution_time_hrs"]
            ).sort_values(
                by="resolution_time_hrs",
                ascending=True
            ).head(10)

            analysis = f"""
Matching tickets with available resolution times: {len(result)}

Tickets with the fastest resolution times:

{result[
    [
        "ticket_id",
        "category",
        "priority",
        "status",
        "response_time_hrs",
        "resolution_time_hrs",
        "agent_id",
        "issue_summary"
    ]
].to_string(index=False)}
"""

        # CATEGORY ANALYSIS
    elif operation == "category_analysis":
        if date_filtered_df.empty:
            analysis = "No tickets matched the requested filters."
        else:
            category_counts = (
                date_filtered_df["category"]
                .value_counts()
                .reset_index()
            )

            category_counts.columns = [
                "category",
                "ticket_count"
            ]

            analysis = f"""
    Tickets by category for the selected filters:

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}

    {category_counts.to_string(index=False)}
    """
    # PRIORITY ANALYSIS
    elif operation == "priority_analysis":
        if date_filtered_df.empty:
            analysis = "No tickets matched the requested filters."
        else:
            priority_counts = (
                date_filtered_df["priority"]
                .value_counts()
                .reset_index()
            )

            priority_counts.columns = [
                "priority",
                "ticket_count"
            ]

            analysis = f"""
    Tickets by priority for the selected filters:

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}

    {priority_counts.to_string(index=False)}
    """
        # AGENT ANALYSIS
    elif operation == "agent_analysis":
        if date_filtered_df.empty:
            analysis = "No tickets matched the requested filters."
        else:
            agent_counts = (
                date_filtered_df["agent_id"]
                .value_counts()
                .reset_index()
            )

            agent_counts.columns = [
                "agent_id",
                "ticket_count"
            ]

            analysis = f"""
    Tickets handled by each agent for the selected filters:

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}

    {agent_counts.to_string(index=False)}
    """
        # FASTEST RESPONSE TIME
    elif operation == "fastest_response_time":

        if filtered_df.empty:
            analysis = "No tickets matched the requested filters."

        else:
            result = filtered_df.sort_values(
                by="response_time_hrs",
                ascending=True
            ).head(10)

            analysis = f"""
Matching tickets: {len(filtered_df)}

Tickets with the fastest response times:

{result[
    [
        "ticket_id",
        "category",
        "priority",
        "status",
        "response_time_hrs",
        "agent_id",
        "issue_summary"
    ]
].to_string(index=False)}
"""

        # HIGHEST RESOLUTION TIME
    elif operation == "highest_resolution_time":

        if filtered_df.empty:
            analysis = "No tickets matched the requested filters."

        else:
            result = filtered_df.dropna(
                subset=["resolution_time_hrs"]
            ).sort_values(
                by="resolution_time_hrs",
                ascending=False
            ).head(10)

            analysis = f"""
Matching tickets with available resolution times: {len(result)}

Tickets with the longest resolution times:

{result[
    [
        "ticket_id",
        "category",
        "priority",
        "status",
        "response_time_hrs",
        "resolution_time_hrs",
        "agent_id",
        "issue_summary"
    ]
].to_string(index=False)}
"""


        # AVERAGE CUSTOMER RATING
    elif operation == "average_customer_rating":
        available_ratings = date_filtered_df[
            "customer_rating"
        ].dropna()

        if available_ratings.empty:
            analysis = """
    No customer rating is available for the matching tickets.
    """
        else:
            average = available_ratings.mean()

            analysis = f"""
    Matching tickets: {len(date_filtered_df)}

    Average customer rating:
    {average:.2f}

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}
    """

        # CUSTOMER RATING BY CATEGORY
    elif operation == "rating_by_category":
        if date_filtered_df.empty:
            analysis = """
    No tickets matched the requested filters.
    """
        else:
            rating_by_category = (
                date_filtered_df
                .groupby("category")["customer_rating"]
                .mean()
                .round(2)
                .reset_index()
            )

            rating_by_category.columns = [
                "category",
                "average_customer_rating"
            ]

            analysis = f"""
    Customer rating by category for the selected filters:

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}

    {rating_by_category.to_string(index=False)}
    """



    elif operation == "rating_by_priority":
        if date_filtered_df.empty:
            analysis = """
    No tickets matched the requested filters.
    """
        else:
            rating_by_priority = (
                date_filtered_df
                .groupby("priority")["customer_rating"]
                .mean()
                .round(2)
                .reset_index()
            )

            rating_by_priority.columns = [
                "priority",
                "average_customer_rating"
            ]

            analysis = f"""
    Customer rating by priority for the selected filters:

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}

    {rating_by_priority.to_string(index=False)}
    """



    elif operation == "rating_by_agent":
        if date_filtered_df.empty:
            analysis = """
    No tickets matched the requested filters.
    """
        else:
            rating_by_agent = (
                date_filtered_df
                .groupby("agent_id")["customer_rating"]
                .mean()
                .round(2)
                .reset_index()
            )

            rating_by_agent.columns = [
                "agent_id",
                "average_customer_rating"
            ]

            analysis = f"""
    Customer rating by agent for the selected filters:

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}

    {rating_by_agent.to_string(index=False)}
    """

    elif operation == "unresolved_summary":
        unresolved_df = date_filtered_df[
            date_filtered_df["status"].str.lower() != "resolved"
        ]

        if unresolved_df.empty:
            analysis = """
    No unresolved tickets matched the requested filters.
    """
        else:
            total_unresolved = len(unresolved_df)

            category_counts = (
                unresolved_df["category"]
                .value_counts()
                .reset_index()
            )

            category_counts.columns = [
                "category",
                "unresolved_tickets"
            ]

            priority_counts = (
                unresolved_df["priority"]
                .value_counts()
                .reset_index()
            )

            priority_counts.columns = [
                "priority",
                "unresolved_tickets"
            ]

            analysis = f"""
    Unresolved ticket summary for the selected filters:

    Total unresolved tickets:
    {total_unresolved}

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}

    Unresolved tickets by category:

    {category_counts.to_string(index=False)}

    Unresolved tickets by priority:

    {priority_counts.to_string(index=False)}
    """


    elif operation == "top_issue_types":
        if date_filtered_df.empty:
            analysis = """
    No tickets matched the requested filters.
    """
        else:
            issue_counts = (
                date_filtered_df["issue_summary"]
                .value_counts()
                .head(10)
                .reset_index()
            )

            issue_counts.columns = [
                "issue_summary",
                "ticket_count"
            ]

            analysis = f"""
    Most common customer issues for the selected filters:

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}

    {issue_counts.to_string(index=False)}
    """
    elif operation == "issue_analysis":
        analysis_df = date_filtered_df

        if analysis_df.empty:
            analysis = """
    No tickets matched the requested filters.
    """
        else:
            issue_counts = (
                analysis_df["issue_summary"]
                .value_counts()
                .head(10)
                .reset_index()
            )

            issue_counts.columns = [
                "issue_summary",
                "ticket_count"
            ]

            analysis = f"""
    Most common issues for the selected filters:

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}

    {issue_counts.to_string(index=False)}
    """

    elif operation == "monthly_ticket_analysis":

        if filtered_df.empty:
            analysis = """
No tickets matched the requested filters.
"""
        else:
            monthly_counts = (
                filtered_df.assign(
                    created_at=pd.to_datetime(
                        filtered_df["created_at"]
                    )
                )
                .groupby(
                    filtered_df["created_at"].dt.to_period("M")
                )
                .size()
                .reset_index(name="ticket_count")
            )

            monthly_counts["created_at"] = (
                monthly_counts["created_at"]
                .astype(str)
            )

            monthly_counts.columns = [
                "month",
                "ticket_count"
            ]

            analysis = f"""
Monthly ticket count for the selected filters:

Filters applied:
{filters}

{monthly_counts.to_string(index=False)}
"""


    elif operation == "daily_ticket_analysis":
        if date_filtered_df.empty:
            analysis = """
    No tickets matched the requested filters.
    """
        else:
            daily_counts = (
                date_filtered_df.assign(
                    created_at=pd.to_datetime(
                        date_filtered_df["created_at"]
                    )
                )
                .groupby(
                    date_filtered_df["created_at"].dt.date
                )
                .size()
                .reset_index(name="ticket_count")
            )

            daily_counts.columns = [
                "date",
                "ticket_count"
            ]

            busiest_day = daily_counts.loc[
                daily_counts["ticket_count"].idxmax()
            ]

            analysis = f"""
    Daily ticket count for the selected filters:

    Filters applied:
    {filters}

    {daily_counts.to_string(index=False)}

    Busiest day:
    {busiest_day["date"]}

    Tickets created on the busiest day:
    {busiest_day["ticket_count"]}
    """


    elif operation == "date_range_analysis":

        if not start_date or not end_date:
            analysis = """
The question does not contain a valid date range.
"""
        else:
            date_df = filtered_df.copy()

            date_df["created_at"] = pd.to_datetime(
                date_df["created_at"]
            )

            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)

            date_df = date_df[
                (date_df["created_at"] >= start)
                & (date_df["created_at"] <= end)
            ]

            if "summary" in question.lower():
                category_counts = (
                    date_df["category"]
                    .value_counts()
                    .reset_index()
                )

                category_counts.columns = [
                    "category",
                    "ticket_count"
                ]

                priority_counts = (
                    date_df["priority"]
                    .value_counts()
                    .reset_index()
                )

                priority_counts.columns = [
                    "priority",
                    "ticket_count"
                ]

                status_counts = (
                    date_df["status"]
                    .value_counts()
                    .reset_index()
                )

                status_counts.columns = [
                    "status",
                    "ticket_count"
                ]

                agent_counts = (
                    date_df["agent_id"]
                    .value_counts()
                    .reset_index()
                )

                agent_counts.columns = [
                    "agent_id",
                    "ticket_count"
                ]

                analysis = f"""
        Ticket summary for:
        {start_date} to {end_date}

        Total tickets:
        {len(date_df)}

        Category breakdown:

        {category_counts.to_string(index=False)}

        Priority breakdown:

        {priority_counts.to_string(index=False)}

        Status breakdown:

        {status_counts.to_string(index=False)}

        Agent breakdown:

        {agent_counts.to_string(index=False)}
        """

            else:
                analysis = f"""
        Date range:
        {start_date} to {end_date}

        Filters applied:
        {filters}

        Matching tickets:
        {len(date_df)}
        """
            
    # AVERAGE RESOLUTION TIME
    elif operation == "average_resolution_time":
        available_times = date_filtered_df[
            "resolution_time_hrs"
        ].dropna()

        if available_times.empty:
            analysis = """
    No resolution time is available for the matching tickets.
    """
        else:
            average = available_times.mean()

            analysis = f"""
    Matching tickets: {len(date_filtered_df)}

    Average resolution time:
    {average:.2f} hours

    Filters applied:
    {filters}

    Date range:
    {start_date} to {end_date}
    """

    else:
        analysis = """
The question could not be mapped to a supported operation.
"""
    # Let Groq convert the Python result into a natural answer
    answer = generate_answer(question, analysis)

    return answer
if __name__ == "__main__":
    question = input(
        "Ask a question about the support tickets: "
    )
    answer = analyze_question(question)
    print("\nAI Answer:")
    print(answer)