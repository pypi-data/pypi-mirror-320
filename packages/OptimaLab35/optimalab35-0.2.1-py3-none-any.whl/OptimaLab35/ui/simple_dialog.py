from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
# ChatGPT
class SimpleDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set default properties
        self.setGeometry(100, 100, 300, 100)

        # Create the layout
        layout = QVBoxLayout()

        # Create the label for the message
        self.message_label = QLabel(self)

        # Create the close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)

        # Add widgets to layout
        layout.addWidget(self.message_label)
        layout.addWidget(close_button)

        # Set layout for the dialog
        self.setLayout(layout)

    def show_dialog(self, title: str, message: str):
        self.setWindowTitle(title)  # Set the window title
        self.message_label.setText(message)  # Set the message text
        self.exec()  # Open the dialog as a modal window
