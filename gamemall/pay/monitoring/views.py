from django.http import JsonResponse
from django.views import View
from django.conf import settings
import redis
import logging

logger = logging.getLogger(__name__)


def get_celery_queue_length():
    """获取Celery队列长度"""
    try:
        # 使用配置信息连接Redis
        r = redis.Redis(
            host=settings.CELERY_BROKER_HOST,
            port=settings.CELERY_BROKER_PORT,
            db=settings.CELERY_BROKER_DB,
            password=settings.CELERY_BROKER_PASSWORD,
            socket_timeout=3  # 设置超时时间
        )

        # 获取默认队列长度（可根据需要修改队列名称）
        queue_name = settings.CELERY_DEFAULT_QUEUE
        return r.llen(queue_name)
    except redis.RedisError as e:
        logger.error(f"Redis连接失败: {str(e)}")
        return -1  # 返回-1表示获取失败
    except Exception as e:
        logger.error(f"获取队列长度异常: {str(e)}")
        return -1


class PaymentStatusView(View):
    def get(self, request):
        return JsonResponse({
            'status': 'ok',
            'queue_size': get_celery_queue_length(),
            'queue_name': settings.CELERY_DEFAULT_QUEUE
        })