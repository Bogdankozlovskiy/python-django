from django.urls import path
from managebook import views

urlpatterns = [
    path('hello/', views.HelloView.as_view(), name="hello"),
    path('hello/<int:page_id>', views.HelloView.as_view(), name="hello"),
    path("add_like_to_comment/<int:id>/", views.AddCommentLike.as_view(), name="add_comment"),
    path('add_rate_for_book/<int:id>/<int:rate>/', views.AddRate.as_view(), name="add_rate"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('AddComment/<str:id>/', views.AddComment.as_view(), name='add_a_new_comment'),
    path("AddNewBook/", views.AddNewBook.as_view(), name="add_new_book"),
    path("update_book/<int:id>/", views.UpdateBook.as_view(), name="update_book"),
    path('DeleteBook/<int:id>/', views.DeleteBook.as_view(), name="delete_book"),
    ########## AJAX
    path("add_ajax_comment/", views.AddAjaxLike.as_view()),
    path("add_ajax_rate/", views.AddAjaxRate.as_view()),
    path("delete_ajax_book/<int:book_id>/", views.DeleteAjaxBook.as_view()),
    path('delete_ajax_comment/<int:comment_id>/', views.DeleteAjaxComment.as_view()),
]
