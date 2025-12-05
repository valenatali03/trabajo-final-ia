import os
os.environ["WANDB_DISABLED"] = "true"  # Desactiva W&B

from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import torch
import numpy as np
from evaluate import load

# cargar dataset desde el JSON
dataset = load_dataset("json", data_files="steam_reviews.json")

# renombrar columnas
dataset = dataset.rename_columns({
    "review": "text",
    "voted_up": "label"
})

# convertir True/False -> 1/0
def convert_label(example):
    example["label"] = int(example["label"])
    return example

dataset = dataset.map(convert_label)

# cargar tokenizer
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-multilingual-cased")

# tokenización
def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

tokenized_dataset = dataset.map(tokenize, batched=True)

# separar train/validation
tokenized_dataset = tokenized_dataset["train"].train_test_split(test_size=0.2)
train_ds = tokenized_dataset["train"]
val_ds = tokenized_dataset["test"]

# modelo pre-entrenado
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-multilingual-cased",
    num_labels=2
)

# 7. Configuración del entrenamiento
training_args = TrainingArguments(
    output_dir="./modelo_distilbert",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    learning_rate=3e-5,
    weight_decay=0.1,
    eval_strategy="epoch",
    save_strategy="epoch",
    metric_for_best_model="loss",
    logging_steps=10,
    report_to="none"
)

# entrenador
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    compute_metrics=compute_metrics,
)

# entrenar
trainer.train()

# guardar modelo entrenado
trainer.save_model("./modelo_distilbert")
tokenizer.save_pretrained("./modelo_distilbert")
print("Entrenamiento completado y modelo guardado.")