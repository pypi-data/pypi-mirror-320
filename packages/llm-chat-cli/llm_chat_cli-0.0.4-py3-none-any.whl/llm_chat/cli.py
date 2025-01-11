"""
Command-line interface for LLM Chat
"""
import sys
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from termcolor import colored
from .config import initialize
from .clients import create_clients
from .chat import chat_with_ai
from .utils import count_tokens, render_markdown
from .setup import setup

def print_help_menu():
    """Print the help menu with available commands."""
    print(colored("Available commands:", "yellow"))
    print(colored("  'change model' - Switch to a different AI model", "yellow"))
    print(colored("  'token count' - Display token count for the conversation", "yellow"))
    print(colored("  'clear history' - Clear the conversation history", "yellow"))
    print(colored("  'quit' or 'exit' - End the conversation", "yellow"))
    print(colored("  'help' - Show menu options", "yellow"))

def handle_commands(user_input, models, model_completer, conversation_history, provider, model):
    """
    Handle CLI commands and their execution.

    Returns:
        tuple: (bool, provider, model)
    """
    if user_input.lower() == 'change model':
        print(colored("\nAvailable models:", "cyan"))
        for p, m_list in models.items():
            print(colored(f"{p.capitalize()}:", "yellow"))
            for m in m_list:
                print(colored(f"  - {m}", "green"))
        new_model = prompt("Enter the name of the new model: ", completer=model_completer).strip()
        for p, m_list in models.items():
            if new_model in m_list:
                provider = p
                model = new_model
                break
        else:
            print(colored(f"Model '{new_model}' not found. Please try again.", "red"))
            return True, provider, model
        print(colored(f"Model changed to: {model} (Provider: {provider})", "cyan"))
        return True, provider, model

    if user_input.lower() == "help":
        print_help_menu()
        return True, provider, model

    if user_input.lower() == 'token count':
        total_tokens = sum(count_tokens(m['content'], model) for m in conversation_history)
        print(colored(f"Current conversation token count: {total_tokens}", "cyan"))
        return True, provider, model

    if user_input.lower() == 'clear history':
        conversation_history.clear()
        print(colored("Conversation history cleared.", "cyan"))
        return True, provider, model

    return False, provider, model

def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup()
        return

    api_keys = initialize()
    clients = create_clients(api_keys)
    print(colored("Initialization Successful.", "green"))

    models = {
        'groq': ['llama-3.1-70b-versatile', 'mixtral-8x7b-32768', 'llama-3.1-8b-instant'],
        'openai': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o'],
        'anthropic': ['claude-3-5-sonnet-latest', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229'],
        'cerebras': ['llama3.1-8b', "llama-3.3-70b"]
    }

    print(colored("Welcome to the Multi-Model AI Chat CLI!", "cyan", attrs=["bold"]))
    print_help_menu()

    all_models = [model for provider_models in models.values() for model in provider_models]
    model_completer = WordCompleter(all_models, ignore_case=True)

    provider = 'cerebras'  # Default provider
    model = 'llama-3.3-70b'  # Default model
    conversation_history = []

    while True:
        user_input = prompt("\nYou: ").strip()
        print("\n" + "–" * 70)

        if user_input.lower() in ['quit', 'exit']:
            print(colored("\nGoodbye!", "cyan"))
            break

        handled, provider, model = handle_commands(
            user_input, models, model_completer, conversation_history, provider, model
        )

        if handled:
            continue

        conversation_history.append({"role": "user", "content": user_input})

        if provider not in clients:
            print(colored(f"Error: No API key available for {provider}.", "red"))
            continue

        response = chat_with_ai(clients[provider], provider, model, conversation_history, stream=True)

        if response:
            print(colored(f"\n{model}:", "green", attrs=["bold"]))

            buffer = ""  # Buffer to accumulate chunks
            inside_code_block = False  # Track whether we're inside a code block

            # Process the streamed response
            for chunk in response:
                buffer += chunk

                # Check for opening/closing of code blocks
                if "```" in chunk:
                    inside_code_block = not inside_code_block

                # If not inside a code block, or buffer exceeds threshold, render
                if not inside_code_block and len(buffer) > 100:
                    render_markdown(buffer)
                    buffer = ""  # Reset buffer

            # Render any remaining content in the buffer
            if buffer:
                render_markdown(buffer)

            print("\n" + "–" * 70)
            conversation_history.append({"role": "assistant", "content": "Streamed content."})
        else:
            print(colored(f"Failed to get a response from {model}.", "red"))




if __name__ == "__main__":
    main()