import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    """Configuration management for the application."""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            env_file: Path to .env file (optional)
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        self._validate_config()

    @property
    def anthropic_api_key(self) -> str:
        """Get Anthropic API key from environment."""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        return api_key

    @property
    def model_name(self) -> str:
        """Get Claude model name."""
        return os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')

    @property
    def max_tokens(self) -> int:
        """Get max tokens for Claude API."""
        return int(os.getenv('MAX_TOKENS', '4096'))

    @property
    def temperature(self) -> float:
        """Get temperature for Claude API."""
        return float(os.getenv('TEMPERATURE', '0'))

    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    @property
    def data_dir(self) -> Path:
        """Get data directory."""
        return self.project_root / 'data'

    @property
    def pdf_dir(self) -> Path:
        """Get PDF input directory."""
        pdf_path = self.data_dir / 'pdfs'
        pdf_path.mkdir(parents=True, exist_ok=True)
        return pdf_path

    @property
    def output_dir(self) -> Path:
        """Get output directory."""
        output_path = self.data_dir / 'output'
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path

    @property
    def prompts_dir(self) -> Path:
        """Get prompts directory."""
        return self.project_root / 'prompts'

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return os.getenv('LOG_LEVEL', 'INFO')

    def _validate_config(self):
        """Validate configuration."""
        try:
            # Check if API key exists
            _ = self.anthropic_api_key
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.warning(f"Configuration validation warning: {e}")

    def get_prompt(self, prompt_name: str) -> str:
        """
        Load a prompt template.

        Args:
            prompt_name: Name of the prompt file (without .txt extension)

        Returns:
            Prompt template content
        """
        prompt_path = self.prompts_dir / f"{prompt_name}.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

        return prompt_path.read_text()

    @classmethod
    def create_example_env(cls, output_path: str = '.env.example'):
        """
        Create an example .env file.

        Args:
            output_path: Path to save the example file
        """
        example_content = """# Anthropic API Configuration
ANTHROPIC_API_KEY=your_api_key_here

# Claude Model Settings
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_TOKENS=4096
TEMPERATURE=0

# Logging
LOG_LEVEL=INFO
"""
        with open(output_path, 'w') as f:
            f.write(example_content)

        logger.info(f"Example .env file created at: {output_path}")
