from flask import Flask, request
from flask_cors import CORS
import os
import requests
import json
import util
import main

app = Flask(__name__)
CORS(app)


@app.get('/')
def home():
    return 'Welcome to WADe GAT!'


@app.post('/question')
def send_question():
    if request.is_json:
        data = request.get_json()

        question = data['question']
        graphql_api_url = data['graphql_api_url']

        schema_name = util.get_schema_name(graphql_api_url)
        if not os.path.isdir('Schemas/' + schema_name):
            util.add_graphql_schema(graphql_api_url)

        location = open('temp.json', 'w')
        json.dump({ "question": question, "schema": schema_name }, location, indent=4)
        location.close()

        return 'Successfully sent!', 200

    return { 'error': 'Request must be JSON' }, 415


@app.get('/prediction')
def get_prediction():
    temp = json.load(open('temp.json', 'r'))
    question = temp['question']
    schema_name = temp['schema']

    model = main.prepare_model()
    input_string = main.prepare_input_string(question, schema_name)
    prediction = main.calculate_output(model, input_string)
    predicted_query = util.convert(prediction)

    return predicted_query, 200


@app.post('/predictedQuery')
def send_graphql_query():
    if request.is_json:
        data = request.get_json()

        query = data['query']
        graphql_api_url = data['graphql_api_url']

        location = open('temp.json', 'w')
        json.dump({ "query": query, "graphql_api_url": graphql_api_url }, location, indent=4)
        location.close()

        return 'Successfully sent!', 200

    return { 'error': 'Request must be JSON' }, 415


@app.get('/response')
def get_grahpql_response():
    temp = json.load(open('temp.json', 'r'))
    query = temp['query']
    graphql_api_url = temp['graphql_api_url']

    result = requests.post(graphql_api_url, json={ 'query': query })
    json_result = json.loads(result.text)

    return json_result, 200
