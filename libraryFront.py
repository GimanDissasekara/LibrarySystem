import csv
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, font
from fuzzywuzzy import process

class LibraryManagementSystem:
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.geometry("800x600")
        
        # CSV paths
        self.csv_paths = {
            'students': 'studentdetails.csv',
            'books': 'bookdata.csv'
        }
        
        # Load data
        self.students = self.load_csv_data('students')
        self.books = self.load_csv_data('books')
        
        # Database connections
        self.setup_database_connections()
        
        # Enhanced UI Configuration
        self.root.configure(bg='#f0f4f8')  # Soft blue-gray background
        self.style = ttk.Style()
        self.configure_styles()
        
        # Custom fonts
        self.title_font = font.Font(family='Segoe UI', size=16, weight='bold')
        self.label_font = font.Font(family='Segoe UI', size=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create tabs
        self.create_book_search_tab()
        self.create_purchase_tab()
        self.create_book_return_tab()
        
        # Update notebook style
        self.notebook.configure(style='Custom.TNotebook')
    
    def setup_database_connections(self):
        """Set up SQLite database connections for purchases and returns."""
        # Purchase database
        self.purchase_conn = sqlite3.connect('book_purchases.db')
        self.purchase_cursor = self.purchase_conn.cursor()
        self.create_purchases_table()
        
        # Returns database
        self.return_conn = sqlite3.connect('book_returns.db')
        self.return_cursor = self.return_conn.cursor()
        self.create_returns_table()
    
    def configure_styles(self):
        """Configure modern ttk styles."""
        self.style.theme_use('clam')  # Use clam theme for more modern look
        
        # Notebook (Tab) Styles
        self.style.configure('Custom.TNotebook', background='#f0f4f8')
        self.style.configure('Custom.TNotebook.Tab', 
                             font=('Segoe UI', 10, 'bold'), 
                             padding=[10, 5], 
                             background='#e1e7f0', 
                             foreground='#2c3e50')
        self.style.map('Custom.TNotebook.Tab', 
                       background=[('selected', '#4a90e2')],
                       foreground=[('selected', 'white')])
        
        # Button Styles
        self.style.configure('TButton', 
                             font=('Segoe UI', 10, 'bold'), 
                             padding=10, 
                             background='#4a90e2', 
                             foreground='white')
        self.style.map('TButton', 
                       background=[('active', '#357abd')],
                       foreground=[('active', 'white')])
        
        # Entry Styles
        self.style.configure('TEntry', 
                             font=('Segoe UI', 10), 
                             padding=5, 
                             background='white')
        
        # Label Styles
        self.style.configure('TLabel', 
                             font=('Segoe UI', 10), 
                             background='#f0f4f8', 
                             foreground='#2c3e50')
    
    def create_purchases_table(self):
        """Create purchases table in SQLite database."""
        self.purchase_cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_purchases (
            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_id TEXT,
            book_barcode TEXT,
            purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.purchase_conn.commit()
    
    def create_returns_table(self):
        """Create returns table in SQLite database."""
        self.return_cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_returns (
            return_id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_id TEXT,
            book_barcode TEXT,
            return_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.return_conn.commit()
    
    def load_csv_data(self, data_type):
        """
        Load data from CSV files.
        For students: Expect columns [school_id, name, class]
        For books: Expect columns [barcode, title, topic, is_purchased]
        """
        data = []
        try:
            with open(self.csv_paths[data_type], 'r', encoding='utf-8') as csvfile:
                # Use DictReader to handle potential column order variations
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Normalize the row to ensure consistency
                    if data_type == 'students':
                        data.append({
                            'school_id': row.get('school_id', row.get('School ID', '')),
                            'name': row.get('name', row.get('Name', '')),
                            'class': row.get('class', row.get('Class', ''))
                        })
                    elif data_type == 'books':
                        data.append({
                            'barcode': row.get('barcode', row.get('Barcode', '')),
                            'title': row.get('title', row.get('Title', '')),
                            'topic': row.get('topic', row.get('Topic', '')),
                            'is_purchased': int(row.get('is_purchased', row.get('Is Purchased', 0)))
                        })
        except FileNotFoundError:
            messagebox.showerror("Error", f"{data_type.capitalize()} CSV file not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading {data_type} data: {str(e)}")
        
        return data
    
    def create_book_search_tab(self):
        """Create the book search tab with fuzzy matching."""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Book Search")
        
        # Book Name input
        ttk.Label(search_frame, text="Enter Book Name:", style='TLabel').pack(pady=10)
        self.search_entry = ttk.Entry(search_frame, width=40, style='TEntry')
        self.search_entry.pack(pady=5)
        
        # Search Button
        search_button = ttk.Button(search_frame, text="Search Book", command=self.search_book, style='TButton')
        search_button.pack(pady=10)
        
        # Search Results Display
        self.search_results = tk.Text(search_frame, height=15, width=60)
        self.search_results.pack(pady=10)
    
    def create_purchase_tab(self):
        """Create the book purchase tab with improved design."""
        purchase_frame = ttk.Frame(self.notebook)
        self.notebook.add(purchase_frame, text="Book Purchase")
        
        # Get unique classes for dropdown
        unique_classes = sorted(set(student['class'] for student in self.students))
        
        # Class input
        ttk.Label(purchase_frame, text="Select Your Class:", style='TLabel').pack(pady=10)
        self.class_var = tk.StringVar()
        self.class_dropdown = ttk.Combobox(purchase_frame, textvariable=self.class_var, values=unique_classes, state="readonly")
        self.class_dropdown.pack(pady=5)
        
        # School ID input
        ttk.Label(purchase_frame, text="Enter Your School ID:", style='TLabel').pack(pady=10)
        self.school_id_entry = ttk.Entry(purchase_frame, width=30, style='TEntry')
        self.school_id_entry.pack(pady=5)
        
        # Book Barcode input
        ttk.Label(purchase_frame, text="Enter Book Barcode:", style='TLabel').pack(pady=10)
        self.barcode_entry = ttk.Entry(purchase_frame, width=30, style='TEntry')
        self.barcode_entry.pack(pady=5)
        
        # Purchase Button
        purchase_button = ttk.Button(purchase_frame, text="Purchase Book", command=self.purchase_book, style='TButton')
        purchase_button.pack(pady=15)
    
    def create_book_return_tab(self):
        """Create the book return tab."""
        return_frame = ttk.Frame(self.notebook)
        self.notebook.add(return_frame, text="Book Return")
        
        # Get unique classes for dropdown
        unique_classes = sorted(set(student['class'] for student in self.students))
        
        # Class dropdown
        ttk.Label(return_frame, text="Select Your Class:", style='TLabel').pack(pady=10)
        self.return_class_var = tk.StringVar()
        self.return_class_dropdown = ttk.Combobox(return_frame, textvariable=self.return_class_var, values=unique_classes, state="readonly")
        self.return_class_dropdown.pack(pady=5)
        
        # School ID input
        ttk.Label(return_frame, text="Enter Your School ID:", style='TLabel').pack(pady=10)
        self.return_school_id_entry = ttk.Entry(return_frame, width=30, style='TEntry')
        self.return_school_id_entry.pack(pady=5)
        
        # Book Barcode input
        ttk.Label(return_frame, text="Enter Book Barcode:", style='TLabel').pack(pady=10)
        self.return_barcode_entry = ttk.Entry(return_frame, width=30, style='TEntry')
        self.return_barcode_entry.pack(pady=5)
        
        # Return Button
        return_button = ttk.Button(return_frame, text="Return Book", command=self.return_book, style='TButton')
        return_button.pack(pady=15)
    
    def search_book(self):
        """
        Search for books with fuzzy matching.
        Handles spelling mistakes and partial matches.
        """
        # Clear previous results
        self.search_results.delete(1.0, tk.END)
        
        # Get search query
        search_query = self.search_entry.get().strip()
        
        if not search_query:
            messagebox.showwarning("Warning", "Please enter a book name")
            return
        
        # Perform fuzzy matching on book titles
        book_titles = [book['title'] for book in self.books]
        matches = process.extract(search_query, book_titles, limit=5)
        
        # Display results with availability
        for match, score in matches:
            # Find books matching this title
            matching_books = [
                book for book in self.books 
                if book['title'] == match
            ]
            
            # Prepare result text
            result_text = f"Title: {match} (Match Score: {score}%)\n"
            available_books = [b for b in matching_books if b['is_purchased'] == 0]
            purchased_books = [b for b in matching_books if b['is_purchased'] == 1]
            
            result_text += f"Total Copies: {len(matching_books)}\n"
            result_text += f"Available Copies: {len(available_books)}\n"
            result_text += f"Purchased Copies: {len(purchased_books)}\n"
            
            # Add barcodes of available books
            if available_books:
                result_text += "Available Barcodes: " + ", ".join(b['barcode'] for b in available_books) + "\n"
            
            result_text += "\n" + "-"*50 + "\n\n"
            
            # Insert result
            self.search_results.insert(tk.END, result_text)
    
    def purchase_book(self):
        """Process book purchase."""
        # Validate inputs
        student_class = self.class_var.get().strip()
        school_id = self.school_id_entry.get().strip()
        book_barcode = self.barcode_entry.get().strip()
        
        # Validate student
        student = next((
            s for s in self.students 
            if s['school_id'] == school_id and s['class'] == student_class
        ), None)
        
        if not student:
            messagebox.showerror("Error", "Invalid Student Details")
            return
        
        # Check if book exists and is available
        book = next((
            b for b in self.books 
            if b['barcode'] == book_barcode and b['is_purchased'] == 0
        ), None)
        
        if not book:
            messagebox.showerror("Error", "Book Not Available")
            return
        
        # Update book status in memory
        book['is_purchased'] = 1
        
        # Record the purchase in database
        self.purchase_cursor.execute('''
            INSERT INTO book_purchases (school_id, book_barcode) 
            VALUES (?, ?)
        ''', (school_id, book_barcode))
        self.purchase_conn.commit()
        
        # Update CSV 
        self.update_book_csv()
        
        # Show success message
        messagebox.showinfo("Success", f"Book {book_barcode} purchased successfully!")
        
        # Clear entries
        self.class_var.set('')
        self.school_id_entry.delete(0, tk.END)
        self.barcode_entry.delete(0, tk.END)
    
    def return_book(self):
        """Process book return."""
        # Validate inputs
        student_class = self.return_class_var.get().strip()
        school_id = self.return_school_id_entry.get().strip()
        book_barcode = self.return_barcode_entry.get().strip()
        
        # Validate student
        student = next((
            s for s in self.students 
            if s['school_id'] == school_id and s['class'] == student_class
        ), None)
        
        if not student:
            messagebox.showerror("Error", "Invalid Student Details")
            return
        
        # Check if book was previously purchased
        self.purchase_cursor.execute('''
            SELECT * FROM book_purchases 
            WHERE school_id = ? AND book_barcode = ?
        ''', (school_id, book_barcode))
        purchase_record = self.purchase_cursor.fetchone()
        
        if not purchase_record:
            messagebox.showerror("Error", "No purchase record found for this book and student")
            return
        
        # Find the book in memory
        book = next((
            b for b in self.books 
            if b['barcode'] == book_barcode and b['is_purchased'] == 1
        ), None)
        
        if not book:
            messagebox.showerror("Error", "Book not found or already returned")
            return
        
        # Update book status in memory
        book['is_purchased'] = 0
        
        # Record the return in database
        self.return_cursor.execute('''
            INSERT INTO book_returns (school_id, book_barcode) 
            VALUES (?, ?)
        ''', (school_id, book_barcode))
        self.return_conn.commit()
        
        # Update CSV 
        self.update_book_csv()
        
        # Show success message
        messagebox.showinfo("Success", f"Book {book_barcode} returned successfully!")
        
        # Clear entries
        self.return_class_var.set('')
        self.return_school_id_entry.delete(0, tk.END)
        self.return_barcode_entry.delete(0, tk.END)
    
    def update_book_csv(self):
        """
        Update the book CSV with the latest purchase information.
        In a real-world scenario, you might want a more robust file writing method.
        """
        try:
            with open(self.csv_paths['books'], 'w', newline='', encoding='utf-8') as csvfile:
                # Determine fieldnames dynamically
                fieldnames = ['barcode', 'title', 'topic', 'is_purchased']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write all books
                for book in self.books:
                    writer.writerow(book)
        except Exception as e:
            messagebox.showerror("Error", f"Could not update book CSV: {str(e)}")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
    
    def __del__(self):
        """Close database connections."""
        if hasattr(self, 'purchase_conn'):
            self.purchase_conn.close()
        if hasattr(self, 'return_conn'):
            self.return_conn.close()

def main():
    # Check if required CSV files exist
    required_files = ['studentdetails.csv', 'bookdata.csv']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"Error: Missing CSV files: {', '.join(missing_files)}")
        print("Please ensure you have the following files in the same directory:")
        for f in missing_files:
            print(f"- {f}")
    else:
        # Install required library if not already installed
        try:
            import fuzzywuzzy
        except ImportError:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'fuzzywuzzy'])
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-Levenshtein'])
        
        # Run the application
        app = LibraryManagementSystem()
        app.run()

if __name__ == "__main__":
    main()