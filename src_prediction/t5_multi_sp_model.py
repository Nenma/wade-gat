import torch
from torch.utils.data import DataLoader, ConcatDataset
from transformers import get_linear_schedule_with_warmup
from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers import AdamW
import pytorch_lightning as pl
import os
# from graphqlval import exact_match

from entities.text_to_graphql_dataset import TextToGraphQLDataset
from entities.mask_graphql_dataset import MaskGraphQLDataset
from entities.spider_dataset import SpiderDataset
from entities.co_sql_mask_dataset import CoSQLMaskDataset

torch.manual_seed(0)


class T5MultiSPModel(pl.LightningModule):
    def __init__(self, task='denoise', test_flag='graphql', train_sampler=None, batch_size=2, temperature=1.0, top_k=50,
                 top_p=1.0, num_beams=1):
        super(T5MultiSPModel, self).__init__()

        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.num_beams = num_beams

        self.lr = 3e-5

        self.task = task
        self.test_flag = test_flag
        self.train_sampler = train_sampler
        self.batch_size = batch_size

        if self.task == 'finetune':
            self.model = T5ForConditionalGeneration.from_pretrained('t5-small')
        else:
            self.model = T5ForConditionalGeneration.from_pretrained('t5-small')  # no output past?

        self.tokenizer = T5Tokenizer.from_pretrained('t5-small')

        self.criterion = torch.nn.CrossEntropyLoss(ignore_index=self.tokenizer.pad_token_id)
        self.add_special_tokens()

    def forward(
            self, input_ids, attention_mask=None, decoder_input_ids=None, decoder_attention_mask=None, labels=None
    ):
        return self.model(
            input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            labels=labels,
        )

    def add_special_tokens(self):
        special_tokens_dict = self.tokenizer.special_tokens_map  # the issue could be here, might need to copy.
        special_tokens_dict['mask_token'] = '<mask>'
        special_tokens_dict['additional_special_tokens'] = ['<t>', '</t>', '<a>', '</a>']
        self.tokenizer.add_tokens(['{', '}', '<c>', '</c>'])
        self.tokenizer.add_special_tokens(special_tokens_dict)
        self.model.resize_token_embeddings(len(self.tokenizer))

    def _step(self, batch):
        if self.task == 'finetune':
            pad_token_id = self.tokenizer.pad_token_id
            source_ids, source_mask, y = batch["source_ids"], batch["source_mask"], batch["target_ids"]
            labels = y[:, :].clone()
            labels[y[:, :] == pad_token_id] = -100
            outputs = self(source_ids, attention_mask=source_mask, labels=labels, )

            loss = outputs[0]

        else:
            y = batch['target_id']
            labels = y[:, :].clone()
            labels[y[:, :] == self.tokenizer.pad_token_id] = -100
            loss = self(
                input_ids=batch["source_ids"],
                labels=labels
            )[0]

        return loss

    def training_step(self, batch, batch_idx):
        loss = self._step(batch)
        tensorboard_logs = {"train_loss": loss}
        return {"loss": loss, "log": tensorboard_logs}

    def validation_step(self, batch, batch_idx):
        loss = self._step(batch)
        return {"val_loss": loss}

    def validation_epoch_end(self, outputs):
        avg_loss = torch.stack([x["val_loss"] for x in outputs]).mean()
        tensorboard_logs = {"val_loss": avg_loss}
        return {'progress_bar': tensorboard_logs, 'log': tensorboard_logs}

    def configure_optimizers(self):
        t_total = len(self.train_dataloader()) * self.trainer.max_epochs * self.trainer.val_check_interval
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in self.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
            {"params": [p for n, p in self.named_parameters() if any(nd in n for nd in no_decay)], "weight_decay": 0.0},
        ]
        optimizer = AdamW(optimizer_grouped_parameters, lr=self.lr, eps=1e-8)
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=0, num_training_steps=t_total
        )
        self.lr_scheduler = scheduler
        return [optimizer]  # , [scheduler]

    def _generate_step(self, batch):
        generated_ids = self.model.generate(
            batch["source_ids"],
            attention_mask=batch["source_mask"],
            num_beams=self.num_beams,
            max_length=1000,
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            length_penalty=1.0,
            early_stopping=True,
        )

        preds = [
            self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            for g in generated_ids
        ]
        target = [
            self.tokenizer.decode(t, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            for t in batch["target_ids"]
        ]
        return preds, target

    # def test_step(self, batch, batch_idx):
    #   preds, target = self._generate_step(batch)
    #   loss = self._step(batch)
    #   if self.test_flag == 'graphql':
    #     accuracy = exact_match.exact_match_accuracy(preds,target)
    #     return {"test_loss": loss, "test_accuracy": torch.tensor(accuracy)}
    #   else:
    #     return {"test_loss": loss, "preds": preds, "target": target }

    def test_epoch_end(self, outputs):
        avg_loss = torch.stack([x["test_loss"] for x in outputs]).mean()

        if self.test_flag == 'graphql':
            avg_acc = torch.stack([x["test_accuracy"] for x in outputs]).mean()
            tensorboard_logs = {"test_loss": avg_loss, "test_acc": avg_acc}
            return {"progress_bar": tensorboard_logs, "log": tensorboard_logs}

        else:
            output_test_predictions_file = os.path.join(os.getcwd(), "test_predictions.txt")
            with open(output_test_predictions_file, "w+", encoding='utf-8') as p_writer:
                for output_batch in outputs:
                    p_writer.writelines(s + "\n" for s in output_batch["preds"])
                p_writer.close()
            tensorboard_logs = {"test_loss": avg_loss}
            return {"progress_bar": tensorboard_logs, "log": tensorboard_logs}

    def prepare_data(self):
        if self.task == 'finetune':
            self.train_dataset_g = TextToGraphQLDataset(self.tokenizer)
            self.val_dataset_g = TextToGraphQLDataset(self.tokenizer, type_path='dev.json')
            self.test_dataset_g = TextToGraphQLDataset(self.tokenizer, type_path='dev.json')

            self.train_dataset_s = SpiderDataset(self.tokenizer)
            self.val_dataset_s = SpiderDataset(self.tokenizer, type_path='dev.json')
            self.test_dataset_s = SpiderDataset(self.tokenizer, type_path='dev.json')

            self.train_dataset = ConcatDataset([self.train_dataset_g, self.train_dataset_s])
            self.val_dataset = ConcatDataset([self.val_dataset_g, self.val_dataset_s])

            if self.test_flag == 'graphql':
                self.test_dataset = self.test_dataset_g
            else:
                self.test_dataset = self.test_dataset_s

        else:
            train_dataset_g = MaskGraphQLDataset(self.tokenizer)
            val_dataset_g = MaskGraphQLDataset(self.tokenizer, type_path='dev.json')

            train_dataset_s = CoSQLMaskDataset(self.tokenizer)
            val_dataset_s = CoSQLMaskDataset(self.tokenizer, type_path='cosql_dev.json')

            self.train_dataset = ConcatDataset([train_dataset_g, train_dataset_s])
            self.val_dataset = ConcatDataset([val_dataset_g, val_dataset_s])

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=self.batch_size)
