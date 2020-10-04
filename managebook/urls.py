from django.urls import path
from managebook.views import HelloView, AddCommentLike, AddRate, LogoutView, LoginView, RegisterView, AddComment, \
    AddNewBook, UpdateBook, DeleteBook, AddAjaxLike, AddAjaxRate, DeleteAjaxBook

urlpatterns = [
    path('hello/', HelloView.as_view(), name="hello"),
    path("add_like_to_comment/<int:id>/", AddCommentLike.as_view(), name="add_comment"),
    path('add_rate_for_book/<int:id>/<int:rate>/', AddRate.as_view(), name="add_rate"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('AddComment/<str:id>', AddComment.as_view(), name='add_a_new_comment'),
    path("AddNewBook/", AddNewBook.as_view(), name="add_new_book"),
    path("update_book/<int:id>", UpdateBook.as_view(), name="update_book"),
    path('DeleteBook/<int:id>/', DeleteBook.as_view(), name="delete_book"),
    ########## AJAX
    path("add_ajax_comment/", AddAjaxLike.as_view()),
    path("add_ajax_rate/", AddAjaxRate.as_view()),
    path("delete_ajax_book/", DeleteAjaxBook.as_view()),
]
