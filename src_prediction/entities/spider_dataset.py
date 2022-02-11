from torch.utils.data import Dataset
import json
import itertools


class SpiderDataset(Dataset):
  'Characterizes a dataset for PyTorch'
  def __init__(self, tokenizer, type_path='train_spider.json', block_size=102):
        'Initialization'
        super(SpiderDataset, ).__init__()
        self.tokenizer = tokenizer

        self.source = []
        self.target = []
        spider_path = './SPEGQL Datasets/spider/'
        path = spider_path + type_path

        tables_path = spider_path + 'tables.json'

        with open(path, 'r', encoding='utf-8') as f, open(tables_path, 'r', encoding='utf-8') as t:
          databases = json.load(t)
          data = json.load(f)

          grouped_dbs = {}
          for db in databases:
            grouped_dbs[db['db_id']] = db

          for element in data:
            db = grouped_dbs[element['db_id']]

            db_tables = db['table_names_original']

            tables_with_columns = ''
            for table_id, group in itertools.groupby(db['column_names_original'], lambda x: x[0]):
              if table_id == -1:
                continue

              columns_names = " ".join([column_name[1] for column_name in group ])
              tables_with_columns += '<t> ' + db_tables[table_id] + ' <c> ' + columns_names + ' </c> ' + '</t> '

            db_with_question = 'translate English to SQL: ' + element['question'] + ' ' + tables_with_columns + '</s>'

            tokenized_s = tokenizer.batch_encode_plus([db_with_question],max_length=1024, padding='max_length', truncation=True,return_tensors='pt')
            self.source.append(tokenized_s)

            tokenized_t = tokenizer.batch_encode_plus([element['query'] + ' </s>'],max_length=block_size, padding='max_length', truncation=True,return_tensors='pt')
            self.target.append(tokenized_t)


  def __len__(self):
        'Denotes the total number of samples'
        return len(self.source)

  def __getitem__(self, index):
        'Generates one sample of data'
        source_ids = self.source[index]['input_ids'].squeeze()
        target_ids = self.target[index]['input_ids'].squeeze()
        src_mask = self.source[index]['attention_mask'].squeeze()
        return { 'source_ids': source_ids,
                'source_mask': src_mask,
                'target_ids': target_ids,
                'target_ids_y': target_ids}