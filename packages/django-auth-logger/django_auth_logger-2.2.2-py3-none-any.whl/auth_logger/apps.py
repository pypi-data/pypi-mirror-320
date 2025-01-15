from django.apps import AppConfig


class AuthLoggerConfig(AppConfig):
    name = "auth_logger"

    def ready(self) -> None:
        from .signals import handlers  # NOQA
