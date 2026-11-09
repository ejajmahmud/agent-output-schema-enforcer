"""Core Agent Output Schema Enforcer implementation."""
import json
import re
from typing import Dict, List, Optional, Tuple, Any


class ParseResult:
    def __init__(self, success: bool, data: Any, was_repaired: bool, error: str = ""):
        self.success = success
        self.data = data
        self.was_repaired = was_repaired
        self.error = error


class OutputSchemaEnforcer:
    def clean_markdown_fences(self, text: str) -> str:
        t = text.strip()
        # Remove ```json ... ```
        if t.startswith("```"):
            lines = t.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            t = "\n".join(lines).strip()
        return t

    def repair_json_string(self, text: str) -> str:
        s = self.clean_markdown_fences(text)

        # Remove trailing commas before closing braces/brackets
        s = re.sub(r",\s*([\}\]])", r"\1", s)

        # Count unbalanced brackets
        open_curly = 0
        open_square = 0
        in_string = False
        escape = False

        for char in s:
            if char == '"' and not escape:
                in_string = not in_string
            elif not in_string:
                if char == '{':
                    open_curly += 1
                elif char == '}':
                    open_curly = max(0, open_curly - 1)
                elif char == '[':
                    open_square += 1
                elif char == ']':
                    open_square = max(0, open_square - 1)

            if char == '\\' and not escape:
                escape = True
            else:
                escape = False

        # Close unclosed quotes and brackets
        if in_string:
            s += '"'
        s += "]" * open_square
        s += "}" * open_curly
        return s

    def enforce_json(self, raw_llm_text: str, required_fields: Optional[List[str]] = None) -> ParseResult:
        cleaned = self.clean_markdown_fences(raw_llm_text)
        try:
            data = json.loads(cleaned)
            self._verify_required(data, required_fields)
            return ParseResult(True, data, False)
        except Exception:
            pass

        # Try repairing
        repaired = self.repair_json_string(raw_llm_text)
        try:
            data = json.loads(repaired)
            self._verify_required(data, required_fields)
            return ParseResult(True, data, True)
        except Exception as e:
            return ParseResult(False, None, True, f"Failed to parse repaired JSON: {e}")

    def _verify_required(self, data: Any, fields: Optional[List[str]]):
        if fields and isinstance(data, dict):
            for f in fields:
                if f not in data:
                    raise ValueError(f"Missing required field: '{f}'")
