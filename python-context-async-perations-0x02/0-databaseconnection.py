import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class DatabaseConnection:
    """Custom context manager to handle database connections automatically."""
    def __init__(self):
        """Initialize connection parameters from environment variables."""
        self.conn = None
        self.host = os.getenv("MYSQL_HOST")
        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.database = os.getenv("MYSQL_DATABASE")

    def __enter__(self):
        """Establish database connection when entering the with block."""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.conn.is_connected():
                print("Database connection established")
                return self.conn
        except Error as e:
            print(f"Error connecting to database: {e}")
            raise  # Re-raise the exception to let the caller handle it

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the database connection when exiting the with block."""
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("Database connection closed")
        if exc_type is not None:
            print(f"Exception occurred: {exc_value}")

# Use the context manager to perform a query
with DatabaseConnection() as conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    print("Query results:", results)