import html

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ui.styles import Theme


class MessageBubble(QFrame):
    def __init__(self, sender, message, is_user=False, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background: transparent; border: none; }")

        row = QHBoxLayout(self)
        row.setContentsMargins(22, 4, 22, 4)
        row.setSpacing(12)

        bubble = QFrame()
        bubble.setObjectName("bubble")
        bubble.setMaximumWidth(780 if is_user else 860)
        bubble.setStyleSheet(self._bubble_style(is_user))

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(16, 12, 16, 14)
        bubble_layout.setSpacing(8)

        sender_label = QLabel(sender)
        sender_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        sender_label.setStyleSheet(
            f"color: {'#FFFFFF' if is_user else Theme.PRIMARY}; background: transparent;"
        )
        bubble_layout.addWidget(sender_label)

        content = QLabel()
        content.setWordWrap(True)
        content.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        content.setStyleSheet(f"""
            QLabel {{
                color: {'#FFFFFF' if is_user else Theme.TEXT_PRIMARY};
                background: transparent;
                border: none;
                font-size: 14px;
                line-height: 1.65;
            }}
        """)
        content.setTextFormat(Qt.RichText)
        content.setOpenExternalLinks(True)
        content.setText(self._format_message(message, is_user))
        bubble_layout.addWidget(content)

        if is_user:
            row.addStretch(1)
            row.addWidget(bubble)
        else:
            row.addWidget(bubble)
            row.addStretch(1)

    def _bubble_style(self, is_user):
        if is_user:
            return f"""
                QFrame#bubble {{
                    background-color: {Theme.PRIMARY};
                    border: 1px solid {Theme.PRIMARY_DARK};
                    border-radius: 8px;
                }}
            """
        return f"""
            QFrame#bubble {{
                background-color: {Theme.BG_AI_MSG};
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
            }}
        """

    @staticmethod
    def _format_message(message, is_user):
        text = message or ""
        has_html = any(token in text.lower() for token in ("<br", "<b", "<code", "<p", "<ul", "<ol"))
        if is_user or not has_html:
            text = html.escape(text).replace("\n", "<br>")
        return f"<div dir='auto'>{text}</div>"
