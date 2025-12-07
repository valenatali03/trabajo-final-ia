import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from const import MODEL_DEFAULT_DIR_PATH

# carga el modelo al que ya se le aplico fine-tunning
def load_model(model_dir: str = MODEL_DEFAULT_DIR_PATH):
    print(f"Cargando modelo desde: {model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()
    return tokenizer, model

def predict(text: str, tokenizer, model):
    # yokenizar
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # Softmax
    probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

    # Obtener clase
    label_id = np.argmax(probs)
    score = float(probs[label_id])

    # En tu modelo: 0 = negativo, 1 = positivo
    label = "POSITIVA" if label_id == 1 else "NEGATIVA"

    return label, score


def main():
    tokenizer, model = load_model()

    print("\nModelo cargado. Escribí una review para clasificar.")
    print("Escribí 'exit' para salir.\n")

    while True:
        text = input("Ingrese review: ").strip()
        if text.lower() == "exit":
            break

        if len(text) == 0:
            print("Ingrese texto, no puede estar vacío.")
            continue

        label, score = predict(text, tokenizer, model)
        print(f"\nPredicción: {label}  (confianza: {score:.4f})\n")


if __name__ == "__main__":
    main()
