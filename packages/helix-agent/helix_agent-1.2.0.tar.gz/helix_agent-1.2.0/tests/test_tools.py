import pytest
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import tempfile
import os
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from helix_agent.tools import (
    AgentTools, MLTools, DataTools, ResearchTools, CollaborationTools
)

# ML Tools Tests
def test_prepare_data():
    # Generate synthetic data
    X, y = make_classification(n_samples=100, n_features=20, random_state=42)
    
    result = MLTools.prepare_data(X, y, test_size=0.2, random_state=42)
    
    assert 'X_train' in result
    assert 'X_test' in result
    assert 'y_train' in result
    assert 'y_test' in result
    assert 'scaler' in result
    assert result['X_train'].shape[0] == 80  # 80% of data
    assert result['X_test'].shape[0] == 20   # 20% of data

def test_train_model():
    X, y = make_classification(n_samples=100, n_features=20, random_state=42)
    model = RandomForestClassifier(random_state=42)
    
    # Test without hyperparameter tuning
    result = MLTools.train_model(model, X, y)
    assert 'model' in result
    assert 'cv_scores' in result
    
    # Test with hyperparameter tuning
    param_grid = {
        'n_estimators': [10, 20],
        'max_depth': [5, 10]
    }
    result = MLTools.train_model(model, X, y, param_grid=param_grid)
    assert 'best_params' in result
    assert 'best_score' in result

def test_evaluate_model():
    X, y = make_classification(n_samples=100, n_features=20, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(X[:80], y[:80])
    
    metrics = MLTools.evaluate_model(model, X[80:], y[80:])
    assert 'accuracy' in metrics
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert 'f1' in metrics
    assert 'confusion_matrix' in metrics

def test_analyze_feature_importance():
    X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)
    
    feature_names = [f'feature_{i}' for i in range(5)]
    result = MLTools.analyze_feature_importance(model, feature_names)
    
    assert 'feature_importance' in result
    assert 'total_features' in result
    assert result['total_features'] == 5
    assert len(result['feature_importance']) == 5

def test_save_load_model():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and train a simple model
        X, y = make_classification(n_samples=100, n_features=20, random_state=42)
        model = RandomForestClassifier(random_state=42)
        model.fit(X, y)
        
        # Save model
        save_path = os.path.join(tmpdir, 'model.joblib')
        save_result = MLTools.save_model(model, save_path)
        assert os.path.exists(save_path)
        
        # Load model
        load_result = MLTools.load_model(save_path)
        assert 'model' in load_result
        assert 'metadata' in load_result
        assert 'saved_at' in load_result

# Data Tools Tests
def test_validate_dataset():
    data = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['x', 'y', 'z'],
        'C': [1.1, 2.2, 3.3]
    })
    
    rules = {
        'dtypes': {
            'A': 'int64',
            'B': 'object',
            'C': 'float64'
        },
        'required_columns': ['A', 'B', 'C']
    }
    
    result = DataTools.validate_dataset(data, rules)
    assert result['passed'] is True
    assert len(result['issues']) == 0

def test_clean_dataset():
    data = pd.DataFrame({
        'A': [1, 2, 2, 3],
        'B': [1.1, None, 2.2, 2.2]
    })
    
    operations = [
        {'type': 'remove_duplicates'},
        {'type': 'fill_missing', 'method': 'mean'}
    ]
    
    result = DataTools.clean_dataset(data, operations)
    assert 'data' in result
    assert 'cleaning_log' in result
    # Verify cleaning operations were logged
    assert any(log['operation'] == 'remove_duplicates' for log in result['cleaning_log'])
    assert any(log['operation'] == 'fill_missing' for log in result['cleaning_log'])

def test_convert_format():
    data = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['x', 'y', 'z']
    })
    
    result = DataTools.convert_format(data, 'dataframe', 'json')
    assert result['success'] is True
    assert result['output_data'] is not None

# Research Tools Tests
def test_search_arxiv():
    results = ResearchTools.search_arxiv("quantum computing", max_results=2, sort_by="submittedDate")
    assert len(results) <= 2
    for paper in results:
        assert 'title' in paper
        assert 'authors' in paper
        assert 'summary' in paper

def test_generate_citation_graph():
    papers = [
        {
            'title': 'Paper A',
            'references': ['Paper B']
        },
        {
            'title': 'Paper B',
            'references': []
        }
    ]
    
    result = ResearchTools.generate_citation_graph(papers)
    assert 'nodes' in result
    assert 'edges' in result
    assert 'metrics' in result

# Collaboration Tools Tests
def test_generate_markdown_report():
    content = {
        'title': 'Test Report',
        'summary': 'This is a test report',
        'methods': ['Method 1', 'Method 2'],
        'results': {'accuracy': 0.95}
    }
    
    result = CollaborationTools.generate_markdown_report(content)
    assert 'markdown' in result
    assert 'html' in result
    assert 'word_count' in result

def test_track_changes():
    original = "This is the original text."
    modified = "This is the modified text."
    
    result = CollaborationTools.track_changes(original, modified)
    assert 'diff' in result
    assert 'additions' in result
    assert 'deletions' in result
    assert 'stats' in result

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
