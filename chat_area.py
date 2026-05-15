from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from ui.message_bubble import MessageBubble
from ui.styles import Theme


class ChatArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {Theme.BG_CANVAS};
            }}
        """)

        self.container = QWidget()
        self.container.setStyleSheet(f"background-color: {Theme.BG_CANVAS};")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 22, 0, 22)
        self.layout.setSpacing(4)
        self.layout.addStretch()

        self.setWidget(self.container)

    def add_message(self, sender, text, is_user=False):
        bubble = MessageBubble(sender, text, is_user)
        self.layout.insertWidget(self.layout.count() - 1, bubble)
        QTimer.singleShot(80, self.scroll_to_bottom)
        return bubble

    def add_thinking(self):
        bubble = MessageBubble("PeacockAI", "جاري التفكير...", is_user=False)
        self.layout.insertWidget(self.layout.count() - 1, bubble)
        QTimer.singleShot(80, self.scroll_to_bottom)
        return bubble

    def remove_thinking(self, bubble):
        self.layout.removeWidget(bubble)
        bubble.deleteLater()

    def remove_all_messages(self):
        while self.layout.count() > 1:
            item = self.layout.itemAt(0)
            widget = item.widget() if item else None
            if widget:
                self.layout.removeWidget(widget)
                widget.deleteLater()
            else:
                break

    def scroll_to_bottom(self):
        vbar = self.verticalScrollBar()
        vbar.setValue(vbar.maximum())
