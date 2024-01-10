from random import randint


# Базовое исключение для доски
class BoardError(Exception):
    pass


# Исключение для ситуации, когда корабль выходит за пределы доски
class IsOut(BoardError):
    pass


# Исключение для ситуации, когда координаты выходят за пределы доски
class BoardOut(BoardError):
    def __str__(self):
        return 'Такой координаты нет, измени её!'


# Исключение для ситуации, когда в ячейку уже стреляли
class CellIsBusy(BoardError):
    def __str__(self):
        return 'В это поле уже стреляли, измени координату!'


# Класс для представления точки на доске
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


# Класс для представления корабля
class Ship:
    def __init__(self, bow, orientation, length,):
        self.bow = bow
        self.orientation = orientation
        self.length = length
        self.lives = length

    @property
    def dots(self):
        ship_dots, x, y = [], self.bow.x, self.bow.y
        for i in range(self.length):
            if self.orientation == 0:
                ship_dots.append(Dot(x+i, y))
            else:
                ship_dots.append(Dot(x, y+i))
        return ship_dots

    def shot(self, shot_dot):
        return shot_dot in self.dots


# Класс для представления доски
class Board:
    def __init__(self, visible=True, size=6):
        self.visible = visible
        self.size = size
        self.cells = [["O"] * self.size for _ in range(self.size)]
        self.busy_cells = []  # Список координат, в которые уже стреляли
        self.ships = []  # Список кораблей на доске
        self.count = 0  # Количество потопленных кораблей

    def __str__(self):
        field = '   '
        for i in range(1, self.size + 1):
            field += f' {i} |'
        for i, j in enumerate(self.cells):
            field += f'\n{i + 1} | ' + ' | '.join(j) + ' |'
        if not self.visible:
            field = field.replace('■', 'O')  # Заменяем символы для невидимой доски
        return field

    # Добавление корабля на доску
    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy_cells:
                raise IsOut()
        for dot in ship.dots:
            self.cells[dot.x][dot.y] = "■"
            self.busy_cells.append(dot)
        self.ships.append(ship)
        self.area(ship)

    # Проверка, выходит ли точка за пределы доски
    def out(self, dot):
        return not (0 <= dot.x < self.size) or not (0 <= dot.y < self.size)

    # Расстановка области вокруг корабля
    def area(self, ship, ship_is_killed=False):
        area_staff_list = [[-1, 0], [0, -1], [0, 1], [1, 0], [-1, -1], [1, -1], [1, 1], [-1, 1]]
        for ship_dot in ship.dots:
            for area_dot_x, area_dot_y in area_staff_list:
                cur_dot = Dot(ship_dot.x + area_dot_x, ship_dot.y + area_dot_y)
                if not self.out(cur_dot) and cur_dot not in self.busy_cells:
                    if ship_is_killed:
                        self.cells[cur_dot.x][cur_dot.y] = 'X'
                    self.busy_cells.append(cur_dot)

    # Выстрел по доске
    def shot(self, shot_dot):
        if self.out(shot_dot):
            raise BoardOut()
        if shot_dot in self.busy_cells:
            raise CellIsBusy()
        for ship in self.ships:
            if shot_dot in ship.dots:
                self.cells[shot_dot.x][shot_dot.y] = '*'
                self.busy_cells.append(shot_dot)
                ship.lives -= 1
                if ship.lives == 0:
                    self.area(ship, ship_is_killed=True)
                    print('Корабль убит')
                    return True
                else:
                    print('Корабль подбит')
                    return True
        self.busy_cells.append(shot_dot)
        self.cells[shot_dot.x][shot_dot.y] = 'X'
        return False

    # Сброс состояния доски перед новой игрой
    def rest(self):
        self.busy_cells = []


# Класс для представления игрока
class Player:
    def __init__(self, player_board, enemy_board):
        self.player_board = player_board
        self.enemy_board = enemy_board

    # Метод для выполнения хода
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardError as e:
                print(e)

    # Метод для запроса хода у игрока
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


# Класс для представления компьютера (ИИ)
class PC(Player):
    # Метод для генерации случайного хода компьютера
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


# Класс для представления пользователя
class User(Player):
    # Метод для запроса хода у пользователя
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# Класс для представления игры
class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.visible = False

        self.pc = PC(co, pl)
        self.us = User(pl, co)

    # Генерация случайной доски
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    # Размещение кораблей на доске
    def random_place(self):
        ships_length = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        for length in ships_length:
            while True:
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), randint(0, 1), length)
                try:
                    board.add_ship(ship)
                    break
                except IsOut:
                    pass
        board.rest()
        return board

    # Приветствие игрока
    @staticmethod
    def show_info():
        print("\nМорской бой - это классическая игра на морскую тематику")
        print("Цель игры - потопить все корабли противника")
        print("Игровое поле представляет собой квадратную доску размерами 6x6")
        print("Формат ввода координат: x y, где x - номер строки, y - номер столбца")
        print("Корабли различной длины размещаются случайным образом на доске")
        print("Игроки поочередно делают выстрелы, пытаясь попасть в корабли противника")
        print("Побеждает тот, кто первым потопит все корабли противника\nУдачи, боец!\n")

    # Основной игровой цикл
    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Ваша доска")
            print(self.us.player_board)
            print("-" * 20)
            print("Доска компьютера")
            print(self.pc.player_board)
            print("-" * 20)
            print("Ваш ход, ждем" if num % 2 == 0 else "Ходит компьютер")
            try:
                repeat = self.us.move() if num % 2 == 0 else self.pc.move()
                if repeat:
                    num -= 1
            except BoardError as e:
                print(e)

            if self.pc.player_board.count == 7:
                print("-" * 20)
                print("Вы выиграли!")
                break

            if self.us.player_board.count == 7:
                print("-" * 20)
                print("Вы проиграли!")
                break

            num += 1

    # Запуск игры
    def start(self):
        print("Управление:")
        print(" 1 - Справка")
        print(" 2 - Начать игру")
        print(" 3 - Выход")
        choice = input("Выберите действие (1/2/3): ")

        if choice == "1":
            self.show_info()
            self.start()  # Возврат в меню после просмотра информации
        elif choice == "2":
            self.loop()
        elif choice == "3":
            print("Выход из игры. До свидания!")
        else:
            print("Некорректный выбор. Пожалуйста, выберите 1, 2 или 3.")
            self.start()


# Создание объекта игры и запуск
game = Game()
game.start()
