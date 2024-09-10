import tkinter as tk
from tkinter import messagebox
from dbconnection import create_connection, close_connection

def add_member_to_db(last_name, first_name, middle_name, phone_number, membership_date):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Check if member already exists
        check_member_query = """
        SELECT * FROM borrowers 
        WHERE last_name = %s AND first_name = %s AND phone_number = %s
        """
        cursor.execute(check_member_query, (last_name, first_name, phone_number))
        existing_member = cursor.fetchone()

        if existing_member:
            messagebox.showwarning("Warning", "Member already exists in the database.")
            close_connection(connection)
            return

        # If the member does not exist, insert the new member
        add_member_query = """
        INSERT INTO borrowers (last_name, first_name, middle_name, phone_number, membership_date)
        VALUES (%s, %s, %s, %s, %s)
        """
        member_data = (last_name, first_name, middle_name, phone_number, membership_date)
        cursor.execute(add_member_query, member_data)
        connection.commit()
        close_connection(connection)
        messagebox.showinfo("Success", "Member added successfully!")
    else:
        messagebox.showerror("Error", "Database connection failed")

def add_borrower_screen(frame, back_command):
    for widget in frame.winfo_children():
        widget.destroy()  # Clear the frame

    tk.Label(frame, text="Add a New Member", font=('Arial', 20)).pack(pady=20)

    # Create Entry Widgets
    entry_last_name = tk.Entry(frame, width=30)
    entry_first_name = tk.Entry(frame, width=30)
    entry_middle_name = tk.Entry(frame, width=30)
    entry_phone_number = tk.Entry(frame, width=30)
    entry_membership_date = tk.Entry(frame, width=30)

    # Create and pack Labels and Entry Widgets
    tk.Label(frame, text="Last Name:").pack(pady=5)
    entry_last_name.pack(pady=5)

    tk.Label(frame, text="First Name:").pack(pady=5)
    entry_first_name.pack(pady=5)

    tk.Label(frame, text="Middle Name:").pack(pady=5)
    entry_middle_name.pack(pady=5)

    tk.Label(frame, text="Phone Number:").pack(pady=5)
    entry_phone_number.pack(pady=5)

    tk.Label(frame, text="Membership Date (YYYY-MM-DD):").pack(pady=5)
    entry_membership_date.pack(pady=5)

    # Add Member Button
    tk.Button(frame, text="Add Member", command=lambda: add_member(entry_last_name, entry_first_name, entry_middle_name, entry_phone_number, entry_membership_date)).pack(pady=20)

    # Back Button
    tk.Button(frame, text="Back", command=back_command).pack(pady=10)

def add_member(entry_last_name, entry_first_name, entry_middle_name, entry_phone_number, entry_membership_date):
    last_name = entry_last_name.get()
    first_name = entry_first_name.get()
    middle_name = entry_middle_name.get()
    phone_number = entry_phone_number.get()
    membership_date = entry_membership_date.get()

    if not all([last_name, first_name, middle_name, phone_number, membership_date]):
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    add_member_to_db(last_name, first_name, middle_name, phone_number, membership_date)
