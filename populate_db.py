import os
import random
import urllib.parse
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models

# Recreate tables to apply the new thumbnail_url schema and clear old data
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

repo_path = r"C:\Users\vasan\AR-Furniture-Models"
base_raw_url = "https://raw.githubusercontent.com/Vasanth1817/AR-Furniture-Models/main/"

categories = ["Beds", "Chairs", "Cupboards", "DiningSets", "Sofas", "Tables"]

def get_random_price(category):
    if category == "Beds": return f"Rs. {random.randint(15, 60)},000"
    if category == "Sofas": return f"Rs. {random.randint(20, 80)},000"
    if category == "Chairs": return f"Rs. {random.randint(3, 12)},500"
    if category == "Tables": return f"Rs. {random.randint(5, 30)},000"
    if category == "DiningSets": return f"Rs. {random.randint(40, 120)},000"
    if category == "Cupboards": return f"Rs. {random.randint(10, 35)},000"
    return f"Rs. {random.randint(1, 10)},000"

# Scan the repository
added_count = 0
for category in categories:
    cat_path = os.path.join(repo_path, category)
    if not os.path.exists(cat_path):
        continue
        
    for filename in os.listdir(cat_path):
        if filename.endswith(".glb"):
            # Format Name: "VictorianBed_1.glb" -> "Victorian Bed 1"
            base_name = filename.replace(".glb", "")
            # Add spaces before capital letters for camel case reading
            import re
            readable_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', base_name).replace("_", " ").strip()
            
            # Create URL safe strings
            encoded_path = f"{category}/{urllib.parse.quote(filename)}"
            model_url = base_raw_url + encoded_path
            
            # Create a placeholder thumbnail with the item's name written on it
            safe_name = urllib.parse.quote_plus(readable_name)
            thumbnail_url = f"https://dummyimage.com/300x300/333333/ffffff.png&text={safe_name}"
            
            price = get_random_price(category)
            
            # Insert into Database
            item = models.Furniture(
                name=readable_name,
                price=price,
                model_url=model_url,
                thumbnail_url=thumbnail_url,
                category=category
            )
            db.add(item)
            added_count += 1

db.commit()
db.close()
print(f"Successfully populated database with {added_count} items!")
