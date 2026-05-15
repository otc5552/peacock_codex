"""
🎨 Peacock4.1 Interface - ChatGPT Style
واجهة احترافية مثل ChatGPT من OpenAI
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QLabel, QFrame, QListWidget, QListWidgetItem, QFileDialog, QScrollArea
)
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QTextCursor
from PyQt5.QtCore import Qt, QSize
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ai_engine import AIEngine
from tools.saver import save_code
from tools.utils import is_code, clean_response


class ChatUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🦚 Peacock4.1 - ChatGPT Style")
        self.resize(1600, 900)
        
        # محركات الذكاء الاصطناعي
        self.ai_engine = AIEngine(model_name="deepseek-coder:latest")
        self.mistral_engine = AIEngine(model_name="mistral:latest")
        
        self._setup_ui()
        self._add_welcome_message()
    
    def _setup_ui(self):
        """تنظيم الواجهة - تصميم ChatGPT"""
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        
        # ============ الشريط الجانبي الأسود ============
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #10a37f;
                border-right: 1px solid #0d7850;
            }
        """)
        sidebar.setMaximumWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # زر New Chat
        new_chat_btn = QPushButton("+ محادثة جديدة")
        new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
                margin: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        new_chat_btn.clicked.connect(self.new_chat)
        sidebar_layout.addWidget(new_chat_btn)
        
        # قائمة المحادثات
        history_label = QLabel("المحادثات الأخيرة")
        history_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                margin: 12px 16px 8px 16px;
                font-weight: bold;
            }
        """)
        sidebar_layout.addWidget(history_label)
        
        self.chat_history = QListWidget()
        self.chat_history.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                color: rgba(255, 255, 255, 0.8);
                padding: 10px;
                margin: 0px 8px;
                border-radius: 6px;
                border: none;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:selected {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        sidebar_layout.addWidget(self.chat_history)
        
        sidebar_layout.addStretch()
        
        # الإعدادات (في الأسفل)
        settings_btn = QPushButton("⚙️ الإعدادات")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: rgba(255, 255, 255, 0.7);
                border: none;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        sidebar_layout.addWidget(settings_btn)
        
        main.addWidget(sidebar)
        
        # ============ منطقة الدردشة الرئيسية ============
        chat_area = QVBoxLayout()
        chat_area.setContentsMargins(0, 0, 0, 0)
        chat_area.setSpacing(0)
        
        # منطقة الرسائل (قابلة للتمرير)
        self.messages_container = QFrame()
        self.messages_container.setStyleSheet("background-color: white; border: none;")
        
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(12)
        self.messages_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidget(self.messages_container)
        scroll.setStyleSheet("QScrollArea { background-color: white; border: none; }")
        scroll.setWidgetResizable(True)
        chat_area.addWidget(scroll)
        
        # حقل الإدخال (في الأسفل)
        input_container = QFrame()
        input_container.setStyleSheet("background-color: white; border-top: 1px solid #e5e7eb;")
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(20, 20, 20, 20)
        input_layout.setSpacing(12)
        
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("اكتب رسالتك... (Ctrl+Enter لإرسال)")
        self.input_field.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                background-color: white;
            }
            QTextEdit:focus {
                border: 2px solid #10a37f;
                outline: none;
            }
        """)
        self.input_field.setFixedHeight(70)
        self.input_field.keyPressEvent = self._handle_key_press
        input_layout.addWidget(self.input_field)
        
        # أزرار الإجراءات
        btn_layout = QHBoxLayout()
        
        upload_btn = QPushButton("📎 رفع ملف")
        upload_btn.setStyleSheet(self._button_style("#6b7280"))
        upload_btn.clicked.connect(self.upload_file)
        btn_layout.addWidget(upload_btn)
        
        btn_layout.addStretch()
        
        self.send_btn = QPushButton("إرسال")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0d7850;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        btn_layout.addWidget(self.send_btn)
        
        input_layout.addLayout(btn_layout)
        chat_area.addWidget(input_container)
        
        main.addLayout(chat_area, 1)
    
    def _button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """
    
    def _add_welcome_message(self):
        """إضافة رسالة الترحيب"""
        welcome_msg = "مرحباً! 👋 أنا بيكوك الطاووس 🦚\n\nأنا متخصص في:\n• بناء التطبيقات\n• إنشاء المواقع\n• تطوير الألعاب\n• كتابة الأكواد البرمجية\n\nكيف يمكنني مساعدتك؟"
        self._add_message(welcome_msg, "assistant")
    
    def send_message(self):
        """إرسال رسالة"""
        text = self.input_field.toPlainText().strip()
        if not text:
            return
        
        # عرض رسالة المستخدم
        self._add_message(text, "user")
        self.input_field.clear()
        
        # إزالة التمدد وإضافة مؤشر تحميل
        if self.messages_layout.count() > 0:
            self.messages_layout.itemAt(self.messages_layout.count() - 1).widget().deleteLater()
        
        self._add_message("⏳ جاري الكتابة...", "assistant")
        
        try:
            # الحصول على الرد
            reply = self.ai_engine.chat(text)
            reply = clean_response(reply) if reply else "عذراً، لم أتمكن من الحصول على رد"
            
            # إزالة مؤشر التحميل
            if self.messages_layout.count() > 0:
                item = self.messages_layout.itemAt(self.messages_layout.count() - 1)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            
            # إضافة الرد الفعلي
            self._add_message(reply, "assistant")
            
            # حفظ الكود إذا لزم الأمر
            if is_code(reply):
                code_path = save_code(reply)
                self._add_message(f"✅ تم حفظ الكود: {code_path}", "system")
            
            # إضافة المحادثة للسجل
            self.chat_history.addItem(QListWidgetItem(f"💬 {text[:40]}..."))
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            
            # إزالة مؤشر التحميل
            if self.messages_layout.count() > 0:
                item = self.messages_layout.itemAt(self.messages_layout.count() - 1)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            
            error_msg = f"❌ خطأ: {str(e)}\n\n💡 الحل: تأكد من تشغيل ollama:\nollama serve"
            self._add_message(error_msg, "error")
        
        # إعادة التمدد
        self.messages_layout.addStretch()
    
    def _add_message(self, text, sender):
        """إضافة رسالة مع تنسيق مثل ChatGPT"""
        msg_frame = QFrame()
        msg_frame.setStyleSheet("background-color: transparent; border: none;")
        
        msg_layout = QHBoxLayout(msg_frame)
        msg_layout.setContentsMargins(0, 0, 0, 0)
        msg_layout.setSpacing(10)
        
        # إنشاء فقاعة الرسالة
        bubble = QFrame()
        bubble.setStyleSheet("""
            QFrame {
                border-radius: 12px;
                padding: 12px 16px;
            }
        """)
        
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        
        if sender == "user":
            # رسالة المستخدم: زرقاء على اليمين
            bubble.setStyleSheet("""
                QFrame {
                    background-color: #10a37f;
                    border-radius: 12px;
                    padding: 12px 16px;
                }
            """)
            msg_layout.addStretch()
            
            text_label = QLabel(text)
            text_label.setStyleSheet("color: white; font-size: 14px;")
            text_label.setWordWrap(True)
            bubble_layout.addWidget(text_label)
            
            bubble.setMaximumWidth(600)
        
        elif sender == "assistant":
            # رسالة المساعد: رمادية على اليسار
            bubble.setStyleSheet("""
                QFrame {
                    background-color: #f7f7f8;
                    border-radius: 12px;
                    padding: 12px 16px;
                }
            """)
            
            text_label = QLabel(text)
            text_label.setStyleSheet("color: #000; font-size: 14px;")
            text_label.setWordWrap(True)
            bubble_layout.addWidget(text_label)
            
            msg_layout.addWidget(bubble)
            msg_layout.addStretch()
            bubble.setMaximumWidth(600)
        
        elif sender == "error":
            # رسالة الخطأ: حمراء
            bubble.setStyleSheet("""
                QFrame {
                    background-color: #fee;
                    border: 1px solid #fcc;
                    border-radius: 12px;
                    padding: 12px 16px;
                }
            """)
            
            text_label = QLabel(text)
            text_label.setStyleSheet("color: #c00; font-size: 14px;")
            text_label.setWordWrap(True)
            bubble_layout.addWidget(text_label)
            
            msg_layout.addWidget(bubble)
            msg_layout.addStretch()
            bubble.setMaximumWidth(600)
        
        else:  # system
            # رسالة النظام: رمادية صغيرة
            msg_layout.addStretch()
            text_label = QLabel(text)
            text_label.setStyleSheet("color: #999; font-size: 12px; font-style: italic;")
            text_label.setWordWrap(True)
            bubble_layout.addWidget(text_label)
            msg_layout.addStretch()
        
        msg_frame.setLayout(msg_layout)
        
        # إضافة الرسالة قبل التمدد
        index = self.messages_layout.count() - 1
        if index >= 0:
            self.messages_layout.insertWidget(index, msg_frame)
        else:
            self.messages_layout.addWidget(msg_frame)
    
    def upload_file(self):
        """رفع ملف"""
        file_path, _ = QFileDialog.getOpenFileName(self, "اختر ملفًا")
        if file_path:
            self._add_message(f"📎 تم رفع الملف: {file_path}", "system")
    
    def new_chat(self):
        """محادثة جديدة"""
        # مسح الرسائل
        while self.messages_layout.count() > 1:
            widget = self.messages_layout.itemAt(0).widget()
            if widget:
                widget.deleteLater()
        
        # مسح السياق
        self.ai_engine.clear_context()
        
        # إضافة رسالة الترحيب
        self._add_welcome_message()
    
    def _handle_key_press(self, event):
        """معالجة الاختصارات"""
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.send_message()
        else:
            QTextEdit.keyPressEvent(self.input_field, event)
