from flask import Flask, request, jsonify
from ariadne import graphql_sync, make_executable_schema, gql, load_schema_from_path
from ariadne.constants import PLAYGROUND_HTML
from ariadne.asgi import GraphQL
from models import query, mutation, setup_db
from flask_cors import CORS

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    type_defs = gql(load_schema_from_path("./schema.graphql"))
    schema = make_executable_schema(type_defs, query, mutation)
    
    @app.route("/graphql", methods=["GET"])
    def graphql_playground():
        return PLAYGROUND_HTML, 200
    
    @app.route("/graphql", methods=["POST"])
    def graphql_server():
        data = request.get_json()
        success, result = graphql_sync(schema, data, context_value={"request": request})
        status_code = 200 if success else 400
        return jsonify(result), status_code
    #when using a function to build the app, we must return the app
    return app

app = create_app()

if __name__=='__main__':
    app.run()