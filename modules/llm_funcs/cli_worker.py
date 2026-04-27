# modules/asr_funcs/cli_worker.py
# CLI mode worker for simple text-based interaction with the LLM

# Local Imports
from modules.llm_funcs import llm

# Partial Imports

# Full Imports


def cli_consumer():
    print("Running in CLI mode. Type 'exit' to quit.")

    while True:
        try:
            user_input = input("> ").strip()

            if user_input.lower() == 'exit':
                print("Exiting CLI mode.")
                break

            if not user_input:
                continue

            response = llm.get_llm_response(user_input)
            print(f"< {response}")

        except KeyboardInterrupt:
            print("\nExiting CLI mode.")
            break
        except Exception as e:
            print(f"Error: {e}")
