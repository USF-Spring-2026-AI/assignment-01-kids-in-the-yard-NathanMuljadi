"""
FamilyTree is the main driver for the family tree simulation.
Maintains all Person instances and provides query/reporting capabilities.
"""

import math
import random
from collections import Counter

from person_ai import Person
from person_factory_ai import PersonFactory


class FamilyTree:
    """
    Orchestrates family tree generation and user queries.
    Holds references to the founding pair and all descendants.
    """

    FOUNDER_NAMES = ("Desmond Jones", "Molly Smith")
    FOUNDER_LAST_NAMES = ("Jones", "Smith")
    CUTOFF_YEAR = 2120

    def __init__(self):
        self._factory = PersonFactory()
        self._registry = []  # All Person instances
        self._founder_one = None
        self._founder_two = None

    def bootstrap(self) -> None:
        """Load data files and generate the full family tree."""
        print("Reading files...")
        self._factory.read_files()
        self._create_founders()
        print("Generating family tree...")
        self._expand_tree()

    def _create_founders(self) -> None:
        """Create the two founding people born in 1950."""
        decade = "1950s"
        expectancy = self._factory.get_life_expectancy(decade)

        p1 = Person(
            year_born=1950,
            year_died=1950 + int(expectancy + random.randint(-10, 10)),
            first_name="Desmond",
            last_name="Jones",
        )
        p2 = Person(
            year_born=1950,
            year_died=1950 + int(expectancy + random.randint(-10, 10)),
            first_name="Molly",
            last_name="Smith",
        )
        p1.spouse = p2
        p2.spouse = p1

        self._founder_one = p1
        self._founder_two = p2
        self._registry.extend([p1, p2])

    def _expand_tree(self) -> None:
        """Generate descendants using breadth-first traversal."""
        # Use list as FIFO queue; Ref: list.pop(0) for BFS
        # https://docs.python.org/3/tutorial/datastructures.html
        frontier = [self._founder_one]

        while frontier:
            person = frontier.pop(0)
            decade = person.decade_born()

            # Possibly create a spouse
            if person.spouse is None:
                marriage_rate = self._factory.get_marriage_rate(decade)
                if random.random() < marriage_rate:
                    spouse_year = person.year_born + random.randint(-10, 10)
                    spouse = self._factory.get_person(spouse_year)
                    person.spouse = spouse
                    spouse.spouse = person
                    self._registry.append(spouse)

            # Determine number of children
            birth_rate = self._factory.get_birth_rate(decade)
            min_children = max(0, math.ceil(birth_rate - 1.5))
            max_children = math.ceil(birth_rate + 1.5)
            num_children = random.randint(min_children, max_children)

            if num_children == 0:
                continue

            elder_year = (
                min(person.year_born, person.spouse.year_born)
                if person.spouse
                else person.year_born
            )
            start_year = elder_year + 25
            end_year = elder_year + 45

            birth_years = self._spread_birth_years(start_year, end_year,
                                                   num_children)

            for birth_year in birth_years:
                if birth_year > self.CUTOFF_YEAR:
                    continue
                child = self._factory.get_person(
                    birth_year,
                    override_last_name=random.choice(self.FOUNDER_LAST_NAMES),
                )
                person.children.append(child)
                if person.spouse:
                    person.spouse.children.append(child)
                self._registry.append(child)
                frontier.append(child)

    def _spread_birth_years(self, start: int, end: int,
                            count: int) -> list:
        """
        Distribute count birth years evenly between start and end.
        Uses linear interpolation.
        """
        if count <= 0:
            return []
        if count == 1:
            return [round((start + end) / 2)]
        step = (end - start) / (count - 1)
        return [
            min(end, max(start, round(start + i * step)))
            for i in range(count)
        ]

    def total_count(self) -> int:
        """Return the total number of people in the tree."""
        return len(self._registry)

    def count_by_decade(self) -> None:
        """Print counts of people born per decade, sorted by decade."""
        # Ref: Counter - https://docs.python.org/3/library/collections.html
        decades = [p.decade_born() for p in self._registry]
        counts = Counter(decades)
        for decade in sorted(counts.keys(), key=lambda d: int(d[:-1])):
            print(f"{decade}: {counts[decade]}")

    def list_duplicate_names(self) -> None:
        """Print full names that appear more than once in the tree."""
        names = [p.full_name() for p in self._registry]
        counts = Counter(names)
        duplicates = [name for name, cnt in counts.items() if cnt > 1]
        print(f"There are {len(duplicates)} duplicate names in the tree:")
        for name in sorted(duplicates):
            print(f"* {name}")

    def run(self) -> None:
        """Main loop: present menu and handle user choices."""
        while True:
            print("Are you interested in:")
            print("(T)otal number of people in the tree")
            print("Total number of people in the tree by (D)ecade")
            print("(N)ames duplicated")
            print("(Q)uit")
            print("> ", end="")

            try:
                choice = input().strip().upper()
            except EOFError:
                break

            if choice == "T":
                print(f"The tree contains {self.total_count()} people total")
            elif choice == "D":
                self.count_by_decade()
            elif choice == "N":
                self.list_duplicate_names()
            elif choice == "Q":
                print("Shutting down...")
                break
            else:
                print("Invalid choice, please enter T, D, N, or Q.")


def main() -> None:
    tree = FamilyTree()
    tree.bootstrap()
    tree.run()


if __name__ == "__main__":
    main()
