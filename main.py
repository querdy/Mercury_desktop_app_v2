import sys

from PyQt6.QtWidgets import QApplication

from app.database.postgre import SessionLocal
from app.window.main import MainWindow


def main():
    db_session = SessionLocal()
    try:
        app = QApplication(sys.argv)
        main_window = MainWindow(db_session=db_session)
        main_window.show()
        sys.exit(app.exec())
    finally:
        db_session.close()


if __name__ == "__main__":
    main()

# ToDo pyinstaller --onefile -w --icon="favicon.ico" --name="veterinary events adder" main.py
