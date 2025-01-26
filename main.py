import sqlite3
import shutil
import os
import time

# Database filename
DB_NAME = "test.db"
DB_COPY = "test-2.db"

def create_and_write_db():
    # First connection with WAL mode
    conn1 = sqlite3.connect(DB_NAME)
    
    # Enable WAL mode
    conn1.execute("PRAGMA journal_mode=WAL")
    
    # Create a test table
    conn1.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            data TEXT
        )
    """)
    
    # Write some data
    print("Writing data with first connection...")
    conn1.execute("INSERT INTO test_table (data) VALUES (?)", ("test data 1",))
    conn1.execute("INSERT INTO test_table (data) VALUES (?)", ("test data 2",))
    conn1.commit()
    
    # Create an empty database file for the second connection
    print("\nCreating empty database file for second connection...")
    empty_conn = sqlite3.connect(DB_COPY)
    empty_conn.close()
    
    # Second connection to the copied database BEFORE copying
    print("\nOpening second connection in read-only mode...")
    conn2 = sqlite3.connect(f"file:{DB_COPY}?mode=ro", uri=True)
    cursor2 = conn2.cursor()
    
    # Try to read data BEFORE copying
    print("\nTrying to read from copied database BEFORE copying...")
    try:
        cursor2.execute("SELECT * FROM test_table")
        rows = cursor2.fetchall()
        print(f"Rows in copied database before copy: {rows}")
    except sqlite3.OperationalError as e:
        print(f"Expected error - {e}")
    
    # Copy database files while both connections are open
    print("\nCopying database files...")
    for ext in ['', '-wal', '-shm']:
        source = f"{DB_NAME}{ext}"
        dest = f"{DB_COPY}{ext}"
        if os.path.exists(source):
            shutil.copy2(source, dest)
            print(f"Copied {source} to {dest}")
    
    # Try to read data from the copied database
    print("\nTrying to read from copied database AFTER copying...")
    cursor2.execute("SELECT * FROM test_table")
    rows = cursor2.fetchall()
    print(f"Rows in copied database after copy: {rows}")
    
    # Write more data with first connection
    print("\nWriting additional data with first connection...")
    conn1.execute("INSERT INTO test_table (data) VALUES (?)", ("test data 3",))
    conn1.commit()
    
    # Copy database files again
    print("\nCopying database files again...")
    for ext in ['', '-wal', '-shm']:
        source = f"{DB_NAME}{ext}"
        dest = f"{DB_COPY}{ext}"
        if os.path.exists(source):
            shutil.copy2(source, dest)
            print(f"Copied {source} to {dest}")
    
    # Try to read data after second copy
    print("\nTrying to read from copied database after second copy...")
    cursor2.execute("SELECT * FROM test_table")
    rows = cursor2.fetchall()
    print(f"Rows in copied database after second copy: {rows}")
    
    # Clean up
    conn2.close()
    conn1.close()
    
    # Clean up files
    for ext in ['', '-wal', '-shm']:
        for prefix in [DB_NAME, DB_COPY]:
            file = f"{prefix}{ext}"
            if os.path.exists(file):
                os.remove(file)
                print(f"Removed {file}")

if __name__ == "__main__":
    create_and_write_db()
