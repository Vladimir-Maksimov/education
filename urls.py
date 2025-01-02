from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='home'),
    path('account', views.account, name='account'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('product_list', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('logout/', views.user_logout, name='logout'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>',views.remove_from_cart, name='remove_from_cart'),
    path('cart', views.cart_view, name='cart'),
    path('create_order', views.create_order, name='create_order'),
    path('order_success/<int:order_id>', views.order_success, name='order_success'),
    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name="registration/reset_password.html"),
         name='reset_password'),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_sent.html"),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_form.html"),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_done.html"),
         name='password_reset_complete')
]
