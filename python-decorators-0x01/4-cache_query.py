import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import functools
import time

# Load environment variables from .env file
load_dotenv()

# Cache dictionary to store query results
query_cache = {}

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

def cache_query(func):
    """Decorator to cache the results of database queries based on the query string."""
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        # Check if the query is already in the cache
        if query in query_cache:
            print(f"Returning cached result for query: {query}")
            return query_cache[query]
        
        # If not cached, execute the function and cache the result
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        print(f"Cached result for query: {query}")
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """Fetch users from the user_data table with caching."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    return cursor.fetchall()

# First call will cache the result
print("First call (should query the database):")
users = fetch_users_with_cache(query="SELECT * FROM user_data")
print("Fetched users:", users)

# Second call will use the cached result
print("\nSecond call (should use cached result):")
users_again = fetch_users_with_cache(query="SELECT * FROM user_data")
print("Fetched users:", users_again)