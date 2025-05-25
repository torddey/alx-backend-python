from datetime import datetime
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import functools

# Load environment variables from .env file
load_dotenv()

def log_queries():
    """Decorator to log SQL queries with timestamps before execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # The query is the first positional argument passed to the function
            query = args[0] if args else kwargs.get('query', 'Unknown query')
            # Get current timestamp and log the query
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] Executing query: {query}")
            # Call the original function with its arguments
            return func(*args, **kwargs)
        return wrapper
    return decorator

@log_queries()  # Invoke the decorator factory with parentheses
def fetch_all_users(query):
    """Fetch users from the user_data table using the provided query."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
    except Error as e:
        print(f"Error executing query: {e}")
        return []

# Fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM user_data")
print("Fetched users:", users)