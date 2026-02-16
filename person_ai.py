"""
Person model for the family tree simulation.
Each member of the family tree is an instance of this class.
"""


class Person:
    """
    Represents a single person in the family tree.
    Encapsulates birth/death years, name, spouse, and children.
    """

    def __init__(self, year_born: int, year_died: int,
                 first_name: str, last_name: str):
        self._year_born = year_born
        self._year_died = year_died
        self._first_name = first_name
        self._last_name = last_name
        self._spouse = None
        self._children = []

    # --- Accessors ---
    @property
    def year_born(self) -> int:
        return self._year_born

    @property
    def year_died(self) -> int:
        return self._year_died

    @property
    def first_name(self) -> str:
        return self._first_name

    @property
    def last_name(self) -> str:
        return self._last_name

    @property
    def spouse(self):
        return self._spouse

    @property
    def children(self):
        return self._children

    # --- Mutators ---
    @year_born.setter
    def year_born(self, value: int) -> None:
        self._year_born = value

    @year_died.setter
    def year_died(self, value: int) -> None:
        self._year_died = value

    @first_name.setter
    def first_name(self, value: str) -> None:
        self._first_name = value

    @last_name.setter
    def last_name(self, value: str) -> None:
        self._last_name = value

    @spouse.setter
    def spouse(self, value) -> None:
        self._spouse = value

    def add_child(self, child: "Person") -> None:
        """Append a child to this person's children list."""
        self._children.append(child)

    def full_name(self) -> str:
        """Return first and last name as a single string."""
        return f"{self._first_name} {self._last_name}"

    def decade_born(self) -> str:
        """Return the decade string for year born (e.g., '1950s')."""
        return f"{(self._year_born // 10) * 10}s"
