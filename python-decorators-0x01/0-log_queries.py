import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import functools

# Load environment variables from .env file
load_dotenv()

# Decorator to log SQL queries before execution.
def log_queries():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            query = args[0] if args else kwargs.get('query', 'Unknown query')
            print(f"Executing query: {query}")            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Function to fetch all users from the user_data table with logging
@log_queries()  
def fetch_all_users(query):
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