from PyQt6.QtWidgets import QApplication, QLabel, QWidget, \
                             QGridLayout, QLineEdit, QPushButton
import sys
from datetime import datetime


class AgeCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Age Calculator")
        grid = QGridLayout()

        # Create widgets
        name_label = QLabel("Name:")
        self.name_line_edit = QLineEdit()

        dob_label = QLabel("Date of Birth:")
        self.dob_line_edit = QLineEdit()
        self.dob_line_edit.setPlaceholderText("mm/dd/yyyy")

        calculate_btn = QPushButton("Calculate Age")
        calculate_btn.clicked.connect(self.calculate_age)
        self.output_label = QLabel()

        # Add widgets to grid
        grid.addWidget(name_label, 0, 0)
        grid.addWidget(self.name_line_edit, 0, 1)
        grid.addWidget(dob_label, 1, 0)
        grid.addWidget(self.dob_line_edit, 1, 1)
        grid.addWidget(calculate_btn, 2, 0, 1, 1)
        grid.addWidget(self.output_label, 3, 0, 1, 2)

        self.setLayout(grid)

    def calculate_age(self):
        current_year = datetime.now().year
        date_of_birth = self.dob_line_edit.text()
        year_of_birth = (datetime.strptime(date_of_birth, "%m/%d/%Y")
                         .date().year)
        age = current_year - year_of_birth
        self.output_label.setText(f"{self.name_line_edit.text()} is {age} "
                                  f"years old")


app = QApplication(sys.argv)
age_calculator = AgeCalculator()
age_calculator.resize(300, 100)
age_calculator.show()
sys.exit(app.exec())


