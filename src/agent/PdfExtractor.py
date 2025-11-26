import anthropic
import base64
from pathlib import Path
import json
from model import ExtractionResult

class ClaudePDFAgent:
    """Agent that uses Claude to extract and analyze PDF content."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic()
        self.model = model

    def _load_pdf_as_base64(self, pdf_path: str | Path) -> str:
        """Load PDF file and encode as base64."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        with open(pdf_path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")

    def _call_claude(
        self,
        pdf_base64: str,
        prompt: str,
        system: str | None = None,
    ) -> ExtractionResult:
        """Send PDF to Claude with a prompt."""
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system or "You are a precise data extraction assistant.",
            messages=messages,
        )

        raw_text = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens

        # Try to parse JSON if present
        structured = None
        try:
            # Look for JSON in the response
            if "```json" in raw_text:
                json_str = raw_text.split("```json")[1].split("```")[0]
                structured = json.loads(json_str.strip())
            elif raw_text.strip().startswith("{"):
                structured = json.loads(raw_text.strip())
        except json.JSONDecodeError:
            pass

        return ExtractionResult(
            raw_response=raw_text,
            structured_data=structured,
            tokens_used=tokens,
        )

    def extract_text(self, pdf_path: str | Path) -> str:
        """Extract all text content from the PDF."""
        pdf_base64 = self._load_pdf_as_base64(pdf_path)
        result = self._call_claude(
            pdf_base64,
            "Extract all text content from this PDF. Preserve the structure "
            "and formatting as much as possible. Return only the extracted text.",
        )
        return result.raw_response

    def extract_structured(
        self,
        pdf_path: str | Path,
        schema: dict[str, Any],
    ) -> dict | None:
        """Extract data according to a provided schema."""
        pdf_base64 = self._load_pdf_as_base64(pdf_path)
        schema_str = json.dumps(schema, indent=2)

        result = self._call_claude(
            pdf_base64,
            f"""Extract data from this PDF according to this schema:

```json
{schema_str}
```

Return ONLY valid JSON matching this schema. No other text.""",
            system="You extract structured data from documents. Always respond with valid JSON only.",
        )
        return result.structured_data

    def extract_tables(self, pdf_path: str | Path) -> list[dict]:
        """Extract all tables from the PDF."""
        pdf_base64 = self._load_pdf_as_base64(pdf_path)
        result = self._call_claude(
            pdf_base64,
            """Find and extract ALL tables in this PDF.

For each table, return:
- table_number: sequential number
- title: table title or description if visible
- headers: list of column headers
- rows: list of rows, each row is a list of cell values

Return as JSON:
```json
{"tables": [...]}
```""",
        )
        if result.structured_data:
            return result.structured_data.get("tables", [])
        return []

    def summarize(self, pdf_path: str | Path) -> str:
        """Generate an intelligent summary of the PDF."""
        pdf_base64 = self._load_pdf_as_base64(pdf_path)
        result = self._call_claude(
            pdf_base64,
            "Provide a comprehensive summary of this document. Include: "
            "main topics, key points, important data, and any conclusions.",
        )
        return result.raw_response

    def answer_question(self, pdf_path: str | Path, question: str) -> str:
        """Answer a specific question about the PDF content."""
        pdf_base64 = self._load_pdf_as_base64(pdf_path)
        result = self._call_claude(
            pdf_base64,
            f"Based on this document, answer the following question:\n\n{question}",
        )
        return result.raw_response

    def extract_entities(self, pdf_path: str | Path) -> dict:
        """Extract named entities (people, organizations, dates, etc.)."""
        pdf_base64 = self._load_pdf_as_base64(pdf_path)
        result = self._call_claude(
            pdf_base64,
            """Extract all named entities from this document.

Return as JSON:
```json
{
  "people": ["name1", "name2"],
  "organizations": ["org1", "org2"],
  "dates": ["date1", "date2"],
  "locations": ["place1", "place2"],
  "monetary_values": ["$100", "€50"],
  "emails": ["email@example.com"],
  "phone_numbers": ["+1-234-567-8900"],
  "urls": ["https://example.com"]
}
```""",
        )
        return result.structured_data or {}

    def extract_invoice(self, pdf_path: str | Path) -> dict | None:
        """Specialized extraction for invoice documents."""
        schema = {
            "invoice_number": "string",
            "date": "string",
            "due_date": "string",
            "vendor": {
                "name": "string",
                "address": "string",
                "email": "string",
            },
            "customer": {
                "name": "string",
                "address": "string",
            },
            "line_items": [
                {
                    "description": "string",
                    "quantity": "number",
                    "unit_price": "number",
                    "total": "number",
                }
            ],
            "subtotal": "number",
            "tax": "number",
            "total": "number",
            "currency": "string",
        }
        return self.extract_structured(pdf_path, schema)

    def extract_resume(self, pdf_path: str | Path) -> dict | None:
        """Specialized extraction for resume/CV documents."""
        schema = {
            "name": "string",
            "email": "string",
            "phone": "string",
            "location": "string",
            "summary": "string",
            "experience": [
                {
                    "company": "string",
                    "title": "string",
                    "start_date": "string",
                    "end_date": "string",
                    "description": "string",
                }
            ],
            "education": [
                {
                    "institution": "string",
                    "degree": "string",
                    "field": "string",
                    "graduation_date": "string",
                }
            ],
            "skills": ["string"],
        }
        return self.extract_structured(pdf_path, schema)

    def custom_extraction(
        self,
        pdf_path: str | Path,
        instructions: str,
        output_format: str = "text",
    ) -> ExtractionResult:
        """Run a custom extraction with your own instructions."""
        pdf_base64 = self._load_pdf_as_base64(pdf_path)

        if output_format == "json":
            instructions += "\n\nReturn your response as valid JSON only."

        return self._call_claude(pdf_base64, instructions)


