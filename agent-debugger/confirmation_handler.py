"""Confirmation handler for file writes and git commits."""

import logging
import os
import subprocess
from difflib import unified_diff
from typing import Optional, Tuple

logger = logging.getLogger("agent_debugger.confirmation")

# Common conversational intents
AFFIRMATIVE_CUES = {
    "y",
    "yes",
    "yeah",
    "yep",
    "sure",
    "sounds good",
    "go ahead",
    "do it",
    "please do",
    "absolutely",
    "of course",
    "looks good",
    "looks good to me",
    "ship it",
    "confirm",
    "okay",
    "ok",
    "k",
    "kk",
    "let's do it",
    "let's go",
    "make it happen",
}

NEGATIVE_CUES = {
    "n",
    "no",
    "nah",
    "nope",
    "don't",
    "do not",
    "stop",
    "hold on",
    "wait",
    "cancel",
    "not yet",
    "skip",
    "maybe later",
}


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


def _interpret_conversational_response(response: str, default: bool) -> bool:
    """Infer confirmation intent from free-form responses."""
    normalized = response.strip().lower()

    if not normalized:
        return default

    for cue in AFFIRMATIVE_CUES:
        if cue in normalized:
            return True

    for cue in NEGATIVE_CUES:
        if cue in normalized:
            return False

    # Fall back to default when intent is unclear
    return default


def _summarize_diff(diff: str) -> Tuple[int, int, str]:
    """
    Provide quick stats and touched sections extracted from the diff.

    Returns:
        Tuple of (added_lines, removed_lines, hunk_summary_text)
    """
    added = 0
    removed = 0
    hunks = []

    for line in diff.splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        if line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            removed += 1
        elif line.startswith("@@"):
            hunks.append(line.strip())

    hunk_summary = (
        "\n".join(f"- {hunk}" for hunk in hunks) if hunks else "- Entire file (no specific hunks reported)"
    )
    return added, removed, hunk_summary


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
    print("CONVERSATIONAL CHECK-IN")
    print("=" * 80)
    print(prompt)
    print("\nFeel free to respond conversationally (e.g., 'yeah sure', 'looks good to me').")
    
    response = input("Your response: ")
    result = _interpret_conversational_response(response, default)
    
    logger.info(f"User response: {response!r} -> {result}")
    print()
    
    return result


def confirm_file_write(file_path: str, new_content: str, issue_summary: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Show file changes and ask for confirmation before writing.
    
    Args:
        file_path: Path to the file to write
        new_content: New content to write
        issue_summary: Optional textual explanation of the bug/root cause
        
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
    added, removed, hunk_summary = _summarize_diff(diff)
    
    logger.info("=" * 80)
    logger.info("PROPOSED FILE CHANGES")
    logger.info("=" * 80)
    logger.info(f"File: {file_path}")
    logger.info("\n" + diff)
    
    # Stage 1: make sure the user wants suggestions
    summary_block = ""
    if issue_summary:
        summary_block = f"""
Here's how the agent described the underlying issue:
{issue_summary.strip()}
"""
    else:
        summary_block = "\n(The agent did not provide any additional context about the issue.)\n"
    
    suggestion_intro = f"""
The agent believes the issue you reported stems from `{file_path}`.
{summary_block}
Would you like to review its suggestions before we touch the file?
"""
    wants_suggestions = ask_confirmation(suggestion_intro, default=True)
    
    if not wants_suggestions:
        logger.warning(f"User declined suggestions for: {file_path}")
        return False, "User declined to review the suggested fix"
    
    suggestions_text = f"""
Suggested plan for `{file_path}`:
- Adds approximately {added} line(s), removes {removed} line(s)
- Touches these areas:
{hunk_summary}

Issue summary:
{issue_summary.strip() if issue_summary else '(not provided)'}

Detailed diff:
{'=' * 80}
{diff or '(No textual diff – likely a new binary file)'}
{'=' * 80}

Should I go ahead and apply these changes now?
"""
    
    confirmed = ask_confirmation(suggestions_text, default=False)
    
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
    
    conversational_prompt = f"""
I'm ready to commit the latest fixes with the message:
  "{commit_message}"

{prompt}

Does that sound good, or would you prefer to hold off?
"""
    
    confirmed = ask_confirmation(conversational_prompt, default=False)
    
    if confirmed:
        logger.info(f"User confirmed git commit with message: {commit_message}")
        return True, None
    else:
        logger.warning(f"User rejected git commit with message: {commit_message}")
        return False, "Git commit cancelled by user"

