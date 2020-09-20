from django.urls import path
from managebook.views import HelloView, AddComment, AddRate

urlpatterns = [
    path('hello/', HelloView.as_view(), name="hello"),
    path("add_like_to_comment/<int:id>/", AddComment.as_view(), name="add_comment"),
    path('add_rate_for_book/<int:id>/<int:rate>', AddRate.as_view(), name="add_rate"),
]
