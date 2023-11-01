from django.db import models
from users.models import User

class Model(models.Model):
    id = models.AutoField('Идентификатор модели', primary_key=True)
    user = models.ForeignKey(to=User, to_field='id', on_delete=models.CASCADE)
    name = models.CharField("Наименование модели", max_length=50, null=False)
    start_date = models.DateField("Дата начала моделирования", null=False)
    finish_date = models.DateField("Дата окончания моделирования", null=False)
    start_amount = models.FloatField("Сумма счета на начало моделирования", null=False)

class Date(models.Model):
    id = models.AutoField('Идентификатор записи', primary_key=True)
    model = models.ForeignKey(to=Model, to_field='id', on_delete=models.CASCADE)
    date = models.DateField('Дата', null=False)
    amount = models.FloatField('Сумма на указанную дату', null=False)
    real_amount = models.FloatField('Реальная сумма на указанную дату', null=True, blank=True)
    comment = models.CharField('Комментарий', max_length=100, null=True, blank=True)

class ReplayType(models.Model):
    id = models.AutoField('Идентификатор повтора', primary_key=True)
    name = models.CharField('Наименование повтора', max_length=50, null=False)
    days = models.IntegerField('Количество дней повторения', null=True, blank=True)
    months = models.IntegerField('Количество месяцев повторения', null=True, blank=True)
    years = models.IntegerField('Количество лет повторения', null=True, blank=True)

class Profit(models.Model):
    id = models.AutoField('Идентификатор дохода', primary_key=True)
    model = models.ForeignKey(to=Model, to_field='id', on_delete=models.CASCADE)
    name = models.CharField('Наименование дохода', max_length=50, null=False)
    start_date = models.DateField('Дата дохода', null=False)
    amount = models.FloatField('Сумма дохода', null=False)

    #Отсутствие replay_type говорит о неповторяющемся доходе
    replay_type = models.ForeignKey(to=ReplayType, to_field='id', on_delete=models.CASCADE, null=False, blank=False)
    custom_replay_days = models.IntegerField('Количество дней повторения для кастомного повтора', null=True, blank=True)
    finish_date = models.DateField('Дата окончания повтора', null=True, blank=True)

class Expense(models.Model):
    id = models.AutoField('Идентификатор расхода', primary_key=True)
    model = models.ForeignKey(to=Model, to_field='id', on_delete=models.CASCADE)
    name = models.CharField('Наименование расхода', max_length=50, null=False)
    start_date = models.DateField('Дата расхода', null=False)
    amount = models.FloatField('Сумма расхода', null=False)
    replay_type = models.ForeignKey(to=ReplayType, to_field='id', on_delete=models.CASCADE, null=True, blank=True)
    custom_replay_days = models.IntegerField('Количество дней повторения для кастомного повтора', null=True, blank=True)
    finish_date = models.DateField('Дата окончания повтора', null=True, blank=True)

class DateProfit(models.Model):
    date = models.ForeignKey(to=Date, to_field='id', on_delete=models.CASCADE)
    profit = models.ForeignKey(to=Profit, to_field='id', on_delete=models.CASCADE)

class DateExpense(models.Model):
    date = models.ForeignKey(to=Date, to_field='id', on_delete=models.CASCADE)
    expense = models.ForeignKey(to=Expense, to_field='id', on_delete=models.CASCADE)

