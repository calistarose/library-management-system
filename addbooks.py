import tkinter as tk
from tkinter import messagebox
from dbconnection import create_connection, close_connection

def add_book_to_db(title, author, genre, published_date, isbn):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        add_book_query = """
        INSERT INTO books (title, author, genre, published_date, isbn, availability)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        book_data = (title, author, genre, published_date, isbn, True)
        cursor.execute(add_book_query, book_data)
        connection.commit()
        close_connection(connection)
        messagebox.showinfo("Success", "Book added successfully!")
    else:
        messagebox.showerror("Error", "Database connection failed")

def add_book():
    title = entry_title.get()
    author = entry_author.get()
    genre = entry_genre.get()
    published_date = entry_published_date.get()
    isbn = entry_isbn.get()

    if not all([title, author, genre, published_date, isbn]):
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    add_book_to_db(title, author, genre, published_date, isbn)

def add_book_screen(frame, back_command):
    tk.Label(frame, text="Add a New Book", font=('Arial', 20)).pack(pady=20)

    global entry_title, entry_author, entry_genre, entry_published_date, entry_isbn

    # Title Label and Entry
    tk.Label(frame, text="Title:").pack(pady=5)
    entry_title = tk.Entry(frame, width=30)
    entry_title.pack(pady=5)

    # Author Label and Entry
    tk.Label(frame, text="Author:").pack(pady=5)
    entry_author = tk.Entry(frame, width=30)
    entry_author.pack(pady=5)

    # Genre Label and Entry
    tk.Label(frame, text="Genre:").pack(pady=5)
    entry_genre = tk.Entry(frame, width=30)
    entry_genre.pack(pady=5)

    # Published Date Label and Entry
    tk.Label(frame, text="Published Date (YYYY-MM-DD):").pack(pady=5)
    entry_published_date = tk.Entry(frame, width=30)
    entry_published_date.pack(pady=5)

    # ISBN Label and Entry
    tk.Label(frame, text="ISBN:").pack(pady=5)
    entry_isbn = tk.Entry(frame, width=30)
    entry_isbn.pack(pady=5)

    # Add Book Button
    tk.Button(frame, text="Add Book", command=add_book).pack(pady=20)

    # Back Button
    tk.Button(frame, text="Back", command=back_command).pack(pady=10)
