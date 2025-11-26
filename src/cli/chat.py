import sys
from typing import List, Optional
from datetime import datetime


class ChatCLI:
    def __init__(self):
        self.conversation_history: List[dict] = []
        self.running = True

    def display_welcome(self):
        print("\n" + "=" * 60)
        print("  Welcome to Terminal Chat CLI")
        print("  Type your message and press Enter to chat")
        print("  Commands: /help, /clear, /history, /exit")
        print("=" * 60 + "\n")

    def display_help(self):
        print("\nAvailable Commands:")
        print("  /help     - Show this help message")
        print("  /clear    - Clear conversation history")
        print("  /history  - Show conversation history")
        print("  /exit     - Exit the chat")
        print()

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
        print("\nConversation history cleared.\n")

    def add_to_history(self, role: str, content: str):
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })

    def generate_response(self, user_message: str) -> str:
        return f"Echo: {user_message}"

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
        elif command == '/exit':
            self.running = False
            print("\nGoodbye!\n")
            return True

        return False

    def process_message(self, user_input: str):
        if user_input.startswith('/'):
            if self.handle_command(user_input):
                return

        self.add_to_history('user', user_input)

        print("\nAssistant: ", end='', flush=True)
        response = self.generate_response(user_input)
        print(response + "\n")

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
                    print("\n\nGoodbye!\n")
                    break
                except KeyboardInterrupt:
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
