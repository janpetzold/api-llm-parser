import os
import requests
import json
import boto3
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

    # Gemma returns everything with ** so remove that
    response_text = response_text.replace('*', '')
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

def analyze_with_bedrock(model, body):
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), 
    )

    response = bedrock_runtime.invoke_model(
        body=body,
        modelId=model, 
        accept="application/json", 
        contentType="application/json"
    )

    # Print response
    response_body = json.loads(response['body'].read())

    if model == "mistral.mistral-large-2402-v1:0":
        response_text = response_body["outputs"][0]["text"]
    elif model == "anthropic.claude-3-sonnet-20240229-v1:0":
        response_text = response_body["content"][0]["text"]
    else:
        ## llama2/llama3
        response_text = response_body["generation"]

    #print(response_text)
    return response_text
    

def analyze_with_llm(model, context, prompt):
    match model:
        case "llama-2-7b-chat-fp16":
            url = "https://api.cloudflare.com/client/v4/accounts/" + os.getenv('CLOUDFLARE_ACCOUNT_ID') + "/ai/run/@cf/meta/llama-2-7b-chat-fp16"
            return analyze_with_cloudflare(url, context, prompt)
        case "llama-3-8b-instruct":
            url = "https://api.cloudflare.com/client/v4/accounts/" + os.getenv('CLOUDFLARE_ACCOUNT_ID') + "/ai/run/@cf/meta/llama-3-8b-instruct"
            return analyze_with_cloudflare(url, context, prompt)
        case "phi-2":
            url = "https://api.cloudflare.com/client/v4/accounts/" + os.getenv('CLOUDFLARE_ACCOUNT_ID') + "/ai/run/@cf/microsoft/phi-2"
            # Phi-2 uses a specific syntax
            return analyze_with_cloudflare(url, "", f"[CONTEXT]{context}[/CONTEXT][PROMPT]{prompt}[/PROMPT]")
        case "gemma-7b-it":
            url = "https://api.cloudflare.com/client/v4/accounts/" + os.getenv('CLOUDFLARE_ACCOUNT_ID') + "/ai/run/@hf/google/gemma-7b-it"
            # Gemma uses specific syntax
            return analyze_with_cloudflare(url, "", f"CONTEXT:{context} PROMPT: {prompt}")
        case "mistral-7b-instruct-v0.2":
            url = "https://api.cloudflare.com/client/v4/accounts/" + os.getenv('CLOUDFLARE_ACCOUNT_ID') + "/ai/run/@hf/mistralai/mistral-7b-instruct-v0.2"
            return analyze_with_cloudflare(url, context, prompt)
        case "gpt-3.5-turbo-0125":
            model = "gpt-3.5-turbo-0125"
            return analyze_with_openai(model, context, prompt)
        case "gpt-4-turbo-2024-04-09":
            model = "gpt-4-turbo-2024-04-09"
            return analyze_with_openai(model, context, prompt)
        case "gpt-4o-mini":
            model = "gpt-4o-mini"
            return analyze_with_openai(model, context, prompt)
        case "gpt-4o":
            model = "gpt-4o"
            return analyze_with_openai(model, context, prompt)
        case "mistral.mistral-large-2402-v1:0":
            model = "mistral.mistral-large-2402-v1:0"
            
            # Mistral instruct models specific syntax
            instruction = f"<s>[INST] {context} [/INST] [QUERY] {prompt} [/QUERY]</s>"

            body = json.dumps({
                "prompt": instruction,
                "temperature": 0.2,
            })
            return analyze_with_bedrock(model, body)
        case "anthropic.claude-3-sonnet-20240229-v1:0":
            model = "anthropic.claude-3-sonnet-20240229-v1:0"

            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "system": context,
                "messages": [
                    {
                        "role": "user",
                        "content": [{
                            "type": "text",
                            "text": prompt
                        }]
                    }
                ]
            })

            return analyze_with_bedrock(model, body)
        
        case "meta.llama2-13b-chat-v1":
            model = "meta.llama2-13b-chat-v1"

            # Llama2 instruct models specific syntax
            instruction = f"<s>[INST] <<SYS>>{context}<</SYS>>{prompt}[/INST]"

            body = json.dumps({
                "prompt": instruction,
                "temperature": 0.2,
            })
            return analyze_with_bedrock(model, body)
        case "meta.llama2-70b-chat-v1":
            model = "meta.llama2-70b-chat-v1"

            # Llama2 instruct models specific syntax
            instruction = f"<s>[INST] <<SYS>>{context}<</SYS>>{prompt}[/INST]"

            body = json.dumps({
                "prompt": instruction,
                "temperature": 0.2,
            })
            return analyze_with_bedrock(model, body)
        case "meta.llama3-70b-instruct-v1:0":
            model = "meta.llama3-70b-instruct-v1:0"

            # Llama3 instruct models specific syntax - follows the format of https://llama.meta.com/docs/model-cards-and-prompt-formats/meta-llama-3
            instruction = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>{context}<|eot_id|><|start_header_id|>user<|end_header_id|>{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"

            body = json.dumps({
                "prompt": instruction,
                "temperature": 0.2,
            })
            return analyze_with_bedrock(model, body)
        case _:
            print("No valid model defined")

load_dotenv()

# Sample call 
# 
# context = "You are a system assistant that helps to support APIs with their correct parameters. Please extract the given location from the user input and always return it in the format LOCATION: <Location that was identified>. In case you were not able to retrieve a location return LOCATION: Unknown."
# prompt = "I am in Romania in the town of Brasov Siebenbürgen."
# analyze_with_llm("phi-2", context, prompt)