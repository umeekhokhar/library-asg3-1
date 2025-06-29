import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import re

class BookNotAvailableError(Exception):
    pass

class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_lent = False

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"

class EBook(Book):
    def __init__(self, title, author, isbn, download_size):
        super().__init__(title, author, isbn)
        self.download_size = download_size  # in MB

    def __str__(self):
        return f"{self.title} by {self.author} (eBook, {self.download_size}MB)"

class Library:
    def __init__(self):
        self.books = []  

    def add_book(self, book):
        self.books.append(book)

    def remove_book(self, isbn):
        initial_len = len(self.books)
        self.books = [book for book in self.books if book.isbn != isbn]
        if len(self.books) == initial_len:
            raise BookNotAvailableError("Book with this ISBN not found.")


    def lend_book(self, isbn):
        """Lends a book by ISBN."""
        for book in self.books:
            if book.isbn == isbn and not book.is_lent:
                book.is_lent = True
                return book
        raise BookNotAvailableError("Book is either not available or already lent.")

    def return_book(self, isbn):
        """Returns a lent book by ISBN."""
        for book in self.books:
            if book.isbn == isbn and book.is_lent:
                book.is_lent = False
                return
        raise BookNotAvailableError("This book was not lent out.")

    def __iter__(self):
        """Custom iterator to yield only available (not lent) books."""
        return (book for book in self.books if not book.is_lent)

    def books_by_author(self, author):
        """Generator function to yield books by a specific author (case-insensitive)."""
        return (book for book in self.books if book.author.lower() == author.lower())

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("700x700")
        self.root.resizable(False, False)

        self.library = Library()

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self._create_widgets()
        self._setup_layout()
        self.update_book_list()

    def _create_widgets(self):
        # --- Frames for grouping ---
        self.input_frame = ttk.LabelFrame(self.root, text="Add New Book", padding=(15, 10))
        self.action_frame = ttk.LabelFrame(self.root, text="Library Actions", padding=(15, 10))
        self.list_frame = ttk.LabelFrame(self.root, text="Library Inventory", padding=(15, 10))

        # --- Input fields ---
        self.title_label = ttk.Label(self.input_frame, text="Title:")
        self.title_entry = ttk.Entry(self.input_frame, width=40)
        self.author_label = ttk.Label(self.input_frame, text="Author:")
        self.author_entry = ttk.Entry(self.input_frame, width=40)
        self.isbn_label = ttk.Label(self.input_frame, text="ISBN:")
        self.isbn_entry = ttk.Entry(self.input_frame, width=40)
        self.ebook_var = tk.BooleanVar()
        self.ebook_checkbox = ttk.Checkbutton(self.input_frame, text="eBook?", variable=self.ebook_var, command=self._toggle_ebook_fields)
        self.size_label = ttk.Label(self.input_frame, text="Download Size (MB):")
        self.size_entry = ttk.Entry(self.input_frame, state='disabled', width=40)
        self.add_button = ttk.Button(self.input_frame, text="Add Book", command=self._add_book)

        # --- Action buttons ---
        self.lend_button = ttk.Button(self.action_frame, text="Lend Book", command=self._lend_book)
        self.return_button = ttk.Button(self.action_frame, text="Return Book", command=self._return_book)
        self.remove_button = ttk.Button(self.action_frame, text="Remove Book", command=self._remove_book)
        self.view_by_author_button = ttk.Button(self.action_frame, text="View Books by Author", command=self._view_books_by_author)
        self.refresh_list_button = ttk.Button(self.action_frame, text="Show All Available", command=self.update_book_list)

        # --- Listbox ---
        self.listbox = tk.Listbox(self.list_frame, width=80, height=18, selectmode=tk.SINGLE, activestyle='none')
        self.listbox_scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.listbox_scrollbar.set)

    def _setup_layout(self):
        # --- Input Frame Layout ---
        self.input_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky='ew')
        self.input_frame.columnconfigure(1, weight=1)
        row = 0
        self.title_label.grid(row=row, column=0, sticky='w', pady=2)
        self.title_entry.grid(row=row, column=1, sticky='ew', pady=2)
        row += 1
        self.author_label.grid(row=row, column=0, sticky='w', pady=2)
        self.author_entry.grid(row=row, column=1, sticky='ew', pady=2)
        row += 1
        self.isbn_label.grid(row=row, column=0, sticky='w', pady=2)
        self.isbn_entry.grid(row=row, column=1, sticky='ew', pady=2)
        row += 1
        self.ebook_checkbox.grid(row=row, column=0, sticky='w', pady=2)
        row += 1
        self.size_label.grid(row=row, column=0, sticky='w', pady=2)
        self.size_entry.grid(row=row, column=1, sticky='ew', pady=2)
        row += 1
        self.add_button.grid(row=row, column=0, columnspan=2, pady=(10, 0))

        # --- Action Frame Layout ---
        self.action_frame.grid(row=1, column=0, padx=20, pady=10, sticky='ew')
        for i in range(3): self.action_frame.columnconfigure(i, weight=1)
        self.lend_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.return_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.remove_button.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        self.view_by_author_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        self.refresh_list_button.grid(row=1, column=2, padx=5, pady=5, sticky='ew')

        # --- List Frame Layout ---
        self.list_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky='nsew')
        self.root.rowconfigure(2, weight=1)
        self.list_frame.rowconfigure(0, weight=1)
        self.list_frame.columnconfigure(0, weight=1)
        self.listbox.grid(row=0, column=0, sticky='nsew')
        self.listbox_scrollbar.grid(row=0, column=1, sticky='ns')

    def _toggle_ebook_fields(self):
        if self.ebook_var.get():
            self.size_entry.config(state='normal')
        else:
            self.size_entry.delete(0, tk.END)
            self.size_entry.config(state='disabled')

    def _validate_isbn(self, isbn):
        return re.fullmatch(r'^\d{9}[\dX]|\d{13}$', isbn) is not None

    def _validate_download_size(self, size_str):
        try:
            size = float(size_str)
            return size > 0
        except ValueError:
            return False

    def _add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        isbn = self.isbn_entry.get().strip()
        is_ebook = self.ebook_var.get()
        size_str = self.size_entry.get().strip()

        if not title or not author or not isbn:
            messagebox.showerror("Error", "Title, Author, and ISBN are required.")
            return

        if not self._validate_isbn(isbn):
            messagebox.showerror("Error", "Invalid ISBN format. Please enter a 10 or 13 digit number (or 9 digits + 'X').")
            return

        if is_ebook:
            if not size_str:
                messagebox.showerror("Error", "Download size required for eBooks.")
                return
            if not self._validate_download_size(size_str):
                messagebox.showerror("Error", "Download size must be a positive number.")
                return
            try:
                book = EBook(title, author, isbn, float(size_str))
            except ValueError:
                messagebox.showerror("Error", "Invalid download size. Please enter a number.")
                return
        else:
            book = Book(title, author, isbn)

        self.library.add_book(book)
        messagebox.showinfo("Success", f"Book '{title}' added to the library.")
        self._clear_input_fields()
        self.update_book_list()

    def _lend_book(self):
        isbn = simpledialog.askstring("Lend Book", "Enter ISBN of the book to lend:")
        if isbn:
            try:
                self.library.lend_book(isbn.strip())
                messagebox.showinfo("Success", "Book lent successfully.")
                self.update_book_list()
            except BookNotAvailableError as e:
                messagebox.showerror("Error", str(e))

    def _return_book(self):
        isbn = simpledialog.askstring("Return Book", "Enter ISBN of the book to return:")
        if isbn:
            try:
                self.library.return_book(isbn.strip())
                messagebox.showinfo("Success", "Book returned successfully.")
                self.update_book_list()
            except BookNotAvailableError as e:
                messagebox.showerror("Error", str(e))

    def _remove_book(self):
        isbn = simpledialog.askstring("Remove Book", "Enter ISBN of the book to remove:")
        if isbn:
            try:
                self.library.remove_book(isbn.strip())
                messagebox.showinfo("Success", "Book removed from library.")
                self.update_book_list()
            except BookNotAvailableError as e:
                messagebox.showerror("Error", str(e))

    def _view_books_by_author(self):
        author = simpledialog.askstring("Search by Author", "Enter author's name:")
        if author:
            books = list(self.library.books_by_author(author.strip()))
            self.listbox.delete(0, tk.END)
            if books:
                self.listbox.insert(tk.END, f"--- Books by {author} ---")
                for idx, book in enumerate(books):
                    self.listbox.insert(tk.END, str(book))
                    if idx % 2 == 1:
                        self.listbox.itemconfig(tk.END, bg="#f0f0ff")
            else:
                self.listbox.insert(tk.END, "No books found by this author.")
            self.listbox.insert(tk.END, "")

    def update_book_list(self):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "--- Available Books in Library ---")
        available_books_found = False
        for idx, book in enumerate(self.library):
            self.listbox.insert(tk.END, str(book))
            if idx % 2 == 1:
                self.listbox.itemconfig(tk.END, bg="#f0f0ff")
            available_books_found = True
        if not available_books_found:
            self.listbox.insert(tk.END, "No books currently available.")
        self.listbox.insert(tk.END, "")

    def _clear_input_fields(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.isbn_entry.delete(0, tk.END)
        self.ebook_var.set(False)
        self.size_entry.delete(0, tk.END)
        self.size_entry.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
