import pygame, os, sys, math, random, copy
from vector import Vector
# Everything should be calculated relative to rocket.

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1000,500),pygame.DOUBLEBUF | pygame.RESIZABLE)
pygame.display.set_caption('Gravitron')
screen.set_colorkey((0,0,0))

pygame.mixer.music.load("music.mid")
pygame.mixer.music.play()

font = pygame.font.SysFont("Arial", 12)

def load_image(name, colorkey=None):
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', name
		raise SystemExit, message
	image = image.convert_alpha()
	if colorkey is not None:
		if colorkey is -1:
		  colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, pygame.RLEACCEL)
	return image, image.get_rect()
AScale = 10

class Projectile( pygame.sprite.DirtySprite ):

	def __init__(self,imagename, vel = Vector(0,0), truePos = Vector(1000,1000), spin = 0, maxSpeed = 7, groups = (), fuel = 10000000, rectPos = (3000,3000)):
		pygame.sprite.Sprite.__init__(self, groups)
		self.original, self.rect = load_image(imagename)
		self.vel = vel
		self.spin = 0
		self.image = self.original
		self.rotate(spin)
		self.true = truePos
		self.rect.center = rectPos
		self.mask = pygame.mask.from_surface(self.image)
		self.maxSpeed = maxSpeed # of the projectiles
		self.fuel = fuel
		self.radius = 200
		
	def update(self):
		self.true = self.true + self.vel
		# wrap around universe
		if self.true.x > 2000:
		  self.true.x -= 2000
		if self.true.y > 2000:
		  self.true.y -=2000
		if self.true.x < 0:
		  self.true.x += 2000
		if self.true.y < 0:
		  self.true.y += 2000
		self.fuel -= 1 # track of time
		if self.fuel < 0:
			self.kill()
			
		true_angle = math.atan2( -self.vel.y, self.vel.x )
		if true_angle < 0:
			true_angle += 2 * math.pi
		dtrue_angle= math.degrees(true_angle)
		spin = (self.spin + 90)%360
		rq_spin = (spin - dtrue_angle) #tt-go
		spinspeed = abs(rq_spin)/77
		if (spin <180) or (spin>270):
			if (((-rq_spin)>0) and (-rq_spin < 180)):
				self.rotate(spinspeed)
			else:
				self.rotate(-spinspeed)
		if((spin > 180) and (spin<270)):
			if ((rq_spin < 180) or rq_spin ==0 or rq_spin==90 or rq_spin ==180):
				self.rotate(spinspeed)
			else:
				self.rotate(-spinspeed)
		if ((spin>=270) and (spin<360)):
			if ((-rq_spin>0)and(-rq_spin < -180)):
				self.rotate(spinspeed)
			else:
				self.rotate(-spinspeed)
	
	def accelerate(self, acceleration):
		self.vel += acceleration
		mag = self.vel.magnitude()
		if mag > self.maxSpeed: # maximum speed
			self.vel = self.vel / mag * self.maxSpeed
		
	def backward(self):
		angle = math.radians(self.spin)
		self.accelerate(Vector(math.sin(angle)/AScale, math.cos(angle)/AScale))
	
	def forward(self):
		angle = math.radians(self.spin)
		self.accelerate(Vector(-math.sin(angle)/AScale, -math.cos(angle)/AScale))
	
	def rotate(self, degrees):
		self.spin = self.spin + degrees
		if self.spin > 360:
			self.spin -= 360
		if self.spin < 0:
			self.spin += 360
		c = self.rect.center
		self.image = pygame.transform.rotate(self.original, round(self.spin))
		self.rect = self.image.get_rect(center = c)
		self.dirty = 1
		self.mask = pygame.mask.from_surface(self.image)
		
	def move(self, dx,dy):
		self.rect.x += dx
		self.rect.y += dy
		
	def reset(self):
		self.true = Vector(1000,1000)
		self.vel = Vector(0,0)
		
	def scroll(self,rocket):
		p = self.true - rocket.true
		dx = round(p.x + pygame.display.Info().current_w/2)
		dy = round(p.y + pygame.display.Info().current_h/2)
		self.rect.center = (dx,dy)
		
class Planet( pygame.sprite.DirtySprite ):
	def __init__(self,radius,x,y, groups = ()):
		pygame.sprite.Sprite.__init__(self, groups)
		self.radius = radius
		name = "planet" + str(random.randint(1,4)) + ".png"
		self.image, self.rect = load_image(name, (0,0,0,0))
		self.image = pygame.transform.scale(self.image, (self.radius*2, self.radius*2))
		self.rect = self.image.get_rect()
		self.true = Vector(x,y)
		self.mask = pygame.mask.from_surface(self.image)
		
	def scroll(self,rocket):
		p = self.true - rocket.true
		dx = round(p.x + pygame.display.Info().current_w/2)
		dy = round(p.y + pygame.display.Info().current_h/2)
		self.rect.center = (dx,dy)
		
	def update(self):
		pass

# TODO: math stuff to calculate effect
def gravity(planets, xpos, ypos):
	ppos = Vector(xpos,ypos)
	all_force = Vector(0,0)
	for s in planets:
		spos = s.true
		direction = spos - ppos
		force =(s.radius**2)/ (direction.magnitude()**2)/50
		direction.normalize()
		all_force = all_force + (direction * force)*0
	return all_force

def pause():
	pausescreen, rect = load_image("pausescreen.jpg")
	done = False
	screen.blit(pausescreen, (0,0))
	pygame.display.update()
	while not done:
		for event in pygame.event.get():
			key = pygame.key.get_pressed()
			if key[pygame.K_s]:
				done = True
			if event.type == pygame.QUIT:
				done = True
	screen.fill((0,0,0,0))
	pygame.display.update()

def end():
	highscore = [0]
	text_file = open("highscore.txt","r+")
	text_file.seek(0)
	f = text_file.readlines()
	for line in f:
		try:
			highscore.append(int(line))
		except:
			pass
	text_file.write(str(score)+"\n")
	high = max(highscore)
	
	endscreen, rect = load_image("endscreen.jpg")
	done = False
	screen.blit(endscreen, (0,0))
	font = pygame.font.Font(None, 42)
	font2 = pygame.font.Font(None, 30)
	text = font.render("Your Score: " + str(score), 1, (39, 255, 20))
	text2 = font2.render("Highscore on this computer: " + str(high), 1, (39, 255, 20))
	screen.blit(text, (390,280))
	screen.blit(text2, (390,320))
	pygame.display.update()
	text_file.close()
	
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
		  		sys.exit()
		key = pygame.key.get_pressed()
		if key[pygame.K_ESCAPE]:
			done = True
			pygame.quit()

		if key[pygame.K_r]:
			done = True
			print "restarting the game... "
			python = sys.executable
			os.execl(python, python, * sys.argv)

allSprites = pygame.sprite.RenderUpdates()
singleRocket = pygame.sprite.GroupSingle()
missileSprites = pygame.sprite.Group()
rocketSprites = pygame.sprite.Group()
planetSprites = pygame.sprite.Group()
enemySprites = pygame.sprite.Group()
lastMissile = pygame.sprite.GroupSingle()
rocket = Projectile("srocket.png",groups = (rocketSprites,allSprites,singleRocket), rectPos = (pygame.display.Info().current_w/2,pygame.display.Info().current_h/2))

frame = 0
score = 0

done = False
dirty_rects = []
clock = pygame.time.Clock()
gamestate = {"level":1}
universe = [2000,2000]

text = ["" for i in xrange(pygame.display.Info().current_h / 15)]
achievement_queue = []

mapArea = pygame.Rect(pygame.display.Info().current_w - 210,pygame.display.Info().current_h - 210,200,200)
mapImage = pygame.Surface((200,200))

numPlanets = 0
numEnemies = 0

pause()

while not done:
	frame += 1
	score += 1
	# randomly generate planets
	while numPlanets < int((frame/50)**(.5)):
		r = random.randint(50,125)
		x = random.randint(0,2000)
		y = random.randint(0,2000)
		a = Planet(r,x,y)
		b =pygame.sprite.spritecollideany(a, allSprites)
		if not b:
			Planet(r,x,y, (planetSprites, allSprites))
			numPlanets = numPlanets + 1
		if b:
			break
	
	while numEnemies <= int((frame/777)):
		for i in range(int(math.sqrt(numPlanets))+1):
			a = random.randint(1,4)
			if a == 1 or a == 2:
				y = random.randint(0,2000)
				x = (a-1)*2000
			if a == 3 or a == 4:
				x = random.randint(0,2000)
				y = (a-3)*2000
			Projectile( "alien.png", truePos = Vector(x,y), groups = (rocketSprites, allSprites, enemySprites), maxSpeed = 3)
		numEnemies += 1
	
	mapImage.fill((10,10,10,77))
	mapImage = mapImage.convert_alpha()
	clock.tick(80)

	screen.fill((0,0,0,0))
	cols = pygame.sprite.groupcollide(singleRocket, planetSprites, False, False).iteritems()
	for r, ps in cols:
		for p in ps:
			if pygame.sprite.collide_mask(r,p):
				done = True
	cols = pygame.sprite.groupcollide(missileSprites, planetSprites, False, False).iteritems()
	for r, ps in cols:
		for p in ps:
			if pygame.sprite.collide_mask(r,p):
				r.kill()
	# not working!
	cols = pygame.sprite.groupcollide(singleRocket, enemySprites, False, False).iteritems()
	for r, ps in cols:
		for p in ps:
			if pygame.sprite.collide_mask(r,p):
				done = True
				
	cols = pygame.sprite.groupcollide(missileSprites, enemySprites, False, False).iteritems()
	for r, ps in cols:
		for p in ps:
			if pygame.sprite.collide_mask(r,p):
				r.kill()
				p.kill()
				score = score + 500
				
	cols = pygame.sprite.groupcollide(missileSprites, planetSprites, False, False).iteritems()
	for r, ps in cols:
		for p in ps:
			if pygame.sprite.collide_mask(r,p):
				r.kill()
	
	visible_planets = []
	screen_rect = screen.get_rect()
	for p in planetSprites:
		if screen_rect.colliderect(p.rect):
		  visible_planets.append(p)
	for projectile in rocketSprites:
		gravity_force = gravity(visible_planets, projectile.true.x, projectile.true.y)
		projectile.accelerate(gravity_force)
		
	for e in enemySprites:
		antigravity = gravity(planetSprites, e.true.x, e.true.y) * -2
		to_rocket = rocket.true - e.true
		to_rocket.normalize()
		e.accelerate(antigravity + to_rocket)

	rocketSprites.update()
	for s in allSprites:
		if s != rocket:
			s.scroll(rocket)	
	
	dirty_rects = allSprites.draw(screen)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
		  sys.exit()
	key = pygame.key.get_pressed()
	if key[pygame.K_UP]:
		rocket.forward()
	if key[pygame.K_DOWN]:
		rocket.backward()
	if key[pygame.K_RIGHT]:
		rocket.rotate(-7)
	if key[pygame.K_LEFT]:
		rocket.rotate(7)
	if key[pygame.K_ESCAPE]:
		done = True
	if key[pygame.K_SPACE]:
		# shoot missile
		shoot = False
		if lastMissile.sprite:
			if lastMissile.sprite.fuel < 250:
				shoot = True
		else:
			shoot = True
		if shoot:
			angle = math.radians(rocket.spin)
			direction = Vector(-math.sin(angle), -math.cos(angle))
			Projectile("gravymissle.png", direction * 10, rocket.true, rocket.spin, 10, (rocketSprites, allSprites, lastMissile, missileSprites), 500)
	if key[pygame.K_p]:
		pause()
	
	text[0] = "Rocket is at " + rocket.true.to_string(3)
	text[1] = "Bearing: " + str((rocket.spin+90) % 360) + " degrees"
	text[2] = "Velocity: " + rocket.vel.to_string(3)
	text[3] = "G force: " + gravity_force.to_string(3)
	text[6] = "Health: 100%"
	text[7] = "3 Enemies Left"
	text[9] = "FPS: " + str(clock.get_fps())
	text[-4] = "Achievement completed: Wormhole"
	text[-3] = "Achievement completed: Eliminate"
	text[-2] = "Achievement completed: Big Bang"
	text[-1] = "Score: " + str(score)
	for i,line in enumerate(text):
		if line != "":
		  textSurface = font.render(line, True, (39,255,20))
		  screen.blit(textSurface, (0,15*i))
		  dirty_rects.append(pygame.Rect(0,15*i,200,15))
	# map, TODO: draw enemies
	sf = universe[0]/mapArea.w
	scaled = rocket.true / sf
	pygame.draw.rect(mapImage, (255,255,255,255), pygame.Rect(scaled.x,scaled.y,5,5))
	for r in rocketSprites:
		pygame.draw.rect(mapImage, (255,255,0,255), pygame.Rect(scaled.x,scaled.y,3,3))
	for p in planetSprites:
		scaled = p.true / sf
		pygame.draw.circle(mapImage, (100,100,100,255), (int(scaled.x),int(scaled.y)), int(p.radius/sf))
	for e in enemySprites:
		scaled = e.true / sf
		pygame.draw.rect(mapImage, (255,0,0,255), pygame.Rect(scaled.x,scaled.y,5,5))
	screen.blit(mapImage, mapArea)
	dirty_rects.append(mapArea)
	
	pygame.display.update(dirty_rects)
	
end()
