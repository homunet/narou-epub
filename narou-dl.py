#!/usr/bin/env python3
"""
narou-dl.py - Download and combine novel chapters from ncode.syosetu.com
Usage: python narou-dl.py <novel_code> <start_episode> <end_episode>
Example: python narou-dl.py n9669bk 1 10
"""

import sys
import time
import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path

def download_page(url, retry_count=3, delay=1):
    """Download a page with retry logic and delay to avoid 403 errors"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for attempt in range(retry_count):
        try:
            # Add delay between requests to avoid rate limiting
            time.sleep(delay)
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < retry_count - 1:
                time.sleep(delay * (attempt + 2))  # Increase delay on retry
            else:
                raise

def extract_novel_info(html_content):
    """Extract novel title and author from the first page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract title
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text()
        # Remove ' - ' and everything after it
        if ' - ' in title_text:
            novel_title = title_text.split(' - ')[0].strip()
        else:
            novel_title = title_text.strip()
    else:
        novel_title = "Unknown Title"
    
    # Extract author
    author_meta = soup.find('meta', attrs={'name': 'twitter:creator'})
    if author_meta and author_meta.get('content'):
        novel_author = author_meta['content'].strip()
    else:
        novel_author = "Unknown Author"
    
    return novel_title, novel_author

def process_html_content(html_content, episode_num):
    """Process HTML to keep only specified elements"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find required elements
    episode_number_div = soup.find('div', class_='p-novel__number')
    h1_tag = soup.find('h1')
    body_div = soup.find('div', class_='p-novel__body')
    
    # Get episode number content
    episode_number_text = ""
    if episode_number_div:
        episode_number_text = episode_number_div.get_text(strip=True)
    
    # Insert episode number before h1 content if h1 exists
    if h1_tag and episode_number_text:
        original_h1_text = h1_tag.get_text(strip=True)
        # Clear h1 content and add new formatted content
        h1_tag.clear()
        h1_tag.string = f"{episode_number_text}\u00A0{original_h1_text}"
    
    # Create new soup with only required elements
    new_soup = BeautifulSoup('<div class="chapter"></div>', 'html.parser')
    chapter_div = new_soup.find('div', class_='chapter')
    
    if h1_tag:
        chapter_div.append(h1_tag)
    
    if body_div:
        chapter_div.append(body_div)
    
    return str(chapter_div)

def combine_chapters(processed_chapters, novel_title, novel_author, novel_code, start_ep, end_ep):
    """Combine all processed chapters into a single HTML file"""
    html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="{novel_author}">
    <title>{novel_title}:{start_ep}-{end_ep}</title>
    <style>
        body {{
            font-family: 'Noto Sans JP', sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            font-size: 1.5em;
            margin: 2em 0 1em 0;
            border-bottom: 1px solid #ddd;
            padding-bottom: 0.5em;
        }}
        .p-novel__body {{
            margin-bottom: 3em;
        }}
        .chapter {{
            margin-bottom: 4em;
        }}
    </style>
</head>
<body>
    <h1>{novel_title}</h1>
    <p>著者: {novel_author}</p>
    <hr>
"""
    
    # Add all chapters
    for chapter in processed_chapters:
        html_template += chapter + "\n"
    
    html_template += """
</body>
</html>"""
    
    return html_template

def main():
    # Check command line arguments
    if len(sys.argv) != 4:
        print("Usage: python narou-dl.py <novel_code> <start_episode> <end_episode>")
        print("Example: python narou-dl.py n9669bk 1 10")
        sys.exit(1)
    
    novel_code = sys.argv[1]
    try:
        start_episode = int(sys.argv[2])
        end_episode = int(sys.argv[3])
    except ValueError:
        print("Error: Start and end episodes must be integers")
        sys.exit(1)
    
    if start_episode > end_episode:
        print("Error: Start episode must be less than or equal to end episode")
        sys.exit(1)
    
    print(f"Downloading novel {novel_code} from episode {start_episode} to {end_episode}")
    
    processed_chapters = []
    novel_title = ""
    novel_author = ""
    
    # Download and process each episode
    for episode in range(start_episode, end_episode + 1):
        url = f"https://ncode.syosetu.com/{novel_code}/{episode}/"
        print(f"Downloading episode {episode}...")
        
        try:
            html_content = download_page(url)
            
            # Extract novel info from first page
            if episode == start_episode:
                novel_title, novel_author = extract_novel_info(html_content)
                print(f"Novel: {novel_title}")
                print(f"Author: {novel_author}")
            
            # Process the HTML content
            processed_content = process_html_content(html_content, episode)
            processed_chapters.append(processed_content)
            
            print(f"Episode {episode} downloaded and processed successfully")
            
        except Exception as e:
            print(f"Error downloading episode {episode}: {e}")
            sys.exit(1)
    
    # Combine all chapters
    print("Combining all chapters...")
    combined_html = combine_chapters(processed_chapters, novel_title, novel_author, 
                                   novel_code, start_episode, end_episode)
    
    # Save to file
    output_filename = f"{novel_code}-{start_episode}-{end_episode}.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(combined_html)
    
    print(f"Successfully saved to {output_filename}")
    print(f"Downloaded {end_episode - start_episode + 1} episodes")

if __name__ == "__main__":
    main()
