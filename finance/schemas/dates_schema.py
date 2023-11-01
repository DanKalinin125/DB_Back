from datetime import timedelta

import graphene
from graphene_django import DjangoObjectType
from ..models import *
from .profit_schema import ProfitType
from .expense_schema import ExpenseType

class DateType(DjangoObjectType):
    """
    Структура даты модели
    """

    class Meta:
        model = Date
        fields = [f.name for f in Date._meta.fields]
        fields.remove("model")
        fields.append("profits")
        fields.append("expenses")

    profits = graphene.List(ProfitType)
    expenses = graphene.List(ExpenseType)

    def resolve_profits(self, info):
        return [d.profit for d in DateProfit.objects.filter(date = self)]

    def resolve_expenses(self, info):
        return [d.expense for d in DateExpense.objects.filter(date = self)]

def resolve_update_input_errors(comment, real_amount):
    """
    Валидация входных значений при обновлении даты
    """

    if not (comment == None) and (len(comment) > Date._meta.get_field('comment').max_length):
        raise Exception("Comment must be lower then " + str(Date._meta.get_field('comment').max_length))

    if (real_amount != None) and (real_amount < 0):
        raise Exception("real_amount must be above zero")

class UpdateDateMutation(graphene.Mutation):
    """
    Обновить комментарий и реальную сумму в дату по индексу
    """
    date = graphene.Field(DateType)

    class Arguments:
        date_id = graphene.ID(required=True)
        comment = graphene.String(required=False)
        real_amount = graphene.Float(required=False)

    @staticmethod
    def mutate(_, info, date_id, comment = None, real_amount = None):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        if not (Date.objects.get(id=date_id)): raise Exception("DateNotFound")
        if not (info.context.user == Date.objects.get(id=date_id).model.user): raise Exception("UserDoesNotHaveThisDate")

        resolve_update_input_errors(comment, real_amount)

        inst_date = Date.objects.get(id=date_id)
        update_fields = []
        all_field_none = True

        if not (comment == None):
            inst_date.comment = comment
            update_fields.append("comment")
            all_field_none = False

        if not (real_amount == None):
            inst_date.real_amount = real_amount
            update_fields.append("real_amount")
            all_field_none = False

        if (all_field_none) : raise Exception("AllFieldsIsNone")
        inst_date.save(update_fields = update_fields)

        return UpdateDateMutation(date = inst_date)


class DateQuery(graphene.ObjectType):
    model_dates = graphene.List(DateType, model_id=graphene.ID(required=True))  # Все даты модели

    def resolve_model_dates(self, info, model_id):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        if not (Model.objects.get(id=model_id)): raise Exception("ModelNotFound")
        if not (info.context.user == Model.objects.get(id=model_id).user): raise Exception("UserDoesNotHaveThisModel")

        return Date.objects.filter(model=Model.objects.get(id=model_id))

class DateMutation(UpdateDateMutation, graphene.ObjectType):
    update_date = UpdateDateMutation.Field()


schema = graphene.Schema(query = DateQuery, mutation=DateMutation)