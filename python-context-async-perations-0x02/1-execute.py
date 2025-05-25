import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class ExecuteQuery:
    """Reusable context manager to execute a database query and manage connection."""
    def __init__(self, query, params):
        """Initialize with the query and parameters."""
        self.query = query
        self.params = params
        self.conn = None
        self.host = os.getenv("MYSQL_HOST")
        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.database = os.getenv("MYSQL_DATABASE")

    def __enter__(self):
        """Establish connection, execute query, and return results."""
        try:
            # Open database connection
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.conn.is_connected():
                cursor = self.conn.cursor(dictionary=True)
                cursor.execute(self.query, self.params)
                results = cursor.fetchall()
                cursor.close()
                return results
        except Error as e:
            print(f"Error executing query: {e}")
            raise  # Re-raise the exception to let the caller handle it

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the database connection when exiting the with block."""
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("Database connection closed")
        if exc_type is not None:
            print(f"Exception occurred: {exc_value}")

# Use the context manager to execute the query
query = "SELECT * FROM user_data WHERE age > %s"
params = (25,)

with ExecuteQuery(query, params) as results:
    print("Users with age > 25:", results)