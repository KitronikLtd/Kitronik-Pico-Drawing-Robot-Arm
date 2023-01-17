from SimplyServos import KitronikSimplyServos
from time import sleep_ms
from math import pi, acos, atan2, degrees, sqrt

# Class for controlling a Drawing Robot made from three servos
class DrawingRobot:
    def __init__(self, shoulderLength, elbowLength, xOffset, yOffset, moveDelay = 100):
        # Initialise base variables
        self.board = KitronikSimplyServos(3)
        self.shoulderLength = shoulderLength
        self.elbowLength = elbowLength
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.moveDelay = moveDelay
        self.shoulderServo = 90
        self.elbowServo = 90
        # Set servos to default position
        self.penUp()
        self.board.goToPosition(0, 90)
        self.board.goToPosition(1, 90)
        self.moveTo(0, 100)
    
    def penDown(self):
        self.board.goToPosition(2, 65)
        sleep_ms(250)
    
    def penUp(self):
        self.board.goToPosition(2, 140)
        sleep_ms(250)
    
    # Draw a rectangle start from x, y
    def drawRectangle(self, x, y, width, height):
        # Move to start position
        self.moveTo(x, y)
        # Now start drawing
        self.penDown()
        self.moveTo(x + width, y)
        self.moveTo(x + width, y + height)
        self.moveTo(x, y + height)
        self.moveTo(x, y)
        self.penUp()
    
    # Draw a line starting from x, y
    def drawLine(self, x, y, toX, toY):
        # Move to start position
        self.moveTo(x, y)
        # Now start drawing
        self.penDown()
        self.moveTo(toX, toY)
        self.penUp()
    
    # Draw an image from a file of x, y coordinates
    def drawImage(self, filename, divider = 10):
        f = open(filename, "r")
        line = f.readline()
        progress = 1

        # Loop until there are no more lines to draw from the file
        while line:
            print("Drawing line", progress)
            temp = list(line.split("[")[1].split("]")[0])
            i = 0
            x = 0
            y = 0
            draw = []
            
            # Loop through and decode the characters in the line
            while i < len(temp):
                # Start of a coordinate
                if temp[i] == "(":
                    strNum = ""
                    i += 1
                    # Retrive the x value
                    while temp[i] != "," and temp[i] != ".":
                        strNum += temp[i]
                        i += 1
                    # Ignore any decimals
                    if temp[i] == ".":
                        while temp[i] != ",":
                            i += 1
                    # Parse the integer and scale using divider
                    x = int(strNum) / divider
                    strNum = ""
                    i += 2
                    # Retrive the y value
                    while temp[i] != ")" and temp[i] != ".":
                        strNum += temp[i]
                        i += 1
                    # Ignore any decimals
                    if temp[i] == ".":
                        while temp[i] != ")":
                            i += 1
                    # Parse the integer and scale using divider
                    y = int(strNum) / divider
                    # Add the point to the line to draw
                    draw.append((x, y))
                    i += 1
                
                else:
                    i += 1
            
            # Move to start of the line
            self.moveTo(draw[0][0], draw[0][1])
            # Now start drawing
            self.penDown()
            
            # Continue drawing the rest of the line processed
            for i in range(len(draw) - 1):
                toX = draw[i + 1][0]
                toY = draw[i + 1][1]
                self.moveTo(toX, toY)
            
            self.penUp()
            # Move on to processing the next line
            line = f.readline()
            progress += 1

        f.close()
    
    # Move the pen to the given x, y coordinate
    def moveTo(self, x, y):
        # Retrieve the angles needed to move the pen to x, y
        shoulderAngle, elbowAngle = self.plot(x, y)
        
        # Difference between the current angles and new angles
        diff0 = self.shoulderServo - shoulderAngle
        diff1 = self.elbowServo - elbowAngle
        diffMin = max(abs(diff0), abs(diff1))
        
        # No difference to move
        if diff0 == 0 and diff1 == 0:
            return
        
        # Calculate a small step used to gradually move to the new angles
        step0 = abs(diff0) / (diffMin * 4)
        step1 = abs(diff1) / (diffMin * 4)
        
        # Loop until both angle differences are less than a step
        while abs(diff0) > step0 or abs(diff1) > step1:
            if diff0 > 0:
                # Decrease the servo angle
                self.shoulderServo -= step0
                diff0 -= step0
            elif diff0 < 0:
                # Increase the servo angle
                self.shoulderServo += step0
                diff0 += step0
            
            if diff1 > 0:
                # Decrease the servo angle
                self.elbowServo -= step1
                diff1 -= step1
            elif diff1 < 0:
                # Increase the servo angle
                self.elbowServo += step1
                diff1 += step1
            
            # Update servo positions
            self.board.goToPosition(0, self.shoulderServo)
            self.board.goToPosition(1, self.elbowServo)
            sleep_ms(self.moveDelay)
        
        # Finally set to exact value
        self.shoulderServo = shoulderAngle
        self.elbowServo = elbowAngle
        self.board.goToPosition(0, self.shoulderServo)
        self.board.goToPosition(1, self.elbowServo)
    
    # Convert an x, y coordinate into shoulder and elbow servo angles
    def plot(self, x, y):
        # Offset the x and y coordinates
        x += self.xOffset
        y += self.yOffset
        # Calculate the length of the invisible side
        lenHypot = sqrt(x ** 2 + y ** 2)
        
        # Stop if the coordinate is too far to reach
        if lenHypot > self.shoulderLength + self.elbowLength:
            return 0, 0

        # Calculate the angles inside the triangle for the shoulder and elbow
        angleInner = acos((self.shoulderLength ** 2 + lenHypot ** 2 - self.elbowLength ** 2)
                          / (2 * self.shoulderLength * lenHypot))
        angleOuter = acos((self.elbowLength ** 2 + self.shoulderLength ** 2 - lenHypot ** 2)
                          / (2 * self.elbowLength * self.shoulderLength))
        # Calculate the angle of the gap between the base and start of the triangle
        angleGap = atan2(y, x)

        # Convert the angles from radians to degrees
        shoulderAngle = degrees(angleInner + angleGap)
        elbowAngle = degrees(pi - angleOuter)

        return shoulderAngle, elbowAngle
