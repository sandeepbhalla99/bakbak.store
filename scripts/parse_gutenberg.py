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

def tokenize(s):
    return re.findall(r'[a-z0-9]+', s.lower())

def is_roman(s):
    return bool(re.match(r'^[ivxlcdm]+$', s.lower()))

def clean_title_tokens(tokens):
    prefix_words = {'chapter', 'book', 'part', 'act', 'scene', 'section'}
    
    # Find how many leading tokens are prefixes, numbers, or roman numerals
    start_idx = 0
    while start_idx < len(tokens):
        token = tokens[start_idx]
        if token in prefix_words or token.isdigit() or is_roman(token):
            start_idx += 1
        else:
            break
            
    if start_idx == len(tokens):
        cleaned = [t for t in tokens if t not in prefix_words]
        if not cleaned:
            return tokens
        return cleaned
        
    return tokens[start_idx:]

def is_toc_match(toc_title, body_line):
    toc_words = tokenize(toc_title)
    body_words = tokenize(body_line)
    if not toc_words or not body_words:
        return False
        
    toc_clean = clean_title_tokens(toc_words)
    body_clean = clean_title_tokens(body_words)
    
    if not toc_clean or not body_clean:
        return False
        
    # If either cleaned token list is a single short token, digit, or Roman numeral,
    # they must match exactly to avoid matching common prose words (like "I", "A", "1")
    if len(toc_clean) == 1 and (len(toc_clean[0]) <= 2 or toc_clean[0].isdigit() or is_roman(toc_clean[0])):
        return len(body_clean) == 1 and body_clean[0] == toc_clean[0]
        
    if len(body_clean) == 1 and (len(body_clean[0]) <= 2 or body_clean[0].isdigit() or is_roman(body_clean[0])):
        return len(toc_clean) == 1 and toc_clean[0] == body_clean[0]
        
    # Standard prefix/exact match for descriptive titles
    # Limit the length difference to prevent matching prose sentences containing the title
    if toc_clean[:len(body_clean)] == body_clean:
        return len(toc_clean) <= len(body_clean) + 2
        
    if body_clean[:len(toc_clean)] == toc_clean:
        return len(body_clean) <= len(toc_clean) + 2
        
    return False

def extract_toc_titles(text):
    lines = text.split('\n')
    toc_start = -1
    for idx, line in enumerate(lines[:300]):
        if re.match(r'^\s*(?:Table of Contents|CONTENTS|Contents)\s*$', line, re.IGNORECASE):
            toc_start = idx
            break
            
    if toc_start == -1:
        return [], -1
        
    toc_titles = []
    
    # Helper to check if a line starts with a chapter/section marker
    def is_header_like(s):
        s_lower = s.lower()
        if re.match(r'^(?:chapter|book|part|act|scene|prologue|epilogue|preface|letter|introduction|dramatis)\b', s_lower):
            return True
        if re.match(r'^(?:[ivxlcdm]+\b|[\d]+\b)', s_lower):
            return True
        return False

    i = toc_start + 1
    while i < min(toc_start + 150, len(lines)):
        line = lines[i]
        trimmed = line.strip()
        
        if not trimmed:
            i += 1
            continue
            
        # Stop if we see a repeat of the first TOC title (indicating the start of the book body)
        if toc_titles:
            if is_toc_match(toc_titles[0], trimmed):
                break
            
        # Check if this line and the next line form a prose paragraph
        next_non_empty = ""
        next_idx = i + 1
        while next_idx < len(lines):
            if lines[next_idx].strip():
                next_non_empty = lines[next_idx].strip()
                break
            next_idx += 1
            
        # If this line and the next line are consecutive (next_idx == i + 1)
        # and neither is header-like, then it's a prose paragraph!
        if next_idx == i + 1 and next_non_empty:
            if not is_header_like(trimmed) and not is_header_like(next_non_empty):
                # We hit a regular paragraph of the story, stop TOC parsing!
                break
                
        # Also, stop if we hit a long line (TOC lines are short)
        if len(trimmed) > 75:
            break
            
        # Clean the title (remove dot leaders and trailing numbers/pages)
        clean_title = re.sub(r'(?:\.[\s\.]*|-[\s-]*|\s{2,})\d+$', '', trimmed).strip()
        clean_title = re.sub(r'[\.\-\s]+$', '', clean_title)
        
        # Avoid short junk symbols
        if clean_title and len(clean_title) > 3:
            toc_titles.append(clean_title)
            
        i += 1
        
    return toc_titles, i

def normalize_title(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

def split_into_chapters(text):
    # First, let's check if there is an explicit Table of Contents we can extract
    toc_titles, toc_end_idx = extract_toc_titles(text)
    
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
        matched_toc = False
        title_text = line.strip()
        
        # Only detect chapter headings if we are past the Table of Contents block
        if i >= toc_end_idx:
            # 1. Match against explicit TOC titles if we found them
            if toc_titles:
                matched_toc = False
                for toc in toc_titles:
                    if is_toc_match(toc, title_text):
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
            # Lookahead subtitle combiner: search for first non-empty line within next 3 lines
            subtitle = ""
            subtitle_idx = -1
            for offset in range(1, 4):
                if i + offset < len(lines):
                    next_val = lines[i + offset].strip()
                    if next_val:
                        # If it is a short line and doesn't look like another chapter header
                        if len(next_val) < 80 and not chapter_regex.match(lines[i + offset]) and not roman_regex.match(lines[i + offset]) and not number_regex.match(lines[i + offset]):
                            following_empty = True
                            if i + offset + 1 < len(lines):
                                following_val = lines[i + offset + 1].strip()
                                if following_val:
                                    following_empty = False
                            if following_empty:
                                subtitle = next_val
                                subtitle_idx = i + offset
                        break
            if subtitle:
                if not matched_toc:
                    base_title = title_text.strip(".:- ")
                    title_text = f"{base_title}: {subtitle}"
                lines[subtitle_idx] = ""

            # Save previous chapter if it had content (or if it is the Introduction)
            if current_chapter_content or current_chapter_title == "Introduction":
                chapters.append({
                    "title": current_chapter_title,
                    "content": "\n".join(current_chapter_content).strip()
                })
            current_chapter_title = title_text
            current_chapter_content = []
        else:
            if current_chapter_title != "Introduction" or i >= toc_end_idx:
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
def reflow_paragraph(para):
    lines = [line.strip() for line in para.split('\n')]
    lines = [l for l in lines if l]
    if not lines:
        return ""
    if len(lines) == 1:
        return para.strip()
    
    # If average line length is small, it's likely a poem or script (skip reflow)
    non_last_lines = lines[:-1]
    avg_len = sum(len(l) for l in non_last_lines) / len(non_last_lines) if non_last_lines else 0
    if avg_len > 45:
        return " ".join(lines)
    return "\n".join(lines)

def reflow_text(text):
    paras = re.split(r'\n\s*\n', text)
    reflowed_paras = []
    for para in paras:
        para_clean = para.strip()
        if not para_clean:
            continue
        reflowed_paras.append(reflow_paragraph(para_clean))
    return "\n\n".join(reflowed_paras)

def save_book(book_id, title, author, genre, chapters):
    book_dir = os.path.join(DEST_DIR, book_id)
    if os.path.exists(book_dir):
        import shutil
        shutil.rmtree(book_dir)
    chapters_dir = os.path.join(book_dir, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)
    
    chapters_list = []
    
    for idx, chap in enumerate(chapters):
        chap_title = chap["title"]
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', chap_title)[:30].strip('_')
        filename = f"{idx+1:02d}_{safe_title}.md"
        
        # If it is the Introduction chapter, dynamically generate a beautiful TOC page
        if idx == 0 and chap_title == "Introduction":
            # Generate the premium HTML/Markdown header and TOC links
            intro_markdown = f"""# Introduction

<div style="text-align: center; margin-bottom: 2.5rem; padding-top: 1rem;">
  <h1 style="font-size: 2.25rem; margin-bottom: 0.5rem; font-weight: 800; color: var(--text-main); line-height: 1.2;">{title}</h1>
  <p style="font-size: 1.25rem; color: var(--text-muted); font-style: italic; margin-top: 0.5rem;">by {author}</p>
</div>

<hr style="border: 0; border-top: 1px solid var(--border-color); margin: 2rem 0; opacity: 0.5;">

<div class="toc-container" style="max-width: 550px; margin: 0 auto; padding: 0 10px;">
  <h3 style="text-align: center; margin-bottom: 1.5rem; letter-spacing: 0.08em; text-transform: uppercase; font-size: 1.1rem; font-weight: 700; color: var(--text-main);">Table of Contents</h3>
  <ul style="list-style: none; padding: 0; margin: 0; line-height: 2;">
"""
            # Build list items for each subsequent chapter
            for c_idx, c_val in enumerate(chapters):
                if c_idx == 0:
                    continue
                c_title = c_val["title"]
                c_safe = re.sub(r'[^a-zA-Z0-9]', '_', c_title)[:30].strip('_')
                c_file = f"{c_idx+1:02d}_{c_safe}.md"
                intro_markdown += f'    <li style="margin-bottom: 0.85rem; border-bottom: 1px dashed var(--border-color); padding-bottom: 0.35rem;"><a href="{c_file}" style="color: var(--accent); text-decoration: none; font-weight: 500; display: flex; justify-content: space-between; align-items: baseline;"><span>{c_title}</span> <span style="color: var(--text-muted); font-size: 0.85rem; font-weight: 400; padding-left: 10px; text-align: right;">Chapter {c_idx}</span></a></li>\n'
                
            intro_markdown += """  </ul>
</div>

"""
            # If there was actual preface/intro text, append it below the TOC
            preface_text = chap['content'].strip()
            if preface_text:
                intro_markdown += f'<hr style="border: 0; border-top: 1px solid var(--border-color); margin: 3rem 0; opacity: 0.5;">\n\n{reflow_text(preface_text)}'
                
            reflowed_content = intro_markdown
        else:
            reflowed_content = reflow_text(chap['content'])
        
        # Write chapter markdown file
        with open(os.path.join(chapters_dir, filename), 'w', encoding='utf-8') as f:
            f.write(f"# {chap_title}\n\n{reflowed_content}")
            
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
