from random import randint
import time


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    # message = "Board Out Exception"
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "Вы пытаетесь выстрелить за доску!"

    def __str__(self):
        return self.message


class UsedPointException(BoardException):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "Вы уже стреляли в эту клетку"

    def __str__(self):
        return self.message


class BoardWrongShipException(BoardException):
    pass


class Dot:
    # x = 0
    # y = 0
    # status = 0  # 0 - свободно, 1 - корабль, 2 - выстрелен

    def __init__(self, x, y, status=0):
        self.x = x
        self.y = y
        self.status = status

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    # length = 1  # Длина.
    # head = None  # Точка, где размещён нос корабля.
    # course = 1 #"vertical"  # Направление корабля: 1 = vertical(вертикальное)/ 2 = horizontal(горизонтальное).
    # lives = length  # Количеством жизней (сколько точек корабля еще не подбито, при создании корабля равно его длине).
    # ship_dots = []  # список всех точек корабля

    def __init__(self, head, length=1, course=1):
        self.length = length
        self.head = head
        self.course = course
        self.lives = length
        self.ship_dots = []
        x = self.head.x
        y = self.head.y
        for i in range(self.length):
            if self.course == 1:
                self.ship_dots.append(Dot(x, y + i, 1))
            else:
                self.ship_dots.append(Dot(x + i, y, 1))

    @property
    def dots(self):
        return self.ship_dots

    def dot_is_in_ship(self, dot):
        return dot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.downed_ships_count = 0  # количество подбитых кораблей
        self.living_ships_count = 0  # количество живых кораблей
        self.field = [["0"] * size for _ in range(size)]
        self.busy_cells = []
        self.ships = []

    def __str__(self):
        ret_val = "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            ret_val += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            ret_val = ret_val.replace("■", "0")
        return ret_val

    def out(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def contour(self, ship, verb=False):
        # шаблон для сдвига координат для обхода контура вокруг указанной точки:
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        # для каждой точки корабля (переданного в параметре ship) - определяем контур:
        for d in ship.dots:
            for dx, dy in near:  # для каждой пары координат шаблона near определяем точку контура:
                cur = Dot(d.x + dx, d.y + dy)  # добавляем к координатам точки корабля - координаты шаблона контура
                # self.field[cur.x][cur.y] = "+"  # для тестирования закомментировать все, что ниже в методе
                if not (self.out(cur)) and cur not in self.busy_cells:  # если НЕ (точка за пределами доски
                    # или уже занята (уже стреляли)):
                    if verb:  # если нужно ставить знак точки вокруг корабля (параметр verb=True)
                        self.field[cur.x][cur.y] = "."  # ставим знак точки
                    self.busy_cells.append(cur)  # добавляем точку в список занятых

    def add_ship(self, ship):  # добавляем корабль на доску
        for d in ship.dots:  # для каждой точки корабля (переданного в параметре ship) проверяем:
            if self.out(d) or d in self.busy_cells:  # если точка за пределами доски или клетка уже занята (уже стреляли):
                raise BoardWrongShipException()  # выбрасываем исключение
        for d in ship.dots:  # для каждой точки корабля (переданного в параметре ship)
            self.field[d.x][d.y] = "■"  # устанавливаем на поле доски символ(знак) корабля - "■"
            self.busy_cells.append(d)  # и добавляем точку в список занятых
        self.ships.append(ship)  # добавляем корабль в список кораблей доски
        self.contour(ship)  # добавляем все точки контура в список занятых (без прорисовки на доске)

    def shot(self, dot, until_miss=False):  # стреляем в точку
        if self.out(dot):
            raise BoardOutException()
        if dot in self.busy_cells:
            raise UsedPointException()

        self.busy_cells.append(dot)

        for ship in self.ships:
            if ship.dot_is_in_ship(dot):
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.lives == 0:
                    self.downed_ships_count += 1
                    self.contour(ship, verb=True)
                    print("Корабль убит!")
                    return until_miss  # если передали until_miss=True, игрок продолжает стрелять/ иначе - переход хода
                else:
                    print("Корабль ранен!")
                    return True

        self.field[dot.x][dot.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy_cells = []

    def defeat(self):
        return self.downed_ships_count == len(self.ships)

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
        self.go_until_miss = False  # ходить до промаха

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target, self.go_until_miss)
                return repeat
            except BoardException as e:
                print(e)

    def go_until_miss_activate(self):
        self.go_until_miss = True


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class Gamer(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход. Введите 2 координаты: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты.")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)


class Game:
    def __init__(self, size=6):
        self.size = size
        self.boards_horizont = False  # расположение досок на экране (True - горизонтальное, в строку)
        self.with_pause = False  # делать паузу во время хода компьютера
        self.go_until_miss = False  # True - игрок ходит, пока не промажет
        pl = self.random_board()
        comp = self.random_board()
        comp.hid = True

        self.ai = AI(comp, pl)
        self.us = Gamer(pl, comp)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts>2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("---------------------")
        print("     Морской бой     ")
        print("---------------------")
        print(" формат ввода: x, y ")
        print(" x - номер строки ")
        print(" y - номер столбца ")

    def print_board(self):
        if self.boards_horizont:
            print("-" * 27, " "*8, "-" * 27)
            print("Доска пользователя:", " "*10, " "*10,"Доска компьютера:")
            print(self.print_two_boards(self.us.board, self.ai.board))
            print("-" * 64)
        else:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)

    def print_two_boards(self, board_1, board_2):
        ret_val = "  | 1 | 2 | 3 | 4 | 5 | 6 |" + " " * 10 + "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        ret_str1 = ret_str2 = ""
        for i in range(6):
            ret_str1 = f"{i + 1} | " + " | ".join(board_1.field[i]) + " |"
            if board_1.hid:
                ret_str1 = ret_str1.replace("■", "0")
            ret_str2 = f"{i + 1} | " + " | ".join(board_2.field[i]) + " |"
            if board_2.hid:
                ret_str2 = ret_str2.replace("■", "0")
            ret_val += "\n" + ret_str1 + " "*10 + ret_str2
        return ret_val

    def loop(self):
        num = 0
        while True:
            self.print_board()
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                if self.with_pause:
                    time.sleep(3)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():  # .downed_ships_count == len(self.ai.board.ships):
                self.print_board()
                print("-" * 20)
                print("Выиграл пользователь!")
                break

            if self.us.board.defeat():
                self.print_board()
                print("-" * 20)
                print("Выиграл компьютер!")
                break

            num += 1

    def start(self):
        if self.go_until_miss:
            self.ai.go_until_miss_activate()
            self.us.go_until_miss_activate()
        self.greet()
        self.loop()


# Создаем экземпляр класса Game
g = Game()
# можно дополнительно поменять некоторые настройки игры:
g.boards_horizont = True  # расположение досок на экране (True - горизонтальное, False - вертикальное)
g.with_pause = True  # делать паузу во время хода компьютера 3 сек
g.go_until_miss = True  # игрок ходит, пока не промажет (False - после потопления корабля противника - переход хода)
# Запускаем игру
g.start()
