import datetime

from PyQt5.QtCore import QEvent, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QLabel, QListWidget, QListWidgetItem, QMenu, QPushButton, QVBoxLayout

from ui.styles import Theme


class Sidebar(QFrame):
    new_chat_clicked = pyqtSignal()
    session_selected = pyqtSignal(str)
    session_delete_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(Theme.SIDEBAR_WIDTH)
        self.setObjectName("sidebar")
        self.setStyleSheet(f"""
            QFrame#sidebar {{
                background-color: {Theme.BG_SIDEBAR};
                border-left: 1px solid {Theme.BORDER_DARK};
            }}
        """)
        self.sessions = {}
        self._pressed_item = None
        self._long_press_timer = QTimer(self)
        self._long_press_timer.setSingleShot(True)
        self._long_press_timer.timeout.connect(self._show_delete_for_pressed_item)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(12)

        brand = QLabel("المحادثات")
        brand.setFont(QFont("Segoe UI", 15, QFont.Bold))
        brand.setStyleSheet(f"color: {Theme.TEXT_ON_DARK};")
        layout.addWidget(brand)

        subtitle = QLabel("كل المحادثات محفوظة في الذاكرة")
        subtitle.setStyleSheet(f"color: {Theme.TEXT_MUTED_ON_DARK}; font-size: 12px;")
        layout.addWidget(subtitle)

        new_btn = QPushButton("+  محادثة جديدة")
        new_btn.setFixedHeight(44)
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                text-align: right;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY_DARK};
            }}
        """)
        new_btn.clicked.connect(self.new_chat_clicked.emit)
        layout.addWidget(new_btn)

        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu_at)
        self.list_widget.itemClicked.connect(self.on_session_clicked)
        self.list_widget.itemPressed.connect(self._start_long_press)
        self.list_widget.viewport().installEventFilter(self)
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                color: {Theme.TEXT_MUTED_ON_DARK};
                padding: 12px 12px;
                border-radius: 8px;
                margin: 2px 0;
            }}
            QListWidget::item:hover {{
                background-color: {Theme.BG_SIDEBAR_HOVER};
                color: {Theme.TEXT_ON_DARK};
            }}
            QListWidget::item:selected {{
                background-color: {Theme.BG_SIDEBAR_HOVER};
                color: {Theme.TEXT_ON_DARK};
                border-right: 3px solid {Theme.PRIMARY};
            }}
        """)
        layout.addWidget(self.list_widget, 1)

        hint = QLabel("اضغط مطولاً أو كليك يمين لحذف محادثة")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"color: {Theme.TEXT_LIGHT}; font-size: 11px; padding: 8px;")
        layout.addWidget(hint)

    def eventFilter(self, obj, event):
        if obj == self.list_widget.viewport() and event.type() in (QEvent.MouseButtonRelease, QEvent.Leave):
            self._long_press_timer.stop()
        return super().eventFilter(obj, event)

    def on_session_clicked(self, item):
        self._long_press_timer.stop()
        session_id = item.data(Qt.UserRole)
        if session_id:
            self.session_selected.emit(session_id)

    def set_sessions(self, sessions):
        self.sessions = {}
        self.list_widget.clear()
        for session in sessions:
            session_id = session.get("id")
            if not session_id:
                continue
            title = session.get("title") or "محادثة"
            preview = session.get("preview") or ""
            count = session.get("message_count", 0)
            label = title if not preview else f"{title}\n{preview[:58]}"
            if count:
                label = f"{label}\n{count} رسالة"
            self._insert_session(session_id, label, title, append=True)

    def add_session(self, session_id, name=None):
        if name is None:
            name = f"محادثة {datetime.datetime.now().strftime('%I:%M %p')}"
        self.remove_session(session_id)
        self._insert_session(session_id, name, name, append=False)
        self.list_widget.setCurrentRow(0)

    def update_session_name(self, session_id, new_name):
        if session_id in self.sessions:
            self.sessions[session_id] = new_name
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)
                if item.data(Qt.UserRole) == session_id:
                    item.setText(new_name)
                    break

    def remove_session(self, session_id):
        self.sessions.pop(session_id, None)
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.data(Qt.UserRole) == session_id:
                self.list_widget.takeItem(index)
                break

    def _insert_session(self, session_id, label, title, append):
        self.sessions[session_id] = title
        item = QListWidgetItem(label)
        item.setData(Qt.UserRole, session_id)
        item.setToolTip("اضغط لفتح المحادثة، اضغط مطولاً للحذف")
        if append:
            self.list_widget.addItem(item)
        else:
            self.list_widget.insertItem(0, item)

    def _start_long_press(self, item):
        self._pressed_item = item
        self._long_press_timer.start(700)

    def _show_delete_for_pressed_item(self):
        if self._pressed_item:
            self._show_delete_menu(self._pressed_item, self.list_widget.visualItemRect(self._pressed_item).center())

    def _show_context_menu_at(self, pos):
        item = self.list_widget.itemAt(pos)
        if item:
            self._show_delete_menu(item, pos)

    def _show_delete_menu(self, item, pos):
        session_id = item.data(Qt.UserRole)
        if not session_id:
            return
        menu = QMenu(self)
        delete_action = menu.addAction("حذف المحادثة")
        selected = menu.exec_(self.list_widget.viewport().mapToGlobal(pos))
        if selected == delete_action:
            self.session_delete_requested.emit(session_id)
