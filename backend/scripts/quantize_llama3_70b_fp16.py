from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "meta-llama/Llama-3.1-70B"  # or "meta-llama/Llama-3.1-70B-Instruct"
save_path = "/data/sovren/models/llama_3.1_70b_fp16"

print(f"Loading model from {model_name} ...")
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Converting model to FP16 ...")
model = model.half()

print(f"Saving quantized model to {save_path} ...")
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)

print(f"Quantized model saved to {save_path}")