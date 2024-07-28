"""
Tic Tac Toe Player
"""

import math

#La libreria copy será necearia para hacer copias de los estados.
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]



""" 
Esta función la utilizamos para contar las veces 
que aparece un valor en una lista de listas 
Esto es necesario en player(), TERMINAL().
"""

def count_list(lista, value):
  count = 0 
  for item in lista:  
    if isinstance(item, list):
      """ Si el objeto que hay que contar es una lista llama recursivamente a count_list  """
      count += count_list(item, value);   
    elif (type(item) == type(value)) and (item == value):
      """ Si el objeto es del mismo tipo que el que estamos buscando y vale lo mismo, lo cuenta."""
      count += 1  
  return count  



def valid_state(board):
    countX = count_list(board, X)
    countY = count_list(board, O)

    """ Los movimientos de O están entre ninguno y 4 """
    if (countY >= 0) and (countY <= 4): 
        """ Los movimientos de O siempre son los mismos o 1 menos que los de X """
        if (countY == countX) or (countY == countX - 1):
            return True
    else:
        print("Estado no válido")
        return False




def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if valid_state(board):
        if count_list(board, EMPTY)%2 == 0:
            return O
        else:
            return X
        
    raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if valid_state(board):
        # Comprobar si hay alguna fila o columna en la que haya un ganador
        for i in list(range(0, 3)):
            """ 
            Comprobar si en esa fila o columna hay un EMPTY
            Con comprobar 1 es suficiente porque luego se comprueba si todos son iguales.
            """
            if board[i][i] != EMPTY:
                # Comprueba si toda la fila es igual"""
                if board[i][0] == board[i][1] and board[i][1] == board[i][2]:
                    return board[i][1]
                # Si no comprueba si toda la columna es igual
                elif board[0][i] == board[1][i] and board[1][i] == board[2][i]:
                    return board[1][i]

        if ((board[0][0] == board[1][1]) and (board[1][1] == board[2][2])) or ((board[2][0] == board[1][1]) and (board[1][1] == board[0][2])):
            return board[1][1]
        else:
            return None
    
    raise NotImplementedError



def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if valid_state(board):
        # Comprueba si la lista esta llena
        if count_list(board, EMPTY) == 0:
                return True
        else:
             # Comprueba si hay un ganador.
            if winner(board) == None:
                return False
            else:
                return True
        
    raise NotImplementedError




def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    if valid_state(board):
        # Acciones tiene que ser un set.
        acciones = set()

        if not terminal(board):
            # Añade un tuple con la posición donde se puede mover
            for i in range(0,3):
                for j in range(0,3):
                    # Se puede mover donde esté vacío
                    if board[i][j] == EMPTY:
                        acciones.add((i, j))
                        
        return acciones
    
    raise NotImplementedError





def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if valid_state(board):
        """
        Crea un nuevo estado sobre el que se guardarán las acciones.
        Esto se debehacer mediante copy.deepcopy() ya que si no, se modifica board
        """
        new_board = copy.deepcopy(board)

        # Si la acción a realizar es posible, la hace
        if action in actions(board):
            new_board[action[0]][action[1]] = player(board)
            return new_board
        else:
            raise NameError("Invalid Action")
    
    raise NotImplementedError




def utility(board):
    """
    Returns 10 if X has won the game, -10 if O has won, 0 otherwise.

    * Se le realiza una modificación que añade la profundida de la jugada.
    Para ello se le resta a la puntuación la profundidad por lo que queda:
    Returns (10 - depth) si gana X, -(10 - depth) si gana O y 0 en cualquuier otro caso.
    """
    if valid_state(board):
        depth = 9 - count_list(board, EMPTY)

        if winner(board) == None:
            return 0
        elif winner(board) == 'X':
            return 10 - depth
        else:
            return -10 + depth

    raise NotImplementedError


def best_score_minimax(board):
    if terminal(board):
        return utility(board)

    if player(board) == 'X':
        best_score = -10
    else:
        best_score = 10


    posible_actions = list(actions(board))

    for action in posible_actions:
        new_board = result(board, action)
        score = best_score_minimax(new_board)
        if player(board) == 'X':    
            if score > best_score:
                best_score = score
        else:
            if score < best_score:
                best_score = score

    
    return best_score
    

def minimax(board):
    best_move = (-1, -1)
    if player(board) == 'X':
        best_score = -10
    else:
        best_score = 10
    
    posible_actions = list(actions(board))

    for action in posible_actions:
        new_board = result(board, action)
        score = best_score_minimax(new_board)
        if player(board) == 'X':    
            if score > best_score:
                best_score = score
                best_move = action
        else:
            if score < best_score:
                best_score = score
                best_move = action
    
    return best_move
    raise NotImplementedError