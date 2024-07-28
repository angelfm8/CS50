import os
import random
import re
import sys


DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 1:
        sys.exit("Usage: python pagerank.py corpus")
    directorio = sys.argv[0].replace("pagerank.py", "corpus"+input("corpus:"))
   
   
    corpus = crawl(directorio)
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

    pages_len = len(corpus[page])   #Número de paginas con las que enlaca page
    
    prob = dict()
    prob[page] = (1- damping_factor)/(pages_len + 1)

    for page_i in corpus[page]: #Para cada una de estas paginas:
        prob[page_i] = damping_factor/pages_len
    
    return prob


    raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    count_pages = dict()
    for page in corpus:
        count_pages[page] = 0
    
    
    random_page = random.choice(list(corpus.keys()))

    count_pages[random_page] += 1/n

    

    for i in range(n-1):
        if random.random() > damping_factor:    #Probabilidad de que vuelva a una pagina al azar
            random_page = random.choice(list(corpus.keys()))
        else:
            available_page = transition_model(corpus, random_page, damping_factor)
            random_page = random.choices(list(available_page.keys()), available_page.values())[0]
        
        count_pages[random_page] += 1/n
    
    return count_pages


    raise NotImplementedError


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    norm = len(corpus)
    count_pages = dict()
    new_count_pages = dict()

    #inicializamos los valores de PR
    for page in corpus:
        count_pages[page] = 1/norm


    var = 1 #Parametro que mide si PR está convergiendo (el limite lo ponemos en 0.00001)
    i = 0

    while i < 10000 and var > 0.00001:
        i += 1
        var = 0
        for page in count_pages:                #Para todas las paginas cambiamos PR por el proveniente de la formula
            new_count_pages[page] = (1-damping_factor)/norm
            for elem, links in corpus.items():            #Hay que hacer sumatorio sobre todas las paginas que tenga un link a la pagina que estamos actualizando
                if page in links:
                    new_count_pages[page] += damping_factor*count_pages[elem]/len(links)
            
            var += abs(count_pages[page] - new_count_pages[page])
        
        var = var/norm  #Actualiza el valor de la variación


        count_pages = new_count_pages.copy()
        new_count_pages.clear()
    
    return count_pages
    


    raise NotImplementedError


if __name__ == "__main__":
    main()
