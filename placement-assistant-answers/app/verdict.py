import json
from collections.abc import Callable

from pydantic import BaseModel, Field, ValidationError, model_validator


class FailedRule(BaseModel):
    rule_id: int
    rule: str
    actual: str | float


class EligibilityVerdict(BaseModel):
    student_id: str = Field(pattern=r"^\d{2}[A-Z]{2}\d{3}$")
    drive_id: int
    eligible: bool
    failed_rules: list[FailedRule]
    summary: str = Field(min_length=1, max_length=280)

    @model_validator(mode="after")
    def verdict_matches_rules(self):
        if self.eligible == bool(self.failed_rules):
            raise ValueError("eligible contradicts failed_rules")
        return self


class VerdictInvalid(Exception):
    def __init__(self, attempts: int, last_errors: list):
        super().__init__(f"no valid verdict after {attempts} attempts")
        self.attempts = attempts
        self.last_errors = last_errors


Generate = Callable[[list[str]], str]


def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""
        t = t.rsplit("```", 1)[0]
    return t.strip()


def structured_verdict(generate: Generate, prompt: str, max_retries: int = 2) -> EligibilityVerdict:
    """Ask the model for an EligibilityVerdict; feed validation errors back; give up after max_retries."""
    messages = [prompt]
    errors: list = []
    for attempt in range(1, max_retries + 2):
        raw = generate(list(messages))
        try:
            return EligibilityVerdict.model_validate_json(_strip_fences(raw))
        except ValidationError as e:
            errors = e.errors(include_url=False, include_context=False)
            messages.append(raw)
            messages.append(
                "Your previous reply failed validation:\n"
                + json.dumps(errors, default=str, indent=2)
                + "\nReply again with corrected JSON only."
            )
    raise VerdictInvalid(max_retries + 1, errors)
