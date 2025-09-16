from llama_stack_client import LlamaStackClient
import pprint

# Connect to Llama Stack
client = LlamaStackClient(
    base_url="http://localhost:8321",
    timeout=600.0
)

# Get available model for judging
available_models = [
    model.identifier for model in client.models.list() if model.model_type == "llm"
]
judge_model = available_models[0]

# Same evaluation examples
handmade_eval_rows = [
    {
        "input_query": "What is the capital of France?",
        "generated_answer": "The capital of France is Paris.",
        "expected_answer": "Paris",
    },
    {
        "input_query": "Who wrote Romeo and Juliet?",
        "generated_answer": "William Shakespeare wrote Romeo and Juliet.",
        "expected_answer": "shakespeare",
    },
    {
        "input_query": "What is 2 + 2?",
        "generated_answer": "The answer is 4.",
        "expected_answer": "4",
    }
]

# Judge prompt
JUDGE_PROMPT = """
Given a QUESTION and GENERATED_RESPONSE and EXPECTED_RESPONSE.

Compare the factual content. Ignore differences in style, grammar, or punctuation.
Answer by selecting one option:
(A) The GENERATED_RESPONSE is a subset of the EXPECTED_RESPONSE and is fully consistent.
(B) The GENERATED_RESPONSE is a superset of the EXPECTED_RESPONSE and is fully consistent.
(C) The GENERATED_RESPONSE contains all the same details as the EXPECTED_RESPONSE.
(D) There is a disagreement between the responses.
(E) The answers differ, but these differences don't matter factually.

Format: "Answer: One of ABCDE, Explanation: "

QUESTION: {input_query}
GENERATED_RESPONSE: {generated_answer}
EXPECTED_RESPONSE: {expected_answer}
"""

print(f"🤖 Testing LLM-as-judge with {judge_model}:")

# Run LLM-as-judge evaluation
scoring_response = client.scoring.score(
    input_rows=handmade_eval_rows,
    scoring_functions={
        "llm-as-judge::base": {
            "judge_model": judge_model,
            "prompt_template": JUDGE_PROMPT,
            "type": "llm_as_judge",
            "judge_score_regexes": ["Answer: (A|B|C|D|E)"],
        }
    }
)

print("\n📊 Results:")
for i, score_row in enumerate(scoring_response.results['llm-as-judge::base'].score_rows):
    print(f"\n{i+1}. {handmade_eval_rows[i]['input_query']}")
    print(f"   Score: {score_row['score']}")
    print(f"   Reasoning: {score_row['judge_feedback']}")
