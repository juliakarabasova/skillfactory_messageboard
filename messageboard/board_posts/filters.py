from django.forms import DateInput
from django_filters import FilterSet, DateFilter, CharFilter, ModelChoiceFilter, ChoiceFilter

from django.contrib.auth.models import User
from .models import Post, Category, Answer


class PostFilter(FilterSet):
    post_date = DateFilter(widget=DateInput(attrs={'type': 'date'}), lookup_expr='gt',
                           field_name='post_date', label='Дата публикации позднее')

    title = CharFilter(lookup_expr='icontains', field_name='title', label='Заголовок')

    author = ModelChoiceFilter(field_name='author', label='Имя автора', empty_label='Все авторы',
                               queryset=User.objects.all())

    postcategory = ModelChoiceFilter(field_name='categories',  # Use 'categories' if that's the field name in your model
                                      label='Категория',
                                      empty_label='Все категории',
                                      queryset=Category.objects.all())

    class Meta:
        model = Post
        fields = ['title', 'author', 'post_date', 'postcategory']


class AnswerFilter(FilterSet):
    post_id = ModelChoiceFilter(
        queryset=Post.objects.none(),  # Initially set to none
        label='Пост',
        empty_label='Все посты'
    )

    class Meta:
        model = Answer
        fields = ['post_id']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Pop the user from kwargs
        super().__init__(*args, **kwargs)

        # Set the queryset for the post_id field based on the answers for the given user
        self.filters['post_id'].queryset = (
            Post.objects.filter(author=user).order_by('-post_date').values_list('pk', flat=True))
