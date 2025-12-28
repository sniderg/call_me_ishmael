
import os
import glob

def generate_index(output_dir="book_output"):
    html_files = sorted(glob.glob(os.path.join(output_dir, "chunk_*.html")))
    
    list_items = ""
    for file_path in html_files:
        filename = os.path.basename(file_path)
        chunk_id = filename.replace("chunk_", "").replace(".html", "")
        list_items += f'<li><a href="{filename}">Part {chunk_id}</a></li>\n'

    index_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Moby Dick - Daily Chunks</title>
        <style>
            body {{ font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; background: #fdf6e3; color: #333; }}
            h1 {{ border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ margin: 10px 0; }}
            a {{ text-decoration: none; color: #d35400; font-weight: bold; font-size: 1.1em; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>Call Me Ishmael: Moby Dick Daily</h1>
        <p>A daily reading of Herman Melville's classic.</p>
        <ul>
            {list_items}
        </ul>
    </body>
    </html>
    """
    
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"Generated {os.path.join(output_dir, 'index.html')}")

if __name__ == "__main__":
    generate_index()
