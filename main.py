from llm_funcs import llm_scr


if __name__ == "__main__":
    print('Running main.py as main. Is this intended?')
    user_input = input("Enter your message: ")
    response = llm_scr.get_llm_response(user_input)
    print("LLM Response:", response)