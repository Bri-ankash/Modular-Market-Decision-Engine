from django.contrib import admin
from django.urls import path
from mmde_gateway import views as gw
from users import views as uv
from payments import views as pv

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', gw.landing, name='landing'),
    path('login/', uv.login_view, name='login'),
    path('register/', uv.register_view, name='register'),
    path('logout/', uv.logout_view, name='logout'),
    path('app/', gw.dashboard, name='dashboard'),
    path('app/analysis/', gw.dashboard, name='analysis'),
    path('subscription/', gw.subscription, name='subscription'),
    path('api/mmde/analyze', gw.analyze, name='analyze'),
    path('api/market-data/', gw.market_data_api, name='market_data_api'),
    path('payments/<int:payment_id>/approve/', pv.admin_approve, name='approve_payment'),
    path('admin/payments/payment/<int:payment_id>/approve/', pv.admin_approve, name='approve_payment_admin'),
]
