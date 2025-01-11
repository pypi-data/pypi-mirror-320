import argparse
import json
import os
# noinspection PyUnresolvedReferences
import readline  # used by input()
import sys
import time
import tomllib
import openai
from appdirs import user_config_dir
from dataclasses import dataclass

from .functions import functions, handle_function_call
from .fancy import print_fancy, print_reset
from .auto_completer import AutoCompleter
from . import fallbacks
from . import model_quirks

app_name = "parrotflume"
config_dir = user_config_dir(appname=app_name)
config_path = os.path.join(config_dir, f"{app_name}.config.toml")

@dataclass
class Config:
    api_provider: str = None
    base_url: str = None
    api_key: str = None
    model: str = None
    temperature: float = 0.0
    max_tokens: int = 4096
    do_markdown: bool = True
    do_latex: bool = True
    do_color: bool = False
    color = "bright_yellow"
    func: bool = True


def load_config(file_path):
    try:
        with open(file_path, "rb") as f:
            config_data = tomllib.load(f)
            return config_data
    except FileNotFoundError:
        try:
            os.makedirs(config_dir, exist_ok=True)
        except OSError:
            pass  # ignore
        return None
    except tomllib.TOMLDecodeError as e:
        print(f"Error parsing TOML config file: {e}", file=sys.stderr)
        sys.exit(1)


def create_completion_response(config, messages, add_functions=True):
    # Ugly quirk for openAI o1-preview* model: Does not know system messages
    if any(config.model.startswith(prefix) for prefix in model_quirks.no_system):
        if messages[0]["role"] == "system":
            messages[0]["role"] = "user"
    # Ugly quirk for openAI o* (non-preview) models: system has been renamed to developer
    elif any(config.model.startswith(prefix) for prefix in model_quirks.no_system):
        if messages[0]["role"] == "system":
            messages[0]["role"] = "developer"
    else:
        if messages[0]["role"] in "developer":
            messages[0]["role"] = "system"

    # Ugly quirk for openAI o1-preview* model: Does not know function calls
    # Ugly quirk for deepseek-* model: Uses tools instead of functions
    if any(config.model.startswith(prefix) for prefix in model_quirks.no_function_call + model_quirks.tool_call):
        messages = [message for message in messages if message["role"] != "function"]

    params = {
        "model": config.model,
        "messages": messages,
    }

    # Ugly quirk for openAI o* models: New parameter for max_tokens, no temperature
    if any(config.model.startswith(prefix) for prefix in model_quirks.max_completion_tokens):
        params["max_completion_tokens"] = config.max_tokens
    else:
        params["max_tokens"] = config.max_tokens

    # Ugly quirk for openAI o* models: No temperature
    if not any(config.model.startswith(prefix) for prefix in model_quirks.no_temperature):
        params["temperature"] = config.temperature

    # Ugly quirk for openAI o1-preview* model: Does not know function calls
    # Ugly quirk for deepseek-* model: Uses tools instead of functions
    if add_functions and config.func and not any(config.model.startswith(prefix) for prefix in model_quirks.no_function_call + model_quirks.tool_call):
        params["functions"] = functions
        params["function_call"] = "auto"

    # Try to get a completion, on rate limit retry 4 times with increasing duration
    retry = 0
    while True:
        try:
            return openai.chat.completions.create(**params)
        except openai.APIError as e:
            print(f"API returned an API Error: {e}", file=sys.stderr)
            return None
        except openai.RateLimitError as e:
            print(f"API request exceeded rate limit: {e}", file=sys.stderr)
            retry += 1
            if retry == 5:
                return None
            else:
                time.sleep(retry ** 2)


def run_oneshot(config, prompt):
    system_message = (
        "You are an assistant providing a direct answer based on the user's input. "
        "You will provide a complete response immediately, without asking clarifying questions. "
        "Your reply should be clear and concise. "
        "Your reply is one-shot, i.e. not part of a conversation."
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    response = create_completion_response(config, messages)
    if not response:
        sys.exit(1)

    while response.choices[0].finish_reason == "function_call":
        function_call = response.choices[0].message.function_call
        handle_function_call(messages, function_call)
        response = create_completion_response(config, messages, False)

    output = response.choices[0].message.content
    print_fancy(output, config.do_markdown, config.do_latex, config.do_color, config.color)


def get_file_content(file_name):
    if not os.path.isfile(file_name):
        print(f"Error: {file_name} does not exist.", file=sys.stderr)
        sys.exit(1)
    with open(file_name, "r") as f:
        try:
            return f.read()
        except OSError as e:
            print(f"Error opening {file_name}: {e}", file=sys.stderr)
            sys.exit(1)


def run_transform(config, prompt, file_paths):
    system_message = (
        "You are a file transformation assistant. "
        "You receive the content of a file. "
        "Execute instructions on the file content and output only the transformed, whole file. "
        "Do not add any explanations, commentary, markdown decoration such as \"\x60\x60\x60\" or other additional text. "
        f"The instructions are:\n{prompt}"
    )

    def transform(file_content):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": file_content}
        ]

        response = create_completion_response(config, messages)
        if not response:
            sys.exit(1)
        output = response.choices[0].message.content

        # end output with newline if the input does
        if file_content.endswith('\n'):
            output = output.rstrip('\n') + '\n'
        else:
            output = output.rstrip('\n')

        sys.stdout.write(output)

    if not file_paths:
        transform(sys.stdin.read())
    else:
        for file in file_paths:
            transform(get_file_content(file))


def run_perform(config, prompt, file_paths):
    system_message = prompt

    def perform(file_content):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": file_content}
        ]

        response = create_completion_response(config, messages)
        if not response:
            sys.exit(1)
        output = response.choices[0].message.content

        output += '\n'

        sys.stdout.write(output)

    if not file_paths:
        perform(sys.stdin.read())
    else:
        for file in file_paths:
            perform(get_file_content(file))


def get_multiline_input():
    print("[Enter multiline input (press Ctrl+D to end)]")
    lines = []
    try:
        while True:
            line = input(">>")
            lines.append(line)
    except EOFError:
        print()
    return "\n".join(lines)


def get_api_providers():
    """Extract API provider names from the config file."""
    config_file_data = load_config(config_path)
    if config_file_data and "api_providers" in config_file_data:
        return [provider["name"] for provider in config_file_data["api_providers"]]
    return []


def run_chat(config):
    system_message = (
        "You are an assistant. "
        "You will hold a conversation with the user. "
        "Respond clearly and concisely to each user message. "
        "Avoid continuation prompts and other open ended closing statements."
    )

    messages = [{"role": "system", "content": system_message}]

    auto_completer = AutoCompleter(get_api_providers())
    auto_completer.setup()  # alters global state of readline

    print("[Entering chat:  /q to quit, /r to reset, /b for multi line buffer, /h for help]")
    while True:
        try:
            user_input = input("> ")
        except EOFError:
            print()
            continue
        except KeyboardInterrupt:
            break

        if user_input.strip() == "/h":
            print(
                "/a try prompt again\n"
                "/b multi line input buffer\n"
                "/c <file_path> save latest code block\n"
                "/d <file_path> dump chat history\n"
                "/f <file path> input file\n"
                "/h help\n"
                "/l list models\n"
                "/m <model> switch model\n"
                "/p <provider> switch API provider\n"
                "/q quit\n"
                "/r reset chat history\n"
                "/t truncate last round\n"
                "/u <file_path> un-dump (load) chat history\n"
                "/w <float> set warmth (temperature)\n"
                "/0 reset ANSII colors ('[0m')\n"
            )
            continue

        elif user_input.strip() == "/q":
            break

        elif user_input.strip() == "/r":
            print("[Conversation history reset]\n")
            messages = [{"role": "system", "content": system_message}]
            continue

        elif user_input.strip() == "/a":
            if len(messages) > 2 and messages[-1]["role"] == "assistant" and messages[-2]["role"] == "user":
                messages.pop()  # pop reply
                user_input = messages[-1]["content"]  # get prompt as input
                messages.pop()  # pop prompt
            elif len(messages) > 1 and messages[-1]["role"] == "user":
                user_input = messages[-1]["content"]  # get prompt as input
                messages.pop()  # pop prompt
            else:
                print("[No suitable messages found]")
                continue

        elif user_input.strip().startswith("/c "):
            file_path = user_input.strip()[3:].lstrip()
            code_block = None

            for message in reversed(messages):
                if "\x60\x60\x60" in message["content"]:
                    parts = message["content"].split("\x60\x60\x60")
                    # The code block is the second-to-last segment
                    if len(parts) >= 2:
                        code_block = parts[-2].strip()
                        break

            if code_block:
                try:
                    with open(file_path, "w") as f:
                        f.write(code_block)
                    print(f"[Code block saved to {file_path}]")
                except OSError as e:
                    print(f"[Error saving code block: {e}]")
            else:
                print("[No code block found in chat history]")
            continue

        elif user_input.strip().startswith("/d "):
            file_path = user_input.strip()[3:].lstrip()
            try:
                with open(file_path, "w") as f:
                    for message in messages:
                        f.write(f"{json.dumps(message)}\n")
                print(f"[Chat history saved to {file_path}]")
            except OSError as e:
                print(f"[Error saving chat history: {e}]")
            continue

        elif user_input.strip().startswith("/f "):
            file_path = user_input.strip()[3:].lstrip()
            try:
                with open(file_path, "r") as f:
                    file_content = f.read()
                user_input = file_content
                print(f"[File content loaded from {file_path}]")
                messages.append({"role": "user", "content": user_input})
            except OSError as e:
                print(f"[Error loading file: {e}]")
            continue

        elif user_input.strip() == "/l":
            try:
                model_ids = [model.id for model in openai.models.list()]
                print("[" + ", ".join(model_ids) + "]")
            except Exception as e:
                print(f"[Error listing models: {e}]")
            continue

        elif user_input.strip().startswith("/m "):
            new_model = user_input.strip()[3:].lstrip()
            if new_model in [model.id for model in openai.models.list()]:
                config.model = new_model
                print(f"[Model switched to {new_model}]")
            else:
                print(f"[Model {new_model} not found]")
            continue

        elif user_input.strip().startswith("/p "):
            old_config = config
            new_provider = user_input.strip()[3:].lstrip()
            config.api_provider = new_provider
            config_file_data = load_config(config_path)
            setup_config_file_base_url(config, config_file_data)
            if not config.base_url:
                config = old_config
                print(f"[no base-url found for {new_provider}]")
                continue
            setup_config_file_api_key(config, config_file_data)
            if not config.api_key:
                config = old_config
                print(f"[no api-key found for {new_provider}]")
                continue
            setup_config_file_model(config, config_file_data)
            if config.model is None:
                config = old_config
                print(f"[no model found for {new_provider}]")
                continue
            openai.base_url = config.base_url.rstrip('/') + '/'
            openai.api_key = config.api_key
            print(f"[API provider switched to {new_provider}]")
            continue

        elif user_input.strip() == "/t":
            if len(messages) > 2 and messages[-1]["role"] == "assistant" and messages[-2]["role"] == "user":
                messages.pop()  # pop reply
                messages.pop()  # pop prompt
                print("[Last round truncated]")
            elif len(messages) > 1 and messages[-1]["role"] == "user":
                messages.pop()  # pop prompt
                print("[Last prompt truncated]")
            else:
                print("[No rounds to truncate]")
            continue

        elif user_input.strip().startswith("/w "):
            try:
                new_temperature = float(user_input.strip()[3:].lstrip())
                if not (0.0 <= new_temperature <= 2.0):
                    raise ValueError
                config.temperature = new_temperature
                print(f"[Temperature set to {new_temperature}]")
            except ValueError:
                print("[Invalid temperature value]")
            continue

        elif user_input.strip().startswith("/u "):
            file_path = user_input.strip()[3:].lstrip()
            try:
                with open(file_path, "r") as f:
                    # Read the file and parse each line as a JSON object
                    new_messages = []
                    for line in f:
                        try:
                            message = json.loads(line.strip())
                            new_messages.append(message)
                        except json.JSONDecodeError as e:
                            print(f"[Error decoding JSON line: {e}]")
                            continue

                    # Replace the current chat history with the loaded messages
                    if new_messages:
                        messages = new_messages
                        print(f"[Chat history loaded from {file_path}]")
                    else:
                        print(f"[No valid chat history found in {file_path}]")
            except FileNotFoundError:
                print(f"[File not found: {file_path}]")
            except OSError as e:
                print(f"[Error loading chat history: {e}]")
            continue

        elif user_input.strip() == "/b":
            user_input = get_multiline_input()

        elif user_input.strip() == "/0":
            print_reset()
            continue

        elif user_input.strip() == "/\u0065\u0067\u0067":
            user_input = "\U0001F95A"
            print(user_input)

        messages.append({"role": "user", "content": user_input})

        response = create_completion_response(config, messages)
        if not response:
            continue
        while response.choices[0].finish_reason == "function_call":
            function_call = response.choices[0].message.function_call
            print(f"[{function_call.name} called]")
            handle_function_call(messages, function_call)
            response = create_completion_response(config, messages, False)

        output = response.choices[0].message.content
        messages.append({"role": "assistant", "content": output})
        print_fancy(output, config.do_markdown, config.do_latex, config.do_color, config.color)

    print("\n[Exiting chat]")


def setup_config_file_base_url(config, config_file_data):
    config.base_url = None

    if config_file_data and "api_providers" in config_file_data and config_file_data["api_providers"]:
        for provider in config_file_data["api_providers"]:
            if provider["name"] == config.api_provider:
                config.base_url = provider.get("base_url", None)
                break
    if not config.base_url:
        # fallback guesswork attempts
        if config.api_provider in fallbacks.base_urls:
            config.base_url = fallbacks.base_urls[config.api_provider]
            print(f"base-url not configured, trying {config.base_url} for {config.api_provider}", file=sys.stderr)


def setup_config_file_api_key(config, config_file_data):
    config.api_key = None

    if config_file_data and "api_providers" in config_file_data and config_file_data["api_providers"]:
        for provider in config_file_data["api_providers"]:
            if provider["name"] == config.api_provider:
                config.api_key = provider.get("api_key", None)
                break
    if not config.api_key:
        # fallback guesswork attempts
        if config.api_provider in fallbacks.api_keys:
            config.api_key = fallbacks.api_keys[config.api_provider]
            print(f"api_key not configured, trying {config.api_key} for {config.api_provider}", file=sys.stderr)


def setup_config_file_model(config, config_file_data):
    config.model = None

    if config_file_data and "api_providers" in config_file_data and config_file_data["api_providers"]:
        for provider in config_file_data["api_providers"]:
            if provider["name"] == config.api_provider:
                config.model = provider.get("model", None)
                break
    if config.model is None:
        # fallback guesswork attempts
        if config.api_provider in fallbacks.models:
            config.model = fallbacks.models[config.api_provider]
            print(f"model not configured, trying {config.model if config.model else "\"\""} for {config.api_provider}", file=sys.stderr)


def main():
    config = Config()

    help_description = f"{app_name}: Process data from a pipe or file with an OpenAI-compatible API, or chat with it."

    help_epilog = (
        "environment variables:\n"
        "    OPENAI_API_KEY=<key>\n"
        "    OPENAI_BASE_URL=<url>\n\n"
        "configuration file location:\n"
        f"    {config_path}\n\n"
        "configuration precedence (descending):\n"
        "    command line, environment, configuration file"
    )

    parser = argparse.ArgumentParser(description=help_description, epilog=help_epilog, formatter_class=argparse.RawDescriptionHelpFormatter)

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("-c", "--chat", action="store_true", help="Interactive chat (default).")
    mode_group.add_argument("-o", "--oneshot", metavar="<prompt>", help="One-shot chat with the given prompt.")
    mode_group.add_argument("-t", "--transform", metavar="<prompt>", help="Transform data with the given prompt.")
    mode_group.add_argument("-p", "--perform", metavar="<prompt>", help="Perform task on data with the given prompt.")
    mode_group.add_argument("-l", "--list", action="store_true", help="List available models.")

    parser.add_argument("-a", "--api-provider", metavar="<provider>", help="Set API provider (default: first in config file).")
    parser.add_argument("-b", "--base-url", metavar="<url>", help="Set API base URL.")
    parser.add_argument("-k", "--key", metavar="<key>", help="Set API key.")
    parser.add_argument("-m", "--model", metavar="<model>", help="Set model.")
    parser.add_argument("-x", "--max-tokens", type=int, metavar="<max>", help=f"Set maximum number of tokens (default: {config.max_tokens}).")
    parser.add_argument("-w", "--warmth", type=float, metavar="<temperature>", help=f"Set model temperature (default: {config.temperature}).")

    group_interactive = parser.add_argument_group("options for chat/oneshot mode")
    group_interactive.add_argument("--markdown", dest="markdown", action="store_true", help="Enable ANSI escape sequences for markdown.")
    group_interactive.add_argument("--no-markdown", dest="markdown", action="store_false", help="Disable ANSI escape sequences for markdown.")
    group_interactive.add_argument("--color", dest="color", action="store_true", help="Enable ANSI escape sequences for reply color.")
    group_interactive.add_argument("--no-color", dest="color", action="store_false", help="Disable ANSI escape sequences for reply color.")
    group_interactive.add_argument("--latex", dest="latex", action="store_true", help="Enable LaTeX replacement.")
    group_interactive.add_argument("--no-latex", dest="latex", action="store_false", help="Disable LaTeX replacement.")
    group_interactive.add_argument("--func", dest="func", action="store_true", help="Enable OpenAI API function calling feature.")
    group_interactive.add_argument("--no-func", dest="func", action="store_false", help="Disable OpenAI API function calling feature.")
    parser.set_defaults(markdown=None, color=None, latex=None, func=None)

    group_non_interactive = parser.add_argument_group("arguments for transform/perform mode")
    group_non_interactive.add_argument("filenames", nargs="*", help="File(s) to read from (default: stdin)")

    args = parser.parse_args()

    env_api_key = os.getenv("OPENAI_API_KEY")
    env_base_url = os.getenv("OPENAI_BASE_URL")

    config_file_data = load_config(config_path)

    # API-provider
    if args.api_provider:
        # preset to look for in config file
        config.api_provider = args.api_provider
    elif config_file_data and "api_providers" in config_file_data and config_file_data["api_providers"]:
        # use the first preset of config file
        config.api_provider = config_file_data["api_providers"][0].get("name", None)

    # Base-URL
    if args.base_url:
        config.base_url = args.base_url
    elif env_base_url:
        config.base_url = env_base_url
    elif config.api_provider:
        setup_config_file_base_url(config, config_file_data)
    if not config.base_url:
        print("base-url not configured", file=sys.stderr)
        sys.exit(1)

    # API-key
    if args.key is not None:
        config.api_key = args.key
    elif env_api_key is not None:
        config.api_key = env_api_key
    elif config.api_provider:
        setup_config_file_api_key(config, config_file_data)
    if not config.api_key:
        print("api_key not configured", file=sys.stderr)
        sys.exit(1)

    openai.base_url = config.base_url.rstrip('/') + '/'
    openai.api_key = config.api_key

    # List
    if args.list:  # We don't need more parameters for this.
        try:
            for model in openai.models.list():
                print(model.id)
        except Exception as e:
            print(f"Error listing models: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    # Model
    if args.model:
        config.model = args.model
    elif config.api_provider:
        setup_config_file_model(config, config_file_data)
    if config.model is None:
        print("model not configured", file=sys.stderr)
        sys.exit(1)

    # Temperature
    if args.warmth is not None:
        config.temperature = args.warmth
    elif config_file_data and "global_options" in config_file_data:
        config.temperature = config_file_data["global_options"].get("temperature", config.temperature)

    # Max tokens
    if args.max_tokens is not None:
        config.max_tokens = args.max_tokens
    elif config_file_data and "global_options" in config_file_data:
        config.max_tokens = config_file_data["global_options"].get("max_tokens", config.max_tokens)

    # Features for chat modes
    if args.markdown is not None:
        config.do_markdown = args.markdown
    elif config_file_data and "global_options" in config_file_data:
        config.do_markdown = config_file_data["global_options"].get("markdown", config.do_markdown)

    if args.color is not None:
        config.do_color = args.color
    elif config_file_data and "global_options" in config_file_data:
        config.do_color = config_file_data["global_options"].get("color", config.do_color)

    if config_file_data and "global_options" in config_file_data:
        config.color = config_file_data["global_options"].get("color_name", config.color).lower().replace('-', '_').replace(' ', '_')

    if args.latex is not None:
        config.do_latex = args.latex
    elif config_file_data and "global_options" in config_file_data:
        config.do_latex = config_file_data["global_options"].get("latex", config.do_latex)

    if args.func is not None:
        config.func = args.func
    elif config_file_data and "global_options" in config_file_data:
        config.func = config_file_data["global_options"].get("func", config.func)

    del config_file_data

    # Main logic
    if args.oneshot:
        run_oneshot(config, args.oneshot)
    elif args.transform:
        run_transform(config, args.transform, args.filenames)
    elif args.perform:
        run_perform(config, args.perform, args.filenames)
    else:  # args.chat
        run_chat(config)


if __name__ == "__main__":
    main()
