from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from userapp.models import *
from alipay import AliPay
from django.conf import settings
from django.views import View
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django.db import transaction

import requests


def index(request):
    products = productinfo.objects.all()
    commod =commodityinfo.objects.all()
    return render(request,'index.html',{'products': products,'commod': commod})
@csrf_exempt
def get_commodities_by_category(request):
    if request.method == 'GET':
        category_id = request.GET.get('category_id')  # 获取分类 ID
        # 查询该分类下的所有商品
        commodities = commodityinfo.objects.filter(category_id_id=category_id).values('id', 'name', 'price','details')
        return JsonResponse(list(commodities), safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def activate_account(request):
    if request.method == 'POST':
        account = request.POST.get('account').strip()  # 去除前后空格
        print("账号的值为：", repr(account))  # 使用repr打印，显示不可见字符

        # 检查账号是否只包含数字
        if not account.isdigit():
            return JsonResponse(
                {'error': '账号必须是数字'},
                status=400,
                json_dumps_params={'ensure_ascii': False}  # 禁用 Unicode 编码
            )

        # 将账号转换为整数
        try:
            account = int(account)
        except ValueError:
            return JsonResponse(
                {'error': '账号必须是数字'},
                status=400,
                json_dumps_params={'ensure_ascii': False}  # 禁用 Unicode 编码
            )

        # 检查账号是否已经存在
        if userinfo.objects.filter(account=account).exists():
            # 如果账号已存在，直接返回成功
            return JsonResponse(
                {'message': '获取账号成功1'},
                json_dumps_params={'ensure_ascii': False}  # 禁用 Unicode 编码
            )

        # 如果账号不存在，尝试激活
        try:
            cdk_obj = CDKActivation.objects.first()  # 获取第一个CDK
            if not cdk_obj:
                return JsonResponse(
                    {'error': '没有可用的CDK'},
                    status=400,
                    json_dumps_params={'ensure_ascii': False}  # 禁用 Unicode 编码
                )

            cdk = cdk_obj.cdk

            # 准备发送到外部API的数据
            external_url = 'http://159.75.94.194:84/ht1/pay/pay.php'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 QuarkPC/2.3.5.270',
                'Cookie': 'b78f709544c04a3aa904a52978073ebe_ssl=c7939fe1-5268-4d15-8a85-52e3366bb543.-COxD06XIRZ3c97ogK_kTC1v2ug;a87f8c20366219d63ef11e567a563a54_ssl=aa61f4c8-2068-42b0-9732-5ddc58b195a9.tfAKd_gOhtEvD4EyYVNJAyjrHWc;b39a87411be1e3a83e8b30607842a26c_ssl=d7d2bd36-9eea-40e5-a415-b2753661e811.EVhd9MsoMn_8KOHYXdRiyWSocLI'
            }
            data = {
                'usr': account,
                'cdk': cdk,
                'sqm': 'cnm123'  # 固定值
            }

            # 发送POST请求到外部API
            response = requests.post(external_url, headers=headers, data=data)

            # 打印外部API的响应内容（用于调试）
            print("外部API响应状态码:", response.status_code)
            print("外部API响应内容:", response.text)

            # 检查外部API的响应
            if response.status_code == 200:
                # 保存账号到userapp表
                userinfo.objects.create(account=account, cdk=cdk)  # 假设密码为默认值

                # 删除已使用的CDK
                cdk_obj.delete()

                # 返回成功响应
                return JsonResponse(
                    {'message': '获取账号成功2'},
                    json_dumps_params={'ensure_ascii': False}  # 禁用 Unicode 编码
                )
            else:
                return JsonResponse(
                    {'error': '外部API激活失败'},
                    status=400,
                    json_dumps_params={'ensure_ascii': False}  # 禁用 Unicode 编码
                )
        except Exception as e:
            # 打印异常信息（用于调试）
            print("发生异常:", str(e))
            return JsonResponse(
                {'error': str(e)},
                status=500,
                json_dumps_params={'ensure_ascii': False}  # 禁用 Unicode 编码
            )
    else:
        return JsonResponse(
            {'error': '无效的请求方法'},
            status=405,
            json_dumps_params={'ensure_ascii': False}  # 禁用 Unicode 编码
        )


class OrderQueryView(View):
    def get(self, request):
        account = request.GET.get('account')
        if not account:
            return JsonResponse({'error': '缺少账号参数'}, status=400)

        try:
            # 校验账号是否为11位数字
            if len(account) != 11 or not account.isdigit():
                return JsonResponse({'error': '账号必须为11位数字'}, status=400)

            account_int = int(account)
            # 进一步校验数值范围（可选）
            if account_int < 10000000000 or account_int > 199999999999:
                return JsonResponse({'error': '无效的手机号格式'}, status=400)

            user = userinfo.objects.get(account=account_int)
            orders = sinkingorder.objects.filter(player=user).select_related('player')

            data = [{
                "time": order.time.strftime("%Y-%m-%d %H:%M:%S"),
                "order_number": order.ordernumber,
                "state": "已完成" if order.state else "未完成"
            } for order in orders]

            return JsonResponse({'orders': data}, safe=False)

        except userinfo.DoesNotExist:
            return JsonResponse({'error': '用户不存在'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'服务器错误: {str(e)}'}, status=500)


@require_GET
def check_benefit(request):
    account = request.GET.get('account')
    if not account or not account.isdigit() or len(account) != 11:
        return JsonResponse({
            'success': False, 
            'error': '无效的账号格式'
        }, status=400)

    try:
        account_int = int(account)
        user = userinfo.objects.get(account=account_int)
        topup = topupinfo.objects.get(player=user)
        
        return JsonResponse({
            'success': True,
            # 'uptoday': topup.uptoday,
            'uptotal': topup.uptotal
        })
        
    except userinfo.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '用户不存在'
        }, status=404)
        
    except topupinfo.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '无充值记录'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)

@csrf_exempt  # 临时禁用CSRF（生产环境需替换为安全方案）
def claim_gift(request):
    # 接收前端参数
    gift_id = request.POST.get('gift_id')
    account = request.POST.get('account')
    uptotal = float(request.POST.get('uptotal', 0))

    # 礼包配置（从数据库读取更安全）
    GIFT_CONFIG = {
        '1': {'min_amount': 100, 'item': '201401'},
        '2': {'min_amount': 200, 'item': '201402'},
        '3': {'min_amount': 500, 'item': '201403'}
    }

    # 验证参数
    if not gift_id or not account:
        return JsonResponse({'success': False, 'message': '参数缺失'})

    if gift_id not in GIFT_CONFIG:
        return JsonResponse({'success': False, 'message': '无效礼包'})

    config = GIFT_CONFIG[gift_id]
    if uptotal < config['min_amount']:
        return JsonResponse({'success': False, 'message': f'累计充值不足{config["min_amount"]}元'})

    # 构建请求参数
    payload = {
        'sqm': 'cnm123',
        'usr': account,
        'bao': '500001',
        'num': '1',
        'item': config['item'],
        'items': '0',
        'nums': '',
        'quid': '1',
        'gnxz': '2'
    }

    # 请求头配置（Cookie需从安全存储获取）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 QuarkPC/2.3.5.270',
        'Cookie': 'b39a87411be1e3a83e8b30607842a26c_ssl=9c940c48-9b23-40eb-95bb-5395a7a98e6b.ttC_dvOAQFENek8hdpWx8wQvbRQ',
        'Referer': 'http://159.75.94.194:84/ht1/vip/',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # 发送请求到外部API
    try:
        response = requests.post(
            'http://159.75.94.194:84/ht1/vip/api.php',
            data=payload,
            headers=headers
        )
        response.raise_for_status()  # 检查HTTP错误
        if '发送成功' in response.text:
            return JsonResponse({'success': True, 'message': '领取成功'})
        else:
            return JsonResponse({'success': False, 'message': response.text})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'请求失败: {str(e)}'})


# Create your views here.
