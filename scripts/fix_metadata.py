#!/usr/bin/env python3
"""
Fix metadata and regenerate covers for books with Unknown Author or missing info.
Run this once to patch all affected books, then push to git.
"""
import os
import re
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont

BAKBAK_BOOKS_DIR = "/home/sb/AI-Works/bakbak.store/books"

# Correct metadata for every book that has wrong/missing info
FIXES = {
    "the-passionate-elopement": {
        "title": "The Passionate Elopement",
        "author": "Compton Mackenzie",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #be185d 0%, #9d174d 100%)",
        "description": "Compton Mackenzie's witty debut novel set in 18th-century England, following the romantic misadventures of a young eloping couple."
    },
    "indias-love-lyrics": {
        "title": "India's Love Lyrics",
        "author": "Laurence Hope",
        "genre": "Poetry",
        "cover_color": "linear-gradient(135deg, #b45309 0%, #92400e 100%)",
        "description": "A celebrated collection of passionate and evocative love poems inspired by India, written under the pen name Laurence Hope."
    },
    "pride-and-prejudice---project-gutenberg": {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
        "description": "Jane Austen's beloved masterpiece about love, marriage, and social class in Regency-era England, featuring Elizabeth Bennet and Mr. Darcy."
    },
    "the-prairie-wife": {
        "title": "The Prairie Wife",
        "author": "Arthur Stringer",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #d97706 0%, #b45309 100%)",
        "description": "Arthur Stringer's epistolary novel following a young society woman's transformation as she adapts to life on the rugged Canadian prairies."
    },
    "erotica-romana": {
        "title": "Erotica Romana",
        "author": "Johann Wolfgang von Goethe",
        "genre": "Poetry",
        "cover_color": "linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)",
        "description": "Goethe's elegant cycle of Roman elegies celebrating love and beauty, inspired by his sojourn in Rome and the classical Latin poets."
    },
    "what-will-people-say": {
        "title": "What Will People Say?",
        "author": "Rupert Hughes",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #0369a1 0%, #075985 100%)",
        "description": "Rupert Hughes' compelling novel about the tension between social expectations and personal freedom in early 20th-century New York high society."
    },
    "i-am-a-woman": {
        "title": "I Am a Woman",
        "author": "Valerie Taylor",
        "genre": "Drama",
        "cover_color": "linear-gradient(135deg, #ec4899 0%, #be185d 100%)",
        "description": "A pioneering and courageous story exploring personal identity, love, and the struggle for authenticity in mid-20th-century America."
    },
    "the-red-lily": {
        "title": "The Red Lily",
        "author": "Anatole France",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #dc2626 0%, #991b1b 100%)",
        "description": "Anatole France's elegant and impassioned novel set in Florence and Paris, exploring love, jealousy, and artistic passion in fin-de-siècle society."
    },
    "romeo-and-juliet---project-gutenberg": {
        "title": "Romeo and Juliet",
        "author": "William Shakespeare",
        "genre": "Drama",
        "cover_color": "linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)",
        "description": "Shakespeare's timeless tragedy of star-crossed lovers from rival families in Verona, whose doomed romance ends in tragedy."
    },
    "the-complete-works-of-william-shakespeare": {
        "title": "The Complete Works of William Shakespeare",
        "author": "William Shakespeare",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #4f46e5 0%, #3730a3 100%)",
        "description": "The definitive collection of all of Shakespeare's plays, sonnets, and poems — comedies, histories, tragedies, and verse — from the greatest writer in the English language."
    },
    "the-countess-of-pembrokes-arcadia": {
        "title": "The Countess of Pembroke's Arcadia",
        "author": "Sir Philip Sidney",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #059669 0%, #047857 100%)",
        "description": "Sir Philip Sidney's renowned pastoral romance, a cornerstone of Elizabethan literature blending adventure, philosophy, and love poetry."
    },
    "camille-la-dame-aux-camilias": {
        "title": "Camille (La Dame aux Camélias)",
        "author": "Alexandre Dumas fils",
        "genre": "Classics",
        "cover_color": "linear-gradient(135deg, #9d174d 0%, #831843 100%)",
        "description": "The romantic tragedy of Marguerite Gautier, a Parisian courtesan who falls passionately in love, by Alexandre Dumas fils — the inspiration for Verdi's La Traviata."
    },
}


def generate_cover(title, author, dest_path, cover_color):
    """Generate a styled book cover with correct author and colors derived from cover_color."""
    width, height = 400, 600

    # Parse gradient colors from CSS string
    matches = re.findall(r'#([0-9a-fA-F]{6})', cover_color)
    if len(matches) >= 2:
        c1 = tuple(int(matches[0][i:i+2], 16) for i in (0, 2, 4))
        c2 = tuple(int(matches[1][i:i+2], 16) for i in (0, 2, 4))
    else:
        c1, c2 = (30, 27, 75), (15, 23, 42)

    img = Image.new("RGB", (width, height), c1)
    draw = ImageDraw.Draw(img)

    # Draw vertical gradient
    for y in range(height):
        r = int(c1[0] + (c2[0] - c1[0]) * (y / height))
        g = int(c1[1] + (c2[1] - c1[1]) * (y / height))
        b = int(c1[2] + (c2[2] - c1[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Subtle decorative border
    draw.rectangle([10, 10, width - 10, height - 10], outline=(255, 255, 255, 60), width=1)
    draw.rectangle([18, 18, width - 18, height - 18], outline=(255, 255, 255, 20), width=1)

    # Load fonts
    font_paths = [
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    font_reg_paths = [
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]

    title_font = author_font = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                title_font = ImageFont.truetype(fp, 34)
                break
            except Exception:
                pass
    for fp in font_reg_paths:
        if os.path.exists(fp):
            try:
                author_font = ImageFont.truetype(fp, 20)
                break
            except Exception:
                pass
    if not title_font:
        title_font = ImageFont.load_default()
    if not author_font:
        author_font = ImageFont.load_default()

    def wrap_text(text, font, max_width):
        words = text.split()
        lines, current = [], []
        for word in words:
            test = " ".join(current + [word])
            try:
                w = font.getbbox(test)[2] - font.getbbox(test)[0]
            except AttributeError:
                w = font.getsize(test)[0]
            if w <= max_width:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
        return lines

    def text_width(text, font):
        try:
            bb = font.getbbox(text)
            return bb[2] - bb[0], bb[3] - bb[1]
        except AttributeError:
            return font.getsize(text)

    # Draw title — centered vertically around middle
    title_lines = wrap_text(title, title_font, width - 60)
    line_h = text_width("A", title_font)[1] + 14
    total_h = len(title_lines) * line_h
    y = (height // 2) - (total_h // 2) - 30

    for line in title_lines:
        lw, _ = text_width(line, title_font)
        x = (width - lw) // 2
        # Shadow
        draw.text((x + 2, y + 2), line, font=title_font, fill=(0, 0, 0, 100))
        draw.text((x, y), line, font=title_font, fill=(255, 255, 255))
        y += line_h

    # Decorative separator line
    sep_y = height - 130
    draw.line([(width // 2 - 40, sep_y), (width // 2 + 40, sep_y)], fill=(255, 255, 255, 180), width=1)

    # Author name
    aw, _ = text_width(author, author_font)
    ax = (width - aw) // 2
    draw.text((ax + 1, height - 100 + 1), author, font=author_font, fill=(0, 0, 0, 80))
    draw.text((ax, height - 100), author, font=author_font, fill=(220, 220, 220))

    img.save(dest_path)
    print(f"  ✓ Generated cover: {dest_path}")


def fix_book(book_id, meta):
    folder_path = os.path.join(BAKBAK_BOOKS_DIR, book_id)
    details_path = os.path.join(folder_path, "details.json")

    if not os.path.isdir(folder_path):
        print(f"  ✗ Folder not found: {folder_path}")
        return False

    if not os.path.exists(details_path):
        print(f"  ✗ details.json not found: {details_path}")
        return False

    with open(details_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Update metadata fields
    data["title"] = meta["title"]
    data["author"] = meta["author"]
    data["genre"] = meta["genre"]
    data["coverColor"] = meta["cover_color"]
    data["description"] = meta["description"]

    # Generate new cover
    cover_path = os.path.join(folder_path, "cover.png")
    generate_cover(meta["title"], meta["author"], cover_path, meta["cover_color"])
    data["coverImage"] = f"books/{book_id}/cover.png"

    with open(details_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Updated details.json for {meta['title']}")
    return True


def main():
    print("=== Fixing book metadata and regenerating covers ===\n")
    fixed = []

    for book_id, meta in FIXES.items():
        print(f"Processing: {meta['title']}...")
        if fix_book(book_id, meta):
            fixed.append(book_id)
        print()

    if not fixed:
        print("Nothing fixed.")
        return

    print(f"Fixed {len(fixed)} books. Regenerating catalog.json...")
    subprocess.run(["python3", "scripts/generate_catalog.py"], check=True, cwd="/home/sb/AI-Works/bakbak.store")

    print("Staging and pushing to git...")
    subprocess.run(["git", "add", "books/", "scripts/fix_metadata.py"], check=True, cwd="/home/sb/AI-Works/bakbak.store")
    subprocess.run(
        ["git", "commit", "-m", f"Fix metadata and covers for {len(fixed)} books: correct authors, descriptions, genres and colors"],
        check=True, cwd="/home/sb/AI-Works/bakbak.store"
    )
    subprocess.run(["git", "push", "origin", "main"], check=True, cwd="/home/sb/AI-Works/bakbak.store")
    print("\n✓ Done! All fixes pushed to GitHub.")


if __name__ == "__main__":
    main()
