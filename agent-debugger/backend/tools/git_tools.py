"""Git operations tools for the debugging agent."""

import logging
import subprocess
import traceback

logger = logging.getLogger("agent_debugger.git_tools")


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
        error_msg = f"Error: Git command '{cmd}' timed out after 30 seconds."
        logger.error(error_msg)
        logger.debug(traceback.format_exc())
        return error_msg
    except FileNotFoundError:
        error_msg = "Error: Git is not installed or not found in PATH."
        logger.error(error_msg)
        logger.debug(traceback.format_exc())
        return error_msg
    except Exception as e:
        error_msg = f"Error running git command '{cmd}': {str(e)}"
        logger.exception(f"Exception in run_git_command: {error_msg}")
        return error_msg


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
            # Try to get error from stderr first, then stdout, then provide a generic message
            error_msg = stage_result.stderr.strip() if stage_result.stderr else ""
            if not error_msg and stage_result.stdout:
                error_msg = stage_result.stdout.strip()
            if not error_msg:
                error_msg = f"Git add failed with return code {stage_result.returncode}"
            
            logger.error(f"Git staging failed: {error_msg}")
            logger.debug(f"Git staging stdout: {stage_result.stdout}")
            logger.debug(f"Git staging stderr: {stage_result.stderr}")
            logger.debug(f"Git staging returncode: {stage_result.returncode}")
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
            # Try to get error from stderr first, then stdout, then provide a generic message
            error_msg = commit_result.stderr.strip() if commit_result.stderr else ""
            stdout_msg = commit_result.stdout.strip() if commit_result.stdout else ""
            
            # Check for common git commit failure scenarios
            combined_output = (error_msg + " " + stdout_msg).lower()
            if "nothing to commit" in combined_output or "no changes" in combined_output:
                error_msg = "Nothing to commit - working tree is clean (no changes detected)"
            elif not error_msg and stdout_msg:
                error_msg = stdout_msg
            elif not error_msg:
                error_msg = f"Git commit failed with return code {commit_result.returncode}"
            
            logger.error(f"Git commit failed: {error_msg}")
            logger.debug(f"Git commit stdout: {commit_result.stdout}")
            logger.debug(f"Git commit stderr: {commit_result.stderr}")
            logger.debug(f"Git commit returncode: {commit_result.returncode}")
            return f"Error committing changes: {error_msg}"
        
        return f"Successfully committed changes with message: '{message}'"
    except subprocess.TimeoutExpired:
        error_msg = "Error: Git commit operation timed out."
        logger.error(error_msg)
        logger.debug(traceback.format_exc())
        return error_msg
    except FileNotFoundError:
        error_msg = "Error: Git is not installed or not found in PATH."
        logger.error(error_msg)
        logger.debug(traceback.format_exc())
        return error_msg
    except Exception as e:
        error_msg = f"Error committing changes: {str(e)}"
        logger.exception(f"Exception in commit_changes: {error_msg}")
        return error_msg

