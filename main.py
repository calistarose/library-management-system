import tkinter as tk
from addbooks import add_book_screen
from bookmanagement import view_books_screen
from transactions import manage_transactions_screen
from addmember import add_borrower_screen

def raise_frame(frame):
    frame.tkraise()

# Create the main window
root = tk.Tk()
root.title("Library Management System")
root.geometry("800x400")

# Create frames for the different screens
main_menu_frame = tk.Frame(root)
view_books_frame = tk.Frame(root)
add_book_frame = tk.Frame(root)
manage_transactions_frame = tk.Frame(root)
add_borrower_frame = tk.Frame(root)

for frame in (main_menu_frame, view_books_frame, add_book_frame, manage_transactions_frame, add_borrower_frame):
    frame.grid(row=0, column=0, sticky="nsew")

# --- Main Menu ---
tk.Label(main_menu_frame, text="Library Management System", font=('Arial', 20)).pack(pady=20)
tk.Button(main_menu_frame, text="View Books", command=lambda: raise_frame(view_books_frame)).pack(pady=10)
tk.Button(main_menu_frame, text="Add Book", command=lambda: raise_frame(add_book_frame)).pack(pady=10)
tk.Button(main_menu_frame, text="Add Member", command=lambda: raise_frame(add_borrower_frame)).pack(pady=10)
tk.Button(main_menu_frame, text="Transactions", command=lambda: raise_frame(manage_transactions_frame)).pack(pady=10)

# Call the functions from the respective files
view_books_screen(view_books_frame, lambda: raise_frame(main_menu_frame))
add_book_screen(add_book_frame, lambda: raise_frame(main_menu_frame))
add_borrower_screen(add_borrower_frame, lambda: raise_frame(main_menu_frame))
manage_transactions_screen(manage_transactions_frame, lambda: raise_frame(main_menu_frame))

# Start with the main menu
raise_frame(main_menu_frame)

# Run the GUI main loop
root.mainloop()
