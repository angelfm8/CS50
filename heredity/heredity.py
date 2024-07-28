import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    
    # Check for proper usage
    if len(sys.argv) != 1:
        sys.exit("Usage: python heredity.py data.csv")

    directorio = sys.argv[0]
    directorio = directorio.replace( "heredity.py", "data\\family" + input("family: ")+".csv")

    people = load_data(directorio)

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def prob_gen(person, gene, people):
    result = 1
    if person != None:
        mother = people[person]["mother"]
        father = people[person]["father"]

        if mother == None and father == None:
            result = PROBS["gene"][gene]
        else:
            herede_m = 0.5*prob_gen(mother, 1, people = people) + 1*prob_gen(mother, 2, people = people)
            noherede_m = 1*prob_gen(mother, 0, people = people) + 0.5*prob_gen(mother, 1, people = people)

            herede_p = 0.5*prob_gen(father, 1, people = people) + 1*prob_gen(father, 2, people = people)
            noherede_p = 1*prob_gen(father, 0, people = people) + 0.5*prob_gen(father, 1, people = people)

            if gene == 0:
                # Debe ser la probabilidad de que:
                # (No la herede de la madre y no mute o la herede y mute) Y (No la herede del padre y no mute o la herede y mute)
                result = result*(noherede_m*(1-PROBS["mutation"]) + herede_m*PROBS["mutation"])
                result = result*(noherede_p*(1-PROBS["mutation"]) + herede_p*PROBS["mutation"])
                
            if gene == 1:
                # (No la herede de la madre y mute o la herede y no mute) y (No la herede del padre y no mute o la herede y mute)
                result = result*(noherede_m*PROBS["mutation"] + herede_m*(1-PROBS["mutation"]))
                result = result*(noherede_p*(1-PROBS["mutation"]) + herede_p*PROBS["mutation"])
                
                # (No la herede de la madre y no mute o la herede y mute) y (No la herede del padre y mute o la herede y no mute) 
                result += (noherede_m*(1-PROBS["mutation"]) + herede_m*PROBS["mutation"])*(noherede_p*PROBS["mutation"] + herede_p*(1-PROBS["mutation"]))
            
            if gene == 2:
                # (No la herede de la madre y mute o la herede y no mute) Y (No la herede del padre y mute o la herede y no mute)
                result = result*(noherede_m*PROBS["mutation"] + herede_m*(1-PROBS["mutation"]))
                result = result*(noherede_p*PROBS["mutation"] + herede_p*(1-PROBS["mutation"]))
    
    return result

            



def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    pfinal = 1

    #Calculo la primera probabilidad:
    for person in people:
        if person in one_gene:                      
            pfinal = pfinal*prob_gen(person, gene = 1, people = people)*PROBS["trait"][1][person in have_trait]
        if person in two_genes:                     
            pfinal = pfinal*prob_gen(person, gene = 2, people = people)*PROBS["trait"][2][person in have_trait]
        if person not in one_gene and person not in two_genes:      
            pfinal = pfinal*prob_gen(person, gene = 0, people = people)*PROBS["trait"][0][person in have_trait]
    
    return pfinal


    raise NotImplementedError


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        if person in two_genes:
            probabilities[person]["gene"][2] += p
        if person not in one_gene and person not in two_genes:
            probabilities[person]["gene"][0] += p
        
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p

    return probabilities
    raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        sum_gene = sum(probabilities[person]["gene"].values())
        sum_trait = sum(probabilities[person]["trait"].values())
        for i in probabilities[person]["gene"]:
            probabilities[person]["gene"][i] = probabilities[person]["gene"][i]/sum_gene
        for i in probabilities[person]["trait"]:
            probabilities[person]["trait"][i] = probabilities[person]["trait"][i]/sum_trait
    
    return probabilities


    raise NotImplementedError


if __name__ == "__main__":
    main()
