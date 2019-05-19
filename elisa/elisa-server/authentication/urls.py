from django.conf.urls import url
from .views import LoginView

urlpatterns = [
    url('login/', LoginView.as_view(), name='token_obtain_pair'),
]