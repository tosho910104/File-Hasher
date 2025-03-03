import sys
import os
import hashlib

# Automatická inštalácia PyQt5, ak nie je nainštalovaná
try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    from PyQt5 import QtWidgets, QtCore, QtGui


class FileHasher(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Slovník prekladov pre SK / EN
        self.translations = {
            'en': {
                'windowTitle': "File Hasher",
                'selectFile': "Select file",
                'noFileSelected': "No file selected",
                'algorithm': "Algorithm",
                'hash': "Hash",
                'copy': "Copy",
                'exportTxt': "Export to TXT",
                'error': "Error",
                'errorLoadFile': "Failed to load file:\n{}",
                'copying': "Copying",
                'hashCopied': "Hash has been copied to clipboard! 😊",
                'errorNoFile': "No file to export.",
                'exportSuccess': "Export was successful! 😊",
                'exportFailed': "Export failed:\n{}",
                'fileName': "File name: ",
                'filePath': "File path: ",
                'language': "Language"
            },
            'sk': {
                'windowTitle': "File Hasher",
                'selectFile': "Vybrať súbor",
                'noFileSelected': "Žiadny súbor nevybraný",
                'algorithm': "Algoritmus",
                'hash': "Hash",
                'copy': "Kopírovať",
                'exportTxt': "Exportovať do TXT",
                'error': "Chyba",
                'errorLoadFile': "Nepodarilo sa načítať súbor:\n{}",
                'copying': "Kopírovanie",
                'hashCopied': "Hash bol skopírovaný do schránky! 😊",
                'errorNoFile': "Žiadny súbor na export.",
                'exportSuccess': "Export prebehol úspešne! 😊",
                'exportFailed': "Export sa nepodaril:\n{}",
                'fileName': "Názov súboru: ",
                'filePath': "Cesta k súboru: ",
                'language': "Jazyk"
            }
        }

        # Načítaj jazyk z QSettings (predvolene SK)
        self.currentLanguage = self.loadLanguage()

        self.file_path = None
        self.hashes = {}

        self.initUI()
        self.setLanguage(self.currentLanguage)  # Aplikujeme preklad

    def initUI(self):
        self.setGeometry(100, 100, 1280, 500)
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # Vytvorenie menu baru
        self.menuBar = QtWidgets.QMenuBar(self)
        self.languageMenu = self.menuBar.addMenu("")  # Titul nastavíme v translateUI

        # Vytvorenie akcií pre jazyky
        self.actionEnglish = QtWidgets.QAction("English", self)
        self.actionSlovak = QtWidgets.QAction("Slovak", self)
        self.actionEnglish.triggered.connect(lambda: self.setLanguage("en"))
        self.actionSlovak.triggered.connect(lambda: self.setLanguage("sk"))

        self.languageMenu.addAction(self.actionEnglish)
        self.languageMenu.addAction(self.actionSlovak)

        # Pridáme menu bar do layoutu
        main_layout.addWidget(self.menuBar)

        # Layout pre výber súboru
        file_layout = QtWidgets.QHBoxLayout()
        self.file_button = QtWidgets.QPushButton()
        self.file_button.clicked.connect(self.select_file)
        self.file_label = QtWidgets.QLabel()
        file_layout.addWidget(self.file_button)
        file_layout.addWidget(self.file_label)
        main_layout.addLayout(file_layout)

        # Tabuľka pre zobrazenie hashov
        self.hash_table = QtWidgets.QTableWidget()
        self.hash_table.setColumnCount(3)
        # Hlavičky budú nastavené v translateUI
        self.hash_table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.hash_table)

        # Tlačidlo pre export do TXT
        export_layout = QtWidgets.QHBoxLayout()
        self.export_button = QtWidgets.QPushButton()
        self.export_button.clicked.connect(self.export_to_txt)
        export_layout.addStretch()
        export_layout.addWidget(self.export_button)
        main_layout.addLayout(export_layout)

    # ----------------------------------------------------------------------
    #                    PREKLADY A NASTAVENIE JAZYKA
    # ----------------------------------------------------------------------
    def translateUI(self):
        """ Aplikuje preklad podľa self.currentLanguage. """
        t = self.translations[self.currentLanguage]

        self.setWindowTitle(t['windowTitle'])
        self.languageMenu.setTitle(t['language'])
        self.file_button.setText(t['selectFile'])
        # Ak ešte nebol vybraný súbor, nastav správu
        if not self.file_path:
            self.file_label.setText(t['noFileSelected'])
        self.export_button.setText(t['exportTxt'])
        # Hlavičky tabuľky
        headers = [t['algorithm'], t['hash'], t['copy']]
        self.hash_table.setHorizontalHeaderLabels(headers)
        # Aktualizácia tabuľky, ak už existujú hashe
        if self.hashes:
            self.populate_table()

    def loadLanguage(self):
        """ Načíta jazyk z QSettings, predvolene SK. """
        settings = QtCore.QSettings("MyCompany", "FileHasher")
        return settings.value("language", "sk")

    def setLanguage(self, lang_code):
        """ Uloží jazyk do QSettings a aplikuje preklad. """
        self.currentLanguage = lang_code
        settings = QtCore.QSettings("MyCompany", "FileHasher")
        settings.setValue("language", lang_code)
        self.translateUI()

    # ----------------------------------------------------------------------
    #                    FUNKCIE NA SPRACOVANIE SÚBORU
    # ----------------------------------------------------------------------
    def select_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            caption=self.translations[self.currentLanguage]['selectFile'],
            directory="",
            filter="All Files (*.*)",
            options=options
        )
        if file_name:
            self.file_path = file_name
            base_name = os.path.basename(file_name)
            self.file_label.setText(base_name)
            self.compute_hashes(file_name)

    def compute_hashes(self, file_path):
        self.hashes = {}
        # Algoritmy
        algorithms = [
            "md5", "sha1", "sha224", "sha256", "sha384", "sha512",
            "sha3_224", "sha3_256", "sha3_384", "sha3_512",
            "blake2b", "blake2s"
        ]
        hash_objs = {}
        for algo in algorithms:
            try:
                hash_objs[algo] = hashlib.new(algo)
            except ValueError:
                pass  # Algoritmus nemusí byť podporovaný

        try:
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    for obj in hash_objs.values():
                        obj.update(chunk)

            for algo, obj in hash_objs.items():
                self.hashes[algo.upper()] = obj.hexdigest()

        except Exception as e:
            err_title = self.translations[self.currentLanguage]['error']
            err_msg = self.translations[self.currentLanguage]['errorLoadFile'].format(str(e))
            QtWidgets.QMessageBox.warning(self, err_title, err_msg)
            return

        self.populate_table()

    def populate_table(self):
        t = self.translations[self.currentLanguage]
        self.hash_table.setRowCount(0)
        for row, (algo, hash_value) in enumerate(self.hashes.items()):
            self.hash_table.insertRow(row)

            algo_item = QtWidgets.QTableWidgetItem(algo)
            hash_item = QtWidgets.QTableWidgetItem(hash_value)

            # Tlačidlo pre kopírovanie hashu do schránky (podľa jazyka)
            copy_button = QtWidgets.QPushButton(t['copy'])
            copy_button.clicked.connect(lambda checked, h=hash_value: self.copy_to_clipboard(h))

            self.hash_table.setItem(row, 0, algo_item)
            self.hash_table.setItem(row, 1, hash_item)
            self.hash_table.setCellWidget(row, 2, copy_button)

        self.hash_table.resizeColumnsToContents()

    def copy_to_clipboard(self, text):
        t = self.translations[self.currentLanguage]
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)
        QtWidgets.QMessageBox.information(self, t['copying'], t['hashCopied'])

    def export_to_txt(self):
        t = self.translations[self.currentLanguage]
        if not self.file_path or not self.hashes:
            QtWidgets.QMessageBox.warning(self, t['error'], t['errorNoFile'])
            return

        options = QtWidgets.QFileDialog.Options()
        save_file, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            caption=t['exportTxt'],
            directory="",
            filter="Text Files (*.txt)",
            options=options
        )
        if save_file:
            try:
                with open(save_file, "w", encoding="utf-8") as f:
                    f.write(t['fileName'] + os.path.basename(self.file_path) + "\n")
                    f.write(t['filePath'] + os.path.abspath(self.file_path) + "\n\n")
                    for algo, hash_value in self.hashes.items():
                        f.write(f"{algo}: {hash_value}\n")
                QtWidgets.QMessageBox.information(self, t['windowTitle'], t['exportSuccess'])
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, t['error'], t['exportFailed'].format(str(e)))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Moderný a svieži dizajn aplikácie
    app.setStyleSheet("""
    QWidget {
        background-color: #f0f0f0;
        color: #333333;
        font-family: Arial, sans-serif;
        font-size: 14px;
    }
    QPushButton {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 8px 16px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QTableWidget {
        background-color: white;
        border: 1px solid #ddd;
    }
    QHeaderView::section {
        background-color: #4CAF50;
        color: white;
        padding: 4px;
        border: none;
    }
    QLineEdit, QComboBox, QSpinBox {
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 4px;
        background-color: #ffffff;
    }
    QLabel {
        font-size: 14px;
    }
    """)

    window = FileHasher()
    window.show()
    sys.exit(app.exec_())
