from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional

import discord

EventHandler = Callable[..., Optional[discord.Embed]]


@dataclass
class RegisteredHandler:
    func: EventHandler
    accepts_positional_event_type: bool
    accepts_keyword_event_type: bool
    has_varargs: bool
    has_varkw: bool


class JiraEventRegistry:
    """
    Maintains a mapping between Jira webhook event identifiers and callables
    that can transform payloads into Discord embeds.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, RegisteredHandler] = {}

    @staticmethod
    def _normalize(event_type: str) -> str:
        return event_type.strip().lower()

    def register(self, event_types: Iterable[str], handler: EventHandler) -> None:
        registration = self._analyze_handler(handler)
        for event_type in event_types:
            if not event_type:
                continue
            key = self._normalize(event_type)
            self._handlers[key] = registration

    def get_handler(self, event_type: str) -> Optional[RegisteredHandler]:
        if not event_type:
            return None
        return self._handlers.get(self._normalize(event_type))

    def dispatch(self, event_type: str, data: dict):
        registration = self.get_handler(event_type)
        if registration:
            handler = registration.func
            if registration.accepts_positional_event_type or registration.has_varargs:
                return handler(data, event_type)
            if registration.accepts_keyword_event_type or registration.has_varkw:
                return handler(data, event_type=event_type)
            return handler(data)
        return None

    def known_events(self) -> Iterable[str]:
        return tuple(self._handlers.keys())

    @staticmethod
    def _analyze_handler(handler: EventHandler) -> RegisteredHandler:
        try:
            signature = inspect.signature(handler)
        except (ValueError, TypeError):
            return RegisteredHandler(
                func=handler,
                accepts_positional_event_type=True,
                accepts_keyword_event_type=True,
                has_varargs=True,
                has_varkw=True,
            )

        accepts_positional = False
        accepts_keyword = False
        has_varargs = False
        has_varkw = False

        for index, param in enumerate(signature.parameters.values()):
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                has_varargs = True
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                has_varkw = True
            elif param.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            ):
                if index >= 1:
                    accepts_positional = True
                if param.name == "event_type":
                    accepts_keyword = True
            elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                if param.name == "event_type":
                    accepts_keyword = True

        return RegisteredHandler(
            func=handler,
            accepts_positional_event_type=accepts_positional,
            accepts_keyword_event_type=accepts_keyword,
            has_varargs=has_varargs,
            has_varkw=has_varkw,
        )
