import streamlit as st
from models import Owner, Pet, Task, Priority
from scheduler import Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
available_minutes = st.number_input("Available minutes", min_value=1, max_value=1440, value=60)

# st.session_state is like a dictionary
if "owner" not in st.session_state:
    # creating an object
    st.session_state.owner = Owner(owner_name, available_minutes)
    # creating an object
if "pet" not in st.session_state:
    st.session_state.pet = Pet(pet_name, 0, "", species)
    

# then use st.session_state.owner wherever you need it

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")


col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

# if st.button("Add task"):
#     st.session_state.tasks.append(
#         # object isn't getting officially created here.
#         {"title": task_title, "duration_minutes": int(duration), "priority": priority}
#     )

# now a real object has been created.
if st.button("Add task"):
    PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}
    task = Task(task_title, int(duration), PRIORITY_MAP[priority])   # build a Task
    st.session_state.pet.add_task(task)                             # ← call the method

#building a dictionary from an object dict in st to display it
if st.session_state.pet.tasks:
    st.write("Current tasks:")
    st.table([
        {"title": t.title, "duration": t.duration, "priority": t.priority.name}
        for t in st.session_state.pet.tasks
         ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    owner = st.session_state.owner
    plan = Scheduler(owner, st.session_state.pet.tasks).build_plan()   # ← use the pet's tasks
    st.subheader("Your plan")
    st.text(plan.explain())

    # # translate the stored string priorities into Priority enums
    # PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}

    # # build the owner from the inputs
    # owner = st.session_state.owner

    # # convert each stored task-dict into a real Task object
    # tasks = []
    # for t in st.session_state.pet.tasks:
    #     tasks.append(
    #         Task(t["title"], t["duration_minutes"], PRIORITY_MAP[t["priority"]])
    #     )

    # run your scheduler and show the explanation
    # plan = Scheduler(owner, tasks).build_plan()
    # st.subheader("Your plan")
    # st.text(plan.explain())

