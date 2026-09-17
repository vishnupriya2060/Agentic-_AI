# Day 2 instructor notes

Nothing to install beyond Python and `pip install -r requirements.txt`. No Docker, no database server.

## Plan

| Part | Min | You | Students |
|---|---|---|---|
| 1 Tools | 0–20 | Live-code `check_eligibility` from an empty method: description, `_evaluate`, error returns. Walk through `apply_to_drive`. | Follow along, run the sample tests |
| | 20–70 | Circulate | TODO 1 `get_student`, TODO 2 `list_open_drives`, TODO 3 `book_interview_slot` |
| 2 Agent | 0–30 | Five minutes on the loop shape (it's Day 1's loop plus a trace) | `run_tool`, `ask` |
| | 30–40 | One student's terminal on the projector | `python -m scripts.chat`, questions that fire their tools |
| 3 Memory | 0–10 | Put the Day 1 in-memory store on screen, ask the room to normalise it | On paper, then `docs/part3_design.md` |
| | 10–60 | Circulate | `schema/agent.sql`, `app/memory.py`, wire memory into `Agent` |
| Lab | 90 | Circulate | L1 notify_student A/B, L2 append-only trigger, L3 pagination |

Chat demo questions, as 22CS045: "What's on my record?", "Which drives are open for CSE?",
"Am I eligible for Zoho?", "Apply me to Zoho", "Book the first slot". As 22IT017
(`--student 22IT017`): "Can I apply to Zoho?" should explain two failed rules.

## Common mistakes

| Where | Mistake |
|---|---|
| TODO 1 | Returning the Student object instead of a dict; returning the integer id as `student_id` |
| TODO 2 | Filtering on every rule (cgpa, backlogs); only branch and grad_year filter the list |
| TODO 3 | Checking `slot.student_id is None` instead of trusting `claim_slot`; no `available_slots` on `slot_taken` |
| Part 2 | Leaving `raw` out of model entries (it can break multi-step calls on newer Gemini models); numbering steps per kind instead of across the run |
| Part 3.2 | Two separate commits in `record_tool_call`; building SQL with f-strings |
| Part 3.3 | Swallowing the AgentError after marking the run failed instead of re-raising; saving everything only at the end |

## Catch-up

At the end of each part, anyone not green copies the matching folder from `catchup/` over their kit
(see `catchup/README.md`). None contains a lab answer.

## Grading

```bash
pytest tests/test_part1_tools.py -q
pytest tests/test_part2_agent.py -q
pytest tests/test_part3_schema.py tests/test_part3_memory.py -q
pytest tests/test_lab1_notify.py tests/test_lab2_append_only.py tests/test_lab3_pagination.py -q
pytest tests/test_stretch_my_applications.py -q          # skipped = not attempted
```
