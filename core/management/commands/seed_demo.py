"""VUCA-konseptida axloq — to'liq demo ma'lumot (har model >= 20)."""

from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

from core.models import (
    Answer,
    Certificate,
    Course,
    CourseImage,
    CourseSyllabus,
    ExternalActivity,
    Infographic,
    Module,
    Question,
    SiteDocument,
    Test,
    UserCourseProgress,
    UserTestResult,
)

User = get_user_model()

PALETTE = [
    (88, 204, 2),
    (28, 176, 246),
    (70, 23, 143),
    (255, 75, 75),
    (255, 200, 0),
    (255, 150, 0),
    (206, 130, 255),
    (255, 75, 140),
    (0, 180, 166),
    (80, 90, 220),
]

YOUTUBE = [
    "https://www.youtube.com/watch?v=l5-2pa66fIU",
    "https://www.youtube.com/watch?v=iG9CE55wbtY",
    "https://www.youtube.com/watch?v=G7sQ8C5VZOs",
    "https://www.youtube.com/watch?v=unfzfe8f9MI",
    "https://www.youtube.com/watch?v=5MgBikgcWnY",
    "https://www.youtube.com/watch?v=8jPQjjsBbIc",
    "https://www.youtube.com/watch?v=R9OCA6UFE-0",
    "https://www.youtube.com/watch?v=3qbk-R1SWys",
    "https://www.youtube.com/watch?v=u7NfiK5oH-E",
    "https://www.youtube.com/watch?v=q-YdQwfSUlE",
]

LA_URLS = [
    "https://learningapps.org/watch?v=p8n3k4d5c",
    "https://learningapps.org/watch?v=eqp6gkzka20",
    "https://learningapps.org/watch?v=p1234567a",
    "https://learningapps.org/display?id=1234567",
    "https://learningapps.org/watch?v=axloq9sinf",
]
KAHOOT_URLS = [
    "https://kahoot.it/",
    "https://create.kahoot.it/share/ethics/1",
    "https://kahoot.com/schools/",
]

MODULES = [
    ("VUCA nima?", "Zamonaviy dunyoning 4 o‘lchami: o‘zgaruvchanlik, noaniqlik, murakkablik, ikkiyoqlamalilik."),
    ("Axloq asoslari", "Yaxshi–yomon, burch va vijdon. 9–11-sinf o‘quvchisi uchun amaliy kirish."),
    ("Huquqiy asoslar", "Konstitutsiya, ta’lim to‘g‘risidagi qonun va o‘quvchining huquqlari."),
    ("O‘zgaruvchanlik (V)", "Tez o‘zgaradigan vaziyatlarda axloqiy barqarorlik."),
    ("Noaniqlik (U)", "Ma’lumot yetarli bo‘lmaganda qanday halol qaror qabul qilinadi."),
    ("Murakkablik (C)", "Ko‘p tomonlama muammolarda mas’uliyatni bo‘lish."),
    ("Ikkiyoqlamalilik (A)", "Bir voqea turli ma’noda o‘qilganda haqiqatni izlash."),
    ("Halollik", "Yolg‘on, intizom va o‘z so‘zida turish."),
    ("Adolat", "Teng munosabat, kamsitmaslik, sinfdagi adolat."),
    ("Hurmat", "O‘qituvchi, ota-ona, tengdosh va o‘ziga hurmat."),
    ("Mas’uliyat", "Qilmishning oqibati. Shaxsiy va jamoaviy javobgarlik."),
    ("Empatiya", "Boshqaning his-tuyg‘usini tushunish va yordam."),
    ("Raqamli axloq", "Internet, AI, deepfake va raqamli iz."),
    ("Ijtimoiy tarmoqlar", "Kiberbulling, like ovlash, maxfiylik."),
    ("Jamoada ishlash", "Hamkorlik, nizo va konstruktiv tanqid."),
    ("Liderlik va axloq", "Ta’sir o‘tkazishda halollik. Lider = namuna."),
    ("Ekologik axloq", "Tabiatga munosabat, iste’mol va kelajak avlod."),
    ("Fuqarolik pozitsiyasi", "Maktab, mahalla, vatan. Faol fuqaro."),
    ("Stress va tanlov", "Bosim ostida axloqiy qaror. VUCA stressi."),
    ("Yakuniy integratsiya", "20 modulni hayotga tatbiq: mini-loyiha va qadriyatlar xaritasi."),
]

INFOGRAPHICS = [
    ("VUCA 10 soniyada", "4 harf — 4 hayotiy vaziyat."),
    ("Halollik kompassi", "Qaror oldida 3 savol bering."),
    ("Raqamli iz", "Internetda yozganingiz qoladi."),
    ("Kiberhurmat", "Ekran orqasida ham odam bor."),
    ("Empatiya mushagi", "Avval tingla, keyin gapir."),
    ("Adolat tarozisi", "O‘zingizga yoqmaganini boshqaga qilmang."),
    ("Jamoa qoidalari", "5 ta oddiy sinf qoidasi."),
    ("Stress pauzasi", "10 nafas — keyin qaror."),
    ("Lider namuna", "So‘z emas, ish o‘rgatadi."),
    ("Yashil qadam", "Bugun 1 ta ekologik ish."),
    ("Huquq va burch", "Huquq borsh bilan juft."),
    ("Noaniqlikda tinchlik", "Bilmaslik — ham ma’lumot."),
    ("Murakkab muammo", "Katta savolni kichik qismlarga bo‘ling."),
    ("Ikki tomon", "Bir voqeani 2 nuqtai nazardan yozing."),
    ("Like tuzog‘i", "Obro‘ ≠ qadriyat."),
    ("Do‘stlik shartnomasi", "Sinfdoshga 3 va’da."),
    ("Vaqt va axloq", "Shoshilinchlik yolg‘onga olib keladi."),
    ("Oila va maktab", "Ikki makonda bir xil qadriyat."),
    ("Kelajak meni", "10 yildan keyin o‘zingizga xat."),
    ("VUCA qahramoni", "O‘zgarishda ham odam bo‘lib qol."),
]

DOCUMENTS = [
    ("program", "Kurs dasturi 2026"),
    ("program", "9-sinf dasturi"),
    ("program", "10-sinf dasturi"),
    ("program", "11-sinf dasturi"),
    ("program", "Kalendar-tematik reja"),
    ("plan", "Yillik ish reja"),
    ("plan", "I chorak ish reja"),
    ("plan", "II chorak ish reja"),
    ("plan", "III chorak ish reja"),
    ("plan", "IV chorak ish reja"),
    ("plan", "Amaliy mashg‘ulotlar rejasi"),
    ("plan", "Tarbiyaviy soatlar rejasi"),
    ("legal", "Konstitutsiyadan ko‘chirma"),
    ("legal", "Ta’lim to‘g‘risidagi qonun"),
    ("legal", "Bola huquqlari konvensiyasi"),
    ("legal", "O‘quvchi odob-axloq qoidalari"),
    ("legal", "Kiberxavfsizlik bo‘yicha yo‘riqnoma"),
    ("other", "Ota-onalar uchun memo"),
    ("other", "O‘qituvchi metodik tavsiya"),
    ("other", "Baholash mezonlari"),
]


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [text]


def make_poster(title: str, subtitle: str, index: int, size=(1280, 720)) -> bytes:
    color = PALETTE[index % len(PALETTE)]
    img = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(img)
    w, h = size
    draw.ellipse((-120, -120, 280, 280), fill=(255, 255, 255, ))
    draw.ellipse((w - 260, h - 260, w + 80, h + 80), fill=tuple(min(255, c + 30) for c in color))
    draw.rounded_rectangle((40, 40, w - 40, h - 40), radius=48, outline=(255, 255, 255), width=8)
    title_font = _font(54)
    sub_font = _font(28)
    badge_font = _font(22)
    y = 160
    for line in _wrap(draw, title, title_font, w - 160):
        draw.text((80, y), line, font=title_font, fill=(255, 255, 255))
        y += 64
    y += 12
    for line in _wrap(draw, subtitle, sub_font, w - 180):
        draw.text((80, y), line, font=sub_font, fill=(255, 255, 255))
        y += 36
    draw.rounded_rectangle((80, h - 110, 360, h - 58), radius=20, fill=(255, 255, 255))
    draw.text((100, h - 100), "VUCA · axloq", font=badge_font, fill=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_thumb(title: str, index: int) -> bytes:
    return make_poster(title, "9–11-sinf darsi", index, size=(960, 540))


def make_pdf(title: str, body: str) -> bytes:
    def esc(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    lines = [title, ""] + body.split("\n")
    content = ["BT /F1 16 Tf 50 750 Td"]
    for i, line in enumerate(lines[:40]):
        if i:
            content.append("0 -22 Td")
        content.append(f"({esc(line[:90])}) Tj")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1", "replace")
    objects = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n",
        b"4 0 obj<< /Length " + str(len(stream)).encode() + b" >>stream\n" + stream + b"\nendstream endobj\n",
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
    ]
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(out.tell())
        out.write(obj)
    xref = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.write(f"{off:010d} 00000 n \n".encode())
    out.write(f"trailer<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return out.getvalue()


def make_docx(title: str, body: str) -> bytes:
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>{title}</w:t></w:r></w:p>
    <w:p><w:r><w:t>{body}</w:t></w:r></w:p>
  </w:body>
</w:document>"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")
        zf.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")
        zf.writestr("word/document.xml", document_xml)
    return buf.getvalue()


class Command(BaseCommand):
    help = "Barcha modellarni kamida 20 tadan demo ma'lumot bilan to'ldiradi."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Eski demo o'chirilmoqda...")
        Certificate.objects.all().delete()
        UserTestResult.objects.all().delete()
        UserCourseProgress.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        Test.objects.all().delete()
        CourseSyllabus.objects.all().delete()
        CourseImage.objects.all().delete()
        ExternalActivity.objects.all().delete()
        Course.objects.all().delete()
        Module.objects.all().delete()
        Infographic.objects.all().delete()
        SiteDocument.objects.all().delete()
        User.objects.filter(username__startswith="demo_").delete()

        self.stdout.write("Foydalanuvchilar...")
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True, "email": "admin@vuca.uz"},
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("AdminDemo123")
        admin.save()

        students = []
        for i in range(1, 21):
            user, _ = User.objects.get_or_create(
                username=f"demo_oquvchi_{i:02d}",
                defaults={"first_name": f"O‘quvchi", "last_name": f"{i}"},
            )
            user.set_password("Demo12345")
            user.first_name = "O‘quvchi"
            user.last_name = str(i)
            user.save()
            students.append(user)
        hero = students[0]
        hero.first_name = "Sardor"
        hero.last_name = "Karimov"
        hero.save()

        self.stdout.write("Infografikalar (20)...")
        for i, (title, caption) in enumerate(INFOGRAPHICS):
            obj = Infographic(
                title=title,
                caption=caption,
                order=i,
                is_active=True,
            )
            obj.image.save(f"info_{i + 1:02d}.png", ContentFile(make_poster(title, caption, i)), save=False)
            obj.save()

        self.stdout.write("Sayt hujjatlari (20)...")
        for i, (kind, title) in enumerate(DOCUMENTS):
            body = f"{title}. VUCA-konseptida axloq kursi, 9-11-sinf. Demo hujjat #{i + 1}."
            obj = SiteDocument(title=title, document_type=kind, order=i, is_active=True)
            if i % 2 == 0:
                obj.file.save(f"doc_{i + 1:02d}.docx", ContentFile(make_docx(title, body)), save=False)
            else:
                obj.file.save(f"doc_{i + 1:02d}.pdf", ContentFile(make_pdf(title, body)), save=False)
            obj.save()

        self.stdout.write("Modullar, darslar, testlar...")
        modules = []
        courses = []
        for i, (title, desc) in enumerate(MODULES):
            module = Module.objects.create(title=title, description=desc, order=i)
            modules.append(module)
            for j in range(2):
                course = Course.objects.create(
                    module=module,
                    title=f"{title}: {j + 1}-dars",
                    content=(
                        f"{desc}\n\n"
                        f"Bu darsda o‘quvchi hayotiy misollar orqali mavzuni mustahkamlaydi. "
                        f"Video, Word ma’ruza, LearningApps/Kahoot amaliyoti va yakuniy refleksiyani bajaring."
                    ),
                    video_url=YOUTUBE[(i * 2 + j) % len(YOUTUBE)],
                    order=j,
                )
                courses.append(course)

        self.stdout.write("Ma'ruza fayllari, rasmlar, mashg'ulotlar...")
        for i, course in enumerate(courses):
            if i < 24:
                syl = CourseSyllabus(course=course, title=f"Ma’ruza {i + 1}")
                body = f"{course.title}. Demo ma’ruza matni. VUCA va axloq."
                if i % 2 == 0:
                    syl.file.save(f"lecture_{i + 1:02d}.docx", ContentFile(make_docx(course.title, body)), save=False)
                else:
                    syl.file.save(f"lecture_{i + 1:02d}.pdf", ContentFile(make_pdf(course.title, body)), save=False)
                syl.save()

                img = CourseImage(course=course, caption=f"{course.title} infografikasi")
                img.image.save(f"course_{i + 1:02d}.png", ContentFile(make_thumb(course.title, i)), save=False)
                img.save()

                kind = ExternalActivity.LEARNINGAPPS if i % 2 == 0 else ExternalActivity.KAHOOT
                url = LA_URLS[i % len(LA_URLS)] if kind == ExternalActivity.LEARNINGAPPS else KAHOOT_URLS[i % len(KAHOOT_URLS)]
                ExternalActivity.objects.create(
                    course=course,
                    title=("LearningApps: " if kind == ExternalActivity.LEARNINGAPPS else "Kahoot: ") + course.module.title,
                    activity_type=kind,
                    url=url,
                    order=0,
                )

        self.stdout.write("Testlar, savollar, javoblar...")
        tests = []
        questions = []
        for i, module in enumerate(modules):
            test = Test.objects.create(
                module=module,
                title=f"{module.title} — yakuniy test",
                description="4 ta savol. 70% dan o‘ting — sertifikat!",
                passing_score_percent=70,
            )
            tests.append(test)
            for qn in range(2):
                question = Question.objects.create(
                    test=test,
                    text=f"{module.title}: {qn + 1}-savol. Axloqiy qaror qaysi?",
                    order=qn,
                )
                questions.append(question)
                Answer.objects.create(question=question, text="O‘zini o‘ylash, oqibatni unutish", is_correct=False)
                Answer.objects.create(question=question, text="Haqiqat, hurmat va mas’uliyat asosida tanlash", is_correct=True)
                Answer.objects.create(question=question, text="Faqat ovoz ko‘p bo‘lgan tomon", is_correct=False)
                Answer.objects.create(question=question, text="Muammoni e’tiborsiz qoldirish", is_correct=False)

        self.stdout.write("Progress, natijalar, sertifikatlar...")
        for course in courses:
            UserCourseProgress.objects.get_or_create(user=hero, course=course)
        for student in students[1:5]:
            for course in courses[:8]:
                UserCourseProgress.objects.get_or_create(user=student, course=course)

        for test in tests:
            UserTestResult.objects.create(user=hero, test=test, score=85, passed=True)
        for student in students[1:6]:
            UserTestResult.objects.create(user=student, test=tests[0], score=60, passed=False)

        counts = {
            "Module": Module.objects.count(),
            "Course": Course.objects.count(),
            "CourseSyllabus": CourseSyllabus.objects.count(),
            "CourseImage": CourseImage.objects.count(),
            "ExternalActivity": ExternalActivity.objects.count(),
            "Infographic": Infographic.objects.count(),
            "SiteDocument": SiteDocument.objects.count(),
            "Test": Test.objects.count(),
            "Question": Question.objects.count(),
            "Answer": Answer.objects.count(),
            "UserCourseProgress": UserCourseProgress.objects.count(),
            "UserTestResult": UserTestResult.objects.count(),
            "Certificate": Certificate.objects.count(),
            "DemoUsers": User.objects.filter(username__startswith="demo_").count(),
        }
        self.stdout.write(self.style.SUCCESS("Demo tayyor:"))
        for name, n in counts.items():
            mark = "OK" if n >= 20 else "KAM"
            self.stdout.write(f"  {name}: {n} [{mark}]")
        self.stdout.write("Kirish: demo_oquvchi_01 / Demo12345  |  admin / AdminDemo123")
