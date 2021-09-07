#bbot_game
import math



#board
WIDTH = 10
HEIGHT = 10
WH_DISTANCE = 1 #from center
PIECE_CHARS = ["e", "l", "m"]

#scoring
WIN_SCORE = 10000
WH_VALUE = 200
DOUBLE_WH_VALUE = 500
TILE_VALUES = [40, 20, 10, 2, 1] #center to border

OCCUPIED_MULT = 10
THREAT_MULT = -1 #* tile value for every piece threatened
THREATENED_MULT = 0 #score mult for threatened tiles seen



alphabet = list("abcdefghijklmnopqrstuvwxyz")

class Piece:
	def __init__(self, t, x, y, side):
		self.t = t #type: 0 = e, 1 = l, 2 = m
		self.x = x
		self.y = y
		self.side = side #0 = white, 1 = black

		self.char = Game.piece_chars[t]
		self.on_wh = False
		self.moves_on_diagonal = (t == 0 or t == 1)
		self.moves_on_straight = (t == 0 or t == 2)
		self.vision = []

		self.threatens = []
		self.threatened_by = []
		self.threatened = False
		self.threatening = False

		for i in range(4): #rows, columns, 2 diagonals
			self.vision.append([[], []])

	def __repr__(self):
		return self.char.upper() + alphabet[self.x] + str(self.y + 1)

	def isThreatenedBy(self, p):
		t = -1 if p.t == 2 else p.t
		if self.side != p.side:
			return self.t - t

	def updateThreats(self):
		self.threatened = False

		for p in self.threatened_by:
			if abs(self.x - p.x) <= 1 and abs(self.y - p.y) <= 1:
				self.threatened = True

		for a in self.vision:
			for b in a:
				for c in b:
					c[2] = 0
					for p in self.threatened_by:
						if abs(c[0] - p.x) <= 1 and abs(c[1] - p.y) <= 1:
							c[2] = 1



class Game:
	#board
	width = WIDTH
	height = HEIGHT
	wh_distance = WH_DISTANCE #from center
	piece_chars = PIECE_CHARS

	#scoring
	WIN_SCORE = WIN_SCORE
	WH_VALUE = WH_VALUE
	DOUBLE_WH_VALUE = DOUBLE_WH_VALUE
	TILE_VALUES = TILE_VALUES

	OCCUPIED_MULT = OCCUPIED_MULT
	THREAT_MULT = THREAT_MULT
	THREATENED_MULT = THREATENED_MULT

	def __init__(self, pieces, turn):
		self.pieces = pieces
		self.turn = turn
		self.wh_count = [0, 0]
		self.occupied = [[0] * Game.width for i in range(Game.height)]
		self.move_count = 0
		self.flip = turn != 0

		#watering holes
		cx = (Game.width - 1)/2
		cy = (Game.height - 1)/2
		self.wh_x1 = math.floor(cx - Game.wh_distance)
		self.wh_y1 = math.floor(cy - Game.wh_distance)
		self.wh_x2 = math.ceil(cx + Game.wh_distance)
		self.wh_y2 = math.ceil(cy + Game.wh_distance)
		self.wh = [[self.wh_x1, self.wh_y1], [self.wh_x2, self.wh_y1], [self.wh_x1, self.wh_y2], [self.wh_x2, self.wh_y2]]

		#sides
		self.white = []
		self.black = []

		for p in self.pieces:
			if p.side:
				self.black.append(p)
			else:
				self.white.append(p)

			for p2 in self.pieces:
				if p.isThreatenedBy(p2) == 1:
					p.threatened_by.append(p2)
				if p2.isThreatenedBy(p) == 1:
					p.threatens.append(p2)

		#score values for tiles
		self.value_table = []

		for i in range(Game.height):
			self.value_table.append([])

			for j in range(Game.width):
				#get value by dist from center
				self.value_table[i].append(self.TILE_VALUES[math.floor(max(abs(j - cx), abs(i - cy)))])

		
		for w in self.wh:
			self.value_table[w[1]][w[0]] = Game.WH_VALUE

		#slices
		#keep track of pieces on every...
		self.slices = [
			[[] for i in range(Game.height)], #row
			[[] for i in range(Game.width)], #col
			[[] for i in range(Game.width + Game.height - 1)], #diagonal
			[[] for i in range(Game.width + Game.height - 1)],
		]

		for p in self.pieces:
			self.movePiece([p, p.x, p.y], True)

		self.move_count = 0


	def __repr__(self): #display game in ascii
		a = []

		for i in range(Game.height):
			if (self.flip and i == Game.height - 1) or (not self.flip and i == 0):
				a.append([".__"] * Game.width)
			else:
				a.append([".  "] * Game.width)
			

		for w in self.wh:
			a[w[1]][w[0]] = "( )" #parens for wh

		for p in self.pieces:
			s = "(" if p.on_wh else "["
			s += p.char if p.side else p.char.upper() #put white in upper
			s += ")" if p.on_wh else "]"
			a[p.y][p.x] = s


		s = ""
		r = range(len(a) - 1, -1, -1) if self.flip else range(len(a))
		for i in r:
			s += "{:3d}".format(len(a) - i) + "|" + "".join(a[-i - 1]) + "\n"

		s += "    "
		for i in range(Game.width):
			s += " " + alphabet[i] + " "

		return s


	def onWH(self, p):
		return (p.x == self.wh_x1 or p.x == self.wh_x2) and (p.y == self.wh_y1 or p.y == self.wh_y2)


	def updateAllSlices(self, p, add):
		for i in range(4):
			self.updateSlice(p, i, add)


	#p (piece)
	#t (type): 0 - row, 1 - col, 2 - forward diagonal, 3 - backward diagonal
	#add: true if adding, false if removing
	def updateSlice(self, p, t, add):
		dx = 0
		dy = 0

		if t == 0:
			n = p.y
			dx = 1
		elif t == 1:
			n = p.x
			dy = 1
		elif t == 2:
			n = p.x - p.y + Game.height - 1
			dx = 1
			dy = 1
		elif t == 3:
			n = p.x + p.y
			dx = 1
			dy = -1


		if add: #check all pieces on slice and update vision
			for q in self.slices[t][n]:
				if not ((t <= 1 and q.moves_on_straight) or (t >= 2 and q.moves_on_diagonal)):
					continue
				if t == 1:
					if p.y < q.y and p.y >= q.y - len(q.vision[t][0]):
						q.vision[t][0] = []
						self.lookOnSlice(q, -dx, -dy, q.vision[t][0])
					if p.y > q.y and p.y <= q.y + len(q.vision[t][1]):
						q.vision[t][1] = []
						self.lookOnSlice(q, dx, dy, q.vision[t][1])
				else:
					if p.x < q.x and p.x >= q.x - len(q.vision[t][0]):
						q.vision[t][0] = []
						self.lookOnSlice(q, -dx, -dy, q.vision[t][0])
					if p.x > q.x and p.x <= q.x + len(q.vision[t][1]):
						q.vision[t][1] = []
						self.lookOnSlice(q, dx, dy, q.vision[t][1])
			self.slices[t][n].append(p)
			if (t <= 1 and p.moves_on_straight) or (t >= 2 and p.moves_on_diagonal):
				p.vision[t] = [[], []]
				self.lookOnSlice(p, -dx, -dy, p.vision[t][0])
				self.lookOnSlice(p, dx, dy, p.vision[t][1])
		else:
			self.slices[t][n].remove(p)
			for q in self.slices[t][n]:
				if not ((t <= 1 and q.moves_on_straight) or (t >= 2 and q.moves_on_diagonal)):
					continue
				if t == 1:
					if p.y < q.y and p.y == q.y - len(q.vision[t][0]) - 1:
						self.lookOnSlice(q, -dx, -dy, q.vision[t][0])
					if p.y > q.y and p.y == q.y + len(q.vision[t][1]) + 1:
						self.lookOnSlice(q, dx, dy, q.vision[t][1])
				else:
					if p.x < q.x and p.x == q.x - len(q.vision[t][0]) - 1:
						self.lookOnSlice(q, -dx, -dy, q.vision[t][0])
					if p.x > q.x and p.x == q.x + len(q.vision[t][1]) + 1:
						self.lookOnSlice(q, dx, dy, q.vision[t][1])
					

	#iterate across slice and add seen tiles to vision
	def lookOnSlice(self, p, dx, dy, a):
		x = p.x + max(len(a), 1) * dx
		y = p.y + max(len(a), 1) * dy

		while x >= 0 and x < Game.width and y >= 0 and y < Game.height:
			if self.occupied[y][x]: break
			threat = 0
			for p2 in p.threatened_by:
				if abs(x - p2.x) <= 1 and abs(y - p2.y) <= 1:
					threat = 1

			a.append([x, y, threat])

			x += dx
			y += dy


	def movePiece(self, m, new):
		p = m[0]
		x = m[1]
		y = m[2]

		if not new:
			self.occupied[p.y][p.x] = 0
			self.updateAllSlices(p, False)
			p.x = x
			p.y = y

			if p.on_wh:
				self.wh_count[p.side] -= 1

		#check if on WH
		p.on_wh = self.onWH(p)
		if p.on_wh:
			self.wh_count[p.side] += 1

		self.occupied[y][x] = 1
		self.updateAllSlices(p, True)
		p.updateThreats()

		for p2 in p.threatens:
			p2.updateThreats()

		self.turn = 1 - self.turn
		self.move_count += 1


	def getMoves(self):
		if self.turn:
			pieces = self.black
		else:
			pieces = self.white

		free = []
		forced = []
		forced_move = False

		for p in pieces:
			if not p.threatened:
				continue

			threatened = [p]
			unthreatened = [p]

			for a in p.vision:
				for b in a:
					for c in b:
						if c[2]:
							if len(unthreatened) == 1:
								threatened.append(c)
						else:
							unthreatened.append(c)


			if len(unthreatened) > 1:
				forced_move = True
				forced.append(unthreatened)
			elif len(threatened) > 1:
				free.append(threatened)

		if not forced_move:
			for p in pieces:
				if p.threatened:
					continue

				unthreatened = [p]

				for a in p.vision:
					for b in a:
						for c in b:
							if not c[2]:
								unthreatened.append(c)

				if len(unthreatened) > 1:
					free.append(unthreatened)

		return forced if forced_move else free


	def getPieceAt(self, x, y):
		for p in self.pieces:
			if p.x == x and p.y == y:
				return p

		return None


	#1 if white is won, -1 if black is won
	def isWon(self):
		if self.wh_count[0] >= 3:
			return 1
		elif self.wh_count[1] >= 3:
			return -1

		return 0


	def evaluate(self):
		s = 0

		w = self.isWon()
		if w != 0:
			return Game.WIN_SCORE * w

		for p in self.pieces:
			m = 1 - 2 * p.side
			
			if p.threatened:
				s += self.value_table[p.y][p.x] * Game.THREAT_MULT * m
			else:
				s += self.value_table[p.y][p.x] * Game.OCCUPIED_MULT * m
			
			for a in p.vision:
				for b in a:
					for c in b:
						s += self.value_table[c[1]][c[0]] * m * (Game.THREATENED_MULT if c[2] else 1)
		
		if self.wh_count[0] >= 2: s += Game.DOUBLE_WH_VALUE
		if self.wh_count[1] >= 2: s -= Game.DOUBLE_WH_VALUE

		return s




		








