from django.contrib import admin
from .models import productinfo, commodityinfo, userinfo, topupinfo, CDKActivation, sinkingorder

# 注册所有模型
admin.site.register(productinfo)
admin.site.register(commodityinfo)
admin.site.register(userinfo)
admin.site.register(topupinfo)
admin.site.register(CDKActivation)
admin.site.register(sinkingorder)