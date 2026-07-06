from models import Owner, Pet, Task, Priority
from scheduler import Scheduler


def main():

    owner = Owner("Addis", 60)                       # ← the owner (time budget)
    albert = Pet("Albert", 2, "Ragdoll", "Cat")
    albert.add_task(Task("Morning walk", 30, Priority.HIGH))
    albert.add_task(Task("Meds", 10, Priority.HIGH))
    scheduler = Scheduler(owner, albert.tasks)       # owner first, pet's tasks second
    plan = scheduler.build_plan()
    print(plan.explain())




if __name__ == "__main__":
    main()


