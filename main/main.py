import math
import turtle
import numpy

scale = 100


turtle.speed(0)
turtle.penup()
turtle.setpos(-8* scale, -8*scale)
turtle.pendown()
for _ in range(4):
	turtle.forward(16*scale)
	turtle.left(90)

hz = 10


class Obstacle:
	x = 0
	y = 0
	r = 0.1
	gr = r*scale


class Robot:
	x = 0
	y = 0
	theta = 0
	vl = 0
	vr = 0
	w = 0.3
	targetx = 0
	targety = 0
	avg = 10
	crashed = False

	def __init__(self,x,y, theta, tx, ty):
		self.x = x
		self.y = y
		self.theta = theta
		self.targetx = tx
		self.targety = ty

		turtle.shape("circle")
		turtle.resizemode("user")
		turtle.shapesize(2, 2)

		turtle.penup()
		turtle.setpos(self.x *scale, self.y *scale)
		turtle.seth(self.theta)
		turtle.speed(0)
		turtle.pendown()

	def incvl(self, val):
		assert -0.05 <= val <= 0.05
		self.vl += val
		self.vl = numpy.clip(self.vl, -0.5, 0.5)

	def incvr(self, val):
		assert -0.05 <= val <= 0.05
		self.vr += val
		self.vr = numpy.clip(self.vr, -0.5, 0.5)

	def calculateObstacleDistance(self, x, y):
		closest = math.inf
		for o in obstacles:
			d = getDistance(x, y, o.x, o.y) - o.r
			if d < closest:
				closest = d
		return closest - (self.w/2)

	def step(self):
		nx, ny, nTheta = self.test(self.vl, self.vr, 1/hz)
		self.avg = 0.8* self.avg + 0.2* getDistance(self.x, self.y, nx, ny)

		self.x = nx
		self.y = ny
		self.theta = nTheta
		if self.calculateObstacleDistance(self.x, self.y)<0:
			print("CRASHED!")
			self.crashed = True
			turtle.pencolor("red")
			turtle.pensize(5)
		else:
			turtle.pensize(1)
			turtle.pencolor("black")
			self.crashed = False

		turtle.goto(self.x*scale, self.y*scale)

	def test(self, nvl, nvr, time):
		if math.fabs(nvr - nvl) < 0.0005:
			if nvr == 0:
				return self.x, self.y, self.theta
			nx = self.x + nvr * time * math.cos(self.theta)
			ny = self.y + nvl * time * math.sin(self.theta)
			nTheta = self.theta
		else:
			R = (self.w * (nvr + nvl)) / (2 * (nvr - nvl))
			dTheta = ((nvr - nvl) * (time)) / self.w
			nx = self.x + R * (math.sin(dTheta + self.theta) - math.sin(self.theta))
			ny = self.y - R * (math.cos(dTheta + self.theta) - math.cos(self.theta))
			nTheta = self.theta + dTheta
		return nx, ny, nTheta

	def run(self):
		i = 0
		while self.avg > 0.005 and i < 1000 and -9<self.x<9 and -9<self.y<9:
			best = 0, 0
			reward = -math.inf
			initd = getDistance(self.x, self.y, self.targetx, self.targety)
			for dl in numpy.linspace(-0.05, 0.05, 3):
				for dr in numpy.linspace(-0.05, 0.05, 3):
					r = 0
					for stage in numpy.linspace(1, 0, 2, endpoint=False):
						nx, ny, nt = self.test(self.vl + dl, self.vr + dr, stage)
						r += initd-getDistance(nx, ny, self.targetx, self.targety)
						r += self.calculateObstacleDistance(nx, ny)
					if r > reward:
						reward = r
						best = (dl, dr)

			self.incvl(best[0])
			self.incvr(best[1])
			self.step()
			i += 1
		return i


obstacles = []
for i in range(200):
	o = Obstacle()
	o.x = numpy.random.uniform(-8, 8)
	o.y = numpy.random.uniform(-8, 8)
	o.r = numpy.random.uniform(0.01, 0.17)
	obstacles.append(o)
	turtle.speed(0)
	turtle.seth(0)
	turtle.penup()
	turtle.setpos(o.x*scale, (o.y-o.r)*scale)
	turtle.pendown()
	turtle.circle(o.r*scale)


def getDistance(ax, ay, bx, by):
	return math.sqrt(math.pow(ax-bx, 2) + math.pow(ay-by, 2))


tx = numpy.random.uniform(-8, 8)
ty = numpy.random.uniform(-8, 8)

for i in range(100):
	rx = numpy.random.uniform(-8, 8)
	ry = numpy.random.uniform(-8, 8)
	rt = numpy.random.uniform(-math.pi, math.pi)
	bot = Robot(rx, ry, rt, tx, ty)
	if bot.calculateObstacleDistance(rx, ry) < 0.1:
		continue
	print(bot.run())


k = input("Done?...")
print(k)