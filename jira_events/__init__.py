from .registry import JiraEventRegistry
from .classifiers import classify_issue_update, register_issue_update_classifier

registry = JiraEventRegistry()

from . import (
    assignee_changed,
    comment_created,
    due_date_changed,
    issue_created,
    issue_reopened,
    labels_updated,
    status_transition,
)

issue_created.register(registry)
status_transition.register(registry, register_issue_update_classifier)
assignee_changed.register(registry, register_issue_update_classifier)
due_date_changed.register(registry, register_issue_update_classifier)
issue_reopened.register(registry, register_issue_update_classifier)
labels_updated.register(registry, register_issue_update_classifier)
comment_created.register(registry)

__all__ = [
    "JiraEventRegistry",
    "registry",
    "classify_issue_update",
    "register_issue_update_classifier",
]
