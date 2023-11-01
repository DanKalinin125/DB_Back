import graphene
from graphene_django import DjangoObjectType
from ..models import *

class ReplayTypeNode(DjangoObjectType):
    class Meta:
        model = ReplayType
        fields = [f.name for f in ReplayType._meta.fields]

class ReplayTypeQuery(graphene.ObjectType):
    all_replay_types = graphene.List(ReplayTypeNode)

    def resolve_all_replay_types(self, info):
        if not(info.context.user.is_authenticated) : raise Exception("UserNotAuthenticated")
        return ReplayType.objects.all()

schema = graphene.Schema(query = ReplayTypeQuery)