from openai import OpenAI

client = OpenAI(
    base_url="https://huggingface.co/spaces/kuntal01/meta-llama-Llama-3.1-8B",
    api_key="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"
)

messages = [
    {"role": "user", "content": "What is the capital of France?"}
]

response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B",
    messages=messages,
    max_tokens=50
)

print(response.choices[0].message)
