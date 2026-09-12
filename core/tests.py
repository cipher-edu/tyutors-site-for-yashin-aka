import base64

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

TINY_PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
)

from core.models import (
    Module,
    Course,
    Test,
    Question,
    Answer,
    CourseSyllabus,
    SiteDocument,
    Infographic,
)
from core.utils import calculate_test_score


class ScoringTests(TestCase):
    def setUp(self):
        self.module = Module.objects.create(title='Axloq moduli', order=1)
        self.test = Test.objects.create(
            module=self.module,
            title='Yakuniy test',
            passing_score_percent=70,
        )
        self.q1 = Question.objects.create(test=self.test, text='Savol 1', order=1)
        self.a1_wrong = Answer.objects.create(question=self.q1, text='Noto\'g\'ri', is_correct=False)
        self.a1_right = Answer.objects.create(question=self.q1, text='To\'g\'ri', is_correct=True)

        self.q2 = Question.objects.create(test=self.test, text='Savol 2', order=2)
        self.a2_right = Answer.objects.create(question=self.q2, text='To\'g\'ri', is_correct=True)
        Answer.objects.create(question=self.q2, text='Noto\'g\'ri', is_correct=False)

    def test_all_correct_passes(self):
        answers = {
            str(self.q1.pk): str(self.a1_right.pk),
            str(self.q2.pk): str(self.a2_right.pk),
        }
        score, passed = calculate_test_score(self.test, answers)
        self.assertEqual(score, 100)
        self.assertTrue(passed)

    def test_wrong_answer_does_not_count_other_question_correct(self):
        answers = {
            str(self.q1.pk): str(self.a2_right.pk),
            str(self.q2.pk): str(self.a2_right.pk),
        }
        score, passed = calculate_test_score(self.test, answers)
        self.assertEqual(score, 50)
        self.assertFalse(passed)

    def test_empty_test_does_not_auto_pass(self):
        empty_module = Module.objects.create(title='Bo\'sh modul', order=2)
        empty_test = Test.objects.create(module=empty_module, title='Bo\'sh test')
        score, passed = calculate_test_score(empty_test, {})
        self.assertEqual(score, 0)
        self.assertFalse(passed)


class DocumentValidationTests(TestCase):
    def setUp(self):
        self.module = Module.objects.create(title='Huquqiy asoslar')
        self.course = Course.objects.create(module=self.module, title='1-ma\'ruza')

    def test_word_file_is_accepted(self):
        syllabus = CourseSyllabus(
            course=self.course,
            title='Ma\'ruza 1',
            file=SimpleUploadedFile('lecture.docx', b'word-bytes', content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
        )
        syllabus.full_clean()

    def test_exe_file_is_rejected(self):
        syllabus = CourseSyllabus(
            course=self.course,
            title='Zararli',
            file=SimpleUploadedFile('virus.exe', b'MZ', content_type='application/octet-stream'),
        )
        with self.assertRaises(ValidationError):
            syllabus.full_clean()

    def test_site_document_word_ok(self):
        doc = SiteDocument(
            title='Ish reja',
            document_type=SiteDocument.PLAN,
            file=SimpleUploadedFile('plan.doc', b'legacy-word', content_type='application/msword'),
        )
        doc.full_clean()


class HomepageTests(TestCase):
    def test_homepage_is_public(self):
        Infographic.objects.create(
            title='VUCA nima?',
            image=SimpleUploadedFile('info.png', TINY_PNG, content_type='image/png'),
            is_active=True,
        )
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('infographics', response.context)
        self.assertEqual(response.context['infographics'].count(), 1)

    def test_inactive_infographic_hidden(self):
        Infographic.objects.create(
            title='Yashirin',
            image=SimpleUploadedFile('info.png', TINY_PNG, content_type='image/png'),
            is_active=False,
        )
        response = self.client.get('/')
        self.assertEqual(response.context['infographics'].count(), 0)
