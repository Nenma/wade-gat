import json
import re
import os
import requests
import copy


# TODO: to be improved
def convert(prediction):
    parts = list(filter(None, re.split('|'.join(r'\b{}\b'.format(word) for word in ['SELECT', 'FROM', 'WHERE']), prediction)))
    parts = [part.strip() for part in parts]
    fields, query_type, condition = parts

    condition_string = ''
    # Check whether WHERE clause is present
    if condition != '':
        condition = condition.replace(' =', ':')
        condition = condition.replace("'", '\"')
        condition_string = '(' + condition + ')'

    
    return 'query { ' + query_type + condition_string + ' { ' + fields + ' } }'


def get_query_types_with_fields(query_types, name_to_type):
    query_and_fields = []
    for field in query_types:
        for key, value in name_to_type.items():
            if key.lower() == field['name'].lower() \
                or key.lower() + 's' == field['name'].lower() \
                or key.lower()[:-1] + 'ies' == field['name'].lower() \
                or 'all' + key.lower() == field['name'].lower() \
                or 'all' + key.lower() + 's' == field['name'].lower() \
                or 'all' + key.lower()[:-1] + 'ies' == field['name'].lower() \
                or 'get' + key.lower() == field['name'].lower() \
                or 'get' + key.lower() + 's' == field['name'].lower() \
                or 'get' + key.lower()[:-1] + 'ies' == field['name'].lower() \
                or 'getfuzzy' + key.lower() == field['name'].lower() \
                or 'getfuzzy' + key.lower() + 's' == field['name'].lower() \
                or 'getfuzzy' + key.lower()[:-1] + 'ies' == field['name'].lower() \
                or key.lower() in field['name'].lower():
                    value_copy = copy.copy(value)
                    value_copy['name'] = field['name']
                    query_and_fields.append(value_copy)

    return query_and_fields


def remove_duplicates(ex):
    new = []
    for elem in ex:
        if elem not in new:
            new.append(elem)
    return new


def save_schema(schema_name, schema_data):
    source = './Schemas/' + schema_name + '/schema.json'
    os.makedirs(os.path.dirname(source), exist_ok=True)
    location = open(source, 'w')
    json.dump(schema_data, location, indent=4)
    location.close()


def get_query_types(types):
    for type in types:
        if type['name'] == 'Query':
            return type['fields']


def save_simple_schema(schema_name):
    source = './Schemas/' + schema_name + '/'

    data = json.load(open(source + 'schema.json', 'r'))
    schema = data['data']['__schema']

    query_types = get_query_types(schema['types'])

    name_to_type = {}
    for type in schema['types']:
        if type['fields'] is not None and type['name'] != 'Query':
            name_to_type[type['name']] = type

    query_types_with_fields = get_query_types_with_fields(query_types, name_to_type)
    arguments = []
    for field in query_types:
        if field['args']:
            for arg in field['args']:
                arguments.append(arg)

    simpleSchema = {
        "types": remove_duplicates(list(query_types_with_fields)),
        "arguments": remove_duplicates(list(arguments))
    }

    os.makedirs(os.path.dirname(source + 'simpleSchema.json'), exist_ok=True)
    location = open(source + 'simpleSchema.json', 'w')
    json.dump(simpleSchema, location, indent=4)
    location.close()


def get_schema_name(graphql_api_url):
    result = re.findall(r'(\w+[\s\w]*)\b', graphql_api_url)
    return result[1]


def add_graphql_schema(graphql_api_url):
    query = """
        fragment FullType on __Type {
        kind
        name
        fields(includeDeprecated: true) {
            name
            args {
            ...InputValue
            }
            type {
            ...TypeRef
            }
            isDeprecated
            deprecationReason
        }
        inputFields {
            ...InputValue
        }
        interfaces {
            ...TypeRef
        }
        enumValues(includeDeprecated: true) {
            name
            isDeprecated
            deprecationReason
        }
        possibleTypes {
            ...TypeRef
        }
        }
        fragment InputValue on __InputValue {
        name
        type {
            ...TypeRef
        }
        defaultValue
        }
        fragment TypeRef on __Type {
        kind
        name
        ofType {
            kind
            name
            ofType {
            kind
            name
            ofType {
                kind
                name
                ofType {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                    }
                    }
                }
                }
            }
            }
        }
        }
        query IntrospectionQuery {
        __schema {
            queryType {
            name
            }
            mutationType {
            name
            }
            types {
            ...FullType
            }
            directives {
            name
            locations
            args {
                ...InputValue
            }
            }
        }
        }
    """

    result = requests.post(graphql_api_url, json={ 'query': query })
    json_result = json.loads(result.text)
    schema_name = get_schema_name(graphql_api_url)
    save_schema(schema_name, json_result)
    save_simple_schema(schema_name)
