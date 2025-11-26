import sys
import os
import time
import threading
import readline
from typing import List, Optional
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.claude_agent import ClaudeAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.orchestrator_agent import OrchestratorAgent
from models.toon import TOONRequest, TOONResponse


DOCGET_SYSTEM_PROMPT = """You are an AI assistant built into DOCGET, a terminal-based chatbot specialized in PDF analysis and hardware projects.

You have access to PDF documents from the data/ folder (provided in your context). Use them when relevant, but you're still a helpful general-purpose chatbot.

📁 When asked about AVAILABLE components/documents:
- "What components do we have?"
- "What's in our documents?"
- "What drones/cameras/chips are available?"
→ Answer ONLY from the provided PDF context. Don't suggest things not in the documents.

💬 For general questions:
- "How does a voltage regulator work?"
- "Explain PWM"
- "Help me design a circuit"
→ Use your general knowledge freely. Be helpful and educational.

🔍 When PDFs are relevant:
- Reference the specific PDF documents when using their information
- Cite which document contains specifications
- Use the actual specs from the PDFs when available

Your role:
- Be a helpful, conversational AI assistant
- Use PDF documents when they contain relevant information
- Provide guidance on hardware projects and electronics
- Answer general technical questions with your knowledge
- Be clear about what's in the documents vs. general knowledge

Response guidelines:
- Provide DIRECT, conversational responses
- Do NOT use "Task:", "Objective:", "Output:" sections
- Cite PDFs when using their information
- Keep responses focused and terminal-friendly
- Format technical data clearly

User context:
- Working on hardware projects
- Has PDFs in data/ folder for reference
- Using terminal interface
- Values helpful, accurate responses
- Commands: /help, /clear, /history, /debug, /exit
"""


class ChatCLI:
    def __init__(self):
        self.conversation_history: List[dict] = []
        self.running = True
        self.debug_mode = False
        self.thinking = False

        # Configure readline for command history (arrow key support)
        self.history_file = os.path.expanduser('~/.docget_history')
        self.setup_readline()

        # Initialize orchestrator agent (coordinates all other agents)
        self.orchestrator = OrchestratorAgent(name="Orchestrator")

        if not self.orchestrator.validate_config():
            print("\n⚠️  Warning: ANTHROPIC_API_KEY not set. Agent will not function properly.")
            print("Set your API key with: export ANTHROPIC_API_KEY='your-key-here'\n")

    def setup_readline(self):
        """Configure readline for command history and arrow key navigation."""
        try:
            # Load history file if it exists
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)

            # Set history length
            readline.set_history_length(1000)

            # Enable tab completion (optional)
            readline.parse_and_bind('tab: complete')
        except Exception as e:
            pass  # Silently fail if readline isn't available

    def save_history(self):
        """Save command history to file."""
        try:
            readline.write_history_file(self.history_file)
        except Exception:
            pass

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')

    def thinking_animation(self):
        """Display a thinking animation while the model processes."""
        animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        idx = 0
        while self.thinking:
            print(f"\r{animation[idx % len(animation)]} Thinking...", end='', flush=True)
            idx += 1
            time.sleep(0.1)
        print("\r" + " " * 20 + "\r", end='', flush=True)

    def display_welcome(self):
        self.clear_screen()
        print("\n" + "=" * 60)
        print("  DOCGET - PDF Analysis & Hardware Project Assistant")
        print("  Analyzes PDFs from 'data/' folder only")
        print("=" * 60)
        print("\n📁 " + self.orchestrator.get_available_pdfs_list())
        print("\n" + "─" * 60)
        print("  Commands: /help, /clear, /history, /debug, /exit")
        print("─" * 60 + "\n")

    def display_help(self):
        print("\n" + "=" * 60)
        print("  DOCGET Help")
        print("=" * 60)
        print("\nAvailable Commands:")
        print("  /help     - Show this help message")
        print("  /clear    - Clear conversation history and screen")
        print("  /history  - Show conversation history")
        print("  /debug    - Toggle debug mode")
        print("  /exit     - Exit the chat")
        print("\nAbout DOCGET:")
        print("  • Analyzes ONLY PDFs from the 'data/' folder")
        print("  • Specializes in hardware datasheets & specifications")
        print("  • Helps with hardware project design")
        print("  • Uses orchestrator to coordinate PDF extraction")
        print("\nHow to use:")
        print("  1. Place PDF files in the 'data/' folder")
        print("  2. Ask questions about the PDFs")
        print("  3. DOCGET will automatically find and analyze relevant PDFs")
        print("\n" + "─" * 60 + "\n")

    def display_history(self):
        if not self.conversation_history:
            print("\nNo conversation history yet.\n")
            return

        print("\n" + "-" * 60)
        print("Conversation History:")
        print("-" * 60)
        for i, msg in enumerate(self.conversation_history, 1):
            role = msg['role'].upper()
            content = msg['content']
            timestamp = msg['timestamp']
            print(f"\n[{i}] {role} ({timestamp}):")
            print(f"  {content}")
        print("-" * 60 + "\n")

    def clear_history(self):
        self.conversation_history.clear()
        self.clear_screen()
        self.display_welcome()

    def add_to_history(self, role: str, content: str):
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })

    def generate_response(self, user_message: str) -> str:
        """Generate response using orchestrator agent."""
        conversation_messages = []
        for msg in self.conversation_history:
            conversation_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        # Prepare request for orchestrator
        request = {
            'message': user_message,
            'conversation_history': conversation_messages,
            'system': DOCGET_SYSTEM_PROMPT,
            'context': {}  # Can add PDF paths or other context here
        }

        response = self.orchestrator.process(request)

        if self.debug_mode:
            print("[DEBUG] Response metadata:")
            if response.get('metadata'):
                pdf_count = response['metadata'].get('pdf_count', 0)
                used_pdf = response['metadata'].get('used_pdf', False)
                print(f"  Used PDF: {used_pdf}")
                if pdf_count > 0:
                    print(f"  PDFs analyzed: {pdf_count}")
                if 'model' in response['metadata']:
                    print(f"  Model: {response['metadata'].get('model', 'N/A')}")
                if 'usage' in response['metadata']:
                    print(f"  Tokens: {response['metadata']['usage']}")
            print()

        if not response['success']:
            return f"Error: {response.get('error', 'Unknown error')}"

        return response['result']

    def handle_command(self, command: str) -> bool:
        command = command.lower().strip()

        if command == '/help':
            self.display_help()
            return True
        elif command == '/clear':
            self.clear_history()
            return True
        elif command == '/history':
            self.display_history()
            return True
        elif command == '/debug':
            self.debug_mode = not self.debug_mode
            status = "enabled" if self.debug_mode else "disabled"
            print(f"\nDebug mode {status}.\n")
            return True
        elif command == '/exit':
            self.running = False
            self.save_history()
            self.clear_screen()
            print("\nGoodbye!\n")
            return True

        return False

    def process_message(self, user_input: str):
        if user_input.startswith('/'):
            if self.handle_command(user_input):
                return

        self.add_to_history('user', user_input)

        self.thinking = True
        thinking_thread = threading.Thread(target=self.thinking_animation)
        thinking_thread.start()

        response = self.generate_response(user_input)

        self.thinking = False
        thinking_thread.join()

        print(f"Assistant: {response}")
        print("─" * 60 + "\n")

        self.add_to_history('assistant', response)

    def run(self):
        self.display_welcome()

        try:
            while self.running:
                try:
                    user_input = input("You: ").strip()

                    if not user_input:
                        continue

                    self.process_message(user_input)

                except EOFError:
                    self.save_history()
                    self.clear_screen()
                    print("\nGoodbye!\n")
                    break
                except KeyboardInterrupt:
                    self.save_history()
                    self.clear_screen()
                    print("\n\nGoodbye!\n")
                    break

        except Exception as e:
            print(f"\nError: {e}")
            sys.exit(1)


def main():
    chat = ChatCLI()
    chat.run()


if __name__ == '__main__':
    main()
