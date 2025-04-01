import logging
import uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.conf import settings
from alipay import AliPay,AliPayConfig
from datetime import datetime
from userapp.models import *  # 导入商品模型
# 解码 biz_content 参数
from urllib.parse import parse_qs, unquote
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F  # 新增此行
import os
import requests
import time
from django.db import transaction,connection
from django.http import JsonResponse
from .tasks import process_payment_success  # 导入Celery任务


alipay = AliPay(
    appid=settings.ALIPAY_APP_ID,
    app_notify_url=settings.ALIPAY_NOTIFY_URL,  # 启用异步通知
    app_private_key_string=settings.ALIPAY_PRIVATE_KEY,
    alipay_public_key_string=settings.ALIPAY_PUBLIC_KEY,
    sign_type="RSA2",  # 明确指定签名类型
    debug=settings.ALIPAY_DEBUG,
)
# print("读取的私钥：" + settings.ALIPAY_PRIVATE_KEY)
# print("读取的公钥：" + settings.ALIPAY_PUBLIC_KEY)


# def load_item_mappings():
#     mappings = {}
#     file_path = os.path.join(settings.BASE_DIR, 'data/item.txt')
#     with open(file_path, 'r', encoding='utf-8') as f:
#         for line in f:
#             line = line.strip()
#             if ';' in line:
#                 item_id, name = line.split(';', 1)  # 按第一个分号分割
#                 mappings[name] = item_id
#     return mappings

# ITEM_MAPPINGS = load_item_mappings()  # 全局缓存映射数据



def alipay_payment(request):
    if request.method == 'POST':
        commodity_id = request.POST.get('commodity_id')
        account = request.POST.get('account')

        try:
            # ================= 1. 数据验证 =================
            with transaction.atomic():
                # 验证商品存在性
                commodity = commodityinfo.objects.select_for_update().get(id=commodity_id)

                # 验证用户存在性
                user = userinfo.objects.get(account=account)

            # ================= 2. 生成订单号 =================
            timestamp = str(int(time.time() * 1000))[-10:]
            random_str = str(uuid.uuid4().hex)[:6]
            order_number = f"{timestamp}{random_str}"

            # ================= 3. 创建订单 =================
            new_order = sinkingorder.objects.create(
                player=user,
                commodity=commodity.name,
                price=commodity.price,
                ordernumber=order_number,
                time=timezone.now(),
                state=False,  # 初始状态为未支付
                zfbordernumber=''  # 支付宝交易号留空
            )

            # ================= 4. 支付宝参数构造 =================

            order_string = alipay.api_alipay_trade_page_pay(
                out_trade_no=order_number,
                total_amount=str(commodity.price),
                subject=f"{commodity.name}",
                return_url=settings.ALIPAY_RETURN_URL,
                notify_url=settings.ALIPAY_NOTIFY_URL
            )

            # ================= 5. 跳转支付 =================
            pay_url = f"{settings.ALIPAY_GATEWAY}?{order_string}"
            return redirect(pay_url)

        except commodityinfo.DoesNotExist:
            return JsonResponse({'status': 'error', 'msg': '商品不存在'}, status=400)
        except userinfo.DoesNotExist:
            return JsonResponse({'status': 'error', 'msg': '用户不存在'}, status=400)
        except Exception as e:
            # 记录完整错误日志
            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'msg': '系统异常'}, status=500)

    return redirect('index')

logger = logging.getLogger(__name__)


@csrf_exempt
def alipay_return(request):
    """处理支付宝同步回调"""
    try:
        raw_params = request.GET.urlencode()
        print(f"原始回调参数: {raw_params}")

        # === 1. 参数解析与验证 ===
        decoded_params = unquote(raw_params)
        data = parse_qs(decoded_params)
        data = {k: v[0] for k, v in data.items()}
        data.pop('sign', None)  # 移除sign参数
        # 记录处理后的参数
        print(f"解码后参数: {data}")

        # 获取并处理签名
        raw_sign = request.GET.get('sign', '')
        sign = unquote(raw_sign.replace(' ', '+'))
        print(f"获取签名: {sign}")
        print(f"获取签名后的data{data}")
        # === 2. 验证支付宝签名 ===
        success = alipay.verify(data, sign)
        print(f"验签结果2: {success}")
        if not success:
            print(f"签名验证失败 | 参数: {data} | 签名: {sign}")
            return HttpResponseRedirect('/index?payment=danger')
        print("验签成功，更新订单")
        # === 2. 更新订单状态 ===
        out_trade_no = data.get('out_trade_no')
        print(f"out_trade_no:{out_trade_no}")
        try:
            # 获取支付时创建的订单（包含用户信息）
            order = sinkingorder.objects.get(ordernumber=out_trade_no)

            # 更新订单状态和支付宝交易号
            order.zfbordernumber = data.get('trade_no')
            order.state = True
            order.process_status = 2
            order.save()
            print("进了更新订单了")
            # 触发异步任务（添加异常捕获）
            try:
                process_payment_success.delay(order.id)
                print("进了process_payment_succes了")
            except Exception as e:
                print(f"异步任务触发失败: {str(e)}")
            connection.close()
            return HttpResponseRedirect('/index?payment=success')

        except sinkingorder.DoesNotExist:
            print(f"订单不存在: {out_trade_no}")
            return HttpResponseRedirect('/index?payment=danger')

        # === 5. 立即返回响应 ===
        print("没进更新订单了")
        return HttpResponseRedirect('/index?payment=success')

    except Exception as e:
        import traceback
        print(f"订单更新失败: {str(e)}\n{traceback.format_exc()}")
        return HttpResponseRedirect('/index?payment=danger')








@csrf_exempt
def alipay_notify(request):
    """处理支付宝异步通知"""
    data = request.POST.dict()
    sign = data.pop('sign', '')
    success = alipay.verify(data, sign)
    
    if success and data.get('trade_status') in ('TRADE_SUCCESS', 'TRADE_FINISHED'):
        try:
            order = sinkingorder.objects.get(ordernumber=data.get('out_trade_no'))
            order.state = True
            order.save()
            return HttpResponse('success')  # 必须返回 'success' 告知支付宝已处理
        except Exception as e:
            print(f"异步通知处理失败: {str(e)}")
    return HttpResponse('fail')






















# Create your views here.
