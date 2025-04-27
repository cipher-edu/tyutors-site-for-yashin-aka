
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
<<<<<<< HEAD
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')),
                ('title', models.CharField(max_length=255, verbose_name='Kurs sarlavhasi')),
                ('content', models.TextField(blank=True, help_text='Kursning asosiy matnli mazmuni.', verbose_name='Kontent (mavzu)')),
                ('video_url', models.URLField(blank=True, help_text="Agar mavjud bo'lsa, YouTube video havolasi.", null=True, verbose_name='Video havolasi (YouTube)')),
                ('order', models.PositiveIntegerField(default=0, help_text="Modul ichidagi kurslarni ko'rsatish tartibi.", verbose_name='Tartib raqami')),
            ],
            options={
                'verbose_name': 'Kurs',
                'verbose_name_plural': 'Kurslar',
                'ordering': ['module__order', 'order', 'title'],
            },
        ),
        migrations.CreateModel(
=======
>>>>>>> aeb74ee0da082676582a69441da7656c46579614
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')),
                ('title', models.CharField(max_length=200, unique=True, verbose_name='Modul sarlavhasi')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Modul tavsifi')),
                ('order', models.PositiveIntegerField(default=0, help_text="Modullarni ko'rsatish tartibi.", verbose_name='Tartib raqami')),
            ],
            options={
                'verbose_name': 'Modul',
                'verbose_name_plural': 'Modullar',
                'ordering': ['order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')),
                ('text', models.TextField(verbose_name='Savol matni')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Tartib raqami')),
            ],
            options={
                'verbose_name': 'Savol',
                'verbose_name_plural': 'Savollar',
                'ordering': ['test', 'order'],
            },
        ),
        migrations.CreateModel(
<<<<<<< HEAD
            name='CourseImage',
=======
            name='Course',
>>>>>>> aeb74ee0da082676582a69441da7656c46579614
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')),
<<<<<<< HEAD
                ('image', models.ImageField(upload_to='course_images/%Y/%m/', verbose_name='Rasm')),
                ('caption', models.CharField(blank=True, help_text="Rasm ostida ko'rinadigan qisqa izoh.", max_length=255, null=True, verbose_name='Rasm tavsifi')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='core.course', verbose_name='Kurs')),
            ],
            options={
                'verbose_name': 'Kurs Rasmi',
                'verbose_name_plural': 'Kurs Rasmlari',
                'ordering': ['course', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='CourseSyllabus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')),
                ('title', models.CharField(blank=True, help_text="Masalan, '1-dars syllabusi'. Bo'sh qolsa fayl nomi ishlatiladi.", max_length=150, verbose_name='Fayl sarlavhasi')),
                ('file', models.FileField(help_text='Faqat PDF formatidagi fayllarni yuklang.', upload_to='course_syllabi/%Y/%m/', verbose_name='Syllabus Fayli (PDF)')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='syllabi', to='core.course', verbose_name='Kurs')),
            ],
            options={
                'verbose_name': 'Kurs Syllabusi',
                'verbose_name_plural': 'Kurs Syllabuslari',
                'ordering': ['course', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='ExternalActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')),
                ('title', models.CharField(help_text="Masalan, 'Lug'atlarni mustahkamlash'", max_length=200, verbose_name="Mashg'ulot sarlavhasi")),
                ('activity_type', models.CharField(choices=[('LA', 'LearningApps'), ('KH', 'Kahoot!'), ('OT', 'Boshqa')], default='OT', max_length=2, verbose_name="Mashg'ulot turi")),
                ('url', models.URLField(help_text="LearningApps uchun 'Share' yoki 'Embed' linkini kiriting (masalan, .../display?id=... yoki .../watch?v=...). Kahoot yoki boshqa platformalar uchun to'g'ridan-to'g'ri havolani kiriting.", max_length=500, verbose_name="Mashg'ulot manzili (URL)")),
                ('order', models.PositiveIntegerField(default=0, help_text="Mashg'ulotlarni ko'rsatish tartibi.", verbose_name='Tartib raqami')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='external_activities', to='core.course', verbose_name='Kurs')),
            ],
            options={
                'verbose_name': "Tashqi Mashg'ulot",
                'verbose_name_plural': "Tashqi Mashg'ulotlar",
                'ordering': ['course', 'order', 'title'],
            },
        ),
        migrations.AddField(
            model_name='course',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='core.module', verbose_name='Modul'),
        ),
        migrations.CreateModel(
=======
                ('title', models.CharField(max_length=255, verbose_name='Kurs sarlavhasi')),
                ('content', models.TextField(help_text='Kursning asosiy matnli mazmuni.', verbose_name='Kontent (mavzu)')),
                ('video_url', models.URLField(blank=True, help_text="Agar mavjud bo'lsa, YouTube video havolasi.", null=True, verbose_name='Video havolasi (YouTube)')),
                ('order', models.PositiveIntegerField(default=0, help_text="Modul ichidagi kurslarni ko'rsatish tartibi.", verbose_name='Tartib raqami')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='core.module', verbose_name='Modul')),
            ],
            options={
                'verbose_name': 'Kurs',
                'verbose_name_plural': 'Kurslar',
                'ordering': ['module', 'order', 'title'],
            },
        ),
        migrations.CreateModel(
>>>>>>> aeb74ee0da082676582a69441da7656c46579614
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')),
                ('text', models.CharField(max_length=255, verbose_name='Javob matni')),
                ('is_correct', models.BooleanField(default=False, help_text="Agar bu javob to'g'ri bo'lsa belgilang.", verbose_name="To'g'ri javob")),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='core.question', verbose_name='Savol')),
            ],
            options={
                'verbose_name': 'Javob',
                'verbose_name_plural': 'Javoblar',
                'ordering': ['question', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')),
                ('title', models.CharField(max_length=255, verbose_name='Test sarlavhasi')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Test tavsifi')),
<<<<<<< HEAD
                ('passing_score_percent', models.PositiveIntegerField(default=70, help_text="Testdan muvaffaqiyatli o'tish uchun talab qilinadigan minimal foiz (0-100).", verbose_name="O'tish bali (foizda)")),
=======
                ('passing_score_percent', models.PositiveIntegerField(default=70, help_text="Testdan muvaffaqiyatli o'tish uchun talab qilinadigan minimal foiz.", verbose_name="O'tish bali (foizda)")),
>>>>>>> aeb74ee0da082676582a69441da7656c46579614
                ('module', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='test', to='core.module', verbose_name='Modul')),
            ],
            options={
                'verbose_name': 'Test',
                'verbose_name_plural': 'Testlar',
<<<<<<< HEAD
                'ordering': ['module__order', 'module__title'],
=======
>>>>>>> aeb74ee0da082676582a69441da7656c46579614
            },
        ),
        migrations.AddField(
            model_name='question',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='core.test', verbose_name='Test'),
        ),
        migrations.CreateModel(
            name='UserTestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')),
                ('score', models.PositiveIntegerField(default=0, verbose_name="To'plangan ball (foizda)")),
                ('passed', models.BooleanField(default=False, verbose_name="O'tdi")),
                ('attempted_at', models.DateTimeField(auto_now_add=True, verbose_name='Urinish vaqti')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_results', to='core.test', verbose_name='Test')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_results', to=settings.AUTH_USER_MODEL, verbose_name='Foydalanuvchi')),
            ],
            options={
                'verbose_name': 'Foydalanuvchi Test Natijasi',
                'verbose_name_plural': 'Foydalanuvchilar Test Natijalari',
                'ordering': ['user', 'test', '-attempted_at'],
            },
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')),
                ('certificate_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Sertifikat ID')),
                ('issued_at', models.DateTimeField(auto_now_add=True, verbose_name='Berilgan vaqti')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to=settings.AUTH_USER_MODEL, verbose_name='Foydalanuvchi')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates_issued', to='core.module', verbose_name='Modul')),
            ],
            options={
                'verbose_name': 'Sertifikat',
                'verbose_name_plural': 'Sertifikatlar',
                'ordering': ['user', '-issued_at'],
                'unique_together': {('user', 'module')},
            },
        ),
        migrations.CreateModel(
            name='UserCourseProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqti')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan vaqti')),
                ('completed_at', models.DateTimeField(auto_now_add=True, verbose_name='Tugatilgan vaqti')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_progress', to='core.course', verbose_name='Kurs')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_progress', to=settings.AUTH_USER_MODEL, verbose_name='Foydalanuvchi')),
            ],
            options={
                'verbose_name': 'Foydalanuvchi Kurs Progressi',
                'verbose_name_plural': 'Foydalanuvchilar Kurs Progresslari',
                'ordering': ['user', '-completed_at'],
                'unique_together': {('user', 'course')},
            },
        ),
    ]
