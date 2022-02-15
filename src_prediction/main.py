import torch
import json
from functools import reduce
from t5_multi_sp_model import T5MultiSPModel
from util import convert

torch.manual_seed(0)


def prepare_model():
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    model = T5MultiSPModel.load_from_checkpoint('./models/after-finetunning.ckpt')

    model.task = 'finetune'
    model.prepare_data()
    model.to(device)

    return model


def prepare_input_string(question, schema):
    with open('./Schemas/' + schema + '/simpleSchema.json', 'r', encoding='utf-8') as s:
        # with open('./SPEGQL Datasets/SPEGQL-dataset/Schemas/' + schema + '/simpleSchema.json', 'r', encoding='utf-8') as s:
        data = json.load(s)

        type_field_tokens = [['<t>'] + [t['name']] + ['{'] + [f['name'] for f in t['fields']] + ['}'] + ['</t>'] for t
                             in data['types']]
        type_field_flat_tokens = reduce(list.__add__, type_field_tokens)

        arguments = [a['name'] for a in data['arguments']]
        schema_tokens = type_field_flat_tokens + ['<a>'] + arguments + ['</a>']

    return 'translate English to GraphQL: ' + question + ' ' + ' '.join(schema_tokens) + ' </s>'


def calculate_output(model, input_string):
    inputs = model.tokenizer.batch_encode_plus([input_string], max_length=1024, return_tensors='pt')['input_ids']
    generated_ids = model.model.generate(inputs, num_beams=5, repetition_penalty=1.0, max_length=56,
                                         early_stopping=True)
    hyps = [model.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in
            generated_ids]

    return hyps[0]


def main():
    print('Preparing model...', end='')
    model = prepare_model()
    print('DONE')

    question = "What is the name of the continent with the 'OC' code?"
    schema = 'countries'
    input_string = prepare_input_string(question, schema)
    prediction = calculate_output(model, input_string)

    print(prediction)

    # convert(question, prediction)


if __name__ == '__main__':
    main()
