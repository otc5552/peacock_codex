from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QComboBox, QFrame, QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from core.media import ModelProviderRegistry
from ui.styles import Theme


class ModelProvidersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self.setStyleSheet(f"background-color: {Theme.BG_CANVAS};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("إضافة نماذج الصور والفيديو")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        layout.addWidget(title)

        form = QFrame()
        form.setStyleSheet(f"""
            QFrame {{
                background: {Theme.BG_MAIN};
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
            }}
        """)
        grid = QGridLayout(form)
        grid.setContentsMargins(14, 14, 14, 14)
        grid.setSpacing(10)

        self.media_type = QComboBox()
        self.media_type.addItems(["image", "video"])
        self.provider_id = QLineEdit()
        self.provider_id.setPlaceholderText("provider_id مثال: local_comfyui")
        self.name = QLineEdit()
        self.name.setPlaceholderText("اسم النموذج")
        self.endpoint = QLineEdit()
        self.endpoint.setPlaceholderText("API endpoint")
        self.auth_env = QLineEdit()
        self.auth_env.setPlaceholderText("اسم متغير البيئة لمفتاح API اختياري")
        self.response_format = QComboBox()
        self.response_format.addItems(["automatic1111", "url_or_base64"])

        fields = [
            ("النوع", self.media_type),
            ("المعرف", self.provider_id),
            ("الاسم", self.name),
            ("الرابط", self.endpoint),
            ("API Env", self.auth_env),
            ("صيغة الرد", self.response_format),
        ]
        for row, (label, widget) in enumerate(fields):
            grid.addWidget(QLabel(label), row, 0)
            grid.addWidget(widget, row, 1)
            widget.setStyleSheet(self._field_style())

        save_btn = QPushButton("حفظ النموذج")
        save_btn.clicked.connect(self.save_provider)
        save_btn.setStyleSheet(self._button_style())
        grid.addWidget(save_btn, len(fields), 1)
        layout.addWidget(form)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet(f"""
            QTextEdit {{
                background: {Theme.BG_CODE};
                color: #E2E8F0;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-family: Consolas;
            }}
        """)
        layout.addWidget(self.output, 1)

    def save_provider(self):
        provider_id = self.provider_id.text().strip()
        endpoint = self.endpoint.text().strip()
        if not provider_id or not endpoint:
            self.output.append("اكتب معرف النموذج والرابط أولاً.")
            return

        headers = {}
        if self.auth_env.text().strip():
            headers["Authorization"] = f"Bearer env:{self.auth_env.text().strip()}"

        media_type = self.media_type.currentText()
        template = {"prompt": "{{prompt}}"}
        if media_type == "image":
            template.update({"width": "{{width}}", "height": "{{height}}", "steps": "{{steps}}"})
        else:
            template.update({"seconds": "{{seconds}}"})

        result = ModelProviderRegistry.add_provider(
            media_type,
            provider_id,
            {
                "name": self.name.text().strip() or provider_id,
                "endpoint": endpoint,
                "method": "POST",
                "headers": headers,
                "payload_template": template,
                "response_format": self.response_format.currentText(),
            },
        )
        self.output.append(result.get("message", "تم الحفظ"))
        self.refresh()

    def refresh(self):
        self.output.clear()
        providers = ModelProviderRegistry.list_providers()
        for media_type, group in providers.items():
            self.output.append(f"[{media_type}] default={group.get('default')}")
            for provider_id, provider in group.get("providers", {}).items():
                self.output.append(f"  - {provider_id}: {provider.get('name')} -> {provider.get('endpoint')}")

    def _field_style(self):
        return f"""
            QLineEdit, QComboBox {{
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
                padding: 8px 10px;
                background: {Theme.BG_MAIN};
                color: {Theme.TEXT_PRIMARY};
            }}
        """

    def _button_style(self):
        return f"""
            QPushButton {{
                background: {Theme.PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {Theme.PRIMARY_DARK};
            }}
        """
