from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "давай напишем сообщение",
            "group": "Групочка"
        }
        help_texts = {
            "text": "обязательно для заполнения",
            "group": "можно не заполнять"
        }


class PostComment(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'вперёд критики!'}
        help_texts = {'text': 'обязательно для заполнения'}
