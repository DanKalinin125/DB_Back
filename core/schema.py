import graphene

import finance.schema as first_app
import users.schema as second_app

class Query(first_app.schema.Query, second_app.schema.Query, graphene.ObjectType):
    # Inherits all classes and methods from app-specific queries, so no need
    # to include additional code here.
    pass

class Mutation(first_app.schema.Mutation, second_app.schema.Mutation, graphene.ObjectType):
    # Inherits all classes and methods from app-specific mutations, so no need
    # to include additional code here.
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)