import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()

#Generator to fetch rows from user_data table in batches.
def stream_users_in_batches(batch_size):
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
            
            # Loop 1: Fetch rows and accumulate into batches
            batch = []
            for row in cursor:
                batch.append(row)
                if len(batch) == batch_size:
                    yield batch
                    batch = []
            
            # Yield any remaining rows as the last batch
            if batch:
                yield batch

            cursor.close()
            connection.close()

    except Error as e:
        print(f"Error fetching data from database: {e}")
        return


#Process batches to filter users over the age of 25.
def batch_processing(batch_size):
    # Loop 2: Iterate over batches from the generator
    for batch in stream_users_in_batches(batch_size):
        # Loop 3: Filter users in the batch with age > 25
        filtered_batch = [user for user in batch if user['age'] > 25]
        if filtered_batch:  # Only yield if the filtered batch is not empty
            yield filtered_batch



#Demonstrate batch processing with a batch size of 50.
def main():
    try:
        print("Processing users in a batch of 50")
        for batch in batch_processing(50):
            for user in batch:
                print(user)
    except BrokenPipeError:
        sys.stderr.close()

if __name__ == "__main__":
    main()