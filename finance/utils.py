from .models import *
from datetime import timedelta
from dateutil.relativedelta import relativedelta

def update_profit_dates(profit):
    DateProfit.objects.filter(profit = profit).delete()

    #Формируем все даты дохода
    profit_dates = []
    replay_type = profit.replay_type
    if (replay_type.name == "Без повтора"):
        profit_dates.append(profit.start_date)
    else:
        days = 0
        months = 0
        years = 0
        if (replay_type.name == "Пользовательский"):
            days = profit.custom_replay_days
        else:
            days = replay_type.days
            months = replay_type.months
            years = replay_type.years
        date = profit.start_date
        while date < profit.finish_date + timedelta(days=1):
            profit_dates.append(date)
            date += relativedelta(days = days, months = months, years = years)

    #Ищем их соответствия в модели Date и добавляем элементы в DateProfit
    for date in profit_dates:
        if not (Date.objects.get(model = profit.model, date = date)): continue
        inst_date = Date.objects.get(model = profit.model, date = date)

        if (inst_date != None):
            date_profit = DateProfit(date = inst_date, profit = profit)
            date_profit.save()

def update_expense_dates(expense):
    DateExpense.objects.filter(expense = expense).delete()

    #Формируем все даты дохода
    expense_dates = []
    replay_type = expense.replay_type
    if (replay_type.name == "Без повтора"):
        expense_dates.append(expense.start_date)
    else:
        days = 0
        months = 0
        years = 0
        if (replay_type.name == "Пользовательский"):
            days = expense.custom_replay_days
        else:
            days = replay_type.days
            months = replay_type.months
            years = replay_type.years
        date = expense.start_date
        while date < expense.finish_date + timedelta(days=1):
            expense_dates.append(date)
            date += relativedelta(days = days, months = months, years = years)

    #Ищем их соответствия в модели Date и добавляем элементы в DateExpense
    for date in expense_dates:
        if not (Date.objects.get(model = expense.model, date = date)): continue
        inst_date = Date.objects.get(model = expense.model, date = date)

        if (inst_date != None):
            date_expense = DateExpense(date = inst_date, expense = expense)
            date_expense.save()

def update_model_dates(model):
    """
    Осуществляет пересчет сумм на каждую дату модели
    """
    model_dates = Date.objects.filter(model = model)

    for i in range(len(model_dates)):
        date = model_dates[i]

        sum_profits = 0
        for date_profit in DateProfit.objects.filter(date = date): sum_profits += date_profit.profit.amount

        sum_expenses = 0
        for date_expense in DateExpense.objects.filter(date = date): sum_expenses += date_expense.expense.amount

        if i == 0:
            date.amount = model.start_amount + sum_profits - sum_expenses
        else:
            date.amount = model_dates[i-1].amount + sum_profits - sum_expenses

        date.save(update_fields = ["amount"])