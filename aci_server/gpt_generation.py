from llm import complete


def generate_prompt(system_prompt, user_prompt):
    return complete(system_prompt, user_prompt)
