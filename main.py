import os
import sys
import threading
import logging
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QGraphicsPixmapItem, QLabel, \
    QTextEdit, QPushButton, QLineEdit, QGraphicsTextItem, QInputDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QPointF, QTimer
import sqlite3

class ChessPiece(QGraphicsPixmapItem):
    def __init__(self, color, piece_type):
        self.color = color  # Dodanie zmiennej przechowującej kolor figury
        self.chessboard = None  # Przechowaj referencję do szachownicy
        self.current_pos = None  # Przechowuje aktualną pozycję figury
        self.piece_type = piece_type
        pixmap_path = f"pionki/{piece_type}_{color}.png"
        pixmap = QPixmap(pixmap_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        super().__init__(pixmap)
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable)  # Ustawienie flagi, aby figura była możliwa do przesuwania

    def mousePressEvent(self, event):
        if self.chessboard.turn_label.text() == "White Turn" and self.color == "black":
            return
        if self.chessboard.turn_label.text() == "Black Turn" and self.color == "white":
            return
        self.setScale(1.25)  # Powiększenie obrazka podczas kliknięcia
        self.current_pos = self.pos()  # Zapisanie aktualnej pozycji figury

    def mouseReleaseEvent(self, event):
        self.setScale(1.0)  # Przywrócenie standardowej skali obrazka po puścięciu myszy
        new_pos = self.pos()
        if new_pos != self.current_pos:  # Sprawdzamy, czy figura została przesunięta na nową pozycję

            #usuniecie figury o przeciwnym kolorze na new_pos.x +20 new_pos.y +20 jesli istnieje
            items = self.scene().items(QPointF(new_pos.x() + 20, new_pos.y() + 20))
            piece = next((item for item in items if isinstance(item, ChessPiece)), None)
            if piece:
                if piece.color != self.color:
                    self.scene().removeItem(piece)
                    if piece.piece_type == "king":
                        self.chessboard.game_over(self.color)
                        return
            #wypisanie ruchu w logach w foramcie np. "a2 a4"
            col_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
            row_map = {0: '8', 1: '7', 2: '6', 3: '5', 4: '4', 5: '3', 6: '2', 7: '1'}
            move = col_map[int(self.current_pos.x()/50)] + row_map[int(self.current_pos.y()/50)] + " to " + col_map[int(new_pos.x()/50)] + row_map[int(new_pos.y()/50)]
            #zapisanie histori
            self.chessboard.history(move)

            self.current_pos = new_pos
            if self.color == "white":
                self.chessboard.turn_label.setText("Black Turn")
                if self.chessboard.mode=="3min":
                    self.chessboard.white_seconds += 3
                    self.chessboard.update_time_label(self.chessboard.white_time_label, self.chessboard.white_seconds)
                elif self.chessboard.mode=="10min":
                    self.chessboard.white_seconds += 10
                    self.chessboard.update_time_label(self.chessboard.white_time_label, self.chessboard.white_seconds)
            else:
                self.chessboard.turn_label.setText("White Turn")
                if self.chessboard.mode=="3min":
                    self.chessboard.black_seconds += 3
                    self.chessboard.update_time_label(self.chessboard.black_time_label, self.chessboard.black_seconds)
                elif self.chessboard.mode=="10min":
                    self.chessboard.black_seconds += 10
                    self.chessboard.update_time_label(self.chessboard.black_time_label, self.chessboard.black_seconds)

    def mouseMoveEvent(self, event):
        if self.chessboard.turn_label.text() == "White Turn" and self.color == "black":
            return
        if self.chessboard.turn_label.text() == "Black Turn" and self.color == "white":
            return
        # Pobranie pozycji myszy
        new_pos = event.scenePos()

        # Zaokrąglenie pozycji do najbliższego punktu siatki planszy (50x50)
        new_x = round((new_pos.x()-25) / 50) * 50 + 25  # Dodanie połowy szerokości pola planszy
        new_y = round((new_pos.y()-25) / 50) * 50 + 25  # Dodanie połowy wysokości pola planszy

        # Sprawdzenie, czy nowa pozycja nie wychodzi poza granice planszy
        if 0 <= new_x < 400 and 0 <= new_y < 400 and self.check_valid_move(new_x, new_y):
            # Sprawdzenie, czy pole docelowe jest wolne
            items = self.scene().items(QPointF(new_x, new_y))
            if not any(isinstance(item, ChessPiece) and item.color == self.color for item in items):
                # Ustawienie nowej pozycji figury
                self.setPos(new_x - self.pixmap().width() / 2,
                            new_y - self.pixmap().height() / 2)  # Odpowiednie wycentrowanie figury



    def check_valid_move(self, new_x, new_y):
        # Implementacja zasad ruchu dla każdej figury
        if self.piece_type == "pawn":
            return self.check_pawn_move(new_x, new_y)
        elif self.piece_type == "rook":
            return self.check_rook_move(new_x, new_y)
        elif self.piece_type == "knight":
            return self.check_knight_move(new_x, new_y)
        elif self.piece_type == "bishop":
            return self.check_bishop_move(new_x, new_y)
        elif self.piece_type == "queen":
            return self.check_queen_move(new_x, new_y)
        elif self.piece_type == "king":
            return self.check_king_move(new_x, new_y)

    def check_pawn_move(self, new_x, new_y):
        # Implementacja zasad ruchu dla piona
        return True

    def check_rook_move(self, new_x, new_y):
        # Implementacja zasad ruchu dla wieży
        return True  # Na potrzeby testu zwrócono True

    def check_knight_move(self, new_x, new_y):
        # Implementacja zasad ruchu dla skoczka
        return True  # Na potrzeby testu True

    def check_bishop_move(self, new_x, new_y):
        # Implementacja zasad ruchu dla gońca
        return True  # Na potrzeby testu zwrócono True

    def check_queen_move(self, new_x, new_y):
        # Implementacja zasad ruchu dla królowej
        return True  # Na potrzeby testu zwrócono True

    def check_king_move(self, new_x, new_y):
        # Implementacja zasad ruchu dla króla
        return True  # Na potrzeby testu zwrócono True

class Chessboard(QGraphicsView):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setWindowTitle("Szachy")
        self.setSceneRect(0, 0, 400, 400)  # Ustawienie rozmiaru planszy
        self.draw_board()
        self.add_pieces()
        self.add_turn_label()  # Dodanie etykiety z informacją o kolejce
        self.black_time_label = self.add_time_label("Black Time", 650, 250)
        self.white_time_label = self.add_time_label("White Time", 650, 350)
        self.black_timer = QTimer(self)
        self.white_timer = QTimer(self)
        self.black_timer.timeout.connect(self.decrement_black_time)
        self.white_timer.timeout.connect(self.decrement_white_time)
        self.start_black_timer()
        self.start_white_timer()
        self.time_button3 = QPushButton("Set Time: 3+3", self)
        self.time_button10 = QPushButton("Set Time: 10+15", self)
        self.reset_button = QPushButton("RESET", self)
        self.history_load = QPushButton("Load History", self)
        self.reset_button.clicked.connect(self.reset_board)
        self.time_button3.move(250, 50)
        self.history_load.move(650, 15)
        self.time_button10.move(450, 50)
        self.reset_button.move(350, 15)
        self.history_load.clicked.connect(self.load_history)
        self.time_button3.clicked.connect(self.set_time_3min)
        self.time_button10.clicked.connect(self.set_time_10min)
        # Dodajemy pole tekstowe dla wprowadzania ruchów
        self.move_input = QLineEdit(self)
        self.move_input.setGeometry(300, 525, 200, 30)
        self.move_input.returnPressed.connect(self.handle_move_input)
        self.mode="3min"
        #dwa radio buttony wybor gry czy vs gracz czy vs komputer
        self.vs_player = QPushButton("VS Player", self)
        self.vs_player.move(50, 50)
        self.vs_player.clicked.connect(self.vs_player_click)
        self.vs_computer = QPushButton("VS Computer", self)
        self.vs_computer.move(50, 100)
        self.vs_computer.clicked.connect(self.vs_computer_click)
        self.vs_player.click()
        #przycisk zapisz ustawienia
        self.save_settings = QPushButton("Save Settings", self)
        self.save_settings.move(50, 150)
        self.save_settings.clicked.connect(self.save_settings_click)
        #przycisk wczytaj ustawienia
        self.load_settings = QPushButton("Load Settings", self)
        self.load_settings.move(50, 200)
        self.load_settings.clicked.connect(self.load_settings_click)

    def save_settings_click(self):
        #zapisanie ustawien do pliku jsnon
        with open("settings.json", "w") as file:
            #czas gry
            file.write(f'{{"mode": "{self.mode}"}}')
            file.write("\n")
            #czy vs gracz czy komputer
            if self.vs_player.isEnabled():
                file.write(f'{{"vs": "player"}}')
            else:
                file.write(f'{{"vs": "computer"}}')
            file.write("\n")
            #adres ip i port
            file.write(f'{{"ip": "{self.parent().ip}"}}')
            file.write("\n")
            file.write(f'{{"port": "{self.parent().port}"}}')
            file.write("\n")

        #zamkniecie pliku
        file.close()
        #wyswietlenie komunikatu
        self.logger.info("Settings saved")



    def load_settings_click(self):
        #wczytanie ustawien z pliku json
        with open("settings.json", "r") as file:
            for line in file:
                #wyswietlenie zawartosci linii
                self.logger.info(line)
                #sprawdzenie czy linia zawiera mode
                if "mode" in line:
                    #jesli w lini wystepuje "3min" to ustaw czas na 3 minuty
                    if "3min" in line:
                        self.set_time_3min()
                    #jesli w lini wystepuje "10min" to ustaw czas na 10 minut
                    elif "10min" in line:
                        self.set_time_10min()
                #sprawdzenie czy linia zawiera vs
                if "vs" in line:
                    #jesli w lini wystepuje "player" to ustaw gre vs player
                    if "player" in line:
                        self.vs_player_click()
                    #jesli w lini wystepuje "computer" to ustaw gre vs computer
                    elif "computer" in line:
                        self.vs_computer_click()
                #odczytanie ip
                if "ip" in line:
                    self.parent().ip = line.split('"')[3]
                #odczytanie portu
                if "port" in line:
                    self.parent().port = line.split('"')[3]

        #reset plnaszy
        self.reset_board()
        #zamkniecie pliku
        file.close()
        #wyswietlenie komunikatu
        self.logger.info("Settings loaded")

    def vs_player_click(self):
        self.vs_player.setStyleSheet("background-color: lightgreen")
        self.vs_computer.setStyleSheet("background-color: white")
        self.vs_player.setEnabled(False)
        self.vs_computer.setEnabled(True)

    def vs_computer_click(self):
        self.vs_computer.setStyleSheet("background-color: lightgreen")
        self.vs_player.setStyleSheet("background-color: white")
        self.vs_computer.setEnabled(False)
        self.vs_player.setEnabled(True)

    def load_history(self):
        #wyskakujace okienko z polem do wpisania textu nazwy pliku z hisoria gry
        text, ok = QInputDialog.getText(self, 'Load History', 'Enter file name:')
        #zapisz fale name do zmiennej
        file_name = text
        #dodanie .xml
        if not file_name.endswith(".xml"):
            file_name = file_name + ".xml"

        #reset planszy
        self.reset_board()

        #jezeli taki plik istnieje
        if os.path.exists(file_name):
            # wczytanie histori z pliku i dodanie
            with open(file_name, "r") as file:
                for line in file:
                    #odczytanie ruchy "a2 to a4" jako "a2 a4, ignorowanie <move> oraaz </move> oraz " to "
                    move = line.replace("<move>", "").replace("</move>", "").strip()
                    move = move.replace(" to ", " ")
                    self.process_move(move)

            #zamkniecie pliku
            file.close()
        else:
            self.logger.warning("File not found")

    def game_over(self, winner_color):
        self.black_timer.stop()
        self.white_timer.stop()
        self.logger.info(f"Game over. The winner is {winner_color}.")
        # zapisanie histori
        with open("game_history.xml", "a") as file:
            file.write('</game>\n')
        # zapisanie histori do bazy danych
        conn = sqlite3.connect('game_history.db')
        c = conn.cursor()
        c.execute("INSERT INTO game_history VALUES (?)", ("game over",))
        conn.commit()
        conn.close()


    def draw_board(self):
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for row in range(8):
            for col in range(8):
                x = col * 50
                y = row * 50
                color = Qt.white if (row + col) % 2 == 0 else Qt.gray
                square = self.scene.addRect(x, y, 50, 50, brush=color)
                square.setZValue(-1)

                # Dodanie etykiet liter na górze planszy
                if row == 0:
                    label = QGraphicsTextItem(letters[col])
                    label.setPos(x + 20, y - 20)
                    self.scene.addItem(label)

                # Dodanie etykiet cyfr po lewej stronie planszy
                if col == 0:
                    label = QGraphicsTextItem(str(8 - row))
                    label.setPos(x - 30, y + 20)
                    self.scene.addItem(label)

    def add_pieces(self):
        pieces_order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]

        # Dodawanie pionków czrnych
        for col in range(8):
            black_pawn = ChessPiece("black", "pawn")
            black_pawn.setPos(col * 50 + 5, 1 * 50 + 5)  # Pozycja figury na planszy
            black_pawn.chessboard = self  # Przypisanie referencji do szachownicy
            self.scene.addItem(black_pawn)

        # Dodawanie pionków white
        for col in range(8):
            white_pawn = ChessPiece("white", "pawn")
            white_pawn.setPos(col * 50 + 5, 6 * 50 + 5)  # Pozycja figury na planszy
            white_pawn.chessboard = self  # Przypisanie referencji do szachownicy
            self.scene.addItem(white_pawn)

        # Dodawanie pozostałych figurek
        for col, piece_type in enumerate(pieces_order):
            black_piece = ChessPiece("black", piece_type)
            black_piece.setPos(col * 50 + 5, 0 * 50 + 5)  # Pozycja figury na planszy
            black_piece.chessboard = self  # Przypisanie referencji do szachownicy
            self.scene.addItem(black_piece)

            white_piece = ChessPiece("white", piece_type)
            white_piece.setPos(col * 50 + 5, 7 * 50 + 5)  # Pozycja figury na planszy
            white_piece.chessboard = self  # Przypisanie referencji do szachownicy
            self.scene.addItem(white_piece)

    #obsługa przycisku zmiany czasu
    def set_time_3min(self):
        self.mode="3min"
        self.black_seconds = 180
        self.white_seconds = 180
        self.update_time_label(self.black_time_label, self.black_seconds)
        self.update_time_label(self.white_time_label, self.white_seconds)
        self.black_timer.start(1000)
        self.white_timer.start(1000)

    def set_time_10min(self):
        self.mode="10min"
        self.black_seconds = 600
        self.white_seconds = 600
        self.update_time_label(self.black_time_label, self.black_seconds)
        self.update_time_label(self.white_time_label, self.white_seconds)
        self.black_timer.start(1000)
        self.white_timer.start(1000)

    def handle_move_input(self):
        move_text = self.move_input.text().strip()
        if move_text:
            self.process_move(move_text)
        self.move_input.clear()

    def reset_board(self):
        # Usunięcie wszystkich elementów ze sceny
        self.scene.clear()
        # usuniecie histori poprzedniej gry
        try:
            os.remove("game_history.xml")
        except:
            pass
        # utworzenie nowego pliku xml z historia gry
        with open("game_history.xml", "w") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<game>\n')

        #usuniecie bazy danych jesli istnieje
        try:
            os.remove("game_history.db")
        except:
            pass
        # utworzenie bazy danych z historia gry sqlite3
        conn = sqlite3.connect('game_history.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE game_history (move text)''')
        conn.commit()
        conn.close()

        # Ponowne narysowanie planszy i dodanie pionków
        self.draw_board()
        self.add_pieces()
        self.turn_label.setText("White Turn")
        self.logger.info("Start")
        if self.mode == "3min":
            self.set_time_3min()
        elif self.mode == "10min":
            self.set_time_10min()

    def process_move(self, move):
        # Sprawdź, czy ruch został wprowadzony w poprawnej notacji szachowej (np. "d4")
        if (len(move) == 5 and ((move[0] and move [3]) in 'abcdefgh') and ((move[1] and move[4]) in '12345678')):
            col_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
            row_map = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}

            #sprawdz czy na move 1 0 znajduje sie figura gracza z akutalna tura
            items = self.scene.items(QPointF(col_map[move[0]]*50 + 25, row_map[move[1]]*50 + 25))
            piece = next((item for item in items if isinstance(item, ChessPiece)), None)
            if piece:
                if self.turn_label.text() == "White Turn" and piece.color == "black":
                    self.logger.warning("Invalid move. It's White's turn.")
                    return
                if self.turn_label.text() == "Black Turn" and piece.color == "white":
                    self.logger.warning("Invalid move. It's Black's turn.")
                    return
            else:
                self.logger.warning("Invalid move. The selected square is empty.")
                return

            #sprawdz czy na move 3 4 znajduje sie figura gracza z akutalna tura
            items = self.scene.items(QPointF(col_map[move[3]]*50 + 25, row_map[move[4]]*50 + 25))
            piece = next((item for item in items if isinstance(item, ChessPiece)), None)
            if piece:
                if self.turn_label.text() == "White Turn" and piece.color == "white":
                    self.logger.warning("Invalid move.")
                    return
                if self.turn_label.text() == "Black Turn" and piece.color == "black":
                    self.logger.warning("Invalid move.")
                    return
                else:
                    self.scene.removeItem(piece)
                    #zbity krol to koniec gry
                    if piece.piece_type == "king":
                        if self.turn_label.text() == "White Turn":
                            winner = "White"
                        else:
                            winner = "Black"
                        self.game_over(winner)
                        return

            # przesun figure na nowa pozycje z pozycji mobe 0 1 na pozycje move 3 4
            items = self.scene.items(QPointF(col_map[move[0]]*50 + 25, row_map[move[1]]*50 + 25))
            piece = next((item for item in items if isinstance(item, ChessPiece)), None)
            if piece:
                piece.setPos(col_map[move[3]]*50 + 5, row_map[move[4]]*50 + 5)
                # zapis histori
                self.history(move)

                #zmien ture
                if self.turn_label.text() == "White Turn":
                    self.turn_label.setText("Black Turn")
                else:
                    self.turn_label.setText("White Turn")

        else:
            self.logger.warning("Invalid move. Please use notation like (e.g., 'd2 d4').")

    def history(self, move):
        self.logger.info(move)
        # zapisanie histori do pliku xml
        with open("game_history.xml", "a") as file:
            file.write(f'<move>{move}</move>\n')
        # zapisanie histori do bazy danych
        conn = sqlite3.connect('game_history.db')
        c = conn.cursor()
        c.execute("INSERT INTO game_history VALUES (?)", (move,))
        conn.commit()
        conn.close()

    def add_turn_label(self):
        self.turn_label = QLabel("White Turn", self)
        self.turn_label.move(75, 250)  # Ustawienie pozycji etykiety

    def add_time_label(self, text, x, y):
        time_label = QLabel(text, self)
        time_label.move(x, y)
        return time_label

    def start_black_timer(self):
        self.black_seconds = 180  # 3 minutes
        self.black_timer.start(1000)  # Start the timer with a 1 second interval

    def start_white_timer(self):
        self.white_seconds = 180  # 3 minutes
        self.white_timer.start(1000)  # Start the timer with a 1 second interval

    def decrement_black_time(self):
        if self.turn_label.text() == "Black Turn":
            self.black_seconds -= 1
            self.update_time_label(self.black_time_label, self.black_seconds)
            if self.black_seconds == 0:
                self.black_timer.stop()

    def decrement_white_time(self):
        if self.turn_label.text() == "White Turn":
            self.white_seconds -= 1
            self.update_time_label(self.white_time_label, self.white_seconds)
            if self.white_seconds == 0:
                self.white_timer.stop()

    def update_time_label(self, label, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        label.setText(f"{minutes:02}:{seconds:02}")

class ThreadSafeLogger(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.setReadOnly(True)
        self.text_widget.setFontPointSize(10)
        self.mutex = threading.Lock()

    def emit(self, record):
        self.mutex.acquire()
        msg = self.format(record)
        self.text_widget.append(msg)
        self.mutex.release()

class LogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 300, 500)  # Ustawienie rozmiaru okna logów
        self.setWindowTitle("Game Log")
        self.logger_widget = QTextEdit(self)
        self.logger_widget.setGeometry(10, 10, 280, 480)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 600)  # Ustawienie rozmiaru okna głównego
        self.logger_window = LogWindow()  # Dodanie okna logów
        self.logger = logging.getLogger('ChessLogger')
        self.logger.setLevel(logging.DEBUG)
        handler = ThreadSafeLogger(self.logger_window.logger_widget)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.chessboard = Chessboard(self.logger)
        self.setCentralWidget(self.chessboard)

        self.ip = None
        self.port = None

        # dodanie okienko do wpisania adresu ip i portu
        self.ipinput()

        #wypisz adres i ip w logach
        self.logger.info(f"IP: {self.ip}")
        self.logger.info(f"Port: {self.port}")

        # Testowy komunikat "Start" na początku gry (zachowanie threadsafety)
        self.log_message("Start")
        # utworzenie nowego pliku xml z historia gry
        try:
            os.remove("game_history.xml")
        except:
            pass
        with open("game_history.xml", "w") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<game>\n')
        # utworzenie bazy danych z historia gry sqlite3
        try:
            os.remove("game_history.db")
        except:
            pass
        # utworzenie bazy danych z historia gry sqlite3
        conn = sqlite3.connect('game_history.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE game_history (move text)''')
        conn.commit()
        conn.close()

    def log_message(self, message):
        self.logger.info(message)

    def ipinput(self):
        #wyskakujace okienko z dwoma polami, jedno do adresu ip i jedno do portu
        text, ok = QInputDialog.getText(None, 'IP Address', 'Enter IP Address:')
        #zapisz adres ip do zmiennej
        self.ip = text
        #jesli ok to zapytaj o port
        if ok:
            text, ok = QInputDialog.getText(None, 'Port', 'Enter Port:')
            #zapisz port do zmiennej
            self.port = text


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.logger_window.show()  # Pokazanie okna logów
    window.show()
    sys.exit(app.exec_())
