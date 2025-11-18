"""Git operations tools for the debugging agent."""

import subprocess


def run_git_command(cmd: str, cwd: str = ".") -> str:
    """
    Run a git command and return the output.
    
    Args:
        cmd: The git command to run (e.g., "status", "diff", "log --oneline").
        cwd: The working directory where the command should be executed.
        
    Returns:
        Command output as a string, or an error message if the command fails.
    """
    try:
        # Split the command into parts
        git_cmd = ["git"] + cmd.split()
        
        result = subprocess.run(
            git_cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown git error"
            return f"Error running git command '{cmd}': {error_msg}"
        
        return result.stdout.strip() if result.stdout else "Command executed successfully (no output)."
    except subprocess.TimeoutExpired:
        return f"Error: Git command '{cmd}' timed out after 30 seconds."
    except FileNotFoundError:
        return "Error: Git is not installed or not found in PATH."
    except Exception as e:
        return f"Error running git command '{cmd}': {str(e)}"


def commit_changes(message: str, cwd: str = ".") -> str:
    """
    Stage all changes and commit them with the given message.
    
    Args:
        message: The commit message.
        cwd: The working directory where the git repository is located.
        
    Returns:
        Success message or error message string.
    """
    try:
        # Check if we're in a git repository
        check_result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if check_result.returncode != 0:
            return f"Error: '{cwd}' is not a git repository."
        
        # Stage all changes
        stage_result = subprocess.run(
            ["git", "add", "-A"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if stage_result.returncode != 0:
            error_msg = stage_result.stderr.strip() if stage_result.stderr else "Unknown error"
            return f"Error staging changes: {error_msg}"
        
        # Commit the changes
        commit_result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if commit_result.returncode != 0:
            error_msg = commit_result.stderr.strip() if commit_result.stderr else "Unknown error"
            return f"Error committing changes: {error_msg}"
        
        return f"Successfully committed changes with message: '{message}'"
    except subprocess.TimeoutExpired:
        return "Error: Git commit operation timed out."
    except FileNotFoundError:
        return "Error: Git is not installed or not found in PATH."
    except Exception as e:
        return f"Error committing changes: {str(e)}"

