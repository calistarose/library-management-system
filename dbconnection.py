# db_connection.py
import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        # Connection details should match your XAMPP settings
        connection = mysql.connector.connect(
            host='localhost',          # Your host, usually 'localhost'
            user='root',               # Default XAMPP username
            password='',               # Default is no password
            database='library_management'   # Your database name
        )
        if connection.is_connected():
            print("Connected to the database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()
        print("Database connection closed")
