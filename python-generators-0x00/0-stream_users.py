import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from itertools import islice

# Load environment variables from .env file
load_dotenv()


#Generator to stream rows one by one from the user_data table.
def stream_users():
    try:
        # Connect to the ALX_prodev database
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)  
            cursor.execute("SELECT * FROM user_data")
            
            # Single loop to fetch and yield each row
            for row in cursor:
                yield row

            cursor.close()
            connection.close()

    except Error as e:
        print(f"Error streaming data from database: {e}")
        return

#Demonstrate streaming users from the database with a limit of 6 rows
def main():
    print("Streaming the first 6 users from user_data table:")
    for user in islice(stream_users(), 6):
        print(user)

if __name__ == "__main__":
    main()