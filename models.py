from enum import Enum

class Pet:
    def __init__(self, name, age, breed, species):
        self.name = name
        self.age = age
        self.breed = breed
        self.species = species

# priority is not recommended here, becuase it becomes confusing
# changed name from availability to availabile_minutes.
class Owner:
    #  preferences = None
    def __init__(self, name, available_minutes):
        self.name = name
        self.available_minutes = available_minutes
        # self.preferences = {}


class Task:
    # category, fixed_time = None
    def __init__(self, title, duration, priority):
        self.title = title
        self.duration = duration
        self.priority = priority

        # not sure about this, category is basically a type of task
        # self.category = category
        # self.fixed_time = fixed_time
        

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    
#ScheduledTask -> Task
class ScheduledTask:
    # start_time
    def __init__(self, task, reason):
        self.task = task
        # self.start_time = start_time
        self.reason = reason


class Plan:
    def __init__(self, scheduled, dropped, total_minutes):
        self.scheduled = scheduled
        self.dropped = dropped
        self.total_minutes  = total_minutes

def explain(self):
    lines = []
    for st in self.scheduled:
        lines.append(
            f"I scheduled {st.task.title} because {st.reason}, "
            f"it takes {st.task.duration} minutes"
        )
    for task in self.dropped:
        lines.append(f"I dropped {task.title} — not enough time left")
    lines.append(f"Total time used: {self.total_minutes} minutes")
    return "\n".join(lines)


