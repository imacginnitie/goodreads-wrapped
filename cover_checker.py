import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd


def parse_read_dates(read_dates_str):
    """Parse the read_dates string format"""
    if pd.isna(read_dates_str):
        return []

    finish_dates = []
    cleaned_str = read_dates_str.strip('"')
    sessions = [s.strip() for s in cleaned_str.split(";") if s.strip()]

    for session in sessions:
        try:
            if session.startswith(","):
                end_date = pd.to_datetime(session[1:].strip())
                finish_dates.append(end_date)
            else:
                dates = [d.strip() for d in session.split(",") if d.strip()]
                if len(dates) == 2:
                    end_date = pd.to_datetime(dates[1])
                    finish_dates.append(end_date)
        except Exception:
            continue

    return finish_dates


def check_missing_covers(csv_file, year, covers_dir="./book_covers"):
    # Read CSV file
    df = pd.read_csv(csv_file)
    covers_path = Path(covers_dir)

    # Process finish dates
    records = []
    for _, row in df.iterrows():
        finish_dates = parse_read_dates(row["read_dates"])
        if finish_dates:  # Only include books with finish dates
            latest_finish = max(finish_dates)
            records.append(
                {
                    "finish_date": latest_finish,
                    "book_id": row["Book Id"],
                    "title": row["Title"],
                    "author": row["Author"],
                }
            )

    books_df = pd.DataFrame(records)

    # Filter for specified year
    books_df["finish_date"] = pd.to_datetime(books_df["finish_date"])
    books_year = books_df[books_df["finish_date"].dt.year == year].copy()

    # Check for missing covers
    missing_covers = []
    for _, book in books_year.iterrows():
        cover_path = covers_path / f"{book.book_id}.jpg"
        if not cover_path.exists():
            missing_covers.append(
                {
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "finish_date": book.finish_date.strftime("%Y-%m-%d"),
                    "expected_path": str(cover_path),
                }
            )

    # Print results
    if missing_covers:
        print(f"\nFound {len(missing_covers)} books missing cover art for {year}:")
        for book in missing_covers:
            print(f"\nBook ID: {book['book_id']}")
            print(f"Title: {book['title']}")
            print(f"Author: {book['author']}")
            print(f"Finished: {book['finish_date']}")
            print(f"Expected cover path: {book['expected_path']}")
    else:
        print(f"\nAll books from {year} have cover art!")

    return missing_covers


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check for missing book covers for a specific year"
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
        help=f"Year to check (default: {datetime.now().year})",
    )
    parser.add_argument(
        "-d",
        "--covers-dir",
        type=str,
        default="./book_covers",
        help="Directory containing book covers (default: ./book_covers)",
    )

    args = parser.parse_args()
    check_missing_covers(args.csv, args.year, args.covers_dir)
