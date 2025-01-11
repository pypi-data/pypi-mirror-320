"""
Utility functions for LLM Chat
"""

import tiktoken
import textwrap
from rich.console import Console
from rich.markdown import Markdown

def count_tokens(text, model):
    """
    Count tokens in the given text.
    
    Args:
        text (str): The text to count tokens for
        model (str): The model name (currently unused, but kept for future model-specific counting)
    
    Returns:
        int: Number of tokens in the text
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def print_wrapped_text(text, width=80, indent="  "):
    """
    Print text with proper wrapping.
    
    Args:
        text (str): The text to wrap and print
        width (int): Maximum line width
        indent (str): Indentation string to prepend to each line
    """
    wrapped_lines = textwrap.wrap(text, width=width)
    for line in wrapped_lines:
        print(f"{indent}{line}")

def render_markdown(text):
    """
    Render text as markdown.
    
    Args:
        text (str): The markdown text to render
    """
    console = Console()
    md = Markdown(text)
    console.print(md)