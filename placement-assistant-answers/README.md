# Placement Assistant: Day 2 answer kit (instructor only)

Do not share this folder with students. It is the complete reference for the student kit.

| Path | What it is |
|---|---|
| `INSTRUCTOR.md` | Timings, what to live-code, common mistakes, catch-up procedure |
| `catchup/` | Checkpoints to hand a stuck student at the end of Part 1, 2 or 3. No lab answers inside. |
| `app/tools/placement_tools.py` | Part 1, lab 1 (`notify_student`) and stretch (`list_my_applications`) |
| `app/agent.py` | Part 2 and Part 3.3 |
| `schema/agent.sql`, `app/memory.py` | Part 3.1 and 3.2; `page_messages` is lab 3 |
| `schema/append_only.sql` | Lab 2 |
| `app/verdict.py` | Stretch |
| `docs/part3_design.md` | Written answer key |

```bash
pip install -r requirements.txt
pytest            # 89 passed
```

`docs/lab1_ab.md` is left blank: A/B results depend on the model and must be produced live.
