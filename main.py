from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase
from PyQt5.QtCore import Qt
import os
from ultralytics import YOLO
from video_tracking import process_video_with_tracking


class FightDetectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fight Detection App")
        screen = QApplication.primaryScreen().size()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        self.setStyleSheet("background-color: white;")

        # Флаг для отслеживания, сохранён ли файл
        self.is_file_saved = False

        # Настройка шрифта
        self.font = QFont("PIXY", 18)
        self.font.setBold(True)
        self.font.setStyleStrategy(QFont.PreferAntialias)

        font_path = os.path.join(os.path.dirname(__file__), "PIXY.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)

        self.video_path = None
        self.model = YOLO('yolov8m-pose.pt')
        self.create_ui()

    def create_ui(self):
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap("1.jpg"))
        self.background.setScaledContents(True)
        self.background.setGeometry(0, 0, self.width(), self.height())

        self.select_button = QPushButton("Выберите файл", self)
        self.select_button.setFont(self.font)
        self.select_button.setStyleSheet("background-color: #3a3837; color: white; border-radius: 10px;")
        self.select_button.clicked.connect(self.open_file_dialog)
        self.update_button_position(self.select_button)

        self.status_label = QLabel(self)
        self.status_label.setFont(self.font)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: white;")
        self.status_label.setAttribute(Qt.WA_TranslucentBackground)
        self.status_label.hide()

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите видеофайл", "", "Video Files (*.mp4 *.avi)",
                                                   options=options)
        if file_path:
            self.video_path = file_path
            self.start_processing()

    def start_processing(self):
        self.select_button.hide()
        self.background.setPixmap(QPixmap("2.jpg"))
        self.status_label.setText("В обработке...")
        self.update_label_position(self.status_label)
        self.status_label.show()
        self.process_video()

    def process_video(self):
        try:
            output_dir = "results"
            process_video_with_tracking(self.model, self.video_path, output_dir=output_dir, show_video=False,
                                        save_video=True)
            self.background.setPixmap(QPixmap("3.jpg"))
            self.status_label.hide()
            self.create_download_button()
        except Exception as e:
            self.status_label.setText(f"Ошибка: {str(e)}")

    def create_download_button(self):
        self.download_button = QPushButton("Скачать файл", self)
        self.download_button.setFont(self.font)
        self.download_button.setStyleSheet("background-color: #3a3837; color: white; border-radius: 10px;")
        self.download_button.clicked.connect(self.save_file_dialog)
        self.update_button_position(self.download_button)
        self.download_button.show()

    def save_file_dialog(self):
        result_file = os.path.join("results", "results.txt")
        save_path = os.path.join("results", "downloaded_results.txt")
        if os.path.exists(result_file):
            try:
                os.rename(result_file, save_path)
                self.status_label.setText("Файл успешно сохранён в папке 'results'.")
                self.update_label_position(self.status_label)
                self.status_label.show()
                self.is_file_saved = True
            except Exception as e:
                self.status_label.setText(f"Ошибка при сохранении: {str(e)}")
                self.update_label_position(self.status_label)
                self.status_label.show()
        else:
            self.status_label.setText("Результат не найден. Проверьте директорию.")
            self.update_label_position(self.status_label)
            self.status_label.show()

    def update_button_position(self, button):
        button_width, button_height = 200, 100
        button.setGeometry(
            (self.width() - button_width) // 2,
            (self.height() - button_height) // 2,
            button_width,
            button_height,
        )

    def update_label_position(self, label):
        label_width, label_height = 400, 50
        label.setGeometry(
            (self.width() - label_width) // 2,
            (self.height() - label_height) // 2,
            label_width,
            label_height,
        )

    def closeEvent(self, event):
        if not self.is_file_saved:
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                "Файл не сохранён. Вы уверены, что хотите выйти?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                event.ignore()  # Отменяем закрытие
            else:
                event.accept()
        else:
            event.accept()  # Закрываем приложение

    def resizeEvent(self, event):
        self.background.setGeometry(0, 0, self.width(), self.height())
        if hasattr(self, 'select_button') and self.select_button.isVisible():
            self.update_button_position(self.select_button)
        if hasattr(self, 'download_button') and self.download_button.isVisible():
            self.update_button_position(self.download_button)
        if self.status_label.isVisible():
            self.update_label_position(self.status_label)


if __name__ == "__main__":
    app = QApplication([])
    window = FightDetectionApp()
    window.show()
    app.exec_()
