import os
import re
import json

SOURCE_DIR = "/home/sb/AI-Works/gutenberg/cleaned_books"
DEST_DIR = "/home/sb/AI-Works/bakbak.store/books"

# Create destination folder if not exists
os.makedirs(DEST_DIR, exist_ok=True)

# List of Shakespeare plays from the Complete Works table of contents
SHAKESPEARE_PLAYS = [
    "THE SONNETS",
    "ALL’S WELL THAT ENDS WELL",
    "THE TRAGEDY OF ANTONY AND CLEOPATRA",
    "AS YOU LIKE IT",
    "THE COMEDY OF ERRORS",
    "THE TRAGEDY OF CORIOLANUS",
    "CYMBELINE",
    "THE TRAGEDY OF HAMLET, PRINCE OF DENMARK",
    "THE FIRST PART OF KING HENRY THE FOURTH",
    "THE SECOND PART OF KING HENRY THE FOURTH",
    "THE LIFE OF KING HENRY THE FIFTH",
    "THE FIRST PART OF HENRY THE SIXTH",
    "THE SECOND PART OF KING HENRY THE SIXTH",
    "THE THIRD PART OF KING HENRY THE SIXTH",
    "KING HENRY THE EIGHTH",
    "THE LIFE AND DEATH OF KING JOHN",
    "THE TRAGEDY OF JULIUS CAESAR",
    "THE TRAGEDY OF KING LEAR",
    "LOVE’S LABOUR’S LOST",
    "THE TRAGEDY OF MACBETH",
    "MEASURE FOR MEASURE",
    "THE MERCHANT OF VENICE",
    "THE MERRY WIVES OF WINDSOR",
    "A MIDSUMMER NIGHT’S DREAM",
    "MUCH ADO ABOUT NOTHING",
    "THE TRAGEDY OF OTHELLO, THE MOOR OF VENICE",
    "PERICLES, PRINCE OF TYRE",
    "KING RICHARD THE SECOND",
    "KING RICHARD THE THIRD",
    "THE TRAGEDY OF ROMEO AND JULIET",
    "THE TAMING OF THE SHREW",
    "THE TEMPEST",
    "THE LIFE OF TIMON OF ATHENS",
    "THE TRAGEDY OF TITUS ANDRONICUS",
    "TROILUS AND CRESSIDA",
    "TWELFTH NIGHT; OR, WHAT YOU WILL",
    "THE TWO GENTLEMEN OF VERONA",
    "THE TWO NOBLE KINSMEN",
    "THE WINTER’S TALE",
    "A LOVER’S COMPLAINT",
    "THE PASSIONATE PILGRIM",
    "THE PHOENIX AND THE TURTLE",
    "THE RAPE OF LUCRECE",
    "VENUS AND ADONIS"
]

def clean_id(title):
    # Convert title to a clean URL-friendly ID
    cleaned = re.sub(r'[^a-zA-Z0-9\s-]', '', title).lower().strip()
    return re.sub(r'[\s-]+', '-', cleaned)

def strip_gutenberg_wrappers(text):
    # Look for start and end markers of Gutenberg ebook
    start_pattern = re.compile(r'\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*', re.IGNORECASE)
    end_pattern = re.compile(r'\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*', re.IGNORECASE)
    
    start_match = start_pattern.search(text)
    end_match = end_pattern.search(text)
    
    start_idx = start_match.end() if start_match else 0
    end_idx = end_match.start() if end_match else len(text)
    
    return text[start_idx:end_idx].strip()

BOOK_METADATA = {
    "11": {"title": "Alice's Adventures in Wonderland", "author": "Lewis Carroll", "genre": "Classics"},
    "43": {"title": "The Strange Case of Dr. Jekyll and Mr. Hyde", "author": "Robert Louis Stevenson", "genre": "Classics"},
    "74": {"title": "The Adventures of Tom Sawyer", "author": "Mark Twain", "genre": "Classics"},
    "76": {"title": "Adventures of Huckleberry Finn", "author": "Mark Twain", "genre": "Classics"},
    "84": {"title": "Frankenstein", "author": "Mary Shelley", "genre": "Classics"},
    "98": {"title": "A Tale of Two Cities", "author": "Charles Dickens", "genre": "Classics"},
    "120": {"title": "Treasure Island", "author": "Robert Louis Stevenson", "genre": "Classics"},
    "145": {"title": "Middlemarch", "author": "George Eliot", "genre": "Classics"},
    "161": {"title": "Sense and Sensibility", "author": "Jane Austen", "genre": "Classics"},
    "174": {"title": "The Picture of Dorian Gray", "author": "Oscar Wilde", "genre": "Classics"},
    "345": {"title": "Dracula", "author": "Bram Stoker", "genre": "Classics"},
    "394": {"title": "Cranford", "author": "Elizabeth Gaskell", "genre": "Classics"},
    "768": {"title": "Wuthering Heights", "author": "Emily Brontë", "genre": "Classics"},
    "1184": {"title": "The Count of Monte Cristo", "author": "Alexandre Dumas", "genre": "Classics"},
    "1259": {"title": "Twenty Years After", "author": "Alexandre Dumas", "genre": "Classics"},
    "1260": {"title": "Jane Eyre", "author": "Charlotte Brontë", "genre": "Classics"},
    "1342": {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Classics"},
    "1513": {"title": "Romeo and Juliet", "author": "William Shakespeare", "genre": "Classics"},
    "1661": {"title": "The Adventures of Sherlock Holmes", "author": "Arthur Conan Doyle", "genre": "Mystery"},
    "1727": {"title": "The Odyssey", "author": "Homer", "genre": "Classics"},
    "1998": {"title": "Thus Spake Zarathustra", "author": "Friedrich Nietzsche", "genre": "Classics"},
    "2160": {"title": "The Expedition of Humphry Clinker", "author": "Tobias Smollett", "genre": "Classics"},
    "21839": {"title": "Sense and Sensibility", "author": "Jane Austen", "genre": "Classics"},
    "23784": {"title": "The History of Sir Richard Calmady", "author": "Lucas Malet", "genre": "Classics"},
    "2542": {"title": "A Doll's House", "author": "Henrik Ibsen", "genre": "Classics"},
    "2554": {"title": "Crime and Punishment", "author": "Fyodor Dostoevsky", "genre": "Classics"},
    "2641": {"title": "A Room with a View", "author": "E. M. Forster", "genre": "Classics"},
    "2680": {"title": "Meditations", "author": "Marcus Aurelius", "genre": "Classics"},
    "2701": {"title": "Moby-Dick", "author": "Herman Melville", "genre": "Classics"},
    "2852": {"title": "The Hound of the Baskervilles", "author": "Arthur Conan Doyle", "genre": "Mystery"},
    "3296": {"title": "The Confessions of St. Augustine", "author": "Saint Augustine", "genre": "Classics"},
    "4085": {"title": "The Adventures of Roderick Random", "author": "Tobias Smollett", "genre": "Classics"},
    "6593": {"title": "The History of Tom Jones, a Foundling", "author": "Henry Fielding", "genre": "Classics"},
    "6761": {"title": "The Adventures of Ferdinand Count Fathom", "author": "Tobias Smollett", "genre": "Classics"},
    "8492": {"title": "The King in Yellow", "author": "Robert W. Chambers", "genre": "Classics"},
    "16389": {"title": "The Enchanted April", "author": "Elizabeth von Arnim", "genre": "Classics"},
    "28054": {"title": "The Brothers Karamazov", "author": "Fyodor Dostoevsky", "genre": "Classics"},
    "37106": {"title": "Little Women", "author": "Louisa May Alcott", "genre": "Classics"},
    "64317": {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Classics"},
    "65661": {"title": "Der Zauberberg (The Magic Mountain)", "author": "Thomas Mann", "genre": "Classics"},
    "67979": {"title": "The Blue Castle", "author": "L. M. Montgomery", "genre": "Classics"}
}

def parse_metadata(text, filename):
    # Try finding the Gutenberg ID in our mapping
    parts = filename.split('_', 1)
    gutenberg_id = parts[0]
    
    if gutenberg_id in BOOK_METADATA:
        meta = BOOK_METADATA[gutenberg_id]
        return meta["title"], meta["author"]

    title = ""
    author = ""
    
    title_match = re.search(r'^Title:\s*(.*)$', text, re.MULTILINE | re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
        
    author_match = re.search(r'^Author:\s*(.*)$', text, re.MULTILINE | re.IGNORECASE)
    if author_match:
        author = author_match.group(1).strip()
        
    # Fallback to file name if not parsed
    if not title:
        name_part = os.path.splitext(filename)[0]
        name_part = re.sub(r'^\d+_', '', name_part) # remove number prefix
        title = name_part.replace('_', ' ')
        
    if not author:
        author = "Project Gutenberg"
        
    return title, author

def extract_toc_titles(text):
    # Try to extract chapter titles from a Table of Contents (Contents) block
    # Search for "Contents" or "CONTENTS" near the start
    lines = text.split('\n')
    toc_start = -1
    for idx, line in enumerate(lines[:300]):
        if re.match(r'^\s*(?:Table of Contents|CONTENTS|Contents)\s*$', line, re.IGNORECASE):
            toc_start = idx
            break
            
    if toc_start == -1:
        return []
        
    toc_titles = []
    # Collect non-empty lines following "Contents" until we hit a long line or start of text
    for line in lines[toc_start+1 : toc_start+100]:
        trimmed = line.strip()
        if not trimmed:
            continue
        
        # Stop indicators for TOC
        if len(trimmed) > 80:
            break
        if trimmed.startswith('***') or re.match(r'^\s*PART\s+[I\d]', trimmed, re.IGNORECASE):
            # Parts are fine, but stop if we see full start of text
            pass
            
        # Clean title (remove page numbers at the end like ". . . 11" or "  12")
        clean_title = re.sub(r'[\.\s\d]+$', '', trimmed).strip()
        
        # Avoid short junk symbols
        if clean_title and len(clean_title) > 3:
            toc_titles.append(clean_title)
            
    return toc_titles

def split_into_chapters(text):
    # First, let's check if there is an explicit Table of Contents we can extract
    toc_titles = extract_toc_titles(text)
    
    lines = text.split('\n')
    chapters = []
    current_chapter_title = "Introduction"
    current_chapter_content = []
    
    # Standard chapter heading regexes
    chapter_regex = re.compile(r'^\s*(?:CHAPTER|Chapter|Act|ACT|Scene|SCENE|PROLOGUE|EPILOGUE|PREFACE|LETTER|BOOK|Book)\b\s*([IVXLCDM\d\.\-]*)(.*)$')
    roman_regex = re.compile(r'^\s*([IVXLCDM]+)\s*$') # e.g. Just "I" or "XX"
    number_regex = re.compile(r'^\s*(\d+)\s*$') # e.g. Just "1" or "2"
    
    for i, line in enumerate(lines):
        is_chapter_head = False
        title_text = line.strip()
        
        # 1. Match against explicit TOC titles if we found them
        if toc_titles:
            # Check if this line matches any of the TOC titles exactly (case-insensitive)
            matched_toc = False
            for toc in toc_titles:
                if title_text.lower() == toc.lower() or title_text.lower().startswith(toc.lower() + "—"):
                    matched_toc = True
                    title_text = toc
                    break
            if matched_toc:
                is_chapter_head = True
                
        # 2. Match standard "Chapter X" or "Act X" patterns
        if not is_chapter_head:
            match = chapter_regex.match(line)
            if match:
                is_chapter_head = True
                title_text = line.strip()
                
        # 3. Match standalone Roman numerals (e.g. "I", "II") followed by a short line (Chapter title)
        if not is_chapter_head and roman_regex.match(line):
            # Check context: empty line above, and next line is a short title (len < 80)
            prev_empty = (i == 0 or lines[i-1].strip() == "")
            if prev_empty and i < len(lines)-1:
                next_line = lines[i+1].strip()
                if next_line and len(next_line) < 80:
                    is_chapter_head = True
                    title_text = f"Chapter {line.strip()}: {next_line}"
                    # Skip the next line since it is incorporated into the title
                    lines[i+1] = ""
                    
        # 4. Match standalone Arabic numbers (e.g. "1", "2") surrounded by empty lines
        if not is_chapter_head and number_regex.match(line):
            prev_empty = (i == 0 or lines[i-1].strip() == "")
            next_empty = (i == len(lines)-1 or lines[i+1].strip() == "")
            if prev_empty and next_empty:
                is_chapter_head = True
                title_text = f"Chapter {line.strip()}"
                
        if is_chapter_head:
            # Save previous chapter if it had content
            if current_chapter_content:
                chapters.append({
                    "title": current_chapter_title,
                    "content": "\n".join(current_chapter_content).strip()
                })
            current_chapter_title = title_text
            current_chapter_content = []
        else:
            current_chapter_content.append(line)
            
    # Append final chapter
    if current_chapter_content:
        chapters.append({
            "title": current_chapter_title,
            "content": "\n".join(current_chapter_content).strip()
        })
        
    # If no chapters were detected, split into roughly equal chunks
    if len(chapters) <= 1:
        # Fallback split: divide book into 10-page chunks (~3000 words each) if text is very long
        words = text.split()
        if len(words) > 5000:
            chapters = []
            chunk_size = 3000
            for chunk_idx, k in enumerate(range(0, len(words), chunk_size)):
                chunk_words = words[k : k + chunk_size]
                chapters.append({
                    "title": f"Section {chunk_idx + 1}",
                    "content": " ".join(chunk_words)
                })
        else:
            chapters = [{"title": "Full Book", "content": text}]
            
    return chapters

def save_book(book_id, title, author, genre, chapters):
    book_dir = os.path.join(DEST_DIR, book_id)
    chapters_dir = os.path.join(book_dir, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)
    
    chapters_list = []
    
    for idx, chap in enumerate(chapters):
        chap_title = chap["title"]
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', chap_title)[:30].strip('_')
        filename = f"{idx+1:02d}_{safe_title}.md"
        
        # Write chapter markdown file
        with open(os.path.join(chapters_dir, filename), 'w', encoding='utf-8') as f:
            f.write(f"# {chap_title}\n\n{chap['content']}")
            
        chapters_list.append({
            "title": chap_title,
            "file": filename
        })
        
    # Write details.json
    details = {
      "id": book_id,
      "title": title,
      "author": author,
      "genre": genre,
      "coverColor": get_random_gradient(book_id),
      "description": f"A classic masterpiece by {author}. Read this Project Gutenberg edition on Bakbak.store.",
      "chapters": chapters_list
    }
    
    with open(os.path.join(book_dir, "details.json"), 'w', encoding='utf-8') as f:
        json.dump(details, f, indent=2)
        
    print(f"Saved: {title} by {author} ({len(chapters)} chapters)")

def get_random_gradient(book_id):
    gradients = [
        "linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%)", # violet
        "linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)", # cyan
        "linear-gradient(135deg, #ec4899 0%, #be185d 100%)", # pink
        "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)", # amber
        "linear-gradient(135deg, #10b981 0%, #059669 100%)", # emerald
        "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)", # blue
        "linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)", # red
        "linear-gradient(135deg, #84cc16 0%, #4d7c0f 100%)"  # lime
    ]
    val = sum(ord(c) for c in book_id)
    return gradients[val % len(gradients)]

def get_genre_for_book(title):
    title_lower = title.lower()
    if any(w in title_lower for w in ["poems", "poetry", "sonnets", "works"]):
        return "Classics"
    if any(w in title_lower for w in ["tragedy", "comedy", "play", "romeo", "hamlet", "macbeth"]):
        return "Classics"
    if any(w in title_lower for w in ["sherlock", "mystery", "detective", "hound", "scarlet"]):
        return "Mystery"
    if any(w in title_lower for w in ["dracula", "frankenstein", "jekyll", "horror"]):
        return "Classics"
    if any(w in title_lower for w in ["island", "treasure", "adventures", "huckleberry", "sawyer"]):
        return "Classics"
    if any(w in title_lower for w in ["time", "science", "future", "space"]):
        return "Sci-Fi"
    return "Classics"

# --- SPECIAL SPLITTERS ---

def process_shakespeare(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        full_text = f.read()
        
    cleaned_body = strip_gutenberg_wrappers(full_text)
    
    positions = []
    for play in SHAKESPEARE_PLAYS:
        pattern = re.compile(rf'^\s*{re.escape(play)}\s*$', re.MULTILINE)
        matches = list(pattern.finditer(cleaned_body))
        
        valid_matches = [m for m in matches if m.start() > 2000]
        if valid_matches:
            positions.append((valid_matches[0].start(), play))
            
    positions.sort()
    
    for i in range(len(positions)):
        start_pos, play_name = positions[i]
        end_pos = positions[i+1][0] if i+1 < len(positions) else len(cleaned_body)
        
        play_text = cleaned_body[start_pos:end_pos].strip()
        chapters = split_into_chapters(play_text)
        
        book_id = clean_id(f"shakespeare-{play_name}")
        save_book(book_id, play_name, "William Shakespeare", "Classics", chapters)

def process_two_magics(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        full_text = f.read()
        
    body = strip_gutenberg_wrappers(full_text)
    cover_end_pattern = re.compile(r'^\s*COVERING END\s*$', re.MULTILINE)
    match = cover_end_pattern.search(body)
    
    if match:
        split_pos = match.start()
        
        # Book 1: The Turn of the Screw
        screw_text = body[:split_pos].strip()
        screw_chapters = split_into_chapters(screw_text)
        save_book("the-turn-of-the-screw", "The Turn of the Screw", "Henry James", "Classics", screw_chapters)
        
        # Book 2: Covering End
        covering_text = body[split_pos:].strip()
        covering_chapters = split_into_chapters(covering_text)
        save_book("covering-end", "Covering End", "Henry James", "Classics", covering_chapters)
    else:
        chapters = split_into_chapters(body)
        save_book("the-two-magics", "The Two Magics", "Henry James", "Classics", chapters)

# --- MAIN CONTROLLER ---

def main():
    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.txt')]
    print(f"Found {len(files)} files to process...")
    
    for filename in files:
        filepath = os.path.join(SOURCE_DIR, filename)
        
        # Special case: Shakespeare Complete Works
        if "Shakespeare" in filename:
            print("Processing Shakespeare Complete Works...")
            process_shakespeare(filepath)
            continue
            
        # Special case: The Two Magics
        if "Two_Magics" in filename:
            print("Processing The Two Magics...")
            process_two_magics(filepath)
            continue
            
        # Standard books
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                raw_content = f.read()
                
            title, author = parse_metadata(raw_content, filename)
            body = strip_gutenberg_wrappers(raw_content)
            
            chapters = split_into_chapters(body)
            
            book_id = clean_id(title)
            parts = filename.split('_', 1)
            gutenberg_id = parts[0]
            if gutenberg_id in BOOK_METADATA:
                genre = BOOK_METADATA[gutenberg_id]["genre"]
            else:
                genre = get_genre_for_book(title)
            
            save_book(book_id, title, author, genre, chapters)
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
if __name__ == "__main__":
    main()
