import tkinter as tk
from tkinter import ttk, messagebox
from dbconnection import create_connection, close_connection
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def fetch_books(treeview, frame):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Query to select all books
        query = """
        SELECT 
            b.id, b.title, b.author, b.genre, b.published_date, b.isbn, b.availability, 
            b.description, COALESCE(GROUP_CONCAT(r.review_text SEPARATOR '; '), 'No reviews') AS reviews
        FROM 
            books b
        LEFT JOIN 
            reviews r ON b.id = r.book_id
        GROUP BY b.id
        """
        
        cursor.execute(query)
        books = cursor.fetchall()
        
        # Clear current Treeview items
        treeview.delete(*treeview.get_children())
        
        for book in books:
            book_data = list(book)
            availability = "Available" if book_data[6] == 1 else "Not Available"
            book_data[6] = availability
            book_data[7] = "More Info"  # Set the "More Info" text for the link
            treeview.insert("", tk.END, values=book_data)
        
        close_connection(connection)

def on_treeview_double_click(event, treeview, frame):
    selected_item = treeview.selection()
    if selected_item:
        book_data = treeview.item(selected_item, "values")
        open_more_info_page(frame, book_data)  # Navigate to the detailed view

def open_more_info_page(parent_frame, book_data):
    # Clear the previous content
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Display the detailed information for the book
    book_id = book_data[0]  # ID is at index 0
    book_title = book_data[1]  # Title is at index 1
    book_author = book_data[2]  # Author is at index 2
    book_genre = book_data[3]  # Genre is at index 3
    book_pub_date = book_data[4]  # Published Date is at index 4
    book_isbn = book_data[5]  # ISBN is at index 5
    book_availability = book_data[6]  # Availability is at index 6
    book_reviews = book_data[8] if len(book_data) > 8 else "No reviews available"

    # Header with Book Title
    tk.Label(parent_frame, text=f"Book Details for: {book_title}", font=('Arial', 20)).pack(pady=20)

    # Detailed Information
    info_frame = tk.Frame(parent_frame)
    info_frame.pack(padx=20, pady=10)

    tk.Label(info_frame, text=f"Author: {book_author}", font=('Arial', 12)).pack(anchor="w")
    tk.Label(info_frame, text=f"Genre: {book_genre}", font=('Arial', 12)).pack(anchor="w")
    tk.Label(info_frame, text=f"Published Date: {book_pub_date}", font=('Arial', 12)).pack(anchor="w")
    tk.Label(info_frame, text=f"ISBN: {book_isbn}", font=('Arial', 12)).pack(anchor="w")
    tk.Label(info_frame, text=f"Availability: {book_availability}", font=('Arial', 12)).pack(anchor="w")

    # Reviews
    reviews_frame = tk.Frame(parent_frame)
    reviews_frame.pack(pady=10)

    if book_reviews != "No reviews available":
        tk.Label(reviews_frame, text="Reviews:", font=('Arial', 14, 'bold')).pack(anchor="w")
        
        reviews_list = book_reviews.split('; ')
        for idx, review in enumerate(reviews_list, 1):
            review_name, review_text = review.split(': ', 1) if ': ' in review else (f"Review {idx}", review)
            tk.Label(reviews_frame, text=f"Review {idx}: {review_name}\n{review_text}", font=('Arial', 12), wraplength=800, justify="left").pack(anchor="w", pady=5)
    else:
        tk.Label(reviews_frame, text="No reviews available", font=('Arial', 12)).pack(anchor="w")

    # Add Review Button
    tk.Button(parent_frame, text="Add Review", command=lambda: open_add_review_page(parent_frame, book_id)).pack(pady=10)

    # Button for sentiment analysis
    tk.Button(parent_frame, text="Analyze Sentiments", command=lambda: analyze_sentiment(book_id)).pack(pady=10)

    # Back Button to navigate to the previous screen
    tk.Button(parent_frame, text="Back", command=lambda: go_back(parent_frame)).pack(pady=20)

def open_add_review_page(parent_frame, book_id):
    # Clear the previous content
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Review submission screen
    tk.Label(parent_frame, text="Add a Review", font=('Arial', 20)).pack(pady=20)

    tk.Label(parent_frame, text=f"Book ID: {book_id}", font=('Arial', 12)).pack(pady=5)

    tk.Label(parent_frame, text="Review:", font=('Arial', 12)).pack(pady=5)
    entry_review = tk.Entry(parent_frame, width=50)
    entry_review.pack(pady=5)

    tk.Label(parent_frame, text="Select Borrower:", font=('Arial', 12)).pack(pady=5)

    # Fetch borrowers for the dropdown
    borrowers = get_borrowers()
    
    if borrowers:
        # Prepare borrower dropdown
        borrower_ids = {name: id for id, name in borrowers}
        borrower_names = list(borrower_ids.keys())
        
        selected_borrower = tk.StringVar(parent_frame)
        selected_borrower.set(borrower_names[0])  # Default value

        borrower_dropdown = tk.OptionMenu(parent_frame, selected_borrower, *borrower_names)
        borrower_dropdown.pack(pady=5)
    else:
        messagebox.showwarning("Warning", "No borrowers found in the database.")
        return

    # Submit Review Button
    tk.Button(parent_frame, text="Submit Review", command=lambda: submit_review(
        parent_frame, book_id, entry_review.get(), borrower_ids[selected_borrower.get()])
    ).pack(pady=10)

    # Back Button to navigate to the detailed book view
    tk.Button(parent_frame, text="Back", command=lambda: open_more_info_page(parent_frame, fetch_book_data(book_id))).pack(pady=10)

def submit_review(parent_frame, book_id, review, borrower_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # Insert the review into the database
        add_review_query = "INSERT INTO reviews (book_id, review_text, borrower_id) VALUES (%s, %s, %s)"
        cursor.execute(add_review_query, (book_id, review, borrower_id))
        connection.commit()

        # Perform sentiment analysis
        sentiment_score = analyze_single_review(review)
        sentiment = categorize_sentiment(sentiment_score)

        messagebox.showinfo("Review Submitted", f"Review added with {sentiment} sentiment.")

        close_connection(connection)
        
        # After submission, navigate back to the detailed book view
        open_more_info_page(parent_frame, fetch_book_data(book_id))

def analyze_single_review(review):
    sia = SentimentIntensityAnalyzer()
    ps = PorterStemmer()

    tokens = word_tokenize(review)
    stemmed_tokens = [ps.stem(token) for token in tokens]
    sentiment_score = sia.polarity_scores(" ".join(stemmed_tokens))
    
    return sentiment_score

def categorize_sentiment(sentiment_score):
    if sentiment_score['compound'] >= 0.05:
        return "Positive"
    elif sentiment_score['compound'] <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def analyze_sentiment(book_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # Fetch reviews for the specific book ID
        cursor.execute("SELECT review_text FROM reviews WHERE book_id = %s", (book_id,))
        reviews = cursor.fetchall()

        if not reviews:
            messagebox.showinfo("Sentiment Analysis", "No reviews available for sentiment analysis.")
            return

        # Initialize NLTK components
        sia = SentimentIntensityAnalyzer()
        ps = PorterStemmer()

        # Variable to store the result with categorized sentiment
        sentiment_results = []

        for (review,) in reviews:
            tokens = word_tokenize(review)
            stemmed_tokens = [ps.stem(token) for token in tokens]
            sentiment_score = sia.polarity_scores(" ".join(stemmed_tokens))

            # Categorize sentiment
            if sentiment_score['compound'] >= 0.05:
                sentiment = "Positive"
            elif sentiment_score['compound'] <= -0.05:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            # Append the review and its sentiment to the result list
            sentiment_results.append(f"Review: {review}\nSentiment: {sentiment}\n")

        close_connection(connection)

        # Display the result in a message box
        result_text = "\n".join(sentiment_results)
        messagebox.showinfo("Sentiment Analysis Results", result_text)


def fetch_book_data(book_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # Query to fetch the updated book details along with reviews
        query = """
        SELECT 
            b.id, b.title, b.author, b.genre, b.published_date, b.isbn, b.availability, 
            b.description, COALESCE(GROUP_CONCAT(r.review_text SEPARATOR '; '), 'No reviews') AS reviews
        FROM 
            books b
        LEFT JOIN 
            reviews r ON b.id = r.book_id
        WHERE 
            b.id = %s
        GROUP BY b.id, b.description
        """
        
        cursor.execute(query, (book_id,))
        book_data = cursor.fetchone()
        close_connection(connection)
        return book_data

def get_borrowers():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, CONCAT(first_name, ' ', last_name) AS name FROM borrowers")
        borrowers = cursor.fetchall()  # Fetch all borrowers (id, name)
        close_connection(connection)
        return borrowers
    else:
        return []

def go_back(parent_frame):
    # Clear the More Info page
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Reload the book management screen
    view_books_screen(parent_frame, lambda: go_back(parent_frame))

def search_books(treeview, frame, search_query):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # NLTK preprocessing: tokenization and lemmatization
        tokens = word_tokenize(search_query.lower())
        lemmatizer = WordNetLemmatizer()
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
        processed_query = " ".join(lemmatized_tokens)

        # Query to search books using the processed search query
        query = """
        SELECT 
            b.id, b.title, b.author, b.genre, b.published_date, b.isbn, b.availability, 
            b.description, COALESCE(GROUP_CONCAT(r.review_text SEPARATOR '; '), 'No reviews') AS reviews
        FROM 
            books b
        LEFT JOIN 
            reviews r ON b.id = r.book_id
        WHERE 
            b.title LIKE %s OR b.author LIKE %s OR b.genre LIKE %s
        GROUP BY b.id
        """
        
        search_pattern = f"%{processed_query}%"
        cursor.execute(query, (search_pattern, search_pattern, search_pattern))
        books = cursor.fetchall()

        # Clear current Treeview items
        treeview.delete(*treeview.get_children())

        for book in books:
            book_data = list(book)
            availability = "Available" if book_data[6] == 1 else "Not Available"
            book_data[6] = availability
            book_data[7] = "More Info"  # Set the "More Info" text for the link
            treeview.insert("", tk.END, values=book_data)

        close_connection(connection)

def view_books_screen(frame, back_command):
    # Clear the frame
    for widget in frame.winfo_children():
        widget.destroy()

    tk.Label(frame, text="Books in Library", font=('Arial', 20)).pack(pady=10)

    search_frame = tk.Frame(frame)
    search_frame.pack(pady=10)

    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side=tk.LEFT, padx=10)

    search_button = tk.Button(search_frame, text="Search", command=lambda: search_books(treeview, frame, search_entry.get()))
    search_button.pack(side=tk.LEFT)

    table_frame = tk.Frame(frame)
    table_frame.pack(fill=tk.BOTH, expand=True)

    columns = ("id", "Title", "Author", "Genre", "Published Date", "ISBN", "Availability", "More Info")
    treeview = ttk.Treeview(table_frame, columns=columns, show="headings")
    treeview.heading("id", text="ID")
    treeview.heading("Title", text="Title")
    treeview.heading("Author", text="Author")
    treeview.heading("Genre", text="Genre")
    treeview.heading("Published Date", text="Published Date")
    treeview.heading("ISBN", text="ISBN")
    treeview.heading("Availability", text="Availability")
    treeview.heading("More Info", text="More Info")

    treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=treeview.yview)
    treeview.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    fetch_books(treeview, frame)

    # Bind double-click event for "More Info"
    treeview.bind("<Double-1>", lambda event: on_treeview_double_click(event, treeview, frame))

     # Add the back button at the bottom of the screen
    tk.Button(frame, text="Back", command=back_command).pack(pady=10, side="bottom")
