from flask import Flask, request
import os
import requests
import json
import util
import main

app = Flask(__name__)


@app.get('/')
def home():
    return 'Welcome to WADe GAT!'


@app.post('/prediction')
def calculate_prediction():
    if request.is_json:
        data = request.get_json()

        question = data['question']
        graphql_api_url = data['graphql_api_url']

        schema_name = util.get_schema_name(graphql_api_url)
        if not os.path.isdir('Schemas/' + schema_name):
            util.add_graphql_schema(graphql_api_url)

        model = main.prepare_model()
        input_string = main.prepare_input_string(question, schema_name)
        prediction = main.calculate_output(model, input_string)
        predicted_query = util.convert(prediction)

        return predicted_query, 200

    return { 'error': 'Request must be JSON' }, 415


# TODO: to be tested
@app.post('/graphqlResponse')
def send_graphql_query():
    if request.is_json:
        data = request.get_json()

        query = data['query']
        graphql_api_url = data['graphql_api_url']

        result = requests.post(graphql_api_url, json={ 'query': query })
        json_result = json.loads(result.text)

        return json_result, 200

    return { 'error': 'Request must be JSON' }, 415
