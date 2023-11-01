import graphene
from .schemas.model_schema import ModelQuery, ModelMutation
from .schemas.profit_schema import ProfitQuery, ProfitMutation
from .schemas.expense_schema import ExpenseQuery, ExpenseMutation
from .schemas.replay_type_schema import ReplayTypeQuery


class Query(ModelQuery, ProfitQuery, ExpenseQuery, ReplayTypeQuery):
    pass

class Mutation(ModelMutation, ProfitMutation, ExpenseMutation):
    pass

schema = graphene.Schema(query = Query, mutation=Mutation)
