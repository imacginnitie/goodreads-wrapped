from bs4 import BeautifulSoup
import requests
import re
from pathlib import Path
import time
import argparse

def download_covers(html_path: str, output_dir: str = "book_covers"):
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Read the HTML file
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all book review divs
    for review in soup.find_all('div', class_='bookalike review'):
        try:
            # Find the book URL and extract ID
            book_link = review.find('a', href=re.compile(r'/book/show/\d+'))
            if not book_link:
                continue
                
            # Extract the book ID from the URL
            book_id = re.search(r'/book/show/(\d+)', book_link['href']).group(1)
                
            # Find cover image
            cover_img = review.find('img', id=lambda x: x and x.startswith('cover_review_'))
            if not cover_img or 'src' not in cover_img.attrs:
                continue
                
            url = cover_img['src']
            
            # Handle relative URLs (when HTML is saved with local files)
            if url.startswith('./') or not url.startswith('http'):
                # Try to find the actual image file in the saved files directory
                html_dir = Path(html_path).parent
                saved_files_dir = html_dir / f"{Path(html_path).stem}_files"
                local_file = saved_files_dir / url.replace('./', '').replace(f"{Path(html_path).stem}_files/", '')
                
                if local_file.exists():
                    # Copy the local file instead of downloading
                    import shutil
                    output_file = output_path / f"{book_id}.jpg"
                    if not output_file.exists():
                        print(f"Copying {book_id}.jpg from saved files")
                        shutil.copy2(local_file, output_file)
                    else:
                        print(f"Skipping {book_id}.jpg - already exists")
                    continue
                else:
                    # Fallback: try to construct GoodReads URL (may not work due to CDN restrictions)
                    print(f"Warning: Could not find local file for {book_id}, skipping (HTML was saved with relative paths)")
                    continue
            else:
                # Convert to high resolution by removing size constraint
                url = re.sub(r'_SX\d+_', '_', url)
                # Also try removing other size constraints
                url = re.sub(r'\._\.jpg$', '.jpg', url)
            
            # Define output path for this book
            output_file = output_path / f"{book_id}.jpg"
            
            # Skip if file already exists
            if output_file.exists():
                print(f"Skipping {book_id}.jpg - already exists")
                continue
            
            # Download the image with browser-like headers
            print(f"Downloading {book_id}.jpg from {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.goodreads.com/'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Save the image
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            # Be nice to Goodreads servers
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing book {book_id if 'book_id' in locals() else 'unknown'}: {str(e)}")
            continue
            
    print("Download complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download book covers from a GoodReads HTML export')
    parser.add_argument('-i', '--html', type=str,
                       default='goodreads_list.html',
                       help='Path to the GoodReads HTML export file (default: goodreads_list.html)')
    parser.add_argument('-o', '--output-dir', type=str,
                       default='book_covers',
                       help='Directory to save cover images (default: book_covers)')
    
    args = parser.parse_args()
    download_covers(args.html, args.output_dir)