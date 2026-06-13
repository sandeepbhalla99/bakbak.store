import os
import re
import json
import shutil

SOURCE_DIR = "/home/sb/AI-Works/docx2convert/output/Romeo_and_Juliet"
DEST_DIR = "/home/sb/AI-Works/bakbak.store/books/romeo-and-juliet"

def main():
    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory {SOURCE_DIR} does not exist!")
        return

    # Delete existing target dir if it exists
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
        print("Deleted existing romeo-and-juliet directory.")

    chapters_dir = os.path.join(DEST_DIR, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)

    # Parse index.md to get ordered chapters
    index_file = os.path.join(SOURCE_DIR, "index.md")
    if not os.path.exists(index_file):
        print("index.md not found in source directory!")
        return

    chapter_mappings = []
    with open(index_file, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(r'-\s*\[(.*?)\]\((.*?)\)', line)
            if match:
                title = match.group(1).strip()
                filename = match.group(2).strip()
                chapter_mappings.append((title, filename))

    print(f"Parsed {len(chapter_mappings)} chapters from index.md")

    chapters_list = []
    
    # We will generate 01_Index.md as the first chapter in target
    # Offset subsequent chapters by 2 (so they start at 02)
    processed_chapters = []
    for idx, (title, src_file) in enumerate(chapter_mappings):
        # Strip original numeric prefix from source filename if it exists
        clean_name = re.sub(r'^\d+_', '', src_file)
        dest_filename = f"{idx+2:02d}_{clean_name}" # start at 02
        processed_chapters.append({
            "title": title,
            "src_file": src_file,
            "dest_file": dest_filename
        })

    # Generate 01_Index.md
    intro_filename = "01_Index.md"
    intro_title = "Index"
    
    intro_markdown = f"""# Index

<div style="text-align: center; margin-bottom: 2.5rem; padding-top: 1rem;">
  <h1 style="font-size: 2.25rem; margin-bottom: 0.5rem; font-weight: 800; color: var(--text-main); line-height: 1.2;">Romeo and Juliet</h1>
  <p style="font-size: 1.25rem; color: var(--text-muted); font-style: italic; margin-top: 0.5rem;">by William Shakespeare</p>
</div>

<hr style="border: 0; border-top: 1px solid var(--border-color); margin: 2rem 0; opacity: 0.5;">

<div class="toc-container" style="max-width: 550px; margin: 0 auto; padding: 0 10px;">
  <h3 style="text-align: center; margin-bottom: 1.5rem; letter-spacing: 0.08em; text-transform: uppercase; font-size: 1.1rem; font-weight: 700; color: var(--text-main);">Table of Contents</h3>
  <ul style="list-style: none; padding: 0; margin: 0; line-height: 2;">
"""

    for idx, chap in enumerate(processed_chapters):
        c_title = chap["title"]
        c_file = chap["dest_file"]
        # Determine labels like "Act I, Scene 1"
        intro_markdown += f'    <li style="margin-bottom: 0.85rem; border-bottom: 1px dashed var(--border-color); padding-bottom: 0.35rem;"><a href="{c_file}" style="color: var(--accent); text-decoration: none; font-weight: 500; display: flex; justify-content: space-between; align-items: baseline;"><span>{c_title}</span></a></li>\n'

    intro_markdown += """  </ul>
</div>

"""

    # Write Index chapter file
    intro_path = os.path.join(chapters_dir, intro_filename)
    with open(intro_path, "w", encoding="utf-8") as f:
        f.write(intro_markdown)
        
    chapters_list.append({
        "title": intro_title,
        "file": intro_filename
    })

    # Copy and clean other chapters
    for chap in processed_chapters:
        src_path = os.path.join(SOURCE_DIR, chap["src_file"])
        dest_path = os.path.join(chapters_dir, chap["dest_file"])
        
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Write to destination
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        chapters_list.append({
            "title": chap["title"],
            "file": chap["dest_file"]
        })

    # Write details.json
    details = {
      "id": "romeo-and-juliet",
      "title": "Romeo and Juliet",
      "author": "William Shakespeare",
      "genre": "Drama",
      "coverColor": "linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)",
      "description": "The classic tragedy of star-crossed lovers Romeo and Juliet by William Shakespeare.",
      "chapters": chapters_list
    }
    
    details_path = os.path.join(DEST_DIR, "details.json")
    with open(details_path, "w", encoding="utf-8") as f:
        json.dump(details, f, indent=2)

    print("Successfully imported Romeo and Juliet with clean chapters!")

if __name__ == "__main__":
    main()
