from abc import abstractmethod


class AbstractSwitches:
    @property
    @abstractmethod
    def capabilities(self) -> dict:
        """
        Return a dict of capabilities this object supports
        """

    @abstractmethod
    def on_action(self):
        """
        Override to do something when the `action` button is pressed.
        """
        pass

    @abstractmethod
    def on_vol_up(self):
        """
        Override to do something when the `volume up` button is pressed.
        """
        pass

    @abstractmethod
    def on_vol_down(self):
        """
        Override to do something when the `volume down` button is pressed.
        """
        pass

    @abstractmethod
    def on_mute(self):
        """
        Override to do something when `mute` switch is activated.
        """
        pass

    @abstractmethod
    def on_unmute(self):
        """
        Override to do something when `mute` switch is deactivated.
        """
        pass

    @abstractmethod
    def shutdown(self):
        """
        Perform any cleanup.
        """

    def get_capabilities(self) -> dict:
        """
        Backwards-compatible method to return `self.capabilities`
        """
        return self.capabilities
