from django import forms
from django.core.exceptions import ValidationError
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Post, Category, Answer


class PostForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorUploadingWidget(), label='Содержание')

    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'categories',
        ]
        labels = {
            'title': 'Заголовок',
            'text': 'Содержание',
            'categories': 'Категории'
        }

    def clean(self):
        cleaned_data = super().clean()
        description = cleaned_data.get("text")

        name = cleaned_data.get("title")
        if name == description:
            raise ValidationError(
                "Текст не должен быть идентичным заголовку."
            )

        return cleaned_data


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
