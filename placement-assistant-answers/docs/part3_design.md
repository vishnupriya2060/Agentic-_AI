# Part 3 — memory design notes (answer key)

1. thread (the conversation), message (what was said), run (the work one user message triggered), run_step (each model call or tool call inside a run), tool_call (the call, its arguments, result and latency).
2. A run is the unit of work and cost: status, model, token totals, timing. One user message can trigger several model calls and tool calls, and none of that is "said" to anyone. A run can fail halfway; a message can't.
3. A step is a position in the run's timeline; a tool call is the detail for steps of kind 'tool'. One-to-one (UNIQUE run_step_id) keeps a single ordering and keeps tool columns off model steps.
4. Replaying or deleting a conversation must not touch business facts. If they share tables, replay can re-create applications, clearing old chats risks deleting applications, and retention rules (chats can expire, applications are records) and permissions get tangled.
