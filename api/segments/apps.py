from core.apps import BaseAppConfig


class SegmentsConfig(BaseAppConfig):
    default = True
    name = "segments"

    def ready(self) -> None:
        super().ready()

        import segments.tasks  # noqa
