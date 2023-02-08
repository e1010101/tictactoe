import sys
from random import choice

import pygame as pg

INF = float('inf')
vector = pg.math.Vector2
WIN_SIZE = 900
CELL_SIZE = WIN_SIZE // 3
CELL_CENTER = vector(CELL_SIZE / 2)


class TicTacToe:
    def __init__(self, game_process):
        self.game = game_process
        self.field_image = self.get_scaled_image(path='resources/Grid.png', res=[WIN_SIZE] * 2)
        self.O_image = self.get_scaled_image(path='resources/O.png', res=[CELL_SIZE] * 2)
        self.X_image = self.get_scaled_image(path='resources/X.png', res=[CELL_SIZE] * 2)

        self.game_array = [[INF, INF, INF], [INF, INF, INF], [INF, INF, INF]]
        self.player = choice([-1, 1])
        self.ai_idx = - self.player
        self.ai = AI(self)

        self.line_indices_array = [[(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)], [(2, 0), (2, 1), (2, 2)],
                                   [(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],
                                   [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]]
        self.winner = None
        self.winner_line = None
        self.game_steps = 0
        self.font = pg.font.SysFont('Verdana', CELL_SIZE // 4, True)

    def check_winner(self):
        for line_indices in self.line_indices_array:
            sum_line = sum([self.game_array[i][j] for i, j in line_indices])
            if sum_line in {-3, 3}:
                self.winner = 'XO'[sum_line == -3]
                self.winner_line = [vector(line_indices[0][::-1]) * CELL_SIZE + CELL_CENTER,
                                    vector(line_indices[2][::-1]) * CELL_SIZE + CELL_CENTER]

    def run_game_process(self):
        current_cell = vector(pg.mouse.get_pos()) // CELL_SIZE
        col, row = map(int, current_cell)
        left_click = pg.mouse.get_pressed()[0]

        if left_click and self.game_array[row][col] == INF and not self.winner:
            self.game_array[row][col] = self.player
            self.game_steps += 1
            if self.game_steps == 9:
                return
            self.player = - self.player
            self.check_winner()
            self.ai.update_board(self.game_array)
        elif self.player == self.ai_idx:
            self.ai.ai_turn()

    def draw_objects(self):
        for y, row in enumerate(self.game_array):
            for x, obj in enumerate(row):
                if obj != INF:
                    self.game.screen.blit(self.X_image if obj == 1 else self.O_image, vector(x, y) * CELL_SIZE)

    def draw_winner(self):
        if self.winner:
            pg.draw.line(self.game.screen, 'red', *self.winner_line, CELL_SIZE // 8)
            label = self.font.render(f'Player "{self.winner}" wins!', True, 'white', 'black')
            self.game.screen.blit(label, (WIN_SIZE // 2 - label.get_width() // 2, WIN_SIZE // 4))

    def draw(self):
        self.game.screen.blit(self.field_image, (0, 0))
        self.draw_objects()
        self.draw_winner()

    @staticmethod
    def get_scaled_image(path, res):
        img = pg.image.load(path)
        return pg.transform.smoothscale(img, res)

    def print_caption(self):
        pg.display.set_caption(f'Player "{"OX"[self.player]}" turn!')
        if self.winner:
            pg.display.set_caption(f'Player "{self.winner}" wins! Press Space to Restart')
        elif self.game_steps == 9:
            pg.display.set_caption(f'It\'s a draw! Press Space to Restart')

    def run(self):
        self.print_caption()
        self.draw()
        self.run_game_process()


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode([WIN_SIZE, WIN_SIZE])
        self.clock = pg.time.Clock()
        self.ttt = TicTacToe(self)

    def new_game(self):
        self.ttt = TicTacToe(self)

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.new_game()

    def run(self):
        while True:
            self.ttt.run()
            self.check_events()
            pg.display.update()
            self.clock.tick(60)


class AI:
    def __init__(self, tictactoe):
        self.board = None
        self.tictactoe = tictactoe
        self.ai_idx = tictactoe.ai_idx

    def update_board(self, board):
        self.board = board

    def ai_turn(self):
        if self.tictactoe.game_steps == 0:
            self.tictactoe.game_array[0][0] = self.ai_idx
        else:
            if self.tictactoe.winner is not None or self.tictactoe.game_steps == 9:
                return
            best_move = self.alpha_beta_search(self.board, self.ai_idx)
            self.tictactoe.game_array[best_move[0]][best_move[1]] = self.ai_idx
        self.tictactoe.player = - self.tictactoe.player
        self.tictactoe.game_steps += 1
        self.tictactoe.check_winner()

    def alpha_beta_search(self, board, player):
        max_value = self.max_value(board, player, -INF, INF)
        for i in range(3):
            for j in range(3):
                if board[i][j] == INF:
                    board[i][j] = player
                    value = self.min_value(board, player, -INF, INF)
                    board[i][j] = INF
                    if value == max_value:
                        return i, j

    def max_value(self, board, player, alpha, beta):
        value = self.evaluate(board)
        if value != 0:
            return value
        value = -INF
        for i in range(3):
            for j in range(3):
                if board[i][j] == INF:
                    board[i][j] = player
                    value = max(value, self.min_value(board, player, alpha, beta))
                    board[i][j] = INF
                    if value >= beta:
                        return value
                    alpha = max(alpha, value)
        return value

    def min_value(self, board, player, alpha, beta):
        value = self.evaluate(board)
        if value != 0:
            return value
        value = INF
        for i in range(3):
            for j in range(3):
                if board[i][j] == INF:
                    board[i][j] = not player
                    value = min(value, self.max_value(board, player, alpha, beta))
                    board[i][j] = INF
                    if value <= alpha:
                        return value
                    beta = min(beta, value)
        return value

    def evaluate(self, board):
        for line_indices in self.tictactoe.line_indices_array:
            sum_line = sum([board[i][j] for i, j in line_indices])
            if sum_line in {3, -3}:
                return 1
        return 0


if __name__ == '__main__':
    game = Game()
    game.run()
