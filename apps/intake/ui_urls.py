from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import ui_views

urlpatterns = [
    path('', ui_views.inbox, name='inbox'),
    path('tester/', ui_views.tester, name='tester'),
    path('requests/<uuid:request_id>/', ui_views.detail, name='detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
