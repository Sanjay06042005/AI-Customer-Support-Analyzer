import pandas as pd

from data_loader import load_data
from ai_analyzer import (
    extract_filters_local,
    extract_month_range,
    apply_filters
)


def get_filtered_data(question):
    df = load_data()

    filters = extract_filters_local(question)

    filtered_df = apply_filters(df, filters)

    start_date, end_date = extract_month_range(question)

    if start_date and end_date:
        filtered_df = filtered_df.copy()

        filtered_df["created_at"] = pd.to_datetime(
            filtered_df["created_at"]
        )

        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        filtered_df = filtered_df[
            (filtered_df["created_at"] >= start)
            & (filtered_df["created_at"] <= end)
        ]

    return filtered_df


tests = [
    "How many technical tickets were handled by each agent in February 2024?",
    "How many tickets are in each category in February 2024?",
    "How many tickets are there for each priority in February 2024?",
    "What are the most common customer issues in February 2024?",
    "Give me a summary of unresolved tickets in February 2024?"
]


df = load_data()

print("=" * 60)
print("LOCAL ANALYSIS TESTS")
print("=" * 60)

for question in tests:

    filtered_df = get_filtered_data(question)

    print("\nQuestion:")
    print(question)

    print("\nMatching tickets:", len(filtered_df))

    if "each agent" in question.lower():
        result = (
            filtered_df["agent_id"]
            .value_counts()
            .reset_index()
        )

    elif "each category" in question.lower():
        result = (
            filtered_df["category"]
            .value_counts()
            .reset_index()
        )

    elif "each priority" in question.lower():
        result = (
            filtered_df["priority"]
            .value_counts()
            .reset_index()
        )

    elif "most common customer issues" in question.lower():
        result = (
            filtered_df["issue_summary"]
            .value_counts()
            .head(10)
            .reset_index()
        )

    elif "summary of unresolved" in question.lower():
        unresolved_df = filtered_df[
            filtered_df["status"].str.lower() != "resolved"
        ]

        print("Unresolved tickets:", len(unresolved_df))

        print("\nBy category:")
        print(
            unresolved_df["category"]
            .value_counts()
        )

        print("\nBy priority:")
        print(
            unresolved_df["priority"]
            .value_counts()
        )

        continue

    print("\nResult:")
    print(result.to_string(index=False))

print("\n" + "=" * 60)
print("TESTS COMPLETED")
print("=" * 60)