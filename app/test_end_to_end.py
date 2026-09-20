from ai_analyzer import analyze_question


questions = [
    "What was the average response time for technical tickets in February 2024?",
    "What was the average resolution time for technical tickets in February 2024?",
    "What was the average customer rating for technical tickets in February 2024?",
    "Which category has the highest average customer rating in February 2024?",
    "Which technical tickets had the highest response times in February 2024?",
    "What are the most common issues in technical tickets in February 2024?",
    "Show me all unresolved technical tickets created in February 2024."
]


for i, question in enumerate(questions, 1):

    print("\n" + "=" * 70)
    print(f"TEST {i}")
    print("Question:", question)
    print("=" * 70)

    answer = analyze_question(question)

    print("\nAI Answer:")
    print(answer)