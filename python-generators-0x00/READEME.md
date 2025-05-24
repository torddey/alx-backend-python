# Project Instructions

## 0. Getting Started with Python Generators

**Objective:**  
Create a generator that streams rows from an SQL database one by one.

**Instructions:**

Write a Python script named `seed.py` that:

1. **Sets up the MySQL database** `ALX_prodev` with a table `user_data` containing:
    - `user_id` (Primary Key, UUID, Indexed)
    - `name` (VARCHAR, NOT NULL)
    - `email` (VARCHAR, NOT NULL)
    - `age` (DECIMAL, NOT NULL)
2. **Populates the database** with sample data from `user_data.csv`.

**Function Prototypes:**
- `def connect_db()`: Connects to the MySQL database server.
- `def create_database(connection)`: Creates the database `ALX_prodev` if it does not exist.
- `def connect_to_prodev()`: Connects to the `ALX_prodev` database in MySQL.
- `def create_table(connection)`: Creates the `user_data` table if it does not exist with the required fields.
- `def insert_data(connection, data)`: Inserts data into the database if it does not exist.

---

## 1. Generator that Streams Rows from an SQL Database

**Objective:**  
Create a generator that streams rows from an SQL database one by one.

**Instructions:**

- In `0-stream_users.py`, write a function that uses a generator to fetch rows one by one from the `user_data` table.
- You must use the `yield` Python generator.

**Prototype:**  
`def stream_users()`

- Your function should have no more than 1 loop.

---

## 2. Batch Processing Large Data

**Objective:**  
Create a generator to fetch and process data in batches from the users database.

**Instructions:**

- Write a function `stream_users_in_batches(batch_size)` that fetches rows in batches.
- Write a function `batch_processing(batch_size)` that processes each batch to filter users over the age of 25.
- You must use no more than 3 loops in your code.
- Your script must use the `yield` generator.

**Prototypes:**
- `def stream_users_in_batches(batch_size)`
- `def batch_processing(batch_size)`

---

## 3. Lazy Loading Paginated Data

**Objective:**  
Simulate fetching paginated data from the users database using a generator to lazily load each page.

**Instructions:**

- Implement a generator function `lazy_paginate(page_size)` that uses `paginate_users(page_size, offset)` to fetch the next page only when needed, starting at offset 0.
- You must only use one loop.
- Include the `paginate_users` function in your code.
- You must use the `yield` generator.

**Prototype:**  
`def lazy_paginate(page_size)`

---

## 4. Memory-Efficient Aggregation with Generators

**Objective:**  
Use a generator to compute a memory-efficient aggregate function (e.g., average age) for a large dataset.

**Instructions:**

- Implement a generator `stream_user_ages()` that yields user ages one by one.
- Use the generator in a different function to calculate the average age without loading the entire dataset into memory.
- Your script should print:  
  `Average age of users: <average age>`
- You must use no more than two loops in your script.
- **Do not use the SQL `AVERAGE` function.**