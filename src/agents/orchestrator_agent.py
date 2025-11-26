import os
import sys
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import from sibling directories
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.PdfExtractor import ClaudePDFAgent
from .claude_agent import ClaudeAgent
from .base_agent import BaseAgent


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator agent that coordinates multiple specialized agents.

    Flow:
    1. Receives request from CLI
    2. Analyzes request and breaks it into tasks
    3. Calls appropriate agents (PdfExtractor, etc.)
    4. Accumulates results
    5. Synthesizes final response
    """

    def __init__(self, name: str = "Orchestrator", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

        # Initialize specialized agents
        self.claude_agent = ClaudeAgent(name="Claude", config=config)
        self.pdf_extractor = ClaudePDFAgent()

        # Store accumulated task results
        self.task_results: List[Dict[str, Any]] = []

        # Data folder for PDFs
        self.data_folder = Path("data")
        self.cache_file = Path(".docget_cache.json")
        self.available_pdfs: List[Path] = []
        self.pdf_metadata: Dict[str, str] = {}
        self.pdf_content_cache: Dict[str, str] = {}  # Cache for pre-loaded PDF content
        self.scan_data_folder()
        self.preload_pdf_context()

    def scan_data_folder(self):
        """Scan the data folder for available PDFs."""
        if not self.data_folder.exists():
            self.data_folder.mkdir(parents=True, exist_ok=True)
            return

        self.available_pdfs = list(self.data_folder.glob("*.pdf"))

        # Store simple metadata (just filenames for now)
        for pdf_path in self.available_pdfs:
            self.pdf_metadata[pdf_path.stem] = str(pdf_path)

    def load_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load cached PDF content from file."""
        if not self.cache_file.exists():
            return {}

        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"   ⚠ Error reading cache: {e}")
            return {}

    def save_cache(self, cache_data: Dict[str, Dict[str, Any]]):
        """Save PDF content cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"   ⚠ Error saving cache: {e}")

    def get_pdf_mtime(self, pdf_path: Path) -> float:
        """Get modification time of PDF file."""
        return pdf_path.stat().st_mtime

    def chunk_text(self, text: str, chunk_size: int = 8000) -> List[str]:
        """
        Split text into chunks of approximately chunk_size characters.
        Tries to break at sentence boundaries.
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        current_chunk = ""

        # Split by sentences (rough approximation)
        sentences = text.replace('\n', ' ').split('. ')

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= chunk_size:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def summarize_chunks(self, chunks: List[str], pdf_name: str) -> str:
        """Summarize multiple chunks into a coherent overview."""
        if len(chunks) == 1:
            return chunks[0]

        # Combine first few chunks for overview
        combined = "\n\n".join(chunks[:3])  # Use first 3 chunks
        return f"[Document chunked into {len(chunks)} parts]\n\n{combined[:5000]}..."

    def preload_pdf_context(self):
        """Pre-load and cache content from all PDFs for faster access."""
        print("📚 Loading PDF documents...")

        # Load existing cache
        cache_data = self.load_cache()
        needs_save = False

        for pdf_path in self.available_pdfs:
            try:
                pdf_name = pdf_path.name
                pdf_mtime = self.get_pdf_mtime(pdf_path)

                # Check if we have a valid cached version
                if pdf_name in cache_data:
                    cached_mtime = cache_data[pdf_name].get('mtime', 0)
                    if cached_mtime == pdf_mtime:
                        # Use cached content
                        print(f"   ✓ {pdf_name} (from cache)")
                        self.pdf_content_cache[pdf_name] = cache_data[pdf_name]['content']
                        continue

                # Extract comprehensive content
                print(f"   • Extracting {pdf_name}...")

                # Get overview
                overview = self.pdf_extractor.answer_question(
                    str(pdf_path),
                    "Provide a comprehensive overview of this document. Include: "
                    "1. What type of document is this (datasheet, specification, manual, etc.)? "
                    "2. What product/component/system does it describe? "
                    "3. Key specifications and important details. "
                    "4. Main features or capabilities."
                )

                # Get full text extraction
                try:
                    full_text = self.pdf_extractor.extract_text(str(pdf_path))
                except Exception:
                    full_text = None

                # Chunk large text
                text_chunks = []
                if full_text:
                    text_chunks = self.chunk_text(full_text, chunk_size=8000)
                    if len(text_chunks) > 1:
                        print(f"      → Split into {len(text_chunks)} chunks")

                # Get tables if available
                try:
                    tables = self.pdf_extractor.extract_tables(str(pdf_path))
                except Exception:
                    tables = []

                # Create comprehensive summary
                comprehensive_content = f"=== OVERVIEW ===\n{overview}\n"

                if tables:
                    comprehensive_content += f"\n=== TABLES ({len(tables)} found) ===\n"
                    for i, table in enumerate(tables, 1):
                        comprehensive_content += f"\nTable {i}:\n{str(table)}\n"

                if text_chunks:
                    if len(text_chunks) == 1:
                        comprehensive_content += f"\n=== FULL TEXT ===\n{text_chunks[0]}\n"
                    else:
                        comprehensive_content += f"\n=== FULL TEXT ({len(text_chunks)} chunks) ===\n"
                        comprehensive_content += f"Chunk 1 of {len(text_chunks)}:\n{text_chunks[0][:3000]}...\n"
                        comprehensive_content += f"\n[Additional chunks available in cache]\n"

                # Cache the comprehensive content
                self.pdf_content_cache[pdf_name] = comprehensive_content
                cache_data[pdf_name] = {
                    'overview': overview,
                    'text_chunks': text_chunks,  # Store all chunks
                    'chunk_count': len(text_chunks),
                    'tables': tables,
                    'content': comprehensive_content,
                    'mtime': pdf_mtime,
                    'extracted_at': datetime.now().isoformat()
                }
                needs_save = True

            except Exception as e:
                print(f"   ⚠ Error loading {pdf_path.name}: {e}")
                self.pdf_content_cache[pdf_path.name] = f"(Error loading document: {e})"

        # Save updated cache
        if needs_save:
            self.save_cache(cache_data)

        print(f"✓ Loaded {len(self.pdf_content_cache)} documents\n")

    def get_available_pdfs_list(self) -> str:
        """Get a formatted list of available PDFs."""
        if not self.available_pdfs:
            return "No PDFs available in data folder."

        pdf_list = "\n".join([f"  - {pdf.name}" for pdf in self.available_pdfs])
        return f"Available PDFs in data folder:\n{pdf_list}"

    def get_full_pdf_context(self) -> str:
        """Get the complete cached context from all PDFs."""
        if not self.pdf_content_cache:
            return ""

        context = "\n=== AVAILABLE COMPONENTS AND DOCUMENTS (from data/ folder) ===\n"
        for pdf_name, content in self.pdf_content_cache.items():
            context += f"\n--- {pdf_name} ---\n{content}\n"

        context += "\n=== END OF AVAILABLE DOCUMENTS ===\n"
        return context

    def get_cached_tables(self, pdf_name: str) -> list:
        """Get cached tables from a specific PDF."""
        cache_data = self.load_cache()
        if pdf_name in cache_data:
            return cache_data[pdf_name].get('tables', [])
        return []

    def get_cached_chunks(self, pdf_name: str) -> List[str]:
        """Get all cached text chunks from a specific PDF."""
        cache_data = self.load_cache()
        if pdf_name in cache_data:
            return cache_data[pdf_name].get('text_chunks', [])
        return []

    def get_cached_full_text(self, pdf_name: str, assembled: bool = True) -> Optional[str]:
        """
        Get cached full text from a specific PDF.
        If assembled=True, joins all chunks together.
        """
        chunks = self.get_cached_chunks(pdf_name)
        if not chunks:
            return None

        if assembled:
            return '\n\n'.join(chunks)
        else:
            return chunks[0] if chunks else None

    def get_chunk_info(self, pdf_name: str) -> Dict[str, Any]:
        """Get information about chunks for a specific PDF."""
        cache_data = self.load_cache()
        if pdf_name in cache_data:
            chunk_count = cache_data[pdf_name].get('chunk_count', 0)
            chunks = cache_data[pdf_name].get('text_chunks', [])
            return {
                'chunk_count': chunk_count,
                'total_chars': sum(len(chunk) for chunk in chunks),
                'avg_chunk_size': sum(len(chunk) for chunk in chunks) // chunk_count if chunk_count > 0 else 0
            }
        return {}

    def get_all_cached_tables(self) -> Dict[str, list]:
        """Get all cached tables from all PDFs."""
        cache_data = self.load_cache()
        all_tables = {}
        for pdf_name, data in cache_data.items():
            tables = data.get('tables', [])
            if tables:
                all_tables[pdf_name] = tables
        return all_tables

    def find_relevant_pdfs(self, user_request: str) -> List[Path]:
        """Determine which PDFs might be relevant to the user's request."""
        if not self.available_pdfs:
            return []

        # For now, return all PDFs - later we can make this smarter
        # by analyzing the request and matching against PDF names/content
        relevant = []
        request_lower = user_request.lower()

        # Simple keyword matching based on filename
        for pdf_path in self.available_pdfs:
            filename_lower = pdf_path.stem.lower()
            # If any word from filename is in the request, consider it relevant
            words = filename_lower.replace('-', ' ').replace('_', ' ').split()
            if any(word in request_lower for word in words if len(word) > 3):
                relevant.append(pdf_path)

        # If no specific matches, return all PDFs (user might want to search across all)
        if not relevant and len(self.available_pdfs) <= 5:
            return self.available_pdfs

        return relevant

    def validate_config(self) -> bool:
        """Validate that required agents are properly configured."""
        return self.claude_agent.validate_config()

    def analyze_request(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze the user request to determine what tasks need to be done.

        Returns:
            Dictionary with 'needs_pdf', 'pdf_paths', 'task_type', 'instructions'
        """
        analysis_prompt = f"""Analyze this user request and determine what needs to be done:

User Request: "{user_request}"

Context: {context or 'None'}

Determine:
1. Does this require PDF analysis? (yes/no)
2. What type of task is this? (answer_question, extract_data, summarize, general_chat, hardware_help)
3. What are the key requirements?

Respond in this format:
NEEDS_PDF: yes/no
TASK_TYPE: [task type]
REQUIREMENTS: [brief description]"""

        response = self.claude_agent.process({
            'prompt': analysis_prompt,
            'messages': []
        })

        if not response['success']:
            return {
                'needs_pdf': False,
                'task_type': 'general_chat',
                'requirements': user_request
            }

        # Parse the analysis
        analysis_text = response['result']
        analysis = {
            'needs_pdf': False,
            'task_type': 'general_chat',
            'requirements': user_request,
            'pdf_paths': []
        }

        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('NEEDS_PDF:'):
                analysis['needs_pdf'] = 'yes' in line.lower()
            elif line.startswith('TASK_TYPE:'):
                analysis['task_type'] = line.split(':', 1)[1].strip()
            elif line.startswith('REQUIREMENTS:'):
                analysis['requirements'] = line.split(':', 1)[1].strip()

        # Look for PDF paths in context first
        if context and 'pdf_path' in context:
            analysis['pdf_paths'] = [context['pdf_path']]
        elif context and 'pdf_paths' in context:
            analysis['pdf_paths'] = context['pdf_paths']
        else:
            # Automatically find relevant PDFs from data folder
            relevant_pdfs = self.find_relevant_pdfs(user_request)
            if relevant_pdfs:
                analysis['pdf_paths'] = [str(pdf) for pdf in relevant_pdfs]
                analysis['needs_pdf'] = True  # Override if we found relevant PDFs

        return analysis

    def execute_pdf_task(self, task_type: str, pdf_path: str, query: str) -> Dict[str, Any]:
        """Execute a PDF-related task using PdfExtractor."""
        try:
            if task_type == 'answer_question':
                result = self.pdf_extractor.answer_question(pdf_path, query)
                return {'success': True, 'result': result, 'type': 'pdf_answer'}

            elif task_type == 'extract_data':
                result = self.pdf_extractor.extract_text(pdf_path)
                return {'success': True, 'result': result, 'type': 'pdf_extraction'}

            elif task_type == 'summarize':
                result = self.pdf_extractor.summarize(pdf_path)
                return {'success': True, 'result': result, 'type': 'pdf_summary'}

            else:
                # Default: answer question
                result = self.pdf_extractor.answer_question(pdf_path, query)
                return {'success': True, 'result': result, 'type': 'pdf_answer'}

        except Exception as e:
            return {
                'success': False,
                'error': f'PDF extraction failed: {str(e)}',
                'type': 'error'
            }

    def synthesize_response(self, user_request: str, task_results: List[Dict[str, Any]],
                          conversation_history: Optional[List] = None) -> str:
        """
        Synthesize final response from accumulated task results.
        """
        if not task_results:
            return "I couldn't process your request. Please try again."

        # If only one task and it was successful, return it directly
        if len(task_results) == 1 and task_results[0].get('success'):
            return task_results[0].get('result', 'No result available')

        # If multiple tasks or need synthesis, use Claude to combine results
        synthesis_prompt = f"""User asked: "{user_request}"

I've gathered the following information:

"""
        for i, result in enumerate(task_results, 1):
            if result.get('success'):
                synthesis_prompt += f"\n{i}. {result.get('type', 'Result')}: {result.get('result', '')}\n"
            else:
                synthesis_prompt += f"\n{i}. Error: {result.get('error', 'Unknown error')}\n"

        synthesis_prompt += """\n\nBased on this information, provide a clear, helpful response to the user's question.
Be direct and conversational. Format for terminal display."""

        response = self.claude_agent.chat(
            synthesis_prompt,
            conversation_history or [],
            system="You synthesize information from multiple sources into clear, helpful responses."
        )

        if response['success']:
            return response['result']
        else:
            # Fallback: return first successful result
            for result in task_results:
                if result.get('success'):
                    return result.get('result', 'Processing completed')
            return "Error processing request"

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration logic.

        Args:
            request: {
                'message': user message,
                'context': optional context dict,
                'conversation_history': optional conversation history
            }
        """
        user_message = request.get('message', '')
        context = request.get('context', {})
        conversation_history = request.get('conversation_history', [])

        # Clear previous task results
        self.task_results = []

        # Step 1: Analyze the request
        analysis = self.analyze_request(user_message, context)

        # Step 2: Build context with cached PDF information
        # Always include full context of all available documents
        # This ensures the agent knows what components/documents are available
        pdf_context = self.get_full_pdf_context()

        # Step 3: Create enhanced prompt with PDF context
        enhanced_message = f"{user_message}\n{pdf_context}"

        # Step 4: Get response from Claude with PDF context
        response = self.claude_agent.chat(
            enhanced_message,
            conversation_history,
            system=request.get('system', None)
        )

        if response['success']:
            return {
                'success': True,
                'result': response['result'],
                'metadata': {
                    'used_pdf': True,  # Always true since we always include PDF context
                    'pdf_count': len(self.pdf_content_cache),
                    'cached_docs': len(self.pdf_content_cache),
                    **response.get('metadata', {})
                }
            }
        else:
            return response
