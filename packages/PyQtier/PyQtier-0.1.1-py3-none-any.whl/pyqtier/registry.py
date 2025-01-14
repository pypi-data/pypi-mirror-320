from typing import Callable, Any


class PyQtierWindowsRegistry:
    _widgets = {}
    _templates = {}
    _settings = {}
    _widgets_initialized = {}

    @classmethod
    def register(cls, widget_id: str, template, settings) -> Callable[[Any], Any]:
        def decorator(widget_class):
            cls._widgets[widget_id] = widget_class
            cls._templates[widget_id] = template
            cls._settings[widget_id] = settings
            return widget_class

        return decorator

    @classmethod
    def create_registered_widgets(cls):
        for widget_id in cls._widgets:
            widget = cls._widgets[widget_id]()
            cls._widgets_initialized[widget_id] = widget
            cls._widgets_initialized[widget_id].setup_view(cls._templates[widget_id], cls._settings[widget_id])

    @classmethod
    def get_initialized_widget(cls, widget_id: str) -> Callable[[Any], Any]:
        if widget_id not in cls._widgets_initialized:
            if widget_id not in cls._widgets:
                raise KeyError(f"{widget_id} registered but not initialized")
            raise KeyError(f"{widget_id} did not registered")
        return cls._widgets_initialized[widget_id]
