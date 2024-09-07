from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QFrame
from loguru import logger


class TextInfoWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.handler_id = None

        layout = QVBoxLayout()

        self.text_browser = QPlainTextEdit()
        self.text_browser.setReadOnly(True)
        self.text_browser.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(self.text_browser)
        self.setLayout(layout)

    def write(self, message):
        message = message.strip()
        if message:
            QMetaObject.invokeMethod(
                self.text_browser, "appendPlainText",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, message)
            )

    def rewrite(self, message):
        message = message.strip()
        if message:
            self.text_browser.moveCursor(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)
            self.text_browser.moveCursor(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.MoveAnchor)
            self.text_browser.moveCursor(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            self.text_browser.textCursor().removeSelectedText()
            QMetaObject.invokeMethod(
                self.text_browser, "appendPlainText",
                Qt.ConnectionType.QueuedConnection, Q_ARG(str, message)
            )

    def write_html(self, message):
        message = message.strip()
        if message:
            QMetaObject.invokeMethod(
                self.text_browser, "appendHtml",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, message)
            )

    def flush(self):
        QMetaObject.invokeMethod(self.text_browser, "clear", Qt.ConnectionType.QueuedConnection)

    def add_logger(self):
        if self.handler_id is None:
            self.handler_id = logger.add(self._loguru_handler)

    def remove_logger(self):
        if self.handler_id is not None:
            logger.remove(self.handler_id)
        self.handler_id = None

    def _loguru_handler(self, message):
        record = message.record
        level = record["level"]
        log_message = record["message"]
        match level.name:
            case "DEBUG":
                html_message = f'<span style="color: green;">{level.icon}: {log_message}</span>'
            case "INFO":
                html_message = f'<span style="color: black;">{level.icon}: {log_message}</span>'
            case "WARNING":
                html_message = f'<span style="color: orange;">{level.icon}: {log_message}</span>'
            case "ERROR":
                html_message = f'<span style="color: red;">{level.icon}: {log_message}</span>'
            case "CRITICAL":
                html_message = f'<span style="color: purple;">{level.icon}: {log_message}</span>'
            case _:
                html_message = log_message

        self.write_html(html_message)
