from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from datetime import timedelta

class productinfo(models.Model):
    category = models.CharField(max_length=100)

    def __str__(self):
        return f'<productinfo:{self.category}>'

class commodityinfo(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    num = models.IntegerField()
    details = models.TextField()
    commodity_image = models.ImageField(upload_to='products/%Y/%m/%d',  # 自动按日期生成目录
        verbose_name='商品图片')
    category_id = models.ForeignKey(productinfo, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class userinfo(models.Model):
    account = models.BigIntegerField(validators=[MinValueValidator(10000000000),  # 最小值
                                                 MaxValueValidator(199999999999)],unique=True)
    cdk = models.TextField(max_length=100)

class topupinfo(models.Model):
    player = models.ForeignKey(to='userinfo',to_field='account', on_delete=models.CASCADE)
    uptoday = models.IntegerField()
    uptotal = models.IntegerField()


class CDKActivation(models.Model):
    cdk = models.TextField(max_length=100)

    def __str__(self):
        return f'{self.account} - {self.status}'

# class sinkingorder(models.Model):
#     player = models.ForeignKey(to='userinfo',to_field='account', on_delete=models.CASCADE)
#     time = models.DateTimeField()
#     ordernumber = models.TextField(max_length=100)
#     state = models.BooleanField(default=False)
#     commodity = models.TextField(max_length=100)
#     zfbordernumber = models.TextField(max_length=100,default="0")


class sinkingorder(models.Model):
    player = models.ForeignKey(to='userinfo', to_field='account', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)  # 自动记录时间
    ordernumber = models.CharField(max_length=32, unique=True)  # 订单号字段
    state = models.BooleanField(default=False)
    commodity = models.CharField(max_length=100)  # 商品名称
    zfbordernumber = models.CharField(max_length=64, blank=True)  # 支付宝交易号
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 新增价格字段
    # 新增处理状态字段
    PROCESSING_STATUS = (
        (0, '未处理'),
        (1, '处理中'),
        (2, '已完成'),
        (3, '失败')
    )
    process_status = models.SmallIntegerField(choices=PROCESSING_STATUS, default=0)

    # 新增重试次数字段
    retry_count = models.IntegerField(default=0)

    # 新增错误日志字段
    error_log = models.TextField(blank=True)
    def __str__(self):
        return f"{self.ordernumber} - {self.commodity}"

class Meta:
    indexes = [
        models.Index(fields=['ordernumber']),
        models.Index(fields=['process_status']),
    ]

# Create your models here.
