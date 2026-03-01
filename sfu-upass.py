import sys
import traceback

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QVBoxLayout, QTextEdit, QComboBox
)
from PySide6.QtCore import QObject, QThread, Signal

from selenium import webdriver
from selenium.common.exceptions import NoSuchDriverException

from upass import UPass


class UPassWorker(QObject):
    finished = Signal()
    log = Signal(str)
    error = Signal(str)
    
    def __init__(self, browser):
        super().__init__()
        self.browser = browser

    def run(self):
        driver = None
        try:
            self.log.emit("Starting browser...")

            if self.browser == "Firefox":
                options = webdriver.FirefoxOptions()
                options.add_argument("--headless")
                driver = webdriver.Firefox(options=options)

            elif self.browser == "Safari":
                options = webdriver.SafariOptions()
                driver = webdriver.Safari(options=options)

            else:
                options = webdriver.ChromeOptions()
                options.add_argument("--headless=new")
                options.add_argument("--log-level=2")
                driver = webdriver.Chrome(options=options)

            upass = UPass(log_callback=self.log.emit)
            upass.request(driver)

        except Exception:
            self.error.emit(traceback.format_exc())
        
        finally:
            if driver:
                self.log.emit("Closing browser")
                driver.quit()
            
            self.finished.emit()

        
# -------------------------
# GUI
# -------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("U-Pass Request Tool")

        self.browser_select = QComboBox()
        self.browser_select.addItems(["Chrome", "Firefox", "Safari"])

        self.start_button = QPushButton("Request U-Pass")
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.browser_select)
        layout.addWidget(self.start_button)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

        self.start_button.clicked.connect(self.start_worker)

    def start_worker(self):
        self.start_button.setEnabled(False)

        browser = self.browser_select.currentText()

        self.thread = QThread()
        self.worker = UPassWorker(browser)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(
            lambda: self.start_button.setEnabled(True)
        )

        self.worker.log.connect(self.update_log)
        self.worker.error.connect(self.show_error)

        self.thread.start()

    def update_log(self, message):
        self.log_output.append(message)

    def show_error(self, error_text):
        self.log_output.append("ERROR:\n" + error_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(500, 500)
    window.show()
    sys.exit(app.exec())