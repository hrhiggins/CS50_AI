import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Create empty frontier and explored lists
    frontier = []
    explored = []
    seen_people = [source]

    # Add source to frontier
    # Create a member for the source (movie_id 1)
    source_member = [1, source]
    # Create a None parent for source
    source_parent = None
    # Create source node
    source_node = [source_member, source_parent]
    frontier.append(source_node)

    ticker = 0

    while True:
        if ticker == 1000:
            print("tick", len(frontier), len(explored))
            ticker = 0
        # If nothing left in frontier then no path
        if len(frontier) == 0:
            return None
        # First in first out (breadth first search requires to start at beginning of list)
        node = frontier[0]
        member = node[0]
        person = member[1]
        parent = node[1]

        # Remove member from frontier and add to explored list
        frontier.remove(node)
        explored.append(node)

        # Check if the member is the target
        # If it is the goal then I need to back track to find the path to the goal
        if person == target:
            path = []
            while parent is not None:
                path.insert(0, member)
                for node in explored:
                    mem = node[0]
                    par = node[1]
                    if mem == parent:
                        member = mem
                        parent = par
                        break
                    else:
                        continue

            return path

        # Otherwise find all the neighbors and add to frontier
        else:
            neighbors = neighbors_for_person(person)
            for neighbor in neighbors:
                new_person = neighbor[1]
                if new_person in seen_people:
                    continue
                else:
                    node = [neighbor, member]
                    seen_people.append(new_person)
                    if new_person == target:
                        frontier.insert(0, node)
                    else:
                        frontier.append(node)

        ticker = ticker + 1
    # TODO
    #raise NotImplementedError


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
