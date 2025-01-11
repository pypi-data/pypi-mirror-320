import pytest
import numpy as np
from datetime import datetime
from helix_agent.tools import AgentTools

def test_parse_scientific_notation():
    text = "The values were 1.23e-4 and 5.67e+8 in the experiment"
    result = AgentTools.parse_scientific_notation(text)
    assert len(result) == 2
    assert result[0] == 1.23e-4
    assert result[1] == 5.67e+8

def test_format_citation():
    authors = ["Smith, J.", "Doe, R."]
    title = "Advances in AI Research"
    journal = "Journal of AI Studies"
    year = 2023
    doi = "10.1234/ai.2023"
    
    citation = AgentTools.format_citation(authors, title, journal, year, doi)
    expected = "Smith, J., Doe, R. (2023). Advances in AI Research. Journal of AI Studies. DOI: 10.1234/ai.2023"
    assert citation == expected

def test_analyze_experiment_data():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    results = AgentTools.analyze_experiment_data(data)
    
    assert 'mean' in results
    assert 'std_dev' in results
    assert 'sample_size' in results
    assert 'confidence_interval' in results
    assert results['sample_size'] == 5
    assert results['mean'] == 3.0
    assert isinstance(results['confidence_interval'], tuple)

def test_create_experiment_protocol():
    steps = ["Step 1", "Step 2"]
    materials = ["Material A", "Material B"]
    duration = "2 hours"
    conditions = {"temperature": 25, "pressure": 1}
    
    protocol = AgentTools.create_experiment_protocol(steps, materials, duration, conditions)
    
    assert 'protocol_id' in protocol
    assert protocol['steps'] == steps
    assert protocol['materials'] == materials
    assert protocol['estimated_duration'] == duration
    assert protocol['conditions'] == conditions
    assert 'created_at' in protocol

def test_extract_paper_metadata():
    text = """Title: AI in Science
    
Abstract: This is a sample abstract about AI in science.

Keywords: artificial intelligence, science, research
    """
    metadata = AgentTools.extract_paper_metadata(text)
    
    assert metadata['title'] == "Title: AI in Science"
    assert "sample abstract" in metadata['abstract']
    assert len(metadata['keywords']) == 3
    assert 'artificial intelligence' in metadata['keywords']

def test_create_task_plan():
    objective = "Complete research project"
    subtasks = ["Literature review", "Data collection", "Analysis"]
    dependencies = {
        "task-2": ["task-1"],  # Data collection depends on literature review
        "task-3": ["task-2"]   # Analysis depends on data collection
    }
    
    plan = AgentTools.create_task_plan(objective, subtasks, dependencies)
    
    assert plan['objective'] == objective
    assert len(plan['subtasks']) == 3
    assert plan['dependencies'] == dependencies
    assert plan['status'] == 'not_started'

def test_track_task_progress():
    task_plan = AgentTools.create_task_plan(
        "Research project",
        ["Task 1", "Task 2", "Task 3"]
    )
    completed_tasks = ["task-1", "task-2"]
    
    updated_plan = AgentTools.track_task_progress(task_plan, completed_tasks)
    
    assert updated_plan['progress'] == pytest.approx(66.67, rel=0.01)
    assert updated_plan['status'] == 'in_progress'
    assert updated_plan['subtasks'][0]['status'] == 'completed'
    assert updated_plan['subtasks'][1]['status'] == 'completed'
    assert updated_plan['subtasks'][2]['status'] == 'pending'

def test_simulate_experiment():
    protocol = {
        'protocol_id': 'test-protocol',
        'steps': ['Step 1'],
        'conditions': {'temp': 25}
    }
    variables = {'concentration': 0.5}
    iterations = 3
    
    results = AgentTools.simulate_experiment(protocol, variables, iterations)
    
    assert results['protocol_id'] == protocol['protocol_id']
    assert results['iterations'] == iterations
    assert len(results['results']) == iterations
    assert 'summary_stats' in results
