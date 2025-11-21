"""Agent loop implementation using LangChain."""

import logging
from langchain.agents import create_react_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain import hub
from langchain_core.callbacks import BaseCallbackHandler
from typing import List, Any, Dict, Optional

from tools.file_tools import list_directory, read_file, write_file as _write_file
from tools.git_tools import run_git_command, commit_changes as _commit_changes
from prompts import SYSTEM_PROMPT
from confirmation_handler import confirm_file_write, confirm_git_commit, RestartFlowException

# Set up logger
logger = logging.getLogger("agent_debugger")

# Track which files have been modified during a run
APPLIED_FILE_CHANGES: List[str] = []


def _record_file_change(file_path: str) -> None:
    """Record that a file has been modified."""
    normalized = file_path.strip()
    if normalized and normalized not in APPLIED_FILE_CHANGES:
        APPLIED_FILE_CHANGES.append(normalized)


def get_applied_file_changes() -> List[str]:
    """Return a copy of the list of modified files."""
    return APPLIED_FILE_CHANGES.copy()


def reset_applied_file_changes() -> None:
    """Clear the list of recorded file changes."""
    APPLIED_FILE_CHANGES.clear()


def _extract_issue_summary(section: str) -> Optional[str]:
    """
    Normalize and extract the agent-provided issue summary block.
    
    The agent is expected to provide a block that begins with one of:
    "ISSUE SUMMARY:", "ISSUE:", or "SUMMARY:". Any remaining text is
    treated as the issue description we can surface to the user.
    """
    cleaned = section.strip()
    if not cleaned:
        return None
    
    upper_clean = cleaned.upper()
    markers = ("ISSUE SUMMARY:", "ISSUE:", "SUMMARY:")
    for marker in markers:
        if upper_clean.startswith(marker):
            return cleaned[len(marker):].strip()
    return cleaned


class LoggingCallbackHandler(BaseCallbackHandler):
    """Callback handler to log LangChain agent execution steps."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("agent_debugger.agent_steps")
    
    def on_agent_action(self, action: Any, **kwargs: Any) -> None:
        """Log when agent takes an action."""
        try:
            # AgentAction is an object, access attributes directly
            tool_name = getattr(action, "tool", "Unknown")
            tool_input = getattr(action, "tool_input", "")
            self.logger.info("=" * 80)
            self.logger.info(f"AGENT ACTION: {tool_name}")
            self.logger.info("=" * 80)
            self.logger.info(f"Tool: {tool_name}")
            self.logger.info(f"Tool Input: {tool_input}")
            self.logger.info("=" * 80)
        except Exception as e:
            # Fallback: try as dict if it's actually a dict
            try:
                tool_name = action.get("tool", "Unknown") if isinstance(action, dict) else str(action)
                tool_input = action.get("tool_input", "") if isinstance(action, dict) else ""
                self.logger.info("=" * 80)
                self.logger.info(f"AGENT ACTION: {tool_name}")
                self.logger.info("=" * 80)
                self.logger.info(f"Tool: {tool_name}")
                self.logger.info(f"Tool Input: {tool_input}")
                self.logger.info("=" * 80)
            except Exception as fallback_error:
                self.logger.exception(f"Exception in on_agent_action fallback: {fallback_error}")
                self.logger.info("=" * 80)
                self.logger.info("AGENT ACTION (raw)")
                self.logger.info("=" * 80)
                self.logger.debug(f"Raw action: {action}")
    
    def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        """Log when agent finishes."""
        try:
            # AgentFinish is an object, access attributes directly
            return_values = getattr(finish, "return_values", {})
            if isinstance(return_values, dict):
                output = return_values.get("output", "")
            else:
                output = getattr(return_values, "output", str(return_values))
            self.logger.info("Agent finished execution")
            self.logger.debug(f"Agent output: {output}")
        except Exception as e:
            # Fallback: try as dict if it's actually a dict
            try:
                if isinstance(finish, dict):
                    output = finish.get("return_values", {}).get("output", "")
                else:
                    output = str(finish)
                self.logger.info("Agent finished execution")
                self.logger.debug(f"Agent output: {output}")
            except Exception as fallback_error:
                self.logger.exception(f"Exception in on_agent_finish fallback: {fallback_error}")
                self.logger.debug(f"Agent Finish (raw): {finish}")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Log when a tool starts."""
        try:
            tool_name = serialized.get("name", "Unknown") if isinstance(serialized, dict) else str(serialized)
            self.logger.info("=" * 80)
            self.logger.info(f"TOOL EXECUTION STARTED: {tool_name}")
            self.logger.info("=" * 80)
            self.logger.info(f"Tool: {tool_name}")
            self.logger.info(f"Input: {input_str}")
            self.logger.info("=" * 80)
        except Exception as e:
            self.logger.exception(f"Exception in on_tool_start: {e}")
            self.logger.info("=" * 80)
            self.logger.info("TOOL EXECUTION STARTED (raw)")
            self.logger.info("=" * 80)
            self.logger.debug(f"Serialized: {serialized}, Input: {input_str}")
    
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Log when a tool ends."""
        try:
            self.logger.info("=" * 80)
            self.logger.info("TOOL EXECUTION COMPLETED")
            self.logger.info("=" * 80)
            self.logger.info(f"Output: {output}")
            self.logger.info("=" * 80)
        except Exception as e:
            self.logger.exception(f"Exception in on_tool_end: {e}")
            self.logger.info("=" * 80)
            self.logger.info("TOOL EXECUTION COMPLETED (raw)")
            self.logger.info("=" * 80)
            self.logger.debug(f"Output: {output}")
    
    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Log tool errors."""
        try:
            self.logger.exception(f"Tool error occurred: {error}")
        except Exception as e:
            self.logger.exception(f"Exception in on_tool_error while logging: {e}, original error: {error}")


def write_file_wrapper(input_str: str) -> str:
    """
    Wrapper for write_file that parses LangChain tool input and asks for confirmation.
    
    Expected format: 
        FILEPATH: <path>
        ISSUE SUMMARY:
        <why the change is needed / description of the bug>
        CONTENT:
        <content>
    A legacy format of "<path>|<content>" is still accepted for backward compatibility,
    but the ISSUE SUMMARY block is strongly encouraged so the user understands the fix.
    
    Args:
        input_str: String containing file path and content.
        
    Returns:
        Result from write_file function or cancellation message.
    """
    logger.info("=" * 80)
    logger.info("WRITE_FILE TOOL CALLED")
    logger.info("=" * 80)
    logger.debug(f"Input received: {input_str[:200]}...")  # Log first 200 chars
    
    issue_summary: Optional[str] = None
    lines = input_str.split('\n', 1)
    if len(lines) < 2:
        # Try alternative format: path|content
        if '|' in input_str:
            parts = input_str.split('|', 1)
            if len(parts) == 2:
                path = parts[0].strip()
                content = parts[1]
            else:
                return "Error: Invalid format. Expected 'FILEPATH: <path>\\nCONTENT:\\n<content>' or '<path>|<content>'"
        else:
            return "Error: Invalid format. Expected 'FILEPATH: <path>\\nCONTENT:\\n<content>' or '<path>|<content>'"
    else:
        remainder = lines[1]
        # Parse FILEPATH: ... format
        if lines[0].startswith('FILEPATH:'):
            path = lines[0].replace('FILEPATH:', '').strip()
        else:
            path = lines[0].strip()
        
        # Detect optional issue summary block before CONTENT:
        upper_remainder = remainder.upper()
        content_marker = "CONTENT:"
        issue_summary = None
        content_section = remainder
        
        marker_index = upper_remainder.find(content_marker)
        if marker_index != -1:
            before_content = remainder[:marker_index]
            content_section = remainder[marker_index + len(content_marker):]
            issue_summary = _extract_issue_summary(before_content)
        else:
            issue_summary = None
        
        content = content_section.lstrip('\n')
    
    logger.info(f"Parsed file path: {path}")
    logger.debug(f"Content length: {len(content)} characters")
    if issue_summary:
        logger.debug(f"Issue summary provided: {issue_summary[:200]}{'...' if len(issue_summary) > 200 else ''}")
    else:
        logger.debug("No issue summary provided with write_file request")
    
    # Ask for confirmation before writing
    # This may raise RestartFlowException if user declines
    try:
        confirmed, error = confirm_file_write(path, content, issue_summary)
        
        if not confirmed:
            if error:
                logger.error(f"File write cancelled: {error}")
                return f"File write cancelled: {error}"
            else:
                logger.warning("File write cancelled by user")
                return "File write cancelled by user. No changes were made."
    except RestartFlowException:
        # Re-raise to let main() handle the restart
        raise
    
    # User confirmed, proceed with write
    logger.info(f"User confirmed, proceeding with file write to: {path}")
    result = _write_file(path, content)
    logger.info(f"File write result: {result}")
    if result.lower().startswith("successfully"):
        _record_file_change(path)
    return result


def commit_changes_wrapper(commit_message: str) -> str:
    """
    Wrapper for commit_changes that asks for confirmation before committing.
    
    Args:
        commit_message: The commit message.
        
    Returns:
        Result from commit_changes function or cancellation message.
    """
    logger.info("=" * 80)
    logger.info("COMMIT_CHANGES TOOL CALLED")
    logger.info("=" * 80)
    logger.info(f"Commit message: {commit_message}")
    
    # Ask for confirmation before committing
    # This may raise RestartFlowException if user declines
    try:
        confirmed, error = confirm_git_commit(commit_message)
        
        if not confirmed:
            if error:
                logger.error(f"Git commit cancelled: {error}")
                return f"Git commit cancelled: {error}"
            else:
                logger.warning("Git commit cancelled by user")
                return "Git commit cancelled by user. No changes were committed."
    except RestartFlowException:
        # Re-raise to let main() handle the restart
        raise
    
    # User confirmed, proceed with commit
    logger.info(f"User confirmed, proceeding with git commit")
    result = _commit_changes(commit_message)
    logger.info(f"Git commit result: {result}")
    return result


def create_tools() -> List[Tool]:
    """
    Create and return a list of tools for the agent.
    
    Returns:
        List of Tool objects that the agent can use.
    """
    tools = [
        Tool(
            name="list_directory",
            func=list_directory,
            description="List all files and directories in a given path. Input should be a directory path string."
        ),
        Tool(
            name="read_file",
            func=read_file,
            description="Read the contents of a file. Input should be a file path string."
        ),
        Tool(
            name="write_file",
            func=write_file_wrapper,
            description="Write content to a file. Always include an ISSUE SUMMARY block describing the bug before the CONTENT block so the user knows why the change is needed. Standard format: 'FILEPATH: <file_path>\\nISSUE SUMMARY:\\n<reasoning>\\nCONTENT:\\n<file_content>'. Older '<file_path>|<file_content>' fallback is supported but not preferred. The file_path should be relative to the current working directory. IMPORTANT: This tool will ask for user confirmation before making any changes."
        ),
        Tool(
            name="run_git_command",
            func=run_git_command,
            description="Run a git command. Input should be the git command string (e.g., 'status', 'diff', 'log --oneline')."
        ),
        Tool(
            name="commit_changes",
            func=commit_changes_wrapper,
            description="Stage all changes and commit them with a message. This will show you what will be committed and ask for confirmation. Input should be the commit message string. IMPORTANT: This tool will ask for user confirmation before committing."
        ),
    ]
    return tools


def create_agent(api_key: str) -> AgentExecutor:
    """
    Create and initialize the LangChain agent using the new API.
    
    Args:
        api_key: Google API key for Gemini.
        
    Returns:
        Initialized LangChain AgentExecutor.
    """
    logger.info("Creating LangChain agent with Gemini model")
    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=api_key
    )
    logger.debug("LLM initialized: gemini-2.5-flash")
    
    # Create tools
    tools = create_tools()
    logger.info(f"Created {len(tools)} tools for the agent")
    
    # Try to pull the standard ReAct prompt from LangChain hub, fallback to custom
    try:
        logger.debug("Attempting to pull standard ReAct prompt from LangChain hub")
        prompt = hub.pull("hwchase17/react")
        # Add system prompt to the beginning
        prompt = prompt.partial(system_message=SYSTEM_PROMPT)
        logger.debug("Using standard ReAct prompt from hub")
    except Exception as e:
        logger.exception(f"Exception while pulling prompt from hub: {e}, using custom prompt")
        # Create a custom prompt template for ReAct agent with system message
        prompt = PromptTemplate.from_template("""{system_message}

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}""").partial(system_message=SYSTEM_PROMPT)
    
    # Create the agent using the new API
    logger.debug("Creating ReAct agent")
    agent = create_react_agent(llm, tools, prompt)
    
    # Create callback handler for logging
    callback_handler = LoggingCallbackHandler()
    
    # Create the agent executor
    logger.debug("Creating AgentExecutor with verbose output")
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
        callbacks=[callback_handler]
    )
    
    logger.info("Agent and AgentExecutor created successfully")
    return agent_executor


def run_agent(agent: AgentExecutor, bug_description: str) -> str:
    """
    Run the agent with a bug description.
    
    Args:
        agent: The initialized LangChain AgentExecutor.
        bug_description: Description of the bug to debug.
        
    Returns:
        Agent's response as a string.
    """
    from prompts import USER_PROMPT_TEMPLATE
    
    user_prompt = USER_PROMPT_TEMPLATE.format(bug_description=bug_description)
    logger.info("=" * 80)
    logger.info("AGENT INVOCATION STARTED")
    logger.info("=" * 80)
    logger.info(f"User prompt: {user_prompt}")
    logger.info("=" * 80)
    
    try:
        logger.info("Invoking agent with bug description")
        # Use invoke() instead of run() with proper input format
        response = agent.invoke({
            "input": user_prompt
        })
        
        logger.info("=" * 80)
        logger.info("AGENT RESPONSE RECEIVED")
        logger.info("=" * 80)
        logger.debug(f"Agent response type: {type(response)}")
        
        if isinstance(response, dict):
            logger.info("Response is a dictionary with keys:")
            for key in response.keys():
                logger.info(f"  - {key}")
            
            # Log intermediate steps if available
            if "intermediate_steps" in response:
                logger.info("=" * 80)
                logger.info("INTERMEDIATE STEPS")
                logger.info("=" * 80)
                for i, step in enumerate(response["intermediate_steps"]):
                    logger.info(f"Step {i+1}: {step}")
                logger.info("=" * 80)
            
            # Extract the output
            if "output" in response:
                output = response["output"]
                logger.info("=" * 80)
                logger.info("FINAL AGENT OUTPUT")
                logger.info("=" * 80)
                logger.info(output)
                logger.info("=" * 80)
                logger.info("Agent execution successful")
                return output
            else:
                logger.warning("Response dict does not contain 'output' key")
                logger.info(f"Full response: {response}")
                return str(response)
        elif isinstance(response, str):
            logger.info("=" * 80)
            logger.info("FINAL AGENT OUTPUT (string)")
            logger.info("=" * 80)
            logger.info(response)
            logger.info("=" * 80)
            logger.info("Agent execution successful (string response)")
            return response
        else:
            logger.warning(f"Unexpected response type: {type(response)}")
            logger.info(f"Full response: {response}")
            return str(response)
    except RestartFlowException:
        # Re-raise to let main() handle the restart
        raise
    except Exception as e:
        error_msg = f"Error running agent: {str(e)}"
        logger.error("=" * 80)
        logger.error("AGENT EXECUTION ERROR")
        logger.error("=" * 80)
        logger.exception(error_msg)
        logger.error("=" * 80)
        return error_msg

