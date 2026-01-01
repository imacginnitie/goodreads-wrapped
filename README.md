# Enhance GoodReads Export - 2025 Workflow

This repository contains an enhanced version of the [Enhance GoodReads Export](https://github.com/PaulKlinger/Enhance-GoodReads-Export) tool, with additional scripts for downloading book covers, creating visualizations, and generating reading statistics.

## Overview

The original tool adds reading dates and genres to your GoodReads export. This enhanced version adds:
- Book cover downloading and management
- Reading journey animated GIF
- Reading heatmap visualization
- Monthly book cover grids
- Cover availability checking

### Example Outputs

| Reading Journey GIF | Reading Heatmap | Monthly Cover Grid |
|---------------------|-----------------|-------------------|
| ![Reading Journey](reading_journey_2025.gif) | ![Reading Heatmap](reading_heatmap_2025.png) | ![Monthly Grid](reading_plot_2025.png) |

## Prerequisites

- Python 3.12+
- All dependencies from `requirements/requirements.txt`
- A GoodReads account with exported library data

## Setup

1. Install dependencies:
```bash
python -m pip install -r requirements/requirements.txt
```

2. Ensure you have the following directories:
   - `book_covers/` - for storing downloaded book cover images

## Complete Workflow for 2025

### Step 1: Export Your GoodReads Data

1. **Export CSV from GoodReads:**
   - Go to GoodReads → My Books → Import and export
   - Click "Export Library" to download `goodreads_library_export.csv`

2. **Export HTML List for 2025 Books:**
   - Go to your GoodReads reading list
   - Filter by: Date Added = 2025, Shelf = read, View = covers
   - Save the page as HTML: `goodreads_list_2025.html`
   - (Alternatively, use browser developer tools to save the full HTML)

### Step 2: Enhance the CSV Export

Run the original enhancement tool to add reading dates and genres:

```bash
python -m enhance_goodreads_export -c goodreads_library_export.csv
```

This will add two columns:
- `read_dates`: Reading sessions in format "START_DATE,END_DATE;START_DATE,END_DATE;..."
- `genres`: Book genres with vote counts

### Step 3: Create 2025-Specific CSV

Filter the enhanced export for 2025 books. You can do this manually or create a script to filter by finish dates in 2025. Save as `goodreads_library_export_2025.csv`.

**Quick Python filter:**
```python
import pandas as pd

# Read the enhanced export
df = pd.read_csv('goodreads_library_export.csv')

# Filter for books finished in 2025
# (You'll need to parse read_dates to check finish dates)
# Save filtered version
df_2025 = # ... your filtering logic ...
df_2025.to_csv('goodreads_library_export_2025.csv', index=False)
```

### Step 4: Download Book Covers

Use `covers.py` to download covers from the HTML export:

```bash
python covers.py -i goodreads_list_2025.html
```

Or use the default filename:
```bash
python covers.py
```

The script will:
- Parse the HTML file for book IDs and cover image URLs
- Download high-resolution covers
- Save them as `{book_id}.jpg` in the `book_covers/` directory
- Skip already-downloaded covers

**Command-line options:**
- `-i, --html`: Path to HTML file (default: `goodreads_list.html`)
- `-o, --output-dir`: Directory to save covers (default: `book_covers`)

### Step 5: Check for Missing Covers

Run `cover_checker.py` to identify any books from 2025 that are missing cover images:

```bash
python cover_checker.py -c goodreads_library_export.csv -y 2025
```

The script will print a list of books missing covers, including their Book ID, title, author, and finish date.

**Command-line options:**
- `-c, --csv`: Path to CSV file (default: `goodreads_library_export.csv`)
- `-y, --year`: Year to check (default: current year)
- `-d, --covers-dir`: Directory containing covers (default: `./book_covers`)

### Step 6: Generate Visualizations

#### Reading Journey GIF

Create an animated GIF showing all books read in 2025 in chronological order:

```bash
python book_gif.py -c goodreads_library_export.csv -y 2025
```

Output: `reading_journey_2025.gif` (or custom filename with `-o`)

![Reading Journey GIF](reading_journey_2025.gif)

**Command-line options:**
- `-c, --csv`: Path to CSV file (default: `goodreads_library_export.csv`)
- `-y, --year`: Year to create animation for (default: current year)
- `-o, --output`: Output GIF filename (default: `reading_journey_{year}.gif`)
- `-d, --covers-dir`: Directory containing covers (default: `./book_covers`)
- `-f, --frame-duration`: Frame duration in milliseconds (default: 300)

#### Reading Heatmap

Create a GitHub-style heatmap showing reading activity throughout 2025:

```bash
python reading-heatmap.py -c goodreads_library_export.csv -y 2025
```

![Reading Heatmap](reading_heatmap_2025.png)

**Command-line options:**
- `-c, --csv`: Path to CSV file (default: `goodreads_library_export.csv`)
- `-y, --year`: Year to create heatmap for (default: current year)
- `-n, --name`: Name to use in title (default: `Isabel`)
- `-o, --orientation`: `landscape` or `portrait` (default: `landscape`)

#### Monthly Book Cover Grid

Create a visual grid showing book covers organized by month:

```bash
python plot_covers.py -c goodreads_library_export.csv -y 2025
```

![Monthly Book Cover Grid](reading_plot_2025.png)

**Command-line options:**
- `-c, --csv`: Path to CSV file (default: `goodreads_library_export.csv`)
- `-y, --year`: Year to create grid for (default: current year)
- `-d, --covers-dir`: Directory containing covers (default: `./book_covers`)
- `-t, --title`: Title for the plot (default: `{year} Reading`)

## Scripts Reference

### `covers.py`
Downloads book covers from a GoodReads HTML export file.
- **Input:** GoodReads HTML export file
- **Output:** Cover images in `book_covers/` directory
- **Usage:** `python covers.py -i goodreads_list_2025.html`
- **Options:**
  - `-i, --html`: HTML file path (default: `goodreads_list.html`)
  - `-o, --output-dir`: Output directory (default: `book_covers`)

### `cover_checker.py`
Checks which books from a specific year are missing cover images.
- **Input:** Enhanced CSV file
- **Output:** Console list of missing covers
- **Usage:** `python cover_checker.py -c goodreads_library_export.csv -y 2025`
- **Options:**
  - `-c, --csv`: CSV file path (default: `goodreads_library_export.csv`)
  - `-y, --year`: Year to check (default: current year)
  - `-d, --covers-dir`: Covers directory (default: `./book_covers`)

### `book_gif.py`
Creates an animated GIF of book covers in reading order.
- **Input:** Enhanced CSV file with `read_dates` column
- **Output:** `reading_journey_{year}.gif`
- **Usage:** `python book_gif.py -c goodreads_library_export.csv -y 2025`
- **Options:**
  - `-c, --csv`: CSV file path (default: `goodreads_library_export.csv`)
  - `-y, --year`: Year for animation (default: current year)
  - `-o, --output`: Output filename (default: `reading_journey_{year}.gif`)
  - `-d, --covers-dir`: Covers directory (default: `./book_covers`)
  - `-f, --frame-duration`: Frame duration in ms (default: 300)

### `reading-heatmap.py`
Generates a GitHub-style heatmap of reading activity.
- **Input:** Enhanced CSV file with `read_dates` column
- **Output:** Matplotlib heatmap visualization
- **Usage:** `python reading-heatmap.py -c goodreads_library_export.csv -y 2025`
- **Options:**
  - `-c, --csv`: CSV file path (default: `goodreads_library_export.csv`)
  - `-y, --year`: Year for heatmap (default: current year)
  - `-n, --name`: Name for title (default: `Isabel`)
  - `-o, --orientation`: `landscape` or `portrait` (default: `landscape`)

### `plot_covers.py`
Creates a monthly grid visualization of book covers.
- **Input:** Enhanced CSV file with `read_dates` column
- **Output:** Matplotlib grid visualization
- **Usage:** `python plot_covers.py -c goodreads_library_export.csv -y 2025`
- **Options:**
  - `-c, --csv`: CSV file path (default: `goodreads_library_export.csv`)
  - `-y, --year`: Year for grid (default: current year)
  - `-d, --covers-dir`: Covers directory (default: `./book_covers`)
  - `-t, --title`: Plot title (default: `{year} Reading`)

## File Structure

```
.
├── book_covers/              # Downloaded book cover images
├── covers.py                 # Cover downloader script
├── cover_checker.py          # Missing cover checker
├── book_gif.py              # Reading journey GIF generator
├── reading-heatmap.py       # Reading heatmap generator
├── plot_covers.py           # Monthly cover grid generator
├── goodreads_library_export.csv          # Original export (enhanced)
├── goodreads_library_export_2025.csv    # 2025-filtered export
├── goodreads_list_2025.html             # HTML export for covers
├── reading_journey.gif                  # Generated animation
└── enhance_goodreads_export/            # Original tool package
```

## Quick Checklist for 2025

- [ ] Export `goodreads_library_export.csv` from GoodReads
- [ ] Export `goodreads_list_2025.html` (filtered for 2025 books)
- [ ] Run `python -m enhance_goodreads_export -c goodreads_library_export.csv`
- [ ] Run `python covers.py -i goodreads_list_2025.html` to download covers
- [ ] Run `python cover_checker.py -c goodreads_library_export.csv -y 2025` to check for missing covers
- [ ] Run `python book_gif.py -c goodreads_library_export.csv -y 2025` to generate GIF
- [ ] Run `python reading-heatmap.py -c goodreads_library_export.csv -y 2025` to generate heatmap
- [ ] Run `python plot_covers.py -c goodreads_library_export.csv -y 2025` to generate monthly grid

## Notes

- The original enhancement tool may take a while to process all books, as it scrapes GoodReads pages
- Cover downloads include a 1-second delay between requests to be respectful to GoodReads servers
- All scripts now accept command-line arguments - no need to edit the code! Just pass `-y 2025` (or any year) to specify the year
- The `read_dates` format supports multiple reading sessions per book (re-reads)
- Missing covers will show as gray placeholders in visualizations
- All scripts default to the current year if no year is specified

## Original Tool

This project extends the [Enhance GoodReads Export](https://github.com/PaulKlinger/Enhance-GoodReads-Export) tool by PaulKlinger, which adds reading dates and genres to GoodReads library exports.
