from data_loader import load_data


def get_ticket_summary():
    df = load_data()

    summary = {
        "total_tickets": len(df),
        "open_tickets": len(
            df[df["status"].str.lower() == "open"]
        ),
        "closed_tickets": len(
            df[df["status"].str.lower() == "closed"]
        ),
        "high_priority_tickets": len(
            df[df["priority"].str.lower() == "high"]
        )
    }

    return summary


def get_high_priority_open_tickets():
    df = load_data()

    result = df[
        (df["priority"].str.lower() == "high") &
        (df["status"].str.lower() == "open")
    ]

    return result


if __name__ == "__main__":

    print("1. Ticket Summary")
    print("--------------------")

    summary = get_ticket_summary()

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\n2. High Priority Open Tickets")
    print("--------------------")

    tickets = get_high_priority_open_tickets()

    print("Count:", len(tickets))
    print(tickets)