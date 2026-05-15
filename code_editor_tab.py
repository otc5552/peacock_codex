# ui/code_editor_tab.py
import os
import subprocess
import sys
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
                             QPushButton, QLabel, QFileDialog, QMessageBox,
                             QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat
from ui.styles import Theme
from core.tools import Tools

# ========== Highlighter ==========
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rules = []
        kw = QTextCharFormat()
        kw.setForeground(QColor("#FF79C6"))
        kw.setFontWeight(QFont.Bold)
        for w in ['def','class','import','from','if','else','elif','for','while','return','try','except','with','as','True','False','None','self','pass','break','continue','and','or','not','in','is']:
            self.rules.append((f"\\b{w}\\b", kw))
        
        s = QTextCharFormat()
        s.setForeground(QColor("#F1FA8C"))
        self.rules.append(('"[^"]*"', s))
        self.rules.append(("'[^']*'", s))
        
        c = QTextCharFormat()
        c.setForeground(QColor("#6272A4"))
        self.rules.append(("#[^\n]*", c))
    
    def highlightBlock(self, text):
        import re
        for p, f in self.rules:
            for m in re.finditer(p, text):
                self.setFormat(m.start(), m.end()-m.start(), f)

# ========== محرر الأكواد ==========
class CodeEditorTab(QWidget):
    code_saved = pyqtSignal(str, str)  # path, content
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.setStyleSheet(f"background-color: {Theme.BG_CANVAS};")

        # شريط الأدوات
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(16, 12, 16, 12)
        toolbar.setSpacing(8)
        
        self.file_label = QLabel("ملف جديد")
        self.file_label.setFont(QFont("Segoe UI", 11))
        self.file_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        toolbar.addWidget(self.file_label)
        toolbar.addStretch()
        
        # أزرار
        buttons = [
            ("فتح", self.open_file),
            ("حفظ", self.save_file),
            ("تشغيل", self.run_code),
            ("جديد", self.new_file),
        ]
        
        for text, func in buttons:
            btn = QPushButton(text)
            btn.setFont(QFont("Segoe UI", 10))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {Theme.BG_MAIN};
                    color: {Theme.TEXT_PRIMARY};
                    border: 1px solid {Theme.BORDER};
                    border-radius: 8px;
                    padding: 8px 14px;
                }}
                QPushButton:hover {{
                    background: {Theme.PRIMARY_LIGHT};
                    border-color: {Theme.PRIMARY};
                    color: {Theme.PRIMARY_DARK};
                }}
            """)
            btn.clicked.connect(func)
            toolbar.addWidget(btn)
        
        layout.addLayout(toolbar)
        
        # Splitter (محرر + مخرجات)
        splitter = QSplitter(Qt.Vertical)
        
        # محرر الكود
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Consolas", 13))
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0F172A;
                color: #E2E8F0;
                border: none;
                padding: 15px;
                selection-background-color: #334155;
            }
        """)
        self.editor.setTabStopWidth(40)
        self.highlighter = PythonHighlighter(self.editor.document())
        splitter.addWidget(self.editor)
        
        # مخرجات
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 11))
        self.output.setMaximumHeight(180)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #111827;
                color: #A7F3D0;
                border: none;
                padding: 10px;
            }
        """)
        splitter.addWidget(self.output)
        splitter.setSizes([500, 150])
        
        layout.addWidget(splitter, 1)
    
    def set_code(self, code):
        """تحميل الكود من الشات"""
        self.editor.setPlainText(code)
        self.file_label.setText("كود من PeacockAI")
    
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "فتح ملف", "", "Python (*.py);;HTML (*.html);;جميع الملفات (*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.editor.setPlainText(f.read())
                self.current_file = path
                self.file_label.setText(os.path.basename(path))
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل فتح الملف: {str(e)}")
    
    def save_file(self):
        content = self.editor.toPlainText()
        if not content:
            QMessageBox.warning(self, "تنبيه", "لا يوجد كود لحفظه!")
            return
        
        if self.current_file:
            path = self.current_file
        else:
            # اقتراح امتداد
            if "<html" in content.lower():
                default_ext = "html"
            else:
                default_ext = "py"
            path, _ = QFileDialog.getSaveFileName(self, "حفظ الملف", f"project.{default_ext}", 
                                                   "Python (*.py);;HTML (*.html);;جميع الملفات (*)")
        
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_file = path
                self.file_label.setText(os.path.basename(path))
                self.code_saved.emit(path, content)
                self.output.append(f"تم الحفظ: {path}")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل الحفظ: {str(e)}")
    
    def new_file(self):
        self.editor.clear()
        self.current_file = None
        self.file_label.setText("ملف جديد")
        self.output.clear()
        self.output.append("ملف جديد جاهز للكتابة")
    
    def run_code(self):
        content = self.editor.toPlainText()
        if not content:
            self.output.append("لا يوجد كود لتشغيله")
            return
        
        # حفظ مؤقت
        is_html = "<html" in content.lower() or "<!DOCTYPE html>" in content.lower()
        ext = ".html" if is_html else ".py"
        tmp_path = os.path.join(Tools.PROJECTS_DIR, f"temp_run_{datetime.now().strftime('%H%M%S')}{ext}")
        os.makedirs(Tools.PROJECTS_DIR, exist_ok=True)
        
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            self.output.append(f"فشل حفظ الملف المؤقت: {str(e)}")
            return
        
        self.output.clear()
        self.output.append(f"جاري التشغيل...\n{'='*50}")
        
        try:
            if is_html:
                os.startfile(tmp_path)
                self.output.append("تم فتح الملف في المتصفح")
            else:
                result = subprocess.run(
                    [sys.executable, tmp_path],
                    capture_output=True, text=True, timeout=30,
                    cwd=Tools.PROJECTS_DIR
                )
                if result.stdout:
                    self.output.append("المخرجات:")
                    self.output.append(result.stdout)
                if result.stderr:
                    self.output.append("أخطاء:")
                    self.output.append(result.stderr)
                if not result.stdout and not result.stderr:
                    self.output.append("تم التنفيذ بنجاح (لا يوجد مخرجات)")
        except subprocess.TimeoutExpired:
            self.output.append("انتهى وقت التشغيل (30 ثانية)")
        except Exception as e:
            self.output.append(f"خطأ: {str(e)}")
