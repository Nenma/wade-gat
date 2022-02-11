from torch.utils.data import Dataset
import json


class MaskGraphQLDataset(Dataset):
  'Characterizes a dataset for PyTorch'
  def __init__(self, tokenizer, type_path='train.json', block_size=64):
        'Initialization'
        super(MaskGraphQLDataset, ).__init__()
        self.tokenizer = tokenizer

        self.source = []
        self.target = []
        path = './SPEGQL Datasets/SPEGQL-dataset/dataset/' + type_path
        with open(path, 'r', encoding='utf-8') as f:
          data = json.load(f)
          for example in data:
            utterance = example['query']
            encoded_source = tokenizer.encode(utterance + ' </s>', max_length=block_size, padding='max_length', truncation=True, return_tensors='pt').squeeze()
            token_count = encoded_source.shape[0]
            repeated_utterance = [encoded_source for _ in range(token_count)]
            for pos in range(1, token_count):
              encoded_source = repeated_utterance[pos].clone()
              target_id = encoded_source[pos].item()
              if target_id == tokenizer.eos_token_id:
                break
              encoded_source[pos] = tokenizer.mask_token_id
              decoded_target = ''.join(tokenizer.convert_ids_to_tokens([target_id])) + ' </s>'
              encoded_target = tokenizer.encode(decoded_target, return_tensors='pt', max_length=4, padding='max_length', truncation=True).squeeze() # should always be of size 1
              self.target.append(encoded_target)
              self.source.append(encoded_source)


  def __len__(self):
        'Denotes the total number of samples'
        return len(self.source)

  def __getitem__(self, index):
        'Generates one sample of data'
        source_ids = self.source[index]
        target_id = self.target[index]
        return { 'source_ids': source_ids,
                'target_id': target_id}