"""Confirmation handler for file writes and git commits."""

import os
import sys
import subprocess
import logging
from typing import Optional, Tuple
from difflib import unified_diff

logger = logging.getLogger("agent_debugger.confirmation")


def show_diff(file_path: str, old_content: str, new_content: str) -> str:
    """
    Generate and return a unified diff between old and new content.
    
    Args:
        file_path: Path to the file being changed
        old_content: Current file content
        new_content: Proposed new content
        
    Returns:
        Formatted diff string
    """
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = unified_diff(
        old_lines,
        new_lines,
        fromfile=f"{file_path} (current)",
        tofile=f"{file_path} (proposed)",
        lineterm=''
    )
    
    return ''.join(diff)


def ask_confirmation(prompt: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        prompt: The confirmation prompt to display
        default: Default value if user just presses Enter
        
    Returns:
        True if confirmed, False otherwise
    """
    logger.info("=" * 80)
    logger.info("CONFIRMATION REQUESTED")
    logger.info("=" * 80)
    logger.info(prompt)
    
    print("\n" + "=" * 80)
    print("CONFIRMATION REQUESTED")
    print("=" * 80)
    print(prompt)
    
    if default:
        response = input("Confirm? [Y/n]: ").strip().lower()
        result = response != 'n'
    else:
        response = input("Confirm? [y/N]: ").strip().lower()
        result = response == 'y'
    
    logger.info(f"User response: {response} -> {result}")
    print()
    
    return result


def confirm_file_write(file_path: str, new_content: str) -> Tuple[bool, Optional[str]]:
    """
    Show file changes and ask for confirmation before writing.
    
    Args:
        file_path: Path to the file to write
        new_content: New content to write
        
    Returns:
        Tuple of (confirmed: bool, error_message: Optional[str])
    """
    logger.info(f"File write requested for: {file_path}")
    
    # Read current content if file exists
    old_content = ""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                old_content = f.read()
            logger.debug(f"Read existing file content ({len(old_content)} chars)")
        except Exception as e:
            error_msg = f"Error reading existing file: {e}"
            logger.error(error_msg)
            return False, error_msg
    else:
        logger.info(f"File does not exist, will create new file: {file_path}")
    
    # Generate diff
    diff = show_diff(file_path, old_content, new_content)
    
    # Log the diff
    logger.info("=" * 80)
    logger.info("PROPOSED FILE CHANGES")
    logger.info("=" * 80)
    logger.info(f"File: {file_path}")
    logger.info("\n" + diff)
    
    # Show diff to user
    prompt = f"""
File: {file_path}
{'=' * 80}

PROPOSED CHANGES:
{diff}
{'=' * 80}

Do you want to apply these changes to {file_path}?
"""
    
    confirmed = ask_confirmation(prompt, default=False)
    
    if confirmed:
        logger.info(f"User confirmed file write for: {file_path}")
        return True, None
    else:
        logger.warning(f"User rejected file write for: {file_path}")
        return False, "File write cancelled by user"


def confirm_git_commit(commit_message: str) -> Tuple[bool, Optional[str]]:
    """
    Show what will be committed and ask for confirmation.
    
    Args:
        commit_message: The commit message
        
    Returns:
        Tuple of (confirmed: bool, error_message: Optional[str])
    """
    logger.info(f"Git commit requested with message: {commit_message}")
    
    # Get git status to show what will be committed
    try:
        status_result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        diff_result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        staged_files = status_result.stdout.strip()
        diff_output = diff_result.stdout.strip()
        
        logger.info("=" * 80)
        logger.info("PROPOSED GIT COMMIT")
        logger.info("=" * 80)
        logger.info(f"Commit message: {commit_message}")
        logger.info(f"Staged files:\n{staged_files}")
        if diff_output:
            logger.info(f"Changes to be committed:\n{diff_output}")
        else:
            logger.info("No staged changes (will stage all changes)")
        
        # Show to user
        prompt = f"""
COMMIT MESSAGE: {commit_message}
{'=' * 80}

STAGED FILES:
{staged_files if staged_files else '(will stage all changes)'}
{'=' * 80}
"""
        
        if diff_output:
            prompt += f"""
CHANGES TO BE COMMITTED:
{diff_output}
{'=' * 80}
"""
        
        prompt += f"\nDo you want to commit these changes with the message: '{commit_message}'?"
        
    except Exception as e:
        logger.warning(f"Could not get git status: {e}")
        prompt = f"""
COMMIT MESSAGE: {commit_message}
{'=' * 80}

Do you want to commit all changes with this message?
"""
    
    confirmed = ask_confirmation(prompt, default=False)
    
    if confirmed:
        logger.info(f"User confirmed git commit with message: {commit_message}")
        return True, None
    else:
        logger.warning(f"User rejected git commit with message: {commit_message}")
        return False, "Git commit cancelled by user"

