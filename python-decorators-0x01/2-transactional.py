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

def transactional(func):
    """Decorator to manage database transactions with commit or rollback."""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Disable autocommit to start a transaction
            conn.autocommit = False
            # Execute the function
            result = func(conn, *args, **kwargs)
            # Commit the transaction if no errors occur
            conn.commit()
            print("Transaction committed successfully")
            return result
        except Exception as e:
            # Rollback the transaction if an error occurs
            conn.rollback()
            print(f"Transaction rolled back due to error: {e}")
            raise  # Re-raise the exception for debugging
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """Update user's email with automatic transaction handling."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("UPDATE user_data SET email = %s WHERE user_id = %s", (new_email, user_id))
    print(f"Updated email for user_id {user_id} to {new_email}")
    return True

# Update user's email with automatic transaction handling
try:
    update_user_email(user_id="09234e50-34eb-4ce2-94ec-26e3fa749796", new_email="Crawford_Cartwright@hotmail.com")
except Exception as e:
    print(f"Failed to update email: {e}")
finally:
    print("Operation completed")