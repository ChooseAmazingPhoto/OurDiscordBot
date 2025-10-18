import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


def parse_jira_datetime(raw_value) -> Optional[datetime]:
    """
    Parses Jira timestamps that may be ISO8601 strings or epoch values (seconds or milliseconds).
    Returns a timezone-aware datetime where possible.
    """
    if raw_value is None:
        return None

    if isinstance(raw_value, (int, float)):
        try:
            epoch = float(raw_value)
            if epoch > 10**11:  # Likely milliseconds
                epoch /= 1000
            return datetime.fromtimestamp(epoch, tz=timezone.utc)
        except (ValueError, OSError) as exc:
            logger.debug("Epoch timestamp conversion failed: %s", exc)
            return None

    if isinstance(raw_value, str):
        candidate = raw_value.strip()
        if not candidate:
            return None

        if candidate.endswith("Z"):
            candidate = candidate[:-1] + "+00:00"
        if (
            len(candidate) > 5
            and candidate[-5] in ("+", "-")
            and candidate[-4:].isdigit()
        ):
            candidate = f"{candidate[:-5]}{candidate[-5:-2]}:{candidate[-2:]}"

        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            base_part = candidate.split(".")[0]
            base_part = base_part.split("+")[0]
            try:
                return datetime.fromisoformat(base_part)
            except ValueError as exc:
                logger.debug("ISO timestamp parsing failed: %s", exc)
                return None

    return None


def build_issue_url(issue: dict) -> Optional[str]:
    """
    Builds a user-facing Jira issue URL from the issue payload.
    """
    issue_self = issue.get("self")
    issue_key = issue.get("key")
    if not issue_self or not issue_key:
        return None

    base_url = issue_self.split("/rest/api")[0]
    return f"{base_url}/browse/{issue_key}"
