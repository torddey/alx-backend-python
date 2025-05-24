import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


#Generator to stream user ages one by one from the user_data table.
def stream_user_ages():
    try:
        # Connect to the ALX_prodev database
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT age FROM user_data")
            
            # Loop 1: Yield each age one by one
            for (age,) in cursor:
                yield float(age)  # Convert DECIMAL to float for calculation

            cursor.close()
            connection.close()

    except Error as e:
        print(f"Error streaming ages from database: {e}")
        return


#Calculate the average age using the stream_user_ages generator.
def calculate_average_age():
    total = 0
    count = 0
    
    # Loop 2: Iterate over ages to compute running sum and count
    for age in stream_user_ages():
        total += age
        count += 1
    
    # Calculate average
    if count == 0:
        return 0  # Avoid division by zero
    return total / count


#Calculate and print the average age of users.
def main():
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age:.2f}")

if __name__ == "__main__":
    main()