import os

from django.shortcuts import render, redirect
from userapp.models import *
from .forms import ProductCategoryForm, ProductForm, UserForm, CDKForm
from .forms import ProductForm
#from .models import commodityinfo
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

def user_management(request):
    users = userinfo.objects.all()
    return render(request, 'user_management.html', {'users': users})

def order_management(request):
    orders = sinkingorder.objects.all()
    return render(request, 'order_management.html', {'orders': orders})

def cdk_management(request):
    cdks = CDKActivation.objects.all()
    return render(request, 'cdk_management.html', {'cdks': cdks})
def product_management(request):
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_management')
    else:
        form = ProductCategoryForm()
    categories = productinfo.objects.all()
    products = commodityinfo.objects.all()
    return render(request, 'product_management.html', {'form': form, 'categories': categories, 'products': products})
# 分类
def edit_category(request, category_id):
    category = productinfo.objects.get(id=category_id)
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('product_management')
    else:
        form = ProductCategoryForm(instance=category)
    return render(request, 'edit_category.html', {'form': form, 'category': category})

def delete_category(request, category_id):
    category = productinfo.objects.get(id=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('product_management')
    return render(request, 'delete_category.html', {'category': category})

def add_category(request):
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_management')
    else:
        form = ProductCategoryForm()
    return render(request, 'add_category.html', {'form': form})


# 商品


def edit_product(request, product_id):
    product = commodityinfo.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # 自动处理图片上传
            form.save()
            return redirect('/admin/products/')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form})











def delete_product(request, product_id):
    product = commodityinfo.objects.get(id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_management')
    return render(request, 'delete_product.html', {'product': product})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # 关键：必须包含 request.FILES
        if form.is_valid():
            form.save()
            return redirect('product_management')  # 重定向到商品管理页
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


# 用户
def edit_user(request, user_id):
    user = userinfo.objects.get(id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = UserForm(instance=user)
    return render(request, 'edit_user.html', {'form': form, 'user': user})

def delete_user(request, user_id):
    user = userinfo.objects.get(id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_management')
    return render(request, 'delete_user.html', {'user': user})

def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = UserForm()
    return render(request, 'add_user.html', {'form': form})


# 订单

def edit_order(request, order_id):
    order = sinkingorder.objects.get(id=order_id)
    if request.method == 'POST':
        # 在实际项目中，你需要根据需求创建一个订单表单
        # 这里只是一个示例
        order.state = request.POST.get('state') == 'true'
        order.save()
        return redirect('order_management')
    return render(request, 'edit_order.html', {'order': order})

def delete_order(request, order_id):
    order = sinkingorder.objects.get(id=order_id)
    if request.method == 'POST':
        order.delete()
        return redirect('order_management')
    return render(request, 'delete_order.html', {'order': order})



# cdk

def edit_cdk(request, cdk_id):
    cdk = CDKActivation.objects.get(id=cdk_id)
    if request.method == 'POST':
        form = CDKForm(request.POST, instance=cdk)
        if form.is_valid():
            form.save()
            return redirect('cdk_management')
    else:
        form = CDKForm(instance=cdk)
    return render(request, 'edit_cdk.html', {'form': form, 'cdk': cdk})

def delete_cdk(request, cdk_id):
    cdk = CDKActivation.objects.get(id=cdk_id)
    if request.method == 'POST':
        cdk.delete()
        return redirect('cdk_management')
    return render(request, 'delete_cdk.html', {'cdk': cdk})

import requests

def generate_cdk(request):
    if request.method == 'POST':
        # 发送 POST 请求到外部 API
        url = 'http://159.75.94.194:84/ht1/cdk/cdks.php'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 QuarkPC/2.3.7.277',
            'Cookie': 'b39a87411be1e3a83e8b30607842a26c_ssl=9c940c48-9b23-40eb-95bb-5395a7a98e6b.ttC_dvOAQFENek8hdpWx8wQvbRQ',
            'Referer': 'http://159.75.94.194:84/ht1/cdk/',
        }
        data = {
            'sqm': 'asd5696954',
            'num': 100,
            'type': 3
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()  # 检查 HTTP 错误

            # 解析返回的文本内容
            cdk_list = response.text.strip().split('\n')

            # 将每个 CDK 添加到数据库中
            for cdk in cdk_list:
                CDKActivation.objects.create(cdk=cdk)

            return render(request, 'generate_cdk_success.html', {'cdk_list': cdk_list})
        except requests.exceptions.RequestException as e:
            return render(request, 'generate_cdk_error.html', {'error': str(e)})
    else:
        return render(request, 'generate_cdk.html')




# Create your views here.
