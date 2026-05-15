from PyQt5.QtCore import QThread, pyqtSignal

from core.intent import IntentClassifier
from core.media import MediaGenerationService
from core.universal_runtime import UniversalRuntime  # ← التغيير الأول: بدل Router
from core.search import WebSearchService


class MultiModelWorker(QThread):
    """Run the selected local model away from the UI thread."""

    response_signal = pyqtSignal(str, str)
    progress_signal = pyqtSignal(str)

    def __init__(self, prompt, is_build_request=False, history=None, parent=None):
        super().__init__(parent)
        self.prompt = prompt
        self.is_build_request = is_build_request
        self.history = history or []
        self.runtime = UniversalRuntime()  # ← التغيير الثاني: استخدم UniversalRuntime بدل Router

    def run(self):
        try:
            self.progress_signal.emit("اختيار النموذج المناسب...")
            model_prompt = self._with_history(self.prompt)
            intent = IntentClassifier.detect(self.prompt)

            # توليد صورة
            if intent.action == "image":
                self.progress_signal.emit("توليد صورة من الطلب...")
                result = MediaGenerationService.generate_image(self.prompt)
                self.response_signal.emit("media", self._format_tool_result(result, "الصورة"))
                return

            # توليد فيديو
            if intent.action == "video":
                self.progress_signal.emit("توليد فيديو من الطلب...")
                result = MediaGenerationService.generate_video(self.prompt)
                self.response_signal.emit("media", self._format_tool_result(result, "الفيديو"))
                return

            # بحث في الإنترنت
            if intent.action == "search":
                self.progress_signal.emit("إجراء بحث تفصيلي على الانترنت...")
                search = WebSearchService.detailed_search(self.prompt)
                if not search.get("success"):
                    self.response_signal.emit("error", search.get("error", "فشل البحث على الانترنت"))
                    return

                # استخدم UniversalRuntime لتلخيص نتائج البحث
                answer_prompt = (
                    "أجب بالعربية اعتماداً على نتائج البحث التالية، واذكر أهم الروابط في نهاية الرد:\n\n"
                    f"{search.get('summary', '')}\n\n"
                    f"سؤال المستخدم: {model_prompt}"
                )
                result = self.runtime.generate(answer_prompt)  # ← استخدم UniversalRuntime
                response = result.get("response", "")
                self.response_signal.emit("text", self._clean_response(response))
                return

            # ← التغيير الثالث والأهم: استخدم UniversalRuntime بدل Router
            self.progress_signal.emit("إرسال الطلب إلى النموذج المحلي...")
            result = self.runtime.generate(model_prompt)
            response = result.get("response", "")
            code = result.get("code", "")
            validation = result.get("validation", {})
            reflection = result.get("reflection", "")

            # نظف الرد من علامات Markdown
            response = self._clean_response(response)

            # حدد نوع الرد (كود ولا نص عادي)
            response_type = "code" if (self.is_build_request or code) and self._looks_like_code(response) else "text"
            
            # لو فيه reflection، ضيفه في الرد
            if reflection:
                response = f"{response}\n\n🪞 **ملاحظات التحسين:**\n{reflection}"
            
            self.response_signal.emit(response_type, response)
            
        except Exception as exc:
            self.response_signal.emit("error", self._friendly_error(exc))

    @staticmethod
    def _clean_response(text):
        text = (text or "").strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text

    @staticmethod
    def _looks_like_code(text):
        markers = (
            "def ",
            "class ",
            "import ",
            "from ",
            "<html",
            "<!doctype",
            "function ",
            "const ",
            "let ",
            "package ",
            "if __name__",
            "pygame",
            "tkinter",
        )
        lowered = text.lower()
        return any(marker in lowered for marker in markers)

    @staticmethod
    def _friendly_error(exc):
        message = str(exc)
        if "ollama" in message.lower():
            return "تعذر الاتصال بـ Ollama. شغل Ollama وتأكد أن النماذج المحلية مثبتة ثم حاول مرة أخرى."
        return f"حدث خطأ أثناء تشغيل النموذج: {message}"

    def _with_history(self, prompt):
        if not self.history:
            return prompt
        turns = []
        for message in self.history[-30:]:
            role = "المستخدم" if message.get("role") == "user" else "المساعد"
            content = (message.get("content") or "").strip()
            if content:
                turns.append(f"{role}: {content}")
        if not turns:
            return prompt
        return (
            "استخدم سياق المحادثة السابق بدقة ولا تنساه:\n"
            + "\n".join(turns)
            + "\n\nالطلب الحالي:\n"
            + prompt
        )

    @staticmethod
    def _format_tool_result(result, label):
        if result.get("success"):
            return (
                f"تم توليد {label} بنجاح.<br><br>"
                f"<b>المسار:</b> <code>{result.get('path')}</code><br>"
                f"<b>النموذج:</b> {result.get('provider', 'default')}"
            )
        return (
            f"لم أستطع توليد {label} الآن.<br><br>"
            f"{result.get('error', 'تحقق من إعدادات النموذج أو API endpoint.')}"
        )