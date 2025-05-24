#PROJECT INSTRUCTIONS


0. Getting started with python generators
Objective: create a generator that streams rows from an SQL database one by one.

Instructions:

Write a python script that seed.py:

Set up the MySQL database, ALX_prodev with the table user_data with the following fields:
user_id(Primary Key, UUID, Indexed)
name (VARCHAR, NOT NULL)
email (VARCHAR, NOT NULL)
age (DECIMAL,NOT NULL)
Populate the database with the sample data from this user_data.csv
Prototypes:
def connect_db() :- connects to the mysql database server
def create_database(connection):- creates the database ALX_prodev if it does not exist
def connect_to_prodev() connects the the ALX_prodev database in MYSQL
def create_table(connection):- creates a table user_data if it does not exists with the required fields
def insert_data(connection, data):- inserts data in the database if it does not exist



1. Generator that streams rows from an SQL database
Objective: create a generator that streams rows from an SQL database one by one.

Instructions:

In 0-stream_users.py write a function that uses a generator to fetch rows one by one from the user_data table. You must use the Yield python generator

Prototype: def stream_users()
Your function should have no more than 1 loop


2. Batch processing Large Data
Objective: Create a generator to fetch and process data in batches from the users database

Instructions:

Write a function stream_users_in_batches(batch_size) that fetches rows in batches

Write a function batch_processing() that processes each batch to filter users over the age of25`

You must use no more than 3 loops in your code. Your script must use the yield generator

Prototypes:

def stream_users_in_batches(batch_size)
def batch_processing(batch_size)



3. Lazy loading Paginated Data
Objective: Simulte fetching paginated data from the users database using a generator to lazily load each page

Instructions:

Implement a generator function lazypaginate(pagesize) that implements the paginate_users(page_size, offset) that will only fetch the next page when needed at an offset of 0.

You must only use one loop
Include the paginate_users function in your code
You must use the yield generator
Prototype:
def lazy_paginate(page_size)



4. Memory-Efficient Aggregation with Generators
Objective: to use a generator to compute a memory-efficient aggregate function i.e average age for a large dataset

Instruction:

Implement a generator stream_user_ages() that yields user ages one by one.

Use the generator in a different function to calculate the average age without loading the entire dataset into memory

Your script should print Average age of users: average age

You must use no more than two loops in your script

You are not allowed to use the SQL AVERAGE