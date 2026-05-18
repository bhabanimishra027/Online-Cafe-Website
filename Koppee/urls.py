from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('menu/', views.menu_view, name='menu'),
    path('order/', views.create_order_view, name='create_order'),
    path('coffee/', views.coffee_detail_view, name='coffee_detail'),
    path('my_orders/', views.my_orders_view, name='my_orders'),
    path('contact/', views.contact_view, name='contact'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('payment/', views.payment_page, name='payment_page'),
    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),
    path('review/', views.review_view, name='review'),
    path('thankyou/', views.thank_you_view, name='thankyou'),
]
