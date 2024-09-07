import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication
from app.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    font = QFont()
    font.setPointSize(8)
    app.setFont(font)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

# ToDo pyinstaller --onefile -w --icon="favicon.ico" --name="vem" main.py
