#bbot_graphic_main
from bbot_game import *
from bbot_engine import *
import pygame as pg
import time



PLAYER_1 = True #true for user, false for bot
PLAYER_2 = False #true for user, false for bot
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

COLORS = {
	#board
	"tile_1": pg.Color(191, 212, 219),
	"tile_2": pg.Color(126, 183, 204),
	"text_1": pg.Color(221, 242, 249),
	"text_2": pg.Color(96, 153, 174),

	#highlights
	"vision": pg.Color(50, 50, 50),
	"last_move": pg.Color(255, 255, 100),
	"threatened": pg.Color(255, 0, 0),
	"won": pg.Color(0, 255, 0),

	#bar
	"bar": pg.Color(0, 0, 0),
	"bar_text": pg.Color(180, 180, 180),
	"bar_text_hl": pg.Color(255, 240, 180)
}

SCREEN_SIZE = (800, 1000)
BAR_HEIGHT = SCREEN_SIZE[1] - SCREEN_SIZE[0]
BAR_MARGIN = 20
BAR_FONT_SIZE = 24

COOR_MARGIN = 5
COOR_FONT_SIZE = 24
COOR_FONT_BOLD = False

HIGHLIGHT_OPACITY = 160
MAX_FPS = 60

image_names = ["wQ", "wB", "wR", "bQ", "bB", "bR"]



images = {}

def loadImages(w, h, file_names):
	w = int(w)
	h = int(h)

	for n in file_names:
		images[n] = pg.transform.scale(pg.image.load("images/" + str(n) + '.png'), (w, h))

def main():
	pg.init()
	running = True
	mouse_pressed = False
	user_control = False

	clock = pg.time.Clock()
	screen = pg.display.set_mode(SCREEN_SIZE)
	game = Game(PIECES, 0)
	bot = Bbot(game)
	board = Board(screen, bot)

	loadImages(board.sw, board.sh, image_names)

	if PLAYER_2 and not PLAYER_1:
		board.flip = True

	while running:
		clock.tick(MAX_FPS)
		board.mouse = pg.mouse.get_pos()

		user_control = (game.turn == 0 and PLAYER_1) or (game.turn == 1 and PLAYER_2)

		if PLAYER_1 and PLAYER_2: board.flip = game.turn

		if not user_control and game.isWon() == 0:
			value, moves = bot.calculate(DEPTH, TIME_LIMIT)
			board.playMove(moves[0], value)

		for e in pg.event.get():
			if e.type == pg.QUIT:
				running = False

			if not user_control or game.isWon() != 0:
				continue

			if e.type == pg.MOUSEBUTTONDOWN and not mouse_pressed and board.move_on_click == None:
				x, y = board.getMouseTile()
				p = game.getPieceAt(x, y)
				if p == None: continue
				if p.side != game.turn: continue
				mouse_pressed = True
				board.grabbed = p
				board.updateHighlights()

			if e.type == pg.MOUSEBUTTONUP:
				if board.mouse[1] > board.size[1]:
					board.click_bar = True

				if (not mouse_pressed or board.grabbed == None) and board.move_on_click == None:
					continue

				x, y = board.getMouseTile()

				if board.move_on_click == None:
					p = board.grabbed

					if x == p.x and y == p.y:
						board.move_on_click = p
				else:
					p = board.move_on_click
					board.move_on_click = None

				if board.tryMove(p, x, y): board.playMove([p, x, y], None)
				board.updateHighlights()
				board.grabbed = None
				mouse_pressed = False


			if e.type == pg.KEYDOWN:
				if e.key == pg.K_LEFT:
					board.currentView = max(board.currentView - 1, 0)
				
				if e.key == pg.K_RIGHT:
					board.currentView = min(board.currentView + 1, len(board.log) - 1)


		board.draw()
		pg.display.flip()

class Board:
	colors = COLORS
	tile_colors = [COLORS["tile_1"], COLORS["tile_2"]]
	text_colors = [COLORS["text_1"], COLORS["text_2"]]

	c_margin = COOR_MARGIN
	c_font_size = COOR_FONT_SIZE
	c_font_bold = COOR_FONT_BOLD

	b_height = BAR_HEIGHT
	b_margin = BAR_MARGIN
	b_font_size = BAR_FONT_SIZE

	highlight_opacity = HIGHLIGHT_OPACITY
	image_names = image_names

	def __init__(self, screen, engine):
		self.screen = screen
		self.engine = engine

		self.game = self.engine.game
		self.w = self.game.width
		self.h = self.game.height
		self.wh = self.game.wh

		self.size = (self.screen.get_width(), self.screen.get_width())
		self.sw = self.size[0] / self.w
		self.sh = self.size[1] / self.h

		self.c_font = pg.font.Font(None, Board.c_font_size)
		self.c_font.set_bold(Board.c_font_bold)
		self.b_font = pg.font.Font(None, Board.b_font_size)

		self.moves = self.game.getMoves()
		self.last_move = None
		self.log = []
		self.log_offset = 0
		self.currentView = 0
		self.click_bar = False

		self.grabbed = None
		self.move_on_click = None
		self.highlight = [[None] * self.w for i in range(self.h)]
		self.mouse = (0, 0)
		self.flip = False

		self.time_start = time.perf_counter()
		self.time_complete = self.time_start

		self.updateLog()


	def checkFlip(self, x, y):
		x = self.w - x - 1 if self.flip else x
		y = y if self.flip else self.h - y - 1
		return int(x), int(y)


	def getMouseTile(self):
		return self.checkFlip(self.mouse[0] // self.sw, self.mouse[1] // self.sh)


	def tryMove(self, p, x, y):
		for m in self.moves:
			if m[0] == p:
				for i in range(1, len(m)):
					if m[i][0] == x and m[i][1] == y:
						return True

		return False


	def playMove(self, m, value):
		self.time_complete = time.perf_counter() - self.time_start
		self.time_start = time.perf_counter()

		self.last_move = [m[0], m[0].x, m[0].y]
		self.engine.movePiece(m)
		self.moves = self.game.getMoves()
		self.updateHighlights()
		self.updateLog()


		s = "\n" + str((self.game.move_count - 1) // 2 + 1) + ". "
		if self.game.move_count % 2 == 0: s += self.engine.log_notated[-2] + ", "
		s += self.engine.log_notated[-1]
		print(s)
		s = ""
		if value != None: s = "{0:+d}".format(value) + ", "
		print(s + str(self.time_complete) + "s")

		is_won = self.game.isWon()

		if is_won == 1:
			print("White wins!")
		elif is_won == -1:
			print("Black wins!")


	def updateLog(self):
		if self.currentView == len(self.log) - 1:
			self.currentView += 1

		self.log.append({})

		for p in self.game.pieces:
			self.log[-1][p] = (p.x, p.y)


	def drawTiles(self):
		#tiles
		for i in range(self.w):
			for j in range(self.h):
				x, y = self.checkFlip(j, i)
				pg.draw.rect(self.screen, Board.tile_colors[(x + y) % 2], pg.Rect(x * self.sw, y * self.sh, self.sw, self.sh))

		#watering holes
		for x, y in self.wh:
			x, y = self.checkFlip(x, y)
			pg.draw.circle(self.screen, Board.tile_colors[(x + y + 1) % 2], ((x + 0.5) * self.sw, (y + 0.5) * self.sh), min(self.sw, self.sh) / 2)


	def drawText(self):
		#rows
		x = Board.c_margin
		for i in range(self.h):
			i =  i if self.flip else self.h - i - 1
			text = self.c_font.render(str(i + 1), 1, Board.text_colors[(i + 1) % 2])
			ts = text.get_size()[0]
			self.screen.blit(text, (x, (i + 0.5) * self.sh - ts / 2))

		#files
		y = self.size[1] - Board.c_margin
		for i in range(self.w):
			x = self.w - i - 1 if self.flip else i
			text = self.c_font.render(alphabet[i], 1, Board.text_colors[(x + Game.height) % 2])
			ts = text.get_size()
			self.screen.blit(text, ((x + 0.5) * self.sw - ts[0] / 2, y - ts[1]))


	def drawPieces(self):
		for p in self.game.pieces:
			if p == self.grabbed:
				continue

			n = image_names[int(p.t + p.side * len(Board.image_names) / 2)]
			x, y = self.checkFlip(self.log[self.currentView][p][0], self.log[self.currentView][p][1])
			self.screen.blit(images[n], pg.Rect(x * self.sw, y * self.sh, self.sw, self.sh))

		if self.grabbed != None:
			n = image_names[int(self.grabbed.t + self.grabbed.side * len(Board.image_names) / 2)]
			self.screen.blit(images[n], pg.Rect(self.mouse[0] - self.sw / 2, self.mouse[1] - self.sh / 2, self.sw, self.sh))


	def updateHighlights(self):
		self.highlight = [[None] * self.w for i in range(self.h)]

		if self.last_move != None:
			m = self.last_move
			self.highlight[m[2]][m[1]] = Board.colors["last_move"]
			self.highlight[m[0].y][m[0].x] = Board.colors["last_move"]

		p = self.grabbed if self.move_on_click == None else self.move_on_click

		if p != None:
			for m in self.moves:
				if m[0] == p:
					for i in range(1, len(m)):
						self.highlight[m[i][1]][m[i][0]] = Board.colors["vision"]

		for p in self.game.pieces:
			if p.threatened:
				self.highlight[p.y][p.x] = Board.colors["threatened"]

		is_won = self.game.isWon()
		if is_won != 0:
			if is_won == 1:
				ps = self.game.white
			else:
				ps = self.game.black

			for p in ps:
				if p.on_wh:
					self.highlight[p.y][p.x] = Board.colors["won"]


	def drawHighlights(self):
		s = pg.Surface(self.size, pg.SRCALPHA)
		s.set_alpha(Board.highlight_opacity)
			

		for i in range(self.h):
			for j in range(self.w):
				if self.highlight[i][j] != None:
					x, y = self.checkFlip(j, i)
					pg.draw.rect(s, self.highlight[i][j], pg.Rect(x * self.sw, y * self.sh, self.sw, self.sh))


		self.screen.blit(s, (0, 0))


	def drawBar(self):
		pg.draw.rect(self.screen, Board.colors["bar"], pg.Rect(0, self.size[1], self.size[0], Board.b_height))

		i = self.log_offset = min(self.log_offset, self.currentView)
		if i > 0 and i % 2 == 0:
			i -= 1
		x = Board.b_margin
		y = self.size[1] + Board.b_margin

		while i < len(self.log):
			c = Board.colors["bar_text_hl"] if i == self.currentView else Board.colors["bar_text"]
			new_line = False

			if i == 0:
				t = "START"
			else:
				if i % 2 == 1:
					t = str((i + 1) // 2) + ". " + self.engine.log_notated[i - 1]

					if i < len(self.log) - 1:
						text = self.b_font.render(t + ", " + self.engine.log_notated[i], 1, c)
						if text.get_size()[0] > self.size[0] - Board.b_margin: new_line = True
				else:
					t = self.engine.log_notated[i - 1]

			if i < len(self.log) - 1:
				t += ", "

			if i % 2 == 0:
				t += ""

			text = self.b_font.render(t, 1, c)
			ts = text.get_size()

			if new_line or x + ts[0] > self.size[0] - Board.b_margin:
				if y + ts[1] * 3 > self.size[1] + Board.b_height - Board.b_margin:
					if self.currentView >= i:
						self.log_offset += 1

					break

				x = Board.b_margin
				y += ts[1] * 2

			self.screen.blit(text, (x, y))

			if self.click_bar:
				if self.mouse[0] > x - 5 and self.mouse[0] < x + ts[0] + 5 and self.mouse[1] > y - 5 and self.mouse[1] < y + ts[1] + 5:
					self.currentView = i

			x += ts[0]

			if i % 2 == 0:
				x += Board.b_margin / 2

			i += 1

		self.click_bar = False


	def draw(self):
		self.drawTiles()
		self.drawText()
		self.drawHighlights()
		self.drawPieces()
		self.drawBar()

if __name__ == "__main__":
	main()
