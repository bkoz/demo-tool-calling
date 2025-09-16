from llama_stack_client import LlamaStackClient
import pprint

# Connect to Llama Stack
client = LlamaStackClient(
    base_url="http://localhost:8321",
    timeout=600.0
)

# Create evaluation examples
handmade_eval_rows = [
    {
        "input_query": "What is the capital of France?",
        "generated_answer": "The capital of France is Paris.",
        "expected_answer": "Paris",
    },
    {
        "input_query": "Who wrote Romeo and Juliet?",
        "generated_answer": "William Shakespeare wrote Romeo and Juliet.",
        "expected_answer": "shakespeare",  # lowercase - will fail!
    },
    {
        "input_query": "What is 2 + 2?",
        "generated_answer": "The answer is 4.",
        "expected_answer": "4",
    }
]

print("📝 Testing subset_of evaluation:")
pprint.pprint(handmade_eval_rows)

# Run subset_of evaluation
scoring_response = client.scoring.score(
    input_rows=handmade_eval_rows,
    scoring_functions={"basic::subset_of": None}
)

print("\n📊 Results:")
pprint.pprint(scoring_response)

# Show accuracy
results = scoring_response.results['basic::subset_of']
accuracy = results.aggregated_results['accuracy']['accuracy']
print(f"\n📈 Accuracy: {accuracy:.1%}")
