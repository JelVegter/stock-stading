import psycopg2
import os

# Database connection parameters
db_host = "stocktrading-db-dev-eu.cwixl1k0d3ug.eu-central-1.rds.amazonaws.com"  # Replace with your RDS instance's endpoint
db_port = 5432
db_name = "stocktrading"
db_user = "edu"
db_password = "password"

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port
)

# Create a new table and insert some data
with conn.cursor() as cursor:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """
    )
    cursor.execute("INSERT INTO users (name) VALUES (%s)", ("John Doe",))

# Commit the changes
conn.commit()

# Query the table and print the results
with conn.cursor() as cursor:
    cursor.execute("SELECT * FROM users;")
    rows = cursor.fetchall()

    for row in rows:
        print(f"User: {row[1]}")

# Close the connection
conn.close()
