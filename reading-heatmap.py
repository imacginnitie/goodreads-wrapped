import argparse
import calendar
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def parse_read_dates(read_dates_str):
    """
    Parse the read_dates string format
    - The entire string is wrapped in quotes
    - Leading comma indicates no start date, just end date (e.g. ",2024-05-01")
    - Dates without leading comma have both start and end (e.g. "2024-10-21,2024-10-21")
    - Multiple sessions separated by semicolons
    Returns a list of end dates (when books were finished)
    """
    if pd.isna(read_dates_str):
        return []

    finish_dates = []
    # Remove the outer quotes and split by semicolon
    cleaned_str = read_dates_str.strip('"')
    sessions = [s.strip() for s in cleaned_str.split(";") if s.strip()]

    for session in sessions:
        try:
            if session.startswith(","):
                # Just an end date
                end_date = pd.to_datetime(session[1:].strip())
                finish_dates.append(end_date)
            else:
                # Has both start and end date
                dates = [d.strip() for d in session.split(",") if d.strip()]
                if len(dates) == 2:  # Should have both start and end date
                    end_date = pd.to_datetime(dates[1])
                    finish_dates.append(end_date)
                else:
                    print(
                        f"Warning: Expected start and end date for session without leading comma: {session}"
                    )
        except Exception:
            print(f"Warning: Could not parse date session: {session}")
            continue

    return finish_dates


def create_reading_heatmap(csv_file, year, name="Isabel", orientation="landscape"):
    """
    Generate a GitHub-style heatmap of reading activity.

    Parameters:
    csv_file (str): Path to the Goodreads CSV export file
    year (int): Year to create heatmap for
    name (str): Name to use in title
    orientation (str): 'landscape' or 'portrait' orientation for the plot
    """
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Get all finish dates from read_dates column
    all_finish_dates = []
    for dates in df["read_dates"]:
        all_finish_dates.extend(parse_read_dates(dates))

    # Convert to DataFrame for easier handling
    dates_df = pd.DataFrame({"finish_date": all_finish_dates})

    # Create a date range for all days in the specified year
    start_date = pd.Timestamp(f"{year}-01-01")
    end_date = pd.Timestamp(f"{year}-12-31")
    all_dates = pd.date_range(start=start_date, end=end_date)

    # Filter for books finished in the specified year and count books per day
    dates_df["finish_date"] = pd.to_datetime(dates_df["finish_date"])
    dates_year = dates_df[dates_df["finish_date"].dt.year == year]
    daily_counts = (
        dates_df["finish_date"].value_counts().reindex(all_dates, fill_value=0)
    )

    # Create week numbers and day numbers for the heatmap
    weeks = []
    days = []
    months = []
    counts = []

    for date in all_dates:
        # Week number (0-52)
        week = date.strftime("%U")
        # Day of week (0-6), where 0 is Monday
        day = date.weekday()
        # Month
        month = date.month - 1  # 0-based index
        count = daily_counts[date]

        weeks.append(int(week))
        days.append(day)
        months.append(month)
        counts.append(count)

    # Create the heatmap data
    heatmap_data = np.zeros((7, 53))  # 7 days x 53 weeks
    for w, d, c in zip(weeks, days, counts):
        heatmap_data[d, w] = c

    # Set up the figure size based on orientation
    if orientation.lower() == "landscape":
        fig_width, fig_height = 20, 3
        rotation = 0
    else:  # portrait
        fig_width, fig_height = 3, 20
        heatmap_data = heatmap_data.T  # Transpose the data
        rotation = 0

    # Create the visualization
    plt.figure(figsize=(fig_width, fig_height))

    # Create custom month labels
    month_positions = []
    month_labels = []

    for month in range(12):
        # Find the first date of each month
        first_day = pd.Timestamp(f"{year}-{month + 1}-01")
        if orientation.lower() == "landscape":
            position = int(first_day.strftime("%U"))
        else:
            position = int(first_day.strftime("%U"))

        month_positions.append(position)
        month_labels.append(calendar.month_abbr[month + 1])

    # Create the heatmap
    ax = sns.heatmap(
        heatmap_data,
        cmap="Greens",
        square=True,
        cbar_kws={"label": "Books finished"},
        yticklabels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        if orientation.lower() == "landscape"
        else month_positions,
        xticklabels=month_positions
        if orientation.lower() == "landscape"
        else ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    )

    # Set the month labels
    if orientation.lower() == "landscape":
        ax.set_xticks(month_positions)
        ax.set_xticklabels(month_labels, rotation=rotation)
    else:
        ax.set_yticks(month_positions)
        ax.set_yticklabels(month_labels, rotation=rotation)

    # Add title and labels
    plt.title(f"{name}'s {year} Books")

    # Calculate statistics
    total_books = int(daily_counts.sum())
    max_books_day = int(daily_counts.max())
    active_days = int((daily_counts > 0).sum())

    # Add statistics text in appropriate position based on orientation
    if orientation.lower() == "landscape":
        plt.figtext(
            0.02,
            -0.2,
            f"Total books: {total_books}\n"
            f"Most books finished in one day: {max_books_day}\n"
            f"Days with completed books: {active_days}",
            fontsize=10,
        )
    else:
        plt.figtext(
            1.2,
            0.02,
            f"Total books: {total_books}\n"
            f"Most books finished in one day: {max_books_day}\n"
            f"Days with completed books: {active_days}",
            fontsize=10,
        )

    plt.tight_layout()
    plt.show()

    # Print additional statistics
    print(f"\nReading Statistics for {year}:")
    print(f"Total books read: {total_books}")
    print(f"Most books finished in one day: {max_books_day}")
    print(f"Number of active reading days: {active_days}")
    if active_days > 0:
        print(f"Average books per active day: {total_books / active_days:.2f}")

    # Show the busiest reading days
    top_days = daily_counts[daily_counts > 0].sort_values(ascending=False).head()
    print("\nBusiest reading days:")
    for date, count in top_days.items():
        print(f"{date.strftime('%Y-%m-%d')}: {int(count)} books")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a GitHub-style heatmap of reading activity"
    )
    parser.add_argument(
        "-c",
        "--csv",
        type=str,
        default="goodreads_library_export.csv",
        help="Path to the enhanced GoodReads CSV file (default: goodreads_library_export.csv)",
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=datetime.now().year,
        help=f"Year to create heatmap for (default: {datetime.now().year})",
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        default="Isabel",
        help="Name to use in title (default: Isabel)",
    )
    parser.add_argument(
        "-o",
        "--orientation",
        type=str,
        choices=["landscape", "portrait"],
        default="landscape",
        help="Orientation: landscape or portrait (default: landscape)",
    )

    args = parser.parse_args()
    create_reading_heatmap(args.csv, args.year, args.name, args.orientation)
