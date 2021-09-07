#bbot_main.py
from bbot_game import *
from bbot_engine import *
import time



USER_PLAYER = True #cmp vs cmp if false
USER_TURN = 0 #0 if white, 1 if black
SHOW_LINE = False #if true, show full line. will not play game
DEPTH = 3
TIME_LIMIT = 120 #s to complete for cmp

PIECES = [
	#white
	Piece(0, 4, 0, 0), Piece(0, 5, 0, 0), #r1
	Piece(1, 3, 1, 0), Piece(2, 4, 1, 0), Piece(2, 5, 1, 0), Piece(1, 6, 1, 0), #r2

	#black
	Piece(1, 3, 8 , 1), Piece(2, 4, 8, 1), Piece(2, 5, 8, 1), Piece(1, 6, 8, 1), #r9
	Piece(0, 4, 9, 1), Piece(0, 5, 9, 1) #r10
]



def main():
	game = Game(PIECES, USER_TURN if USER_PLAYER else 0)
	print(game)
	print("Start")
	bot = Bbot(game)

	if SHOW_LINE:
		time_start = time.perf_counter()
		value, moves = bot.calculate(DEPTH, TIME_LIMIT)
		time_complete = time.perf_counter() - time_start

		for i in range(len(moves)):
			m = moves[i]
			s = str(m[0])
			bot.movePiece(m)
			print(game)
			s = str((game.move_count - 1) // 2 + 1) + ". "
			if game.move_count % 2 == 0: s += bot.log_notated[-2] + ", "
			s += bot.log_notated[-1]
			print(s)
		
		print("{0:+d}".format(value) + ", " + str(time_complete) + "s")
		return
	
	while game.isWon() == 0:
		if USER_PLAYER and game.turn == USER_TURN:
			move = None
			time_start = time.perf_counter()

			while move == None:
				move = bot.notationToMove(input("Your move: "))

			time_complete = time.perf_counter() - time_start
		else:
			time_start = time.perf_counter()
			value, moves = bot.calculate(DEPTH, TIME_LIMIT)
			time_complete = time.perf_counter() - time_start
			move = moves[0]

		bot.movePiece(move)
		print(game)
		s = str((game.move_count - 1) // 2 + 1) + ". "
		if game.move_count % 2 == 0: s += bot.log_notated[-2] + ", "
		s += bot.log_notated[-1]
		print(s)
		s = ""
		if not USER_PLAYER or game.turn == USER_TURN: s = "{0:+d}".format(value) + ", "
		print(s + str(time_complete) + "s")
	else:
		if game.isWon() == 1:
			print("White wins.")
		else:
			print("Black wins.")



if __name__ == "__main__":
    main()