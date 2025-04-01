from django import forms
from userapp.models import *
# from django.utils.translation import gettext_lazy as _

class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = productinfo
        fields = '__all__'
        labels = {
            'category': '分类名称',
        }
        error_messages = {
            'category': {
                'required': '分类名称是必填的。',
            },
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = commodityinfo
        fields = '__all__'
        labels = {
            'name': '名称',
            'price': '价格',
            'num': '数量',
            'details': '详情',
            'category_id': '分类 ID',
        }
        error_messages = {
            'name': {
                'required': '名称是必填的。',
            },
            'price': {
                'required': '价格是必填的。',
            },
            'num': {
                'required': '数量是必填的。',
            },
            'details': {
                'required': '详情是必填的。',
            },
            'category_id': {
                'required': '分类 ID 是必填的。',
            },
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = userinfo
        fields = '__all__'
        labels = {
            'account': '账号',
            'cdk': '激活CDK',
        }
        error_messages = {
            'account': {
                'required': '账号是必填的。',
            },
            'cdk': {
                'required': '激活CDK',
            },
        }

class CDKForm(forms.ModelForm):
    class Meta:
        model = CDKActivation
        fields = '__all__'
        labels = {
            'cdk': 'CDK码',
            'activation_count': '激活次数',
        }
        error_messages = {
            'cdk': {
                'required': 'CDK码是必填的。',
            },
            'activation_count': {
                'required': '激活次数是必填的。',
            },
        }