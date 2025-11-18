"""File manipulation tools for the debugging agent."""

import os
from typing import List, Union


def list_directory(path: str) -> Union[List[str], str]:
    """
    List all files and directories in the given path.
    
    Args:
        path: The directory path to list.
        
    Returns:
        List of file and directory names, or an error message string if an exception occurs.
    """
    try:
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist."
        
        if not os.path.isdir(path):
            return f"Error: '{path}' is not a directory."
        
        items = os.listdir(path)
        return items
    except PermissionError as e:
        return f"Error: Permission denied accessing '{path}': {str(e)}"
    except Exception as e:
        return f"Error listing directory '{path}': {str(e)}"


def read_file(path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
        path: The file path to read.
        
    Returns:
        File contents as a string, or an error message string if an exception occurs.
    """
    try:
        if not os.path.exists(path):
            return f"Error: File '{path}' does not exist."
        
        if not os.path.isfile(path):
            return f"Error: '{path}' is not a file."
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except PermissionError as e:
        return f"Error: Permission denied reading '{path}': {str(e)}"
    except UnicodeDecodeError as e:
        return f"Error: Unable to decode file '{path}' as UTF-8. It may be a binary file: {str(e)}"
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"


def write_file(path: str, content: str) -> str:
    """
    Write content to a file.
    
    Args:
        path: The file path to write to.
        content: The content to write to the file.
        
    Returns:
        Success message string, or an error message string if an exception occurs.
    """
    try:
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote content to '{path}'."
    except PermissionError as e:
        return f"Error: Permission denied writing to '{path}': {str(e)}"
    except OSError as e:
        return f"Error: OS error writing to '{path}': {str(e)}"
    except Exception as e:
        return f"Error writing file '{path}': {str(e)}"

