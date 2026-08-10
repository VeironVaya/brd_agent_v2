"""Opaque id generation — never derived from user-editable text.

See ../../brainstorming/api_contract.md §0: application-data ids are
random/opaque, not slugified titles. UUID4 is the simple, defensible
default named there.
"""

import uuid


def new_id() -> str:
    return str(uuid.uuid4())
