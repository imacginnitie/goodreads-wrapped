import argparse
from datetime import datetime
from pathlib import Path

import imageio
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw


def parse_read_dates(read_dates_str):
    """Parse the read_dates string format, returning all finish dates"""
    if pd.isna(read_dates_str):
        return []

    finish_dates = []
    cleaned_str = read_dates_str.strip('"')
    sessions = [s.strip() for s in cleaned_str.split(";") if s.strip()]

    for session in sessions:
        try:
            if session.startswith(","):
                # Just an end date
                end_date = pd.to_datetime(session[1:].strip())
                finish_dates.append(end_date)
            else:
                # Has start and end date
                dates = [d.strip() for d in session.split(",") if d.strip()]
                if len(dates) == 2:
                    end_date = pd.to_datetime(dates[1])
                    finish_dates.append(end_date)
        except Exception:
            continue

    return finish_dates


def create_reading_animation(
    csv_file,
    year,
    covers_dir="./book_covers",
    output_file=None,
    frame_duration=300,
    output_format=None,
):
    """
    Create an animated GIF or MP4 video of book covers in reading order, including rereads
    """
    if output_file is None:
        if output_format == "mp4":
            output_file = f"reading_journey_{year}.mp4"
        else:
            output_file = f"reading_journey_{year}.gif"
    elif output_format is None:
        # Auto-detect format from extension
        output_path = Path(output_file)
        if output_path.suffix.lower() == ".mp4":
            output_format = "mp4"
        else:
            output_format = "gif"

    # Read and process data
    df = pd.read_csv(csv_file)
    covers_path = Path(covers_dir)

    # Get all finish dates and book info
    records = []
    for _, row in df.iterrows():
        finish_dates = parse_read_dates(row["read_dates"])
        for finish_date in finish_dates:  # Process each reading session
            records.append(
                {
                    "finish_date": finish_date,
                    "book_id": row["Book Id"],
                    "title": row["Title"],
                    "author": row["Author"],
                    "read_count": len(finish_dates),  # Track total number of reads
                }
            )

    books_df = pd.DataFrame(records)

    # Filter for specified year and sort by finish date
    books_df["finish_date"] = pd.to_datetime(books_df["finish_date"])
    books_year = books_df[books_df["finish_date"].dt.year == year].sort_values(
        "finish_date"
    )

    if len(books_year) == 0:
        print(f"No books found for {year}")
        return

    # Initialize list for frames
    frames = []
    target_size = (300, 450)  # Standard size for all covers

    # Create frames for each book reading session
    for _, book in books_year.iterrows():
        cover_path = covers_path / f"{book.book_id}.jpg"

        # Create frame
        if cover_path.exists():
            # Load and resize cover
            with Image.open(cover_path) as img:
                frame = img.convert("RGB")
                frame = frame.resize(target_size, Image.Resampling.LANCZOS)
        else:
            # Create placeholder for missing cover
            frame = Image.new("RGB", target_size, "lightgray")
            draw = ImageDraw.Draw(frame)
            draw.text(
                (150, 200),
                f"{book.title}\nby\n{book.author}",
                fill="black",
                anchor="mm",
                align="center",
            )

        # Add date overlay
        draw = ImageDraw.Draw(frame)
        date_text = book.finish_date.strftime("%b %d, %Y")
        if book.read_count > 1:
            # Calculate which read this is by counting previous reads
            read_number = pd.Series(
                books_df[books_df["book_id"] == book.book_id]["finish_date"]
                <= book.finish_date
            ).sum()
            if read_number > 1:
                date_text += f" (Read #{read_number})"
        draw.text(
            (10, 435), date_text, fill="white", stroke_width=1, stroke_fill="black"
        )

        frames.append(frame)

    # Save as animated GIF or MP4
    if frames:
        output_path = Path(output_file)
        file_ext = output_path.suffix.lower()

        if file_ext == ".mp4" or output_format == "mp4":
            # Convert frames to numpy arrays for imageio
            frame_arrays = [np.array(frame) for frame in frames]
            # Calculate fps from frame_duration (milliseconds to fps)
            fps = 1000.0 / frame_duration if frame_duration > 0 else 30
            # Save as MP4
            try:
                imageio.mimwrite(
                    output_file, frame_arrays, fps=fps, codec="libx264", quality=8
                )
            except Exception as err:
                # Fallback if libx264 not available
                print(
                    f"Warning: libx264 codec not available, trying alternative: {err}"
                )
                imageio.mimwrite(output_file, frame_arrays, fps=fps)
            print(
                f"Created MP4 video with {len(frames)} reading sessions in {output_file}"
            )
        else:
            # Save as animated GIF
            frames[0].save(
                output_file,
                save_all=True,
                append_images=frames[1:],
                duration=frame_duration,
                loop=0,
            )
            print(
                f"Created GIF animation with {len(frames)} reading sessions in {output_file}"
            )

        # Print some statistics
        unique_books = len(books_year["book_id"].unique())
        total_reads = len(books_year)
        reread_books = books_year[books_year["read_count"] > 1]["book_id"].nunique()
        print(f"\nReading Statistics for {year}:")
        print(f"Unique books: {unique_books}")
        print(f"Total reading sessions: {total_reads}")
        print(f"Books that were reread: {reread_books}")

        if reread_books > 0:
            print("\nBooks with multiple reads:")
            reread_stats = (
                books_year[books_year["read_count"] > 1]
                .drop_duplicates("book_id")[["title", "read_count"]]
                .sort_values("read_count", ascending=False)
            )
            for _, book in reread_stats.iterrows():
                print(f"- {book['title']}: {book['read_count']} times")
    else:
        print("No frames created")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create an animated GIF of book covers in reading order"
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
        help=f"Year to create animation for (default: {datetime.now().year})",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output filename (default: reading_journey_{year}.gif). Use .mp4 extension for video output",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["gif", "mp4"],
        default=None,
        help="Output format: gif or mp4 (default: auto-detect from filename extension)",
    )
    parser.add_argument(
        "-d",
        "--covers-dir",
        type=str,
        default="./book_covers",
        help="Directory containing book covers (default: ./book_covers)",
    )
    parser.add_argument(
        "-f",
        "--frame-duration",
        type=int,
        default=300,
        help="Frame duration in milliseconds (default: 300)",
    )

    args = parser.parse_args()
    create_reading_animation(
        args.csv,
        args.year,
        args.covers_dir,
        args.output,
        args.frame_duration,
        args.format,
    )
