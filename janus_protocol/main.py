import json
from psychographer import Psychographer

# Define the source texts that represent the user's mind for this project.
# In a real scenario, this would be a dynamic list of notes, chats, code, etc.
SOURCE_FILES = [
    'AGENTS.md',
    'README.md',
    # We can also point it to the manifestos themselves if they are in the repo.
    # For now, these two files provide a good starting point.
]

def run_psychographer():
    """
    Main function to run the Psychographer and build the user model.
    """
    print("--- Starting Protocol Janus: Phase 1 (The Mirror) ---")

    # 1. Initialize the Psychographer
    psychographer = Psychographer()

    # 2. Analyze all source files
    for filepath in SOURCE_FILES:
        psychographer.analyze_source_text(filepath)

    # 3. Get the final model
    user_model = psychographer.get_model()

    # 4. Save the model to a file for inspection
    output_filename = 'user_model.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(user_model, f, indent=4, ensure_ascii=False)

    print(f"\n--- Psychographic Model Generation Complete ---")
    print(f"Model saved to '{output_filename}'.")
    print(json.dumps(user_model, indent=2))


if __name__ == "__main__":
    run_psychographer()
