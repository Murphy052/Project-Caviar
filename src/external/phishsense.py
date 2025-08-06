from typing import Any

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

from src.abstract.singleton import SingletonMeta


class Phishsense1BModel(metaclass=SingletonMeta):
    tokenizer: Any
    _base_model: Any
    model_with_lora: Any

    def __init__(self):
        model_name = "AcuteShrewdSecurity/Llama-Phishsense-1B"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._base_model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model_with_lora = PeftModel.from_pretrained(self._base_model, model_name)

        if torch.cuda.is_available():
            self.model_with_lora = self.model_with_lora.to('cuda')

    def predict(
            self,
            raw_text: str,
    ):
        prompt = f"Classify the following text as phishing or not. Respond with 'TRUE' or 'FALSE':\n\n{raw_text}\nAnswer:"
        inputs = self.tokenizer(prompt, return_tensors="pt")

        if torch.cuda.is_available():
            inputs = {key: value.to('cuda') for key, value in inputs.items()}

        with torch.no_grad():
            output = self.model_with_lora.generate(**inputs, max_new_tokens=5, temperature=0.01, do_sample=False)

        response = self.tokenizer.decode(output[0], skip_special_tokens=True).split("Answer:")[1].strip()
        return "TRUE" in response


def get_phishsense_model() -> Phishsense1BModel:
    return Phishsense1BModel()


if __name__ == "__main__":
    # Example email text
    email_text = "Urgent: Your account has been flagged for suspicious activity. Please log in immediately."
    model = Phishsense1BModel()
    prediction = model.predict(email_text)
    print(f"Model Prediction for the email: {prediction}")
