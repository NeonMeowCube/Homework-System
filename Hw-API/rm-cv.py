from tinydb import TinyDB, Query

db = TinyDB('db/hw.json')
Entry = Query()

# Get all entries
all_entries = db.all()

# Track seen keys and store actual docs to delete
seen = set()
to_remove = []

for entry in all_entries:
    # Define what makes an entry a "duplicate"
    key = (entry.get('date'), entry.get('text'))
    
    if key in seen:
        to_remove.append(entry.doc_id)  # Collect doc_id only
    else:
        seen.add(key)

# Remove duplicates by doc_id
db.remove(doc_ids=to_remove)

print(f"✅ Removed {len(to_remove)} duplicates.")
