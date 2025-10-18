from typing import Callable, Optional

Classifier = Callable[[dict], Optional[str]]

_issue_update_classifiers: list[Classifier] = []


def register_issue_update_classifier(classifier: Classifier) -> None:
    """
    Registers a classifier that attempts to map an issue-updated payload
    to a more specific event type.
    """
    _issue_update_classifiers.append(classifier)


def classify_issue_update(data: dict) -> Optional[str]:
    """
    Executes registered classifiers in order until one returns a non-None
    event type identifier.
    """
    for classifier in _issue_update_classifiers:
        event_type = classifier(data)
        if event_type:
            return event_type
    return None
