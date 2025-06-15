import sys
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QProgressBar,
    QListWidget, QListWidgetItem, QWidget, QVBoxLayout, QPushButton, QDialog, QLabel, QHBoxLayout
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineDownloadItem


class DownloadsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Загрузки")
        self.resize(500, 300)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

    def add_download(self, download):
        item_widget = DownloadItemWidget(download)
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(item_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, item_widget)


class DownloadItemWidget(QWidget):
    def __init__(self, download: QWebEngineDownloadItem):
        super().__init__()
        self.download = download

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(download.path().split("/")[-1])
        self.progress = QProgressBar()
        self.cancel_btn = QPushButton("Отменить")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.cancel_btn)

        self.cancel_btn.clicked.connect(self.cancel_download)

        download.downloadProgress.connect(self.on_progress)
        download.finished.connect(self.on_finished)
        download.accept()

    def on_progress(self, received, total):
        if total > 0:
            self.progress.setValue(int(received * 100 / total))

    def on_finished(self):
        self.progress.setValue(100)
        self.cancel_btn.setText("Готово")
        self.cancel_btn.setEnabled(False)

    def cancel_download(self):
        self.download.cancel()
        self.cancel_btn.setText("Отменён")
        self.cancel_btn.setEnabled(False)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мой Браузер")
        self.resize(1200, 800)

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.downloadRequested.connect(self.on_download_requested)

        self.webview = QWebEngineView()
        self.webview.setUrl(QUrl("https://www.google.com"))
        self.setCentralWidget(self.webview)

        self._create_toolbar()
        self._create_downloads_window()

        self.webview.urlChanged.connect(self.update_urlbar)
        self.webview.loadProgress.connect(self.update_progress)

    def _create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        back_btn = QAction("←", self)
        back_btn.triggered.connect(self.webview.back)
        toolbar.addAction(back_btn)

        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(self.webview.forward)
        toolbar.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(self.webview.reload)
        toolbar.addAction(reload_btn)

        home_btn = QAction("🏠", self)
        home_btn.triggered.connect(self.navigate_home)
        toolbar.addAction(home_btn)

        toolbar.addSeparator()

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.urlbar)

        toolbar.addSeparator()

        downloads_btn = QAction("⬇️ Загрузки", self)
        downloads_btn.triggered.connect(self.show_downloads)
        toolbar.addAction(downloads_btn)

        # Прогресс загрузки страницы
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(120)
        self.progress_bar.setTextVisible(False)
        toolbar.addWidget(self.progress_bar)

        self.toolbar = toolbar

    def _create_downloads_window(self):
        self.downloads_window = DownloadsWindow()

    def navigate_home(self):
        self.webview.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        url = self.urlbar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.webview.setUrl(QUrl(url))

    def update_urlbar(self, qurl):
        self.urlbar.setText(qurl.toString())

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def on_download_requested(self, download):
        self.downloads_window.add_download(download)
        if not self.downloads_window.isVisible():
            self.downloads_window.show()

    def show_downloads(self):
        self.downloads_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Красивый минималистичный стиль
    app.setStyleSheet("""
        QToolBar {
            background-color: #282c34;
        }
        QLineEdit {
            background-color: #3c4048;
            border: none;
            color: white;
            padding: 5px;
            border-radius: 5px;
        }
        QLineEdit:focus {
            border: 1px solid #61afef;
        }
        QPushButton {
            background-color: #61afef;
            color: white;
            border-radius: 5px;
            padding: 4px 10px;
        }
        QPushButton:hover {
            background-color: #529ecc;
        }
        QLabel {
            color: white;
        }
        QProgressBar {
            background-color: #3c4048;
            border-radius: 5px;
            height: 15px;
            text-align: center;
            color: white;
        }
        QProgressBar::chunk {
            background-color: #61afef;
            border-radius: 5px;
        }
    """)

    window = Browser()
    window.show()
    sys.exit(app.exec_())
