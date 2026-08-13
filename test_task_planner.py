import pytest
from core.task_planner import TaskPlanner
from core.task_executor import TaskExecutor

def test_split_compound_prompt():
    planner = TaskPlanner()
    
    prompt = "Open Chrome, search YouTube for Python tutorials, and then create a folder called Major Project"
    plan = planner.create_plan(prompt)
    
    assert len(plan) == 3
    assert plan[0]["intent"] == "OPEN_APP"
    assert plan[1]["intent"] == "YOUTUBE_SEARCH"
    assert plan[2]["intent"] == "CREATE_FOLDER"

def test_execute_plan_single_step():
    executor = TaskExecutor()
    step = {
        "step_number": 1,
        "sub_prompt": "take a screenshot",
        "intent": "SCREENSHOT",
        "entities": {}
    }
    success, msg = executor.execute_step(step)
    assert success is True
    assert "saved" in msg.lower()
