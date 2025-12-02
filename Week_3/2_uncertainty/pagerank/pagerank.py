import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # Establish initial variables
    # Number of pages linked to the specified one is the number of items in the value of the relevant corpus key
    number_pages_linked = len(corpus[page])
    # Number of total pages is number of items in corpus
    number_pages = len(corpus)
    linked_pages = corpus[page]
    # Initialise a dict in which to place relevant probabilities
    probability_dict = {}

    # If number of pages in corpus is 0 then raise error
    if number_pages == 0:
        raise ValueError("No pages in corpus")

    # Different probabilities based on if a page is linked to the current one or not
    if number_pages_linked > 0:
        probability_linked = damping_factor / number_pages_linked
        probability_not_linked = (1 - damping_factor) / number_pages
    # If the number of linked pages is 0 then a uniform probability of 1 divided by the number of pages
    elif number_pages_linked == 0:
        probability = 1/number_pages
        # Iterate through the keys and assign the calculated probability
        for key in corpus:
            probability_dict[key] = probability
        # Return the dict with all keys and probabilities (when no linked pages)
        return probability_dict

    # Iterate through keys and assign correct calculated probability
    for key in corpus:
        # If the page is linked to the current one then give it the correct probability
        if key in linked_pages:
            probability_dict[key] = probability_linked
        # If the page is not linked to the current one then give it a different probability
        else:
            probability_dict[key] = probability_not_linked

    # Return the proability dict
    return probability_dict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Create a list of all pages
    list_of_pages = list(corpus.keys())
    # Randomly select a page to start on
    current_page = random.choice(list_of_pages)

    # Intialise a dict for all the visited pages
    visited_pages = {}
    # For each page in the list of all pages, add it to the dict
    # With a value of 0
    # (the value representing the number of time the page was visited in the sample)
    for p in list_of_pages:
        visited_pages.update({p : 0})

    # Initialise count of the number of pages visited
    nr_pages_visited = 0

    # Perform action n times (n being the number of samples)
    for i in range(n):
        # Up tick in count of pages visited
        nr_pages_visited += 1
        # Increase the value of the current page in the visited pages dict
        visited_pages[current_page] += 1
        # Using trasition_model func. get the probability distribution of other pages from the current page
        distribution = transition_model(corpus, current_page, damping_factor)
        # Randomly select a value to create a 'first past the post' style randomiser
        random_value = random.random() * sum(distribution.values())
        # Start at 0
        sum_probabilities = 0.0
        # Iterate through the distribution
        for page, probility in distribution.items():
            # Add the probabilities, continuously
            sum_probabilities += probility
            # When the added probabilities are over the randomly selected values
            # Then select that specific page as the random next page to go to
            if sum_probabilities >= random_value:
                # Set the randomly selected page as the current page
                current_page = page
                # Restart the loop
                break

    # Initialise a dict for page rank
    page_rank = {}
    # Iterate through the keys and values in the visited_pages dict
    for page, value in visited_pages.items():
        # The rank of each page is the number of times it was visited divided by the total number of pages visitied
        # (This gives a proportional representation of the most popular pages)
        rank = value/nr_pages_visited
        # Update page rank with new value
        page_rank.update({page : rank})

    # Return the page rank dict with pages and values
    return page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Calculate the number of pages in the corpus
    number_pages = len(corpus)
    # Get a list of the pages from the keys of the corpus
    pages = list(corpus.keys())
    # Initialise a page rank dict
    page_rank = {}
    # Set the initial value of the highest calculated change in page rank as 1
    # (This is only to start the while loop)
    highest_page_rank_change = 1
    # Set the threshold of acceptible maximum change in page rank as 0.001
    threshold = 0.001

    # As a starting point to page rank:
    # Set the page rank of every page to a uniform probability of 1/total number of pages in corpus
    for page in pages:
        # Add the page and value to the page rank dict
        page_rank[page] = (1.0/number_pages)

    # A while loop which only ends when the highest change in page rank fall below a specified value
    while highest_page_rank_change > threshold:
        # Set the highest change to 0 (so that the loop does not get stuck)
        highest_page_rank_change = 0
        # Initialise a new ranks dic
        # (so that the page rank dict is not mutated during the loop)
        new_ranks = {}
        # Iterate through each page
        for page in pages:
            # For second half of formula
            sum_of_links = 0
            # Iterate through pages and see if they link to current one
            for possible_link in pages:
                # Treat pages with no links as connecting to all
                number_links = len(corpus[possible_link])
                if number_links == 0:
                    number_links = number_pages
                    links_to_page = True
                else:
                    # True if possible link is listed in values of corpus key
                    links_to_page = (page in corpus[possible_link])

                if links_to_page:
                    sum_of_links += (page_rank[possible_link] / number_links)

            page_rank_current = ((1 - damping_factor) / number_pages) + damping_factor * sum_of_links
            new_ranks[page] = page_rank_current
            page_rank_change_current = abs(page_rank_current - page_rank[page])
            if highest_page_rank_change < page_rank_change_current:
                highest_page_rank_change = page_rank_change_current
        page_rank = new_ranks

    return page_rank

if __name__ == "__main__":
    main()
