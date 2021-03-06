
screen_size = (640,480)
import pygame
from pygame.constants import *

import random


##################################################################
pygame.init()
global fullscreen
fullscreen=False

scrnflags = 0
if fullscreen: scrnflags = pygame.FULLSCREEN
global screen
screen = pygame.display.set_mode(screen_size, scrnflags)

pygame.mouse.set_visible(True)
clock = pygame.time.Clock()
prevkeybits = []
keybits = []

def	read_moto(f):
	a = ord( f.read(1))
	a = (a << 8) | ord( f.read(1))
	a = (a << 8) | ord( f.read(1))
	a = (a << 8) | ord( f.read(1))
	return a

##################################################################
class	playfield:
	def __init__(self,mapfile):
		f = open( datapath_art(mapfile),'rb')
		if f:
			magic = read_moto(f)
			version = read_moto(f)
			self.mapxsz = read_moto(f)
			self.mapysz = read_moto(f)
			print "size = " + `self.mapxsz` + "," + `self.mapysz`
			self.tiles = []
			for j in range(self.mapysz):
				for i in range(self.mapxsz):
					self.tiles.append( read_moto(f))
			f.close()
	def	plot( self, screenX, screenY, screenW, screenH, playfieldULX, playfieldULY, tileMap, tileXSize, tileYSize):
		# clip away portions not necessary for this view
		tileLeft   = playfieldULX / tileXSize;
		tileTop    = playfieldULY / tileYSize;
		tileRight  = tileLeft + (screenW + 2 * tileXSize - 1) / tileXSize;
		tileBottom = tileTop  + (screenH + 2 * tileYSize - 1) / tileYSize;

		if (tileLeft < 0):			   tileLeft		= 0;
		if (tileRight > self.mapxsz):  tileRight	= self.mapxsz;
		if (tileTop < 0):			   tileTop		= 0;
		if (tileBottom > self.mapysz): tileBottom	= self.mapysz;

		tileMapStride = tileMap.get_width() / tileXSize;

		for j in range( tileTop, tileBottom):
			for i in range( tileLeft, tileRight):
				screenTileX = screenX + tileXSize * i - playfieldULX
				screenTileY = screenY + tileYSize * j - playfieldULY

				c = self.tiles[ i + j * self.mapxsz]

				# <WIP> animation?

				c &= 0x00000fff
				
				# find where we're pulling from?
				sourceX = (c % tileMapStride) * tileXSize
				sourceY = (c / tileMapStride) * tileYSize

				tileRect = [sourceX, sourceY, tileXSize, tileYSize]

				# clip smoothly
				if screenTileX < screenX:
					tileRect[0] += screenX - screenTileX
					tileRect[2] -= screenX - screenTileX
					screenTileX = screenX
				if screenTileY < screenY:
					tileRect[1] += screenY - screenTileY
					tileRect[3] -= screenY - screenTileY
					screenTileY = screenY
				if screenTileX + tileXSize > screenX + screenW:
					tileRect[2] -= (screenTileX + tileXSize) - (screenX + screenW)
				if screenTileY + tileYSize > screenY + screenH:
					tileRect[3] -= (screenTileY + tileYSize) - (screenY + screenH)

				# <WIP> right and bottom clipping needed still

	
				if tileRect[2] > 0:
					if tileRect[3] > 0:
						screen.blit( tilemap, [screenTileX, screenTileY], tileRect)




def	datapath_art(file):
	return "data/art/" + file
def	datapath_sound(file):
	return "data/sound/" + file


##################################################################

def load_image(file, transparent=1):
	"""
	file -- the filename of the image to load
	transparent -- whether the background of the image should be transparent.
				   Defaults to true.
				   The background colour is taken as the colour of the pixel
				   at (0,0) in the image.
	"""
	surface = pygame.image.load(datapath_art(file))
	if transparent:
		corner = surface.get_at((0, 0))
		surface.set_colorkey(corner, RLEACCEL)
	return surface		#.convert

def load_sound(file):
	"""
	Load a sound file, returning a Sound object.
	"""
	return pygame.mixer.Sound(datapath_sound(file))


##################################################################

def	load_image_rotable( file, maxrots):
	baseimage = load_image( file)

	imagearray = []

	for i in range( maxrots):
		angle = -(i * 360) / maxrots
		rotate = pygame.transform.rotate
		imagearray.append( rotate( baseimage, angle))

	return imagearray



class shapestrip:
	def	__init__(self,file,ysize):
		self.shape = load_image( file)
		self.xsize = self.shape.get_width()
		self.ysize = ysize
		self.numframes = self.shape.get_height() / ysize
	def	plot(self,x,y,frameno):
		dst = [x - self.xsize / 2, y - self.ysize / 2,0,0]
		src = [0, frameno * self.ysize, self.xsize, self.ysize]
		screen.blit( self.shape, dst, src)



JUSTIFY_LEFT   = 0x0000
JUSTIFY_CENTER = 0x0001
JUSTIFY_RIGHT  = 0x0002

class	_vgaprn:
	def __init__(self):
		self.print_font = pygame.font.SysFont("Times New Roman",30)
		self.color0 = (0,0,0)
		self.color1 = (255,255,255)
		self.zerowrite = 0
		self.justify = 0
	def	printf(self,x,y,str):
		if self.print_font:
			s = self.print_font.render( str,False,self.color1)
			if self.justify & JUSTIFY_CENTER:
				x -= s.get_width() / 2
			elif self.justify & JUSTIFY_RIGHT:
				x -= s.get_width()
			if self.zerowrite:
				pygame.draw.rect( screen, self.color0, (x,y,s.get_width(),s.get_height()))
			screen.blit( s, (x, y))
		return			

VGAPRN = _vgaprn()


##################################################################
joystick_initialized = 0
joystick1 = 0

jx1 = -1
jy1 = -1
jx2 = -1
jy2 = -1

prevjbuttons = 0
jbuttons = 0

##################################################################
def joystick_think():
	global joystick1, joystick_initialized

	if not joystick_initialized:
		joystick_initialized = 1
		try:
			joystick1 = pygame.joystick.Joystick(0)
		except pygame.error:
			joystick1 = 0
			return
		joystick1.init()

	if not joystick1:
		return

	global jx1, jy1, jx2, jy2
	jx1 = -1
	jy1 = -1
	jx2 = -1
	jy2 = -1

	global jbuttons, prevjbuttons
	prevjbuttons = jbuttons
	jbuttons = 0
	if joystick1.get_button(0):
		jbuttons |= 1
	if joystick1.get_button(1):
		jbuttons |= 2
	if joystick1.get_button(2):
		jbuttons |= 4
	if joystick1.get_button(3):
		jbuttons |= 8

	for i in range( joystick1.get_numaxes()):
		xxx = joystick1.get_axis(i)
		xxx = 100 + 100 * xxx
		if i == 0: jx1 = xxx
		if i == 1: jy1 = xxx
		if i == 2: jx2 = xxx
		if i == 3: jy2 = xxx
	return



##################################################################

class	OBJ:
	def __init__(self):
		# status
		self.flag = 0
		self.dead = 0
		self.type = 0
		self.subtype = 0
		# timers, counters, etc
		self.timer = 0
		self.state = 0
		self.points = 0
		# hitpoints
		self.hits = 0
		self.maxhits = 0	# generally, 0 will imply 1
		# fixed point
		self.x = 0
		self.y = 0
		self.xm = 0
		self.ym = 0
		self.rot = 0
		self.rotm = 0
		# integer (screen coords generally)
		self.ix = 0
		self.iy = 0
		self.r = pygame.Rect(0,0,0,0)
		# appearance
		self.frameno = 0
		self.animseq = 0
		# misc
		self.gunheat = 0
		return
	def	calcrect(self,w,h):
		self.ix = self.x >> 16
		self.iy = self.y >> 16
		self.r.x = self.ix - w / 2
		self.r.y = self.iy - h / 2
		self.r.w = w
		self.r.h = h
		return



##################################################################

def	plot( x, y, shape):
	r = [x - shape.get_width() / 2,y - shape.get_height() / 2,0,0]
	screen.blit( shape, r)
	return




##################################################################

CANVAS_GREET    =  1
CANVAS_INITGAME =  2
CANVAS_INITWAVE =  3
CANVAS_PLAYING  =  4
CANVAS_MAXIMUM  =  5


your_ship = load_image( "your_ship.png")
your_ship_iconic = load_image( "your_ship_iconic.png")

ss_shots_and_bombs = shapestrip( "shots_and_bombs.png", 25)

ss_expl1 = shapestrip( "expl1.png", 18)
ss_expl2 = shapestrip( "expl2.png", 25)

ss_invaders = shapestrip( "invaders.png", 25)

ss_invader_boss = shapestrip( "invader_boss.png", 100)

ss_saucer1 = shapestrip( "saucer1.png", 16)

MAXROTS = 64

shape_meteor1 = load_image_rotable( "meteor1.png", MAXROTS)
shape_meteor2 = load_image_rotable( "meteor2.png", MAXROTS)



sounds_shots = []
sounds_shots.append( load_sound( "shot1.wav"))
sounds_shots.append( load_sound( "shot2.wav"))
sounds_shots.append( load_sound( "shot3.wav"))

sounds_expls = []
sounds_expls.append( load_sound( "expl1.wav"))
sounds_expls.append( load_sound( "expl2.wav"))
sounds_expls.append( load_sound( "expl3.wav"))
sounds_expls.append( load_sound( "expl4.wav"))
sounds_expls.append( load_sound( "expl5.wav"))
sounds_expls.append( load_sound( "expl6.wav"))

sounds_bombs = []
sounds_bombs.append( load_sound( "bomb1.wav"))

sound_saucer1 = load_sound( "saucer1.wav")

def	sound_silence_all():
	sound_saucer1.stop()
	return

WAVETYPE_INVADERFIELD = 1
WAVETYPE_METEORSTORM  = 2
WAVETYPE_BOSSINVADER  = 3


WAVETYPE_FRAMEWORK_LENGTH = 4


class	gamestate:
	def	__init__(self):




		self.score = 0
		self.highscore = 0
		self.ships = 0
		self.waveno = 0


		self.canvasno = 0
		self.canvastimer = 0

		self.bonus = 0
		self.boninc = 0


		self.wave_lo = 0
		self.wave_hi = 0

		self.you = OBJ()
		self.you_safe_timer = 0
		self.shots = []
		self.bombs = []
		self.expls = []
		self.saucers = []
		self.meteors = []
		self.invaders = []
		self.invaders_rover = 0
		self.invaders_numthinks = 0
		self.invaders_xm_basic = 0
		self.invaders_ym_basic = 0
		self.invaders_xm = 0
		self.invaders_ym = 0
		self.invaders_tempxm = 0
		self.invaders_phase = 0
		self.invaders_pause = 0
		self.invaders_have_landed = 0
		self.invader_bomb_drop_rate = 100

		self.wavetype = 0

		self.time_to_advance_wave = 0

		self.saucer_appearance_counter = 0
		self.difficulty_cursaucers = 0
		self.difficulty_maxsaucers = 0

		self.difficulty_curbombs = 0
		self.difficulty_maxbombs = 0
		self.difficulty_curshots = 0
		self.difficulty_maxshots = 0

		self.cheating = 0

		return

	def addscore(self,points):
		self.score += points
		if self.score >= self.bonus:
			self.ships += 1
			self.bonus += self.boninc


STATE = gamestate()

hisc_filename = "anisi_highscore.txt"

try:
	hiscfile = open( hisc_filename, "rt")
	try:
		STATE.highscore = int( hiscfile.read())
	except ValueError:
		pass
	hiscfile.close()
except IOError:
	pass

if STATE.highscore < 1000:
	STATE.highscore = 1000

def	init_initgame():
	STATE.cheating = 0
	STATE.score = 0
	STATE.bonus  = 10000
	STATE.boninc = 10000
	STATE.ships = 3
	STATE.waveno = 0
	STATE.you.__init__()
	aliens_clearall()
	bombs_clearall()
	shots_clearall()
	expls_clearall()
	STATE.invaders_have_landed = 0
	STATE.you_safe_timer = 0
	return

def	init_create_invader_field():

	STATE.invaders_xm_basic = 5 << 16		# across
	STATE.invaders_ym_basic = 15 << 16		# down
	STATE.invaders_numthinks = 5
	STATE.invader_bomb_drop_rate = 100

	STATE.invaders_xm = STATE.invaders_xm_basic
	STATE.invaders_ym = 0

	STATE.invaders_phase = 0

	STATE.invaders_pause = 0

	lowest_alien_row = 150 + 50 * STATE.wave_hi
	# but don't let it get INSANELY low
	if lowest_alien_row > screen.get_height() - 100:
		lowest_alien_row = screen.get_height() - 100

	invaders_across = 7 + (STATE.wave_hi & 3)
	invaders_down   = 4 + (STATE.wave_hi & 3)

	if STATE.wavetype == WAVETYPE_BOSSINVADER:
		invaders_across = 1
		invaders_down = 1
		STATE.invaders_ym_basic = 0
		STATE.invaders_numthinks = 1
		if lowest_alien_row > screen.get_height() / 2:
			lowest_alien_row = screen.get_height() / 2

	invader_jumbled_color = random.randrange(5) == 0
	invader_type_offset = random.randrange(10)

	for j in range( invaders_down):
		for i in range( invaders_across):
			a = invaders_alloc()
			if a:
				a.flag = 1
				a.type = (j + invader_type_offset) & 7
				if invader_jumbled_color:
					a.type = random.randrange( 8)
				a.points = 10 * (j + 1)
				a.x = (150 + i * 40) << 16
				a.y = (lowest_alien_row - j * 30) << 16
				a.calcrect( 30, 20)
				a.frameno = (a.type & 7) * 2

				if STATE.wavetype == WAVETYPE_BOSSINVADER:
					a.points = 2000
					a.type = 100
					a.maxhits = 10 + STATE.wave_hi
					if a.maxhits > 20:
						a.maxhits = 20
					a.frameno = 0
	return
	
def	init_initwave():
	STATE.time_to_advance_wave = 0

	STATE.waveno = STATE.waveno + 1
	STATE.wave_lo = (STATE.waveno - 1) % WAVETYPE_FRAMEWORK_LENGTH
	STATE.wave_hi = (STATE.waveno - 1) / WAVETYPE_FRAMEWORK_LENGTH


	STATE.meteor_field_timer = 0
	if STATE.wave_lo == 0:
		STATE.wavetype = WAVETYPE_INVADERFIELD
	elif STATE.wave_lo == 1:
		STATE.wavetype = WAVETYPE_METEORSTORM
	elif STATE.wave_lo == 2:
		STATE.wavetype = WAVETYPE_INVADERFIELD
	elif STATE.wave_lo == 3:
		STATE.wavetype = WAVETYPE_BOSSINVADER


	if STATE.wavetype == WAVETYPE_INVADERFIELD:
		init_create_invader_field()
	elif STATE.wavetype == WAVETYPE_METEORSTORM:
		STATE.meteor_field_timer = 200 + random.randrange( 200)
	elif STATE.wavetype == WAVETYPE_BOSSINVADER:
		init_create_invader_field()


	STATE.difficulty_maxbombs = 5 + STATE.wave_hi
	STATE.difficulty_maxshots = 2 + STATE.wave_hi
	

	if STATE.difficulty_maxshots > 3:
		STATE.difficulty_maxshots = 3

	STATE.saucer_appearance_counter = 0
	STATE.difficulty_maxsaucers = 1

	return

cheatarray = []
cheatarray.append( "")
cheatarray.append( " (by cheating)")

def	canvas_greet():
	c = [80,0,0]
	screen.fill( c)

	if STATE.cheating == 0:
		if STATE.score > STATE.highscore:
			STATE.highscore = STATE.score
			try:
				hiscfile = open( hisc_filename, "wt")
				hiscfile.write( str( STATE.highscore))
				hiscfile.close()
			except IOError:
				pass

	VGAPRN.zerowrite = 0
	VGAPRN.color1 = (255, 255, 0)
	VGAPRN.justify = JUSTIFY_CENTER

	nn = 10
	VGAPRN.printf( screen_size[0] / 2, 1 * screen_size[1] / nn,
					"Space Invaders!")
	VGAPRN.printf( screen_size[0] / 2, 2 * screen_size[1] / nn,
					"By Ani Tangellapalli")
	VGAPRN.printf( screen_size[0] / 2, 3 * screen_size[1] / nn,
					"")
	VGAPRN.printf( screen_size[0] / 2, 4 * screen_size[1] / nn,
					"Press <ENTER> to begin new game");
	tmp = "Last: " + `STATE.score` + cheatarray[STATE.cheating] + " --- High: " + `STATE.highscore`
	VGAPRN.printf( screen_size[0] / 2, 5 * screen_size[1] / nn,
					tmp);
	VGAPRN.printf( screen_size[0] / 2, 6 * screen_size[1] / nn,
					"Use arrows to move and Ctrl to fire")
	VGAPRN.printf( screen_size[0] / 2, 7 * screen_size[1] / nn,
					"ESCAPE to exit and <F> to toggle Fullscreen")
	VGAPRN.printf( screen_size[0] / 2, 8 * screen_size[1] / nn,
					"For cheats ask Ani :)")

	joystick_think()

	if jbuttons & 15:
		STATE.canvasno = CANVAS_INITGAME

	if len( keypresses):
		if keypresses[0] == K_RETURN:
			STATE.canvasno = CANVAS_INITGAME
		if keypresses[0] == K_ESCAPE:
			global finished
			finished = True

	return

EXPLTYPE_EXPL1 = 101
EXPLTYPE_EXPL2 = 102
EXPLTYPE_EXPL3 = 103


##################################################################
def	expls_clearall():
	STATE.expls = []
	return

def	expls_alloc():
	for e in STATE.expls:
		if e:
			if e.flag == 0:
				e.__init__()
				return e
	e = OBJ()
	STATE.expls.append(e)
	return e

def	expls_think():
	for e in STATE.expls:
		if e:
			if e.flag:
				if e.type == EXPLTYPE_EXPL1:
					e.animseq += 1
					e.frameno = e.animseq - 1
					if e.animseq >= 10:
						e.flag = 0
				if e.type == EXPLTYPE_EXPL2:
					e.timer -= 1
					if e.timer <= 0:
						e.flag = 0

				if e.type == EXPLTYPE_EXPL3:
					STATE.time_to_advance_wave = 0
					e.timer -= 1
					if e.timer <= 0:
						e.flag = 0
					newe = expls_alloc()
					if newe:
						sounds_expls[random.randrange(len(sounds_expls))].play()
						newe.flag = 1
						if random.randrange(2) == 0:
							newe.type = EXPLTYPE_EXPL1
						else:
							newe.type = EXPLTYPE_EXPL2
						newe.timer = 10
						newe.x = e.x + ((random.randrange(130) - 65) << 16)
						newe.y = e.y + ((random.randrange(130) - 65) << 16)
						newe.calcrect( 0, 0)
				e.calcrect( 0,0)
	return

def	expls_paint():
	for e in STATE.expls:
		if e:
			if e.flag:
				if e.type == EXPLTYPE_EXPL1:
					ss_expl1.plot( e.ix, e.iy, e.frameno)
				if e.type == EXPLTYPE_EXPL2:
					ss_expl2.plot( e.ix, e.iy, 0)
	return

def	shots_clearall():
	STATE.shots = []
	return

def	shots_alloc():
	for s in STATE.shots:
		if s:
			if s.flag == 0:
				s.__init__()
				return s
	s = OBJ()
	STATE.shots.append(s)
	return s
################################################################
def	shots_think():
	for s in STATE.shots:
		if s:
			if s.flag:
				## <WIP> this should support different types of shots!
				s.x += s.xm
				s.y += s.ym
				s.calcrect( 10, 20)
				if aliens_check_shot(s) or meteors_check_shot(s) or bombs_check_shot(s):
					s.flag = 0
					sounds_expls[random.randrange(len(sounds_expls))].play()
					e = expls_alloc()
					if e:
						e.flag = 1
						e.type = EXPLTYPE_EXPL1
						e.x = s.x
						e.y = s.y
						e.calcrect( 0,0)

				if s.iy < -20:
					s.flag = 0
	return

def	shots_paint():
	numshots = 0
	for s in STATE.shots:
		if s:
			if s.flag:
				## <WIP> this should support different types of shots!
				ss_shots_and_bombs.plot( s.ix, s.iy, 0)
				numshots += 1

	STATE.difficulty_curshots = numshots

	return

##################################################################
def	bombs_clearall():
	STATE.bombs = []
	return

def	bombs_alloc():
	for b in STATE.bombs:
		if b:
			if b.flag == 0:
				b.__init__()
				return b
	b = OBJ()
	STATE.bombs.append(b)
	return b

def	bombs_think():
	for b in STATE.bombs:
		if b:
			if b.flag:
				b.animseq += 1
				b.x += b.xm
				b.y += b.ym
				b.calcrect( 10, 20)
				if b.type == 2:
					b.frameno = 3
				elif b.type == 1:
					b.frameno = 1 + ((b.animseq >> 1) & 1)

				if STATE.you.flag:
					if STATE.you.dead == 0:
						if abs( STATE.you.ix - b.ix) < 26:
							if abs( STATE.you.iy - b.iy) < 20:
								STATE.you.dead = 1
								b.flag = 0

				if b.iy > screen.get_height() - 35:
					b.flag = 0
					e = expls_alloc()

					if e:
						e.flag = 1
						e.type = EXPLTYPE_EXPL1
						e.x = b.x
						e.y = (screen.get_height() - 30) << 16
						e.calcrect( 0,0)
	return

def	bombs_paint():
	numbombs = 0
	for b in STATE.bombs:
		if b:
			if b.flag:
				## <WIP> this should support different types of bombs!
				ss_shots_and_bombs.plot( b.ix, b.iy, b.frameno)
				numbombs += 1

	STATE.difficulty_curbombs = numbombs

	return


def	bombs_check_shot(s):
	for b in STATE.bombs:
		if b:
			if b.flag:
				if abs( b.ix - s.ix) < ( b.r.w + s.r.w) / 2:
					if abs( b.iy - s.iy) < ( b.r.h + s.r.h) / 2:

						if random.randrange(3):
							b.flag = 0
						STATE.addscore( 1)

						e = expls_alloc()
						if e:
							e.flag = 1
							e.type = EXPLTYPE_EXPL1
							e.x = b.x
							e.y = b.y
							e.calcrect( 0,0)
						return 1
	return 0


##################################################################
INVADER_EDGEX = 30


##################################################################
def	aliens_clearall():
	STATE.invaders = []
	STATE.invaders_rover = 0
	STATE.saucers = []
	sound_saucer1.stop()
	return

def	saucers_alloc():
	for a in STATE.saucers:
		if a:
			if a.flag == 0:
				a.__init__()
				return a
	a = OBJ()
	STATE.saucers.append(a)
	return a

def	invaders_alloc():
	for a in STATE.invaders:
		if a:
			if a.flag == 0:
				a.__init__()
				return a
	a = OBJ()
	STATE.invaders.append(a)
	return a

def	aliens_think_one_invader():
	deadlock = 0
	if not len( STATE.invaders): return
	while 1:
		if STATE.invaders_rover == 0:

			if STATE.invaders_phase == 1:
				STATE.invaders_tempxm = STATE.invaders_xm
				STATE.invaders_xm = 0
				STATE.invaders_ym = STATE.invaders_ym_basic
				STATE.invaders_phase = 2
			elif STATE.invaders_phase == 2:
				STATE.invaders_xm = -STATE.invaders_tempxm
				STATE.invaders_ym = 0
				STATE.invaders_phase = 0
		a = STATE.invaders[ STATE.invaders_rover]
		STATE.invaders_rover += 1
		if STATE.invaders_rover >= len(STATE.invaders):
			STATE.invaders_rover = 0
			if deadlock >= 2:
				return
			deadlock += 1
		if a:
			if a.flag:
				STATE.time_to_advance_wave = 0
				a.x += STATE.invaders_xm
				a.y += STATE.invaders_ym
				
				if a.type == 100:
					a.calcrect( 110, 80)
				else:
					a.calcrect( 30, 20)


				if a.iy >= STATE.you.iy - 25:
					a.iy = STATE.you.iy
					a.y = a.iy << 16
					STATE.invaders_have_landed = 1
					STATE.you.dead = 1
					STATE.ships = 0


				if (a.ix < INVADER_EDGEX) or (a.ix > screen.get_width() - INVADER_EDGEX):
					if STATE.invaders_phase == 0:
						STATE.invaders_phase = 1
				a.animseq += 1
				if a.type == 100:
					a.frameno = (a.animseq >> 1) & 1
				else:
					a.frameno = (a.type & 7) * 2 + (a.animseq & 1)

				if STATE.difficulty_curbombs < STATE.difficulty_maxbombs:
					if random.randrange( STATE.invader_bomb_drop_rate) == 0:
						b = bombs_alloc()
						if b:
							b.flag = 1
							b.type = 2
							b.x = a.x
							b.y = a.y
							b.xm = 0
							b.ym = 5 << 16
							if STATE.wave_hi & 1:
								b.type = 1
								b.ym = 8 << 16
							b.calcrect( 0,0)
							sounds_bombs[random.randrange(len(sounds_bombs))].play()
				break
	return

def	aliens_think_invaders():
	if STATE.invaders_have_landed:
		return

	if STATE.invaders_pause > 0:
		STATE.time_to_advance_wave = 0
		STATE.invaders_pause -= 1
		return
	STATE.invaders_pause = 0

	if STATE.you.dead:
		return
	for a in range( STATE.invaders_numthinks):
		aliens_think_one_invader()
	return

def	aliens_think_saucers():
	numsaucers = 0
	for a in STATE.saucers:
		if a:
			if a.flag:
				numsaucers += 1

				a.x += a.xm
				a.y += a.ym
				a.calcrect( 40, 20)
				a.frameno = a.type
				if a.xm > 0:
					if a.ix >= screen.get_width() + 30:
						a.flag = 0
						sound_saucer1.stop()
				if a.xm < 0:
					if a.ix <= -30:
						a.flag = 0
						sound_saucer1.stop()
	STATE.difficulty_cursaucers = numsaucers


def	aliens_think():
	aliens_think_invaders()
	aliens_think_saucers()

	if STATE.invaders_have_landed:
		return


	if STATE.difficulty_cursaucers < STATE.difficulty_maxsaucers:
		STATE.saucer_appearance_counter += 1
		if STATE.saucer_appearance_counter > 300:
			STATE.saucer_appearance_counter = 0
			a = saucers_alloc()
			if a:
				a.flag = 1
				a.y = 20 << 16
				a.type = random.randrange(4)
				if random.randrange(2) == 0:
					a.x = -30 << 16
					a.xm = (2 + random.randrange(2)) << 16
				else:
					a.x = (screen.get_width() + 30) << 16
					a.xm = -(2 + random.randrange(2)) << 16
				a.calcrect( 0,0)
				sound_saucer1.play(-1)

def	aliens_paint():
	for a in STATE.invaders:
		if a:
			if a.flag:
				if a.type == 100:
					bossx = a.ix
					bossy = a.iy
					if STATE.invaders_pause > 0:
						bossx += random.randrange( 16) - 8
						bossy += random.randrange( 10) - 5
					ss_invader_boss.plot( bossx, bossy, a.frameno)
				else:
					ss_invaders.plot( a.ix, a.iy, a.frameno)
	for a in STATE.saucers:
		if a:
			if a.flag:
				ss_saucer1.plot( a.ix, a.iy, a.frameno)
	if STATE.invaders_have_landed:
		VGAPRN.zerowrite = 0
		VGAPRN.color1 = (random.randrange( 256), random.randrange( 256), random.randrange(256))
		VGAPRN.justify = JUSTIFY_CENTER
		VGAPRN.printf( screen.get_width() / 2, screen.get_height() / 3,
						"*** YOU HAVE BEEN INVADED ***")
	return

def	aliens_check_shot(s):
	for a in STATE.saucers:
		if a:
			if a.flag:
				if abs( a.ix - s.ix) < ( a.r.w + s.r.w) / 2:
					if abs( a.iy - s.iy) < ( a.r.h + s.r.h) / 2:
						a.flag = 0
						STATE.addscore( 100 * (1 + random.randrange( 9)))
						sound_saucer1.stop()
						sounds_expls[random.randrange(len(sounds_expls))].play()

						e = expls_alloc()
						if e:
							e.flag = 1
							e.type = EXPLTYPE_EXPL2
							e.timer = 10
							e.x = a.x
							e.y = a.y
							e.calcrect( 0,0)
						return 1

	for a in STATE.invaders:
		if a:
			if a.flag:
				if abs( a.ix - s.ix) < ( a.r.w + s.r.w) / 2:
					if abs( a.iy - s.iy) < ( a.r.h + s.r.h) / 2:
						if a.maxhits:
							a.hits += 1
							if a.hits < a.maxhits:


								STATE.invaders_pause = 15

								for bc in range(5):
									b = bombs_alloc()
									if b:
										b.flag = 1
										b.type = 1 + random.randrange(2)
										b.x = a.x + ((random.randrange(120) - 60) << 16)
										b.y = a.y + ((random.randrange(20) + 20) << 16)
										b.xm = (random.randrange(400) - 200) * 655
										b.ym = (3 + random.randrange( 6)) << 16
										b.calcrect( 0, 0)

								STATE.invader_bomb_drop_rate = 20

								return 1
						a.flag = 0
						STATE.addscore( a.points)


						STATE.invaders_pause = 5

						e = expls_alloc()
						if e:
							e.flag = 1
							e.type = EXPLTYPE_EXPL2
							e.timer = 10
							if a.type == 100:
								e.type = EXPLTYPE_EXPL3
								e.timer = 100
							e.x = a.x
							e.y = a.y
							e.calcrect( 0,0)
						return 1
	return 0


##################################################################
def	meteors_clearall():
	STATE.meteors = []
	return

def	meteors_alloc():
	for m in STATE.meteors:
		if m:
			if m.flag == 0:
				m.__init__()
				return m
	m = OBJ()
	STATE.meteors.append(m)
	return m

def	meteors_think():
	for m in STATE.meteors:
		if m:
			if m.flag:
				STATE.time_to_advance_wave = 0
				m.x += m.xm
				m.y += m.ym
				m.rot += m.rotm
				if m.type == 1:
					m.calcrect( 28, 28)
				if m.type == 2:
					m.calcrect( 40, 40)
				else:
					m.calcrect( 40, 40)


				if STATE.you.flag:
					if STATE.you.dead == 0:
						if abs( STATE.you.ix - m.ix) < 26:
							if abs( STATE.you.iy - m.iy) < 20:
								STATE.you.dead = 1
								m.flag = 0


				if m.iy > screen.get_height() + 30:
					m.flag = 0
	

				if m.xm < 0:
					if m.ix < -30:
						m.flag = 0
				if m.xm > 0:
					if m.ix > screen.get_width() + 30:
						m.flag = 0


	if STATE.meteor_field_timer > 0:
		STATE.meteor_field_timer -= 1
		if (STATE.canvastimer & 7) == 0:
			m = meteors_alloc()
			if m:
				m.flag = 1
				m.type = 1 + random.randrange(2)
				m.rot = random.randrange( 360)
				m.rotm = (random.randrange(2) * 2 - 1) * (2 + random.randrange(3))
				m.x = (random.randrange( screen.get_width() + 80) - 40) << 16
				m.y = (-20 - random.randrange(40)) << 16;
				m.xm = (random.randrange(2) * 2 - 1) * (100 + random.randrange(300)) * 655
				m.ym = (100 + random.randrange(300)) * 655
				m.calcrect(0,0)
	return

def	meteors_paint():
	nummeteors = 0
	for m in STATE.meteors:
		if m:
			if m.flag:
				n = ((m.rot * MAXROTS) / 360) & (MAXROTS - 1)
				if m.type == 1:
					newimage = shape_meteor1[ n]
				if m.type == 2:
					newimage = shape_meteor2[ n]
				plot( m.ix, m.iy, newimage)
				nummeteors += 1

	STATE.difficulty_curmeteors = nummeteors

	return


def	meteors_check_shot(s):
	for m in STATE.meteors:
		if m:
			if m.flag:
				if abs( m.ix - s.ix) < ( m.r.w + s.r.w) / 2:
					if abs( m.iy - s.iy) < ( m.r.h + s.r.h) / 2:
						m.flag = 0
						STATE.addscore( 25 * (3 - m.type))

						e = expls_alloc()
						if e:
							e.flag = 1
							e.type = EXPLTYPE_EXPL2
							e.timer = 10
							e.x = m.x
							e.y = m.y
							e.calcrect( 0,0)
						return 1
	return 0


##################################################################

YOU_EDGEX = 50

##################################################################
def	you_think():
	if STATE.you.flag == 0:
		if STATE.ships > 0:
			STATE.ships -= 1
			
			STATE.you.flag = 1
			STATE.you.dead = 0

			STATE.you.x = YOU_EDGEX << 16
			STATE.you.y = (screen.get_height() - 40) << 16

			STATE.you.calcrect( 0,0)
		else:
			sound_silence_all()
			STATE.canvasno = CANVAS_GREET

	if STATE.you_safe_timer:
		STATE.you.dead = 0
		STATE.you_safe_timer -= 1

	if STATE.you.dead > 0:
		STATE.you.dead += 1
		if STATE.you.dead > 80:
			STATE.you.flag = 0
			STATE.you_safe_timer = 60
			return
		e = expls_alloc()
		if e:
			e.flag = 1
			e.type = EXPLTYPE_EXPL1
			e.x = STATE.you.x + ((random.randrange( 40) - 20) << 16)
			e.y = STATE.you.y + ((random.randrange( 16) -  8) << 16)
			e.calcrect( 0,0)
			if (STATE.you.dead & 3) == 0:
				sounds_expls[random.randrange(len(sounds_expls))].play()
		return

	STATE.you.xm = 0
	STATE.you.ym = 0

	if STATE.you.gunheat > 0:
		STATE.you.gunheat -= 1

	joystick_think()


	leftbit = 0
	rightbit = 0
	firebit = 0
	prevfirebit = 0
	if keybits[ K_LEFT] or ((jx1 != -1) and (jx1 < 50)):
		leftbit = 1
	if keybits[ K_RIGHT] or ((jx1 != -1) and (jx1 > 150)):
		rightbit = 1
	if keybits[ K_LCTRL] or keybits[ K_RCTRL] or (jbuttons & 15):
		firebit = 1
	if prevkeybits[ K_LCTRL] or prevkeybits[ K_RCTRL] or (prevjbuttons & 15):
		prevfirebit = 1


	if firebit:
		if (STATE.you.gunheat == 0) or (not prevfirebit):
			if STATE.difficulty_curshots < STATE.difficulty_maxshots:
				s = shots_alloc()
				if s:
					s.flag = 1
					s.x = STATE.you.x
					s.y = STATE.you.y
					s.xm = 0
					s.ym = -10 << 16
					s.calcrect( 0,0)
					STATE.you.gunheat = 5		# firerate
					sounds_shots[random.randrange(len(sounds_shots))].play()

	if leftbit:
		STATE.you.xm = -5 << 16

	if rightbit:
		STATE.you.xm =  5 << 16

	STATE.you.x += STATE.you.xm
	STATE.you.y += STATE.you.ym

	if STATE.you.x < YOU_EDGEX << 16:
		STATE.you.x = YOU_EDGEX << 16
	if STATE.you.x > (screen.get_width() - YOU_EDGEX) << 16:
		STATE.you.x = (screen.get_width() - YOU_EDGEX) << 16

	STATE.you.calcrect( 30, 40)

	return

def	you_paint():
	if STATE.you.flag:
		if STATE.you.dead == 0:
			if STATE.you_safe_timer > 20:
				if STATE.canvastimer & 4:
					return
			if STATE.you_safe_timer > 0:
				if STATE.canvastimer & 2:
					return
			plot( STATE.you.ix, STATE.you.iy, your_ship)
	return

##################################################################
def	canvas_playing():
	screen.fill((0,0,0))


	pygame.draw.rect( screen, [150, 100,  50], [0, screen.get_height() - 27, screen.get_width(), 5])

	for i in range( STATE.ships):
		plot( 15 + i * 27, screen.get_height() - 10, your_ship_iconic)

	VGAPRN.zerowrite = 0
	VGAPRN.color1 = ( 200,200,200)
	VGAPRN.justify = JUSTIFY_LEFT
	VGAPRN.printf( 5, 5, `STATE.score`);

	you_think()
	shots_think()
	aliens_think()
	meteors_think()
	bombs_think()
	expls_think()

	you_paint()
	shots_paint()
	bombs_paint()
	aliens_paint()
	expls_paint()
	meteors_paint()


	if STATE.you.flag and not STATE.you.dead:
		STATE.time_to_advance_wave += 1
		if STATE.time_to_advance_wave > 50:
			STATE.canvasno = CANVAS_INITWAVE

	if len(keypresses):
		if keypresses[0] == K_ESCAPE:
			STATE.canvasno = CANVAS_GREET

		if keypresses[0] == K_x:
			STATE.cheating = 1
			STATE.ships += 1
			if STATE.ships >= 4:
				STATE.ships = 4

		if keypresses[0] == K_n:
			STATE.cheating = 1
			aliens_clearall()
			meteors_clearall()
			STATE.canvasno = CANVAS_INITWAVE

	return




##################################################################
def	dispatch_canvases():
	STATE.canvastimer += 1
	if STATE.canvasno == CANVAS_GREET:
		canvas_greet()
	elif STATE.canvasno == CANVAS_INITGAME:
		init_initgame()
		STATE.canvasno = STATE.canvasno + 1
	elif STATE.canvasno == CANVAS_INITWAVE:
		init_initwave()
		STATE.canvasno = STATE.canvasno + 1
	elif STATE.canvasno == CANVAS_PLAYING:
		canvas_playing()
	else:
		STATE.canvasno = STATE.canvasno + 1
		if STATE.canvasno >= CANVAS_MAXIMUM:
			STATE.canvasno = CANVAS_GREET


##################################################################
finished = False
while not finished:

	prevkeybits = keybits[:]
	keybits = pygame.key.get_pressed()


	keypresses = []

	for e in pygame.event.get():
		if e.type == pygame.KEYDOWN:

			if e.key == pygame.K_f:
				if not fullscreen:
					screen=pygame.display.set_mode((640,480),pygame.FULLSCREEN)
					fullscreen=True
					pygame.mouse.set_visible(False)
				else:
					pygame.mouse.set_visible(True)
					screen=pygame.display.set_mode((640,480))
					fullscreen=False
			else:

				keypresses.append( e.key)

		if e.type in [pygame.QUIT]:
			finished = True
			break

	dispatch_canvases()

	pygame.display.update()

	clock.tick(30)
