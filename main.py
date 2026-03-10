from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from schema import schema
import uvicorn

app = FastAPI(title="CRM GraphQL API")

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def index():
    return {"message": "CRM GraphQL API is running. Go to /graphql for the interface."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)
