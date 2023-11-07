from datetime import timedelta

import graphene
from graphene_django import DjangoObjectType
from ..models import *
from .profit_schema import ProfitType
from ..utils import update_profit_dates, update_expense_dates, update_model_dates

#Модели
class ModelType(DjangoObjectType):
    """
    Структура модели
    """
    class Meta:
        model = Model
        fields = [f.name for f in Model._meta.fields]

def resolve_create_input_errors(name, start_date, finish_date, start_amount):
    """
    Валидация входных значений при создании модели
    """

    if (len(name) > Model._meta.get_field('name').max_length):
        raise Exception("Name must be lower then " + str(Model._meta.get_field('name').max_length))

    if (finish_date < start_date):
        raise Exception("finish_date must be before a start_date")

    if (start_amount < 0):
        raise Exception("start_amount must be above zero")

def resolve_update_input_errors(model, name, start_date, finish_date, start_amount):
    """
    Валидация входных значений при обновлении модели
    """

    if not (name == None) and (len(name) > Model._meta.get_field('name').max_length):
        raise Exception("Name must be lower then " + str(Model._meta.get_field('name').max_length))

    if (finish_date != None):
        if (start_date != None):
            if (finish_date < start_date): raise Exception("finish_date must be before a start_date")
        else:
            if (finish_date < model.start_date): raise Exception("finish_date must be before a start_date")
    else:
        if (start_date != None):
            if (model.finish_date < start_date): raise Exception("finish_date must be before a start_date")

    if (start_amount != None) and (start_amount < 0):
        raise Exception("start_amount must be above zero")


class CreateModelMutation(graphene.Mutation):
    """
    Создать новую модель
    """
    model = graphene.Field(ModelType)

    class Arguments:
        name = graphene.String(required=True)
        start_date = graphene.Date(required=True)
        finish_date = graphene.Date(required=True)
        start_amount = graphene.Float(required=True)

    @staticmethod
    def mutate(_, info, name, start_date, finish_date, start_amount):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")

        resolve_create_input_errors(name, start_date, finish_date, start_amount)
        inst_model = Model(user = info.context.user, name = name, start_date = start_date, finish_date = finish_date, start_amount = start_amount)
        inst_model.save()

        #Создание записей с датами
        date = start_date
        while date < finish_date + timedelta(days=1):
            new_date = Date(model = inst_model, date = date, amount = start_amount)
            new_date.save()
            date += timedelta(days=1)

        return CreateModelMutation(model = inst_model)


def find_date_in_array_from_model_Date(date, dates):
    """
    Находит нужный объект модели Date из массива
    """
    for inst_date in dates:
        if (inst_date.date == date):
            return inst_date
    return None


class UpdateModelMutation(graphene.Mutation):
    """
    Обновить данные модели по индексу
    """
    model = graphene.Field(ModelType)

    class Arguments:
        model_id = graphene.ID(required=True)
        name = graphene.String(required=False)
        start_date = graphene.Date(required=False)
        finish_date = graphene.Date(required=False)
        start_amount = graphene.Float(required=False)

    @staticmethod
    def mutate(_, info, model_id, name = None, start_date = None, finish_date = None, start_amount = None):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        if not (Model.objects.get(id=model_id)): raise Exception("ModelNotFound")
        if not (info.context.user == Model.objects.get(id=model_id).user): raise Exception("UserDoesNotHaveThisModel")

        resolve_update_input_errors(Model.objects.get(id=model_id), name, start_date, finish_date, start_amount)
        inst_model = Model.objects.get(id=model_id)
        update_fields = []
        all_field_none = True

        if not (name == None):
            inst_model.name = name
            update_fields.append("name")
            all_field_none = False
        if not (start_date == None):
            inst_model.start_date = start_date
            update_fields.append("start_date")
            all_field_none = False
        if not (finish_date == None):
            inst_model.finish_date = finish_date
            update_fields.append("finish_date")
            all_field_none = False
        if not (start_amount == None):
            inst_model.start_amount = start_amount
            update_fields.append("start_amount")
            all_field_none = False

        if (all_field_none) : raise Exception("AllFieldsIsNone")
        inst_model.save(update_fields = update_fields)

        #Удаляем все старые значения и записываем их в переменную
        old_dates = list(Date.objects.filter(model = inst_model))
        Date.objects.filter(model = inst_model).delete()

        #Записываем новые значения
        date = inst_model.start_date
        while date < inst_model.finish_date + timedelta(days=1):
            old_date = find_date_in_array_from_model_Date(date, old_dates)
            if (old_date != None):
                new_date = Date(id=old_date.id, model=inst_model, date=date, amount=inst_model.start_amount, real_amount = old_date.real_amount, comment = old_date.comment)
                new_date.save()
            else:
                new_date = Date(model=inst_model, date=date, amount=inst_model.start_amount)
                new_date.save()
            date += timedelta(days=1)

        for profit in Profit.objects.filter(model = inst_model):
            update_profit_dates(profit)

        for expense in Expense.objects.filter(model = inst_model):
            update_expense_dates(expense)

        update_model_dates(inst_model)

        return UpdateModelMutation(model = inst_model)

#Обновление модели
class DeleteModelMutation(graphene.Mutation):
    """
    Удалить модель по индексу
    """
    all_models = graphene.List(ModelType)

    class Arguments:
        model_id = graphene.ID(required=True)

    @staticmethod
    def mutate(_, info, model_id):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        if not (Model.objects.get(id=model_id)): raise Exception("ModelNotFound")
        if not (info.context.user == Model.objects.get(id=model_id).user): raise Exception("UserDoesNotHaveThisModel")

        Model.objects.get(id=model_id).delete()

        return DeleteModelMutation(Model.objects.filter(user = info.context.user))


class ModelQuery(graphene.ObjectType):
    all_models = graphene.List(ModelType)
    model = graphene.Field(ModelType, model_id=graphene.ID(required=True)) #Модель пользователя по идентификатору

    def resolve_all_models(self, info):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        return Model.objects.filter(user=info.context.user)

    def resolve_model(self, info, model_id):
        if not (info.context.user.is_authenticated) : raise Exception("UserNotAuthenticated")
        if not (Model.objects.get(id=model_id)): raise Exception("ModelNotFound")
        if not (info.context.user == Model.objects.get(id=model_id).user): raise Exception("UserDoesNotHaveThisModel")
        return Model.objects.get(id=model_id)

class ModelMutation(CreateModelMutation, UpdateModelMutation, DeleteModelMutation, graphene.ObjectType):
    create_model = CreateModelMutation.Field()
    update_model = UpdateModelMutation.Field()
    delete_model = DeleteModelMutation.Field()

schema = graphene.Schema(query = ModelQuery, mutation=ModelMutation)