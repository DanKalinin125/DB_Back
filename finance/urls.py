from django.urls import path
from graphene_django.views import GraphQLView
from finance.schemas.model_schema import schema as model_schema
from finance.schemas.profit_schema import schema as profit_schema
from finance.schemas.expense_schema import schema as expense_schema
from finance.schemas.dates_schema import schema as date_schema

from finance.schemas.replay_type_schema import schema as replay_type_schema
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('models', csrf_exempt(GraphQLView.as_view(graphiql=False, schema=model_schema))),
    path('profits', csrf_exempt(GraphQLView.as_view(graphiql=False, schema=profit_schema))),
    path('expenses', csrf_exempt(GraphQLView.as_view(graphiql=False, schema=expense_schema))),
    path('replays', csrf_exempt(GraphQLView.as_view(graphiql=False, schema=replay_type_schema))),
    path('dates', csrf_exempt(GraphQLView.as_view(graphiql=False, schema=date_schema))),
]