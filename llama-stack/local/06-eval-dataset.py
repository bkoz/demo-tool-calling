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

# Register SimpleQA dataset
print("📚 Registering SimpleQA dataset...")
client.datasets.register(
    purpose="eval/messages-answer",
    source={
        "type": "uri",
        "uri": "huggingface://datasets/llamastack/simpleqa?split=train",
    },
    dataset_id="huggingface::simpleqa",
)

# Get sample questions
eval_rows = client.datasets.iterrows(
    dataset_id="huggingface::simpleqa",
    limit=3,
)

print("\n📋 Sample questions:")
for i, row in enumerate(eval_rows.data):
    print(f"{i+1}. {row['input_query']}")
    print(f"   Expected: {row['expected_answer']}")

# Register benchmark
client.benchmarks.register(
    benchmark_id="meta-reference::simpleqa",
    dataset_id="huggingface::simpleqa",
    scoring_functions=["llm-as-judge::base"],
)

# Evaluate model
print(f"\n🤖 Evaluating {model_id} on knowledge questions...")
response = client.eval.evaluate_rows(
    benchmark_id="meta-reference::simpleqa",
    input_rows=eval_rows.data,
    scoring_functions=["llm-as-judge::base"],
    benchmark_config={
        "eval_candidate": {
            "type": "model",
            "model": model_id,
            "sampling_params": {
                "strategy": {"type": "greedy"},
                "max_tokens": 512,
            },
        },
    },
)

print("\n📊 Results:")
for i, gen in enumerate(response.generations):
    score = response.scores['llm-as-judge::base'].score_rows[i]
    print(f"\n{i+1}. Question: {eval_rows.data[i]['input_query']}")
    print(f"   Expected: {eval_rows.data[i]['expected_answer']}")
    print(f"   Generated: {gen['generated_answer']}")
    print(f"   Score: {score['score']}")
