def get_code_android_code():
    return """
///////////////////////////////////////////////////////////////////
ANDROID CODE
ADAPTER
package com.example.zero.adapters
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.zero.R
import com.example.zero.models.Book
import java.util.List

class BooksAdapter(
    private val books: List<Book>,
    private val onRentClick: (Book) -> Unit
) : RecyclerView.Adapter<BooksAdapter.BookViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): BookViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_book, parent, false)
        return BookViewHolder(view)
    }

    override fun onBindViewHolder(holder: BookViewHolder, position: Int) {
        val book = books[position]
        holder.bind(book)
    }

    override fun getItemCount(): Int {
        return books.size
    }

    inner class BookViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val textViewTitle: TextView = itemView.findViewById(R.id.textViewTitle)
        private val textViewAuthor: TextView = itemView.findViewById(R.id.textViewAuthor)
        private val textViewPrice: TextView = itemView.findViewById(R.id.textViewPrice)
        private val textViewDate: TextView = itemView.findViewById(R.id.textViewDate)
        private val buttonRent: Button = itemView.findViewById(R.id.buttonRent)

        fun bind(book: Book) {
            textViewTitle.text = book.title
            textViewAuthor.text = book.author
            textViewPrice.text = "Price: ${book.price}"
            textViewDate.text = "Date: ${book.date}"

            buttonRent.setOnClickListener {
                onRentClick(book)
            }
        }
    }
}
BOOK
package com.example.zero.models

data class Book(
    val id: String,
    val title: String,
    val price: Int,
    val date: String,
    val author: String
)
RENTED_BOOK
package com.example.zero.models

data class RentedBook(
    val bookId: String,
    val rentDate: String,
    val returnDate: String
)
BOOKS_ACTIVITY
package com.example.zero

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.android.volley.Request
import com.android.volley.toolbox.JsonArrayRequest
import com.android.volley.toolbox.JsonObjectRequest
import com.android.volley.toolbox.Volley
import org.json.JSONObject

class BooksActivity : AppCompatActivity() {

    private lateinit var recyclerViewBooks: RecyclerView
    private lateinit var buttonRentedBooks: Button
    private var clientId: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_books)

        recyclerViewBooks = findViewById(R.id.recyclerViewBooks)
        buttonRentedBooks = findViewById(R.id.buttonRentedBooks)

        clientId = intent.getIntExtra("client_id", 0)

        recyclerViewBooks.layoutManager = LinearLayoutManager(this)

        loadBooks()

        buttonRentedBooks.setOnClickListener {
            val intent = Intent(this, RentedBooksActivity::class.java)
            intent.putExtra("client_id", clientId)
            startActivity(intent)
        }
    }

    private fun loadBooks() {
        val url = "http://10.0.2.2:5000/books"
        val requestQueue = Volley.newRequestQueue(this)

        val request = JsonArrayRequest(
            Request.Method.GET, url, null,
            { response ->
                val books = mutableListOf<Book>()
                for (i in 0 until response.length()) {
                    val book = response.getJSONObject(i)
                    books.add(Book(
                        book.getString("id"),
                        book.getString("title"),
                        book.getInt("price"),
                        book.getString("date"),
                        book.getString("author")
                    ))
                }

                val adapter = BooksAdapter(books) { book ->
                    rentBook(book.id)
                }
                recyclerViewBooks.adapter = adapter
            },
            { error ->
                Toast.makeText(this, "Error: ${error.message}", Toast.LENGTH_SHORT).show()
            }
        )

        requestQueue.add(request)
    }

    private fun rentBook(bookId: String) {
        val url = "http://10.0.2.2:5000/rent"
        val requestQueue = Volley.newRequestQueue(this)

        val jsonBody = JSONObject().apply {
            put("client_id", clientId)
            put("book_id", bookId)
            put("days", 14)
        }

        val request = JsonObjectRequest(
            Request.Method.POST, url, jsonBody,
            { response ->
                Log.d("API_RESPONSE", response.toString())
                Toast.makeText(this, "Book is rent", Toast.LENGTH_SHORT).show()
            },
            { error ->
                Log.e("API_ERROR", error.toString())
                val errorMessage = error.networkResponse?.data?.let {
                    String(it, Charsets.UTF_8)
                } ?: "Error"
                Toast.makeText(this, "Error: $errorMessage", Toast.LENGTH_SHORT).show()
            }
        )

        requestQueue.add(request)
    }
}
LOGIN_ACTIVITY
package com.example.zero

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.android.volley.Request
import com.android.volley.toolbox.JsonObjectRequest
import com.android.volley.toolbox.Volley
import org.json.JSONObject

class LoginActivity : AppCompatActivity() {

    private lateinit var editTextTicketNumber: EditText
    private lateinit var buttonLogin: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        editTextTicketNumber = findViewById(R.id.editTextTicketNumber)
        buttonLogin = findViewById(R.id.buttonLogin)

        buttonLogin.setOnClickListener {
            val ticketNumber = editTextTicketNumber.text.toString()
            if (ticketNumber.isNotEmpty()) {
                login(ticketNumber)
            } else {
                Toast.makeText(this, "Write tickets number", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun login(ticketNumber: String) {
        val url = "http://10.0.2.2:5000/login"
        val requestQueue = Volley.newRequestQueue(this)

        val jsonBody = JSONObject().apply {
            put("ticket_number", ticketNumber)
        }

        val request = JsonObjectRequest(
            Request.Method.POST, url, jsonBody,
            { response ->
                Log.d("API_RESPONSE", response.toString())
                try {
                    val clientId = response.getInt("client_id")
                    val intent = Intent(this, BooksActivity::class.java)
                    intent.putExtra("client_id", clientId)
                    startActivity(intent)
                } catch (e: Exception) {
                    Log.e("API_ERROR", "Error: ${e.message}")
                    Toast.makeText(this, "Error", Toast.LENGTH_SHORT).show()
                }
            },
            { error ->
                Log.e("API_ERROR", error.toString())
                Toast.makeText(this, "Error", Toast.LENGTH_SHORT).show()
            }
        )

        requestQueue.add(request)
    }
}
RENTED_BOOKS_ACTIVITY
package com.example.zero

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.android.volley.Request
import com.android.volley.toolbox.JsonArrayRequest
import com.android.volley.toolbox.Volley

class RentedBooksActivity : AppCompatActivity() {

    private lateinit var recyclerViewRentedBooks: RecyclerView
    private var clientId: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_rented_books)

        clientId = intent.getIntExtra("client_id", 0)

        recyclerViewRentedBooks = findViewById(R.id.recyclerViewRentedBooks)
        recyclerViewRentedBooks.layoutManager = LinearLayoutManager(this)

        loadRentedBooks()
    }

    private fun loadRentedBooks() {
        val url = "http://10.0.2.2:5000/rented_books/$clientId"
        val requestQueue = Volley.newRequestQueue(this)

        val request = JsonArrayRequest(
            Request.Method.GET, url, null,
            { response ->
                val rentedBooks = mutableListOf<RentedBook>()
                for (i in 0 until response.length()) {
                    val book = response.getJSONObject(i)
                    rentedBooks.add(RentedBook(
                        book.getString("book_id"),
                        book.getString("rent_date"),
                        book.getString("return_date")
                    ))
                }
                val adapter = RentedBooksAdapter(rentedBooks)
                recyclerViewRentedBooks.adapter = adapter
            },
            { error ->
                Toast.makeText(this, "Error: ${error.message}", Toast.LENGTH_SHORT).show()
            }
        )

        requestQueue.add(request)
    }
}
RENTED_BOOKS_ADAPTER
package com.example.zero.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.zero.R
import com.example.zero.models.RentedBook

class RentedBooksAdapter(
    private val rentedBooks: List<RentedBook>
) : RecyclerView.Adapter<RentedBooksAdapter.RentedBookViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RentedBookViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_rented_book, parent, false)
        return RentedBookViewHolder(view)
    }

    override fun onBindViewHolder(holder: RentedBookViewHolder, position: Int) {
        val rentedBook = rentedBooks[position]
        holder.bind(rentedBook)
    }

    override fun getItemCount(): Int {
        return rentedBooks.size
    }

    inner class RentedBookViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val textViewTitle: TextView = itemView.findViewById(R.id.textViewTitle)
        private val textViewRentDate: TextView = itemView.findViewById(R.id.textViewRentDate)
        private val textViewReturnDate: TextView = itemView.findViewById(R.id.textViewReturnDate)

        fun bind(rentedBook: RentedBook) {
            textViewTitle.text = "Book ID: ${rentedBook.bookId}"
            textViewRentDate.text = "Date rent: ${rentedBook.rentDate}"
            textViewReturnDate.text = "Back date: ${rentedBook.returnDate}"
        }
    }
}
"""


def get_code_pyqt():
    return """
    PYQT
json_editor_app.py
import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton, QListView, QMessageBox, QDateEdit
from PyQt5.QtCore import QStringListModel, QDate

class JsonEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_data()

    def initUI(self):
        self.setWindowTitle('JSON Editor')

        self.title_edit = QLineEdit(self)
        self.id_edit = QLineEdit(self)
        self.price_edit = QLineEdit(self)
        self.date_edit = QDateEdit(self)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.author_edit = QLineEdit(self)

        self.label1 = QLabel(self)
        self.label1.setText("Title")

        self.label2 = QLabel(self)
        self.label2.setText("ID")

        self.label3 = QLabel(self)
        self.label3.setText("Price")

        self.label4 = QLabel(self)
        self.label4.setText("Date")

        self.label5 = QLabel(self)
        self.label5.setText("Author")

        self.list_view = QListView(self)
        self.model = QStringListModel()
        self.list_view.setModel(self.model)

        self.add_button = QPushButton('Add', self)
        self.delete_button = QPushButton('Delete', self)
        self.edit_button = QPushButton('Edit', self)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label1)
        vbox.addWidget(self.title_edit)
        vbox.addWidget(self.label2)
        vbox.addWidget(self.id_edit)
        vbox.addWidget(self.label3)
        vbox.addWidget(self.price_edit)
        vbox.addWidget(self.label4)
        vbox.addWidget(self.date_edit)
        vbox.addWidget(self.label5)
        vbox.addWidget(self.author_edit)
        vbox.addWidget(self.list_view)

        hbox = QHBoxLayout()
        hbox.addWidget(self.add_button)
        hbox.addWidget(self.delete_button)
        hbox.addWidget(self.edit_button)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.list_view.clicked.connect(self.on_item_clicked)
        self.add_button.clicked.connect(self.add_item)
        self.delete_button.clicked.connect(self.delete_item)
        self.edit_button.clicked.connect(self.edit_item)

    def load_data(self):
        try:
            with open('data.json', 'r', encoding='utf-8') as file:
                self.data = json.load(file)
                self.update_list_view()
        except FileNotFoundError:
            self.data = []

    def save_data(self):
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def update_list_view(self):
        titles = [item['title'] for item in self.data]
        self.model.setStringList(titles)

    def on_item_clicked(self, index):
        selected_item = self.data[index.row()]
        self.title_edit.setText(selected_item['title'])
        self.id_edit.setText(selected_item['id'])
        self.price_edit.setText(str(selected_item['price']))
        self.date_edit.setDate(QDate.fromString(selected_item['date'], "yyyy-MM-dd"))
        self.author_edit.setText(selected_item['author'])

    def add_item(self):
        try:
            price = int(self.price_edit.text())
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Price must be an integer')
            return

        new_item = {
            'title': self.title_edit.text(),
            'id': self.id_edit.text(),
            'price': price,
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'author': self.author_edit.text()
        }
        self.data.append(new_item)
        self.save_data()
        self.update_list_view()
        QMessageBox.information(self, 'Success', 'Item added')

    def delete_item(self):
        index = self.list_view.currentIndex().row()
        if index >= 0:
            del self.data[index]
            self.save_data()
            self.update_list_view()
            QMessageBox.information(self, 'Success', 'Item deleted')
        else:
            QMessageBox.warning(self, 'Error', 'No item selected')

    def edit_item(self):
        index = self.list_view.currentIndex().row()
        if index >= 0:
            try:
                price = int(self.price_edit.text())
            except ValueError:
                QMessageBox.warning(self, 'Error', 'Price must be an integer')
                return

            self.data[index] = {
                'title': self.title_edit.text(),
                'id': self.id_edit.text(),
                'price': price,
                'date': self.date_edit.date().toString("yyyy-MM-dd"),
                'author': self.author_edit.text()
            }
            self.save_data()
            self.update_list_view()
            QMessageBox.information(self, 'Success', 'Item updated')
        else:
            QMessageBox.warning(self, 'Error', 'No item selected')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = JsonEditorApp()
    ex.show()
    sys.exit(app.exec_())
    """


def get_code_xml():
    return """
    /////////////////////////////////////////////////////
ANDROID XML


ACTIVITY_BOOKS.XML
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerViewBooks"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:layout_marginBottom="16dp"/>

    <Button
        android:id="@+id/buttonRentedBooks"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="My Books"
        android:backgroundTint="@color/black"
        android:textColor="@color/white"/>

</LinearLayout>



ACTIVITY_MAIN.XML
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    android:gravity="center">

    <EditText
        android:id="@+id/editTextTicketNumber"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="Ticket Number"
        android:inputType="number"
        android:maxLines="1"
        android:layout_marginBottom="16dp"/>

    <Button
        android:id="@+id/buttonLogin"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Login"
        android:backgroundTint="@color/black"
        android:textColor="@color/white"/>

</LinearLayout>



ACTIVITY_RENTED_BOOKS.XML
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerViewRentedBooks"
        android:layout_width="match_parent"
        android:layout_height="match_parent"/>

</LinearLayout>




ITEMS_BOOK.XML
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:padding="16dp"
    android:background="?attr/selectableItemBackground"
    android:focusable="true"
    android:clickable="true">

    <TextView
        android:id="@+id/textViewTitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Book Title"
        android:textSize="18sp"
        android:textStyle="bold"
        android:layout_marginBottom="8dp"/>

    <TextView
        android:id="@+id/textViewAuthor"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Author"
        android:textSize="16sp"
        android:layout_marginBottom="8dp"/>

    <TextView
        android:id="@+id/textViewPrice"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Price: 123"
        android:textSize="14sp"
        android:layout_marginBottom="8dp"/>

    <TextView
        android:id="@+id/textViewDate"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Date: 22.05.2006"
        android:textSize="14sp"
        android:layout_marginBottom="16dp"/>

    <Button
        android:id="@+id/buttonRent"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Rent"
        android:backgroundTint="@color/black"
        android:textColor="@color/white"/>

</LinearLayout>



ITEM_RENTED_BOOK.XML
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:padding="16dp"
    android:background="?attr/selectableItemBackground"
    android:focusable="true"
    android:clickable="true">

    <TextView
        android:id="@+id/textViewTitle"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Book Title"
        android:textSize="18sp"
        android:textStyle="bold"
        android:layout_marginBottom="8dp"/>

    <TextView
        android:id="@+id/textViewRentDate"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Rent Date: 22.05.2006"
        android:textSize="14sp"
        android:layout_marginBottom="8dp"/>

    <TextView
        android:id="@+id/textViewReturnDate"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Return Date: 29.05.2006"
        android:textSize="14sp"/>

</LinearLayout>
    """


def get_code_api():
    return """
    /////////////////////////////////////////
API
app.py
from flask import Flask, jsonify, request, abort
import json
from datetime import datetime, timedelta

app = Flask(__name__)

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    ticket_number = data.get('ticket_number')
    clients = load_data('clients.json')
    client = next((c for c in clients if c['ticket_number'] == ticket_number), None)
    if client:
        return jsonify({"message": "Login successful", "client_id": client['id']})
    else:
        abort(404, description="Client not found")

@app.route('/books', methods=['GET'])
def get_books():
    books = load_data('data.json')
    return jsonify(books)

@app.route('/rent', methods=['POST'])
def rent_book():
    data = request.json
    client_id = data.get('client_id')
    book_id = data.get('book_id')
    days = int(data.get('days', 1))

    if days > 14:
        return jsonify({"error": "Maximum rental period is 14 days"}), 400

    books = load_data('data.json')
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    rented_books = load_data('rented_books.json')
    rented_books.append({
        "client_id": client_id,
        "book_id": book_id,
        "rent_date": datetime.now().strftime("%Y-%m-%d"),
        "return_date": (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    })
    save_data('rented_books.json', rented_books)

    return jsonify({"message": "Book rented successfully"})

@app.route('/rented_books/<int:client_id>', methods=['GET'])
def get_rented_books(client_id):
    rented_books = load_data('rented_books.json')
    client_books = [rb for rb in rented_books if rb['client_id'] == client_id]
    return jsonify(client_books)

if __name__ == '__main__':
    app.run(debug=True)
    """