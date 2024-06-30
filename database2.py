from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import sql
import datetime
from urllib.parse import urlparse

load_dotenv()

class PostgresDatabase:
    def __init__(self):
        db_url = os.getenv('DATABASE_URL')
        result = urlparse(db_url)
        self.dbname = result.path[1:]
        self.user = result.username
        self.password = result.password
        self.host = result.hostname
        self.port = result.port
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print("Database connection successful.")
        except psycopg2.OperationalError as error:
            print(f"OperationalError: {error}")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"DatabaseError: {error}")
        finally:
            if not self.connection:
                print("Connection failed, please check the connection details and server status.")

    def create_database(self, new_dbname):
        try:
            temp_conn = psycopg2.connect(
                dbname='postgres',
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            temp_conn.autocommit = True
            temp_cursor = temp_conn.cursor()
            
            temp_cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(new_dbname)
            ))

            temp_cursor.close()
            temp_conn.close()
            print(f"Database {new_dbname} created successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")

    def create_table(self, create_table_sql):
        try:
            self.cursor.execute(create_table_sql)
            self.connection.commit()
            print("Table created successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")
            self.connection.rollback()

    def save_message(self, user_id, conversation_id, role, content):
        try:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            insert_sql = sql.SQL("INSERT INTO chat_messages (user_id, conversation_id, role, content, timestamp) VALUES (%s, %s, %s, %s, %s)")
            self.cursor.execute(insert_sql, (user_id, conversation_id, role, content, timestamp))
            self.connection.commit()
            print("Message saved successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")
            self.connection.rollback()

    def get_message_history(self, user_id, conversation_id):
        try:
            select_sql = sql.SQL("SELECT role, content, timestamp FROM chat_messages WHERE user_id = %s AND conversation_id = %s ORDER BY id")
            self.cursor.execute(select_sql, (user_id, conversation_id))
            messages = self.cursor.fetchall()
            print("Message history retrieved successfully.")
            
            return [{"role": message[0], "content": message[1], "timestamp": message[2].isoformat()} for message in messages]
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")
            self.connection.rollback()
            return []

    def user_exists(self, user_id):
        try:
            select_sql = sql.SQL("SELECT 1 FROM chat_messages WHERE user_id = %s LIMIT 1")
            self.cursor.execute(select_sql, (user_id,))
            exists = self.cursor.fetchone() is not None
            return exists
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")
            self.connection.rollback()
            return False
        
        
    def clear_message_history(self, user_id, conversation_id):
        try:
            delete_sql = sql.SQL("DELETE FROM chat_messages WHERE user_id = %s AND conversation_id = %s")
            self.cursor.execute(delete_sql, (user_id, conversation_id))
            self.connection.commit()
            print("Message history cleared successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
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
#     # pass
    db = PostgresDatabase()
    db.connect()

#     create_table_sql_chat = '''
#     CREATE TABLE chat_messages (
#         id SERIAL PRIMARY KEY,
#         user_id VARCHAR(255) NOT NULL,
#         conversation_id VARCHAR(255) NOT NULL,
#         role VARCHAR(50) NOT NULL,  -- 'user' or 'assistant'
#         content TEXT NOT NULL,
#         tags TEXT[] DEFAULT '{}',  -- Array of tags
#         timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
#     );
#     '''
#     # # Uncomment the line below to create the table
#     db.create_table(create_table_sql_chat)

    # # Save a message
    # db.save_message("user124", "default", "assistant", "The user is new")

    # # Retrieve message history
    # history = db.get_message_history('hello', 'profile_evaluation_hello')
    # user_id = 'user123'
    # history = db.get_message_history(user_id, f"profile_evaluation_{user_id}")
    # # db.save_message('user123',f'question_answer_chapter_chapter_1_user_123','assistant',"response")
    # print(history)
    # # print(len(history))
    # al = []
    # for message in history:
    #     al.append(message['content'][1:-1])
    # print(type(al))
    #     print('user')

    # db.close()
    
    

