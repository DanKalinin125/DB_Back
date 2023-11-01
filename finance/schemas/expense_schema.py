import graphene
from graphene_django import DjangoObjectType
from ..models import *
from ..utils import update_expense_dates, update_model_dates
from .replay_type_schema import ReplayTypeNode

class ExpenseType(DjangoObjectType):
    class Meta:
        model = Expense
        fields = [f.name for f in Expense._meta.fields]
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
                raise Exception("For none replay expense finish_date must be None")
            if (custom_replay_days != None):
                raise Exception("For none replay expense custom_replay_days must be None")

        else:
            if (finish_date == None):
                raise Exception("finish_date cannot be None")
            else:
                if (finish_date < start_date):
                    raise Exception("finish_date must be before a start_date")

            if (custom_replay_days != None):
                raise Exception("For none replay expense custom_replay_days must be None")

def resolve_input_errors(name, amount):

    if (name != None) and len(name) > Model._meta.get_field('name').max_length:
        raise Exception("Name must be lower then " + str(Model._meta.get_field('name').max_length))

    if (amount != None) and amount < 0:
        raise Exception("amount must be above or equals zero")

#Создание новой модели
class CreateExpenseMutation(graphene.Mutation):
    """
    Создать новый расход
    """

    expense = graphene.Field(ExpenseType)

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

        inst_expense = Expense(model=Model.objects.get(id=model_id), name=name, start_date=start_date, amount=amount, replay_type = ReplayType.objects.get(id = replay_type_id), custom_replay_days = custom_replay_days, finish_date = finish_date)
        inst_expense.save()

        #Обновление модели DateExpense
        update_expense_dates(inst_expense)

        #Обновление модели Date
        update_model_dates(inst_expense.model)

        return CreateExpenseMutation(expense = inst_expense)

class UpdateExpenseMutation(graphene.Mutation):
    """
    Обновить данные расхода по индексу
    """

    expense = graphene.Field(ExpenseType)

    class Arguments:
        expense_id = graphene.ID(required=True)
        name = graphene.String(required=False)
        start_date = graphene.Date(required=False)
        amount = graphene.Float(required=False)
        replay_type_id = graphene.ID(required=False)
        custom_replay_days = graphene.Int(required=False)
        finish_date = graphene.Date(required=False)

    @staticmethod
    def mutate(_, info, expense_id, name = None, start_date = None, amount = None, replay_type_id = None, custom_replay_days = None,
               finish_date = None):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        if not (Expense.objects.get(id=expense_id)): raise Exception("ExpenseNotFound")
        if not (info.context.user == Expense.objects.get(id=expense_id).model.user): raise Exception("UserDoesNotHaveThisExpense")

        resolve_input_errors(name, amount)

        inst_expense = Expense.objects.get(id=expense_id)
        update_fields = []
        all_field_none = True

        if not (name == None):
            inst_expense.name = name
            update_fields.append("name")
            all_field_none = False

        if not (start_date == None):
            inst_expense.start_date = start_date
            update_fields.append("start_date")
            all_field_none = False

        if not (amount == None):
            inst_expense.amount = amount
            update_fields.append("amount")
            all_field_none = False

        if not (replay_type_id == None):
            if not (ReplayType.objects.get(id=replay_type_id)): raise Exception("ReplayTypeNotFound")

            new_replay_type = ReplayType.objects.get(id=replay_type_id)
            inst_expense.replay_type = new_replay_type
            update_fields.append("replay_type")
            all_field_none = False

            if (new_replay_type.name == "Без повтора"):
                inst_expense.custom_replay_days = None
                update_fields.append("custom_replay_days")

                inst_expense.finish_date = None
                update_fields.append("finish_date")

            else:
                if (new_replay_type.name == "Пользовательский"):
                    if (inst_expense.custom_replay_days == None):
                        if (custom_replay_days == None): raise Exception("custom_replay_days cannot be None")
                        if (custom_replay_days < 1): raise Exception("custom_replay_days must be above zero")

                        inst_expense.custom_replay_days = custom_replay_days
                        update_fields.append("custom_replay_days")

                    if (inst_expense.finish_date == None):
                        if (finish_date == None): raise Exception("finish_date cannot be None")
                        if not (inst_expense.start_date < finish_date): raise Exception("finish_date must be after start_date")

                        inst_expense.finish_date = finish_date
                        update_fields.append("finish_date")
                else:
                    inst_expense.custom_replay_days = None
                    update_fields.append("custom_replay_days")

                    if (inst_expense.finish_date == None):
                        if (finish_date == None): raise Exception("finish_date cannot be None")
                        if not (inst_expense.start_date < finish_date): raise Exception("finish_date must be after start_date")

                        inst_expense.finish_date = finish_date
                        update_fields.append("finish_date")
        else:
            if not (custom_replay_days == None):
                if (inst_expense.replay_type.name != "Пользовательский"): raise Exception("custom_replay_days must be None")
                if (custom_replay_days < 1): raise Exception("custom_replay_days must be above zero")

                inst_expense.custom_replay_days = custom_replay_days
                update_fields.append("custom_replay_days")
                all_field_none = False

            if not (finish_date == None):
                if (inst_expense.replay_type.name == "Без повтора"): raise Exception("finish_date must be None")
                if not (inst_expense.start_date < finish_date): raise Exception("finish_date must be after start_date")

                inst_expense.finish_date = finish_date
                update_fields.append("finish_date")
                all_field_none = False

        if (all_field_none): raise Exception("AllFieldsIsNone")
        inst_expense.save(update_fields=update_fields)

        # Обновление модели DateExpense
        update_expense_dates(inst_expense)

        # Обновление модели Date
        update_model_dates(inst_expense.model)

        return UpdateExpenseMutation(expense = inst_expense)

class DeleteExpenseMutation(graphene.Mutation):
    """
    Удалить расход по индексу
    """
    all_expenses = graphene.List(ExpenseType)

    class Arguments:
        expense_id = graphene.ID(required=True)

    @staticmethod
    def mutate(_, info, expense_id):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        if not (Expense.objects.get(id=expense_id)): raise Exception("ExpenseNotFound")
        if not (info.context.user == Expense.objects.get(id=expense_id).model.user): raise Exception("UserDoesNotHaveThisExpense")
        model = Expense.objects.get(id=expense_id).model

        Expense.objects.get(id=expense_id).delete()
        update_model_dates(model)

        return DeleteExpenseMutation(Expense.objects.filter(model=model))


class ExpenseQuery(graphene.ObjectType):
    model_expenses = graphene.List(ExpenseType, model_id=graphene.ID(required=True))
    expense =  graphene.Field(ExpenseType, expense_id=graphene.ID(required=True))

    def resolve_model_expenses(self, info, model_id):
        if not (info.context.user.is_authenticated) : raise Exception("UserNotAuthenticated")
        if not (Model.objects.get(id=model_id)): raise Exception("ModelNotFound")
        if not (info.context.user == Model.objects.get(id=model_id).user): raise Exception("UserDoesNotHaveThisModel")
        return Expense.objects.filter(model = model_id)

    def resolve_expense(self, info, expense_id):
        if not (info.context.user.is_authenticated): raise Exception("UserNotAuthenticated")
        if not (Expense.objects.get(id=expense_id)): raise Exception("ExpenseNotFound")
        if not (info.context.user == Expense.objects.get(id=expense_id).model.user): raise Exception("UserDoesNotHaveThisExpense")
        return Expense.objects.get(id = expense_id)

class ExpenseMutation(CreateExpenseMutation, UpdateExpenseMutation, DeleteExpenseMutation, graphene.ObjectType):
    create_expense = CreateExpenseMutation.Field()
    update_expense = UpdateExpenseMutation.Field()
    delete_expense = DeleteExpenseMutation.Field()

schema = graphene.Schema(query = ExpenseQuery, mutation=ExpenseMutation)