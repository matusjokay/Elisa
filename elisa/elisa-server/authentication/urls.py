from django.conf.urls import url
from .views import LoginView, RefreshView

urlpatterns = [
    url('login/', LoginView.as_view(), name='token_obtain_pair'),
    url('api/token/refresh/', RefreshView.as_view(), name='token_refresh'),
]
