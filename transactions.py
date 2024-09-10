import tkinter as tk
from tkinter import ttk, messagebox
from dbconnection import create_connection, close_connection
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from addtransactions import add_transaction_page
import nltk
nltk.download('stopwords')
nltk.download('punkt')

def fetch_transactions(treeview, search_query=None):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Base query to select transactions with book titles and borrower details
        query = """
        SELECT t.id, CONCAT(b.first_name, ' ', b.last_name) AS borrower_name, bk.title AS book_title, t.borrow_date, t.return_date, t.status
        FROM transactions t
        JOIN borrowers b ON t.borrower_id = b.id
        JOIN books bk ON t.book_id = bk.id
        """
        
        parameters = []  # Initialize parameters

        # If a search query is provided, process it with NLTK
        if search_query:
            stop_words = set(stopwords.words('english'))
            query_tokens = word_tokenize(search_query.lower())
            filtered_words = [word for word in query_tokens if word.isalnum() and word not in stop_words]
            
            if filtered_words:
                like_query = " OR ".join([f"LOWER(b.first_name) LIKE %s OR LOWER(b.last_name) LIKE %s OR LOWER(bk.title) LIKE %s" for _ in filtered_words])
                query += f" WHERE {like_query}"
                parameters = [f"%{word.lower()}%" for word in filtered_words] * 3  # Repeat for each column being searched

        # Execute the query and fetch results
        cursor.execute(query, parameters)
        transactions = cursor.fetchall()
        
        # Clear existing Treeview data
        treeview.delete(*treeview.get_children())

        # Insert fetched transactions into the Treeview
        for transaction in transactions:
            treeview.insert("", tk.END, values=transaction)

        close_connection(connection)


def search_transactions(treeview, search_entry):
    search_query = search_entry.get()
    fetch_transactions(treeview, search_query)

def fetch_borrowed_books():
    """Fetch titles of books that are currently borrowed."""
    connection = create_connection()
    borrowed_books = []
    if connection:
        cursor = connection.cursor()
        
        # Query to select borrowed books
        query = """
        SELECT t.id, b.title 
        FROM transactions t 
        JOIN books b ON t.book_id = b.id 
        WHERE t.status = 'Borrowed'
        """
        
        cursor.execute(query)
        borrowed_books = cursor.fetchall()
        close_connection(connection)
    
    return borrowed_books

def return_selected_book(transaction_id, treeview, return_frame):
    """Update the status of the selected book to 'Returned'."""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Update the status of the selected book
        update_query = "UPDATE transactions SET status = 'Returned' WHERE id = %s"
        cursor.execute(update_query, (transaction_id,))
        connection.commit()
        close_connection(connection)

        # Refresh the transaction list to reflect the change
        fetch_transactions(treeview)
        
        # Show success message
        messagebox.showinfo("Success", "Book successfully returned!")

        # Refresh the return books page
        return_books_page(return_frame, lambda: manage_transactions_screen(return_frame, lambda: manage_transactions_screen(return_frame, None)))

def return_books_page(frame, back_command):
    """Display the Return Books page."""
    for widget in frame.winfo_children():
        widget.destroy()  # Clear the frame

    tk.Label(frame, text="Return Books", font=('Arial', 20)).pack(pady=20)

    return_frame = tk.Frame(frame)
    return_frame.pack(pady=10)

    # Fetch borrowed books
    borrowed_books = fetch_borrowed_books()

    if borrowed_books:
        tk.Label(return_frame, text="Select a book to return:", font=('Arial', 14)).pack(pady=10)
        
        # Dropdown menu for selecting borrowed books
        selected_book = tk.StringVar()
        dropdown = ttk.Combobox(return_frame, textvariable=selected_book, state="readonly")
        dropdown['values'] = [f"{book_id} - {title}" for book_id, title in borrowed_books]
        dropdown.pack(pady=10)

        # Button to confirm the return
        tk.Button(return_frame, text="Return Book", 
                  command=lambda: return_selected_book(
                      int(selected_book.get().split(" - ")[0]), frame.winfo_toplevel().winfo_children()[1], return_frame)).pack(pady=10)
    else:
        tk.Label(return_frame, text="No books currently borrowed.", font=('Arial', 14)).pack(pady=10)
    
    # Back Button to go back to the manage transactions screen
    tk.Button(frame, text="Back", command=back_command).pack(pady=10)

def manage_transactions_screen(frame, back_command):
    for widget in frame.winfo_children():
        widget.destroy()  # Clear the frame

    tk.Label(frame, text="Transactions", font=('Arial', 20)).pack(pady=20)

    # Create a frame for the search bar and button
    search_frame = tk.Frame(frame)
    search_frame.pack(pady=10)

    # Search entry box
    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side=tk.LEFT, padx=10)

    # Search button
    search_button = tk.Button(search_frame, text="Search", command=lambda: search_transactions(treeview, search_entry))
    search_button.pack(side=tk.LEFT)

    # Define columns for the Transactions Treeview
    columns = ("id", "Borrower Name", "Book Title", "Borrow Date", "Return Date", "Status")
    treeview = ttk.Treeview(frame, columns=columns, show="headings")
    
    treeview.heading("id", text="ID")
    treeview.heading("Borrower Name", text="Borrower Name")
    treeview.heading("Book Title", text="Book Title")
    treeview.heading("Borrow Date", text="Borrow Date")
    treeview.heading("Return Date", text="Return Date")
    treeview.heading("Status", text="Status")

    treeview.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Scrollbar for the Treeview
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=treeview.yview)
    treeview.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Populate the treeview with transactions data
    fetch_transactions(treeview)

    # Create a bottom frame for the buttons
    button_frame = tk.Frame(frame)
    button_frame.pack(side=tk.BOTTOM, pady=10)

    # Button to open the Add Transaction page (Borrow Book)
    tk.Button(button_frame, text="Borrow Book", command=lambda: add_transaction_page(frame, lambda: manage_transactions_screen(frame, back_command))).pack(side=tk.LEFT, padx=10)

    # Button to open the Return Books page
    tk.Button(button_frame, text="Return Books", command=lambda: return_books_page(frame, lambda: manage_transactions_screen(frame, back_command))).pack(side=tk.LEFT, padx=10)

    # Back Button
    tk.Button(button_frame, text="Back", command=back_command).pack(side=tk.LEFT, padx=10)
