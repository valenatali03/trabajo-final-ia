import os
os.environ["WANDB_DISABLED"] = "true"  # Desactiva W&B
from datasets import load_dataset
from const import DATASET_NAME, MODEL_DEFAULT_DIR_PATH
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import numpy as np
from evaluate import load


# convertir True/False -> 1/0
def convert_label(example):
    example["label"] = int(example["label"])
    return example

def entrenar(file: str, test_size: float, epochs: int, learning_rate: float, output_dir=MODEL_DEFAULT_DIR_PATH):
# cargar dataset desde el JSON
    if not(file.endswith(".json")):
        print("El archivo no es de tipo json")
        return

    dataset = load_dataset("json", data_files=file)

    # renombrar columnas
    dataset = dataset.rename_columns({
        "review": "text",
        "voted_up": "label"
    })

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
    tokenized_dataset = tokenized_dataset["train"].train_test_split(test_size=test_size)
    train_ds = tokenized_dataset["train"]
    val_ds = tokenized_dataset["test"]

    # modelo pre-entrenado
    model = AutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-multilingual-cased",
        num_labels=2
    )

    # métricas
    precision = load("precision")
    recall = load("recall")
    f1 = load("f1")
    accuracy = load("accuracy")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)

        return {
            "accuracy": accuracy.compute(predictions=preds, references=labels)["accuracy"],
            "precision": precision.compute(predictions=preds, references=labels, average="binary")["precision"],
            "recall": recall.compute(predictions=preds, references=labels, average="binary")["recall"],
            "f1": f1.compute(predictions=preds, references=labels, average="binary")["f1"],
        }

# configuración del entrenamiento
    training_args = TrainingArguments(
        output_dir=MODEL_DEFAULT_DIR_PATH,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=epochs,
        learning_rate=learning_rate,
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
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("Entrenamiento completado y modelo guardado.")

if __name__ == "__main__":
    entrenar(file=DATASET_NAME, test_size=0.2, epochs=3, learning_rate=3e-5)