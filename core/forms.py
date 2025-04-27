# learning_platform/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

# Modellarni import qilish (agar Test ga havola kerak bo'lsa)
# To'g'ri import yo'lini ko'rsating
from core.models import Question, Answer, Test


# Django'ning standart UserCreationFormidan meros olib,
# emailni talab qilinadigan qilish va boshqa o'zgartirishlar kiritish mumkin.
# Hozircha standartini ishlatsak bo'ladi yoki o'zinikini yaratish mumkin:
# class CustomUserCreationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     class Meta(UserCreationForm.Meta):
#         fields = UserCreationForm.Meta.fields + ('email',)

class CustomAuthenticationForm(AuthenticationForm):
    """Login uchun standart forma (agar kerak bo'lsa moslashtiriladi)"""
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': _('Foydalanuvchi nomi')})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'placeholder': _('Parol')}),
    )


class TestSubmissionForm(forms.Form):
    """
    Test javoblarini qabul qilish uchun dinamik yaratiladigan forma.
    Har bir savol uchun RadioSelect widget ishlatiladi.
    """
    # test_pk ni endi init da o'rnatamiz, alohida field shart emas
    # test_pk = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        # Formani yaratishda test obyektini olishimiz kerak
        test_instance = kwargs.pop('test', None)
        if not isinstance(test_instance, Test):
             raise ValueError("TestSubmissionForm 'test' argumentini talab qiladi.")

        super().__init__(*args, **kwargs)
        self.test = test_instance # Test obyektini saqlab qo'yamiz

        # Testdagi har bir savol uchun forma maydoni (field) qo'shamiz
        # Savollarni va javoblarni oldindan yuklab olish samaradorlikni oshiradi
        questions = self.test.questions.prefetch_related('answers').order_by('order')

        for question in questions:
            # Variantlarni (choices) tayyorlaymiz: (answer.pk, answer.text) formatida
            # Javoblarni aralashtirish (shuffle) mumkin, agar kerak bo'lsa
            choices = [
                (answer.pk, answer.text)
                for answer in question.answers.all() # Javoblar allaqachon prefetch qilingan
            ]
            if not choices:
                 # Agar savolning javoblari bo'lmasa, bu savolni o'tkazib yuborish mumkin
                 # yoki xatolik ko'rsatish mumkin. Hozircha o'tkazib yuboramiz.
                 continue

            # Har bir savol uchun RadioSelect maydoni
            field_name = f'question_{question.pk}'
            self.fields[field_name] = forms.ChoiceField(
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
        PK lar string sifatida qaytariladi, chunki ChoiceField qiymati string.
        """
        answers = {}
        if self.is_valid():
            for name, value in self.cleaned_data.items():
                if name.startswith('question_'):
                    # Maydon nomidan 'question_' qismini olib tashlab, question_pk ni olamiz
                    # PK ni int ga o'tkazmasdan string holida saqlaymiz
                    question_pk_str = name.split('_')[1]
                    answers[question_pk_str] = value # value bu tanlangan answer.pk (string)
        return answers