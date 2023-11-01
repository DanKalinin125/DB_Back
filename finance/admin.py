from django.contrib import admin
from .models import *

admin.site.register(Model)
admin.site.register(Date)
admin.site.register(ReplayType)
admin.site.register(Profit)
admin.site.register(Expense)
admin.site.register(DateProfit)
admin.site.register(DateExpense)

