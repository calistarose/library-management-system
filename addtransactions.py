import tkinter as tk
from tkinter import ttk, messagebox
from dbconnection import create_connection, close_connection

def fetch_books_and_borrowers():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Fetch book titles and IDs
        cursor.execute("SELECT id, title FROM books")
        books = cursor.fetchall()  # [(book_id, book_title), ...]
        
        # Fetch borrower names and IDs
        cursor.execute("SELECT id, CONCAT(first_name, ' ', last_name) AS name FROM borrowers")
        borrowers = cursor.fetchall()  # [(borrower_id, borrower_name), ...]
        
        close_connection(connection)
        return books, borrowers
    else:
        messagebox.showerror("Error", "Database connection failed")
        return [], []

def add_transaction_to_db(book_id, borrower_id, borrow_date, return_date):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Check if the book is currently borrowed and not returned
        cursor.execute("SELECT status FROM transactions WHERE book_id = %s ORDER BY id DESC LIMIT 1", (book_id,))
        last_status = cursor.fetchone()
        
        if last_status and last_status[0] == 'borrowed':
            messagebox.showerror("Error", "This book is currently borrowed and cannot be borrowed again until it's returned.")
            close_connection(connection)
            return
        
        # If not borrowed, insert a new transaction
        add_transaction_query = """
        INSERT INTO transactions (book_id, borrower_id, borrow_date, return_date, status)
        VALUES (%s, %s, %s, %s, 'borrowed')
        """
        transaction_data = (book_id, borrower_id, borrow_date, return_date)
        cursor.execute(add_transaction_query, transaction_data)
        connection.commit()
        close_connection(connection)
        messagebox.showinfo("Success", "Transaction added successfully!")
    else:
        messagebox.showerror("Error", "Database connection failed")

def add_transaction_page(frame, back_command):
    for widget in frame.winfo_children():
        widget.destroy()  # Clear the frame

    tk.Label(frame, text="Borrow Book", font=('Arial', 20)).pack(pady=20)

    books, borrowers = fetch_books_and_borrowers()

    tk.Label(frame, text="Select Book:").pack(pady=5)
    entry_book_id = ttk.Combobox(frame, values=[f"{book[1]}" for book in books], width=30)
    entry_book_id.pack(pady=5)

    tk.Label(frame, text="Select Borrower:").pack(pady=5)
    entry_borrower_id = ttk.Combobox(frame, values=[f"{borrower[1]}" for borrower in borrowers], width=30)
    entry_borrower_id.pack(pady=5)

    tk.Label(frame, text="Borrow Date:").pack(pady=5)
    entry_borrow_date = tk.Entry(frame, width=30)
    entry_borrow_date.pack(pady=5)

    tk.Label(frame, text="Return Date:").pack(pady=5)
    entry_return_date = tk.Entry(frame, width=30)
    entry_return_date.pack(pady=5)

    # Add Transaction Button
    tk.Button(frame, text="Add Transaction", command=lambda: add_transaction_with_ids(entry_book_id, entry_borrower_id, entry_borrow_date, entry_return_date)).pack(pady=20)

    # Back Button
    tk.Button(frame, text="Back", command=back_command).pack(pady=10)

def add_transaction_with_ids(book_id_entry, borrower_id_entry, borrow_date_entry, return_date_entry):
    book_title = book_id_entry.get()
    borrower_name = borrower_id_entry.get()
    borrow_date = borrow_date_entry.get()
    return_date = return_date_entry.get()

    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # Fetch the corresponding book ID and borrower ID from titles/names
        cursor.execute("SELECT id FROM books WHERE title = %s", (book_title,))
        book_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM borrowers WHERE CONCAT(first_name, ' ', last_name) = %s", (borrower_name,))
        borrower_id = cursor.fetchone()[0]

        # Insert transaction with status set to 'borrowed'
        add_transaction_to_db(book_id, borrower_id, borrow_date, return_date)
    else:
        messagebox.showerror("Error", "Database connection failed")

# Assuming `manage_transactions_screen` is your main page function
def manage_transactions_screen(frame, back_command):
    for widget in frame.winfo_children():
        widget.destroy()  # Clear the frame

    tk.Label(frame, text="Transactions", font=('Arial', 20)).pack(pady=20)

    # Button to open the Add Transaction page (Borrow Book)
    tk.Button(frame, text="Borrow Book", command=lambda: add_transaction_page(frame, back_command)).pack(pady=10)

    # Other elements like transaction list, search functionality, etc. can go here

    # Back Button
    tk.Button(frame, text="Back", command=back_command).pack(pady=10)
