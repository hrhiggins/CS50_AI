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

    number_pages_linked = len(corpus[page])
    number_pages = len(corpus)
    number_pages_not_linked = number_pages - number_pages_linked
    probability_not_linked = (1 - damping_factor) / number_pages_not_linked
    probability_linked = damping_factor / number_pages_linked

    linked_pages = corpus[page]
    probability_dict = {}

    for key in corpus:
        if key in linked_pages:
            probability_dict[key] = probability_linked
        else:
            probability_dict[key] = probability_not_linked

    return probability_dict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    current_page = corpus[random.randint(1, len(corpus))]
    list_visited_pages = []
    page_rank = {}
    nr_pages_visited = 0

    while nr_pages_visited < n:
        nr_pages_visited += 1
        page_distribution = []
        list_visited_pages.append(current_page)
        next_page_corpus = transition_model(corpus, current_page, damping_factor)
        for page, probability in next_page_corpus.items():
            probability_page = probability * 100
            for i in range(probability_page):
                page_distribution.append(page)
        current_page = random.choice(page_distribution)

    for page in list_visited_pages:
        if page in page_rank:
            page_rank[page] += 1
        else:
            page_rank.update({page: 1})

    return page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    number_pages = len(corpus)
    page_rank = {}
    highest_page_rank_change = 1

    for page in corpus:
        page_rank.update({page: (1/number_pages)})

    while highest_page_rank_change < 0.001:
        highest_page_rank_change = 0
        for page in corpus:
            page_rank_current = ((1 - damping_factor) / number_pages)
            sum_of_links = 0
            for link in corpus[page]:
                sum_of_links += (page_rank[link]/corpus[link])
            page_rank_current += number_pages * sum_of_links
            page_rank_change_current = abs(page_rank_current - page_rank[page])
            if highest_page_rank_change < page_rank_change_current:
                highest_page_rank_change = page_rank_change_current
            page_rank[page] = page_rank_current

    # Check that values in page rank dict sum to 1
    sum = 0
    for page_rank_value in page_rank.values():
        sum += page_rank_value
    if sum != 1:
        raise ValueError("PageRank values do not sum to 1")

    return page_rank
if __name__ == "__main__":
    main()
