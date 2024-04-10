# LLM API Parser benchmark

Evaluate different LLMs by their ability to parse data from user input and correctly interpret it as input for a (theoretical) API.

## Purpose

TODO

## Run

Run tests via 

    python3 test_api_parser.py

## Results

Last execution on 10th of April 2024, commit 

| Model | Provider | Tests passed | Tests failed | Execution time |
| ----- | -------- | ------------ | ------------ | -------------- |
| GPT 4 Turbo | OpenAI | 9 | 1 | 47s |
| GPT 3.5 Turbo | OpenAI | 5 | 5 | 25s |
| llama-2-7b-chat-fp16 | Cloudflare | 2 | 8 | 122s |
| phi-2 | Cloudflare | TODO | TODO | TODO |
| gemma-7b-it | Cloudflare | TODO | TODO | TODO |
| mistral-7b-instruct-v0.2 | Cloudflare | TODO | TODO | TODO |