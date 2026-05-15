# PeacockAI Studio

واجهة ذكاء اصطناعي محلية بأسلوب ChatGPT مع محرر أكواد ومساحة مشاريع.

## قدرات الملفات

- إنشاء ملفات `README.md`.
- إنشاء ملفات Word بصيغة `.docx`.
- إنشاء عروض PowerPoint بصيغة `.pptx`.
- إنشاء ملفات PDF بصيغة `.pdf`.
- رفع ملفات نصية و`docx` و`pptx` و`pdf` وقراءتها داخل البرنامج.
- تعديل الملفات النصية وحفظها.
- ضغط ملفات ومجلدات إلى ZIP.
- فك ضغط ملفات ZIP وأرشيفات Python المدعومة.

## قدرات النماذج والوسائط

- فهم نية المستخدم تلقائياً: محادثة، بحث، توليد صورة، توليد فيديو، إنشاء ملفات، أو صناعة تطبيق.
- إضافة نماذج صور وفيديو مفتوحة المصدر عبر تبويب `النماذج`.
- دعم Stable Diffusion WebUI محلياً من خلال `http://127.0.0.1:7860/sdapi/v1/txt2img`.
- دعم أي API خارجي يرجع رابط ملف أو Base64 عبر endpoints `/media/providers`.
- زر `+` في واجهة الشات يفتح: رفع ملف، فتح كاميرا، توليد صورة، توليد فيديو، بحث تفصيلي، إنشاء ملف، وصناعة تطبيق.
- البحث التفصيلي يعمل عبر Brave أو SerpAPI عند ضبط مفاتيح API، أو DuckDuckGo HTML كبديل.

متغيرات البحث الاختيارية:

```powershell
$env:PEACOCK_SEARCH_PROVIDER="brave"
$env:BRAVE_SEARCH_API_KEY="..."
```

## تشغيل واجهة سطح المكتب

```powershell
python -m pip install -r requirements.txt
python main.py
```

## تشغيل الباكند

```powershell
python -m pip install -r requirements.txt
uvicorn backend.app:app --reload
```

## تشغيل واجهة الويب

```powershell
cd frontend
npm install
npm run dev
```

واجهة الويب تتصل افتراضياً بـ `http://127.0.0.1:8000`. يمكن تغيير المسار عبر `VITE_API_URL`.
