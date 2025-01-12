import re
import json
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

class AgentTools:
    """A collection of utility tools that can be used with HelixAgent."""
    
    @staticmethod
    def parse_scientific_notation(text: str) -> List[float]:
        """Extract numbers in scientific notation from text."""
        pattern = r'[-+]?\d*\.?\d+[eE][-+]?\d+'
        return [float(match) for match in re.findall(pattern, text)]
    
    @staticmethod
    def format_citation(authors: List[str], title: str, journal: str, 
                       year: int, doi: Optional[str] = None) -> str:
        """Format a scientific citation in APA style."""
        citation = f"{', '.join(authors)} ({year}). {title}. {journal}"
        if doi:
            citation += f". DOI: {doi}"
        return citation
    
    @staticmethod
    def analyze_experiment_data(data: List[float], 
                              confidence_level: float = 0.95) -> Dict[str, Any]:
        """Perform statistical analysis on experimental data."""
        results = {
            'mean': float(np.mean(data)),
            'std_dev': float(np.std(data)),
            'sample_size': len(data),
            'confidence_interval': None
        }
        
        # Calculate confidence interval
        from scipy import stats
        ci = stats.t.interval(confidence_level, len(data)-1,
                            loc=np.mean(data),
                            scale=stats.sem(data))
        results['confidence_interval'] = (float(ci[0]), float(ci[1]))
        
        return results
    
    @staticmethod
    def create_experiment_protocol(steps: List[str], 
                                 materials: List[str],
                                 duration: str,
                                 conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Create a structured experiment protocol."""
        return {
            'protocol_id': f"EXP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'steps': steps,
            'materials': materials,
            'estimated_duration': duration,
            'conditions': conditions,
            'created_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def extract_paper_metadata(text: str) -> Dict[str, Any]:
        """Extract metadata from research paper text."""
        # Basic metadata extraction
        title_pattern = r'(?i)Title:\s*(.*?)(?=\n|$)'
        abstract_pattern = r'(?i)Abstract:\s*(.*?)(?=\n\n|\Z)'
        
        metadata = {
            'title': '',
            'abstract': '',
            'keywords': [],
            'references': []
        }
        
        # Extract title
        if title_match := re.search(title_pattern, text.strip()):
            metadata['title'] = f"Title: {title_match.group(1).strip()}"
            
        # Extract abstract
        if abstract_match := re.search(abstract_pattern, text, re.DOTALL):
            metadata['abstract'] = abstract_match.group(1).strip()
        
        # Extract keywords
        keywords_pattern = r'(?i)Keywords:\s*(.*?)(?=\n\n|\Z)'
        if keywords_match := re.search(keywords_pattern, text, re.DOTALL):
            metadata['keywords'] = [k.strip() for k in keywords_match.group(1).split(',')]
            
        return metadata
    
    @staticmethod
    def create_task_plan(objective: str, 
                        subtasks: List[str],
                        dependencies: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
        """Create a structured task plan with dependencies."""
        task_plan = {
            'objective': objective,
            'subtasks': [{'id': f'task-{i+1}', 'description': task, 'status': 'pending'}
                        for i, task in enumerate(subtasks)],
            'created_at': datetime.now().isoformat(),
            'status': 'not_started'
        }
        
        if dependencies:
            task_plan['dependencies'] = dependencies
            
        return task_plan
    
    @staticmethod
    def track_task_progress(task_plan: Dict[str, Any], 
                           completed_tasks: List[str]) -> Dict[str, Any]:
        """Update task plan with completed tasks and calculate progress."""
        total_tasks = len(task_plan['subtasks'])
        completed_count = 0
        
        for task in task_plan['subtasks']:
            if task['id'] in completed_tasks:
                task['status'] = 'completed'
                completed_count += 1
                
        progress = (completed_count / total_tasks) * 100
        
        task_plan['progress'] = progress
        task_plan['status'] = 'completed' if progress == 100 else 'in_progress'
        task_plan['last_updated'] = datetime.now().isoformat()
        
        return task_plan
    
    @staticmethod
    def simulate_experiment(protocol: Dict[str, Any], 
                          variables: Dict[str, Any],
                          iterations: int = 1) -> Dict[str, Any]:
        """Simulate an experiment based on protocol and variables."""
        results = []
        for i in range(iterations):
            # Add random variation to simulate real experimental conditions
            iteration_vars = {
                k: v * (1 + np.random.normal(0, 0.05))  # 5% random variation
                for k, v in variables.items()
                if isinstance(v, (int, float))
            }
            
            results.append({
                'iteration': i + 1,
                'variables': iteration_vars,
                'timestamp': datetime.now().isoformat()
            })
            
        return {
            'protocol_id': protocol['protocol_id'],
            'iterations': iterations,
            'results': results,
            'summary_stats': AgentTools.analyze_experiment_data(
                [r['variables'][list(variables.keys())[0]] for r in results]
            )
        }
