from .utils import cut_namespace


class Criteria:
    def __init__(self, name: str, trigger: str):
        """
        Class of the advancement criteria.
        :param name: Name of the criteria.
        :param trigger: trigger of the criteria.
        """
        self._name = name
        self._trigger = cut_namespace(trigger)
        self._is_impossible = None

    @property
    def name(self) -> str:
        """
        :return: name of the criteria
        """
        return self._name

    @property
    def trigger(self) -> str:
        """
        :return: trigger of the criteria
        """
        return self._trigger

    def __repr__(self):
        return f"<Criteria name={self._name}, trigger={self._trigger}"

    def __str__(self):
        return f"<Criteria name={self._name}, trigger={self._trigger}"

    def __eq__(self, other: "Criteria") -> bool:
        if other.__class__ != self.__class__:
            raise TypeError("Element must be an instance of the Criteria class")
        return (self._name == other._name) and (self._trigger == other._trigger)

    def __ne__(self, other: "Criteria") -> bool:
        return not self.__eq__(other)

    @property
    def is_impossible(self):
        """
        :return: True if criteria is impossible, False otherwise
        """
        if self._is_impossible is None:
            self._is_impossible = self._trigger == "impossible"
        return self._is_impossible
