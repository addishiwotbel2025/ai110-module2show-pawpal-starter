import streamlit as st
from datetime import time
from models import Owner, Pet, Task, Priority
from scheduler import Scheduler

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    "Plan your pet's day of care. Add tasks with times, priorities, and recurrence, "
    "and PawPal+ builds a **conflict-aware schedule** that fits the time you have."
)

with st.expander("How it works", expanded=False):
    st.markdown(
        """
- **Add tasks** with a duration, priority, optional fixed start time, and recurrence.
- PawPal+ **sorts** them, **flags time conflicts**, and skips finished tasks.
- **Generate a schedule** to see what fits your available minutes — highest priority
  first — and why anything was dropped.
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
available_minutes = st.number_input("Available minutes", min_value=1, max_value=1440, value=60)

# st.session_state persists objects across Streamlit reruns (like a dictionary)
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, available_minutes)
if "pet" not in st.session_state:
    st.session_state.pet = Pet(pet_name, 0, "", species)

# keep the stored objects in sync with the current inputs
st.session_state.owner.name = owner_name
st.session_state.owner.available_minutes = available_minutes
st.session_state.pet.name = pet_name
st.session_state.pet.species = species

st.markdown("### Tasks")
st.caption("Add tasks with an optional fixed start time and recurrence. These feed the scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    has_time = st.checkbox("Fixed start time?")
    fixed_time = st.time_input("Start time", value=time(8, 0)) if has_time else None
with col5:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
with col6:
    weekday = None
    if frequency == "weekly":
        weekday = WEEKDAYS.index(st.selectbox("Recurs on", WEEKDAYS))

if st.button("Add task"):
    task = Task(
        task_title, int(duration), PRIORITY_MAP[priority],
        fixed_time=fixed_time, frequency=frequency, weekday=weekday,
    )
    st.session_state.pet.add_task(task)

# show the current tasks, sorted by start time (Scheduler.sort_by_time)
if st.session_state.pet.tasks:
    scheduler = Scheduler(st.session_state.owner, st.session_state.pet.tasks)

    st.write("**Current tasks** (sorted by start time):")
    st.table([
        {
            "time": t.fixed_time.strftime("%H:%M") if t.fixed_time else "flexible",
            "title": t.title,
            "duration": f"{t.duration} min",
            "priority": t.priority.name,
            "frequency": t.frequency,
            "done": "✅" if t.completed else "",
        }
        for t in scheduler.sort_by_time()
    ])

    # conflict detection: show the exact overlap and a concrete next step
    clashes = scheduler.find_conflicts()
    if clashes:
        st.warning(
            f"⚠️ {len(clashes)} time conflict(s) found. These tasks overlap, so only the "
            "higher-priority one will be scheduled — move one to a different time to keep both."
        )
        for a, b in clashes:
            st.markdown(
                f"- **{a.title}** ({a.fixed_time.strftime('%H:%M')}, {a.duration} min) "
                f"overlaps **{b.title}** ({b.fixed_time.strftime('%H:%M')}, {b.duration} min)"
            )
    else:
        st.success("✅ No time conflicts — every scheduled time is clear.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# completing a task — recurring tasks queue up their next occurrence
st.subheader("Complete a task")
st.caption("Marking a daily/weekly task complete automatically queues its next occurrence.")
open_tasks = [t for t in st.session_state.pet.tasks if not t.completed]
if open_tasks:
    labels = [f"{i}: {t.title}" for i, t in enumerate(st.session_state.pet.tasks) if not t.completed]
    chosen = st.selectbox("Task to complete", labels)
    if st.button("Mark complete"):
        idx = int(chosen.split(":", 1)[0])
        task = st.session_state.pet.tasks[idx]
        upcoming = st.session_state.pet.complete_task(task)
        if upcoming is not None:
            st.success(f"Completed '{task.title}' — queued its next {task.frequency} occurrence.")
        else:
            st.success(f"Completed '{task.title}'.")
        st.rerun()
else:
    st.info("Nothing to complete yet.")

st.divider()

st.subheader("Build Schedule")
st.caption("Schedules pending tasks, highest priority first, dropping time conflicts and overflow.")

if st.button("Generate schedule"):
    owner = st.session_state.owner
    # only schedule tasks that aren't done yet (filtering by status)
    pending = Scheduler(owner, st.session_state.pet.tasks).pending()
    plan = Scheduler(owner, pending).build_plan()

    st.subheader("📋 Your plan")

    # at-a-glance summary
    m1, m2, m3 = st.columns(3)
    m1.metric("Scheduled", len(plan.scheduled))
    m2.metric("Time used", f"{plan.total_minutes} min")
    m3.metric("Time left", f"{owner.available_minutes - plan.total_minutes} min")

    if plan.scheduled:
        st.success(f"Planned {len(plan.scheduled)} task(s) within your {owner.available_minutes} minutes.")
        # show the scheduled tasks in time order
        scheduled_tasks = [sched.task for sched in plan.scheduled]
        ordered = Scheduler(owner, scheduled_tasks).sort_by_time()
        st.table([
            {
                "time": t.fixed_time.strftime("%H:%M") if t.fixed_time else "flexible",
                "task": t.title,
                "duration": f"{t.duration} min",
                "priority": t.priority.name,
            }
            for t in ordered
        ])
    else:
        st.info("No tasks could be scheduled with the available time.")

    # explain anything that didn't make the cut
    if plan.dropped:
        st.warning(f"⚠️ {len(plan.dropped)} task(s) couldn't be scheduled:")
        for task, reason in plan.dropped:
            st.markdown(f"- **{task.title}** — {reason}")

