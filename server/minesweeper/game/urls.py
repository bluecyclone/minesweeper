from django.urls import path

from .views import BoardView


app_name = "games"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('games/', BoardView.as_view()),
    path('games/<int:id>/check/', BoardView.check),
    path('games/<int:id>/', BoardView.open),
]
