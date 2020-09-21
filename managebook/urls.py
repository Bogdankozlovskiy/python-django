from django.urls import path
from managebook.views import HelloView, AddComment, AddRate, LogoutView, LoginView, RegisterView

urlpatterns = [
    path('hello/', HelloView.as_view(), name="hello"),
    path("add_like_to_comment/<int:id>/", AddComment.as_view(), name="add_comment"),
    path('add_rate_for_book/<int:id>/<int:rate>/', AddRate.as_view(), name="add_rate"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
]
