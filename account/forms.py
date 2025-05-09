from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from .models import CustomUser 
import re
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=150)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

class CustomUserForm(forms.ModelForm):
    # Добавляем поле для выбора групп подписок
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'groups']

class RegisterForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=150, required=True)
    user_nickname = forms.CharField(label='Никнейм(@имя пользователя)', max_length=150, required=True)
    email = forms.EmailField(label='Электронная почта', required=True)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)
    age = forms.IntegerField(label='Возраст', required=True, min_value=18, max_value=120)
    confirm_password = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Это имя пользователя уже занято.')
        return username

    def clean_user_nickname(self):
        user_nickname = self.cleaned_data.get('user_nickname')
        if not re.match(r'^[A-Za-z0-9_]+$', user_nickname):
            raise ValidationError('Никнейм может содержать только английские буквы, цифры и подчеркивания.')
        if CustomUser.objects.filter(user_nickname=user_nickname).exists():
            raise ValidationError('Этот никнейм уже используется.')
        return user_nickname

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Этот адрес электронной почты уже используется.')
        return email
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 18 or age > 120:
            raise ValidationError('Возраст должен быть от 18 до 120 лет.')
        return age

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError('Пароли не совпадают.')

        return cleaned_data

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'description', 'avatar','age', 'user_nickname']