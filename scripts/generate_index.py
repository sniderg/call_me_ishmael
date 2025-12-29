
import os
import glob

def generate_index(output_dir="book_output"):
    # 1. Find all book directories
    book_dirs = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    
    book_links = ""
    
    for book_id in book_dirs:
        # Skip if it's not a book folder
        book_path = os.path.join(output_dir, book_id)
        
        # Load Manifest if available
        import json
        manifest = {}
        manifest_path = os.path.join(book_path, "manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest_list = json.load(f)
                    # Convert list to dict for lookup: {1: ["Ch1"], 2: ...}
                    manifest = {item["chunk_id"]: item["chapters"] for item in manifest_list}
            except Exception as e:
                print(f"Warning: Failed to load manifest for {book_id}: {e}")
        
        # 2. Generate Index for THIS Book
        html_files = sorted(glob.glob(os.path.join(book_path, "chunk_*.html")))
        if not html_files:
            continue
            
        list_items = ""
        for file_path in html_files:
            filename = os.path.basename(file_path)
            chunk_id_str = filename.replace("chunk_", "").replace(".html", "")
            chunk_id = int(chunk_id_str)
            
            # Get chapter info
            chapters = manifest.get(chunk_id, [])
            chapter_text = ""
            if chapters:
                chapter_text = f' <span class="chapters">({", ".join(chapters)})</span>'
            
            list_items += f'<li><a href="chunk_{chunk_id_str}" class="part-link">Part {chunk_id_str}</a>{chapter_text}</li>\n'
            
        book_title = book_id.replace("_", " ").title()
        
        book_index_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{book_title} - Daily Chunks</title>
            <style>
                :root {{
                    --bg-color: #fdf6e3;
                    --card-bg: #ffffff;
                    --text-color: #2c3e50;
                    --accent-color: #d35400;
                    --link-color: #2980b9;
                    --border-color: #ecf0f1;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    background-color: var(--bg-color);
                    color: var(--text-color);
                    margin: 0;
                    padding: 20px;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: var(--card-bg);
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                }}
                h1 {{
                    font-family: Georgia, serif;
                    color: var(--text-color);
                    border-bottom: 2px solid var(--border-color);
                    padding-bottom: 15px;
                    margin-top: 0;
                }}
                .toc-list {{
                    list-style: none;
                    padding: 0;
                    margin-top: 30px;
                }}
                .toc-item {{
                    border-bottom: 1px solid var(--border-color);
                    padding: 15px 0;
                    display: flex;
                    flex-direction: column;
                }}
                .toc-item:last-child {{ border-bottom: none; }}
                .part-link {{
                    font-weight: 700;
                    text-decoration: none;
                    color: var(--link-color);
                    font-size: 1.1em;
                    margin-bottom: 4px;
                }}
                .part-link:hover {{ color: var(--accent-color); text-decoration: underline; }}
                .chapters {{
                    font-size: 0.9em;
                    color: #7f8c8d;
                    font-style: italic;
                }}
                .back-link {{
                    display: inline-block;
                    margin-top: 30px;
                    color: #7f8c8d;
                    text-decoration: none;
                    font-weight: 500;
                }}
                .back-link:hover {{ color: var(--text-color); }}
                
                @media (max-width: 600px) {{
                    .container {{ padding: 20px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{book_title}</h1>
                <p>Table of Contents</p>
                <ul class="toc-list">
                    {list_items}
                </ul>
                <a href="../" class="back-link">← Back to Library</a>
            </div>
        </body>
        </html>
        """
        
        with open(os.path.join(book_path, "index.html"), "w", encoding="utf-8") as f:
            f.write(book_index_html)
        print(f"Generated index for {book_id}")
        
        # Add to main library list
        # Optionally show book author or chunk count here if we wanted
        book_links += f'<a href="{book_id}/" class="book-card"><h3>{book_title}</h3><span class="arrow">→</span></a>\n'

    # 3. Generate Root Library Index
    root_index_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Call Me Ishmael - Library</title>
        <style>
            :root {{
                --bg-color: #fdf6e3;
                --card-bg: #ffffff;
                --text-color: #2c3e50;
                --accent-color: #d35400;
                --hover-bg: #f8f9fa;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 40px 20px;
                line-height: 1.6;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
            }}
            header {{
                text-align: center;
                margin-bottom: 50px;
            }}
            h1 {{
                font-family: Georgia, serif;
                font-size: 2.5em;
                margin-bottom: 10px;
                color: var(--text-color);
            }}
            .subtitle {{
                color: #7f8c8d;
                font-size: 1.1em;
            }}
            .book-list {{
                display: flex;
                flex-direction: column;
                gap: 15px;
            }}
            .book-card {{
                background: var(--card-bg);
                padding: 20px 30px;
                border-radius: 12px;
                text-decoration: none;
                color: var(--text-color);
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                transition: transform 0.2s, box-shadow 0.2s;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .book-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 15px rgba(0,0,0,0.1);
            }}
            .book-card h3 {{
                margin: 0;
                font-size: 1.2em;
                font-weight: 600;
            }}
            .arrow {{
                color: #bdc3c7;
                font-size: 1.5em;
                transition: color 0.2s;
            }}
            .book-card:hover .arrow {{
                color: var(--accent-color);
            }}
            .footer {{
                margin-top: 60px;
                text-align: center;
                font-size: 0.9em;
                color: #95a5a6;
            }}
            .footer a {{
                color: #7f8c8d;
                text-decoration: none;
                border-bottom: 1px dotted #95a5a6;
            }}
            .footer a:hover {{
                color: var(--accent-color);
                border-bottom: 1px solid var(--accent-color);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Call Me Ishmael</h1>
                <div class="subtitle">Your daily reading companion.</div>
            </header>
            
            <div class="book-list">
                {book_links}
            </div>
            
            <div class="footer">
                <p>Project by Graydon Snider. <a href="https://github.com/sniderg/call_me_ishmael">View Source on GitHub</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(root_index_html)
    print(f"Generated root library index")

if __name__ == "__main__":
    generate_index()
