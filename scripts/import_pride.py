import os
import re
import json
import shutil

SOURCE_DIR = "/home/sb/AI-Works/docx2convert/output/Pride_and_Prejudice"
DEST_DIR = "/home/sb/AI-Works/bakbak.store/books/pride-and-prejudice"

def normalize_title(title):
    # Convert Chapter Ii -> Chapter II, Chapter Xlvi -> Chapter XLVI
    def uppercase_roman(match):
        return "Chapter " + match.group(1).upper()
    return re.sub(r'(?i)^Chapter\s+([ivxlcdm]+)$', uppercase_roman, title)

def main():
    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory {SOURCE_DIR} does not exist!")
        return

    # Delete existing target dir if it exists
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
        print("Deleted existing pride-and-prejudice directory.")

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
                normalized = normalize_title(title)
                chapter_mappings.append((normalized, filename))

    print(f"Parsed {len(chapter_mappings)} chapters from index.md")

    # We will generate details.json chapters list
    # The first chapter is 01_Introduction.md (which contains the TOC)
    # The second is 02_preface.md, etc.
    chapters_list = []
    
    # 1. First, prepare the list of actual chapters to be written
    # We need to know filenames in advance to build the TOC inside Introduction.md
    processed_chapters = []
    
    # Index 1 is Introduction, but in the final chapters list it's idx 0
    # Let's collect all subsequent chapters first
    for idx, (title, src_file) in enumerate(chapter_mappings):
        dest_filename = f"{idx+2:02d}_{src_file}" # start at 02
        processed_chapters.append({
            "title": title,
            "src_file": src_file,
            "dest_file": dest_filename
        })

    # 2. Generate Index.md
    intro_filename = "01_Index.md"
    intro_title = "Index"
    
    intro_markdown = f"""# Index

<div style="text-align: center; margin-bottom: 2.5rem; padding-top: 1rem;">
  <h1 style="font-size: 2.25rem; margin-bottom: 0.5rem; font-weight: 800; color: var(--text-main); line-height: 1.2;">Pride and Prejudice</h1>
  <p style="font-size: 1.25rem; color: var(--text-muted); font-style: italic; margin-top: 0.5rem;">by Jane Austen</p>
</div>

<hr style="border: 0; border-top: 1px solid var(--border-color); margin: 2rem 0; opacity: 0.5;">

<div class="toc-container" style="max-width: 550px; margin: 0 auto; padding: 0 10px;">
  <h3 style="text-align: center; margin-bottom: 1.5rem; letter-spacing: 0.08em; text-transform: uppercase; font-size: 1.1rem; font-weight: 700; color: var(--text-main);">Table of Contents</h3>
  <ul style="list-style: none; padding: 0; margin: 0; line-height: 2;">
"""

    for idx, chap in enumerate(processed_chapters):
        c_title = chap["title"]
        c_file = chap["dest_file"]
        # Label could be "Preface" or "Chapter X"
        label = "Preface" if c_title.lower() == "preface" else f"Chapter {idx}"
        intro_markdown += f'    <li style="margin-bottom: 0.85rem; border-bottom: 1px dashed var(--border-color); padding-bottom: 0.35rem;"><a href="{c_file}" style="color: var(--accent); text-decoration: none; font-weight: 500; display: flex; justify-content: space-between; align-items: baseline;"><span>{c_title}</span> <span style="color: var(--text-muted); font-size: 0.85rem; font-weight: 400; padding-left: 10px; text-align: right;">{label}</span></a></li>\n'

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


    # 3. Copy other chapters
    for chap in processed_chapters:
        src_path = os.path.join(SOURCE_DIR, chap["src_file"])
        dest_path = os.path.join(chapters_dir, chap["dest_file"])
        
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Clean title in the file itself (e.g. "# Chapter Ii" -> "# Chapter II")
        content = re.sub(r'^#\s+Chapter\s+([ivxlcdm]+)$', lambda m: "# Chapter " + m.group(1).upper(), content, flags=re.IGNORECASE | re.MULTILINE)
        
        # Write to destination
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        chapters_list.append({
            "title": chap["title"],
            "file": chap["dest_file"]
        })

    # 4. Write details.json
    details = {
      "id": "pride-and-prejudice",
      "title": "Pride and Prejudice",
      "author": "Jane Austen",
      "genre": "Classics",
      "coverColor": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
      "coverImage": "books/pride-and-prejudice/cover.jpg",
      "description": "A classic masterpiece by Jane Austen. Read this cleaned edition on Bakbak.store.",
      "chapters": chapters_list
    }
    
    details_path = os.path.join(DEST_DIR, "details.json")
    with open(details_path, "w", encoding="utf-8") as f:
        json.dump(details, f, indent=2)

    # Copy cover.jpg if exists in source
    src_cover = os.path.join(SOURCE_DIR, "cover.jpg")
    dest_cover = os.path.join(DEST_DIR, "cover.jpg")
    if os.path.exists(src_cover):
        shutil.copy(src_cover, dest_cover)
        print("Copied cover.jpg to destination.")

    print("Successfully imported Pride and Prejudice with clean chapters!")

if __name__ == "__main__":
    main()

