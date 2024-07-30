from django.urls import path
from .views import (PostList, PostDetail, PostSearch, PostUpdate, PostDelete,
                    post_create, UserPostsView, UserAnswersView, UserPostAnswersView,
                    AcceptAnswerView, DeleteAnswerView)

urlpatterns = [
    path('', PostList.as_view(), name='posts_list'),
    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('search', PostSearch.as_view(), name='posts_filter'),
    path('create', post_create, name='posts_create'),  # PostCreate.as_view()
    path('<int:pk>/edit/', PostUpdate.as_view(), name='posts_update'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='posts_delete'),
    path('posts/<int:pk>/', UserPostsView.as_view(), name='my_posts'),
    path('answers/<int:pk>/', UserAnswersView.as_view(), name='my_answers'),
    path('post_answers/<int:pk>/', UserPostAnswersView.as_view(), name='my_post_answers'),
    path('answer/<int:answer_id>/accept/', AcceptAnswerView.as_view(), name='accept_answer'),
    path('answer/<int:answer_id>/delete/', DeleteAnswerView.as_view(), name='delete_answer'),
]
