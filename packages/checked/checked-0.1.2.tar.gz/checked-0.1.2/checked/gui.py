import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QComboBox
    
from checked.cli import load_translations, convert_spreadsheet  # Import functions from cli.py

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Checked")
        self.setGeometry(100, 100, 400, 200)

        self.file_path = ""
        self.language = "EN"

        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select HTML File:"))

        self.file_entry = QLineEdit(self)
        layout.addWidget(self.file_entry)

        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_file)
        layout.addWidget(browse_button)

        layout.addWidget(QLabel("Select Language:"))

        self.language_combo = QComboBox(self)
        self.language_combo.addItems(['EN', 'PT'])
        layout.addWidget(self.language_combo)

        convert_button = QPushButton("Convert", self)
        convert_button.clicked.connect(self.convert_file)
        layout.addWidget(convert_button)

        self.setLayout(layout)

    def browse_file(self):
        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Select HTML File", "", "HTML Files (*.html);;All Files (*)", options=options)
        if self.file_path:
            self.file_entry.setText(self.file_path)

    def convert_file(self):
        if not self.file_path:
            QMessageBox.warning(self, "Warning", "Please select an HTML file.")
            return

        translations = load_translations('translations.json')
        if isinstance(translations, dict) and not translations:
            QMessageBox.critical(self, "Error", "No translations found or failed to load.")
            return

        result = convert_spreadsheet(self.file_path, self.language_combo.currentText(), translations)
        QMessageBox.information(self, "Result", result)

def main():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

