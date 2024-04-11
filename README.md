# LLM API Parser benchmark

Evaluate different LLMs by their ability to parse data from user input and correctly interpret it as input for a (theoretical) API.

## Background & Purpose

TODO

## Configuration

You need a .env file with the following parameters:

    CLOUDFLARE_ACCOUNT_ID=X
    CLOUDFLARE_TOKEN=Y
    OPENAI_API_KEY=Z

## Run

Run tests via 

    python3 test_api_parser.py

## Results

Last execution on 10th of April 2024, commit **351c9e7**.

| Model | Provider | Tests passed | Tests failed | Execution time |
| ----- | -------- | ------------ | ------------ | -------------- |
| GPT 4 Turbo | OpenAI | 9 | 1 | 47s |
| GPT 3.5 Turbo | OpenAI | 5 | 5 | 25s |
| llama2 70b | Bedrock | 7 | 3 | 65s |
| llama2 13b | Bedrock | 2 | 8 | 66s |
| llama2 7b (fp16) | Cloudflare | 3 | 7 | 144s |
| Mistral Large | Bedrock | 8 | 2 | 112s |
| mistral-7b-instruct-v0.2 | Cloudflare | 3 | 7 | 78s |
| Claude Sonnet | Bedrock | 8 | 2 | 42s |
| phi-2 | Cloudflare | 0 | 10 | 74s |
| gemma-7b-it | Cloudflare | 0 | 10 | 113s |

## Pricing

For OpenAI a single run of the test suite with GPT4 is approx. $0.04. GPT3 is less than $0.01.

Most open source models are provided by Cloudflare via convenient API where a limited amount of tokens is free per day using [Workers AI](https://developers.cloudflare.com/workers-ai/platform/pricing). This tier is sufficient for a run of the complete test suite.