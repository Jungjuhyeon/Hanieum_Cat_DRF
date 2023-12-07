from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .import views 

urlpatterns = [
    # User
    path('users/register', views.RegistrationAPIView.as_view()),
    path('users/login', views.LoginAPIView.as_view()),
    path('users/auth',views.SmsSendView.as_view()),
    path('users/auth/check',views.SMSVerificationView.as_view()),
    path('users/uid-lost',views.UserIdLostView.as_view()),
    path('users/uid-recovery',views.UserIdRecoveryView.as_view()),
    path('users/password-lost',views.UserPasswordLostView.as_view()),
    path('users/password-recovery',views.UserPasswordRecoveryView.as_view()),
    path('users/password-restore',views.UserPasswordRestoreView.as_view()),

    #diagonsis
    path('diagnosis', views.DiagnosisRetrieveView.as_view(), name='diagnosis-list_diagnosis'),
    path('diagnosis/list', views.DiagnosisListView.as_view(), name='diagnosis-list_all'),
    path('diagnosis/image-upload', views.PredictedImageAPIView.as_view(), name='diagnosis-test'),

    #pet
    path('pet/create-pet', views.PetCreateView.as_view(), name='pet-create_pet'),
    path('pet/', views.PetListView.as_view(), name='pet-list_all'),
]
