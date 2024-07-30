from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail

from .models import Post, User, PostCategory, Category, Answer
from .filters import PostFilter, AnswerFilter
from .forms import PostForm, AnswerForm


class PostList(ListView):
    model = Post
    ordering = '-post_date'
    # queryset = Product.objects[.filter(price__lt=300)].order_by(-name)

    template_name = 'posts.html'
    context_object_name = 'posts'

    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        for post in queryset:
            post.text_categories = ', '.join(
                list(PostCategory.objects.filter(post=post).values_list('category__category', flat=True))
            )
            post.answers = Answer.objects.filter(post=post).count()
        return queryset


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answers_count'] = Answer.objects.filter(post=self.object).count()
        context['answer_form'] = AnswerForm()  # Add the form to the context

        answered = Answer.objects.filter(post=self.object, user=self.request.user).exists()
        context['answered'] = answered  # Add this to the context

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.post = self.object  # Assign the post
            answer.user = request.user  # Assign the user (if your Answer model has a user field)
            answer.save()

            # Send notification email to the author
            subject = 'Новый отклик на ваш запрос'
            message = (f'Пользователь {request.user.username} откликнулся на вашу запись "{answer.post.title}". '
                       f'Посмотреть тут: http://127.0.0.1:8000/posts/{answer.post.pk}')  # TODO: add url
            recipient_list = [answer.post.author.email]

            send_mail(subject, message, 'Skillfactory MessageBoard <juliakarabasova@yandex.ru>', recipient_list)

            return self.get(self, request, *args, **kwargs)  # Redirect to the same page or another page
        return self.render_to_response({'answer_form': form, 'post': self.object})


class PostSearch(ListView):
    model = Post
    ordering = '-post_date'

    template_name = 'post_search.html'
    context_object_name = 'posts'

    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        self.filterset = PostFilter(self.request.GET, queryset)

        for post in self.filterset.qs:
            post.text_categories = ', '.join(
                list(PostCategory.objects.filter(post=post).values_list('category__category', flat=True))
            )

        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Set the author field
            post.save()

            categories = form.cleaned_data.get('categories')
            for category in categories:
                PostCategory.objects.create(post=post, category=category)

            return redirect('posts_list')  # Или на страницу с детальной информацией о посте
    else:
        form = PostForm()
    return render(request, 'post_edit.html', {'form': form})


class PostUpdate(LoginRequiredMixin, UpdateView):
    # permission_required = ('post.change_post',)

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('posts_list')


class PostDelete(LoginRequiredMixin, DeleteView):
    # permission_required = ('post.delete_post',)

    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts_list')


class CategoryList(ListView):
    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'


class UserPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10  # Number of posts per page

    def get_queryset(self):
        # Get the user by pk from the URL
        user_pk = self.kwargs['pk']  # Assuming the URL pattern captures user pk
        user = get_object_or_404(User, pk=user_pk)
        # Filter posts where the user is in the answers field
        return Post.objects.filter(author=user).order_by('-post_date')

    # Optionally define `get_context_data` if you want to pass the user to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_pk = self.kwargs['pk']
        context['user'] = get_object_or_404(User, pk=user_pk)
        return context


class UserAnswersView(LoginRequiredMixin, ListView):
    model = Answer
    template_name = 'user_answers.html'
    context_object_name = 'answers'
    paginate_by = 10  # Number of posts per page

    def get_queryset(self):
        # Get the user by pk from the URL
        user_pk = self.kwargs['pk']  # Assuming the URL pattern captures user pk
        user = get_object_or_404(User, pk=user_pk)
        # Filter posts where the user is in the answers field
        return Answer.objects.filter(user=user).select_related('post').order_by('-create_time')

    # Optionally define `get_context_data` if you want to pass the user to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_pk = self.kwargs['pk']
        context['user'] = get_object_or_404(User, pk=user_pk)
        return context


class UserPostAnswersView(LoginRequiredMixin, ListView):
    model = Answer
    template_name = 'user_post_answers.html'
    context_object_name = 'answers'
    paginate_by = 10  # Number of posts per page

    def get_queryset(self):
        user_pk = self.kwargs['pk']  # User ID from URL
        user = get_object_or_404(User, pk=user_pk)

        queryset = Answer.objects.filter(post__author=user).order_by('-create_time')
        self.filterset = AnswerFilter(self.request.GET, queryset, user=user)

        return self.filterset.qs

    # Optionally define `get_context_data` if you want to pass the user to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_pk = self.kwargs['pk']
        context['user'] = get_object_or_404(User, pk=user_pk)
        context['filterset'] = self.filterset
        return context


class AcceptAnswerView(View):

    def post(self, request, answer_id):
        answer = get_object_or_404(Answer, pk=answer_id)
        answer.accepted = True
        answer.save()

        # Send notification email to the author
        subject = 'Ваш отклик был принят'
        message = (f'Пользователь {answer.post.author.username} принял ваш отклик на вашу запись "{answer.post.title}". '
                   f'Посмотреть тут: http://127.0.0.1:8000/answers/{answer.post.author.pk}')
        recipient_list = [answer.user.email]

        send_mail(subject, message, 'Skillfactory MessageBoard <juliakarabasova@yandex.ru>', recipient_list)

        return redirect('my_post_answers', pk=request.user.pk)  # Redirect to the answer list


class DeleteAnswerView(View):

    def post(self, request, answer_id):
        answer = get_object_or_404(Answer, pk=answer_id)
        answer.delete()
        return redirect('my_post_answers', pk=request.user.pk)  # Redirect to the answer list
