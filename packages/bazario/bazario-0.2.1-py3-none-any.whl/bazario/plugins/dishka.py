__all__ = (
    "DishkaHandlerResolver",
    "DishkaNotificationHandlerFinder",
    "DishkaRequestHandlerFinder",
)

from collections.abc import Iterable

from dishka import Container, WithParents

from bazario import (
    Dispatcher,
    HandlerResolver,
    Notification,
    NotificationHandler,
    NotificationHandlerFinder,
    Request,
    RequestHandler,
    RequestHandlerFinder,
    THandler,
)
from bazario.type_inspection import (
    extract_base_generic_type,
    matches_generic_type,
)


class DishkaHandlerResolver(HandlerResolver):
    def __init__(self, container: Container) -> None:
        self._container = container

    def resolve(self, handler_type: type[THandler]) -> THandler:
        return self._container.get(handler_type)


class DishkaRequestHandlerFinder(RequestHandlerFinder):
    def __init__(self, container: Container) -> None:
        self._container = container

    def find(self, request: type[Request]) -> type[RequestHandler] | None:
        for key in self._container.registry.factories:
            generic_type = extract_base_generic_type(key.type_hint)

            if generic_type and matches_generic_type(
                generic_type,
                RequestHandler,
                request,
            ):
                return key.type_hint

        return None


class DishkaNotificationHandlerFinder(NotificationHandlerFinder):
    def __init__(self, container: Container) -> None:
        self._container = container

    def find(
        self,
        notification: type[Notification],
    ) -> Iterable[type[NotificationHandler]]:
        for key in self._container.registry.factories:
            generic_type = extract_base_generic_type(key.type_hint)

            if generic_type and matches_generic_type(
                generic_type,
                NotificationHandler,
                notification,
            ):
                yield key.type_hint


def dispatcher_factory(
    handler_resolver: DishkaHandlerResolver,
    request_handler_finder: DishkaRequestHandlerFinder,
    notification_handler_finder: DishkaNotificationHandlerFinder,
) -> WithParents[Dispatcher]:
    return Dispatcher(
        handler_resolver,
        request_handler_finder,
        notification_handler_finder,
    )
