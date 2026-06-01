import sqlite3

def run():
    conn = sqlite3.connect('C:/Users/vasan/RoomifyBackend/furniture.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE saved_layouts ADD COLUMN mode VARCHAR DEFAULT 'AR'")
        print("Column 'mode' added successfully!")
    except Exception as e:
        print("Error or already exists:", e)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run()
