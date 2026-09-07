"""app/ai/validator.py
===================
Anti-Hallucination and Project Evidence Fact Validation Engine.

Validates that generated BRD draft content does not introduce unconfirmed
numeric values, percentages, SLAs, currencies, durations, dates, or factual claims
that are not present in confirmed user/project evidence (C*).
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ValidationResult:
    """Result of anti-hallucination validation on generated BRD content against project evidence."""
    is_safe: bool
    unsupported_claims: tuple[str, ...] = ()
    reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "is_safe": self.is_safe,
            "unsupported_claims": list(self.unsupported_claims),
            "reason": self.reason,
        }

WORD_NUMBERS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19",
    "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50", "sixty": "60",
    "seventy": "70", "eighty": "80", "ninety": "90", "hundred": "100", "thousand": "1000",
    "million": "1000000"
}


def extract_numeric_tokens(text: str) -> list[str]:
    """Extracts numeric values, currencies, percentages, and metrics."""
    # Strip inline citation tags like [R1], [C1], and list bullet prefixes across all lines
    clean = re.sub(r"\[[RCG]\d+\]", "", text)
    clean = re.sub(r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)+", "", clean, flags=re.MULTILINE)
    tokens = re.findall(r"(?:[\$€£¥Rp]\s*)?\b\d+(?:[.,]\d+)?\b%?", clean)
    return [t.strip() for t in tokens if t.strip()]


_QUANTITY_UNIT_PATTERN = r"(?:hours?|days?|weeks?|months?|years?|minutes?|seconds?|%|percent)"


def _extract_quantity_unit_pairs(text: str) -> list[tuple[str, str]]:
    """Extracts (number, unit) pairs for time/percentage quantities (e.g. SLA claims
    like "2 hours" or "99%"). These always require an exact evidence match regardless
    of the benign-small-digit exemption in validate_project_facts — a small number is
    a reasonable unconfirmed retry count/priority, but a small number attached to a
    time/percentage unit is very often an SLA-style claim that can directly contradict
    a different value already stated in evidence (e.g. draft says "2 hours" while the
    user said "1 hour")."""
    return re.findall(rf"\b(\d+(?:[.,]\d+)?)\s*({_QUANTITY_UNIT_PATTERN})\b", text, re.IGNORECASE)


def _normalize_unit(unit: str) -> str:
    unit = unit.lower()
    if unit in ("%", "percent"):
        return "%"
    return unit[:-1] if unit.endswith("s") else unit


def validate_project_facts(
    generated_text: str,
    project_evidence_text: str,
    context_answers: dict[str, str] | None = None,
) -> ValidationResult:
    """
    Validates generated BRD text against confirmed project evidence and prior completed sections.
    Returns a ValidationResult indicating whether the text is safe or contains unconfirmed claims.
    """
    if not generated_text or not generated_text.strip():
        return ValidationResult(is_safe=True, unsupported_claims=(), reason=None)

    # Combine direct evidence with completed cross-section answers
    evidence_parts = [project_evidence_text or ""]
    if context_answers:
        evidence_parts.extend(context_answers.values())
    combined_evidence = " ".join(evidence_parts)

    unsupported: list[str] = []

    # 1a. Time/percentage quantity claims ("2 hours", "99%") always require an exact
    # match in evidence — these are SLA-style claims, not generic small config digits,
    # so the benign-small-digit allowlist below must NOT apply to them (a hallucinated
    # "2 hours" when evidence says "1 hour" must still be flagged even though "2" alone
    # would otherwise be allowlisted).
    flagged_quantity_numbers: set[str] = set()
    gen_quantities = _extract_quantity_unit_pairs(generated_text)
    if gen_quantities:
        evidence_quantities = {
            (number, _normalize_unit(unit)) for number, unit in _extract_quantity_unit_pairs(combined_evidence)
        }
        for number, unit in gen_quantities:
            normalized_unit = _normalize_unit(unit)
            if (number, normalized_unit) not in evidence_quantities:
                unsupported.append(number)
                flagged_quantity_numbers.add(number)

    # 1b. Generic numeric and metric verification (currency, counts, percentages
    # not already covered by the quantity-unit check above).
    gen_numeric = extract_numeric_tokens(generated_text)
    if gen_numeric:
        evidence_numeric = set(extract_numeric_tokens(combined_evidence))
        evidence_digits = set(re.findall(r"\b\d+(?:[.,]\d+)?\b", combined_evidence))

        # Standard technical design digits allowed without strict citation (e.g. 0-5 for retries/priority)
        benign_small_digits = {"0", "1", "2", "3", "4", "5"}

        for token in gen_numeric:
            if token in flagged_quantity_numbers:
                continue
            clean_digit = re.sub(r"[^\d.]", "", token)
            # Allowed if found in evidence or if it's a small standard technical config digit
            if token in evidence_numeric or clean_digit in evidence_digits or token in benign_small_digits:
                continue
            unsupported.append(token)

    # 2. Word-number verification
    clean_gen = re.sub(r"\[[RCG]\d+\]", "", generated_text)
    clean_gen = re.sub(r"^\s*(?:\d+(?:\.\d+)*[.)]?\s*)+", "", clean_gen, flags=re.MULTILINE)

    for word, digit_eq in WORD_NUMBERS.items():
        if re.search(rf"\b{word}\b", clean_gen, re.IGNORECASE):
            # Check if word or digit equivalent is in project evidence / context answers or small number
            if digit_eq in {"0", "1", "2", "3", "4", "5"}:
                continue
            if not re.search(rf"\b{word}\b", combined_evidence, re.IGNORECASE) and not re.search(rf"\b{digit_eq}\b", combined_evidence):
                unsupported.append(word)

    if unsupported:
        unique_unsupported = tuple(sorted(list(set(unsupported))))
        reason = (
            f"Generated draft introduces unconfirmed factual claims/metrics: {', '.join(unique_unsupported)} "
            "not present in user project evidence."
        )
        return ValidationResult(
            is_safe=False,
            unsupported_claims=unique_unsupported,
            reason=reason,
        )

    return ValidationResult(is_safe=True, unsupported_claims=(), reason=None)

