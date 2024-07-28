import sys
import time
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype(sys.argv[0].replace("generate.py", "assets/fonts/OpenSans-Regular.ttf", 100))
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            new_domain = set()
            for word in self.domains[var]:
                if len(word) == var.length:
                    new_domain.add(word)
            self.domains[var] = new_domain

        return
        
        raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        cell = self.crossword.overlaps[(x, y)]      #Devuelve (i, j) donde i es el caracter de x que coincide con el caracter j de y
                                                    #Si no hay celdas comunes devuelve None

        if cell != None:
            new_x_domain = set()
            for xword in self.domains[x]:
                new_y_domain = set()
                for yword in self.domains[y]:     #Va creando un nuevo dominio de y que coumpla la consistencia con xword
                    # if xword == yword:          # Esto lo podemos comprobar aquí, sin embargo lo haremos en consistent
                    #     continue

                    if xword[cell[0]] == yword[cell[1]]:            # Comprueba que se cumpla la consistencia
                        new_y_domain.add(yword)                     # la añade al nuevo dominio
                
                if new_y_domain != set():                           # Si tras el bucle el nuevo dominio de y no está vacío
                    new_x_domain.add(xword)                         # añade xword al nuevo dominio de x
            
            if (self.domains[x] == new_x_domain):
                return False
            else:
                self.domains[x] = new_x_domain
                return True


        raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:                                        #Si no se envía ningun arc se analizan todos.
            arcs = list()
            for arc in self.crossword.overlaps:
                if self.crossword.overlaps[arc] != None:
                    arcs.append(arc)
        
        new_arcs = arcs.copy()
        while new_arcs != list():
            arc = new_arcs.pop(0)
            if self.revise(arc[0], arc[1]):                         # Si al revisarlo se modifica algo:
                for arc_x in arcs:                                  # Añade de nuevo todos los arcos en los que aparece la variable modificada
                    if arc[0] in arc_x and arc_x not in new_arcs:
                        new_arcs.append(arc_x)

        for x in self.domains:                      # Si alguno de los dominios está vacío devuelve none
            if self.domains[x] == None:
                return False
        
        return True
        
        raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(self.domains) == len(assignment):
            return True
        else:
            return False
        
        raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        if len(list(assignment.values())) != len(set(assignment.values())):         #Si hay duplicados
            return False
        
        for x, x_word in assignment.items():
            for y, y_word in assignment.items():
                if y != x:
                    cell = self.crossword.overlaps[(x, y)]
                    if cell != None:
                        if x_word[cell[0]] != y_word[cell[1]]:
                            return False
        
        return True
    
        raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
    #     neighbors_set = self.crossword.neighbors(var)
    #     result = list()
        

    #     for word in self.domains[var]:                              #Bucle para todas las palabras del dominio de var
    #         new_crossword = CrosswordCreator(self.crossword)        #Creamos un nuevo tablero en el que introduciremos los assignment conocidos
    #         for var_as, word_as in assignment.items():
    #             new_crossword.domains[var_as] = word_as
    #         new_crossword.domains[var] = word                       #añadimos esa palabra como el único dominio de var

    #         #Con este nuevo tablero volvemos a aplicar las condiciones
    #         new_crossword.enforce_node_consistency()
    #         new_crossword.ac3()                                   #Si al aplicarlas nos quedan dominios vacios pasamos de palabra
            
    #         n_sum = 0
    #         #Ahora calculamnos n_sum como la suma de los dominios de todas los vecinos
    #         for neighbor_var in neighbors_set:
    #             n_sum += len(new_crossword.domains[neighbor_var])
            
    #         #Guardamos el resultado en una lista con word, n_sum:
    #         result.append((word, n_sum))


    #     sorted_result = dict(sorted(result, key=lambda x:x[1]))
        
    #     return list(sorted_result.keys())
    
        # sorted_result = sorted(self.domains[var])
        # return sorted_result
        neighbors_set = self.crossword.neighbors(var)
        result = []

        for word in self.domains[var]:
            n_sum = 0

            for neighbor in neighbors_set:
                if neighbor in assignment:
                    continue

                overlap_indices = [(var.cells.index(cell), neighbor.cells.index(cell)) for cell in var.cells if cell in neighbor.cells]
                if not overlap_indices:
                    continue

                for neighbor_word in self.domains[neighbor]:
                    overlap_match = True
                    for var_idx, neighbor_idx in overlap_indices:
                        if word[var_idx] != neighbor_word[neighbor_idx]:
                            overlap_match = False
                            break
                    if overlap_match:
                        n_sum += 1

            result.append((word, n_sum))

        result.sort(key=lambda x: x[1])
        return [word for word, _ in result]
    
        raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        n = float("inf")
        degree = - float("inf")
    
        for var in self.crossword.variables:
            if var not in assignment:
                n_var = len(self.domains[var])
                if n_var < n:
                    n = n_var
                    select_var = var
                elif n == n_var:
                    degree_var = len(self.crossword.neighbors(var))
                    if degree_var > degree:
                        degree = degree_var
                        select_var = var
        return select_var

        raise NotImplementedError

    # def backtrack(self, assignment):
    #     """
    #     Using Backtracking Search, take as input a partial assignment for the
    #     crossword and return a complete assignment if possible to do so.

    #     `assignment` is a mapping from variables (keys) to words (values).
    #     If no assignment is possible, return None.
    #     """

    #     new_crossword = CrosswordCreator(self.crossword)        #Creamos un nuevo tablero en el que introduciremos los assignment conocidos
    #     for var, word in assignment.items():
    #         new_crossword.domains[var] = word
        
    #     new_crossword.enforce_node_consistency()                #Comprobamos que este nuevo tablero tiene solución
    #     if not new_crossword.ac3():
    #         return None                                         #Si no la tiene, devuelve None

    #     if self.assignment_complete(assignment):
    #         return assignment
       
    #     # Si aún no esta completo:
    #     unassigned_variable = self.select_unassigned_variable(assignment)           # Escoge una casilla vacía

    #     variable_value = self.order_domain_values(unassigned_variable, assignment)  # Recoge los valores posibles ordenados.
    #     for value in variable_value:
    #         new_assignment = assignment.copy()
    #         new_assignment[unassigned_variable] = value
            
    #         if self.consistent(new_assignment):
    #             result = self.backtrack(new_assignment)
    #             if result is not None:
    #                 return result

    #     return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """

        # Check if the assignment is complete
        if self.assignment_complete(assignment):
            return assignment

        # Select an unassigned variable with the minimum remaining values
        var = self.select_unassigned_variable(assignment)

        # Order the domain values using the least constraining value heuristic
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            # Check consistency of the new assignment
            if self.consistent(new_assignment):
                # Make a deep copy of the domains to restore later if needed
                original_domains = self.domains.copy()
                
                # Enforce node consistency and apply AC-3
                self.domains[var] = {value}
                self.enforce_node_consistency()
                if self.ac3():
                    result = self.backtrack(new_assignment)
                    if result is not None:
                        return result

                # Restore the original domains if the assignment was not successful
                self.domains = original_domains




        
        raise NotImplementedError


def main():
    # Añadir el directorio
    if len(sys.argv) != 1:
        sys.exit("Usage: python pagerank.py corpus")
    directorio = sys.argv[0].replace("generate.py", "data/")


    # # Check usage
    # if len(sys.argv) not in [3, 4]:
    #     print(sys.argv)
    #     sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = directorio + "structure2.txt"
    words = directorio + "words2.txt"
    output = directorio + "structure2.png"



    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            print("creating save...")
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
