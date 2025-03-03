import sys
import secrets
import string
import base64

# Kontrola a automatická inštalácia PyQt5, ak chýba
try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    from PyQt5 import QtWidgets, QtCore, QtGui


class TokenGenerator(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Token Generator")
        self.setGeometry(100, 100, 400, 300)
        self.setupUI()

    def setupUI(self):
        layout = QtWidgets.QVBoxLayout()

        # Názov aplikácie
        title = QtWidgets.QLabel("Secure Token Generator")
        title.setFont(QtGui.QFont("Arial", 18))
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        # Výber typu tokenu
        type_layout = QtWidgets.QHBoxLayout()
        type_label = QtWidgets.QLabel("Typ tokenu:")
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["Alfanumerický", "Hexadecimálny", "Base64"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Výber dĺžky tokenu
        length_layout = QtWidgets.QHBoxLayout()
        length_label = QtWidgets.QLabel("Dĺžka tokenu:")
        self.length_spin = QtWidgets.QSpinBox()
        self.length_spin.setRange(8, 128)
        self.length_spin.setValue(16)
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_spin)
        layout.addLayout(length_layout)

        # Zobrazenie vygenerovaného tokenu
        token_layout = QtWidgets.QHBoxLayout()
        self.token_edit = QtWidgets.QLineEdit()
        self.token_edit.setReadOnly(True)
        token_layout.addWidget(self.token_edit)
        layout.addLayout(token_layout)

        # Tlačidlá pre generovanie a kopírovanie tokenu
        button_layout = QtWidgets.QHBoxLayout()
        self.generate_button = QtWidgets.QPushButton("Generovať token")
        self.generate_button.clicked.connect(self.generateToken)
        self.copy_button = QtWidgets.QPushButton("Kopírovať token")
        self.copy_button.clicked.connect(self.copyToken)
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.copy_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def generateToken(self):
        token_type = self.type_combo.currentText()
        length = self.length_spin.value()
        token = ""

        if token_type == "Alfanumerický":
            chars = string.ascii_letters + string.digits
            token = ''.join(secrets.choice(chars) for _ in range(length))
        elif token_type == "Hexadecimálny":
            nbytes = (length + 1) // 2  # Zabezpečí požadovanú dĺžku
            token = secrets.token_hex(nbytes)[:length]
        elif token_type == "Base64":
            nbytes = length
            token = base64.urlsafe_b64encode(secrets.token_bytes(nbytes)).decode('utf-8').rstrip('=')
            token = token[:length]
        else:
            token = "Neznámy typ tokenu"

        self.token_edit.setText(token)

    def copyToken(self):
        token = self.token_edit.text()
        if token:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(token)
            QtWidgets.QMessageBox.information(self, "Kopírovanie", "Token bol skopírovaný do schránky! 😊")
        else:
            QtWidgets.QMessageBox.warning(self, "Chyba", "Žiadny token na kopírovanie. 😕")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Moderný tmavý dizajn aplikácie
    app.setStyleSheet("""
    QWidget {
        background-color: #2C2F33;
        color: #FFFFFF;
        font-family: Arial;
    }
    QPushButton {
        background-color: #7289DA;
        border: none;
        padding: 10px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #5b6eae;
    }
    QLineEdit, QComboBox, QSpinBox {
        background-color: #23272A;
        border: 1px solid #7289DA;
        border-radius: 5px;
        padding: 5px;
    }
    QLabel {
        font-size: 14px;
    }
    """)

    window = TokenGenerator()
    window.show()
    sys.exit(app.exec_())
