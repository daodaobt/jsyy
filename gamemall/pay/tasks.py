from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import transaction, connection
import requests
import logging
from userapp.models import *
import os

def load_item_mappings():
    mappings = {}
    file_path = os.path.join(settings.BASE_DIR, 'data/item.txt')
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if ';' in line:
                item_id, name = line.split(';', 1)  # 按第一个分号分割
                mappings[name] = item_id
    return mappings

ITEM_MAPPINGS = load_item_mappings()  # 全局缓存映射数据


@shared_task(bind=True, max_retries=3)
def process_payment_success(self, order_id):
    print("开始处理支付成订单")
    try:
        # ================= 1. 更新订单状态 =================
        with transaction.atomic():
            order = sinkingorder.objects.select_for_update().get(id=order_id)
            order.state = True
            order.save(update_fields=['state'])

            # ================= 2. 更新充值记录 =================
            player = order.player
            topup, created = topupinfo.objects.get_or_create(
                player=player,
                defaults={'uptoday': 0, 'uptotal': order.price}
            )
            if not created:
                topup.uptotal += order.price
                topup.save(update_fields=['uptotal'])

            # ================= 3. 异步发送道具请求 =================
            send_item_request.delay(order.id)
            return True

    except Exception as e:
        print("订单处理失败")
        self.retry(exc=e, countdown=60 * self.request.retries)

    finally:
        # ================= 4. 清理数据库连接 =================
        connection.close()

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_item_request(self, order_id):
    try:
        # 使用独立事务获取订单数据
        with transaction.atomic():
            order = sinkingorder.objects.select_for_update().get(id=order_id)
            commodity = commodityinfo.objects.get(name=order.commodity)

            # 从映射文件获取道具编号
            item_number = ITEM_MAPPINGS.get(commodity.name)
            if not item_number:
                error_msg = f"商品 '{commodity.name}' 未找到对应的道具编号"
                raise ValueError(error_msg)

            # 准备请求参数
            headers = {
                'User-Agent': settings.EXTERNAL_API_USER_AGENT,
                'Cookie': settings.EXTERNAL_API_COOKIE,
                'Referer': settings.EXTERNAL_API_REFERER,
                'X-Requested-With': 'XMLHttpRequest'
            }

            data = {
                'sqm': settings.API_SECRET_KEY,
                'usr': order.player.account,
                'bao': '500001',  # 固定参数
                'num': commodity.num,
                'item': item_number,
                'items': '0',  # 固定参数
                'nums': '',  # 固定参数
                'quid': '1',  # 固定参数
                'gnxz': '2'  # 固定参数
            }

            # 发送请求到外部API
            print(f"开始发送道具请求，订单ID: {order_id}，参数: {data}")
            response = requests.post(
                settings.EXTERNAL_API_URL,
                headers=headers,
                data=data,
                timeout=30  # 设置超时时间
            )
            response.raise_for_status()

            # 检查响应内容
            if '发送成功' not in response.text:
                error_msg = f"外部API返回异常: {response.text}"
                raise requests.exceptions.RequestException(error_msg)

            print(f"道具发放成功，订单ID: {order_id}，响应: {response.text}")
            return True

    except Exception as e:
        print(f"道具发放失败，订单ID: {order_id}，错误: {str(e)}")
        self.retry(exc=e, countdown=60 * self.request.retries)

logger = get_task_logger(__name__)