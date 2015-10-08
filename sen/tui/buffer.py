import logging
from sen.docker_backend import DockerContainer
from sen.tui.constants import HELP_TEXT
from sen.tui.widget import AsyncScrollableListBox, MainListBox, ScrollableListBox

logger = logging.getLogger(__name__)


class Buffer:
    """
    base buffer class
    """
    display_name = None  # display in status bar
    widget = None  # display this in main frame

    def __init__(self):
        logger.debug("creating buffer %r", self)

    def __repr__(self):
        return "{}(name={!r}, widget={!r})".format(
            self.__class__.__name__, self.display_name, self.widget)

    def destroy(self):
        destroy_method = getattr(self.widget, "destroy", None)
        if destroy_method:
            destroy_method()


class MainListBuffer(Buffer):
    display_name = "Listing"

    def __init__(self, docker_backend, ui):
        self.widget = MainListBox(docker_backend, ui)
        super().__init__()
        self.refresh()

    def refresh(self):
        self.widget.populate()


class LogsBuffer(Buffer):
    def __init__(self, docker_object, ui, follow=False):
        """

        :param docker_object: container to display logs
        :param ui: ui object so we refresh
        """
        self.display_name = "[{}] {}".format("F" if follow else "L", docker_object.short_name)
        if isinstance(docker_object, DockerContainer):
            if follow:
                logs_generator = docker_object.logs(follow=follow)
                self.widget = AsyncScrollableListBox(logs_generator, ui)
            else:
                logs_data = docker_object.logs(follow=follow)
                self.widget = ScrollableListBox(logs_data)
        else:
            raise Exception("Only containers have logs.")
        super().__init__()


class InspectBuffer(Buffer):
    def __init__(self, docker_object):
        """

        :param docker_object: object to inspect
        """
        inspect_data = docker_object.display_inspect()
        self.widget = ScrollableListBox(inspect_data)
        self.display_name = "{} inspect".format(docker_object.short_name)
        super().__init__()


class HelpBuffer(Buffer):
    def __init__(self):
        """
        """
        self.widget = ScrollableListBox(HELP_TEXT)
        self.display_name = "[H]"
        super().__init__()