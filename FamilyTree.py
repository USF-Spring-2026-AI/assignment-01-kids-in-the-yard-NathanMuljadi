from collections import deque
import random

from numpy import ceil
from PersonFactory import PersonFactory
from Person import Person

class FamilyTree():
    def __init__(self):
        self.factory = PersonFactory()
        print("Reading files...")
        self.factory.read_files()

        self.people = []
        self.queue = deque() # CITE: https://docs.python.org/3/library/collections.html#collections.deque

        self.root_last_names = {"Jones", "Smith"} # descendants of root people will have one of these last names

        self.init_roots()
        print("Generating family tree...")
        self.generate_family_tree()

    '''
    Determines the year a person dies based on their year born and life expectancy for that decade, 
    with some random variation. This is a helper method used in init_roots() and generate_family_tree() 
    to avoid code duplication.
    Returns the year died as an integer
    '''
    def determine_year_died(self, year_born):
        # Convert year_born to decade string, e.g. "1950s"
        decade = f"{(year_born // 10) * 10}s"
        life_expectancy = self.factory.life_expectancy_by_decade[decade]

        # Add random +/- 10 variation
        variation = random.randint(-10, 10)
        year_died = int(year_born + life_expectancy + variation)

        return year_died

    def init_roots(self):
        # Create 2 root people born in the 1950s
        year_died = self.determine_year_died(1950)

        root1 = Person(
            year_born=1950,
            year_died=year_died,
            first_name="Desmond",
            last_name="Jones",
            spouse=None,
            children=[]
        ) # Desmond Jones

        # Call method again for second root to ensure they don't have the same year died
        year_died = self.determine_year_died(1950)
        root2 = Person(
            year_born=1950,
            year_died=year_died,
            first_name="Molly",
            last_name="Smith",
            spouse=None,
            children=[]
        ) # Molly Smith

        root1.spouse = root2
        root2.spouse = root1

        self.people.append(root1)
        self.people.append(root2)

        self.queue.append(root1) # Only add one root to queue to avoid duplication

    '''
    Distributes birth years for children of a parent between a start and end year.
    Return a list of birth years for the children
    CITE: Used chatGPT to find the math equation for distributing birth years evenly between a range
    '''
    def distribute_birth_years(self, start: int, end: int, num_children: int) -> list[int]:
        if num_children <= 0:
            return []
        
        if num_children == 1:
            return [round((start + end) / 2)]
        
        interval = (end - start) / (num_children - 1)
        birth_years = [round(start + i * interval) for i in range(num_children)]
        # Clamp birth years to be within the start and end range in case of out of bounds
        return [min(end, max(start, year)) for year in birth_years]
    
    def total_people(self):
        return len(self.people)
    
    '''
    Prints the total number of people born in each decade, sorted by decade
    '''
    def total_by_decade(self):
        decade_counts = {}
        for person in self.people: # Get count of people born in each decade
            decade = f"{(person.year_born // 10) * 10}s"
            decade_counts[decade] = decade_counts.get(decade, 0) + 1
        
        for decade in sorted(decade_counts.keys()): # Print counts sorted by decade
            print(decade + ": " + str(decade_counts[decade]))

    '''
    Prints all of the duplicate names in the family tree
    '''
    def duplicate_names(self):
        name_counts = {}
        for person in self.people: # Get count of each full name
            full_name = person.first_name + " " + person.last_name
            name_counts[full_name] = name_counts.get(full_name, 0) + 1
        
        # Remove names that are not duplicated
        for name, count in list(name_counts.items()): # CITE: https://www.geeksforgeeks.org/python/python-remove-item-from-dictionary-by-value/
            if count <= 1:
                name_counts.pop(name)

        # Print names that are duplicated
        print("There are " + str(len(name_counts)) + " duplicate names in the tree:")
        for name in name_counts:
            if name_counts[name] > 1:
                print("* " + name)

    def generate_family_tree(self):
        while self.queue:
            current_person = self.queue.popleft()
            decade = f"{(current_person.year_born // 10) * 10}s"

            # Determine if person gets married
            if current_person.spouse is None:
                marriage_rate = self.factory.marriage_rate_by_decade[decade]
                if random.random() < marriage_rate: # CITE: https://docs.python.org/3/library/random.html#random.random
                    spouse_year_born = current_person.year_born + random.randint(-10, 10) # Spouse is born within +/- 10 years of current person
                    spouse = self.factory.get_person(spouse_year_born) # Create person object

                    # Set spouse relationship
                    current_person.spouse = spouse
                    spouse.spouse = current_person

                    self.people.append(spouse)

            # Determine children
            birth_rate = self.factory.birth_rate_by_decade[decade]
            min_children = int(ceil(birth_rate - 1.5))
            max_children = int(ceil(birth_rate + 1.5))

            num_children = random.randint(min_children, max_children)
            
            if num_children == 0:
                continue

            if current_person.spouse is not None:
                parent_year_born = min(current_person.year_born, current_person.spouse.year_born)
            else:
                parent_year_born = current_person.year_born
            
            child_birth_start = parent_year_born + 25
            child_birth_end = parent_year_born + 45

            child_years = self.distribute_birth_years(child_birth_start, child_birth_end, num_children)

            for year in child_years:
                if year > 2120:
                    continue

                child = self.factory.get_person(year)

                # Descendants must be Jones or Smith
                child.last_name = random.choice(list(self.root_last_names))

                current_person.children.append(child)
                if current_person.spouse is not None:
                    current_person.spouse.children.append(child)

                self.people.append(child)
                self.queue.append(child)

    def run(self):
        while True:
            # Prompt user for what they want to see about the family tree
            print("Are you interested in:")
            print("(T)otal number of people in the tree")
            print("Total number of people in the tree by (D)ecade")
            print("(N)ames duplicated")
            print("(Q)uit")

            choice = input().strip().upper()
            if choice == "T":
                print("The tree contains " + str(self.total_people()) + " people total.")
            elif choice == "D":
                self.total_by_decade()
            elif choice == "N":
                self.duplicate_names()
            elif choice == "Q":
                print("Shutting down...")
                break
            else:
                print("Invalid choice, please enter T, D, N, or Q.")


if __name__ == "__main__":
    FamilyTree().run()