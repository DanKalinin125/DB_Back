import graphene
from graphene_django import DjangoObjectType
from ..models import *
from ..utils import update_profit_dates, update_model_dates
from .replay_type_schema import ReplayTypeNode

class ProfitType(DjangoObjectType):
    class Meta:
        model = Profit
        fields = [f.name for f in Profit._meta.fields]
        fields.remove("model")

def check_new_replay_type(start_date, replay_type_id, custom_replay_days, finish_date):
    if not (ReplayType.objects.get(id=replay_type_id)): raise Exception("ReplayTypeNotFound")

    if (ReplayType.objects.get(id=replay_type_id).name == "Пользовательский"):
        if (finish_date == None):
            raise Exception("finish_date cannot be None")
        else:
            if (finish_date < start_date):
                raise Exception("finish_date must be before a start_date")

        if (custom_replay_days == None):
            raise Exception("custom_replay_days cannot be None")
        if (custom_replay_days < 1):
            raise Exception("custom_replay_days must be above zero")

    else:
        if (ReplayType.objects.get(id=replay_type_id).name == "Без повтора"):
            if (finish_date != None):
                raise Exception("For none replay profits finish_date must be None")
            if (custom_replay_days != None):
                raise Exception("For none replay profits custom_replay_days must be None")

        else:
            if (finish_date == None):
                raise Exception("finish_date cannot be None")
            else:
                if (finish_date < start_date):
                    raise Exception("finish_date must be before a start_date")

            if (custom_replay_days != None):
                raise Exception("For none replay profits custom_replay_days must be None")

def resolve_input_errors(name, amount):

    if (name != None) and len(name) > Model._meta.get_field('name').max_length:
        raise Exception("Name must be lower then " + str(Model._meta.get_field('name').max_length))

    if (amount != None) and amount < 0:
        raise Exception("amount must be above or equals zero")

#Создание новой модели
class CreateProfitMutation(graphene.Mutation):
    """
    Создать новый доход
    """

    profit = graphene.Field(ProfitType)

    class Arguments:
        model_id = graphene.ID(required=True)
        name = graphene.String(required=True)
        start_date = graphene.Date(required=True)
        amount = graphene.Float(required=True)
        replay_type_id = graphene.ID(required=True)
        custom_replay_days = graphene.Int(required=False)
        finish_date = graphene.Date(required=False)

    @staticmethod
    def mutate(_, info, model_id, name, start_date, amount, replay_type_id, custom_replay_days = None, finish_date = None):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        if not (Model.objects.get(id=model_id)): raise Exception("ModelNotFound")
        if not (info.context.user == Model.objects.get(id=model_id).user): raise Exception("UserDoesNotHaveThisModel")

        resolve_input_errors(name, amount)
        check_new_replay_type(start_date, replay_type_id, custom_replay_days, finish_date)

        inst_profit = Profit(model=Model.objects.get(id=model_id), name=name, start_date=start_date, amount=amount, replay_type = ReplayType.objects.get(id = replay_type_id), custom_replay_days = custom_replay_days, finish_date = finish_date)
        inst_profit.save()

        #Обновление модели DateProfit
        update_profit_dates(inst_profit)

        #Обновление модели Date
        update_model_dates(inst_profit.model)

        return CreateProfitMutation(profit = inst_profit)

class UpdateProfitMutation(graphene.Mutation):
    """
    Обновить данные дохода по индексу
    """
    profit = graphene.Field(ProfitType)

    class Arguments:
        profit_id = graphene.ID(required=True)
        name = graphene.String(required=False)
        start_date = graphene.Date(required=False)
        amount = graphene.Float(required=False)
        replay_type_id = graphene.ID(required=False)
        custom_replay_days = graphene.Int(required=False)
        finish_date = graphene.Date(required=False)

    @staticmethod
    def mutate(_, info, profit_id, name = None, start_date = None, amount = None, replay_type_id = None, custom_replay_days = None,
               finish_date = None):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        if not (Profit.objects.get(id=profit_id)): raise Exception("ProfitNotFound")
        if not (info.context.user == Profit.objects.get(id=profit_id).model.user): raise Exception("UserDoesNotHaveThisProfit")

        resolve_input_errors(name, amount)

        inst_profit = Profit.objects.get(id=profit_id)
        update_fields = []
        all_field_none = True

        if not (name == None):
            inst_profit.name = name
            update_fields.append("name")
            all_field_none = False

        if not (start_date == None):
            inst_profit.start_date = start_date
            update_fields.append("start_date")
            all_field_none = False

        if not (amount == None):
            inst_profit.amount = amount
            update_fields.append("amount")
            all_field_none = False

        if not (replay_type_id == None):
            if not (ReplayType.objects.get(id=replay_type_id)): raise Exception("ReplayTypeNotFound")

            new_replay_type = ReplayType.objects.get(id=replay_type_id)
            inst_profit.replay_type = new_replay_type
            update_fields.append("replay_type")
            all_field_none = False

            if (new_replay_type.name == "Без повтора"):
                inst_profit.custom_replay_days = None
                update_fields.append("custom_replay_days")

                inst_profit.finish_date = None
                update_fields.append("finish_date")

            else:
                if (new_replay_type.name == "Пользовательский"):
                    if (inst_profit.custom_replay_days == None):
                        if (custom_replay_days == None): raise Exception("custom_replay_days cannot be None")
                        if (custom_replay_days < 1): raise Exception("custom_replay_days must be above zero")

                        inst_profit.custom_replay_days = custom_replay_days
                        update_fields.append("custom_replay_days")

                    if (inst_profit.finish_date == None):
                        if (finish_date == None): raise Exception("finish_date cannot be None")
                        if not (inst_profit.start_date < finish_date): raise Exception("finish_date must be after start_date")

                        inst_profit.finish_date = finish_date
                        update_fields.append("finish_date")
                else:
                    inst_profit.custom_replay_days = None
                    update_fields.append("custom_replay_days")

                    if (inst_profit.finish_date == None):
                        if (finish_date == None): raise Exception("finish_date cannot be None")
                        if not (inst_profit.start_date < finish_date): raise Exception("finish_date must be after start_date")

                        inst_profit.finish_date = finish_date
                        update_fields.append("finish_date")
        else:
            if not (custom_replay_days == None):
                if (inst_profit.replay_type.name != "Пользовательский"): raise Exception("custom_replay_days must be None")
                if (custom_replay_days < 1): raise Exception("custom_replay_days must be above zero")

                inst_profit.custom_replay_days = custom_replay_days
                update_fields.append("custom_replay_days")
                all_field_none = False

            if not (finish_date == None):
                if (inst_profit.replay_type.name == "Без повтора"): raise Exception("finish_date must be None")
                if not (inst_profit.start_date < finish_date): raise Exception("finish_date must be after start_date")

                inst_profit.finish_date = finish_date
                update_fields.append("finish_date")
                all_field_none = False

        if (all_field_none): raise Exception("AllFieldsIsNone")
        inst_profit.save(update_fields=update_fields)

        # Обновление модели DateProfit
        update_profit_dates(inst_profit)

        # Обновление модели Date
        update_model_dates(inst_profit.model)

        return UpdateProfitMutation(profit=inst_profit)

class DeleteProfitMutation(graphene.Mutation):
    """
    Удалить доход по индексу
    """

    all_profits = graphene.List(ProfitType)

    class Arguments:
        profit_id = graphene.ID(required=True)

    @staticmethod
    def mutate(_, info, profit_id):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        if not (Profit.objects.get(id=profit_id)): raise Exception("ProfitNotFound")
        if not (info.context.user == Profit.objects.get(id=profit_id).model.user): raise Exception("UserDoesNotHaveThisProfit")
        model = Profit.objects.get(id=profit_id).model

        Profit.objects.get(id=profit_id).delete()
        update_model_dates(model)

        return DeleteProfitMutation(Profit.objects.filter(model=model))


class ProfitQuery(graphene.ObjectType):
    model_profits = graphene.List(ProfitType, model_id=graphene.ID(required=True))
    profit =  graphene.Field(ProfitType, profit_id=graphene.ID(required=True))

    def resolve_model_profits(self, info, model_id):
        if not (info.context.user.is_authenticated) : raise Exception("UserNotAuthenticated")
        if not (Model.objects.get(id=model_id)): raise Exception("ModelNotFound")
        if not (info.context.user == Model.objects.get(id=model_id).user): raise Exception("UserDoesNotHaveThisModel")
        return Profit.objects.filter(model = model_id)

    def resolve_profit(self, info, profit_id):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        if not (Profit.objects.get(id=profit_id)): raise Exception("ProfitNotFound")
        if not (info.context.user == Profit.objects.get(id=profit_id).model.user): raise Exception("UserDoesNotHaveThisProfit")
        return Profit.objects.get(id = profit_id)

class ProfitMutation(CreateProfitMutation, UpdateProfitMutation, DeleteProfitMutation, graphene.ObjectType):
    create_profit = CreateProfitMutation.Field()
    update_profit = UpdateProfitMutation.Field()
    delete_profit = DeleteProfitMutation.Field()

schema = graphene.Schema(query = ProfitQuery, mutation=ProfitMutation)