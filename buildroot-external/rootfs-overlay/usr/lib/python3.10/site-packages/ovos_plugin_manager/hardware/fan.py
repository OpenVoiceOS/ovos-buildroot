from abc import abstractmethod


class AbstractFan:
    @abstractmethod
    def set_fan_speed(self, percent: int):
        """
        Set the fan speed to the specified percentage value.
        :param percent: 0-100 fan speed value
        """

    @abstractmethod
    def get_fan_speed(self) -> int:
        """
        Get the current fan speed as a 0-100 percentage value.
        """
        # TODO: Consider an equivalent property for this

    @abstractmethod
    def get_cpu_temp(self) -> float:
        """
        Get the current CPU temp in celsius (-1.0 if not available)
        """
        # TODO: Consider an equivalent property for this
        return -1.0

    @abstractmethod
    def shutdown(self):
        """
        Perform any cleanup and set the fan to a reasonable speed.
        """
