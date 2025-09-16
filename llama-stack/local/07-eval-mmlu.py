from llama_stack_client import LlamaStackClient
import pprint

# Connect to Llama Stack
client = LlamaStackClient(
    base_url="http://localhost:8321",
    timeout=600.0
)

# Get model
available_models = [
    model.identifier for model in client.models.list() if model.model_type == "llm"
]
model_id = available_models[0]

# Define system prompt for multiple choice questions
SYSTEM_PROMPT_TEMPLATE = """
You are an expert in {subject} whose job is to answer multiple choice questions.

First, reason about the correct answer.

Then write the answer in the following format where X is exactly one of A,B,C,D:

Answer: X

Make sure X is one of A,B,C,D.

If you are uncertain of the correct answer, guess the most likely one.
"""

# Sample MMLU-style questions (normally you'd load from the actual dataset)
mmlu_sample_rows = [
    {
        "input_query": "What is the capital of France?\nA) London\nB) Berlin\nC) Paris\nD) Madrid",
        "expected_answer": "C",
        "chat_completion_input": '[{"role": "user", "content": "What is the capital of France?\\nA) London\\nB) Berlin\\nC) Paris\\nD) Madrid"}]'
    },
    {
        "input_query": "Which of the following is a prime number?\nA) 4\nB) 6\nC) 8\nD) 7",
        "expected_answer": "D",
        "chat_completion_input": '[{"role": "user", "content": "Which of the following is a prime number?\\nA) 4\\nB) 6\\nC) 8\\nD) 7"}]'
    },
    {
        "input_query": "Who wrote 'Romeo and Juliet'?\nA) Charles Dickens\nB) William Shakespeare\nC) Mark Twain\nD) Jane Austen",
        "expected_answer": "B",
        "chat_completion_input": '[{"role": "user", "content": "Who wrote \'Romeo and Juliet\'?\\nA) Charles Dickens\\nB) William Shakespeare\\nC) Mark Twain\\nD) Jane Austen"}]'
    }
]

print("📚 MMLU-style multiple choice evaluation:")
for i, row in enumerate(mmlu_sample_rows):
    print(f"{i+1}. {row['input_query']}")
    print(f"   Expected: {row['expected_answer']}")

# Create system message being an expert in Academic Subjects
system_message = {
    "role": "system",
    "content": SYSTEM_PROMPT_TEMPLATE.format(subject="academic subjects"),
}

# Register benchmark
client.benchmarks.register(
    benchmark_id="meta-reference::mmlu-sample",
    dataset_id="mmlu-sample",
    scoring_functions=[],
)

# Evaluate with regex parser for multiple choice
print(f"\n🎯 Evaluating {model_id} on MMLU-style questions...")
response = client.eval.evaluate_rows(
    benchmark_id="meta-reference::mmlu-sample",
    input_rows=mmlu_sample_rows,
    scoring_functions=["basic::regex_parser_multiple_choice_answer"],
    benchmark_config={
        "eval_candidate": {
            "type": "model",
            "model": model_id,
            "sampling_params": {
                "strategy": {
                    "type": "top_p",
                    "temperature": 0.1,
                    "top_p": 0.95,
                },
                "max_tokens": 512,
            },
            "system_message": system_message,
        },
    },
)

print("\n📊 MMLU Results:")
for i, gen in enumerate(response.generations):
    score = response.scores['basic::regex_parser_multiple_choice_answer'].score_rows[i]
    print(f"\n{i+1}. Question: {mmlu_sample_rows[i]['input_query'].split('?')[0]}?")
    print(f"   Expected: {mmlu_sample_rows[i]['expected_answer']}")
    print(f"   Generated: {gen['generated_answer']}")
    print(f"   Score: {score['score']}")

# Calculate accuracy
results = response.scores['basic::regex_parser_multiple_choice_answer']
if 'accuracy' in results.aggregated_results:
    accuracy = results.aggregated_results['accuracy']['accuracy']
    print(f"\n📈 MMLU Accuracy: {accuracy:.1%}")
