from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QLabel, QWidget,
                             QGridLayout, QLineEdit, QPushButton,
                             QMainWindow, QTableWidget, QTableWidgetItem,
                             QDialog, QVBoxLayout, QComboBox, QToolBar,
                             QStatusBar, QMessageBox)
from PyQt6.QtGui import QAction, QIcon, QBrush, QColor
import sys

from mysql.connector import Error
from mysql.connector import connection


class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password="root",
                 database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        try:
            db_connection = connection.MySQLConnection(host=self.host,
                                                    user=self.user,
                                                    password=self.password,
                                                    database=self.database)
            if db_connection.is_connected():
                print("Connected")
                return db_connection

        except Error as e:
            print(f"Error while connecting to database: {e}")
            return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"),
                                     "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        add_about_action = QAction("About", self)
        help_menu_item.addAction(add_about_action)
        add_about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("icons/search.png"),
                                "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course",
                                              "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # create status bar and elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Listen for click event in table
        self.table.cellClicked.connect(self.add_buttons_to_statusbar)

    def add_buttons_to_statusbar(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QWidget)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()

        self.table.setRowCount(0)
        for row, data in enumerate(result):
            self.table.insertRow(row)
            for col, col_data in enumerate(data):
                self.table.setItem(row, col, QTableWidgetItem(str(col_data)))
        connection.close()

    def insert(self):
        student_dialog = InsertDialog()
        student_dialog.exec()

    def search(self):
        search_dialog = AddSearchDialogue()
        search_dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")

        content = """
        This app was created using PyQt6 and is the author's first attempt 
        at using this library
        """

        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = sms.table.currentRow()
        # Get id from selected row
        self.student_id = sms.table.item(index, 0).text()

        # Get student name from selected row
        student_name = sms.table.item(index, 1).text()

        # Add student name
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add courses
        course_name = sms.table.item(index, 2).text()
        self.course_names = QComboBox()
        self.course_names.addItems(["Select course from list below",
                                    "Biology",
                                    "Math",
                                    "Astronomy",
                                    "Physics"])
        self.course_names.setCurrentText(course_name)
        layout.addWidget(self.course_names)

        # Add mobile number
        mobile = sms.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        submit_student_button = QPushButton("Update Student Record")
        layout.addWidget(submit_student_button)
        submit_student_button.clicked.connect(self.update_student)

        self.setLayout(layout)

    def update_student(self):
        print("Running update")
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, "
                       "mobile = %s "
                       "WHERE id = %s",
                       (self.student_name.text(),
                        self.course_names.itemText(
                            self.course_names.currentIndex()),
                        self.mobile.text(),
                        self.student_id))

        self.student_name.clear()
        self.mobile.clear()
        self.course_names.setCurrentIndex(0)

        connection.commit()
        cursor.close()
        connection.close()
        sms.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        print("Instantiating")
        super().__init__()
        self.setWindowTitle("Delete Student Record")

        layout = QGridLayout()

        confirm = QLabel("Are you sure you want to delete this record?")
        layout.addWidget(confirm, 0, 0, 1, 2)

        confirm_delete_button = QPushButton("Confirm")
        layout.addWidget(confirm_delete_button, 2, 0)

        cancel_delete_button = QPushButton("Cancel")
        layout.addWidget(cancel_delete_button, 2, 1)

        self.setLayout(layout)

        confirm_delete_button.clicked.connect(self.delete_student)
        cancel_delete_button.clicked.connect(self.close)

    def delete_student(self):
        index = sms.table.currentRow()
        student_id = sms.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = %s", (student_id, ))

        connection.commit()
        cursor.close()
        connection.close()
        sms.load_data()

        self.close()

        deletion_confirmed = QMessageBox()
        deletion_confirmed.setWindowTitle("Success")
        deletion_confirmed.setText("The record was successfully deleted!")
        deletion_confirmed.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Add student name
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add courses
        self.course_names = QComboBox()
        self.course_names.addItems(["Select course from list below",
                                    "Biology",
                                    "Math",
                                    "Astronomy",
                                    "Physics"])
        layout.addWidget(self.course_names)

        # Add mobile number
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        submit_student_button = QPushButton("Register Student")
        layout.addWidget(submit_student_button)
        submit_student_button.clicked.connect(self.add_student)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_names.itemText(self.course_names.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES "
                       "(%s, %s,  %s)",
                       (name, course, mobile))
        self.student_name.clear()
        self.mobile.clear()
        self.course_names.setCurrentIndex(0)

        connection.commit()
        cursor.close()
        connection.close()
        sms.load_data()


class AddSearchDialogue(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Enter name to search for")
        layout.addWidget(self.student_name)

        search_button = QPushButton("Search")
        layout.addWidget(search_button)
        search_button.clicked.connect(self.search)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s",
                                (name,))
        result = cursor.fetchall()
        rows = list(result)
        print(rows)
        items = sms.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            table_item = sms.table.item(item.row(), 1)
            table_item.setSelected(True)

            # to set a background color do this
            # table_item.setBackground(QBrush(QColor(
            #     "red")))

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
sms = MainWindow()
sms.show()
sms.load_data()
sys.exit(app.exec())
