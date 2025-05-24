import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

#Fetch a page of users from the user_data table.
def paginate_users(page_size, offset):
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
            cursor.execute(query, (page_size, offset))
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
    except Error as e:
        print(f"Error fetching page from database: {e}")
        return []


#Generator to lazily load paginated users from the user_data table.
def lazy_paginate(page_size):
    offset = 0
    # Loop 1: Iterate over page numbers to fetch each page lazily
    while True:
        page = paginate_users(page_size, offset)
        if not page:  # Stop if no more rows are returned
            break
        yield page
        offset += page_size


#Demonstrate lazy pagination with a page size of 5.
def main():
    print("Lazy loading paginated users:")
    for page in lazy_paginate(5):
        for user in page:
            print(user)

if __name__ == "__main__":
    main()