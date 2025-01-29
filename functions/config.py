CHATGPT_SUMMARIZER_CONFIG = {
    "model": "gpt-3.5-turbo",
    "chunk_size": 12000,
    "chunk_overlap": 0,
    "temperature": 0.1,
    "max_tokens": None,
    "response_format": "text",
}

LLAMA_SUMMARIZER_CONFIG = {
    "model": "meta.llama3-70b-instruct-v1:0",
    "chunk_size": 12000,
    "chunk_overlap": 0,
    "temperature": 0.1,
    "response_format": "text",
}

CLAUDE_SUMMARIZER_CONFIG = {
    "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "chunk_size": 12000,
    "chunk_overlap": 0,
    "temperature": 0.1,
    "response_format": "text",
}

CLAUDE_FEATURE_FINDER_CONFIG = {
    "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "chunk_size": 12000,
    "chunk_overlap": 0,
    "temperature": 0.1,
    "response_format": "text",
}

CHATGPT_FEATURE_FINDER_CONFIG = {
    "model": "gpt-3.5-turbo",
    "chunk_size": 12000,
    "chunk_overlap": 0,
    "temperature": 0.1,
    "max_tokens": None,
    "response_format": "json_object",
}

LLAMA_FEATURE_FINDER_CONFIG = {
    "model": "meta.llama3-70b-instruct-v1:0",
    "chunk_size": 12000,
    "chunk_overlap": 0,
    "temperature": 0.1,
    "response_format": "json_object",
}

CHATGPT_CODE_GEN_CONFIG = {
    "model": "gpt-3.5-turbo",
    "chunk_size": 12000,
    "chunk_overlap": 0,
    "temperature": 0.3,
    "max_tokens": None,
    "response_format": "text",
}

LLAMA_CODE_GEN_CONFIG = {
    "model": "meta.llama3-70b-instruct-v1:0",
    "chunk_size": 12000,
    "chunk_overlap": 0,
    "temperature": 0.3,
    "response_format": "text",
}

CLAUDE_CODE_GEN_CONFIG = {
    "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "chunk_size": 12000,
    "chunk_overlap": 0,
    "temperature": 0.3,
    "response_format": "text",
}

CHATGPT_TEST_GEN_CONFIG = {
    "model": "gpt-3.5-turbo",
    "chunk_overlap": 0,
    "temperature": 0,
    "max_tokens": None,
    "response_format": "json_object",
}

LLAMA_TEST_GEN_CONFIG = {
    "model": "meta.llama3-70b-instruct-v1:0",
    "chunk_overlap": 0,
    "temperature": 0,
    "max_tokens": None,
    "response_format": "json_object",
}

CLAUDE_TEST_GEN_CONFIG = {
    "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "chunk_overlap": 0,
    "temperature": 0,
    "max_tokens": None,
    "response_format": "json_object",
}