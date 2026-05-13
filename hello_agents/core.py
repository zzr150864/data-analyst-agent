import json
import inspect
import os
from typing import Any, Dict, List, Optional
import httpx


class _ToolCall:
    """Thin wrapper to mimic OpenAI SDK tool_call object."""
    def __init__(self, data: dict):
        self.id = data.get("id", "")
        self.type = data.get("type", "function")
        self.function = _FunctionCall(data.get("function", {}))


class _FunctionCall:
    def __init__(self, data: dict):
        self.name = data.get("name", "")
        self.arguments = data.get("arguments", "{}")


class _Message:
    """Thin wrapper to mimic OpenAI SDK message object."""
    def __init__(self, data: dict):
        self.content = data.get("content")
        self.role = data.get("role", "assistant")
        tc_list = data.get("tool_calls") or []
        self.tool_calls = [_ToolCall(tc) for tc in tc_list] if tc_list else None


class _Choice:
    """Thin wrapper to mimic OpenAI SDK choice object."""
    def __init__(self, data: dict):
        self.index = data.get("index", 0)
        self.message = _Message(data.get("message", {}))
        self.finish_reason = data.get("finish_reason", "")


class _Response:
    """Thin wrapper to mimic OpenAI SDK response object."""
    def __init__(self, data: dict):
        self.choices = [_Choice(c) for c in data.get("choices", [])]
        self.usage = data.get("usage", {})


class HelloAgentsLLM:
    """Unified LLM interface compatible with OpenAI API standard. Uses httpx."""

    def __init__(
        self,
        model: Optional[str] = None,
        apiKey: Optional[str] = None,
        baseUrl: Optional[str] = None,
        timeout: int = 120,
    ):
        self.model = model or os.getenv("LLM_MODEL_ID", "deepseek-chat")
        api_key = apiKey or os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
        self.base_url = (baseUrl or os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")).rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self._timeout = timeout
        # Bypass system proxy to avoid SSL errors in restricted environments
        self._client = httpx.Client(
            proxy=None,
            trust_env=False,
            timeout=timeout,
        )

    def chat(
        self,
        messages: List[Dict],
        tools: Optional[list] = None,
        temperature: float = 0.1,
    ) -> _Response:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools

        try:
            resp = self._client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._headers,
            )
            resp.raise_for_status()
            return _Response(resp.json())
        except httpx.HTTPStatusError as e:
            error_msg = f"LLM API error ({e.response.status_code}): {e.response.text[:500]}"
            raise RuntimeError(error_msg) from e
        except httpx.RequestError as e:
            raise RuntimeError(f"LLM connection error: {e}") from e


class BaseTool:
    """Base class for all tools. Subclass and define name, description, and run()."""
    name: str = ""
    description: str = ""

    def run(self, **kwargs) -> str:
        raise NotImplementedError

    def to_openai_schema(self) -> dict:
        sig = inspect.signature(self.run)
        params = {}
        for pname, param in sig.parameters.items():
            if pname in ("self", "kwargs", "args"):
                continue
            annot = param.annotation
            ptype = "string"
            if annot is not inspect.Parameter.empty:
                if annot is int:
                    ptype = "integer"
                elif annot is float:
                    ptype = "number"
                elif annot is bool:
                    ptype = "boolean"
            params[pname] = {"type": ptype, "description": f"Parameter: {pname}"}

        required = [
            pname for pname, param in sig.parameters.items()
            if pname not in ("self", "kwargs", "args") and param.default is inspect.Parameter.empty
        ]

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": params,
                    "required": required,
                },
            },
        }


class ToolRegistry:
    """Central registry for tool management."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def register_tools(self, tools: List[BaseTool]):
        for t in tools:
            self.register_tool(t)

    def to_openai_schema(self) -> List[Dict]:
        return [t.to_openai_schema() for t in self._tools.values()]

    def get_tools_description(self) -> str:
        lines = []
        for t in self._tools.values():
            lines.append(f"- {t.name}: {t.description}")
        return "\n".join(lines)

    def execute_tool(self, name: str, params: dict) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"Error: tool '{name}' not found. Available: {list(self._tools.keys())}"
        try:
            return tool.run(**params)
        except Exception as e:
            return f"Error executing {name}: {e}"


class SimpleAgent:
    """Basic agent with LLM + tools. Handles the function-calling loop."""

    def __init__(
        self,
        name: str = "Agent",
        llm: Optional[HelloAgentsLLM] = None,
        system_prompt: str = "You are a helpful assistant.",
        tool_registry: Optional[ToolRegistry] = None,
        max_steps: int = 15,
    ):
        self.name = name
        self.llm = llm or HelloAgentsLLM()
        self.system_prompt = system_prompt
        self.tool_registry = tool_registry or ToolRegistry()
        self.max_steps = max_steps

    def run(self, task: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task},
        ]
        tools = self.tool_registry.to_openai_schema() if self.tool_registry._tools else None

        for _ in range(self.max_steps):
            response = self.llm.chat(messages, tools=tools)
            choice = response.choices[0]
            msg = choice.message

            if msg.content and not msg.tool_calls:
                return msg.content

            if msg.tool_calls:
                tc_dicts = []
                for tc in msg.tool_calls:
                    tc_dicts.append({
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    })
                messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": tc_dicts,
                })
                for tc in msg.tool_calls:
                    tool_name = tc.function.name
                    try:
                        tool_args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}
                    result = self.tool_registry.execute_tool(tool_name, tool_args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })
            else:
                return msg.content or ""

        return "Agent reached maximum steps without final response."


class ReActAgent:
    """Agent using the ReAct (Reasoning + Acting) paradigm."""

    REACT_SYSTEM_TEMPLATE = """You are {name}. You solve problems using the ReAct approach:
Thought: Analyze what you need to do next.
Action: Call a tool using its name and parameters.
Observation: Receive the tool's result.
Repeat until you can give a Final Answer.

Available tools:
{tools_desc}

Always end with: Final Answer: <your comprehensive answer>"""

    def __init__(
        self,
        name: str = "ReActAgent",
        llm_client: Optional[HelloAgentsLLM] = None,
        tool_registry: Optional[ToolRegistry] = None,
        tool_executor: Optional[ToolRegistry] = None,
        max_steps: int = 8,
        system_prompt: str = "",
    ):
        self.name = name
        self.llm = llm_client or HelloAgentsLLM()
        self.tool_registry = tool_registry or tool_executor or ToolRegistry()
        self.max_steps = max_steps
        self.custom_prompt = system_prompt

    def run(self, task: str) -> str:
        tools_desc = self.tool_registry.get_tools_description()
        if self.custom_prompt:
            system_msg = self.custom_prompt
        else:
            system_msg = self.REACT_SYSTEM_TEMPLATE.format(
                name=self.name, tools_desc=tools_desc
            )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": task},
        ]

        for _ in range(self.max_steps):
            response = self.llm.chat(messages)
            content = response.choices[0].message.content or ""

            if "Final Answer:" in content:
                idx = content.index("Final Answer:")
                return content[idx + len("Final Answer:"):].strip()

            action_match = None
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("Action:"):
                    action_match = stripped[len("Action:"):].strip()
                    break

            if action_match:
                tool_result = self._execute_action(action_match)
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content": f"Observation: {tool_result}"})
            else:
                messages.append({"role": "assistant", "content": content})
                messages.append({
                    "role": "user",
                    "content": "Continue with Thought/Action or provide Final Answer.",
                })

        messages.append({
            "role": "user",
            "content": "Please provide your Final Answer now based on all observations above.",
        })
        final = self.llm.chat(messages)
        content = final.choices[0].message.content or ""
        if "Final Answer:" in content:
            idx = content.index("Final Answer:")
            return content[idx + len("Final Answer:"):].strip()
        return content

    def _execute_action(self, action_str: str) -> str:
        tool_name = action_str.split("(")[0].strip()
        args_str = ""
        if "(" in action_str and action_str.rstrip().endswith(")"):
            start = action_str.index("(")
            args_str = action_str[start + 1:action_str.rindex(")")].strip()
        params = {}
        if args_str:
            try:
                params = json.loads(args_str)
            except json.JSONDecodeError:
                for part in args_str.split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        params[k.strip()] = v.strip().strip("\"'")
        return self.tool_registry.execute_tool(tool_name, params)


class PlanAndSolveAgent:
    """Agent that first creates a plan, then executes each step."""

    PLAN_PROMPT = """You are a planning agent. Given a task, create a step-by-step plan.
Output each step on a new line starting with "Step N: " where N is the step number.
Be specific about what each step should accomplish.
After listing all steps, end with "---END PLAN---".

Task: {task}"""

    SOLVE_PROMPT = """You are {name}, executing a plan.

Original task: {task}

Current plan step: {step}

Previous results:
{context}

Complete this step thoroughly. Provide a detailed result."""

    def __init__(
        self,
        name: str = "Planner",
        llm_client: Optional[HelloAgentsLLM] = None,
        llm: Optional[HelloAgentsLLM] = None,
        tool_registry: Optional[ToolRegistry] = None,
        max_steps: int = 10,
    ):
        self.name = name
        self.llm_client = llm_client or llm or HelloAgentsLLM()
        self.tool_registry = tool_registry
        self.max_steps = max_steps

    def run(self, task: str) -> str:
        plan_msg = self.PLAN_PROMPT.format(task=task)
        response = self.llm_client.chat([{"role": "user", "content": plan_msg}])
        plan_text = response.choices[0].message.content or ""

        steps = []
        for line in plan_text.split("\n"):
            line = line.strip()
            if line.startswith("Step ") and ":" in line:
                step_content = line.split(":", 1)[1].strip()
                if step_content:
                    steps.append(step_content)
            if "---END PLAN---" in line:
                break

        if not steps:
            steps = [task]

        results = []
        for i, step in enumerate(steps):
            context = "\n".join(f"Step {j+1}: {r}" for j, r in enumerate(results))
            solve_msg = self.SOLVE_PROMPT.format(
                name=self.name, task=task, step=step, context=context or "(none)"
            )

            if self.tool_registry and self.tool_registry._tools:
                tools = self.tool_registry.to_openai_schema()
                resp = self.llm_client.chat([{"role": "user", "content": solve_msg}], tools=tools)
                msg = resp.choices[0].message

                if msg.tool_calls:
                    tool_msgs = [{"role": "user", "content": solve_msg}]
                    tc_dicts = []
                    for tc in msg.tool_calls:
                        tc_dicts.append({
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                        })
                    tool_msgs.append({
                        "role": "assistant",
                        "content": msg.content or "",
                        "tool_calls": tc_dicts,
                    })
                    for tc in msg.tool_calls:
                        try:
                            args = json.loads(tc.function.arguments)
                        except json.JSONDecodeError:
                            args = {}
                        result = self.tool_registry.execute_tool(tc.function.name, args)
                        tool_msgs.append({"role": "tool", "tool_call_id": tc.id, "content": result})
                    final_resp = self.llm_client.chat(tool_msgs)
                    results.append(final_resp.choices[0].message.content or "")
                else:
                    results.append(msg.content or "")
            else:
                resp = self.llm_client.chat([{"role": "user", "content": solve_msg}])
                results.append(resp.choices[0].message.content or "")

        synthesis_prompt = f"""Synthesize the following step results into a comprehensive final answer.

Original task: {task}

Step results:
{chr(10).join(f'Step {i+1}: {r}' for i, r in enumerate(results))}

Provide a complete, well-structured final answer:"""

        final_resp = self.llm_client.chat([{"role": "user", "content": synthesis_prompt}])
        return final_resp.choices[0].message.content or "\n".join(results)
