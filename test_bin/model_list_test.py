from openai import OpenAI

client = OpenAI(
    api_key="sk-e155ff6bb3944cb1a619625a3dbecd8c",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

models = client.models.list()

for model in models.data:
    print(model.id)