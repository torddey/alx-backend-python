import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import functools

# Load environment variables from .env file
load_dotenv()

def with_db_connection(func):
    """Decorator to automatically handle opening and closing database connections."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        connection = None
        try:
            # Open database connection
            connection = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE")
            )
            if connection.is_connected():
                # Pass the connection as the first argument to the function
                return func(connection, *args, **kwargs)
        except Error as e:
            print(f"Error opening database connection: {e}")
            return None
        finally:
            # Close the connection if it was opened
            if connection and connection.is_connected():
                connection.close()
                print("Database connection closed")
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    """Fetch user by ID with automatic connection handling."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data WHERE user_id = %s", (user_id,))
    return cursor.fetchone()

# Fetch user by ID with automatic connection handling
user = get_user_by_id(user_id="09234e50-34eb-4ce2-94ec-26e3fa749796")  # Example UUID from previous data
print("Fetched user:", user)