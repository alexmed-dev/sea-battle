from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    # message = "Board Out Exception"
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "Board Out Exception"

    def __str__(self):
        return self.message


class UsedPointException(BoardException):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = "Shoot Used Point Exception"

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

    def shot(self, dot):  # стреляем в точку
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
                    return False
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
        print("-" * 20)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.board)
        print("-" * 20)

    def loop(self):
        num = 0
        while True:
            self.print_board()
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
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
        self.greet()
        self.loop()



###########


g = Game()
g.start()

# g = Game()
# g.size = 6
# print(g.random_board())


#
# ta = Dot(2, 3)
# tb = Dot(2, 3)
# tb.status = 1
# print(ta == tb)
#
# sh = Ship(ta, 4, 1)
# # print(sh.get_dots())
# # shdts = sh.get_dots()
# print(sh.dots)
# shdts = sh.dots
# for sh_d in shdts:
#     print(sh_d.x, sh_d.y, sh_d.status)
#
# print(tb in shdts)
# print(sh.dot_is_in_ship(tb))
#
# b = Board()
# # b.contour(sh)
# # b.contour(Ship(Dot(1, 2), 4, 0))
# b.add_ship(Ship(Dot(1, 2), 4, 0))
# b.add_ship(Ship(Dot(0, 0), 2, 0))
#
# print(b)
# print(b.busy_cells)

# a = input("Input positive integer: ")
# a=12
#
# try:
#     a = int(a)
#     if a < 0:
#         #raise BoardOutException("You give negative!")
#         raise BoardOutException("111")
# except ValueError:
#     print("Error type of value!")
# except BoardOutException as mr:
#     print("ERROR",mr)
# else:
#     print(a)

# l1 = [(1,1), (1,3), (3,2)]
# print((1,3) in l1)

# for i in range (len(l1)):
#     print(i)
