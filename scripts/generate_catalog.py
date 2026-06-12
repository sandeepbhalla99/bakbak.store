import os
import json

BOOKS_DIR = "/home/sb/AI-Works/bakbak.store/books"
OUTPUT_FILE = os.path.join(BOOKS_DIR, "catalog.json")

def main():
    catalog = []
    
    # Iterate through all subdirectories in the books folder
    for folder in os.listdir(BOOKS_DIR):
        folder_path = os.path.join(BOOKS_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
            
        details_file = os.path.join(folder_path, "details.json")
        if not os.path.exists(details_file):
            continue
            
        try:
            with open(details_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract only the summary metadata (no chapters list to keep catalog.json small)
            summary = {
                "id": data["id"],
                "title": data["title"],
                "author": data["author"],
                "genre": data["genre"],
                "coverColor": data["coverColor"],
                "description": data["description"],
                "rating": 4.5, # default mock rating
                "reviewsCount": 12 # default mock reviews count
            }
            catalog.append(summary)
        except Exception as e:
            print(f"Error reading {details_file}: {e}")
            
    # Write the compiled catalog.json
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)
        
    print(f"Compiled {len(catalog)} books into {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
