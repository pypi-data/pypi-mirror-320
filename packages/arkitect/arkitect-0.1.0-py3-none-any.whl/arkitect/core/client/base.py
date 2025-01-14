import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from arkitect.telemetry.trace import task
from arkitect.utils.common import Singleton


class Client(Singleton):
    """
    Base class for all clients.
    """

    pass


class ClientPool(Singleton):
    """
    A pool of clients that can be accessed by name.
    """

    _registry: Dict[str, Type[Client]] = {}
    clients: Dict[str, Client] = {}

    def __init__(
        self,
        clients: Dict[str, Tuple[Type[Client], Dict[str, Any]]],
    ) -> None:
        """
        Initialize the client pool with a dictionary of clients.

        :param clients: A dictionary of clients.
        """
        for name, (cls, config) in (clients or dict()).items():
            try:
                self.clients[name] = cls(**config)
            except Exception as e:
                logging.error(f"init client pool failed:{e}")
                continue

    def get_client_names(self) -> List[str]:
        """
        Get the names of all clients in the pool.

        :return: A list of client names.
        """
        return [name for name in self.clients.keys()]

    def get_client(self, name: str) -> Optional[Client]:
        """
        Get a client by name.

        :param name: The name of the client.
        :return: The client instance, or None if the client is not found.
        """
        return self.clients.get(name)

    @classmethod
    def register(
        cls, name: Optional[str] = None
    ) -> Callable[[Type[Client]], Type[Client]]:
        """
        Decorator to register a client class with the client pool.

        :param name: The name to register the class under.
                     If not provided, the class name will be used.
        :return: The decorated class.
        """

        def func(wrapped_cls: Type[Client]) -> Type[Client]:
            if name:
                cls._registry[name] = wrapped_cls
            else:
                cls._registry[wrapped_cls.__name__] = wrapped_cls

            return wrapped_cls

        return func

    @classmethod
    async def async_get_client(cls, name: str, config: Dict[str, Any]) -> Client:
        """
        Asynchronously get a client instance by name.
        If the client does not exist, create it.

        :param name: The name of the client.
        :param config: The configuration for the client.
        :return: The client instance.
        """
        if name not in cls.clients:
            cls.clients[name] = await cls.async_create_client(name, **config)

        return cls.clients[name]

    @classmethod
    async def async_create_client(cls, name: str, *args: Any, **kwargs: Any) -> Client:
        """
        Asynchronously create a client instance by name.

        :param name: The name of the client.
        :return: The client instance.
        """
        if name not in cls._registry:
            raise ValueError(f"Unknown client name: {name}")
        if not issubclass(cls._registry[name], Client):
            raise ValueError(f"{name} is not a subclass of client")
        client_cls = cls._registry[name]

        return await client_cls.get_instance_async(*args, **kwargs)


@task()
def get_client_pool(
    clients: Optional[Dict[str, Tuple[Type[Client], Any]]] = None,
) -> ClientPool:
    """
    Get the client pool instance.

    :param clients: A dictionary of clients.
    :return: The client pool instance.
    """
    return ClientPool.get_instance_sync(clients=clients)
