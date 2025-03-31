import csv
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog
from fuzzywuzzy import process
from PIL import Image, ImageTk
import webbrowser

class LibraryManagementSystem:
    def __init__(self):
        # Initialize main window with modern styling
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Set application icon
        try:
            self.root.iconbitmap('library_icon.ico')  # Provide your own icon file
        except:
            pass  # Continue without icon if not available
        
        # Color scheme
        self.colors = {
            'primary': '#4a6fa5',
            'secondary': '#6b8cae',
            'accent': '#ff7e5f',
            'background': '#f5f7fa',
            'text': '#2c3e50',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336'
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['background'])
        
        # Load data
        self.csv_paths = {
            'students': 'studentdetails.csv',
            'books': 'bookdata.csv'
        }
        self.students = self.load_csv_data('students')
        self.books = self.load_csv_data('books')
        
        # Setup database
        self.setup_database_connections()
        
        # Custom fonts
        self.title_font = font.Font(family='Helvetica', size=18, weight='bold')
        self.subtitle_font = font.Font(family='Helvetica', size=12)
        self.label_font = font.Font(family='Helvetica', size=10)
        self.button_font = font.Font(family='Helvetica', size=10, weight='bold')
        
        # Configure styles
        self.style = ttk.Style()
        self.configure_styles()
        
        # Create header frame
        self.create_header()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(expand=True, fill='both', padx=20, pady=(0, 20))
        
        # Create tabs
        self.create_book_search_tab()
        self.create_purchase_tab()
        self.create_book_return_tab()
        self.create_help_tab()
        
        # Status bar
        self.create_status_bar()
        
        # Center the window
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_header(self):
        """Create the application header with logo and title"""
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        
        # Try to load logo image
        try:
            logo_img = Image.open('library_logo.png')  # Provide your own logo
            logo_img = logo_img.resize((60, 60), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header_frame, image=self.logo, bg=self.colors['primary'])
            logo_label.pack(side='left', padx=20, pady=10)
        except:
            pass  # Continue without logo if image not available
        
        # Application title
        title_label = tk.Label(
            header_frame, 
            text="Library Management System", 
            font=self.title_font,
            fg='white',
            bg=self.colors['primary']
        )
        title_label.pack(side='left', pady=20)
        
        # Version label
        version_label = tk.Label(
            header_frame, 
            text="v1.0", 
            font=self.subtitle_font,
            fg='white',
            bg=self.colors['primary']
        )
        version_label.pack(side='right', padx=20, pady=20)
    
    def configure_styles(self):
        """Configure modern ttk styles."""
        self.style.theme_use('clam')
        
        # Notebook (Tab) Styles
        self.style.configure('Custom.TNotebook', background=self.colors['background'])
        self.style.configure('Custom.TNotebook.Tab', 
                            font=self.button_font, 
                            padding=[15, 5], 
                            background=self.colors['secondary'], 
                            foreground='white')
        self.style.map('Custom.TNotebook.Tab', 
                      background=[('selected', self.colors['primary'])],
                      foreground=[('selected', 'white')])
        
        # Button Styles
        self.style.configure('TButton', 
                            font=self.button_font, 
                            padding=10, 
                            background=self.colors['primary'], 
                            foreground='white',
                            borderwidth=0)
        self.style.map('TButton', 
                      background=[('active', self.colors['accent'])],
                      foreground=[('active', 'white')])
        
        # Entry Styles
        self.style.configure('TEntry', 
                            font=self.label_font, 
                            padding=8, 
                            fieldbackground='white',
                            bordercolor=self.colors['secondary'],
                            lightcolor=self.colors['secondary'],
                            darkcolor=self.colors['secondary'])
        
        # Combobox Styles
        self.style.configure('TCombobox', 
                            font=self.label_font, 
                            padding=8,
                            fieldbackground='white')
        
        # Label Styles
        self.style.configure('TLabel', 
                            font=self.label_font, 
                            background=self.colors['background'], 
                            foreground=self.colors['text'])
        
        # Text Widget Styles
        self.style.configure('Text', 
                           font=self.label_font,
                           background='white',
                           foreground=self.colors['text'],
                           padx=10,
                           pady=10)
    
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
        """Load data from CSV files with error handling."""
        data = []
        file_path = self.csv_paths[data_type]
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            return data
        
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if data_type == 'students':
                        data.append({
                            'school_id': row.get('school_id', row.get('School ID', '')).strip(),
                            'name': row.get('name', row.get('Name', '')).strip(),
                            'class': row.get('class', row.get('Class', '')).strip()
                        })
                    elif data_type == 'books':
                        data.append({
                            'barcode': row.get('barcode', row.get('Barcode', '')).strip(),
                            'title': row.get('title', row.get('Title', '')).strip(),
                            'topic': row.get('topic', row.get('Topic', '')).strip(),
                            'is_purchased': int(row.get('is_purchased', row.get('Is Purchased', 0)))
                        })
        except Exception as e:
            messagebox.showerror("Error", f"Error loading {data_type} data: {str(e)}")
        
        return data
    
    def create_book_search_tab(self):
        """Create the book search tab with fuzzy matching."""
        search_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(search_frame, text="🔍 Book Search")
        
        # Search container
        search_container = ttk.Frame(search_frame)
        search_container.pack(fill='x', pady=(0, 20))
        
        # Book Name input
        ttk.Label(search_container, text="Search Books:", style='TLabel').pack(side='left', padx=(0, 10))
        
        self.search_entry = ttk.Entry(
            search_container, 
            width=40, 
            style='TEntry',
            font=self.label_font
        )
        self.search_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.search_book())  # Search on Enter key
        
        # Search Button
        search_button = ttk.Button(
            search_container, 
            text="Search", 
            command=self.search_book, 
            style='TButton'
        )
        search_button.pack(side='left')
        
        # Search Results Display
        results_frame = ttk.Frame(search_frame)
        results_frame.pack(expand=True, fill='both')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.search_results = tk.Text(
            results_frame, 
            height=15, 
            width=80,
            wrap='word',
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10,
            font=self.label_font
        )
        self.search_results.pack(expand=True, fill='both')
        
        # Configure scrollbar
        scrollbar.config(command=self.search_results.yview)
        
        # Configure tags for colored text
        self.search_results.tag_config('title', foreground=self.colors['primary'], font=('Helvetica', 11, 'bold'))
        self.search_results.tag_config('available', foreground=self.colors['success'])
        self.search_results.tag_config('unavailable', foreground=self.colors['error'])
        self.search_results.tag_config('match_score', foreground=self.colors['warning'])
        
        # Set initial help text
        self.search_results.insert(tk.END, "Enter a book title to search...\n")
        self.search_results.config(state='disabled')
    
    def create_purchase_tab(self):
        """Create the book purchase tab with improved design."""
        purchase_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(purchase_frame, text="🛒 Book Purchase")
        
        # Form container
        form_frame = ttk.Frame(purchase_frame)
        form_frame.pack(fill='both', expand=True)
        
        # Section header
        ttk.Label(
            form_frame, 
            text="Book Purchase Form", 
            font=self.subtitle_font,
            style='TLabel'
        ).pack(pady=(0, 20))
        
        # Form fields
        fields = [
            ("Select Your Class:", 'class_var', 'combobox'),
            ("Enter Your School ID:", 'school_id_entry', 'entry'),
            ("Enter Book Barcode:", 'barcode_entry', 'entry')
        ]
        
        # Get unique classes for dropdown
        unique_classes = sorted(set(student['class'] for student in self.students))
        
        for label_text, attr_name, field_type in fields:
            # Create container for each field
            field_container = ttk.Frame(form_frame)
            field_container.pack(fill='x', pady=10)
            
            # Add label
            ttk.Label(
                field_container, 
                text=label_text, 
                style='TLabel',
                width=20,
                anchor='e'
            ).pack(side='left', padx=(0, 10))
            
            # Add field
            if field_type == 'entry':
                entry = ttk.Entry(
                    field_container,
                    style='TEntry',
                    font=self.label_font
                )
                entry.pack(side='left', expand=True, fill='x')
                setattr(self, attr_name, entry)
            elif field_type == 'combobox':
                var = tk.StringVar()
                combobox = ttk.Combobox(
                    field_container,
                    textvariable=var,
                    values=unique_classes,
                    state="readonly",
                    font=self.label_font,
                    style='TCombobox'
                )
                combobox.pack(side='left', expand=True, fill='x')
                setattr(self, attr_name, var)
        
        # Button container
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill='x', pady=20)
        
        # Purchase Button
        purchase_button = ttk.Button(
            button_frame, 
            text="Purchase Book", 
            command=self.purchase_book, 
            style='TButton'
        )
        purchase_button.pack(pady=10, ipadx=20)
        
        # Add some visual separation
        ttk.Separator(purchase_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Quick help section
        help_text = """Instructions:
1. Select your class from the dropdown
2. Enter your school ID
3. Enter the book barcode
4. Click 'Purchase Book' to complete the transaction"""
        
        ttk.Label(
            purchase_frame, 
            text=help_text, 
            style='TLabel',
            font=('Helvetica', 9),
            justify='left'
        ).pack(fill='x', pady=10)
    
    def create_book_return_tab(self):
        """Create the book return tab."""
        return_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(return_frame, text="↩️ Book Return")
        
        # Form container
        form_frame = ttk.Frame(return_frame)
        form_frame.pack(fill='both', expand=True)
        
        # Section header
        ttk.Label(
            form_frame, 
            text="Book Return Form", 
            font=self.subtitle_font,
            style='TLabel'
        ).pack(pady=(0, 20))
        
        # Form fields
        fields = [
            ("Select Your Class:", 'return_class_var', 'combobox'),
            ("Enter Your School ID:", 'return_school_id_entry', 'entry'),
            ("Enter Book Barcode:", 'return_barcode_entry', 'entry')
        ]
        
        # Get unique classes for dropdown
        unique_classes = sorted(set(student['class'] for student in self.students))
        
        for label_text, attr_name, field_type in fields:
            # Create container for each field
            field_container = ttk.Frame(form_frame)
            field_container.pack(fill='x', pady=10)
            
            # Add label
            ttk.Label(
                field_container, 
                text=label_text, 
                style='TLabel',
                width=20,
                anchor='e'
            ).pack(side='left', padx=(0, 10))
            
            # Add field
            if field_type == 'entry':
                entry = ttk.Entry(
                    field_container,
                    style='TEntry',
                    font=self.label_font
                )
                entry.pack(side='left', expand=True, fill='x')
                setattr(self, attr_name, entry)
            elif field_type == 'combobox':
                var = tk.StringVar()
                combobox = ttk.Combobox(
                    field_container,
                    textvariable=var,
                    values=unique_classes,
                    state="readonly",
                    font=self.label_font,
                    style='TCombobox'
                )
                combobox.pack(side='left', expand=True, fill='x')
                setattr(self, attr_name, var)
        
        # Button container
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill='x', pady=20)
        
        # Return Button
        return_button = ttk.Button(
            button_frame, 
            text="Return Book", 
            command=self.return_book, 
            style='TButton'
        )
        return_button.pack(pady=10, ipadx=20)
        
        # Add some visual separation
        ttk.Separator(return_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Quick help section
        help_text = """Instructions:
1. Select your class from the dropdown
2. Enter your school ID
3. Enter the book barcode
4. Click 'Return Book' to complete the transaction"""
        
        ttk.Label(
            return_frame, 
            text=help_text, 
            style='TLabel',
            font=('Helvetica', 9),
            justify='left'
        ).pack(fill='x', pady=10)
    
    def create_help_tab(self):
        """Create a help/instructions tab."""
        help_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(help_frame, text="❓ Help")
        
        # Main container
        container = ttk.Frame(help_frame)
        container.pack(expand=True, fill='both')
        
        # Title
        ttk.Label(
            container,
            text="Library Management System Help",
            font=self.title_font,
            style='TLabel'
        ).pack(pady=10)
        
        # Help text
        help_text = """Welcome to the Library Management System!

This application helps manage book purchases and returns in your library.

Features:
- 🔍 Book Search: Find books by title with fuzzy matching
- 🛒 Book Purchase: Check out books to students
- ↩️ Book Return: Process book returns

Requirements:
- studentdetails.csv - Contains student information
- bookdata.csv - Contains book inventory

For support, please contact your system administrator.
"""
        
        ttk.Label(
            container,
            text=help_text,
            style='TLabel',
            font=self.label_font,
            justify='left'
        ).pack(fill='x', pady=10)
        
        # Documentation link
        doc_link = ttk.Label(
            container,
            text="Click here for documentation",
            style='TLabel',
            font=('Helvetica', 9, 'underline'),
            foreground='blue',
            cursor='hand2'
        )
        doc_link.pack(pady=10)
        doc_link.bind('<Button-1>', lambda e: webbrowser.open("https://example.com/docs"))
        
        # Version info
        version_info = ttk.Label(
            container,
            text="Version 1.0 | © 2025 Library System",
            style='TLabel',
            font=('Helvetica', 8)
        )
        version_info.pack(side='bottom', pady=10)
    
    def create_status_bar(self):
        """Create a status bar at the bottom of the window."""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w',
            font=('Helvetica', 9)
        )
        status_bar.pack(side='bottom', fill='x')
    
    def update_status(self, message):
        """Update the status bar message."""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def search_book(self):
        """Search for books with fuzzy matching."""
        # Clear previous results
        self.search_results.config(state='normal')
        self.search_results.delete(1.0, tk.END)
        
        # Get search query
        search_query = self.search_entry.get().strip()
        
        if not search_query:
            self.search_results.insert(tk.END, "Please enter a book name to search...\n")
            self.search_results.config(state='disabled')
            self.update_status("Please enter a book name")
            return
        
        self.update_status(f"Searching for: {search_query}...")
        
        # Perform fuzzy matching on book titles
        book_titles = [book['title'] for book in self.books]
        matches = process.extract(search_query, book_titles, limit=5)
        
        if not matches:
            self.search_results.insert(tk.END, "No books found matching your search.\n")
            self.search_results.config(state='disabled')
            self.update_status("No results found")
            return
        
        # Display results with availability
        for i, (match, score) in enumerate(matches):
            # Find books matching this title
            matching_books = [book for book in self.books if book['title'] == match]
            
            # Insert title with styling
            self.search_results.insert(tk.END, f"{i+1}. ", 'title')
            self.search_results.insert(tk.END, f"{match}\n", 'title')
            
            # Insert match score
            self.search_results.insert(tk.END, f"  Match confidence: {score}%\n", 'match_score')
            
            # Count available and purchased books
            available = sum(1 for b in matching_books if b['is_purchased'] == 0)
            purchased = len(matching_books) - available
            
            # Insert availability info
            self.search_results.insert(tk.END, f"  Total copies: {len(matching_books)}\n")
            self.search_results.insert(tk.END, f"  Available: ", 'available')
            self.search_results.insert(tk.END, f"{available}\n")
            self.search_results.insert(tk.END, f"  Checked out: ", 'unavailable')
            self.search_results.insert(tk.END, f"{purchased}\n")
            
            # Add barcodes of available books if any
            if available > 0:
                available_barcodes = [b['barcode'] for b in matching_books if b['is_purchased'] == 0]
                self.search_results.insert(tk.END, "  Available barcodes: ")
                self.search_results.insert(tk.END, ", ".join(available_barcodes) + "\n")
            
            # Add separator between results
            if i < len(matches) - 1:
                self.search_results.insert(tk.END, "\n")
        
        self.search_results.config(state='disabled')
        self.update_status(f"Found {len(matches)} matching books")
    
    def purchase_book(self):
        """Process book purchase with validation."""
        # Get input values
        student_class = self.class_var.get().strip()
        school_id = self.school_id_entry.get().strip()
        book_barcode = self.barcode_entry.get().strip()
        
        # Validate inputs
        if not all([student_class, school_id, book_barcode]):
            messagebox.showwarning("Missing Information", "Please fill in all fields")
            self.update_status("Purchase failed - missing information")
            return
        
        # Validate student
        student = next((
            s for s in self.students 
            if s['school_id'] == school_id and s['class'] == student_class
        ), None)
        
        if not student:
            messagebox.showerror("Error", "Invalid student details. Please check your class and school ID.")
            self.update_status("Purchase failed - invalid student")
            return
        
        # Check if book exists and is available
        book = next((
            b for b in self.books 
            if b['barcode'] == book_barcode and b['is_purchased'] == 0
        ), None)
        
        if not book:
            messagebox.showerror("Error", "Book not available. It may be checked out or the barcode may be incorrect.")
            self.update_status("Purchase failed - book unavailable")
            return
        
        # Confirm purchase
        confirm = messagebox.askyesno(
            "Confirm Purchase",
            f"Confirm purchase for:\n\nStudent: {student['name']}\nClass: {student_class}\nBook: {book['title']}\nBarcode: {book_barcode}"
        )
        
        if not confirm:
            self.update_status("Purchase cancelled")
            return
        
        # Update book status in memory
        book['is_purchased'] = 1
        
        # Record the purchase in database
        try:
            self.purchase_cursor.execute('''
                INSERT INTO book_purchases (school_id, book_barcode) 
                VALUES (?, ?)
            ''', (school_id, book_barcode))
            self.purchase_conn.commit()
            
            # Update CSV 
            self.update_book_csv()
            
            # Show success message
            messagebox.showinfo(
                "Success", 
                f"Book checked out successfully!\n\nTitle: {book['title']}\nBarcode: {book_barcode}"
            )
            
            # Clear entries
            self.class_var.set('')
            self.school_id_entry.delete(0, tk.END)
            self.barcode_entry.delete(0, tk.END)
            
            self.update_status(f"Book {book_barcode} checked out to {student['name']}")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not record purchase: {str(e)}")
            self.update_status("Purchase failed - database error")
    
    def return_book(self):
        """Process book return with validation."""
        # Get input values
        student_class = self.return_class_var.get().strip()
        school_id = self.return_school_id_entry.get().strip()
        book_barcode = self.return_barcode_entry.get().strip()
        
        # Validate inputs
        if not all([student_class, school_id, book_barcode]):
            messagebox.showwarning("Missing Information", "Please fill in all fields")
            self.update_status("Return failed - missing information")
            return
        
        # Validate student
        student = next((
            s for s in self.students 
            if s['school_id'] == school_id and s['class'] == student_class
        ), None)
        
        if not student:
            messagebox.showerror("Error", "Invalid student details. Please check your class and school ID.")
            self.update_status("Return failed - invalid student")
            return
        
        # Check if book was previously purchased by this student
        self.purchase_cursor.execute('''
            SELECT * FROM book_purchases 
            WHERE school_id = ? AND book_barcode = ?
        ''', (school_id, book_barcode))
        purchase_record = self.purchase_cursor.fetchone()
        
        if not purchase_record:
            messagebox.showerror("Error", "No record found of this student checking out this book.")
            self.update_status("Return failed - no purchase record")
            return
        
        # Find the book in memory
        book = next((
            b for b in self.books 
            if b['barcode'] == book_barcode and b['is_purchased'] == 1
        ), None)
        
        if not book:
            messagebox.showerror("Error", "Book not found or already returned.")
            self.update_status("Return failed - book not found")
            return
        
        # Confirm return
        confirm = messagebox.askyesno(
            "Confirm Return",
            f"Confirm return for:\n\nStudent: {student['name']}\nClass: {student_class}\nBook: {book['title']}\nBarcode: {book_barcode}"
        )
        
        if not confirm:
            self.update_status("Return cancelled")
            return
        
        # Update book status in memory
        book['is_purchased'] = 0
        
        # Record the return in database
        try:
            self.return_cursor.execute('''
                INSERT INTO book_returns (school_id, book_barcode) 
                VALUES (?, ?)
            ''', (school_id, book_barcode))
            self.return_conn.commit()
            
            # Update CSV 
            self.update_book_csv()
            
            # Show success message
            messagebox.showinfo(
                "Success", 
                f"Book returned successfully!\n\nTitle: {book['title']}\nBarcode: {book_barcode}"
            )
            
            # Clear entries
            self.return_class_var.set('')
            self.return_school_id_entry.delete(0, tk.END)
            self.return_barcode_entry.delete(0, tk.END)
            
            self.update_status(f"Book {book_barcode} returned by {student['name']}")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not record return: {str(e)}")
            self.update_status("Return failed - database error")
    
    def update_book_csv(self):
        """Update the book CSV file with current data."""
        try:
            backup_path = self.csv_paths['books'] + '.bak'
            
            # Create backup first
            if os.path.exists(self.csv_paths['books']):
                os.replace(self.csv_paths['books'], backup_path)
            
            # Write new file
            with open(self.csv_paths['books'], 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['barcode', 'title', 'topic', 'is_purchased']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.books)
            
            self.update_status("Book inventory updated successfully")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not update book CSV: {str(e)}")
            self.update_status("Error updating book inventory")
            
            # Try to restore backup
            if os.path.exists(backup_path):
                try:
                    os.replace(backup_path, self.csv_paths['books'])
                except:
                    pass
            
            return False
    
    def run(self):
        """Run the application."""
        self.update_status("Ready")
        self.root.mainloop()
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'purchase_conn'):
            self.purchase_conn.close()
        if hasattr(self, 'return_conn'):
            self.return_conn.close()

def check_requirements():
    """Check for required packages and install if missing."""
    required = ['fuzzywuzzy', 'pillow']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        import subprocess
        import sys
        
        install_cmd = [sys.executable, '-m', 'pip', 'install'] + missing
        try:
            subprocess.check_call(install_cmd)
            # Also install python-Levenshtein for better performance
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-Levenshtein'])
        except subprocess.CalledProcessError:
            print(f"Failed to install required packages: {', '.join(missing)}")
            return False
    
    return True

def main():
    # Check for required packages
    if not check_requirements():
        return
    
    # Check for required CSV files
    required_files = ['studentdetails.csv', 'bookdata.csv']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        # Ask user to locate missing files
        for file in missing_files:
            messagebox.showwarning(
                "Missing File",
                f"The required file '{file}' was not found.\n\nPlease locate this file."
            )
            
            file_path = filedialog.askopenfilename(
                title=f"Locate {file}",
                filetypes=[("CSV files", "*.csv")]
            )
            
            if file_path:
                # Copy file to current directory
                import shutil
                try:
                    shutil.copy(file_path, file)
                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Could not copy file:\n\n{str(e)}"
                    )
                    return
            else:
                messagebox.showerror(
                    "Error",
                    f"Cannot run without {file}. Please ensure all required files are available."
                )
                return
    
    # Run the application
    app = LibraryManagementSystem()
    app.run()

if __name__ == "__main__":
    main()