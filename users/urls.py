from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "users"

urlpatterns = [
    path('login/', views.login_user, name='login'),
    # path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('lk/', views.lk_user, name='lk_user'),
    path('add_users/', views.add_user, name='add_users'),
    # path('add_pokazaniya/', views.add_pokazaniya, name='add_pokazaniya'),
    path('edit_phone_ajax/', views.EditPhoneAjax.as_view(), name='edit_phone_ajax'),
    path('edit_email_ajax/', views.EditEmailAjax.as_view(), name='edit_email_ajax'),
    path('edit_rec_doc_ajax/', views.EditRecDocAjax.as_view(), name='edit_rec_doc_ajax'),
    path('password_change_ajax/', views.ChangePasswordAjax.as_view(), name='password_change_ajax'),
    path('verify_email/<uidb64>/<token>/', views.EmailVerify.as_view(), name='verify_email'),
    path('invalid_verify/', TemplateView.as_view(template_name='users/invalid_verify.html'), name='invalid_verify'),
    path('pokazaniya_write_ajax/', views.PokazaniyaWriteAjax.as_view(), name='pokazaniya_write_ajax'),
]
