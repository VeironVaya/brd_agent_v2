from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InvalidChoiceDataError, NotFoundError
from app.repositories import answer_repository, section_repository
from app.services import conversation_service


DIRECTORATE_OPTIONS = (
    "CEO Office",
    "Marketing",
    "Sales",
    "Planning & Transformation (P&T)",
    "Finance & Risk Management",
    "Network",
    "Information Technology (IT)",
    "Human Capital Management (HCM)",
)


CHOICE_SECTIONS = {
    "1.3": {
        "title": "Purpose of this Business Requirement",
        "groups": {
            "selected": {
                "label": "Purpose",
                "options": (
                    "BR to enhance existing service/application/process",
                    "BR to terminate existing service/application/process",
                    "BR for new service/application/process",
                    "BR to replace existing service/application/process",
                    "Others, please specify",
                ),
                "required": True,
                "multiple": True,
            }
        },
    },
    "1.4": {
        "title": "Program Type",
        "groups": {
            "selected": {
                "label": "If IT-led / IT-driven program",
                "options": (
                    "Automation",
                    "Audit compliance",
                    "Business engagement model",
                    "Capacity expansion",
                    "Cloud",
                    "Digital ways of working",
                    "End of life replacement",
                    "End of Support (EoS)",
                    "Infrastructure",
                    "License renewal",
                    "Integration / Modernization",
                    "Security compliance",
                    "Security enhancement",
                    "Others, please specify",
                ),
                "required": True,
                "multiple": True,
            }
        },
    },
    "3.2": {
        "title": "Product / Service Specification",
        "groups": {
            "target_market_segmentation": {
                "label": "Target market segmentation",
                "options": ("HVC", "Non-HVC", "SME", "Corporate", "Governance", "Targeted segment, please specify"),
                "required": True,
                "multiple": True,
            },
            "subscriber_eligibility": {
                "label": "Subscriber eligibility",
                "options": ("Telkomsel customer", "Telkomsel employee", "Others, please specify"),
                "required": True,
                "multiple": True,
            },
            "brand_eligibility": {
                "label": "Brand eligibility",
                "options": ("simPATI", "KartuAS", "Loop", "ByU", "Others"),
                "required": True,
                "multiple": True,
            },
            "channel_eligibility": {
                "label": "Channel eligibility",
                "options": (
                    "Self service channel",
                    "Assisted channel",
                    "UMB, please specify ADN",
                    "SMS, please specify ADN",
                    "Web, please specify",
                    "Walk-in",
                    "Call-in",
                    "Mobile apps, please specify",
                    "3rd party channels, please specify",
                ),
                "required": True,
                "multiple": True,
            },
            "area_coverage": {
                "label": "Area coverage",
                "options": ("National-wide", "Selected area, please specify"),
                "required": True,
                "multiple": False,
            },
            "terms_and_conditions": {
                "label": "Product / Service Terms and Conditions",
                "options": (
                    "Customer restriction / limitation to purchase / register the product",
                    "Eligible time period for customer to purchase / register this product/service",
                    "Product / service compatibility and correlation with other product / service",
                ),
                "required": True,
                "multiple": True,
            },
        },
    },
}


def get_choice_config(section_id: str) -> dict | None:
    return CHOICE_SECTIONS.get(section_id)


def _validate_group(group_id: str, value: dict, config: dict) -> tuple[list[str], str | None]:
    if not isinstance(value, dict):
        raise InvalidChoiceDataError(f"Choice group {group_id!r} must be an object.")
    selected = value.get("selected", [])
    other_text = value.get("other_text")
    if not isinstance(selected, list) or not all(isinstance(item, str) for item in selected):
        raise InvalidChoiceDataError(f"Choice group {group_id!r} must contain a string selected list.")
    if not config["multiple"] and len(selected) > 1:
        raise InvalidChoiceDataError(f"Choice group {group_id!r} allows only one selection.")
    invalid = [item for item in selected if item not in config["options"]]
    if invalid:
        raise InvalidChoiceDataError(f"Unsupported choice in {group_id!r}: {invalid[0]}")
    if config["required"] and not selected:
        raise InvalidChoiceDataError(f"Choice group {group_id!r} requires at least one selection.")
    needs_text = any("specify" in item.lower() or item == "Others" for item in selected)
    if needs_text and (not isinstance(other_text, str) or not other_text.strip()):
        raise InvalidChoiceDataError(f"Choice group {group_id!r} requires Other text.")
    if other_text is not None and not isinstance(other_text, str):
        raise InvalidChoiceDataError(f"Other text for {group_id!r} must be a string.")
    return selected, other_text.strip() if isinstance(other_text, str) else None


def validate_choice_data(section_id: str, choice_data: dict) -> dict:
    config = get_choice_config(section_id)
    if config is None:
        raise InvalidChoiceDataError(f"Section {section_id!r} is not a choice section.")
    if not isinstance(choice_data, dict):
        raise InvalidChoiceDataError("choice_data must be an object.")
    groups = config["groups"]
    if set(choice_data) != set(groups):
        raise InvalidChoiceDataError("choice_data contains unexpected or missing groups.")
    validated = {}
    for group_id, group_config in groups.items():
        selected, other_text = _validate_group(group_id, choice_data[group_id], group_config)
        validated[group_id] = {"selected": selected, "other_text": other_text}
    return validated


def build_answer_text(section_id: str, choice_data: dict) -> str:
    config = CHOICE_SECTIONS[section_id]
    lines = []
    for group_id, group_config in config["groups"].items():
        value = choice_data[group_id]
        selections = list(value["selected"])
        if value["other_text"]:
            selections.append(value["other_text"])
        lines.append(f"{group_config['label']}: " + "; ".join(selections))
    return "\n".join(lines)


async def save_choices(
    session: AsyncSession, *, conversation_id: str, user_id: str, section_id: str, choice_data: dict
) -> dict:
    await conversation_service.get_accessible(session, conversation_id, user_id, min_role="editor")
    config = get_choice_config(section_id)
    if config is None:
        raise InvalidChoiceDataError(f"Section {section_id!r} is not a choice section.")
    sections = await section_repository.list_by_conversation(session, conversation_id)
    section = next((item for item in sections if item.template_key == section_id), None)
    if section is None:
        raise NotFoundError(f"Section {section_id!r} not found.")
    validated = validate_choice_data(section_id, choice_data)
    answer = await answer_repository.upsert(
        session,
        section.section_id,
        status="done",
        completeness=100,
        confidence=100,
        answer_text=build_answer_text(section_id, validated),
        missing_items=[],
        choice_data=validated,
    )
    return {
        "status": answer.status,
        "completeness": answer.completeness,
        "confidence": answer.confidence,
        "answer": answer.answer_text,
        "missing": answer.missing_items,
        "choice_data": answer.choice_data,
    }