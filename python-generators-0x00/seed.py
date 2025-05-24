import mysql.connector
import csv
import uuid
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()


#Connect to the MySQL server
def connect_db():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD")
        )
        if connection.is_connected():
            print("Successfully connected to MySQL server")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL server: {e}")
        return None


#Create the ALX_prodev database if it does not exist
def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created or already exists")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")

def connect_to_prodev():
    """Connect to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        if connection.is_connected():
            print("Successfully connected to ALX_prodev database")
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None


#Create the user_data table if it does not exist,
def create_table(connection):
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5,2) NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table user_data created or already exists")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")



#Generator to read CSV file row by row
def csv_reader_generator(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            try:
                yield {
                    'user_id': str(uuid.uuid4()),  # Generate a new UUID for each row
                    'name': row['name'],
                    'email': row['email'],
                    'age': float(row['age'])
                }
            except KeyError as e:
                print(f"Missing column {e} in row, skipping")
                continue
            except ValueError:
                print(f"Invalid age value in row: {row['age']}, skipping")
                continue



#Insert data into the user_data table if it does not exist.
def insert_data(connection, data):
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO user_data (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
        """
        for row in data:
            cursor.execute("SELECT user_id FROM user_data WHERE user_id = %s", (row['user_id'],))   #Check if user_id already exists
            if cursor.fetchone():
                print(f"User ID {row['user_id']} already exists, skipping")
                continue
            cursor.execute(insert_query, (row['user_id'], row['name'], row['email'], row['age']))
            print(f"Inserted data for {row['name']}")
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error inserting data: {e}")

def main():
    # Step 1: Connect to MySQL server
    connection = connect_db()
    if not connection:
        return

    # Step 2: Create ALX_prodev database
    create_database(connection)
    connection.close()

    # Step 3: Connect to ALX_prodev database
    connection = connect_to_prodev()
    if not connection:
        return

    # Step 4: Create user_data table
    create_table(connection)

    # Step 5: Read CSV using generator and insert data
    csv_file_path = "user_data.csv"  
    data_generator = csv_reader_generator(csv_file_path)
    insert_data(connection, data_generator)

    # Step 6: Close the connection
    if connection.is_connected():
        connection.close()
        print("MySQL connection closed")

if __name__ == "__main__":
    main()