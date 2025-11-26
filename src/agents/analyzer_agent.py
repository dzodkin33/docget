from typing import Dict, Any, Optional
from .claude_agent import ClaudeAgent


class AnalyzerAgent:
    """
    Agent that analyzes user requests and creates structured TOON requirements.
    This agent acts as an intermediary that processes raw user input.
    """

    def __init__(self, backend_agent: Optional[ClaudeAgent] = None):
        """
        Initialize the analyzer agent.

        Args:
            backend_agent: The agent to use for analysis (default: ClaudeAgent)
        """
        self.backend_agent = backend_agent or ClaudeAgent(name="Analyzer")

    def analyze_request(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user input and create a TOON-structured requirement.

        Args:
            user_input: Raw user input string

        Returns:
            Dictionary with TOON structure fields
        """
        analysis_prompt = f"""Analyze the following user request and extract:
1. Task: What specific task needs to be done
2. Objective: The goal or purpose of this task
3. Output Format: What format the result should be in
4. Notes: Any additional context or constraints

User Request: "{user_input}"

Respond in this exact format:
TASK: [extracted task]
OBJECTIVE: [extracted objective]
OUTPUT_FORMAT: [desired output format]
NOTES: [any additional notes or context]"""

        response = self.backend_agent.chat(analysis_prompt)

        if not response['success']:
            return {
                'task': user_input,
                'objective': 'Respond to user query',
                'output_format': 'text',
                'notes': 'Failed to analyze request'
            }

        return self._parse_analysis(response['result'], user_input)

    def _parse_analysis(self, analysis_text: str, original_input: str) -> Dict[str, Any]:
        """Parse the analysis response into TOON fields."""
        toon_data = {
            'task': original_input,
            'objective': 'Respond to user query',
            'output_format': 'text',
            'notes': ''
        }

        try:
            lines = analysis_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('TASK:'):
                    toon_data['task'] = line.replace('TASK:', '').strip()
                elif line.startswith('OBJECTIVE:'):
                    toon_data['objective'] = line.replace('OBJECTIVE:', '').strip()
                elif line.startswith('OUTPUT_FORMAT:'):
                    toon_data['output_format'] = line.replace('OUTPUT_FORMAT:', '').strip()
                elif line.startswith('NOTES:'):
                    toon_data['notes'] = line.replace('NOTES:', '').strip()
        except:
            pass

        return toon_data

    def create_toon_request(self, user_input: str, context: Optional[Dict[str, Any]] = None):
        """
        Create a TOON request from user input.

        Args:
            user_input: Raw user input
            context: Optional context dictionary

        Returns:
            TOONRequest object
        """
        from models.toon import TOONRequest

        analysis = self.analyze_request(user_input)

        return TOONRequest(
            task=analysis['task'],
            objective=analysis['objective'],
            output_format=analysis['output_format'],
            notes=analysis['notes'],
            context=context or {}
        )
