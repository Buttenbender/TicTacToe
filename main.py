import os
import socket

def print_board(board):
    os.system("cls" if os.name == "nt" else "clear")

    print("\n")
    for i in range(3):
        print(" " + board[i*3] + " | " + board[i*3+1] + " | " + board[i*3+2])
        if i < 2:
            print("---+---+---")
    print()

WINS = [
   (0, 1, 2), (3, 4, 5), (6, 7, 8),
   (0, 3, 6), (1, 4, 7), (2, 5, 8),
   (0, 4, 8), (2, 4, 6),
]

def Winner(board):
    for a, b, c in WINS:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None

def valid_position(board, row, column):
    if not (0 <= row <= 2 and 0 <= column <= 2):
        return None
    
    index = row * 3 + column

    if board[index] != " ":
        return None
    return index

def read_local_play(board):
    while True:
        try:
            entry = input("Your turn - row and column (ex: 1 2): ")
            row, column = map(int, entry.split())
        except ValueError:
            print("Enter two numbers separated by a Space (ex: 1 2)!")
            continue

        if not (0 <= row <= 2 and 0 <= column <= 2):
            print("Play out of bounds (use 0 to 2)!")
            continue

        index = valid_position(board, row, column)

        if index is None:
            print("Position already ocupied, try another one!")
            continue
        return row, column, index

def play(connection, client_symbol):
    board = [" "] * 9
    turn = "X"
    reader = connection.makefile("r", encoding="utf-8", newline="\n")

    try:
        while True:
            print_board(board)

            if turn == client_symbol:
                row, column, index = read_local_play(board)
                try:
                    connection.sendall(f"{row},{column}\n".encode())
                except OSError:
                    print("\nConnection with opponent ended...")
                    return
                board[index] = client_symbol
            else:
                print(f"Waiting for opponent's play ({turn})...")
                try:
                    message = reader.readline()
                except OSError:
                    message = ""

                if not message:
                    print("\nConnection with opponent ended...")
                    return

                try:
                    text_row, text_column = message.strip().split(",")
                    row, column = int(text_row), int(text_column)
                except ValueError:
                    print("\nInvalid message received. Ending the match...")
                    return

                index = valid_position(board, row, column)

                if index is None:
                    print("\nInvalid move received from the opponent. Ending the match...")
                    return

                board[index] = turn
                print(f"Opponent ({turn}) played in row {row}, column {column}.")

            winner = Winner(board)
            if winner is not None:
                print_board(board)

                if winner == client_symbol:
                    print("You won!")
                else:
                    print("You lost!")

                return

            if " " not in board:
                print_board(board)
                print("Tie!")
                return

            turn = "O" if turn == "X" else "X"
    finally:
        reader.close()

def find_local_IP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()

def create_match():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", 5000))
        server.listen()

        print("Match created! Waiting for an opponent...")
        print(f"Inform this IP address to the other player: {find_local_IP()}")
        print("Port number: 5000")

        conn, addr = server.accept()
        print(f"Opponent connected: {addr[0]}")

        return conn
    except OSError as error:
        print(f"Unable to create match: {error}")
        return None
    finally:
        server.close()

def join_match():
    ip = input("Enter the computer's IP (or 0 to return to the menu): ").strip()

    if ip == "0":
        return None

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.settimeout(5)
        client.connect((ip, 5000))
        client.settimeout(None)

        print("Connected to the match!")
        return client
    except OSError as error:
        print("Unable to join match: {error}")
        client.close()
        return None

def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")

        print("=== Tic Tac Toe ===")
        print(" 1) Create match")
        print(" 2) Join match")
        print(" 3) Exit")
        pick = input("Pick an option: ")

        os.system("cls" if os.name == "nt" else "clear")

        if pick == "1":
            connection = create_match()

            if connection is not None:
                print("Connection established!")
                play(connection, "X")
                connection.close()

        elif pick == "2":
            connection = join_match()
            
            if connection is not None:
                print("Connection established!")
                play(connection, "O")
                connection.close()

        elif pick == "3":
            print("Exiting...")
            break

        else:
            print("Invalid option!")

        input("Press Enter to return to the menu...")

main()