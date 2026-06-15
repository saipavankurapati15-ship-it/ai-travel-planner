from google import genai

client = genai.Client(
    api_key="AQ.Ab8RN6LSt_9SdFYQczAfn4Z9cpF25taUSoO5up-kkN-KWDTzpg"
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello"
)

print(response.text)