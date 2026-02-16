"""
PersonFactory handles reading data files and creating Person instances.
Uses weighted random selection based on census/probability data.
"""

import csv
import math
import random

from person_ai import Person


class PersonFactory:
    """
    Loads demographic data from CSV files and generates Person objects
    with attributes determined by probabilistic rules.
    """

    def __init__(self):
        self._first_names = {}   # {(decade, gender): [(name, weight), ...]}
        self._last_names = {}    # {decade: [(name, weight), ...]}
        self._life_expectancy = {}  # {decade: float}
        self._birth_rates = {}   # {decade: float}
        self._marriage_rates = {}  # {decade: float}
        self._year_min = 1950
        self._year_max = 2129

    def read_files(self) -> None:
        """Load all required CSV data files into memory."""
        self._load_first_names()
        self._load_last_names()
        self._load_life_expectancy()
        self._load_birth_and_marriage_rates()

    def _load_first_names(self) -> None:
        """Load first names with frequency weights by decade and gender."""
        # Ref: csv.DictReader - https://docs.python.org/3/library/csv.html
        with open("first_names.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["decade"], row["gender"])
                if key not in self._first_names:
                    self._first_names[key] = []
                self._first_names[key].append(
                    (row["name"], float(row["frequency"]))
                )

    def _load_last_names(self) -> None:
        """Load last names with rank-based probabilities."""
        rank_probs = self._parse_rank_probabilities()
        with open("last_names.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                decade = row["Decade"]
                rank = int(row["Rank"])
                name = row["LastName"]
                weight = rank_probs.get(rank, 0.0)
                if decade not in self._last_names:
                    self._last_names[decade] = []
                self._last_names[decade].append((name, weight))

    def _parse_rank_probabilities(self) -> dict:
        """Parse rank_to_probability.csv; returns {rank: probability}."""
        result = {}
        with open("rank_to_probability.csv", newline="", encoding="utf-8") as f:
            line = f.readline().strip()
            for idx, val in enumerate(line.split(",")):
                result[idx + 1] = float(val)
        return result

    def _load_life_expectancy(self) -> None:
        """Compute average life expectancy per decade from yearly data."""
        # Ref: defaultdict - https://docs.python.org/3/library/collections.html
        from collections import defaultdict
        by_decade = defaultdict(list)
        with open("life_expectancy.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                year = int(row["Year"])
                decade = f"{(year // 10) * 10}s"
                by_decade[decade].append(
                    float(row["Period life expectancy at birth"]))
        for decade, values in by_decade.items():
            self._life_expectancy[decade] = sum(values) / len(values)

    def _load_birth_and_marriage_rates(self) -> None:
        """Load birth and marriage rates per decade."""
        with open("birth_and_marriage_rates.csv", newline="",
                  encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                decade = row["decade"]
                self._birth_rates[decade] = float(row["birth_rate"])
                self._marriage_rates[decade] = float(row["marriage_rate"])

    def get_person(self, year_born: int, override_last_name: str = None) -> Person:
        """
        Create a new Person with attributes derived from year_born.
        If override_last_name is set, use it instead of selecting from data.
        """
        year_born = self._clamp_year(year_born)
        decade = f"{(year_born // 10) * 10}s"

        gender = random.choice(["male", "female"])
        first_name = self._weighted_pick(
            self._first_names.get((decade, gender), [("Unknown", 1.0)]))

        if override_last_name is not None:
            last_name = override_last_name
        else:
            last_name = self._weighted_pick(
                self._last_names.get(decade, [("Unknown", 1.0)]))

        expectancy = self._life_expectancy.get(decade, 80.0)
        year_died = int(year_born + expectancy + random.randint(-10, 10))

        return Person(
            year_born=year_born,
            year_died=year_died,
            first_name=first_name,
            last_name=last_name,
        )

    def _weighted_pick(self, choices: list) -> str:
        """Select one item from [(item, weight), ...] using weights."""
        if not choices:
            return "Unknown"
        names, weights = zip(*choices)
        return random.choices(names, weights=weights, k=1)[0]

    def _clamp_year(self, year: int) -> int:
        """Clamp year to valid data range."""
        return max(self._year_min, min(self._year_max, year))

    def get_birth_rate(self, decade: str) -> float:
        return self._birth_rates.get(decade, 2.0)

    def get_marriage_rate(self, decade: str) -> float:
        return self._marriage_rates.get(decade, 0.5)

    def get_life_expectancy(self, decade: str) -> float:
        return self._life_expectancy.get(decade, 80.0)
