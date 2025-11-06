import openai

# Replace with your OpenAI API key
client = openai.OpenAI(api_key="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")

# Get available models
models = client.models.list()

# Print available model names
for model in models.data:
    print(model.id)
