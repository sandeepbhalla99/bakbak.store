import os
import re
import json
import shutil
import datetime
import subprocess

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
        src_cover = config["cover_image_src"]
        if not src_cover.startswith("/"):
            src_cover = os.path.join(src_dir, src_cover)
            
        if os.path.exists(src_cover):
            ext = os.path.splitext(src_cover)[1].lower()
            if not ext:
                ext = ".jpg"
            shutil.copy(src_cover, os.path.join(dest_dir, f"cover{ext}"))
            cover_image_path = f"books/{config['id']}/cover{ext}"
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

def log_activity(action, details):
    log_path = "/home/sb/AI-Works/bakbak.store/activity.log"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {action}\n{details}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"Logged activity to activity.log")

def bump_service_worker():
    sw_path = "/home/sb/AI-Works/bakbak.store/sw.js"
    if not os.path.exists(sw_path):
        print("sw.js not found.")
        return
    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r"const CACHE_NAME = 'bakbak-store-cache-v(\d+)';", content)
    if match:
        old_ver = int(match.group(1))
        new_ver = old_ver + 1
        new_line = f"const CACHE_NAME = 'bakbak-store-cache-v{new_ver}';"
        content = re.sub(r"const CACHE_NAME = 'bakbak-store-cache-v\d+';", new_line, content)
        with open(sw_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Bumped Service Worker cache version from v{old_ver} to v{new_ver}")
        return new_ver
    else:
        print("Could not find CACHE_NAME in sw.js")
        return None

def regenerate_catalog():
    print("Regenerating catalog...")
    try:
        subprocess.run(["python3", "scripts/generate_catalog.py"], check=True)
        print("Catalog regenerated successfully.")
    except Exception as e:
        print(f"Error regenerating catalog: {e}")

def git_push_changes(imported_titles):
    print("Running Git commands...")
    try:
        # git add
        subprocess.run(["git", "add", "books/", "sw.js", "uploaded_books.json", "activity.log"], check=True)
        
        # git commit
        commit_msg = f"Import new books: {', '.join(imported_titles)} and update catalog/sw"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        # git push
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Changes successfully committed and pushed to git!")
    except Exception as e:
        print(f"Git operations failed: {e}")

KNOWN_METADATA = {
    "Around_the_World_in_Eighty_Days": {
        "id": "around-the-world-in-eighty-days",
        "title": "Around the World in Eighty Days",
        "author": "Jules Verne",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #b45309 0%, #78350f 100%)",
        "description": "Jules Verne's classic adventure novel detailing Phileas Fogg's quest to circumnavigate the globe in 80 days.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/around_world_cover_1781747265572.png"
    },
    "I_Am_a_Woman": {
        "id": "i-am-a-woman",
        "title": "I Am a Woman",
        "author": "Unknown Author",
        "genre": "Drama",
        "cover_color": "linear-gradient(135deg, #ec4899 0%, #be185d 100%)",
        "description": "A compelling story exploring personal identity, societal expectations, and emotional courage.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/i_am_woman_cover_1781747290399.png"
    },
    "Sex_life_of_the_gods": {
        "id": "sex-life-of-the-gods",
        "title": "Sex Life of the Gods",
        "author": "Michael Knerr",
        "genre": "Fantasy",
        "cover_color": "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)",
        "description": "A fascinating dive into mythological stories, cosmic conflicts, and the humanlike passions of ancient deities.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/sex_life_gods_cover_1781747312989.png"
    },
    "The_Blue_Lagoon_A_Romance": {
        "id": "the-blue-lagoon-a-romance",
        "title": "The Blue Lagoon: A Romance",
        "author": "H. De Vere Stacpoole",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%)",
        "description": "The timeless romance of two children marooned on a lush South Pacific island, growing up together in nature.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/blue_lagoon_cover_1781747340544.png"
    },
    "The_King_in_Yellow": {
        "id": "the-king-in-yellow",
        "title": "The King in Yellow",
        "author": "Robert W. Chambers",
        "genre": "Horror",
        "cover_color": "linear-gradient(135deg, #eab308 0%, #ca8a04 100%)",
        "description": "A collection of weird fiction stories linked by a play that induces madness in anyone who reads it.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/king_yellow_cover_1781747362504.png"
    },
    "Twenty_Years_After": {
        "id": "twenty-years-after",
        "title": "Twenty Years After",
        "author": "Alexandre Dumas",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%)",
        "description": "Alexandre Dumas' sequel to The Three Musketeers, following D'Artagnan and his companions two decades later.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/twenty_years_after_cover_1781747386108.png"
    },
    "Ulysses": {
        "id": "ulysses",
        "title": "Ulysses",
        "author": "James Joyce",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #6b7280 0%, #374151 100%)",
        "description": "James Joyce's modernist masterpiece, following Leopold Bloom's ordinary day in Dublin.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/ulysses_cover_1781747412280.png"
    },
    "Under_the_Red_Dragon": {
        "id": "under-the-red-dragon",
        "title": "Under the Red Dragon",
        "author": "James Grant",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #dc2626 0%, #991b1b 100%)",
        "description": "An engaging historical military novel filled with action, drama, and romance.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/red_dragon_cover_1781747438335.png"
    },
    # 7 New Books
    "Meditations": {
        "id": "meditations",
        "title": "Meditations",
        "author": "Marcus Aurelius",
        "genre": "Philosophy",
        "cover_color": "linear-gradient(135deg, #78350f 0%, #451a03 100%)",
        "description": "The private writings of the Roman Emperor Marcus Aurelius, offering Stoic philosophy and spiritual reflections.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/meditations_cover_1781703324325.png"
    },
    "Middlemarch": {
        "id": "middlemarch",
        "title": "Middlemarch",
        "author": "George Eliot",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #1e1b4b 0%, #030712 100%)",
        "description": "George Eliot's masterpiece examining the lives and relationships of the inhabitants of a provincial English town.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/middlemarch_cover_1781703341031.png"
    },
    "The_Blue_Castle": {
        "id": "the-blue-castle",
        "title": "The Blue Castle",
        "author": "L. M. Montgomery",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
        "description": "L.M. Montgomery's charming novel about Valancy Stirling, who decides to rebel against her family and find true love.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/blue_castle_cover_1781703359268.png"
    },
    "The_Green_Mummy": {
        "id": "the-green-mummy",
        "title": "The Green Mummy",
        "author": "Fergus Hume",
        "genre": "Mystery",
        "cover_color": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
        "description": "A classic mystery novel by Fergus Hume involving a Peruvian mummy, murder, and hidden secrets.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/green_mummy_cover_1781703379244.png"
    },
    "The_Lady_of_the_Lake": {
        "id": "the-lady-of-the-lake",
        "title": "The Lady of the Lake",
        "author": "Sir Walter Scott",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)",
        "description": "A narrative poem by Sir Walter Scott set in the Trossachs region of Scotland, featuring a clash between clans.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/lady_lake_cover_1781703397392.png"
    },
    "The_Mysteries_of_Udolpho": {
        "id": "the-mysteries-of-udolpho",
        "title": "The Mysteries of Udolpho",
        "author": "Ann Radcliffe",
        "genre": "Horror",
        "cover_color": "linear-gradient(135deg, #111827 0%, #030712 100%)",
        "description": "The quintessential Gothic romance novel by Ann Radcliffe, filled with suspense, castles, and unexplained phenomena.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/mysteries_udolpho_cover_1781703418711.png"
    },
    "The_Secret_of_Chimneys": {
        "id": "the-secret-of-chimneys",
        "title": "The Secret of Chimneys",
        "author": "Agatha Christie",
        "genre": "Mystery",
        "cover_color": "linear-gradient(135deg, #374151 0%, #111827 100%)",
        "description": "A classic murder mystery novel by Agatha Christie featuring the character Inspector Battle.",
        "cover_image_src": "/home/sb/.gemini/antigravity/brain/70d6c7b5-d081-492a-9b4a-c7f5abfe0d84/secret_chimneys_cover_1781703441770.png"
    },
    
    # Existing Books (so that if we run it on those, we retain their metadata)
    "The_Adventures_of_Sherlock_Holmes": {
        "id": "the-adventures-of-sherlock-holmes",
        "title": "The Adventures of Sherlock Holmes",
        "author": "Arthur Conan Doyle",
        "genre": "Mystery",
        "cover_color": "linear-gradient(135deg, #4b5563 0%, #1f2937 100%)",
        "cover_image_src": "../../html/cove-adventures-sherlockr.jpg",
        "description": "A collection of twelve detective stories featuring Arthur Conan Doyle's famous consulting detective Sherlock Holmes."
    },
    "William_Shakespeare": {
        "id": "complete-works-of-william-shakespeare",
        "title": "The Complete Works of William Shakespeare",
        "author": "William Shakespeare",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)",
        "cover_image_src": "cover-shakespeare.jpg",
        "description": "The complete works of William Shakespeare, including all his plays, sonnets, and poems."
    },
    "Evolution of Constitution": {
        "id": "evolution-of-the-constitution",
        "title": "The Evolution of the Constitution",
        "author": "K.P. Tewari",
        "genre": "History",
        "cover_color": "linear-gradient(135deg, #0d9488 0%, #0f766e 100%)",
        "description": "An in-depth study of the historical evolution of constitutional development and law.",
        "is_wiki_index": True
    },
    "Alices_Adventures_in_Wonderland": {
        "id": "alices-adventures-in-wonderland",
        "title": "Alice's Adventures in Wonderland",
        "author": "Lewis Carroll",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #f43f5e 0%, #be123c 100%)",
        "cover_image_src": "../../html/cover-alice.jpg",
        "description": "The classic story of Alice's journey down a rabbit hole into a fantasy world populated by peculiar creatures."
    },
    "Ancient_States_and_Empires": {
        "id": "ancient-states-and-empires",
        "title": "Ancient States and Empires",
        "author": "John Lord",
        "genre": "History",
        "cover_color": "linear-gradient(135deg, #84cc16 0%, #4f7f02 100%)",
        "description": "An educational overview of the history of ancient states and empires."
    },
    "Charles_Dickens": {
        "id": "the-life-of-charles-dickens",
        "title": "The Life of Charles Dickens",
        "author": "John Forster",
        "genre": "Biography",
        "cover_color": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
        "cover_image_src": "../../html/cover-dickens.jpg",
        "description": "A comprehensive biography of Charles Dickens written by John Forster."
    },
    "Dracula": {
        "id": "dracula",
        "title": "Dracula",
        "author": "Bram Stoker",
        "genre": "Horror",
        "cover_color": "linear-gradient(135deg, #1e1b4b 0%, #030712 100%)",
        "cover_image_src": "../../html/cover-dracula.jpg",
        "description": "The gothic horror masterpiece telling the story of Count Dracula's attempt to move from Transylvania to England."
    },
    "History_of_the_Negro_Race_in_America": {
        "id": "history-of-the-negro-race-in-america",
        "title": "History of the Negro Race in America",
        "author": "George W. Williams",
        "genre": "History",
        "cover_color": "linear-gradient(135deg, #78350f 0%, #451a03 100%)",
        "description": "The landmark historical study of Negro history in America, detailing their struggles and accomplishments."
    },
    "Life_on_the_Mississippi": {
        "id": "life-on-the-mississippi",
        "title": "Life on the Mississippi",
        "author": "Mark Twain",
        "genre": "Memoir",
        "cover_color": "linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%)",
        "cover_image_src": "../../html/cover-misisippi-twain.jpg",
        "description": "Mark Twain's memoir of his time as a steamboat pilot on the Mississippi River."
    },
    "Napoleon": {
        "id": "napoleon",
        "title": "Napoleon",
        "author": "T.P. Tresling",
        "genre": "Biography",
        "cover_color": "linear-gradient(135deg, #e11d48 0%, #9f1239 100%)",
        "description": "De biografie van Napoleon Bonaparte door T.P. Tresling (Dutch edition)."
    },
    "The_Murder_of_Roger_Ackroyd": {
        "id": "the-murder-of-roger-ackroyd",
        "title": "The Murder of Roger Ackroyd",
        "author": "Agatha Christie",
        "genre": "Mystery",
        "cover_color": "linear-gradient(135deg, #1f2937 0%, #111827 100%)",
        "cover_image_src": "../../html/cover-roger-ackroyd.png",
        "description": "Agatha Christie's famous detective novel featuring Hercule Poirot investigating the murder of Roger Ackroyd."
    },
    "War_and_Peace": {
        "id": "war-and-peace",
        "title": "War and Peace",
        "author": "Leo Tolstoy",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #b45309 0%, #78350f 100%)",
        "cover_image_src": "../../html/cover-war-peace.jpg",
        "description": "The epic masterpiece detailing the French invasion of Russia and the impact of the Napoleonic era."
    },
    "A_Honeymoon_in_Space": {
        "id": "a-honeymoon-in-space",
        "title": "A Honeymoon in Space",
        "author": "George Griffith",
        "genre": "Sci-Fi",
        "cover_color": "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
        "description": "A classic science fiction novel featuring a journey through the solar system in a space ship called the Astronef."
    },
    "Dr_Jekyll_and_Mr_Hyde": {
        "id": "dr-jekyll-and-mr-hyde",
        "title": "Dr. Jekyll and Mr. Hyde",
        "author": "Robert Louis Stevenson",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #475569 0%, #334155 100%)",
        "description": "The strange case of Dr. Jekyll and his alter ego, Mr. Hyde, investigating the duality of human nature."
    },
    "The_Misplaced_Battleship": {
        "id": "the-misplaced-battleship",
        "title": "The Misplaced Battleship",
        "author": "Harry Harrison",
        "genre": "Sci-Fi",
        "cover_color": "linear-gradient(135deg, #b45309 0%, #78350f 100%)",
        "description": "A classic science fiction adventure following the Stainless Steel Rat as he searches for a stolen battleship."
    },
    "The_Monk": {
        "id": "the-monk",
        "title": "The Monk",
        "author": "M. G. Lewis",
        "genre": "Horror",
        "cover_color": "linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%)",
        "description": "A gothic horror romance novel by Matthew Gregory Lewis, depicting the downfall of the monk Ambrosio."
    },
    "The_Odyssey": {
        "id": "the-odyssey",
        "title": "The Odyssey",
        "author": "Homer",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #0891b2 0%, #0e7490 100%)",
        "description": "The ancient epic poem detailing Odysseus' ten-year journey home after the fall of Troy."
    },
    "Thuvia_Maid_of_Mars": {
        "id": "thuvia-maid-of-mars",
        "title": "Thuvia, Maid of Mars",
        "author": "Edgar Rice Burroughs",
        "genre": "Sci-Fi",
        "cover_color": "linear-gradient(135deg, #ea580c 0%, #9a3412 100%)",
        "description": "A classic science fantasy novel, the fourth of the Barsoom series by Edgar Rice Burroughs."
    },
    "A_Farewell_to_Arms": {
        "id": "a-farewell-to-arms",
        "title": "A Farewell to Arms",
        "author": "Ernest Hemingway",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
        "description": "Ernest Hemingway's semi-autobiographical novel set during the Italian Campaign of World War I."
    },
    "A_Room_With_a_View": {
        "id": "a-room-with-a-view",
        "title": "A Room with a View",
        "author": "E. M. Forster",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
        "description": "A romantic novel set in Italy and England about a young woman choosing between conventions and passion."
    },
    "Autobiography_of_Benjamin_Franklin": {
        "id": "autobiography-of-benjamin-franklin",
        "title": "Autobiography of Benjamin Franklin",
        "author": "Benjamin Franklin",
        "genre": "Biography",
        "cover_color": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
        "description": "The classic unfinished memoirs written by one of the key Founding Fathers of the United States."
    },
    "Frankenstein": {
        "id": "frankenstein",
        "title": "Frankenstein",
        "author": "Mary Shelley",
        "genre": "Horror",
        "cover_color": "linear-gradient(135deg, #1e1b4b 0%, #030712 100%)",
        "description": "The gothic horror masterpiece detailing the creation of a sentient monster by Victor Frankenstein."
    },
    "King_Arthur": {
        "id": "king-arthur",
        "title": "King Arthur",
        "author": "Rupert S. Holland",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)",
        "cover_image_src": "../../html/cover-king.jpg",
        "description": "A compilation of the traditional legends of King Arthur and the Knights of the Round Table."
    },
    "Moby_Dick": {
        "id": "moby-dick",
        "title": "Moby Dick",
        "author": "Herman Melville",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%)",
        "description": "Herman Melville's classic novel of Captain Ahab's obsessive quest for revenge against the giant white whale."
    },
    "That_Girl_Montana": {
        "id": "that-girl-Montana",
        "title": "That Girl Montana",
        "author": "Marah Ellis Ryan",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #ec4899 0%, #be185d 100%)",
        "description": "A Western romance story of love, honor, and survival in the wilderness of Montana."
    },
    "The_Adventures_of_Roderick_Random": {
        "id": "the-adventures-of-roderick-random",
        "title": "The Adventures of Roderick Random",
        "author": "Tobias Smollett",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #10b981 0%, #047857 100%)",
        "description": "A picaresque novel following the fortunes and misfortunes of Roderick Random."
    },
    "The_Adventures_of_Tom_Sawyer": {
        "id": "the-adventures-of-tom-sawyer",
        "title": "The Adventures of Tom Sawyer",
        "author": "Mark Twain",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #f97316 0%, #c2410c 100%)",
        "description": "The beloved classic of a young boy's adventures growing up along the banks of the Mississippi River."
    },
    "The_Brothers_Karamazov": {
        "id": "the-brothers-karamazov",
        "title": "The Brothers Karamazov",
        "author": "Fyodor Dostoyevsky",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #1f2937 0%, #111827 100%)",
        "description": "Fyodor Dostoyevsky's final masterpiece about a patricide and the philosophical debates that unfold within a Russian family."
    },
    "The_Count_of_Monte_Cristo": {
        "id": "the-count-of-monte-cristo",
        "title": "The Count of Monte Cristo",
        "author": "Alexandre Dumas",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #6b7280 0%, #374151 100%)",
        "description": "An epic tale of wrongfully accused Edmond Dantes, his escape from the Chateau d'If, and his return as the wealthy and vengeful Count."
    },
    "Treasure_Island": {
        "id": "treasure-island",
        "title": "Treasure Island",
        "author": "Robert Louis Stevenson",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #0d9488 0%, #0f766e 100%)",
        "description": "The ultimate pirate adventure featuring Jim Hawkins, a mysterious map, and the infamous Long John Silver."
    }
}

def main():
    log_path = "/home/sb/AI-Works/bakbak.store/uploaded_books.json"
    
    # Run the HTML book converter first
    print("Running convert_new_books.py to convert any new HTML books...")
    try:
        subprocess.run(["python3", "/home/sb/AI-Works/docx2convert/convert_new_books.py"], check=True)
        print("HTML book conversion completed.")
    except Exception as e:
        print(f"Warning: HTML book conversion failed: {e}")
        
    # Load uploaded log
    uploaded = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                uploaded = json.load(f)
        except Exception as e:
            print(f"Error loading log: {e}")

    # Scan output directory for any subdirectories
    if not os.path.exists(OUTPUT_DIR):
        print(f"Output directory {OUTPUT_DIR} not found.")
        return

    output_folders = [d for d in os.listdir(OUTPUT_DIR) if os.path.isdir(os.path.join(OUTPUT_DIR, d))]
    
    books_to_import = []
    for folder in sorted(output_folders):
        if folder in uploaded:
            continue
            
        # Determine metadata
        if folder in KNOWN_METADATA:
            meta = KNOWN_METADATA[folder]
            config = {
                "id": meta.get("id", folder.lower().replace('_', '-').replace(' ', '-')),
                "folder": folder,
                "index_file": "00_Index.md" if meta.get("is_wiki_index") else "index.md",
                "title": meta.get("title", folder.replace('_', ' ')),
                "author": meta.get("author", "Unknown Author"),
                "genre": meta.get("genre", "Classics"),
                "cover_color": meta.get("cover_color", "linear-gradient(135deg, #6b7280 0%, #374151 100%)"),
                "description": meta.get("description", f"No description available for {folder.replace('_', ' ')}."),
                "is_wiki_index": meta.get("is_wiki_index", False)
            }
            if "cover_image_src" in meta:
                config["cover_image_src"] = meta["cover_image_src"]
        else:
            # Dynamically infer metadata for totally new/unregistered books
            book_id = re.sub(r'[^a-z0-9\-]', '', folder.lower().replace('_', '-').replace(' ', '-'))
            index_file = "index.md"
            for name in ["index.md", "00_Index.md", "01_Index.md"]:
                if os.path.exists(os.path.join(OUTPUT_DIR, folder, name)):
                    index_file = name
                    break
                    
            title = folder.replace('_', ' ')
            index_path = os.path.join(OUTPUT_DIR, folder, index_file)
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#'):
                        title = first_line.lstrip('#').strip()
                        title = re.sub(r'\s*-\s*Index$', '', title, flags=re.IGNORECASE)
                        title = re.sub(r'\s*Index$', '', title, flags=re.IGNORECASE)
                        title = re.sub(r'\s*-\s*Table of Contents$', '', title, flags=re.IGNORECASE)
                        title = re.sub(r'\s*Table of Contents$', '', title, flags=re.IGNORECASE)
                        title = title.strip()
                        
            config = {
                "id": book_id,
                "folder": folder,
                "index_file": index_file,
                "title": title,
                "author": "Unknown Author",
                "genre": "Classics",
                "cover_color": "linear-gradient(135deg, #6b7280 0%, #374151 100%)",
                "description": f"No description available for {title}.",
                "is_wiki_index": (index_file == "00_Index.md")
            }
            
        books_to_import.append(config)
            
    imported_any = False
    imported_titles = []
    log_details = ""
    
    for book in books_to_import:
        print(f"Sync: new book detected: {book['title']}...")
        success = import_book(book)
        if success:
            uploaded.append(book["folder"])
            imported_titles.append(book["title"])
            imported_any = True
            log_details += f"- {book['title']} ({book['folder']}): Imported and configured.\n"
            
    if imported_any:
        # Save updated registry
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(uploaded, f, indent=2)
            
        # Log to activity.log
        log_activity(
            "AUTOMATED BOOK SYNC: New books imported",
            log_details
        )
        
        # Compile catalog.json
        regenerate_catalog()
        
        # Bump sw.js
        bump_service_worker()
        
        # Push to Git
        git_push_changes(imported_titles)
        print("Sync complete.")
    else:
        print("No new books found in output folder to sync.")

if __name__ == "__main__":
    main()
