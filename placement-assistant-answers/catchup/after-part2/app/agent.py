import time
from collections.abc import Callable

from app.memory import ConversationStore
from app.providers import AgentError
from app.tools.placement_tools import PlacementTools

MAX_STEPS = 8

SYSTEM = """You are the Placement Assistant for an engineering college's placement cell.
You are talking to the student with roll number {student_id}. Act only for this student.
Use the tools for every fact about drives, eligibility, applications and slots; never guess.
Eligibility is decided by check_eligibility, not by you. Keep replies short and concrete."""


class Agent:
    """A small agent: one student, one conversation, the placement tools."""

    def __init__(self, provider, tools: PlacementTools, student_id: str,
                 memory: ConversationStore | None = None, thread_id: str | None = None,
                 on_step: Callable[[dict], None] | None = None):
        self.provider = provider
        self.tools = tools
        self.system = SYSTEM.format(student_id=student_id)
        self.memory = memory
        self.thread_id = thread_id
        self.on_step = on_step
        self.contents: list[dict] = []     # what the model sees, turn after turn
        self.trace: list[dict] = []        # what happened, step by step
        # TODO (Part 3.3): if memory and thread_id are given, start self.contents from
        # memory.load_history(thread_id), as {"role": ..., "text": ...} entries.

    # ------------------------------------------------------------------ Part 2.1

    def run_tool(self, name: str, args: dict) -> dict:
        """Call one tool. Never raises: every failure becomes a result the model can read."""
        try:
            return self.tools.call(name, args)
        except NotImplementedError:
            return {"error": "not_implemented", "hint": f"{name} is not available yet. Tell the user."}
        except Exception as e:                                   # self-healing: a crash becomes information
            return {"error": "tool_failed", "hint": f"{name} failed ({type(e).__name__}). Try another way or tell the user."}

    def _log(self, entry: dict) -> None:
        self.trace.append(entry)
        if self.on_step:
            self.on_step(entry)

    # ------------------------------------------------------------------ Part 2.2

    def ask(self, text: str) -> str:
        """One user turn: loop model calls and tool calls until the model answers."""
        self.contents.append({"role": "user", "text": text})
        run_id = None
        # TODO (Part 3.3): save the user message and start a run.
        # TODO (Part 3.3): on AgentError, finish the run as failed with e.code, then re-raise.
        reply = self._loop(run_id)
        # TODO (Part 3.3): save the reply and finish the run as succeeded.
        return reply

    def _loop(self, run_id: str | None) -> str:
        functions = list(self.tools.functions().values())
        seq = 0
        while seq < MAX_STEPS:
            turn = self.provider.generate(self.system, self.contents, functions)
            seq += 1
            self._log({"step": seq, "kind": "model", "tokens_in": turn.tokens_in, "tokens_out": turn.tokens_out})
            # TODO (Part 3.3): record this model step.

            if not turn.tool_calls:
                reply = turn.text or ""
                self.contents.append({"role": "model", "text": reply, "raw": turn.raw})
                return reply

            self.contents.append({"role": "model", "text": turn.text, "raw": turn.raw,
                                  "tool_calls": [{"name": c.name, "args": c.args} for c in turn.tool_calls]})
            for call in turn.tool_calls:
                seq += 1
                started = time.perf_counter()
                result = self.run_tool(call.name, call.args)
                ms = round((time.perf_counter() - started) * 1000)
                ok = "error" not in result
                self._log({"step": seq, "kind": "tool", "tool": call.name, "args": call.args,
                           "result": result, "ok": ok, "ms": ms})
                # TODO (Part 3.3): record this tool call.
                self.contents.append({"role": "tool", "name": call.name, "result": result})

        raise AgentError("step_limit", f"Stopped after {MAX_STEPS} steps without an answer.")
