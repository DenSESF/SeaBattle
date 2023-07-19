import random


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'Координаты выходят за поле доски.'


class BoardRepeatDotException(BoardException):
    def __str__(self):
        return 'Повторный выстрел по координатам.'


class BoardShipFailed(BoardException):
    def __str__(self):
        return 'Не удалось разместить корабль.'


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # def __str__(self):
    #     return f'Dot({self.x}, {self.y})'


class Ship:

    def __init__(self, decks, bow: Dot, v_orient):
        self._decks = decks
        self._bow = bow
        self._v_orient = v_orient
        self.live = decks
        self._dots = self.create_dots()

    @property
    def dots(self):
        return self._dots

    def create_dots(self):
        dots = [self._bow]
        for i in range(1, self._decks):
            if self._v_orient:
                dots.append(Dot(self._bow.x + i, self._bow.y))
            else:
                dots.append(Dot(self._bow.x, self._bow.y + i))
        return dots

    def __str__(self):
        return (f'Ship: decks = {self._decks}, bow = {self._bow},'
                f' vertical orientation = {self._v_orient}, live = {self.live}')


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self._size = size
        self._board = self.create_board()
        self._ships = []
        self.ships_live = 0
        self._dots_busy = []

    def create_board(self):
        row_cell = ['0' for _ in range(self._size)]
        board = [row_cell.copy() for _ in range(self._size)]
        return board

    def clear_board(self):
        self._board = self.create_board()
        self._ships = []
        self.ships_live = 0
        self._dots_busy = []

    def clear_dots_busy(self):
        self._dots_busy = []

    @property
    def size(self):
        return self._size

    # @size.setter
    # def size(self, custom_size):
    #     self._size = custom_size

    def get_board(self):
        list_row = []
        str_row = ' |' + '|'.join(str(i + 1) for i in range(self._size)) + '|'
        list_row.append(str_row)
        for i, row in enumerate(self._board):
            str_row = str(i + 1) + '|' + '|'.join(row) + '|'
            list_row.append(str_row)
        return list_row

    # def __str__(self):
    #     str_cells = ' |'
    #     str_cells += '|'.join(str(i + 1) for i in range(self._size)) + '|\n'
    #     for i, row in enumerate(self._board):
    #         str_cells += str(i + 1) + '|' + '|'.join(row) + '|\n'
    #     return str_cells

    def out(self, dot: Dot):
        return not (0 <= dot.x < self._size) or not (0 <= dot.y < self._size)

    def contur(self, ship: Ship, visible=False):
        near_dots = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]
        for desk in ship.dots:
            for x, y in near_dots:
                test_dot = Dot(desk.x + x, desk.y + y)
                if not(self.out(test_dot)) and test_dot not in self._dots_busy:
                    self._dots_busy.append(test_dot)
                    if visible:
                        self._board[test_dot.x][test_dot.y] = '.'

    def add_ship(self, ship: Ship):
        for desk in ship.dots:
            if self.out(desk) or desk in self._dots_busy:
                raise BoardShipFailed
        for desk in ship.dots:
            self._dots_busy.append(desk)
            if self.hid:
                self._board[desk.x][desk.y] = '■'
        self._ships.append(ship)
        self.ships_live += 1
        self.contur(ship)

    def shot(self, dot: Dot):
        if self.out(dot):
            raise BoardOutException
        if dot in self._dots_busy:
            raise BoardRepeatDotException
        for ship in self._ships:
            if dot in ship.dots:
                self._dots_busy.append(dot)
                ship.live -= 1
                print('Попал!') if ship.live != 0 else print('Убил!')
                if ship.live == 0:
                    self.contur(ship, True)
                    self.ships_live -= 1
                self._board[dot.x][dot.y] = 'X'
                return True
        self._board[dot.x][dot.y] = '.'
        self._dots_busy.append(dot)
        print('Мимо!')
        return False


class Player:
    def __init__(self, player: Board, enemy: Board):
        self.player_board = player
        self.enemy_board = enemy

    def ask(self) -> Dot:
        pass

    def move(self):
        while True:
            shot: Dot = self.ask()
            try:
                hit = self.enemy_board.shot(shot)
            except BoardException as error:
                print(error)
            else:
                return hit


class User(Player):
    def ask(self):
        while True:
            coord_shot = input('Ведите координаты выстрела:').split()
            if len(coord_shot) != 2:
                print('Введите две координаты через пробел.')
                continue
            elif any(not (c.isdigit()) for c in coord_shot):
                print(f'Введите цифры от 1 до {self.enemy_board.size}')
                continue
            break
        x, y = map(int, coord_shot)
        return Dot(x - 1, y - 1)


class Ai(Player):
    def ask(self):
        x = random.randint(1, self.enemy_board.size)
        y = random.randint(1, self.enemy_board.size)
        print(f'Координаты выстрела противника: {x} {y}')
        return Dot(x - 1, y - 1)


class Game:
    def __init__(self):
        self._ship_desk = [3, 2, 2, 1, 1, 1, 1]
        self.user_board = Board(True)
        self.random_board(self.user_board)
        self.comp_board = Board(False)
        self.random_board(self.comp_board)
        self._user = User(self.user_board, self.comp_board)
        self._comp = Ai(self.comp_board, self.user_board)

    def random_board(self, board: Board):
        def get_free_dots():
            dots = []
            for x in range(0, board.size):
                for y in range(0, board.size):
                    dots.append(Dot(x, y))
            return dots

        # count = 0
        free_dots = get_free_dots()
        while board.ships_live != len(self._ship_desk):
            while True:
                if board.ships_live == len(self._ship_desk):
                    # print(f'Количество повторов очистки доски: {count}')
                    break
                len_ship = self._ship_desk[board.ships_live]
                if len(free_dots) == 0 and board.ships_live < len(self._ship_desk):
                    # count += 1
                    board.clear_board()
                    free_dots = get_free_dots()
                    break
                index = random.randint(0, len(free_dots) - 1)
                vertical = True if 0 == random.randint(0, 1) else False
                # print(Ship(len_ship, free_dots[index], vertical))
                try:
                    board.add_ship(Ship(len_ship, free_dots[index], vertical))
                except BoardException:
                    # except BoardException as error:
                    # print({error})
                    free_dots.remove(free_dots[index])
                else:
                    free_dots.remove(free_dots[index])
                    # print(board)
        board.clear_dots_busy()
        # print(f'Кораблей на доске: {board.ships_live}\n')

    @staticmethod
    def greet():
        print('*' * 58)
        print('*' + ' ' * 56 + '*')
        print('*' + ' ' * 19 + 'Игра "Морской бой"' + ' ' * 19 + '*')
        print('*' + ' ' * 10 + 'Формат ввода координат выстрела: x y' + ' ' * 10 + '*')
        print('*' + ' ' * 16 + 'x - строки, y - столбцы.' + ' ' * 16 + '*')
        print('*' + ' ' * 56 + '*')
        print('*' * 58)

    def loop(self):
        def print_boards():
            user_list_board = self._user.player_board.get_board()
            comp_list_board = self._comp.player_board.get_board()
            print('\n' + ' ' * 10 + 'Своя доска:' + ' ' * 12 + 'Доска противника:')
            for i in range(len(user_list_board)):
                print(' ' * 8 + user_list_board[i] + ' ' * 12 + comp_list_board[i])
            print(' ' * 5 + f'Кораблей осталось: {self._user.player_board.ships_live}' +
                  ' ' * 6 + f'Кораблей осталось: {self._comp.player_board.ships_live}')
            print('\n' + '*' * 58)

        def repeat():
            nonlocal count, hit
            count += 1
            if hit:
                count -= 1

        self.greet()
        print_boards()
        count = 0
        while True:
            if count % 2 == 0:
                hit = self._user.move()
                repeat()
            else:
                hit = self._comp.move()
                repeat()
            print_boards()
            if self._user.player_board.ships_live == 0:
                print(' ' * 20 + 'Победил компьютер!')
                break
            if self._comp.player_board.ships_live == 0:
                print(' ' * 20 + 'Победил игрок!')
                break

    def start(self):
        self.loop()
