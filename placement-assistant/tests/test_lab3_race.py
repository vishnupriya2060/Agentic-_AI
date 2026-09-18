"""Lab 3 — two runs booking the same slot; one wins cleanly."""
import threading

from app.memory import RunStore
from app.placement_db import PlacementDb
from app.providers import ModelTurn, PositionalMock, ToolCall
from app.worker import Worker


def race_mock(student_id: str) -> PositionalMock:
    return PositionalMock([
        ModelTurn(text=None, tool_calls=[ToolCall("check_eligibility", {"student_id": student_id, "drive_id": 2})]),
        ModelTurn(text=None, tool_calls=[ToolCall("apply_to_drive", {"student_id": student_id, "drive_id": 2})]),
        ModelTurn(text=None, tool_calls=[ToolCall("book_interview_slot", {"student_id": student_id, "slot_id": 3})]),
        ModelTurn(text="Done."),
    ])


def test_two_workers_two_runs_one_slot(db_files, clock):
    agent, place = db_files
    stores = [RunStore(agent, clock), RunStore(agent, clock)]
    placements = [PlacementDb(place), PlacementDb(place)]
    students = ["22IT017", "22CS045"]
    run_ids = [stores[i].enqueue(stores[i].create_thread(students[i]), "Apply to TCS and book slot 3", "mock")
               for i in range(2)]
    barrier = threading.Barrier(2)
    outcomes = [None, None]

    def work(i):
        barrier.wait()
        outcomes[i] = Worker(stores[i], placements[i], race_mock(students[i]), worker_id=f"w{i}").run_once()

    threads = [threading.Thread(target=work, args=(i,)) for i in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sorted(outcome[1] for outcome in outcomes) == ["succeeded", "succeeded"]
    runs = [stores[0].get_run(run_id) for run_id in run_ids]
    booking_results = [step["result"] for run in runs for step in run["steps"]
                       if step["kind"] == "tool" and step["tool_name"] == "book_interview_slot"]
    assert len(booking_results) == 2
    assert sum(result.get("status") == "booked" for result in booking_results) == 1
    assert sum(result.get("error") == "slot_taken" for result in booking_results) == 1
    slot = placements[0].conn.execute("SELECT student_id FROM interview_slot WHERE id = 3").fetchone()
    assert slot["student_id"] is not None


def test_truly_concurrent_claims_have_one_winner(db_files):
    _, place = db_files
    setup = PlacementDb(place)
    setup.create_application(2, 2)
    setup.create_application(1, 2)
    version = setup.slot_version(3)
    barrier = threading.Barrier(8)
    results = [None] * 8

    def claim(i):
        db = PlacementDb(place)
        barrier.wait()
        results[i] = db.claim_slot(3, 2 if i % 2 == 0 else 1, version)
        db.conn.close()

    threads = [threading.Thread(target=claim, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count(True) == 1
    assert results.count(False) == 7
    assert setup.slot_version(3) == version + 1
