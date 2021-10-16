from django.forms import ModelForm, ValidationError

from .models import Comment, Post


class PostForm(ModelForm):
    """Форма для создания нового поста или его редактирования."""
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']

    def clean_text(self):
        """Валидация поля text."""
        data = self.cleaned_data['text']
        if data is None:
            raise ValidationError('Поле должно быть заполенно')
        return data


class CommentForm(ModelForm):
    """Форма для создания комментария."""
    class Meta:
        model = Comment
        fields = ['text']

    def clean_text(self):
        data = self.cleaned_data['text']
        if data is None:
            raise ValidationError('Поле должно быть заполнено')
        return data
