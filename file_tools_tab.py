from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.tools import Tools
from ui.styles import Theme


class FileToolsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"background-color: {Theme.BG_CANVAS};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        header = QLabel("إدارة الملفات والمستندات")
        header.setFont(QFont("Segoe UI", 15, QFont.Bold))
        header.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        layout.addWidget(header)

        form = QFrame()
        form.setStyleSheet(f"""
            QFrame {{
                background: {Theme.BG_MAIN};
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
            }}
        """)
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(14, 14, 14, 14)
        form_layout.setSpacing(10)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("عنوان المستند")
        self.title_input.setStyleSheet(self._input_style())
        form_layout.addWidget(self.title_input)

        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("اكتب محتوى المستند أو اعرض هنا محتوى ملف مرفوع...")
        self.content_edit.setMinimumHeight(220)
        self.content_edit.setStyleSheet(self._text_style())
        form_layout.addWidget(self.content_edit)

        doc_buttons = QGridLayout()
        doc_buttons.setSpacing(8)
        buttons = [
            ("README", lambda: self.create_document("readme")),
            ("Word", lambda: self.create_document("word")),
            ("PowerPoint", lambda: self.create_document("powerpoint")),
            ("PDF", lambda: self.create_document("pdf")),
            ("رفع وقراءة ملف", self.load_file),
            ("حفظ التعديل النصي", self.save_text_changes),
            ("ضغط ملفات", self.compress_files),
            ("ضغط مجلد", self.compress_folder),
            ("فك الضغط", self.extract_archive),
        ]
        for index, (text, handler) in enumerate(buttons):
            button = self._button(text)
            button.clicked.connect(handler)
            doc_buttons.addWidget(button, index // 3, index % 3)
        form_layout.addLayout(doc_buttons)
        layout.addWidget(form, 1)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(140)
        self.output.setStyleSheet(f"""
            QTextEdit {{
                background: {Theme.BG_CODE};
                color: #A7F3D0;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-family: Consolas;
            }}
        """)
        layout.addWidget(self.output)

    def create_document(self, kind):
        title = self.title_input.text().strip() or "PeacockAI Document"
        content = self.content_edit.toPlainText()
        result = Tools.create_document(kind, title, content)
        self._show_result(result)

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "اختر ملف",
            "",
            "Supported (*.txt *.md *.py *.json *.html *.css *.csv *.docx *.pptx *.pdf);;All files (*)",
        )
        if not path:
            return
        result = Tools.read_file(path)
        if result.get("success"):
            self.current_file = path
            self.content_edit.setPlainText(result.get("content", ""))
            self.title_input.setText(path.split("/")[-1].split("\\")[-1])
        self._show_result(result)

    def save_text_changes(self):
        if not self.current_file:
            QMessageBox.information(self, "تنبيه", "ارفع ملفاً نصياً أولاً قبل الحفظ.")
            return
        result = Tools.edit_text_file(self.current_file, content=self.content_edit.toPlainText())
        self._show_result(result)

    def compress_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "اختر ملفات للضغط")
        if not paths:
            return
        output, _ = QFileDialog.getSaveFileName(self, "حفظ ملف ZIP", "archive.zip", "ZIP (*.zip)")
        result = Tools.compress(paths, output or None)
        self._show_result(result)

    def compress_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "اختر مجلد للضغط")
        if not folder:
            return
        output, _ = QFileDialog.getSaveFileName(self, "حفظ ملف ZIP", "folder.zip", "ZIP (*.zip)")
        result = Tools.compress([folder], output or None)
        self._show_result(result)

    def extract_archive(self):
        archive, _ = QFileDialog.getOpenFileName(
            self,
            "اختر ملف ضغط",
            "",
            "Archives (*.zip *.tar *.gztar *.bztar *.xztar);;All files (*)",
        )
        if not archive:
            return
        target = QFileDialog.getExistingDirectory(self, "اختر مجلد فك الضغط")
        result = Tools.extract(archive, target or None)
        self._show_result(result)

    def _show_result(self, result):
        if result.get("success"):
            self.output.append(f"{result.get('message', 'تمت العملية')}: {result.get('path', '')}")
        else:
            self.output.append(f"خطأ: {result.get('error', 'فشلت العملية')}")

    def _button(self, text):
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(40)
        button.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.BG_MAIN};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {Theme.PRIMARY_LIGHT};
                border-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_DARK};
            }}
        """)
        return button

    def _input_style(self):
        return f"""
            QLineEdit {{
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
                padding: 10px 12px;
                color: {Theme.TEXT_PRIMARY};
                background: {Theme.BG_MAIN};
            }}
            QLineEdit:focus {{
                border-color: {Theme.PRIMARY};
            }}
        """

    def _text_style(self):
        return f"""
            QTextEdit {{
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
                padding: 12px;
                color: {Theme.TEXT_PRIMARY};
                background: {Theme.BG_MAIN};
            }}
            QTextEdit:focus {{
                border-color: {Theme.PRIMARY};
            }}
        """
