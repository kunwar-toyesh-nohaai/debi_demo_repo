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
from confirmation_handler import (
    confirm_git_commit, 
    RestartFlowException,
    AFFIRMATIVE_CUES,
    NEGATIVE_CUES
)
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
    print("The following files are pending commit. Please review and confirm.")
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
        # Raise exception to restart the flow
        raise RestartFlowException("User declined commit confirmation")

    logger.info("User confirmed commit from post-run prompt.")
    result = _commit_changes(commit_message)
    logger.info(f"Commit result: {result}")
    print(result)
    reset_applied_file_changes()
    print("=" * 60)
    print("Thanks for confirming those changes.")
    print("=" * 60)

def main():
    """Main CLI function."""
    logger.info("=" * 60)
    logger.info("AI Code Debugging Agent")
    logger.info("=" * 60)
    logger.info("")
    
    while True:
        try:
            # Step 1 & 2: greet and capture the bug description
            print("Hi, I'm Debi. I do full stack development. What would you like me to help you with?")
            print()
            print("Please describe the issue (press Enter twice to finish).")
            print()
            lines: List[str] = []
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
            
            # Step 3: capture the repo URL (simulated)
            print()
            print("Can you give me the URL to the codebase that you're referring to?")
            repo_url_input = input("Repository URL: ").strip()
            
            # Check if user actually provided a repo URL or declined
            if not repo_url_input:
                logger.info("User did not provide repository URL")
                print()
                print("I'll need the repository URL to continue. Let me start over.")
                print()
                raise RestartFlowException("User did not provide repository URL")
            
            # Check if input looks like a valid git repository URL
            normalized_repo_input = repo_url_input.lower()
            looks_like_url = (
                repo_url_input.startswith("http://") or
                repo_url_input.startswith("https://") or
                repo_url_input.startswith("git@") or
                repo_url_input.startswith("git://") or
                ("github.com" in normalized_repo_input) or
                ("gitlab.com" in normalized_repo_input) or
                ("bitbucket.org" in normalized_repo_input) or
                (".git" in normalized_repo_input)
            )
            
            # Check if user declined (said "no" or similar) - but only if it doesn't look like a URL
            declined = False
            if not looks_like_url:
                for cue in NEGATIVE_CUES:
                    if cue in normalized_repo_input:
                        declined = True
                        break
            
            if declined:
                logger.info("User declined to provide repository URL")
                print()
                print("I'll need the repository URL to continue. Let me start over.")
                print()
                raise RestartFlowException("User declined to provide repository URL")
            
            # If it doesn't look like a URL and wasn't declined, it's invalid
            if not looks_like_url:
                logger.info(f"Invalid repository URL provided: {repo_url_input}")
                print()
                print("That doesn't look like a valid repository URL. Let me start over.")
                print()
                raise RestartFlowException("Invalid repository URL provided")
            
            # User provided a valid-looking URL
            repo_url = repo_url_input
            logger.info(f"Repo URL provided: {repo_url}")
            
            # Step 4 & 5: ask for credential usage with intent detection
            print()
            print("Okay, can I use your credentials in my context to pull the repo?")
            credential_response = input("Your response: ").strip()
            
            # Detect intent using conversational cues
            normalized_response = credential_response.lower()
            granted = None  # None means unclear intent
            
            if not normalized_response:
                # Empty response defaults to yes for demo flow
                granted = True
            else:
                # Check for affirmative cues first
                for cue in AFFIRMATIVE_CUES:
                    if cue in normalized_response:
                        granted = True
                        break
                
                # If no affirmative found, check for negative cues
                if granted is None:
                    for cue in NEGATIVE_CUES:
                        if cue in normalized_response:
                            granted = False
                            break
                
                # If intent is still unclear, default to yes for demo flow
                if granted is None:
                    granted = True
            
            if not granted:
                logger.info("User declined to grant credential access")
                print()
                print("In that case, I won't be able to pull the repo. Is there anything else you need help with?")
                print()
                raise RestartFlowException("User declined credential access")
            
            print("Great, thanks for granting access.")
            logger.info("Repo access permission granted.")
            
            # Step 6: simulate pulling the repository before initializing the agent
            print()
            print(f"Perfect, let me pull {repo_url} and start debugging.")
            print()
            logger.info("Initializing agent...")
            print("I'm initializing my debugging tools...")
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
            print("I'm analyzing the bug. This may take a moment...")
            logger.info("Starting agent execution...")
            print()
            
            response = run_agent(agent, bug_description)
            logger.info("Agent execution completed")
            print("=" * 60)
            print("Here's what I found. Want to see the suggested fix?")
            print("=" * 60)
            input("Press Enter to view the diagnosis and suggested fix: ")
            print()
            logger.info("Agent Response:")
            logger.info(response)
            print(response)
            print()
            # After agent output, prompt for commit if files were modified
            prompt_commit_for_pending_changes(response)
            
            # If we get here, everything completed successfully
            break
            
        except RestartFlowException:
            # User said no to a confirmation, restart from the beginning
            print()
            print("=" * 60)
            print("I understand. Let me start over from the beginning.")
            print("=" * 60)
            print()
            reset_applied_file_changes()
            continue
        except KeyboardInterrupt:
            error_msg = "\n\nOperation cancelled by user."
            logger.warning("Operation cancelled by user (KeyboardInterrupt)")
            print(error_msg)
            reset_applied_file_changes()
            sys.exit(0)
        except Exception as e:
            error_msg = f"Error running agent: {e}"
            logger.exception(f"Exception in main loop: {error_msg}")
            print(error_msg)
            reset_applied_file_changes()
            sys.exit(1)


if __name__ == "__main__":
    main()

