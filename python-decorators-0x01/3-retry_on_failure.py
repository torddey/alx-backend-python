import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import functools
import time

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

def retry_on_failure(retries=3, delay=2):
    """Decorator to retry a function on failure with a specified number of retries and delay."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    # Attempt to execute the function
                    return func(*args, **kwargs)
                except Error as e:
                    last_exception = e
                    attempt_num = attempt + 1
                    if attempt_num == retries:
                        print(f"Max retries ({retries}) reached. Last error: {e}")
                        raise  # Re-raise the last exception after all retries
                    print(f"Attempt {attempt_num} failed. Retrying in {delay} seconds...")
                    time.sleep(delay)
            raise last_exception  # This line is technically unreachable due to the raise above, but included for clarity
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)  # Adjusted delay to 1 second as per instructions
def fetch_users_with_retry(conn):
    """Fetch users from the user_data table with automatic retry on failure."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")
    return cursor.fetchall()

# Attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print("Fetched users:", users)