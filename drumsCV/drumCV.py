import pygame
import cv2
import numpy as np
import sys


# MAIN CLASS
class drumsCV(object):

	def __init__(self,width,height):
		self.width = width
		self.height = height
		(self.startScreen, self.freePlay, self.openWindow) = (True, False, False)

	def initAnimation(self):
		pygame.init()
		self.window = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("drumsCV")

	def run(self):
		self.initAnimation()
		while True:
			if self.startScreen:
				self.runStartScreen()
			elif self.freePlay:
				self.runDrums()

	# FUNCTION FOR DRUMS
	def runDrums(self):
		Drums(self.window).run()
		# BACK TO START
		self.freePlay = False
		self.startScreen = True

	# FUNCTION FOR START
	def runStartScreen(self):
		self.playDrumButton = startDraw(self.window).redrawAll()
		while True:
			self.responseStart()
			if not self.startScreen:
				break

	# ACTIONS ON START
	def responseStart(self):
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				# DRUMS
				if self.playDrumButton.collidepoint(pygame.mouse.get_pos()):
					self.startScreen = False
					self.freePlay = True
			# QUIT
			elif event.type == pygame.QUIT:
				sys.exit()


# START SCREEN
class startDraw(object):
	def __init__(self, window):
		self.window = window
		(self.width, self.height) = self.window.get_size()

	def initStart(self):
		self.options = ["Click Below", "LAUNCH"]
		self.textColor = (255,255,255)

	# REDRAWING
	def redrawAll(self):
		self.initStart()
		self.drawStartBG()
		self.drawStartHeader()
		self.drawOptions()
		self.drumsButton()
		pygame.display.flip()  # RE-UPDATE PYGAME WINDOW
		return (self.playDrumButton)

	def drawStartBG(self):
		background = pygame.image.load("startBG.jpg")
		self.window.blit(background, (0, 0))

	def drawStartHeader(self):
		# TEXT ALIGNMENT
		textX = self.width / 2
		textY = self.height / 20
		fontSize = 80
		font = pygame.font.Font(None, fontSize)
		header = "drumsCV"
		text = font.render(header, 1, self.textColor)
		# CENTER
		textPos = text.get_rect()
		textPos.centerx = textX
		textPos.centery = textY
		self.window.blit(text, textPos)

	def drawOptions(self):
		header = self.options[0]
		textX = self.width / 2
		textY = self.height / (len(self.options) + 1)
		fontSize = 30
		self.drawText(textX, textY, header, fontSize)

	def drawButton(self, centerX, centerY):
		# SIZE
		buttonWidth = 300
		buttonHeight = 100
		# POSITION
		startX = centerX - (buttonWidth / 2)
		startY = centerY - (buttonHeight / 2)
		rect = (startX, startY, buttonWidth, buttonHeight)
		color = (0, 0, 26)
		outlineWidth = 0
		pygame.draw.rect(self.window, color, rect, outlineWidth)
		pygame.draw.rect(self.window, (0, 0, 0), rect, 1)
		# GETTING THE BUTTON VALUE
		button = pygame.Rect(startX, startY, buttonWidth, buttonHeight)
		return button

	def drawText(self, textX, textY, header, fontSize):
		font = pygame.font.Font(None, fontSize)
		text = font.render(header, 1, (255, 255, 255))
		textPos = text.get_rect()
		textPos.centerx = textX
		textPos.centery = textY
		self.window.blit(text, textPos)

	def drumsButton(self):
		header = self.options[1]
		textX = centerX = self.width / 2
		textY = centerY = (2 * self.height) / (len(self.options) + 1)
		fontSize = 40
		self.playDrumButton = self.drawButton(centerX, centerY)
		self.drawText(textX, textY, header, fontSize)


# DRUMS
class Drums(object):
	def __init__(self, window):
		self.window = window
		(self.width, self.height) = self.window.get_size()

	def initAnimation(self):
		self.textColor = (0,0,0)
		self.run = True

		# SOUNDS
		self.snareSound = pygame.mixer.Sound("snareShort.wav")
		self.highSound = pygame.mixer.Sound("highShort.wav")
		self.tomSound = pygame.mixer.Sound("lowSnare.wav")
		self.smashSound = pygame.mixer.Sound("smash.wav")

		# RED & BLUE
		self.blueX0, self.blueY0 = 0, 0
		self.redX0, self.redY0 = 0, 0
		self.blueX1, self.blueY1 = 0, 0
		self.redX1, self.redY1 = 0, 0

		# INITIAL
		self.blueInsidePrevious = False
		self.redInsidePrevious = False
		self.blueInside = False
		self.redInside = False

		# PRE-LOADER
		self.window.fill((0, 0, 0))

	def run(self):
		self.initAnimation()
		vidCapture = cv2.VideoCapture(0)
		while True:
			self.drawBackButton()
			self.responseActions()
			ret, self.frame = vidCapture.read()
			self.resizeCameraInput()
			self.drawDrums()
			self.trackBlue()
			self.trackRed()
			self.drawBlueTrackers()
			self.drawRedTrackers()

			# RESETTING VALUES
			self.blueX0, self.blueY0 = self.blueX1, self.blueY1
			self.redX0, self.redY0 = self.redX1, self.redY1
			self.blueInsidePrevious = self.blueInside
			self.redInsidePrevious = self.redInside

			# OpenCV to PyGame
			image = self.cvimage_to_pygame()

			# FRAME DISPLAY
			self.window.blit(image, (0, 0))
			pygame.display.update()

			if not self.run:
				break

	# RESIZING FRAME
	def resizeCameraInput(self):
		ratio = 1000.0 / self.frame.shape[1]
		dim = (1000, int(self.frame.shape[0] * ratio))
		self.frame = cv2.resize(self.frame, dim, interpolation=cv2.INTER_CUBIC)

	# DRUM FRAMES
	def drawDrums(self):
		color = (255, 255, 255)  # frame_color
		drumWidth, drumHeight, outlineWidth = 170, 215, 3

		highStart = (self.highX0, self.highY0) = (40, 80)
		highEnd = (self.highX1, self.highY1) = (self.highX0 + drumWidth, self.highY0 + drumHeight)
		cv2.rectangle(self.frame, highStart, highEnd, color, 3)

		snareStart = (self.snareX0, self.snareY0) = (290, 455)
		snareEnd = (self.snareX1, self.snareY1) = (self.snareX0 + drumWidth, self.snareY0 + drumHeight)
		cv2.rectangle(self.frame, snareStart, snareEnd, color, outlineWidth)

		tomStart = (self.tomX0, self.tomY0) = (540, 455)
		tomEnd = (self.tomX1, self.tomY1) = (self.tomX0 + drumWidth, self.tomY0 + drumHeight)
		cv2.rectangle(self.frame, tomStart, tomEnd, color, outlineWidth)

		smashStart = (self.smashX0, self.smashY0) = (790, 80)
		smashEnd = (self.smashX1, self.smashY1) = (self.smashX0 + drumWidth, self.smashY0 + drumHeight)
		cv2.rectangle(self.frame, smashStart, smashEnd, color, outlineWidth)

	# TRACKERS
	# py_contours
	def drawBlueTrackers(self):
		try:
			areas = self.blueContours[0]
			moment = cv2.moments(areas)
			self.blueX1 = int(moment['m10']/moment['m00'])
			self.blueY1 = int(moment['m01']/moment['m00'])
			speed = Drums.determineDistance(self.blueX0, self.blueY0, self.blueX1, self.blueY1)
			# POINTER TO FOLLOW
			radius, color, thickness = 15, (255, 255, 255), 4
			cv2.circle(self.frame, (self.blueX1, self.blueY1), radius, color, thickness)
			self.detBSound(speed)
			# something might go wrong up there ^
		except:
			pass

	def drawRedTrackers(self):
		try:
			areas = self.redContours[0]
			moment = cv2.moments(areas)
			self.redX1 = int(moment['m10']/moment['m00'])
			self.redY1 = int(moment['m01']/moment['m00'])
			speed = Drums.determineDistance(self.redX0, self.redY0, self.redX1, self.redY1)
			# POINTER TO FOLLOW
			radius, color, thickness = 15, (255, 255, 255), 4
			cv2.circle(self.frame, (self.redX1, self.redY1), radius, color, thickness)
			self.detRSound(speed)
			# if something goes wrong up there, then this will follow it ^
		except:
			self.redInside = False

	def detBSound(self, speed):
		# CHECK THE BOUNDARY
		if self.snareX0 < self.blueX1 < self.snareX1 and self.snareY0 < self.blueY1 < self.snareY1 and speed > 10:
			self.blueInside = True
			# PLAY if not PREVIOUSLY in REGION
			if self.blueInside and not self.blueInsidePrevious:
				self.snareSound.play()

		# SAME GOES FOR EVERY SOUND
		elif self.highX0 < self.blueX1 < self.highX1 and self.highY0 < self.blueY1 < self.highY1 and speed > 10:
			self.blueInside = True
			if self.blueInside and not self.blueInsidePrevious:
				self.highSound.play()

		elif self.tomX0 < self.blueX1 < self.tomX1 and self.tomY0 < self.blueY1 < self.tomY1 and speed > 10:
			self.blueInside = True
			if self.blueInside and not self.blueInsidePrevious:
				self.tomSound.play()

		elif self.smashX0 < self.blueX1 < self.smashX1 and self.smashY0 < self.blueY1 < self.smashY1 and speed > 10:
			self.blueInside = True
			if self.blueInside and not self.blueInsidePrevious:
				self.smashSound.play()

		else:
			self.blueInside = False

	def detRSound(self, speed):
		if self.snareX0 < self.redX1 < self.snareX1 and self.snareY0 < self.redY1 < self.snareY1 and speed > 10:
			self.redInside = True
			if self.redInside and not self.redInsidePrevious:
				self.snareSound.play()

		elif self.highX0 < self.redX1 < self.highX1 and self.highY0 < self.redY1 < self.highY1:
			self.redInside = True
			if self.redInside and not self.redInsidePrevious:
				self.highSound.play()

		elif self.tomX0 < self.redX1 < self.tomX1 and self.tomY0 < self.redY1 < self.tomY1:
			self.redInside = True
			if self.redInside and not self.redInsidePrevious:
				self.tomSound.play()

		elif self.smashX0 < self.redX1 < self.smashX1 and self.smashY0 < self.redY1 < self.smashY1:
			self.redInside = True
			if self.redInside and not self.redInsidePrevious:
				self.smashSound.play()

		else:
			self.redInside = False

	# DOCS
	def trackBlue(self):
		# BRG to HSV
		hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
		kernel = np.ones((5, 5), np.uint8)
		# THRESHOLD
		lowerBlue = np.array([100, 150, 80], dtype=np.uint8)
		upperBlue = np.array([130, 255, 255], dtype=np.uint8)

		mask = cv2.inRange(hsv, lowerBlue, upperBlue)
		opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
		closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

		ret, thresh = cv2.threshold(closing, 127, 255, 0)
		contours, hierarchy = cv2.findContours(thresh, 1, 2)
		self.blueContours = contours

	def trackRed(self):
		hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
		kernel = np.ones((5,5),np.uint8)
		lowerRed = np.array([160,100,180], dtype = np.uint8)
		upperRed = np.array([180,255,255], dtype = np.uint8)

		mask = cv2.inRange(hsv,lowerRed,upperRed)
		opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
		closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

		ret, thresh = cv2.threshold(closing,127,255,0)
		contours, hierarchy = cv2.findContours(thresh,1,2)
		self.redContours = contours

	# DISTANCE b/w 2 POINTS
	@staticmethod
	def determineDistance(x0, y0, x1, y1):
		xComp = abs(x0-x1)
		yComp = abs(y0-y1)
		return (xComp**2 + yComp**2)**0.5

	# OpenCV to PYGAME
	def cvimage_to_pygame(self):	 
		# BRG TO RBGf
		image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
		for row in range(len(image)):
			image[row] = image[row][::-1]
		return pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "RGB")

	def drawBackButton(self):
		# LOCATION
		startX = 20
		startY = 750
		buttonWidth = 80
		buttonHeight = 50
		rect = (startX, startY, buttonWidth, buttonHeight)
		color = (0, 0, 26)
		outlineWidth = 0
		header = "BACK"
		pygame.draw.rect(self.window, color, rect, outlineWidth)
		pygame.draw.rect(self.window, (0, 0, 0), rect, 1)
		self.backButton = pygame.Rect(startX, startY, buttonWidth, buttonHeight)
		fontSize = 30
		textX = startX + buttonWidth / 2
		textY = startY + buttonHeight / 2
		font = pygame.font.Font(None, fontSize)
		text = font.render(header, 1, (225, 225, 225))
		textPos = text.get_rect()
		textPos.centerx = textX
		textPos.centery = textY
		self.window.blit(text, textPos)

	def responseActions(self):
		for evt in pygame.event.get():
			if evt.type == pygame.MOUSEBUTTONDOWN:
				co_ord = pygame.mouse.get_pos()
				if self.backButton.collidepoint(co_ord):
					self.run = False
			elif evt.type == pygame.QUIT:
				sys.exit()


def runDrumsCV():
	drumsCV(1000, 800).run()

runDrumsCV()