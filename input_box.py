from PyQt5.QtCore import QEvent, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QMenu, QPushButton, QTextEdit, QVBoxLayout

from ui.styles import Theme


class InputBox(QFrame):
    message_sent = pyqtSignal(str)
    file_selected = pyqtSignal(str)
    action_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(132)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_MAIN};
                border-top: 1px solid {Theme.BORDER};
            }}
        """)
        self.is_processing = False
        self.dot_count = 0
        self.dot_timer = QTimer()
        self.dot_timer.timeout.connect(self._update_thinking_text)
        self.setup_ui()

    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 16, 28, 14)
        outer.setSpacing(8)

        composer = QFrame()
        composer.setObjectName("composer")
        composer.setStyleSheet(f"""
            QFrame#composer {{
                background-color: {Theme.BG_INPUT};
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
            }}
        """)
        row = QHBoxLayout(composer)
        row.setContentsMargins(10, 10, 10, 10)
        row.setSpacing(10)

        self.send_btn = QPushButton("↑")
        self.send_btn.setToolTip("إرسال")
        self.send_btn.setFixedSize(42, 42)
        self.send_btn.setFont(QFont("Segoe UI", 17, QFont.Bold))
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self._apply_send_style()
        self.send_btn.clicked.connect(self.send)
        row.addWidget(self.send_btn)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("اكتب رسالتك...")
        self.text_edit.setFont(QFont("Segoe UI", 12))
        self.text_edit.setFixedHeight(58)
        self.text_edit.setAcceptRichText(False)
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                color: {Theme.TEXT_PRIMARY};
                background-color: transparent;
                padding: 8px 6px;
            }}
            QTextEdit:disabled {{
                color: {Theme.TEXT_LIGHT};
            }}
        """)
        self.text_edit.installEventFilter(self)
        row.addWidget(self.text_edit, 1)

        self.attach_btn = QPushButton("+")
        self.attach_btn.setToolTip("فتح أدوات PeacockAI")
        self.attach_btn.setFixedSize(42, 42)
        self.attach_btn.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.attach_btn.setCursor(Qt.PointingHandCursor)
        self.attach_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BG_CANVAS};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY_LIGHT};
                border-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_DARK};
            }}
        """)
        self.attach_btn.clicked.connect(self.show_action_menu)
        row.addWidget(self.attach_btn)

        outer.addWidget(composer)

        hint = QLabel("Enter للإرسال، Shift+Enter لسطر جديد")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"color: {Theme.TEXT_LIGHT}; font-size: 11px; border: none;")
        outer.addWidget(hint)

    def eventFilter(self, obj, event):
        if obj == self.text_edit and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
                self.send()
                return True
        return super().eventFilter(obj, event)

    def send(self):
        if self.is_processing:
            return
        text = self.text_edit.toPlainText().strip()
        if text:
            self.message_sent.emit(text)
            self.text_edit.clear()

    def pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "اختر ملف",
            "",
            "Supported (*.txt *.md *.py *.json *.html *.css *.csv *.docx *.pptx *.pdf *.zip);;All files (*)",
        )
        if path:
            self.file_selected.emit(path)

    def show_action_menu(self):
        menu = QMenu(self)
        actions = [
            ("فتح الكاميرا", "camera"),
            ("ملفات", "upload"),
            ("صور", "image"),
            ("بحث تفصيلي", "search"),
            ("إنشاء فيديوهات", "video"),
            ("تفكير عميق", "deep_thinking"),
            ("كودكس", "codex"),
        ]
        for label, action_id in actions:
            action = menu.addAction(label)
            action.triggered.connect(lambda checked=False, value=action_id: self.handle_action(value))
        menu.exec_(self.attach_btn.mapToGlobal(self.attach_btn.rect().bottomLeft()))

    def handle_action(self, action_id):
        if action_id == "upload":
            self.pick_file()
            return

        prefixes = {
            "image": "ولّد صورة: ",
            "video": "ولّد فيديو: ",
            "search": "ابحث تفصيلياً في الانترنت عن: ",
            "deep_thinking": "فكّر بعمق وحلل كل الاحتمالات ثم أجب عن: ",
            "codex": "كودكس: اصنع أو عدّل الكود المطلوب لـ: ",
        }
        if action_id in prefixes:
            self.text_edit.setFocus()
            self.text_edit.setPlainText(prefixes[action_id])
            cursor = self.text_edit.textCursor()
            cursor.movePosition(cursor.End)
            self.text_edit.setTextCursor(cursor)

        self.action_selected.emit(action_id)

    def set_processing(self, processing):
        self.is_processing = processing
        self.text_edit.setEnabled(not processing)
        self.send_btn.setEnabled(not processing)
        self.attach_btn.setEnabled(not processing)

        if processing:
            self.dot_count = 0
            self.send_btn.setText("...")
            self.text_edit.setPlaceholderText("PeacockAI يفكر")
            self.dot_timer.start(500)
        else:
            self.dot_timer.stop()
            self.text_edit.setPlaceholderText("اكتب رسالتك...")
            self.send_btn.setText("↑")
            self._apply_send_style()

    def _update_thinking_text(self):
        dots = "." * ((self.dot_count % 3) + 1)
        self.text_edit.setPlaceholderText(f"PeacockAI يفكر{dots}")
        self.dot_count += 1

    def _apply_send_style(self):
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.TEXT_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY};
            }}
            QPushButton:disabled {{
                background-color: {Theme.BORDER};
                color: {Theme.TEXT_LIGHT};
            }}
        """)
