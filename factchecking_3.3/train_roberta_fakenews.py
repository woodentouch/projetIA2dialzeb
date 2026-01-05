import argparse
import json
import os
from typing import Dict, List, Tuple

import pandas as pd
import torch
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)


LABEL2ID: Dict[str, int] = {"FAKE": 0, "REAL": 1}
ID2LABEL: Dict[int, str] = {v: k for k, v in LABEL2ID.items()}


class FakeNewsDataset(Dataset):
    def __init__(self, texts: List[str], labels: List[int], tokenizer: AutoTokenizer, max_length: int):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding=False,
            max_length=max_length,
        )
        self.labels = labels

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


def load_dataframe(path: str, seed: int) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = df["label"].str.upper().str.strip()
    df = df[df["label"].isin(LABEL2ID.keys())]
    df = df.drop_duplicates(subset=["text", "label"], keep="first")
    # Shuffle once up-front; Trainer will reshuffle each epoch.
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def compute_metrics(eval_pred: Tuple[List, List]) -> Dict[str, float]:
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="binary", pos_label=LABEL2ID["FAKE"], zero_division=0)
    acc = accuracy_score(labels, preds)
    return {
        "accuracy": acc,
        "precision_fake": precision,
        "recall_fake": recall,
        "f1_fake": f1,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fine-tune RoBERTa on fake news detection")
    parser.add_argument("--data_path", type=str, default="fake_news_dataset_multilang.csv", help="Path to CSV with 'text' and 'label' columns")
    parser.add_argument("--model_name", type=str, default="roberta-base", help="HF model checkpoint to start from")
    parser.add_argument("--output_dir", type=str, default=os.path.join("models", "roberta-fake-news"), help="Where to save the fine-tuned model")
    parser.add_argument("--max_length", type=int, default=256, help="Max sequence length")
    parser.add_argument("--test_size", type=float, default=0.15, help="Validation split ratio")
    parser.add_argument("--batch_size", type=int, default=16, help="Per-device batch size")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


def main():
    args = parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    df = load_dataframe(args.data_path, args.seed)
    texts = df["text"].tolist()
    labels = [LABEL2ID[label] for label in df["label"].tolist()]

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts,
        labels,
        test_size=args.test_size,
        stratify=labels,
        random_state=args.seed,
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=len(LABEL2ID),
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    train_dataset = FakeNewsDataset(train_texts, train_labels, tokenizer, args.max_length)
    val_dataset = FakeNewsDataset(val_texts, val_labels, tokenizer, args.max_length)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        overwrite_output_dir=True,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.lr,
        weight_decay=0.01,
        warmup_ratio=0.1,
        seed=args.seed,
        data_seed=args.seed,
        fp16=torch.cuda.is_available(),
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    eval_metrics = trainer.evaluate()
    print("Validation metrics:", eval_metrics)

    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    with open(os.path.join(args.output_dir, "label_map.json"), "w", encoding="utf-8") as f:
        json.dump(ID2LABEL, f, ensure_ascii=True, indent=2)

    print(f"Model saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
