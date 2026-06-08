from openai import OpenAI

client = OpenAI(
    api_key="s2_485ad5943af14dc4a6a663af88e4ef5e",
    base_url="https://routellm.abacus.ai/v1"
)

try:

    models = client.models.list()

    print("CONNECTED")

    for model in models.data[:10]:
        print(model.id)

except Exception as e:

    print("ERROR")
    print(type(e))
    print(e)