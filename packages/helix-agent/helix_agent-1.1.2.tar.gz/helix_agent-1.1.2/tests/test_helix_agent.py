import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from helix_agent.agent import HelixAgent

@pytest.fixture
def agent():
    return HelixAgent(
        agent_name="Test Scientist",
        model_name="helix-70b",
        tools_enabled=True,
        interactive=True,
        streaming_on=False,  # Disable streaming for testing
        api_key="test_key"
    )

def test_initialization():
    agent = HelixAgent(agent_name="Test Agent")
    assert agent.agent_name == "Test Agent"
    assert agent.model_name == "gpt-4"  # Default model mapping
    assert agent.interactive is True
    assert agent.use_context is True

def test_initialization_with_persona():
    agent = HelixAgent(persona="physicist")
    assert agent.agent_name == "Physicist"
    assert agent.persona_description == "An expert in physics, capable of explaining complex physical phenomena."

def test_invalid_model_name():
    with pytest.raises(ValueError, match="Invalid model_name"):
        HelixAgent(model_name="invalid-model")

@patch('openai.ChatCompletion.create')
def test_generate_response(mock_create):
    # Mock OpenAI response
    mock_create.return_value = {
        'choices': [{
            'message': {
                'content': 'Test response'
            }
        }]
    }
    
    agent = HelixAgent(streaming_on=False)
    response = agent.generate_response("Test prompt")
    
    assert response == "Test response"
    assert len(agent.context) == 2  # System message + user prompt

@patch('openai.ChatCompletion.create')
def test_generate_response_without_context(mock_create):
    mock_create.return_value = {
        'choices': [{
            'message': {
                'content': 'Test response'
            }
        }]
    }
    
    agent = HelixAgent(use_context=False, streaming_on=False)
    response = agent.generate_response("Test prompt")
    
    assert response == "Test response"
    assert agent.context is None

def test_reset_context(agent):
    agent.generate_response("Test prompt")
    assert len(agent.context) > 0
    
    agent.reset_context()
    assert len(agent.context) == 0

def test_export_context(agent):
    agent.generate_response("Test prompt")
    context = agent.export_context()
    
    assert isinstance(context, list)
    assert len(context) > 0
    assert all(isinstance(msg, dict) for msg in context)

def test_memory_management(agent):
    agent.learn("topic1", "test details")
    assert agent.recall("topic1") == "test details"
    assert agent.recall("nonexistent") == "I don't remember anything about that."

def test_plan_research_task(agent):
    plan = agent.plan_research_task(
        objective="Test objective",
        subtasks=["Task 1", "Task 2"],
        dependencies={"Task 2": ["Task 1"]}
    )
    
    assert plan['objective'] == "Test objective"
    assert len(plan['subtasks']) == 2
    assert plan['status'] == 'not_started'

def test_update_task_progress(agent):
    plan = agent.plan_research_task(
        objective="Test objective",
        subtasks=["Task 1", "Task 2", "Task 3"]
    )
    
    updated_plan = agent.update_task_progress(["task-1", "task-2"])
    
    assert updated_plan['progress'] == pytest.approx(66.67, rel=0.01)
    assert updated_plan['status'] == 'in_progress'
    assert updated_plan['subtasks'][0]['status'] == 'completed'
    assert updated_plan['subtasks'][1]['status'] == 'completed'
    assert updated_plan['subtasks'][2]['status'] == 'pending'

def test_create_experiment(agent):
    protocol = agent.create_experiment(
        steps=["Step 1", "Step 2"],
        materials=["Material A"],
        duration="1 hour",
        conditions={"temp": 25}
    )
    
    assert 'protocol_id' in protocol
    assert protocol['steps'] == ["Step 1", "Step 2"]
    assert protocol['materials'] == ["Material A"]
    assert protocol['estimated_duration'] == "1 hour"
    assert protocol['conditions'] == {"temp": 25}

def test_run_experiment(agent):
    protocol = agent.create_experiment(
        steps=["Step 1"],
        materials=["Material A"],
        duration="1 hour",
        conditions={"temp": 25}
    )
    
    results = agent.run_experiment(
        protocol=protocol,
        variables={"concentration": 0.5},
        iterations=3
    )
    
    assert results['protocol_id'] == protocol['protocol_id']
    assert results['iterations'] == 3
    assert len(results['results']) == 3
    assert 'summary_stats' in results
    
    # Check experiment history
    assert len(agent.experiment_history) == 1
    assert agent.experiment_history[0] == results

def test_analyze_paper(agent):
    paper_text = """
    Title: Test Paper
    
    Abstract: This is a test abstract.
    
    Keywords: test, research, science
    """
    
    metadata = agent.analyze_paper(paper_text)
    
    assert metadata['title'] == "Title: Test Paper"
    assert "test abstract" in metadata['abstract'].lower()
    assert len(metadata['keywords']) == 3

def test_format_citation(agent):
    citation = agent.format_citation(
        authors=["Smith, J.", "Doe, R."],
        title="Test Paper",
        journal="Test Journal",
        year=2023,
        doi="10.1234/test"
    )
    
    assert "Smith, J., Doe, R." in citation
    assert "Test Paper" in citation
    assert "Test Journal" in citation
    assert "2023" in citation
    assert "10.1234/test" in citation

def test_analyze_data(agent):
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    analysis = agent.analyze_data(data)
    
    assert analysis['mean'] == 3.0
    assert 'std_dev' in analysis
    assert analysis['sample_size'] == 5
    assert isinstance(analysis['confidence_interval'], tuple)

def test_tools_disabled():
    agent = HelixAgent(tools_enabled=False)
    
    with pytest.raises(ValueError, match="Tools must be enabled"):
        agent.plan_research_task("objective", ["task"])
        
    with pytest.raises(ValueError, match="Tools must be enabled"):
        agent.create_experiment([], [], "", {})
        
    with pytest.raises(ValueError, match="Tools must be enabled"):
        agent.analyze_paper("text")

def test_social_media_not_configured(agent):
    with pytest.raises(ValueError, match="Social media tools not configured"):
        agent.post_tweet("content")
        
    with pytest.raises(ValueError, match="Social media tools not configured"):
        agent.get_tweet_history()
        
    with pytest.raises(ValueError, match="Social media tools not configured"):
        agent.analyze_tweet_engagement("id")

@patch('openai.ChatCompletion.create')
def test_basic_collaboration(mock_create):
    """Test basic collaboration between two agents."""
    # Mock OpenAI responses for all API calls
    responses = [
        # Initial responses for physicist
        {"choices": [{"message": {"content": "Physics perspective: Quantum tunneling enables..."}}]},
        # Initial responses for biologist
        {"choices": [{"message": {"content": "Biology perspective: This mechanism affects..."}}]},
        # Second round responses
        {"choices": [{"message": {"content": "Physics analysis: The rate of tunneling..."}}]},
        {"choices": [{"message": {"content": "Biology conclusion: These effects are significant..."}}]},
    ]
    mock_create.side_effect = responses
    
    # Create specialized agents
    physicist = HelixAgent(
        agent_name="Quantum Physicist",
        persona="physicist",
        streaming_on=False,
        use_context=False  # Disable context to simplify response tracking
    )
    biologist = HelixAgent(
        agent_name="Molecular Biologist",
        persona="biologist",
        streaming_on=False,
        use_context=False
    )
    
    # Test collaboration
    discussion = physicist.collaborate(
        other_agent=biologist,
        prompt="Discuss quantum effects in enzyme catalysis",
        turns=2  # Two back-and-forth exchanges
    )
    
    # The discussion should contain the initial prompt and all responses
    assert "Discuss quantum effects in enzyme catalysis" in discussion
    assert "Physics perspective: Quantum tunneling enables..." in discussion
    assert "Biology perspective: This mechanism affects..." in discussion
    assert "Physics analysis: The rate of tunneling..." in discussion
    assert "Biology conclusion: These effects are significant..." in discussion

@patch('openai.ChatCompletion.create')
def test_multi_agent_research_collaboration(mock_create):
    """Test complex collaboration involving multiple agents and research tools."""
    # Mock OpenAI responses for all API calls
    responses = [
        # Chemist's response for analysis
        {"choices": [{"message": {"content": "Chemical mechanism analysis"}}]},
    ]
    mock_create.side_effect = responses
    
    # Create a team of specialized agents
    physicist = HelixAgent(
        persona="physicist",
        tools_enabled=True,
        streaming_on=False,
        use_context=False
    )
    biologist = HelixAgent(
        persona="biologist",
        tools_enabled=True,
        streaming_on=False,
        use_context=False
    )
    chemist = HelixAgent(
        persona="chemist",
        tools_enabled=True,
        streaming_on=False,
        use_context=False
    )
    
    # Test collaborative experiment
    # 1. Physicist designs experiment
    protocol = physicist.create_experiment(
        steps=[
            "Setup quantum tunneling detector",
            "Prepare enzyme samples",
            "Measure reaction rates"
        ],
        materials=[
            "Quantum detector",
            "Purified enzymes",
            "Temperature control"
        ],
        duration="2 hours",
        conditions={"temperature": 5}
    )
    
    assert protocol['steps'][0] == "Setup quantum tunneling detector"
    assert len(protocol['materials']) == 3
    
    # 2. Run experiment and get physicist's analysis
    physics_results = physicist.run_experiment(
        protocol=protocol,
        variables={"tunneling_rate": 0.1},
        iterations=3
    )
    
    assert physics_results['iterations'] == 3
    assert 'tunneling_rate' in physics_results['results'][0]['variables']
    
    # 3. Get biologist's interpretation
    biology_analysis = biologist.analyze_data(
        [r['variables']['tunneling_rate'] for r in physics_results['results']]
    )
    
    assert 'mean' in biology_analysis
    assert 'confidence_interval' in biology_analysis
    
    # 4. Get chemist's insights
    chemistry_response = chemist.generate_response(
        f"Analyze these results from chemical perspective:\n"
        f"Physics data: {physics_results['summary_stats']}\n"
        f"Biology analysis: {biology_analysis}"
    )
    
    assert "Chemical mechanism analysis" in chemistry_response

@patch('openai.ChatCompletion.create')
def test_collaborative_task_planning(mock_create):
    """Test collaborative research task planning between agents."""
    # Mock responses for generate_response calls
    responses = [
        # Response for physicist's analysis
        {"choices": [{"message": {"content": "Collaborative research plan analysis"}}]},
    ]
    mock_create.side_effect = responses
    
    # Create agents with different expertise
    physicist = HelixAgent(
        persona="physicist",
        tools_enabled=True,
        streaming_on=False,
        use_context=False
    )
    biologist = HelixAgent(
        persona="biologist",
        tools_enabled=True,
        streaming_on=False,
        use_context=False
    )
    
    # Create task plans for both agents
    subtasks = [
        "Review quantum biology literature",
        "Design quantum measurements",
        "Analyze biological samples",
        "Integrate findings"
    ]
    dependencies = {
        "task-2": ["task-1"],
        "task-3": ["task-1"],
        "task-4": ["task-2", "task-3"]
    }
    
    # Create separate plans for each agent
    physics_plan = physicist.plan_research_task(
        objective="Study quantum effects in photosynthesis",
        subtasks=subtasks,
        dependencies=dependencies
    )
    
    biology_plan = biologist.plan_research_task(
        objective="Study quantum effects in photosynthesis",
        subtasks=subtasks,
        dependencies=dependencies
    )
    
    # Update progress from both perspectives
    physics_update = physicist.update_task_progress(["task-1", "task-2"])
    biology_update = biologist.update_task_progress(["task-1", "task-3"])
    
    assert physics_update['progress'] == 50.0
    assert biology_update['progress'] == 50.0
    
    # Get collaborative analysis
    collaborative_analysis = physicist.generate_response(
        f"Analyze research progress:\n"
        f"Physics tasks: {physics_update['progress']}% complete\n"
        f"Biology tasks: {biology_update['progress']}% complete"
    )
    
    assert "Collaborative research plan analysis" in collaborative_analysis
