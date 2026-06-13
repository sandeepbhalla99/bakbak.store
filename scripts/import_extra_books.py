import os
import re
import json
import shutil

OUTPUT_DIR = "/home/sb/AI-Works/docx2convert/output"
BAKBAK_BOOKS_DIR = "/home/sb/AI-Works/bakbak.store/books"

def normalize_title(title):
    # Convert Chapter Ii -> Chapter II, Act I, Scene 1
    def uppercase_roman(match):
        return match.group(1) + match.group(2).upper()
    return re.sub(r'(?i)\b(Chapter|Act|Scene|Part)\s+([ivxlcdm]+)\b', uppercase_roman, title)

def import_book(config):
    src_dir = os.path.join(OUTPUT_DIR, config["folder"])
    dest_dir = os.path.join(BAKBAK_BOOKS_DIR, config["id"])
    
    if not os.path.exists(src_dir):
        print(f"Source folder {src_dir} not found. Skipping.")
        return False
        
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
        
    chapters_dir = os.path.join(dest_dir, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)
    
    # Parse chapters
    chapter_mappings = []
    index_path = os.path.join(src_dir, config["index_file"])
    if not os.path.exists(index_path):
        print(f"Index {index_path} not found. Skipping.")
        return False
        
    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            if config.get("is_wiki_index"):
                # Wiki link format: ## [[01_Introduction_Section|Introduction_Section]]
                match = re.search(r'\[\[(.*?)(?:\|(.*?))?\]\]', line)
                if match:
                    src_file = match.group(1).strip() + ".md"
                    title = match.group(2).strip() if match.group(2) else match.group(1).strip()
                    title = title.replace("_", " ")
                    chapter_mappings.append((title, src_file))
            else:
                # Markdown link format: - [Title](file.md)
                match = re.search(r'-\s*\[(.*?)\]\((.*?)\)', line)
                if match:
                    title = match.group(1).strip()
                    src_file = match.group(2).strip()
                    chapter_mappings.append((title, src_file))
                    
    print(f"Parsed {len(chapter_mappings)} chapters for {config['title']}")
    
    # Process files
    chapters_list = []
    processed_chapters = []
    
    # Offset by 2 (so index is 01, and actual chapters start at 02)
    for idx, (title, src_file) in enumerate(chapter_mappings):
        clean_name = re.sub(r'^\d+_', '', src_file)
        dest_filename = f"{idx+2:02d}_{clean_name}"
        processed_chapters.append({
            "title": normalize_title(title),
            "src_file": src_file,
            "dest_file": dest_filename
        })
        
    # Generate 01_Index.md
    intro_filename = "01_Index.md"
    intro_markdown = f"""# Index

<div style="text-align: center; margin-bottom: 2.5rem; padding-top: 1rem;">
  <h1 style="font-size: 2.25rem; margin-bottom: 0.5rem; font-weight: 800; color: var(--text-main); line-height: 1.2;">{config['title']}</h1>
  <p style="font-size: 1.25rem; color: var(--text-muted); font-style: italic; margin-top: 0.5rem;">by {config['author']}</p>
</div>

<hr style="border: 0; border-top: 1px solid var(--border-color); margin: 2rem 0; opacity: 0.5;">

<div class="toc-container" style="max-width: 550px; margin: 0 auto; padding: 0 10px;">
  <h3 style="text-align: center; margin-bottom: 1.5rem; letter-spacing: 0.08em; text-transform: uppercase; font-size: 1.1rem; font-weight: 700; color: var(--text-main);">Table of Contents</h3>
  <ul style="list-style: none; padding: 0; margin: 0; line-height: 2;">
"""

    for idx, chap in enumerate(processed_chapters):
        c_title = chap["title"]
        c_file = chap["dest_file"]
        intro_markdown += f'    <li style="margin-bottom: 0.85rem; border-bottom: 1px dashed var(--border-color); padding-bottom: 0.35rem;"><a href="{c_file}" style="color: var(--accent); text-decoration: none; font-weight: 500; display: flex; justify-content: space-between; align-items: baseline;"><span>{c_title}</span></a></li>\n'

    intro_markdown += """  </ul>
</div>

"""

    # Write 01_Index.md
    with open(os.path.join(chapters_dir, intro_filename), "w", encoding="utf-8") as f:
        f.write(intro_markdown)
        
    chapters_list.append({
        "title": "Index",
        "file": intro_filename
    })
    
    # Copy chapter files
    for chap in processed_chapters:
        src_path = os.path.join(src_dir, chap["src_file"])
        dest_path = os.path.join(chapters_dir, chap["dest_file"])
        
        if os.path.exists(src_path):
            with open(src_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Normalize title inside content if applicable
            content = normalize_title(content)
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            print(f"Warning: chapter file {src_path} not found!")
            
        chapters_list.append({
            "title": chap["title"],
            "file": chap["dest_file"]
        })
        
    # Copy cover image if configured
    cover_image_path = None
    if config.get("cover_image_src"):
        src_cover = os.path.join(src_dir, config["cover_image_src"])
        if os.path.exists(src_cover):
            shutil.copy(src_cover, os.path.join(dest_dir, "cover.jpg"))
            cover_image_path = f"books/{config['id']}/cover.jpg"
            print(f"Copied cover image for {config['title']}")
            
    # Write details.json
    details = {
        "id": config["id"],
        "title": config["title"],
        "author": config["author"],
        "genre": config["genre"],
        "coverColor": config["cover_color"],
        "description": config["description"],
        "chapters": chapters_list
    }
    if cover_image_path:
        details["coverImage"] = cover_image_path
        
    with open(os.path.join(dest_dir, "details.json"), "w", encoding="utf-8") as f:
        json.dump(details, f, indent=2)
        
    print(f"Successfully imported {config['title']}!")
    return True

def main():
    books_to_import = [
        {
            "id": "the-adventures-of-sherlock-holmes",
            "folder": "The_Adventures_of_Sherlock_Holmes",
            "index_file": "index.md",
            "title": "The Adventures of Sherlock Holmes",
            "author": "Arthur Conan Doyle",
            "genre": "Mystery",
            "cover_color": "linear-gradient(135deg, #4b5563 0%, #1f2937 100%)",
            "description": "A collection of twelve detective stories featuring Arthur Conan Doyle's famous consulting detective Sherlock Holmes.",
            "is_wiki_index": False
        },
        {
            "id": "complete-works-of-william-shakespeare",
            "folder": "William_Shakespeare",
            "index_file": "index.md",
            "title": "The Complete Works of William Shakespeare",
            "author": "William Shakespeare",
            "genre": "Classics",
            "cover_color": "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)",
            "cover_image_src": "cover-shakespeare.jpg",
            "description": "The complete works of William Shakespeare, including all his plays, sonnets, and poems.",
            "is_wiki_index": False
        },
        {
            "id": "evolution-of-the-constitution",
            "folder": "Evolution of Constitution",
            "index_file": "00_Index.md",
            "title": "The Evolution of the Constitution",
            "author": "K.P. Tewari",
            "genre": "History",
            "cover_color": "linear-gradient(135deg, #0d9488 0%, #0f766e 100%)",
            "description": "An in-depth study of the historical evolution of constitutional development and law.",
            "is_wiki_index": True
        }
    ]
    
    for book in books_to_import:
        import_book(book)

if __name__ == "__main__":
    main()
