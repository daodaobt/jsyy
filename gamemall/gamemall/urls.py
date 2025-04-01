"""
URL configuration for gamemall project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from django.contrib import admin
from userapp import views as userapp_views  # 前端视图
from admin_panel import views as admin_panel_views  # 后端视图
from pay.views import alipay_payment, alipay_return
from userapp.views import OrderQueryView,check_benefit  # 关键导入语句
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('index', userapp_views.index),
    path('activate-account/', userapp_views.activate_account, name='activate_account'),
    path('api/get-commodities/', userapp_views.get_commodities_by_category, name='get_commodities_by_category'),
    path('alipay/payment/', alipay_payment, name='alipay_payment'),  # 支付宝支付路由
    path('alipay/return/', alipay_return, name='alipay_return'),  # 同步返回 URL 路由
    path('alipay/notify/', alipay_return, name='alipay_notify'),  # 异步返回 URL 路由
    path('order-query/', OrderQueryView.as_view(), name='order-query'),
    path('check-benefit/', check_benefit, name='check-benefit'),
    path('claim-gift/', userapp_views.claim_gift, name='claim_gift'),
    path('admin/', admin_panel_views.admin_dashboard, name='admin_dashboard'),
    path('admin/products/', admin_panel_views.product_management, name='product_management'),
    path('admin/users/', admin_panel_views.user_management, name='user_management'),
    path('admin/orders/', admin_panel_views.order_management, name='order_management'),
    path('admin/cdks/', admin_panel_views.cdk_management, name='cdk_management'),
    path('admin/products/edit_category/<int:category_id>/', admin_panel_views.edit_category, name='edit_category'),
    path('admin/products/delete_category/<int:category_id>/', admin_panel_views.delete_category, name='delete_category'),
    path('admin/products/edit_product/<int:product_id>/', admin_panel_views.edit_product, name='edit_product'),
    path('admin/products/delete_product/<int:product_id>/', admin_panel_views.delete_product, name='delete_product'),
    path('admin/users/edit_user/<int:user_id>/', admin_panel_views.edit_user, name='edit_user'),
    path('admin/users/delete_user/<int:user_id>/', admin_panel_views.delete_user, name='delete_user'),
    path('admin/orders/edit_order/<int:order_id>/', admin_panel_views.edit_order, name='edit_order'),
    path('admin/orders/delete_order/<int:order_id>/', admin_panel_views.delete_order, name='delete_order'),
    path('admin/cdks/edit_cdk/<int:cdk_id>/', admin_panel_views.edit_cdk, name='edit_cdk'),
    path('admin/cdks/delete_cdk/<int:cdk_id>/', admin_panel_views.delete_cdk, name='delete_cdk'),
    path('admin/products/add_category/', admin_panel_views.add_category, name='add_category'),
    path('admin/products/add_product/', admin_panel_views.add_product, name='add_product'),
    path('admin/users/add_user/', admin_panel_views.add_user, name='add_user'),
    path('admin/cdks/generate/', admin_panel_views.generate_cdk, name='generate_cdk'),
    path('payment/status/', include('pay.monitoring.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
