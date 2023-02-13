from random import choice

INF = float('inf')

board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
player = choice([1, -1])
opponent = -player


def print_board():
    for row in board:
        print(row)


def is_valid_move(x, y):
    return board[x][y] == 0


def is_board_full():
    for row in board:
        for cell in row:
            if cell == 0:
                return False
    return True


def is_game_over():
    return is_board_full() or is_winner(player) or is_winner(opponent)


def is_winner(current_player):
    for row in board:
        if all(cell == current_player for cell in row):
            return True
    for col in range(3):
        if all(board[row][col] == current_player for row in range(3)):
            return True
    if all(board[i][i] == current_player for i in range(3)):
        return True
    if all(board[i][2 - i] == current_player for i in range(3)):
        return True
    return False


def minimax(board, current_player):
    if is_winner(current_player):
        return current_player
    if is_board_full():
        return 0
    best_score = -INF
    for x in range(3):
        for y in range(3):
            if is_valid_move(x, y):
                board[x][y] = current_player
                score = minimax(board, -current_player)
                board[x][y] = 0
                best_score = max(best_score, score)
    return best_score


if __name__ == '__main__':
    while not is_game_over():
        print_board()
        if player == 1:
            x, y = map(int, input('Enter coordinates: ').split())
            if is_valid_move(x, y):
                board[x][y] = player
                player, opponent = opponent, player
            else:
                print('Invalid move')
        else:
            best_score = -INF
            best_move = None
            for x in range(3):
                for y in range(3):
                    if is_valid_move(x, y):
                        board[x][y] = player
                        score = minimax(board, opponent)
                        board[x][y] = 0
                        if score > best_score:
                            best_score = score
                            best_move = (x, y)
            x, y = best_move
            board[x][y] = player
            player, opponent = opponent, player
    print_board()
    if is_winner(player):
        print(f"Player {player} wins!")
    elif is_winner(opponent):
        print(f"Player {opponent} wins!")
    else:
        print("It's a draw!")
