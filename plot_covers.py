import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path
import matplotlib.gridspec as gridspec
import argparse
from datetime import datetime

def parse_read_dates(read_dates_str):
    """Parse the read_dates string format"""
    if pd.isna(read_dates_str):
        return []
    
    finish_dates = []
    cleaned_str = read_dates_str.strip('"')
    sessions = [s.strip() for s in cleaned_str.split(';') if s.strip()]
    
    for session in sessions:
        try:
            if session.startswith(','):
                end_date = pd.to_datetime(session[1:].strip())
                finish_dates.append(end_date)
            else:
                dates = [d.strip() for d in session.split(',') if d.strip()]
                if len(dates) == 2:
                    end_date = pd.to_datetime(dates[1])
                    finish_dates.append(end_date)
        except Exception as e:
            continue
            
    return finish_dates

def create_monthly_book_grid(csv_file, year, covers_dir='./book_covers', title=None):
    if title is None:
        title = f'{year} Reading'
    
    # Read and process data
    df = pd.read_csv(csv_file)
    covers_path = Path(covers_dir)

    # Get all finish dates and book info
    records = []
    for _, row in df.iterrows():
        for date in parse_read_dates(row['read_dates']):
            records.append({
                'finish_date': date,
                'book_id': row['Book Id'],
                'title': row['Title']
            })
    
    books_df = pd.DataFrame(records)
    
    # Filter for specified year and group by month
    books_df['finish_date'] = pd.to_datetime(books_df['finish_date'])
    books_year = books_df[books_df['finish_date'].dt.year == year].copy()
    books_year['month'] = books_year['finish_date'].dt.month
    monthly_books = dict(tuple(books_year.groupby('month')))

    # Calculate layout
    active_months = sorted(monthly_books.keys())
    if not active_months:
        print(f"No books found for {year}")
        return

    # Create figure with tighter spacing
    # Calculate height based on number of rows needed (more compact)
    max_rows_per_month = max([(len(monthly_books[m]) - 1) // min(8, len(monthly_books[m])) + 1 
                              for m in active_months] + [1])
    fig_height = max(8, 1.2 * len(active_months) * max_rows_per_month)
    fig = plt.figure(figsize=(15, fig_height))
    
    # Create main gridspec with minimal spacing
    outer_gs = gridspec.GridSpec(len(active_months), 1)
    outer_gs.update(left=0.05, right=0.98, top=0.97, bottom=0.02, hspace=0.05)

    for idx, month in enumerate(active_months):
        month_books = monthly_books[month]
        
        # Calculate grid dimensions for this month
        n_books = len(month_books)
        cols = min(8, n_books)  # Max 8 books per row
        rows = (n_books - 1) // cols + 1
        
        # Create month subplot with smaller label area
        month_gs = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer_gs[idx], 
                                                   width_ratios=[0.06, 0.94])
        
        # Month label subplot
        label_ax = plt.subplot(month_gs[0])
        label_ax.text(1.0, 0.5, f"{month_books.iloc[0].finish_date.strftime('%B')}", 
                     ha='right', va='center', fontsize=10)
        label_ax.set_xticks([])
        label_ax.set_yticks([])
        label_ax.axis('off')
        
        # Books grid subplot with minimal spacing
        books_gs = gridspec.GridSpecFromSubplotSpec(rows, cols, subplot_spec=month_gs[1],
                                                   hspace=0.02, wspace=0.02)

        # Plot book covers
        for book_idx, book in enumerate(month_books.itertuples()):
            row = book_idx // cols
            col = book_idx % cols
            
            book_ax = plt.subplot(books_gs[row, col])
            cover_path = covers_path / f"{book.book_id}.jpg"
            
            if cover_path.exists():
                img = mpimg.imread(cover_path)
                book_ax.imshow(img, aspect='equal')
            else:
                book_ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor='lightgray'))
            
            book_ax.set_xticks([])
            book_ax.set_yticks([])
            book_ax.set_frame_on(False)
            book_ax.set_aspect('equal')

    plt.suptitle(title, y=0.99, fontsize=14, fontweight='bold')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a monthly grid visualization of book covers')
    parser.add_argument('-c', '--csv', type=str,
                       default='goodreads_library_export.csv',
                       help='Path to the enhanced GoodReads CSV file (default: goodreads_library_export.csv)')
    parser.add_argument('-y', '--year', type=int,
                       default=datetime.now().year,
                       help=f'Year to create grid for (default: {datetime.now().year})')
    parser.add_argument('-d', '--covers-dir', type=str,
                       default='./book_covers',
                       help='Directory containing book covers (default: ./book_covers)')
    parser.add_argument('-t', '--title', type=str,
                       default=None,
                       help='Title for the plot (default: {year} Reading)')
    
    args = parser.parse_args()
    create_monthly_book_grid(args.csv, args.year, args.covers_dir, args.title)