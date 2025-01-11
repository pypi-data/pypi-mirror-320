import openai
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from .tools import AgentTools
from .social import SocialMediaTools

class HelixAgent:
    # Mapping of user-friendly model names to actual OpenAI model names
    MODEL_NAME_MAPPING = {
        "helix-70b": "gpt-4",
        "helix-3b-small": "gpt-4o-mini",
    }
    
    # Predefined agent personas
    PREDEFINED_PERSONAS = {
        "neuroscientist": "An expert in neuroscience, specializing in the study of the brain and nervous system.",
        "physicist": "An expert in physics, capable of explaining complex physical phenomena.",
        "biologist": "An expert in biology, with a focus on living organisms and ecosystems.",
    }

    def __init__(self,
                 agent_name="Default Scientist",
                 model_name="helix-70b",
                 tools_enabled=True,
                 max_loops="auto",
                 interactive=True,
                 streaming_on=True,
                 api_key=None,
                 temperature=0.7,
                 max_tokens=150,
                 top_p=1.0,
                 frequency_penalty=0.0,
                 presence_penalty=0.0,
                 use_context=True,
                 persona=None,
                 logging_enabled=False,
                 log_file="helix_agent.log",
                 twitter_config=None):
        """
        Initialize the HelixAgent.

        Parameters:
            agent_name (str): The name of the agent.
            model_name (str): One of the allowed Helix model names ("helix-70b", "helix-3b-small").
            max_loops (int or str): Maximum loops for task processing ('auto' for dynamic adjustment).
            interactive (bool): Whether the agent operates interactively.
            streaming_on (bool): Whether to use streaming for responses.
            api_key (str): OpenAI API key.
            temperature (float): Controls the randomness of the output.
            max_tokens (int): Maximum length of the output response.
            top_p (float): Controls diversity via nucleus sampling.
            frequency_penalty (float): Penalizes repeated phrases in the output.
            presence_penalty (float): Encourages new topic exploration in the response.
            use_context (bool): Enable or disable conversation context tracking.
            persona (str): Predefined persona for the agent.
            logging_enabled (bool): Enable logging of interactions.
            log_file (str): Path to the log file.
            twitter_config (dict): Twitter API credentials for social media integration.
        """
        if model_name not in self.MODEL_NAME_MAPPING:
            raise ValueError(f"Invalid model_name '{model_name}'. Choose from: {list(self.MODEL_NAME_MAPPING.keys())}")
        
        self.agent_name = agent_name
        self.model_name = self.MODEL_NAME_MAPPING[model_name]
        self.max_loops = max_loops
        self.interactive = interactive
        self.streaming_on = streaming_on
        self.api_key = api_key or "Your-Default-API-Key"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.use_context = use_context
        self.logging_enabled = logging_enabled
        self.log_file = log_file if logging_enabled else None
        self.memory = {}
        
        # Set predefined persona
        if persona in self.PREDEFINED_PERSONAS:
            self.agent_name = persona.capitalize()
            self.persona_description = self.PREDEFINED_PERSONAS[persona]
        else:
            self.persona_description = None
        
        self.context = [] if use_context else None
        self.tools = AgentTools() if tools_enabled else None
        self.social = SocialMediaTools(twitter_config) if twitter_config else None
        self.current_task = None
        self.experiment_history = []

        openai.api_key = self.api_key  # Set the OpenAI API key

    def log(self, message):
        if self.logging_enabled and self.log_file:
            with open(self.log_file, "a") as f:
                f.write(message + "\n")

    def generate_response(self, prompt):
        """
        Generate a response from the AI model.

        Parameters:
            prompt (str): The input prompt for the AI.

        Returns:
            str: The response from the AI model.
        """
        if self.logging_enabled:
            self.log(f"Prompt: {prompt}")
        
        if self.use_context:
            self.context.append({"role": "user", "content": prompt})
            messages = [{"role": "system", "content": f"You are a {self.agent_name}."}] + self.context
        else:
            messages = [{"role": "system", "content": f"You are a {self.agent_name}."},
                        {"role": "user", "content": prompt}]

        try:
            if self.streaming_on:
                response = self._stream_response(messages)
            else:
                response = self._get_response(messages)
        except Exception as e:
            response = f"Error: {e}"
        
        if self.logging_enabled:
            self.log(f"Response: {response}")
        
        if self.use_context and isinstance(response, str):
            self.context.append({"role": "assistant", "content": response})
        
        return response

    def _get_response(self, messages):
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
        )
        return response['choices'][0]['message']['content']

    def _stream_response(self, messages):
        response_stream = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stream=True,
        )
        response_text = ""
        for chunk in response_stream:
            content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
            response_text += content
            print(content, end="", flush=True)  # Streaming to console
        return response_text

    def reset_context(self):
        """Reset the conversation context."""
        if self.use_context:
            self.context = []

    def export_context(self):
        """Export the current conversation context."""
        return self.context

    def learn(self, topic, details):
        """Learn and store information about a topic."""
        self.memory[topic] = details

    def recall(self, topic):
        """Recall stored information about a topic."""
        return self.memory.get(topic, "I don't remember anything about that.")

    def summarize(self, text):
        """Summarize the given text."""
        summary_prompt = f"Summarize the following text concisely:\n\n{text}"
        return self.generate_response(summary_prompt)

    def extract_key_points(self, text):
        """Extract key points from the given text."""
        key_points_prompt = f"Extract the key points from the following text:\n\n{text}"
        return self.generate_response(key_points_prompt)

    def suggest_related_topics(self, topic):
        """Suggest related topics to the given topic."""
        suggestion_prompt = f"Suggest related topics to '{topic}' in the field of {self.agent_name.lower()}."
        return self.generate_response(suggestion_prompt)

    def collaborate(self, other_agent, prompt, turns=3):
        """
        Collaborate with another HelixAgent on a task.

        Parameters:
            other_agent (HelixAgent): The other agent to collaborate with.
            prompt (str): Initial prompt for the conversation.
            turns (int): Number of turns in the collaboration.

        Returns:
            str: The final output of the collaboration.
        """
        conversation = [{"role": "user", "content": prompt}]
        for _ in range(turns):
            response = self.generate_response(conversation[-1]["content"])
            conversation.append({"role": "assistant", "content": response})
            response = other_agent.generate_response(conversation[-1]["content"])
            conversation.append({"role": "assistant", "content": response})
        return "\n".join([msg["content"] for msg in conversation])

    async def generate_response_async(self, prompt):
        """Asynchronous response generation."""
        messages = [{"role": "system", "content": f"You are a {self.agent_name}."},
                    {"role": "user", "content": prompt}]
        response = await openai.ChatCompletion.acreate(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response['choices'][0]['message']['content']

    def plan_research_task(self, objective: str, subtasks: List[str], 
                          dependencies: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
        """Create a structured research task plan."""
        if not self.tools:
            raise ValueError("Tools must be enabled to use this feature")
        self.current_task = self.tools.create_task_plan(objective, subtasks, dependencies)
        return self.current_task

    def update_task_progress(self, completed_tasks: List[str]) -> Dict[str, Any]:
        """Update the progress of the current research task."""
        if not self.tools or not self.current_task:
            raise ValueError("No active task plan found")
        self.current_task = self.tools.track_task_progress(self.current_task, completed_tasks)
        return self.current_task

    def create_experiment(self, steps: List[str], materials: List[str],
                         duration: str, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new experiment protocol."""
        if not self.tools:
            raise ValueError("Tools must be enabled to use this feature")
        protocol = self.tools.create_experiment_protocol(steps, materials, duration, conditions)
        return protocol

    def run_experiment(self, protocol: Dict[str, Any], variables: Dict[str, Any],
                      iterations: int = 1) -> Dict[str, Any]:
        """Run a simulated experiment and analyze results."""
        if not self.tools:
            raise ValueError("Tools must be enabled to use this feature")
        results = self.tools.simulate_experiment(protocol, variables, iterations)
        self.experiment_history.append(results)
        return results

    def analyze_paper(self, paper_text: str) -> Dict[str, Any]:
        """Extract and analyze metadata from a research paper."""
        if not self.tools:
            raise ValueError("Tools must be enabled to use this feature")
        return self.tools.extract_paper_metadata(paper_text)

    def format_citation(self, authors: List[str], title: str, journal: str,
                       year: int, doi: Optional[str] = None) -> str:
        """Format a citation in APA style."""
        if not self.tools:
            raise ValueError("Tools must be enabled to use this feature")
        return self.tools.format_citation(authors, title, journal, year, doi)

    def analyze_data(self, data: List[float], confidence_level: float = 0.95) -> Dict[str, Any]:
        """Perform statistical analysis on experimental data."""
        if not self.tools:
            raise ValueError("Tools must be enabled to use this feature")
        return self.tools.analyze_experiment_data(data, confidence_level)

    def parse_scientific_values(self, text: str) -> List[float]:
        """Extract scientific notation values from text."""
        if not self.tools:
            raise ValueError("Tools must be enabled to use this feature")
        return self.tools.parse_scientific_notation(text)

    def get_experiment_history(self) -> List[Dict[str, Any]]:
        """Retrieve the history of conducted experiments."""
        return self.experiment_history

    def post_tweet(self, content: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Post a tweet with optional media attachments."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.post_tweet(content, media_paths)

    def schedule_tweet(self, content: str, scheduled_time: datetime,
                      media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Schedule a tweet for future posting."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.schedule_tweet(content, scheduled_time, media_paths)

    def get_tweet_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent tweets from the account."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.get_tweet_history(count)

    def analyze_tweet_engagement(self, tweet_id: str) -> Dict[str, Any]:
        """Analyze engagement metrics for a specific tweet."""
        if not self.social:
            raise ValueError("Social media tools not configured. Provide twitter_config during initialization.")
        return self.social.analyze_engagement(tweet_id)

    def __repr__(self):
        tools_status = "enabled" if self.tools else "disabled"
        social_status = "enabled" if self.social else "disabled"
        return (f"<HelixAgent(agent_name={self.agent_name}, model_name={self.model_name}, "
                f"interactive={self.interactive}, streaming_on={self.streaming_on}, "
                f"tools={tools_status}, social={social_status})>")
