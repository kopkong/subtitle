import sys
import argparse
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QColor, QFont


class SubtitleWindow(QMainWindow):
    def __init__(self, subtitle_file, color, position):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize properties
        self.subtitles = self.load_subtitles(subtitle_file)
        self.color = QColor(color)
        self.position = position
        self.current_index = 0

        # Main widget and layout
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.layout.setAlignment(Qt.AlignCenter)

        # Create two QLabel objects for displaying Chinese and English subtitles
        self.label_cn = QLabel("", self)
        self.label_en = QLabel("", self)

        # Configure labels
        self.label_cn.setStyleSheet(f"color: {self.color.name()};")
        self.label_cn.setFont(QFont("Arial", 24))
        self.label_cn.setAlignment(Qt.AlignCenter)

        self.label_en.setStyleSheet(f"color: {self.color.name()};")
        self.label_en.setFont(QFont("Arial", 18))
        self.label_en.setAlignment(Qt.AlignCenter)

        # Add labels to layout
        self.layout.addWidget(self.label_cn)
        self.layout.addWidget(self.label_en)

        self.setCentralWidget(self.widget)

        # Timer to update subtitles
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_subtitle)
        self.timer.start(100)  # Check every 100ms

        # Set initial geometry
        self.resize(800, 150)
        self.move_to_position()

        # Start playback time
        self.start_time = QTime.currentTime()

    def load_subtitles(self, subtitle_file):
        """Load subtitles from a file with time and text format."""
        subtitles = []
        with open(subtitle_file, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    try:
                        time_part, text_part = line.split(" ", 1)
                        time_ms = self.time_to_milliseconds(time_part)
                        chinese_text, english_text = text_part.split("|", 1)
                        subtitles.append((time_ms, chinese_text.strip(), english_text.strip()))
                    except ValueError:
                        print(f"Invalid subtitle format: {line}")
        return subtitles

    @staticmethod
    def time_to_milliseconds(time_str):
        """Convert HH:MM:SS.sss to milliseconds."""
        parts = time_str.split(":")
        hours, minutes, seconds = int(parts[0]), int(parts[1]), float(parts[2])
        return int((hours * 3600 + minutes * 60 + seconds) * 1000)

    def move_to_position(self):
        screen = QApplication.primaryScreen().availableGeometry()
        if self.position == 'bottom':
            self.move((screen.width() - self.width()) // 2, screen.height() - self.height() - 50)
        elif self.position == 'top':
            self.move((screen.width() - self.width()) // 2, 50)

    def update_subtitle(self):
        if self.current_index < len(self.subtitles):
            elapsed_time = self.start_time.msecsTo(QTime.currentTime())
            next_time, chinese_text, english_text = self.subtitles[self.current_index]

            if elapsed_time >= next_time:
                self.label_cn.setText(chinese_text)
                self.label_en.setText(english_text)
                self.current_index += 1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


def parse_args():
    parser = argparse.ArgumentParser(description="Desktop Subtitle Application")
    parser.add_argument("--file", type=str, required=True, help="Path to the subtitle file.")
    parser.add_argument("--color", type=str, default="white", help="Subtitle text color (default: white).")
    parser.add_argument("--position", type=str, choices=["top", "bottom"], default="bottom", help="Position of the subtitles on the screen (default: bottom).")
    return parser.parse_args()


def main():
    args = parse_args()
    app = QApplication(sys.argv)
    window = SubtitleWindow(args.file, args.color, args.position)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
