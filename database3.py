import sqlite3
import datetime
from urllib.parse import urlparse

class SQLiteDatabase:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, db_file):
        try:
            self.connection = sqlite3.connect(db_file)
            self.cursor = self.connection.cursor()
            print("Database connection successful.")
        except sqlite3.Error as error:
            print(f"Error: {error}")

    def create_database(self, new_dbname):
        # For SQLite, creating a new database is simply connecting to a new file
        self.connect(new_dbname)
        print(f"Database {new_dbname} created successfully.")

    def create_table(self, create_table_sql):
        try:
            self.cursor.execute(create_table_sql)
            self.connection.commit()
            print("Table created successfully.")
        except sqlite3.Error as error:
            print(f"Error: {error}")
            self.connection.rollback()

    def save_message(self, user_id, conversation_id, role, content):
        try:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            insert_sql = "INSERT INTO chat_messages (user_id, conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)"
            self.cursor.execute(insert_sql, (user_id, conversation_id, role, content, timestamp))
            self.connection.commit()
            print("Message saved successfully.")
        except sqlite3.Error as error:
            print(f"Error: {error}")
            self.connection.rollback()

    def get_message_history(self, user_id, conversation_id):
        try:
            select_sql = "SELECT role, content, timestamp FROM chat_messages WHERE user_id = ? AND conversation_id = ? ORDER BY id"
            self.cursor.execute(select_sql, (user_id, conversation_id))
            messages = self.cursor.fetchall()
            print("Message history retrieved successfully.")
            
            return [{"role": message[0], "content": message[1], "timestamp": message[2]} for message in messages]
        except sqlite3.Error as error:
            print(f"Error: {error}")
            self.connection.rollback()
            return []

    def user_exists(self, user_id):
        try:
            select_sql = "SELECT 1 FROM chat_messages WHERE user_id = ? LIMIT 1"
            self.cursor.execute(select_sql, (user_id,))
            exists = self.cursor.fetchone() is not None
            return exists
        except sqlite3.Error as error:
            print(f"Error: {error}")
            self.connection.rollback()
            return False
        
    def clear_message_history(self, user_id, conversation_id):
        try:
            delete_sql = "DELETE FROM chat_messages WHERE user_id = ? AND conversation_id = ?"
            self.cursor.execute(delete_sql, (user_id, conversation_id))
            self.connection.commit()
            print("Message history cleared successfully.")
        except sqlite3.Error as error:
            print(f"Error: {error}")
            self.connection.rollback()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")

# Example usage:
if __name__ == '__main__':
    db = SQLiteDatabase()
    db.connect('chat_database.db')

    # create_table_sql = """
    # CREATE TABLE IF NOT EXISTS chat_messages (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     user_id TEXT NOT NULL,
    #     conversation_id TEXT NOT NULL,
    #     role TEXT NOT NULL,
    #     content TEXT NOT NULL,
    #     timestamp TEXT NOT NULL
    # );
    # """
    # db.create_table(create_table_sql)
    
    # Test the database operations
    db.save_message('user123', 'conv456', 'user', 'Hello, how are you?')
    # history = db.get_message_history('user123', 'conv456')
    # print(history)
    # # db.clear_message_history('user123', 'conv456')
    # db.close()
