import os
from typing import Dict, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv
from .base_agent import BaseAgent

load_dotenv()


class ClaudeAgent(BaseAgent):
    """Claude AI agent implementation using Anthropic API."""

    def __init__(self, name: str = "Claude", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.api_key = config.get('api_key') if config else None
        if not self.api_key:
            self.api_key = os.getenv('ANTHROPIC_API_KEY')

        self.model = config.get('model', 'claude-3-haiku-20240307') if config else 'claude-3-haiku-20240307'
        self.max_tokens = config.get('max_tokens', 4096) if config else 4096
        self.client = None

        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)

    def validate_config(self) -> bool:
        """Validate that API key is set."""
        if not self.api_key:
            return False
        if not self.client:
            return False
        return True

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request using Claude API.

        Args:
            request: Dictionary containing 'prompt' or 'messages'

        Returns:
            Dictionary with 'success', 'result', and optional 'error'
        """
        if not self.validate_config():
            return {
                'success': False,
                'result': '',
                'error': 'Claude agent not properly configured. Set ANTHROPIC_API_KEY environment variable.',
                'metadata': {}
            }

        try:
            prompt = request.get('prompt', '')
            messages = request.get('messages', [])
            system_prompt = request.get('system', None)

            if not messages and prompt:
                messages = [{"role": "user", "content": prompt}]

            create_params = {
                'model': self.model,
                'max_tokens': self.max_tokens,
                'messages': messages
            }

            if system_prompt:
                create_params['system'] = system_prompt

            response = self.client.messages.create(**create_params)

            result_text = response.content[0].text

            return {
                'success': True,
                'result': result_text,
                'metadata': {
                    'model': self.model,
                    'usage': {
                        'input_tokens': response.usage.input_tokens,
                        'output_tokens': response.usage.output_tokens
                    }
                }
            }

        except Exception as e:
            return {
                'success': False,
                'result': '',
                'error': f'Error calling Claude API: {str(e)}',
                'metadata': {}
            }

    def chat(self, message: str, conversation_history: Optional[list] = None, system: Optional[str] = None) -> Dict[str, Any]:
        """
        Simplified chat interface.

        Args:
            message: User message
            conversation_history: Optional list of previous messages
            system: Optional system prompt

        Returns:
            Response dictionary
        """
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})

        request = {'messages': messages}
        if system:
            request['system'] = system

        return self.process(request)
