import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from PyQt6.QtCore import Qt, QTimer, QPoint, QRectF
from PyQt6.QtGui import QAction, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


APP_DIR = Path.home() / ".task_widget"
CONFIG_PATH = APP_DIR / "config.json"
TASKS_PATH = APP_DIR / "tasks.json"


@dataclass
class TaskItem:
    text: str
    completed: bool = False


DEFAULT_CONFIG = {
    "sound_enabled": True,
    "reminder_enabled": False,
    "reminder_interval": 30,
    "pomodoro_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "theme": "dark",
    "window_x": None,
    "window_y": None,
}


class TimerCircle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(180, 180)
        self.total_seconds = 25 * 60
        self.remaining_seconds = self.total_seconds
        self.phase_name = "Work"

    def set_timer(self, remaining_seconds: int, total_seconds: int, phase_name: str):
        self.remaining_seconds = max(0, remaining_seconds)
        self.total_seconds = max(1, total_seconds)
        self.phase_name = phase_name
        self.update()

    def paintEvent(self, event):
        del event
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(16, 16, -16, -16)
        cx = rect.center()
        radius = min(rect.width(), rect.height()) / 2

        track_color = QColor("#5a5a5a") if self._is_dark() else QColor("#d0d0d0")
        progress_color = QColor("#4CAF50")

        track_pen = QPen(track_color, 12)
        p.setPen(track_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(cx, radius, radius)

        ratio = 1 - (self.remaining_seconds / self.total_seconds)
        progress_pen = QPen(progress_color, 12)
        p.setPen(progress_pen)
        arc_rect = QRectF(cx.x() - radius, cx.y() - radius, radius * 2, radius * 2)
        p.drawArc(arc_rect, 90 * 16, int(-360 * ratio * 16))

        p.setPen(QColor("#ffffff") if self._is_dark() else QColor("#222222"))
        p.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        mins, secs = divmod(self.remaining_seconds, 60)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{self.phase_name}\n{mins:02d}:{secs:02d}")

    def _is_dark(self):
        return self.palette().window().color().value() < 130


class SettingsDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)

        layout = QFormLayout(self)

        self.sound_enabled = QCheckBox("Sound Enabled")
        self.sound_enabled.setChecked(config["sound_enabled"])

        self.reminder_enabled = QCheckBox("Reminder Enabled")
        self.reminder_enabled.setChecked(config["reminder_enabled"])

        self.reminder_interval = QSpinBox()
        self.reminder_interval.setRange(5, 240)
        self.reminder_interval.setValue(config["reminder_interval"])
        self.reminder_interval.setSuffix(" min")

        self.pomodoro_minutes = QSpinBox()
        self.pomodoro_minutes.setRange(5, 60)
        self.pomodoro_minutes.setValue(config["pomodoro_minutes"])
        self.pomodoro_minutes.setSuffix(" min")

        self.short_break_minutes = QSpinBox()
        self.short_break_minutes.setRange(1, 30)
        self.short_break_minutes.setValue(config["short_break_minutes"])
        self.short_break_minutes.setSuffix(" min")

        self.long_break_minutes = QSpinBox()
        self.long_break_minutes.setRange(1, 60)
        self.long_break_minutes.setValue(config["long_break_minutes"])
        self.long_break_minutes.setSuffix(" min")

        layout.addRow(self.sound_enabled)
        layout.addRow(self.reminder_enabled)
        layout.addRow("Reminder Interval:", self.reminder_interval)
        layout.addRow("Pomodoro Duration:", self.pomodoro_minutes)
        layout.addRow("Short Break:", self.short_break_minutes)
        layout.addRow("Long Break:", self.long_break_minutes)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addRow(btn_row)

    def to_config(self, base: dict) -> dict:
        base = base.copy()
        base.update(
            {
                "sound_enabled": self.sound_enabled.isChecked(),
                "reminder_enabled": self.reminder_enabled.isChecked(),
                "reminder_interval": self.reminder_interval.value(),
                "pomodoro_minutes": self.pomodoro_minutes.value(),
                "short_break_minutes": self.short_break_minutes.value(),
                "long_break_minutes": self.long_break_minutes.value(),
            }
        )
        return base


class TaskWidgetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Widget")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        APP_DIR.mkdir(parents=True, exist_ok=True)
        self.config = self.load_config()
        self.tasks: List[TaskItem] = self.load_tasks()

        self.is_break = False
        self.session_count = 0
        self.timer_running = False
        self.current_duration = self.config["pomodoro_minutes"] * 60
        self.remaining_seconds = self.current_duration
        self.drag_position = QPoint()

        self.qt_timer = QTimer(self)
        self.qt_timer.timeout.connect(self.tick)

        self._build_ui()
        self.apply_theme()
        self.refresh_tasks_ui()
        self.update_timer_ui()
        self.restore_window_position()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("Task & Reminder")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()

        self.theme_btn = QToolButton()
        self.theme_btn.setText("🌙" if self.config["theme"] == "dark" else "☀")
        self.theme_btn.clicked.connect(self.toggle_theme)

        settings_btn = QToolButton()
        settings_btn.setText("⚙")
        settings_btn.clicked.connect(self.open_settings)

        close_btn = QToolButton()
        close_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton))
        close_btn.clicked.connect(self.close)

        header.addWidget(self.theme_btn)
        header.addWidget(settings_btn)
        header.addWidget(close_btn)
        outer.addLayout(header)

        self.timer_circle = TimerCircle()
        outer.addWidget(self.timer_circle, alignment=Qt.AlignmentFlag.AlignHCenter)

        timer_row = QHBoxLayout()
        start_btn = QPushButton("Start")
        pause_btn = QPushButton("Pause")
        reset_btn = QPushButton("Reset")
        start_btn.clicked.connect(self.start_timer)
        pause_btn.clicked.connect(self.pause_timer)
        reset_btn.clicked.connect(self.reset_timer)
        timer_row.addWidget(start_btn)
        timer_row.addWidget(pause_btn)
        timer_row.addWidget(reset_btn)
        outer.addLayout(timer_row)

        add_row = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add task...")
        self.task_input.returnPressed.connect(self.add_task)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_task)
        add_row.addWidget(self.task_input)
        add_row.addWidget(add_btn)
        outer.addLayout(add_row)

        self.task_list = QListWidget()
        outer.addWidget(self.task_list)

        clear_btn = QPushButton("🗑 Clear")
        clear_btn.clicked.connect(self.clear_completed)
        outer.addWidget(clear_btn)

        self.setMinimumSize(340, 620)

    def add_task(self):
        text = self.task_input.text().strip()
        if not text:
            return
        self.tasks.append(TaskItem(text=text))
        self.task_input.clear()
        self.refresh_tasks_ui()
        self.save_tasks()

    def refresh_tasks_ui(self):
        self.task_list.clear()
        for idx, task in enumerate(self.tasks):
            item = QListWidgetItem()
            widget = QWidget()
            row = QHBoxLayout(widget)
            row.setContentsMargins(4, 2, 4, 2)

            chk = QCheckBox(task.text)
            chk.setChecked(task.completed)
            chk.setStyleSheet("QCheckBox::indicator { width: 16px; height: 16px; border-radius: 8px; }")
            if task.completed:
                chk.setStyleSheet(
                    "QCheckBox::indicator { width: 16px; height: 16px; border-radius: 8px; }"
                    "QCheckBox { text-decoration: line-through; color: gray; }"
                )
            chk.toggled.connect(lambda checked, i=idx: self.toggle_task(i, checked))
            row.addWidget(chk)

            del_btn = QToolButton()
            del_btn.setText("✕")
            del_btn.clicked.connect(lambda _=None, i=idx: self.delete_task(i))
            row.addWidget(del_btn)

            item.setSizeHint(widget.sizeHint())
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)

    def toggle_task(self, index: int, checked: bool):
        if 0 <= index < len(self.tasks):
            self.tasks[index].completed = checked
            self.refresh_tasks_ui()
            self.save_tasks()

    def delete_task(self, index: int):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.refresh_tasks_ui()
            self.save_tasks()

    def clear_completed(self):
        self.tasks = [t for t in self.tasks if not t.completed]
        self.refresh_tasks_ui()
        self.save_tasks()

    def start_timer(self):
        if not self.timer_running:
            self.qt_timer.start(1000)
            self.timer_running = True

    def pause_timer(self):
        self.qt_timer.stop()
        self.timer_running = False

    def reset_timer(self):
        self.pause_timer()
        if self.is_break:
            self.current_duration = self._break_duration_seconds()
        else:
            self.current_duration = self.config["pomodoro_minutes"] * 60
        self.remaining_seconds = self.current_duration
        self.update_timer_ui()

    def tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_timer_ui()
            return

        self.notify_done()
        if self.is_break:
            self.is_break = False
            self.current_duration = self.config["pomodoro_minutes"] * 60
        else:
            self.session_count += 1
            self.is_break = True
            self.current_duration = self._break_duration_seconds()

        self.remaining_seconds = self.current_duration
        self.update_timer_ui()

    def _break_duration_seconds(self):
        if self.session_count > 0 and self.session_count % 4 == 0:
            return self.config["long_break_minutes"] * 60
        return self.config["short_break_minutes"] * 60

    def notify_done(self):
        if self.config.get("sound_enabled", True):
            QApplication.beep()

    def update_timer_ui(self):
        phase = "Break" if self.is_break else "Work"
        self.timer_circle.set_timer(self.remaining_seconds, self.current_duration, phase)

    def open_settings(self):
        dlg = SettingsDialog(self.config, self)
        if dlg.exec():
            old_pomodoro = self.config["pomodoro_minutes"]
            self.config = dlg.to_config(self.config)
            self.save_config()

            if not self.timer_running and not self.is_break and old_pomodoro != self.config["pomodoro_minutes"]:
                self.current_duration = self.config["pomodoro_minutes"] * 60
                self.remaining_seconds = self.current_duration
                self.update_timer_ui()

    def toggle_theme(self):
        self.config["theme"] = "light" if self.config["theme"] == "dark" else "dark"
        self.theme_btn.setText("🌙" if self.config["theme"] == "dark" else "☀")
        self.apply_theme()
        self.save_config()

    def apply_theme(self):
        dark = self.config["theme"] == "dark"
        if dark:
            style = """
            QWidget { background: #1e1f22; color: #f2f2f2; font-family: Segoe UI; }
            QLineEdit, QListWidget, QSpinBox { background: #2a2d31; border: 1px solid #3a3d42; border-radius: 6px; padding: 6px; }
            QPushButton, QToolButton { background: #2f343a; border: 1px solid #474d55; border-radius: 6px; padding: 6px 10px; }
            QPushButton:hover, QToolButton:hover { background: #3b4148; }
            QLabel#title { font-size: 16px; font-weight: 600; }
            """
        else:
            style = """
            QWidget { background: #f4f5f7; color: #1c1c1c; font-family: Segoe UI; }
            QLineEdit, QListWidget, QSpinBox { background: #ffffff; border: 1px solid #d6d6d6; border-radius: 6px; padding: 6px; }
            QPushButton, QToolButton { background: #ffffff; border: 1px solid #d0d0d0; border-radius: 6px; padding: 6px 10px; }
            QPushButton:hover, QToolButton:hover { background: #f0f0f0; }
            QLabel#title { font-size: 16px; font-weight: 600; }
            """
        self.setStyleSheet(style)

    def load_config(self):
        if not CONFIG_PATH.exists():
            return DEFAULT_CONFIG.copy()
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(data)
            return merged
        except Exception:
            return DEFAULT_CONFIG.copy()

    def save_config(self):
        self.config["window_x"] = self.x()
        self.config["window_y"] = self.y()
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

    def load_tasks(self) -> List[TaskItem]:
        if not TASKS_PATH.exists():
            return []
        try:
            with open(TASKS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [TaskItem(**item) for item in data]
        except Exception:
            return []

    def save_tasks(self):
        with open(TASKS_PATH, "w", encoding="utf-8") as f:
            json.dump([asdict(t) for t in self.tasks], f, indent=2)

    def restore_window_position(self):
        x = self.config.get("window_x")
        y = self.config.get("window_y")
        if isinstance(x, int) and isinstance(y, int):
            self.move(x, y)

    def closeEvent(self, event):
        self.save_config()
        self.save_tasks()
        super().closeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


def main():
    app = QApplication(sys.argv)
    window = TaskWidgetApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
