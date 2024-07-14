from functools import wraps

from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QWidget, QGridLayout, QPlainTextEdit, QFrame
from loguru import logger


class LogWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.handler_id = None

        layout = QGridLayout()

        self.text_browser = CustomPlainTextEdit()
        self.text_browser.setReadOnly(True)
        self.text_browser.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(self.text_browser, 1, 1, 1, 1)
        self.setLayout(layout)

    def write(self, message):
        self.text_browser.write(message)

    def rewrite(self, message):
        self.text_browser.rewrite(message)

    def write_html(self, message):
        self.text_browser.write_html(message)

    def flush(self):
        self.text_browser.flush()

    def add_logger(self):
        if self.handler_id is None:
            self.handler_id = logger.add(self._loguru_handler)

    def remove_logger(self):
        if self.handler_id is not None:
            logger.remove(self.handler_id)
        self.handler_id = None

    def _loguru_handler(self, message):
        record = message.record
        level = record["level"].name
        log_message = record["message"]

        match level:
            case "DEBUG":
                html_message = f'<span style="color: green;">DEBUG: {log_message}</span>'
            case "INFO":
                html_message = f'<span style="color: black;">INFO: {log_message}</span>'
            case "WARNING":
                html_message = f'<span style="color: orange;">WARNING: {log_message}</span>'
            case "ERROR":
                html_message = f'<span style="color: red;">ERROR: {log_message}</span>'
            case "CRITICAL":
                html_message = f'<span style="color: purple;">CRITICAL: {log_message}</span>'
            case _:
                html_message = log_message

        self.write_html(html_message)


class CustomPlainTextEdit(QPlainTextEdit):
    def write(self, message):
        message = message.strip()
        if message:
            QMetaObject.invokeMethod(self, "appendPlainText", Qt.ConnectionType.QueuedConnection, Q_ARG(str, message))

    def rewrite(self, message):
        message = message.strip()
        if message:
            self.moveCursor(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)
            self.moveCursor(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.MoveAnchor)
            self.moveCursor(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            self.textCursor().removeSelectedText()
            QMetaObject.invokeMethod(self, "appendPlainText", Qt.ConnectionType.QueuedConnection, Q_ARG(str, message))

    def write_html(self, message):
        message = message.strip()
        if message:
            QMetaObject.invokeMethod(self, "appendHtml", Qt.ConnectionType.QueuedConnection, Q_ARG(str, message))

    def flush(self):
        QMetaObject.invokeMethod(self, "clear", Qt.ConnectionType.QueuedConnection)
