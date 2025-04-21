# learning_platform/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import Question, Answer, Test


# Django'ning standart UserCreationFormidan meros olib,
# emailni talab qilinadigan qilish va boshqa o'zgartirishlar kiritish mumkin.
# Hozircha standartini ishlatsak bo'ladi yoki o'zinikini yaratish mumkin:
# class CustomUserCreationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     class Meta(UserCreationForm.Meta):
#         fields = UserCreationForm.Meta.fields + ('email',)

class CustomAuthenticationForm(AuthenticationForm):
    """Login uchun standart forma (agar kerak bo'lsa moslashtiriladi)"""
    # Misol uchun, placeholder qo'shish:
    # username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('Foydalanuvchi nomi yoki Email')}))
    # password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': _('Parol')}))
    pass # Hozircha o'zgartirish yo'q


class TestSubmissionForm(forms.Form):
    """
    Test javoblarini qabul qilish uchun dinamik yaratiladigan forma.
    Har bir savol uchun RadioSelect widget ishlatiladi.
    """
    test_pk = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        # Formani yaratishda test obyektini yoki pk'sini olishimiz kerak
        test_instance_or_pk = kwargs.pop('test', None)
        super().__init__(*args, **kwargs)

        test = None
        if isinstance(test_instance_or_pk, Test):
            test = test_instance_or_pk
            self.fields['test_pk'].initial = test.pk
        elif isinstance(test_instance_or_pk, int):
             self.fields['test_pk'].initial = test_instance_or_pk
             try:
                 test = Test.objects.prefetch_related('questions__answers').get(pk=test_instance_or_pk)
             except Test.DoesNotExist:
                 # Test topilmasa, savollar qo'shilmaydi. View qismida bu holatni handle qilish kerak.
                 pass

        if test:
            # Testdagi har bir savol uchun forma maydoni (field) qo'shamiz
            for question in test.questions.all():
                # Variantlarni (choices) tayyorlaymiz: (answer.pk, answer.text) formatida
                choices = [
                    (answer.pk, answer.text)
                    for answer in question.answers.all()
                ]
                # Har bir savol uchun RadioSelect maydoni
                self.fields[f'question_{question.pk}'] = forms.ChoiceField(
                    label=question.text,
                    choices=choices,
                    widget=forms.RadioSelect,
                    required=True, # Har bir savolga javob berish majburiy
                    error_messages={'required': _("Iltimos, ushbu savolga javob tanlang.")}
                )

    def get_user_answers(self) -> dict:
        """
        Forma validatsiyadan o'tgandan so'ng, foydalanuvchi javoblarini
        {'question_pk': 'answer_pk', ...} formatida qaytaradi.
        """
        answers = {}
        if self.is_valid():
            for name, value in self.cleaned_data.items():
                if name.startswith('question_'):
                    # Maydon nomidan 'question_' qismini olib tashlab, question_pk ni olamiz
                    question_pk = name.split('_')[1]
                    answers[question_pk] = value # value bu tanlangan answer.pk
        return answers