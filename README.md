# LLM API Parser benchmark

Evaluate different LLMs by their ability to parse data from user input and correctly interpret it as input for a (theoretical) API.

## Background & Purpose

In the past we were used to fill in web forms with all kinds of (personal) data, e.g. for some sign-up, order or request. With LLMs we can simplify the process so the customer just tells us what she wants and the AI determines the API parameters our backends need based on that user input for all forther processing. This was possible with NLU technologies already a few years ago, however LLMs add context, knowledge and corrections that makes this actually usable.

This benchmark was created to run the same test suite (currently 15 tests) against a broad suite of LLMs to see how "smart" they are identifying the relevant content out of the user input.

## Configuration

You need a .env file with the following parameters:

    CLOUDFLARE_ACCOUNT_ID=X
    CLOUDFLARE_TOKEN=Y
    OPENAI_API_KEY=Z

## Run

Run tests via 

    python3 test_api_parser.py

## Results

Last execution on 5th of May 2024 (15 tests in total), commit **TODO**.

| Model | Provider | Tests passed | Tests failed | Execution time | Price/run |
| ----- | -------- | ------------ | ------------ | -------------- | --------- |
| GPT 4 Turbo | OpenAI | 13 | 2 | 116s | $0.09 |
| Mistral Large | Bedrock | 12 | 3 | 109s | N/A |
| llama2 70b | Bedrock | 11 | 4 | 199s | N/A |
| Claude Sonnet | Bedrock | 10 | 5 | 84s | N/A |
| llama3 70b | Bedrock | 10 | 5 | 90s | N/A |
| GPT 3.5 Turbo | OpenAI | 8 | 7 | 49s | $0.01 |
| llama3 8b | Cloudflare | 8 | 7 | 142s | ? |
| llama2 7b (fp16) | Cloudflare | 7 | 8 | 280s | $0.02* |
| llama2 13b | Bedrock | 5 | 10 | 97s | N/A |
| mistral-7b-instruct-v0.2 | Cloudflare | 4 | 11 | 169s | ? |
| gemma-7b-it | Cloudflare | 3 | 12 | 168s | ? |
| phi-2 | Cloudflare | 1 | 14 | 77s | ? |


*free tier available, otherwise part of $5 monthly plan

## Pricing

Most open source models are provided by Cloudflare via convenient API where a limited amount of tokens is free per day using [Workers AI](https://developers.cloudflare.com/workers-ai/platform/pricing). This tier is sufficient for a run of the complete test suite.

## ToDos

- add Phi-3, Claude Opus, Gemini
- more tests