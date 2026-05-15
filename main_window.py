import os
import uuid
import html
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStatusBar, QTabWidget, QVBoxLayout, QWidget

from core.ai_worker import MultiModelWorker
from core.memory import Memory
from core.tools import Tools
from ui.chat_area import ChatArea
from ui.code_editor_tab import CodeEditorTab
from ui.file_tools_tab import FileToolsTab
from ui.input_box import InputBox
from ui.model_providers_tab import ModelProvidersTab
from ui.sidebar import Sidebar
from ui.styles import Theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PeacockAI Studio")
        self.setMinimumSize(1100, 720)
        self.resize(1380, 860)
        self.setStyleSheet(Theme.get_stylesheet())

        self.memory = Memory()
        self.session_id = str(uuid.uuid4())[:8]
        self.thinking_bubble = None
        self.last_code = None
        self.worker = None

        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "peacock_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.new_chat_clicked.connect(self.new_chat)
        self.sidebar.session_selected.connect(self.switch_session)
        self.sidebar.session_delete_requested.connect(self.delete_session)
        self.sidebar.setVisible(False)

        content = QWidget()
        content.setStyleSheet(f"background-color: {Theme.BG_MAIN};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        content_layout.addWidget(self._build_top_bar())
        content_layout.addWidget(self._build_tabs(), 1)

        self.input_box = InputBox()
        self.input_box.message_sent.connect(self.send_message)
        self.input_box.file_selected.connect(self.handle_uploaded_file)
        self.input_box.action_selected.connect(self.handle_plus_action)
        content_layout.addWidget(self.input_box)

        main_layout.addWidget(content, 1)
        main_layout.addWidget(self.sidebar)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background: {Theme.BG_MAIN};
                color: {Theme.TEXT_SECONDARY};
                border-top: 1px solid {Theme.BORDER};
                padding: 3px 10px;
            }}
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("جاهز")

        self.chat_area.add_message(
            "PeacockAI Studio",
            (
                "<b>مرحباً بك في PeacockAI Studio.</b><br><br>"
                "اكتب طلبك وسأتعامل معه كنظام عمل متكامل: محادثة، كتابة كود، بناء مشروع، "
                "أو تجهيز ملف للتعديل داخل محرر الأكواد.<br><br>"
                "<b>النماذج:</b> Qwen و DeepSeek عبر Ollama<br>"
                "<b>الأدوات:</b> ذاكرة محادثات، حفظ مشاريع، محرر كود، تشغيل سريع"
            ),
            is_user=False,
        )
        self.memory.ensure_session(self.session_id, "محادثة جديدة")
        self.refresh_sessions()

    def _build_top_bar(self):
        top_bar = QFrame()
        top_bar.setFixedHeight(62)
        top_bar.setStyleSheet(f"""
            QFrame {{
                background: {Theme.BG_MAIN};
                border-bottom: 1px solid {Theme.BORDER};
            }}
        """)

        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 0, 24, 0)
        top_layout.setSpacing(12)

        title = QLabel("PeacockAI Studio")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; border: none;")
        top_layout.addWidget(title)

        self.status_label = QLabel("جاهز | Qwen + DeepSeek")
        self.status_label.setStyleSheet(f"""
            color: {Theme.TEXT_SECONDARY};
            background: {Theme.BG_CANVAS};
            border: 1px solid {Theme.BORDER};
            border-radius: 8px;
            padding: 6px 10px;
        """)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()

        projects_btn = QPushButton("المشاريع")
        projects_btn.setCursor(Qt.PointingHandCursor)
        projects_btn.setToolTip("فتح مجلد المشاريع المحفوظة")
        projects_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.BG_MAIN};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {Theme.PRIMARY_LIGHT};
                border-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_DARK};
            }}
        """)
        projects_btn.clicked.connect(lambda checked=False: Tools.open_folder())
        top_layout.addWidget(projects_btn)

        self.menu_btn = QPushButton("☰")
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.setToolTip("عرض المحادثات السابقة")
        self.menu_btn.setFixedSize(42, 38)
        self.menu_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.TEXT_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background: {Theme.PRIMARY};
            }}
        """)
        self.menu_btn.clicked.connect(self.toggle_conversations)
        top_layout.addWidget(self.menu_btn)
        return top_bar

    def _build_tabs(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {Theme.BG_CANVAS};
            }}
            QTabBar {{
                background: {Theme.BG_MAIN};
            }}
            QTabBar::tab {{
                padding: 12px 22px;
                font-size: 13px;
                font-weight: 600;
                color: {Theme.TEXT_SECONDARY};
                background: transparent;
                border: none;
                border-bottom: 3px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {Theme.TEXT_PRIMARY};
                border-bottom: 3px solid {Theme.PRIMARY};
            }}
            QTabBar::tab:hover {{
                color: {Theme.PRIMARY_DARK};
                background: {Theme.BG_HOVER};
            }}
        """)

        self.chat_area = ChatArea()
        self.tab_widget.addTab(self.chat_area, "المحادثة")

        self.code_editor_tab = CodeEditorTab()
        self.tab_widget.addTab(self.code_editor_tab, "محرر الأكواد")

        self.file_tools_tab = FileToolsTab()
        self.tab_widget.addTab(self.file_tools_tab, "الملفات")

        self.model_providers_tab = ModelProvidersTab()
        self.tab_widget.addTab(self.model_providers_tab, "النماذج")
        return self.tab_widget

    def send_message(self, text):
        if self.input_box.is_processing:
            return

        self.chat_area.add_message("أنت", text, is_user=True)
        self.memory.save_message(self.session_id, "user", text)
        self.sidebar.update_session_name(self.session_id, text[:34] or "محادثة")
        self.refresh_sessions()

        self.input_box.set_processing(True)
        self.status_label.setText("جاري التفكير...")
        self.status_bar.showMessage("جاري إرسال الطلب إلى النموذج المحلي")
        self.thinking_bubble = self.chat_area.add_thinking()

        build_keywords = [
            "ابني", "بناء", "برمج", "كود", "لعبة", "موقع", "تطبيق", "برنامج",
            "اكتب كود", "صمم", "أنشئ", "اعمل", "build", "code", "app", "website",
            "اصنع", "كودكس",
        ]
        is_build = any(word in text.lower() for word in build_keywords)

        history = self.memory.get_conversation_history(self.session_id, limit=30)
        self.worker = MultiModelWorker(text, is_build_request=is_build, history=history)
        self.worker.response_signal.connect(self.handle_response)
        self.worker.progress_signal.connect(self.update_status)
        self.worker.start()

    def update_status(self, message):
        self.status_bar.showMessage(message)

    def handle_response(self, response_type, content):
        if self.thinking_bubble:
            self.chat_area.remove_thinking(self.thinking_bubble)
            self.thinking_bubble = None

        if response_type == "code":
            self.last_code = content
            path = Tools.save_project(content, "project")
            self.chat_area.add_message(
                "PeacockAI Studio",
                (
                    "<b>تم بناء المشروع وحفظه.</b><br><br>"
                    f"<b>المسار:</b> <code>{path}</code><br><br>"
                    "تم تحميل الكود تلقائياً في محرر الأكواد حتى تراجعه أو تشغله."
                ),
                is_user=False,
            )
            self.code_editor_tab.set_code(content)
            self.memory.save_project(f"مشروع {datetime.now().strftime('%H:%M')}", {"path": path})
        elif response_type == "error":
            self.chat_area.add_message("خطأ", content, is_user=False)
        else:
            self.chat_area.add_message("PeacockAI Studio", content, is_user=False)

        self.memory.save_message(self.session_id, "assistant", content[:1000])
        self.refresh_sessions()
        self.input_box.set_processing(False)
        self.status_label.setText("جاهز | Qwen + DeepSeek")
        self.status_bar.showMessage("جاهز")

    def handle_uploaded_file(self, path):
        if path.lower().endswith(".zip"):
            result = Tools.extract(path)
            if result.get("success"):
                self.chat_area.add_message(
                    "PeacockAI Studio",
                    f"تم فك ضغط الملف: <code>{result.get('path')}</code>",
                    is_user=False,
                )
            else:
                self.chat_area.add_message("خطأ", result.get("error", "تعذر فك الضغط"), is_user=False)
            return

        result = Tools.read_file(path)
        if not result.get("success"):
            self.chat_area.add_message("خطأ", result.get("error", "تعذر قراءة الملف"), is_user=False)
            return

        content = result.get("content", "")
        name = os.path.basename(path)
        preview = html.escape(content[:1200] + ("..." if len(content) > 1200 else ""))
        self.chat_area.add_message(
            "PeacockAI Studio",
            f"تم رفع وقراءة الملف <b>{name}</b>.<br><br><code>{preview}</code>",
            is_user=False,
        )
        self.code_editor_tab.set_code(content)
        self.tab_widget.setCurrentWidget(self.code_editor_tab)

    def handle_plus_action(self, action_id):
        if action_id == "camera":
            try:
                os.startfile("microsoft.windows.camera:")
                self.chat_area.add_message(
                    "PeacockAI Studio",
                    "تم فتح تطبيق الكاميرا. بعد التقاط الصورة ارفعها من زر + ليقرأها التطبيق.",
                    is_user=False,
                )
            except Exception as exc:
                self.chat_area.add_message(
                    "PeacockAI Studio",
                    f"تعذر فتح الكاميرا تلقائياً: {exc}",
                    is_user=False,
                )
            return

        if action_id == "document":
            self.tab_widget.setCurrentWidget(self.file_tools_tab)
            self.status_bar.showMessage("اختر نوع الملف من تبويب الملفات")
            return

        hints = {
            "image": "اكتب وصف الصورة ثم اضغط إرسال. يمكن ضبط نموذج الصور من ملف data/model_providers.json أو API /media/providers.",
            "video": "اكتب وصف الفيديو ثم اضغط إرسال. أضف مزود فيديو محلي أو API قبل التوليد.",
            "search": "اكتب موضوع البحث وسيجلب التطبيق نتائج تفصيلية من الانترنت.",
            "deep_thinking": "وضع التفكير العميق يستخدم سياق المحادثة كاملة ويطلب تحليلاً أكثر عمقاً من النموذج.",
            "codex": "وضع كودكس يوجه الطلب لصناعة أو تعديل كود ومشاريع حقيقية قابلة للحفظ.",
        }
        if action_id in hints:
            self.status_bar.showMessage(hints[action_id])

    def open_in_editor(self):
        if self.last_code:
            self.code_editor_tab.set_code(self.last_code)
            self.tab_widget.setCurrentWidget(self.code_editor_tab)

    def new_chat(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.memory.ensure_session(self.session_id, "محادثة جديدة")
        self.chat_area.remove_all_messages()
        self.chat_area.add_message(
            "PeacockAI Studio",
            "محادثة جديدة جاهزة. اكتب طلبك وسأبدأ من هنا.",
            is_user=False,
        )
        self.sidebar.add_session(self.session_id, "محادثة جديدة")
        self.refresh_sessions()
        self.status_bar.showMessage(f"محادثة جديدة | {self.session_id}")

    def switch_session(self, session_id):
        self.session_id = session_id
        self.chat_area.remove_all_messages()
        history = self.memory.get_conversation_history(session_id)
        if history:
            for msg in history[-20:]:
                is_user = msg["role"] == "user"
                sender = "أنت" if is_user else "PeacockAI Studio"
                self.chat_area.add_message(sender, msg["content"], is_user=is_user)
        else:
            self.chat_area.add_message(
                "PeacockAI Studio",
                "لا توجد رسائل محفوظة لهذه المحادثة بعد.",
                is_user=False,
            )
        self.sidebar.setVisible(False)
        self.status_bar.showMessage(f"تم تحميل المحادثة | {session_id}")

    def toggle_conversations(self):
        self.refresh_sessions()
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def refresh_sessions(self):
        self.sidebar.set_sessions(self.memory.list_sessions())

    def delete_session(self, session_id):
        deleted = self.memory.delete_session(session_id)
        if not deleted:
            return
        self.sidebar.remove_session(session_id)
        if session_id == self.session_id:
            self.new_chat()
        else:
            self.refresh_sessions()
        self.status_bar.showMessage("تم حذف المحادثة")
