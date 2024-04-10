import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

def analyze_with_cloudflare(url, context, prompt):
    response = requests.post(url,
        headers = {"Authorization": f"Bearer {os.getenv('CLOUDFLARE_TOKEN')}"},
        json = {
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ]
        }
    )
    response_text = response.json()["result"]["response"]
    #print(response_text)
    return response_text

def analyze_with_openai(model, context, prompt):
    client = OpenAI(
        api_key = os.getenv('OPENAI_API_KEY'),
    )
    response = client.chat.completions.create(
            model = model,
            temperature = 0.1,
            max_tokens = 256,
            messages = [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ]
        )

    response_text = response.choices[0].message.content
    #print(response_text)
    return response_text

def analyze_with_llm(model, context, prompt):
    match model:
        case "llama-2-7b-chat-fp16":
            url = "https://api.cloudflare.com/client/v4/accounts/" + os.getenv('CLOUDFLARE_ACCOUNT_ID') + "/ai/run/@cf/meta/llama-2-7b-chat-fp16"
            return analyze_with_cloudflare(url, context, prompt)
        case "phi-2":
            url = "https://api.cloudflare.com/client/v4/accounts/" + os.getenv('CLOUDFLARE_ACCOUNT_ID') + "ai/run/@cf/microsoft/phi-2"
            return analyze_with_cloudflare(url, context, prompt)
        case "gemma-7b-it":
            url = "https://api.cloudflare.com/client/v4/accounts/" + os.getenv('CLOUDFLARE_ACCOUNT_ID') + "/ai/run/@hf/google/gemma-7b-it"
            return analyze_with_cloudflare(url, context, prompt)
        case "mistral-7b-instruct-v0.2":
            url = "https://api.cloudflare.com/client/v4/accounts/" + os.getenv('CLOUDFLARE_ACCOUNT_ID') + "/ai/run/@hf/mistralai/mistral-7b-instruct-v0.2"
            return analyze_with_cloudflare(url, context, prompt)
        case "gpt-3.5-turbo-0125":
            model = "gpt-3.5-turbo-0125"
            return analyze_with_openai(model, context, prompt)
        case "gpt-4-turbo-2024-04-09":
            model = "gpt-4-turbo-2024-04-09"
            return analyze_with_openai(model, context, prompt)
        case _:
            print("No valid model defined")

load_dotenv()

# Sample call 
# 
# context = "You are a system assistant that helps to support APIs with their correct parameters. Please extract the given location from the user input and always return it in the format LOCATION: <Location that was identified>. In case you were not able to retrieve a location return LOCATION: Unknown."
# prompt = "I am in Romania in the town of Brasov Siebenbürgen."
# analyze_with_llm("phi-2", context, prompt)