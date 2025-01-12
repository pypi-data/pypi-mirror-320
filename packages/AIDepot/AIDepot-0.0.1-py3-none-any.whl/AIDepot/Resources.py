from enum import Enum

VISION = 'vision'


class Resources(Enum):
    LLM_JOB_RESULTS = {
        'route': 'llm/job_results'
    }
    LLAMA3_2_3B_MESSAGE = {
        'route': 'llm/llama_3_2_3b/message'
    }
    LLAMA3_2_3B_EMBEDDING = {
        'route': 'llm/llama_3_2_3b/embed'
    }
    LLAMA3_1_8B_MESSAGE = {
        'route': 'llm/llama_3_1_8b/message'
    }
    LLAMA3_1_8B_EMBEDDING = {
        'route': 'llm/llama_3_1_8b/embed'
    }
    LLAMA3_2_VISION_11B_MESSAGE = {
        'route': 'llm/llama_3_2_vision_11b/message', VISION: (512, 512)
    }
    LLAMA3_2_VISION_11B_EMBEDDING = {
        'route': 'llm/llama_3_2_vision_11b/embed', VISION: (512, 512)
    }
    LLAMA3_1_NEMOTRON_51B_MESSAGE = {
        'route': 'llm/llama_3_1_nemotron_51b/message'
    }
    LLAMA3_1_NEMOTRON_51B_EMBEDDING = {
        'route': 'llm/llama_3_1_nemotron_51b/embed'
    }
    LLAMA3_1_NEMOTRON_70B_MESSAGE = {
        'route': 'llm/llama_3_1_nemotron_70b/message'
    }
    LLAMA3_1_NEMOTRON_70B_EMBEDDING = {
        'route': 'llm/llama_3_1_nemotron_70b/embed'
    }
    MISTRAL_7B_MESSAGE = {
        'route': 'llm/mistral_7b/message'
    }
    MISTRAL_7B_EMBEDDING = {
        'route': 'llm/mistral_7b/embed'
    }
    MIXTRAL_8x7B_MESSAGE = {
        'route': 'llm/mixtral_8x7b/message'
    }
    MIXTRAL_8x7B_EMBEDDING = {
        'route': 'llm/mixtral_8x7b/embed'
    }
    PIXTRAL_12B_MESSAGE = {
        'route': 'llm/pixtral_12b/message', VISION: (512, 512)
    }
    PIXTRAL_12B_EMBEDDING = {
        'route': 'llm/pixtral_12b/embed', VISION: (512, 512)
    }
