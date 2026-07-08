from datetime import time

from models import Owner, Pet, Task, Priority
from scheduler import Scheduler


# ---------------------------------------------------------------------------
# Basics (happy paths)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    t = Task("Walk", 30, Priority.HIGH)
    assert t.completed is False
    t.mark_complete()
    assert t.completed is True


def test_add_task_increases_count():
    pet = Pet("Albert", 2, "Ragdoll", "Cat")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feed", 10, Priority.HIGH))
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_is_chronological():
    """Tasks with fixed times come back earliest-first."""
    noon = Task("Lunch", 15, Priority.LOW, fixed_time=time(12, 0))
    morning = Task("Walk", 20, Priority.HIGH, fixed_time=time(8, 0))
    evening = Task("Dinner", 15, Priority.MEDIUM, fixed_time=time(18, 30))
    s = Scheduler(Owner("A", 120), [noon, morning, evening])
    assert [t.title for t in s.sort_by_time()] == ["Walk", "Lunch", "Dinner"]


def test_sort_by_time_puts_flexible_tasks_last():
    """A task with no fixed_time sorts after all timed tasks (and doesn't crash)."""
    flexible = Task("Play", 15, Priority.LOW)               # no fixed_time
    timed = Task("Meds", 5, Priority.HIGH, fixed_time=time(9, 0))
    s = Scheduler(Owner("A", 60), [flexible, timed])
    assert [t.title for t in s.sort_by_time()] == ["Meds", "Play"]


def test_sort_by_priority_high_first():
    low = Task("Groom", 25, Priority.LOW)
    high = Task("Meds", 10, Priority.HIGH)
    med = Task("Play", 15, Priority.MEDIUM)
    s = Scheduler(Owner("A", 60), [low, high, med])
    assert [t.priority for t in s.sort_by_priority()] == [
        Priority.HIGH, Priority.MEDIUM, Priority.LOW,
    ]


# ---------------------------------------------------------------------------
# Filtering (by status and by pet)
# ---------------------------------------------------------------------------

def test_pending_excludes_completed_tasks():
    done = Task("Walk", 20, Priority.HIGH)
    done.mark_complete()
    todo = Task("Feed", 10, Priority.HIGH)
    s = Scheduler(Owner("A", 60), [done, todo])
    assert [t.title for t in s.pending()] == ["Feed"]


def test_for_pet_returns_only_that_pets_tasks():
    cat = Pet("Mochi", 2, "", "cat")
    dog = Pet("Rex", 3, "", "dog")
    cat_task = Task("Litter", 5, Priority.HIGH)
    dog_task = Task("Walk", 30, Priority.HIGH)
    cat.add_task(cat_task)
    dog.add_task(dog_task)
    s = Scheduler(Owner("A", 60), [cat_task, dog_task])
    assert s.for_pet(cat) == [cat_task]
    assert s.for_pet(dog) == [dog_task]


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_conflicts_flags_identical_times():
    """Two tasks at the exact same time overlap."""
    a = Task("Walk", 30, Priority.HIGH, fixed_time=time(8, 0))
    b = Task("Meds", 10, Priority.MEDIUM, fixed_time=time(8, 0))
    s = Scheduler(Owner("A", 120), [a, b])
    assert s.conflicts(a, b) is True
    assert s.find_conflicts() == [(a, b)]


def test_conflicts_flags_partial_overlap():
    a = Task("Walk", 30, Priority.HIGH, fixed_time=time(8, 0))    # 8:00–8:30
    b = Task("Meds", 10, Priority.MEDIUM, fixed_time=time(8, 15))  # 8:15–8:25
    s = Scheduler(Owner("A", 120), [a, b])
    assert s.conflicts(a, b) is True


def test_no_conflict_when_back_to_back():
    a = Task("Walk", 30, Priority.HIGH, fixed_time=time(8, 0))    # 8:00–8:30
    b = Task("Meds", 10, Priority.MEDIUM, fixed_time=time(8, 30))  # 8:30–8:40
    s = Scheduler(Owner("A", 120), [a, b])
    assert s.conflicts(a, b) is False
    assert s.find_conflicts() == []


def test_flexible_tasks_never_conflict():
    a = Task("Play", 15, Priority.LOW)                            # no time
    b = Task("Groom", 20, Priority.LOW, fixed_time=time(8, 0))
    s = Scheduler(Owner("A", 60), [a, b])
    assert s.conflicts(a, b) is False


# ---------------------------------------------------------------------------
# Recurrence
# ---------------------------------------------------------------------------

def test_completing_daily_task_creates_next_occurrence():
    """Marking a daily task complete queues a fresh task for the next day."""
    pet = Pet("Mochi", 2, "", "cat")
    walk = Task("Walk", 20, Priority.HIGH, frequency="daily")
    pet.add_task(walk)

    upcoming = pet.complete_task(walk)

    assert walk.completed is True            # today's instance is done
    assert upcoming is not None              # a new one was created
    assert upcoming.completed is False       # and it's fresh
    assert upcoming.title == "Walk"
    assert upcoming.frequency == "daily"
    assert len(pet.tasks) == 2               # original + next occurrence


def test_once_task_does_not_recur():
    pet = Pet("Mochi", 2, "", "cat")
    vet = Task("Vet visit", 40, Priority.HIGH, frequency="once")
    pet.add_task(vet)

    upcoming = pet.complete_task(vet)

    assert vet.completed is True
    assert upcoming is None
    assert len(pet.tasks) == 1               # nothing new queued


def test_tasks_for_day_respects_frequency():
    daily = Task("Walk", 20, Priority.HIGH, frequency="daily")
    monday = Task("Groom", 30, Priority.LOW, frequency="weekly", weekday=0)
    wednesday = Task("Vet", 45, Priority.HIGH, frequency="weekly", weekday=2)
    s = Scheduler(Owner("A", 120), [daily, monday, wednesday])

    assert [t.title for t in s.tasks_for_day(0)] == ["Walk", "Groom"]   # Monday
    assert [t.title for t in s.tasks_for_day(2)] == ["Walk", "Vet"]     # Wednesday
    assert [t.title for t in s.tasks_for_day(4)] == ["Walk"]            # Friday


# ---------------------------------------------------------------------------
# Plan building (integration) + edge cases
# ---------------------------------------------------------------------------

def test_build_plan_empty_task_list():
    """A pet with no tasks produces an empty plan, not an error."""
    plan = Scheduler(Owner("A", 60), []).build_plan()
    assert plan.scheduled == []
    assert plan.dropped == []
    assert plan.total_minutes == 0


def test_build_plan_drops_overflow_task():
    walk = Task("Walk", 40, Priority.HIGH)
    groom = Task("Groom", 30, Priority.LOW)        # 40 + 30 > 60 budget
    plan = Scheduler(Owner("A", 60), [walk, groom]).build_plan()
    assert [st.task.title for st in plan.scheduled] == ["Walk"]
    assert [(t.title, r) for t, r in plan.dropped] == [("Groom", "not enough time left")]


def test_build_plan_drops_conflicting_task():
    """When two timed tasks overlap, the higher-priority one wins."""
    walk = Task("Walk", 30, Priority.HIGH, fixed_time=time(8, 0))
    meds = Task("Meds", 10, Priority.MEDIUM, fixed_time=time(8, 15))
    plan = Scheduler(Owner("A", 120), [walk, meds]).build_plan()
    assert [st.task.title for st in plan.scheduled] == ["Walk"]
    assert plan.dropped[0][0].title == "Meds"
    assert "overlaps" in plan.dropped[0][1]
