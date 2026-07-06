from models import Pet, Task, Priority

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
