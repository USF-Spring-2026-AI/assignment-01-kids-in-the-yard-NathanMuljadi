import csv
from collections import defaultdict
import random
from Person import Person

class PersonFactory():
    def get_person(self, year_born):
        # Determine decade based on year_born
        year_born = self.clamp_year_to_data(year_born)
        decade = f"{(year_born // 10) * 10}s"

        # Choose first name (weighted)
        first_name = self.weighted_choice(
            self.first_name_by_decade[decade]
        )

        # Choose last name (weighted)
        last_name = self.weighted_choice(
            self.last_name_by_decade[decade]
        )

        # Determine year died
        life_expectancy = self.life_expectancy_by_decade[decade]

        # Add random +/- 10 variation
        variation = random.randint(-10, 10)
        year_died = int(year_born + life_expectancy + variation)

        # Create and return Person object
        person = Person(
            year_born=year_born,
            year_died=year_died,
            first_name=first_name,
            last_name=last_name,
            spouse=None,
            children=[]
        )
        return person

    def read_files(self):
        # Initialize data structures
        self.first_name_by_decade = defaultdict(list) # Searched on chatGPT to find a
        self.last_name_by_decade = defaultdict(list)  # dictionary that has list as default value
        self.life_expectancy_by_decade = {}
        self.probability_by_rank = {}
        self.birth_rate_by_decade = {}
        self.marriage_rate_by_decade = {}

        # Read data from first_names.csv
        with open('first_names.csv', 'r') as file: # CITE: https://stackoverflow.com/questions/3277503/how-to-read-a-file-line-by-line-into-a-list
            fileReader = csv.DictReader(file) # CITE: https://stackoverflow.com/questions/52400408/import-csv-file-into-python
            for row in fileReader:
                decade = row["decade"]
                name = row["name"]
                frequency = float(row["frequency"])
                # Store as a tuple of (name, frequency) in the list for the corresponding decade
                self.first_name_by_decade[decade].append((name, frequency))

        # Read data from rank_to_probability.csv
        with open('rank_to_probability.csv', 'r') as file:
            line = file.readline().strip().split(",")
            for i in range(len(line)):
                self.probability_by_rank[i + 1] = float(line[i])
        
        # Read data from last_names.csv
        with open('last_names.csv', 'r') as file:
            fileReader = csv.DictReader(file) # CITE: https://docs.python.org/3/library/csv.html
            for row in fileReader:
                decade = row["Decade"]
                rank = int(row["Rank"])
                last_name = row["LastName"]
                weight = self.probability_by_rank.get(rank, 0.0)
                self.last_name_by_decade[decade].append((last_name, weight))

        # Read data from life_expectancy.csv
        decade_totals = defaultdict(list)
        with open('life_expectancy.csv', 'r') as file:
            fileReader = csv.DictReader(file)
            for row in fileReader:
                year = int(row["Year"])
                expectancy = float(row["Period life expectancy at birth"])

                decade = f"{(year // 10) * 10}s" # CITE: chatGPT to find a way to convert year to decade string
                decade_totals[decade].append(expectancy)
        
        for decade, values in decade_totals.items():
            self.life_expectancy_by_decade[decade] = sum(values) / len(values) # Get average life expectancy for each decade
        

        # Read data from birth_and_marriage_rates.csv
        with open('birth_and_marriage_rates.csv', 'r') as file:
            fileReader = csv.DictReader(file)
            for row in fileReader:
                decade = row["decade"]
                self.birth_rate_by_decade[decade] = float(row["birth_rate"])
                self.marriage_rate_by_decade[decade] = float(row["marriage_rate"])
    
    """
    choices is a list of (name, weight) tuples
    returns one name based on weight
    """
    def weighted_choice(self, choices):
        names = [name for name, weight in choices] # CITE: https://stackoverflow.com/questions/3679694/a-weighted-version-of-random-choice
        weights = [weight for name, weight in choices]
        return random.choices(names, weights=weights, k=1)[0] # CITE: https://docs.python.org/3/library/random.html#random.choices
    
    '''
    Clamps a year to be within the range of years in the data to avoid out of bounds errors
    '''
    def clamp_year_to_data(self, year: int) -> int:
        if year < 1950:
            return 1950
        if year > 2129:
            return 2129
        return year