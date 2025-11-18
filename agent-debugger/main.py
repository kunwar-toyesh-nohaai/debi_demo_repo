"""Main CLI entry point for the debugging agent."""

import os
import sys
from typing import List, Optional
from dotenv import load_dotenv
from agent_loop import (
    create_agent,
    run_agent,
    get_applied_file_changes,
    reset_applied_file_changes,
)
from logging_config import setup_logging
from confirmation_handler import confirm_git_commit
from tools.git_tools import commit_changes as _commit_changes

# Set up logging first
logger = setup_logging()

# Load environment variables from .env file if it exists
path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(path)

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    logger.error("GOOGLE_API_KEY environment variable is not set")
    raise ValueError("GOOGLE_API_KEY environment variable is not set")


def _derive_commit_message(agent_summary: Optional[str]) -> str:
    """Create an actionable suggested commit message from the agent summary."""
    default_message = "fix: apply debugging fix"
    if not agent_summary:
        return default_message

    candidate = None
    for line in agent_summary.splitlines():
        cleaned = line.strip().strip("#*- ")
        if cleaned:
            candidate = cleaned
            break

    if not candidate:
        return default_message

    lower = candidate.lower()
    if lower.startswith("the bug was in"):
        candidate = candidate.replace("The bug was ", "Fix ", 1)
    elif not (candidate.lower().startswith("fix") or candidate.lower().startswith("feat") or candidate.lower().startswith("chore")):
        candidate = f"fix: {candidate}"

    if len(candidate) > 72:
        candidate = candidate[:69].rstrip() + "..."

    return candidate


def prompt_commit_for_pending_changes(agent_summary: Optional[str]) -> None:
    """After file writes, ask the user if they want to commit."""
    modified_files = get_applied_file_changes()

    if not modified_files:
        logger.info("No file changes recorded; skipping commit prompt.")
        return

    logger.info("=" * 80)
    logger.info("PENDING FILE CHANGES DETECTED")
    logger.info("=" * 80)
    for path in modified_files:
        logger.info(f"- {path}")

    print("=" * 80)
    print("Files modified during this session:")
    print("=" * 80)
    for path in modified_files:
        print(f"- {path}")
    print("=" * 80)

    suggested_message = _derive_commit_message(agent_summary)
    print("Suggested commit message:")
    print(f"  {suggested_message}")
    print("Press Enter to accept the suggestion, type a custom message to edit it,")
    print("or type 'skip' to leave the changes uncommitted.")

    user_input = input("Commit message [press Enter to accept suggestion]: ").strip()

    if user_input.lower() == "skip":
        logger.info("User chose to skip committing changes.")
        print("Changes left uncommitted.")
        reset_applied_file_changes()
        return

    commit_message = user_input or suggested_message

    confirmed, error = confirm_git_commit(commit_message)

    if not confirmed:
        if error:
            logger.error(f"Commit skipped: {error}")
            print(f"Commit skipped: {error}")
        else:
            logger.info("Commit cancelled by user.")
            print("Commit cancelled. Changes remain uncommitted.")
        reset_applied_file_changes()
        return

    logger.info("User confirmed commit from post-run prompt.")
    result = _commit_changes(commit_message)
    logger.info(f"Commit result: {result}")
    print(result)
    reset_applied_file_changes()

def main():
    """Main CLI function."""
    logger.info("=" * 60)
    logger.info("AI Code Debugging Agent")
    logger.info("=" * 60)
    logger.info("")
    # Get bug description from user
    print("Please describe the bug you'd like me to debug:")
    print("(Press Enter twice or Ctrl+Z then Enter on Windows to finish)")
    logger.info("Waiting for user input...")
    print()
    
    lines = []
    try:
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
    except EOFError:
        pass
    
    bug_description = "\n".join(lines).strip()
    
    if not bug_description:
        error_msg = "Error: Bug description cannot be empty."
        logger.error(error_msg)
        print(error_msg)
        sys.exit(1)
    
    logger.info(f"Bug description received: {len(bug_description)} characters")
    logger.debug(f"Bug description: {bug_description}")
    
    print()
    logger.info("Initializing agent...")
    print("Initializing agent...")
    print()
    
    # Create agent
    try:
        agent = create_agent(api_key)
        logger.info("Agent created successfully")
    except Exception as e:
        error_msg = f"Error creating agent: {e}"
        logger.exception(error_msg)
        print(error_msg)
        sys.exit(1)
    
    # Run agent
    print("Agent is analyzing the bug. This may take a moment...")
    logger.info("Starting agent execution...")
    print()
    
    try:
        response = run_agent(agent, bug_description)
        logger.info("Agent execution completed")
        print("=" * 60)
        print("Agent Response:")
        print("=" * 60)
        logger.info("Agent Response:")
        logger.info(response)
        print(response)
        print()
        # After agent output, prompt for commit if files were modified
        prompt_commit_for_pending_changes(response)
    except KeyboardInterrupt:
        error_msg = "\n\nOperation cancelled by user."
        logger.warning("Operation cancelled by user (KeyboardInterrupt)")
        print(error_msg)
        reset_applied_file_changes()
        sys.exit(0)
    except Exception as e:
        error_msg = f"Error running agent: {e}"
        logger.exception(error_msg)
        print(error_msg)
        reset_applied_file_changes()
        sys.exit(1)


if __name__ == "__main__":
    main()

