#bbot_engine
from bbot_game import *
import math
import time


REPEAT_MAX = 2 #if move played x times
REPEAT_SEARCH = 13 #in the last y turns, prohibit



class Bbot:
	REPEAT_MAX = REPEAT_MAX
	REPEAT_SEARCH = REPEAT_SEARCH

	def __init__(self, start):
		self.game = start
		self.depth = None
		self.log = []
		self.log_notated = []
		self.prohibited = []


	def calculate(self, depth, time_limit):
		self.depth = depth
		self.time_limit = time_limit 
		self.time_start = time.perf_counter()
		#check if move played twice within last x turns. if so, prohibit
		self.rep_count = []
		for m in self.log[-Bbot.REPEAT_SEARCH:]:
			found = False
			for n in self.rep_count:
				if m[0] == n[0][0] and m[1] == n[0][1] and m[2] == n[0][2]:
					n[1] += 1
					found = True
			if not found:
				self.rep_count.append([m, 1])

		v, c = self.alphabeta(self.game, depth, -math.inf, math.inf)
		return v, c


	def moveNotation(m):
		return str(m[0]) + alphabet[m[1]] + str(m[2] + 1)


	def notationToMove(self, s):
		try:
			p = None
			s = list(s)

			if len(s) > 7:
				print("Invalid input.")
				return None

			for i in range(1, len(s)):
				if s[i] == "0":
					s[i - 1] += "0"
					del s[i]

			x1 = alphabet.index(s[1])
			y1 = int(s[2]) - 1


			for q in self.game.pieces:
				if q.char == s[0].lower() and q.x == x1 and q.y == y1:
					p = q

			if p == None:
				print("Invalid input.")
				return None

			moves = self.game.getMoves()
			x2 = alphabet.index(s[3])
			y2 = int(s[4]) - 1

			for m in moves:
				if m[0] == p:
					for i in range(1, len(m)):
						if m[i][0] == x2 and m[i][1] == y2:
							return [p, m[i][0], m[i][1]]

			print("Invalid input.")
			return None

		except:
			print("Invalid input.")
			return None


	def movePiece(self, m):
		self.log_notated.append(Bbot.moveNotation(m))
		self.game.movePiece(m, False)
		self.log.append(m)
		

	def alphabeta(self, g, depth, alpha, beta):
		if depth == 0 or g.isWon() != 0 or time.perf_counter() - self.time_start > self.time_limit:
			return g.evaluate(), []

		best_c = None
		best_cl = []
		sm = 1 - 2 * g.turn
		maxV = -math.inf * sm

		for m in g.getMoves():
			if len(m) <= 1:
				continue

			p = m[0]
			old = [p, p.x, p.y]

			for i in range(1, len(m)):
				c = [p, m[i][0], m[i][1]]

				if depth == self.depth:
					prohibited = False

					for n in self.rep_count:
						if c[0] == n[0][0] and c[1] == n[0][1] and c[2] == n[0][2] and n[1] >= Bbot.REPEAT_MAX:
							prohibited = True

					if prohibited:
						continue

				g.movePiece(c, False)
				v, cl = self.alphabeta(g, depth - 1, alpha, beta)
				if v * sm > maxV * sm:
					maxV = v
					best_c = c
					best_cl = cl
				g.movePiece(old, False) #undo move
				g.move_count -= 2
				if g.turn:
					beta = min(beta, v)
				else:
					alpha = max(alpha, v)
				if beta <= alpha: break

		return int(maxV * 0.9), [best_c] + best_cl

				 


