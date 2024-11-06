import random

# Исключения
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы доски!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"

class BoardWrongShipException(BoardException):
    def __str__(self):
        return "Невозможно разместить корабль в этой позиции!"

# Класс для представления точки на доске
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

# Класс корабля
class Ship:
    def __init__(self, bow, length, orientation):
        self.bow = bow  # нос корабля — точка
        self.length = length  # длина корабля
        self.orientation = orientation  # 0 — горизонтально, 1 — вертикально
        self.lives = length  # количество жизней корабля

    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x + i if self.orientation == 1 else self.bow.x
            cur_y = self.bow.y + i if self.orientation == 0 else self.bow.y
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

# Класс доски
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.board = [["O"] * size for _ in range(size)]
        self.ships = []
        self.busy = []  # Занятые клетки
        self.count = 0  # Количество пораженных кораблей

    def add_ship(self, ship):
        for d in ship.dots():
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots():
            self.board[d.x][d.y] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots():
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.board[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def out(self, d):
        return not (0 <= d.x < self.size and 0 <= d.y < self.size)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots():
                ship.lives -= 1
                self.board[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                else:
                    print("Корабль ранен!")
                return True

        self.board[d.x][d.y] = "T"
        print("Мимо!")
        return False

    def __str__(self):
        res = "   | " + " | ".join([str(i + 1) for i in range(self.size)]) + " |\n"
        for i, row in enumerate(self.board):
            res += f"{i + 1} | " + " | ".join(row) + " |\n"
        if self.hid:
            res = res.replace("■", "O")
        return res

    def begin(self):
        self.busy = []

# Классы игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

class User(Player):
    def ask(self):
        while True:
            coords = input("Ваш ход: ").split()
            if len(coords) != 2:
                print("Введите 2 координаты!")
                continue
            x, y = coords
            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue
            x, y = int(x) - 1, int(y) - 1
            return Dot(x, y)

# Главный класс игры
class Game:
    def __init__(self, size=6):
        pl_board = self.random_board()
        co_board = self.random_board()
        co_board.hid = True
        self.ai = AI(co_board, pl_board)
        self.user = User(pl_board, co_board)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        board = Board(size=6)
        attempts = 0
        lengths = [3, 2, 2, 1, 1, 1, 1]
        for length in lengths:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(
                    Dot(random.randint(0, 5), random.randint(0, 5)),
                    length,
                    random.randint(0, 1)
                )
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    continue
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветствуем вас ")
        print("      в игре       ")
        print("    Морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.user.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == len(self.ai.board.ships):
                print("Пользователь выиграл!")
                break
            if self.user.board.count == len(self.user.board.ships):
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.start()