import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel


# Function to load the model and tokenizer
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("AcuteShrewdSecurity/Llama-Phishsense-1B")
    base_model = AutoModelForCausalLM.from_pretrained("AcuteShrewdSecurity/Llama-Phishsense-1B")
    model_with_lora = PeftModel.from_pretrained(base_model, "AcuteShrewdSecurity/Llama-Phishsense-1B")

    if torch.cuda.is_available():
        model_with_lora = model_with_lora.to('cuda')

    return model_with_lora, tokenizer


# Function to make a single prediction
def predict_email(model, tokenizer, email_text):
    prompt = f"Classify the following text as phishing or not. Respond with 'TRUE' or 'FALSE':\n\n{email_text}\nAnswer:"
    inputs = tokenizer(prompt, return_tensors="pt")

    # Move inputs to GPU if available
    if torch.cuda.is_available():
        inputs = {key: value.to('cuda') for key, value in inputs.items()}

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=5, temperature=0.01, do_sample=False)

    response = tokenizer.decode(output[0], skip_special_tokens=True).split("Answer:")[1].strip()
    return response


# Load model and tokenizer
model, tokenizer = load_model()

# Example email text
email_text = "Urgent: Your account has been flagged for suspicious activity. Please log in immediately."
prediction = predict_email(model, tokenizer, email_text)
print(f"Model Prediction for the email: {prediction}")
