import pygame
from random import choice, randint

pygame.init()
pygame.display.init()

#  Utility functions
def loadSpriteSheet(path):
    """Load in a sprite sheet image"""
    image = pygame.image.load(path)
    return image

def spriteImage(spritesheet, size, xcoord, ycoord, width, height):
    """Function to extract an individual image from a Sprite sheet"""
    surface = pygame.Surface(size)
    surface.fill("Black")
    surface.blit(spritesheet, (0, 0), (xcoord, ycoord, width, height))
    surface.set_colorkey("Black")
    return surface

def loadImages(path, numimghor=1, numimgver=1, scaleimage=False, scalesize=(64, 64), rotateimage=False, rotation=0, simg=False):
    """Function to collect all sprites from a sheet into a single list"""
    spriteSheet = loadSpriteSheet(path)
    spriteSheetWidth = spriteSheet.get_width()
    spriteSheetHeight = spriteSheet.get_height()
    spriteWidth = spriteSheetWidth // numimghor
    spriteHeight = spriteSheetHeight // numimgver

    imageList = []
    for row in range(numimgver):
        for col in range(numimghor):
            if simg==True:
                image = spriteSheet
            else:
                image = spriteImage(spriteSheet,
                                    (spriteWidth, spriteHeight),
                                    col * spriteWidth, row * spriteHeight,
                                    spriteWidth, spriteHeight)
            if scaleimage == True:
                image = pygame.transform.scale(image, scalesize)
            if rotateimage == True:
                image = pygame.transform.rotate(image, rotation)
            imageList.append(image)
    return imageList

def testLoadedImages(window, xstart, ystart, imgwidth, imgheight, imglist, imgdict):
    """Test function to reflect all images on the game window."""
    for row, num in enumerate(imglist):
        for col, img in enumerate(imgdict[num]):
            window.blit(img, (xstart + (imgwidth * col), ystart + (imgheight * row)))


#  Classes
class Game:
    def __init__(self):
        self.sw = SCREENWIDTH
        self.sh = SCREENHEIGHT

        self.screen = pygame.display.set_mode((self.sw, self.sh))
        pygame.display.set_caption("Pipes")

        self.gameplay = PipeGamePlay()

        self.run = True

    def runGame(self):
        while self.run:
            self.input()
            self.update()
            self.draw()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    xPos, yPos = pygame.mouse.get_pos()
                    self.gameplay.insert_new_piece(xPos, yPos, XOFFSET, YOFFSET)

                if event.button == 3:
                    xPos, yPos = pygame.mouse.get_pos()
                    self.gameplay.removePiece(xPos, yPos, XOFFSET, YOFFSET)

    def update(self):
        self.gameplay.update()

    def draw(self):
        self.screen.fill("Black")
        #self.screen.blit(START["SRIGHT"][5], (500, 500))
        #testLoadedImages(self.screen, 64, 64, 64, 64, list(START.keys()), START)
        #testLoadedImages(self.screen, 64, 320, 64, 64, list(END.keys()), END)
        #testLoadedImages(self.screen, 704, 320, 64, 64, list(PIPES.keys()), PIPES)
        #testLoadedImages(self.screen, 64, 64, 64, 64, list(FLOW.keys()), FLOW)
        #testLoadedImages(self.screen, 64, 64, 64, 64, list(BOARD.keys()), BOARD)
        self.gameplay.draw(self.screen)
        pygame.display.update()

class PipeGamePlay:
    def __init__(self):
        self.rows = ROWS
        self.cols = COLUMNS

        self.grid = self._create_game_grid()
        self.pieces = {}

        self.startTime = 5000

        self._insert_start_pieces(START, self._verify_start, StartPiece)
        self._insert_start_pieces(END, self._verify_end, EndPiece)

        self.nextPieces = [choice(list(PIPES.keys())) for _ in range(6)]
        self.currentPiece = self.nextPieces.pop(0)

    def _create_game_grid(self):
        """Creates an empty game grid per the number of rows and columns"""
        grid = []
        for row in range(self.rows):
            line = []
            for col in range(self.cols):
                line.append(" ")
            grid.append(line)
        return grid

    def _insert_start_pieces(self, startpiecedict, verify_pos, newObject):
        """Randomly select a Starting piece, then insert it into the grid in a valid position"""
        piece = choice(list(startpiecedict.keys()))
        validStartPos = False
        row, col = 0, 0
        while not validStartPos:
            row, col = randint(0, self.rows - 1), randint(0, self.cols - 1)
            validStartPos = verify_pos(piece, self.rows, self.cols, row, col)

        self.pieces[(row, col)] = newObject(self, piece, row, col, XOFFSET, YOFFSET, self.startTime)
        self.grid[row][col] = self.pieces[(row, col)].piece
        return

    def _verify_start(self, startpiece, rows, cols, row, col):
        """Verify the starting location randomly selected"""
        if startpiece == "SRIGHT" and col != cols - 1: return True
        elif startpiece == "SLEFT" and col != 0: return True
        elif startpiece == "SUP" and row != 0: return True
        elif startpiece == "SDOWN" and row != rows - 1: return True
        return False

    def _verify_end(self, endpiece, rows, columns, row, col):
        if self.grid[row][col] != " ": return False
        if row == 0 and endpiece == "EDOWN": return False
        elif row == rows - 1 and endpiece == "EUP": return False
        elif col == 0 and endpiece == "ERIGHT": return False
        elif col == columns - 1 and endpiece == "ELEFT": return False
        else:
            if row < rows - 1:
                if self.grid[row + 1][col] != " ": return False
                if col < columns - 1:
                    if self.grid[row][col + 1] != " ": return False
                if col > 0:
                    if self.grid[row][col - 1] != " ": return False
            if row > 0:
                if self.grid[row - 1][col] != " ": return False
        return True

    def draw_game_board(self, window):
        for row in range(self.rows):
            for col in range(self.cols):
                if row % 2 == 0:
                    type = "Dark" if col % 2 == 0 else "Light"
                else:
                    type = "Light" if col % 2 == 0 else "Dark"
                window.blit(BOARD[type][0], (XOFFSET + (col * 64), YOFFSET + (row * 64)))

    def draw_current_next_pieces(self, window):
        window.blit(pygame.transform.scale(PIPES[self.currentPiece][0], (128, 128)), (XOFFSET - 128, 64))
        pygame.draw.rect(window, "White", (XOFFSET - 128, 64, 128, 128), 1)
        for num, item in enumerate(self.nextPieces):
            window.blit(PIPES[item][0], (XOFFSET - 96, YOFFSET + 194 + (64 * num)))
        return

    def _get_row_and_col(self, xpos, ypos, xoffset, yoffset):
        row = (ypos - yoffset) // CELLSIZE
        col = (xpos - xoffset) // CELLSIZE
        return row, col

    def insert_new_piece(self, xpos, ypos, xoffset, yoffset):
        row, col = self._get_row_and_col(xpos, ypos, xoffset, yoffset)
        if row < 0 or col < 0 or row >= self.rows or col >= self.cols:
            return

        #  Can change this code to allow for replacing current tiles: Remember to make a check for Start/end piece
        if self.grid[row][col] != " ":
            return

        self.grid[row][col] = self.currentPiece
        self.pieces[(row, col)] = Piece(self, self.currentPiece, row, col, xoffset, yoffset)

        self.currentPiece = self.nextPieces.pop(0)
        self.nextPieces.append(choice(list(PIPES.keys())))

    def removePiece(self, xpos, ypos, xoffset, yoffset):
        row, col = self._get_row_and_col(xpos, ypos, xoffset, yoffset)
        if row < 0 or col < 0 or row >= self.rows or col >= self.cols:
            return

        if self.grid[row][col] in [" ", 'SRIGHT', 'SLEFT', 'SUP', 'SDOWN', 'ERIGHT', 'ELEFT', 'EUP', 'EDOWN']:
            return

        self.grid[row][col] = " "
        del self.pieces[(row, col)]

    def update(self):
        for value in self.pieces.values():
            value.update()

    def draw(self, window):
        self.draw_game_board(window)
        self.draw_current_next_pieces(window)
        for piece in self.pieces.values():
            piece.draw(window)

class StartPiece:
    def __init__(self, game, piece, row, column, xoffset, yoffset, starttime):
        self.game = game
        self.piece = piece
        self.row = row
        self.col = column
        self.xPos = xoffset + (self.col * CELLSIZE)
        self.yPos = yoffset + (self.row * CELLSIZE)
        self.imgIndex = 0

        self.image = START[self.piece][self.imgIndex]
        self.rect = self.image.get_rect(topleft=(self.xPos, self.yPos))

        self.timer = Timer(starttime)
        self.timer.activate()

        self.active = True
        self.direction = self.piece[1:]

    def update(self):
        if not self.active:
            return

        self.timer.update()

        if self.timer.active == False and self.imgIndex < (len(START[self.piece])-1):
            self.updateImageAnimation()
            self.resetTimer(FLOWTIME)

        if self.imgIndex == len(START[self.piece]) - 1 and self.active == True:
            self.active = False
            currentPiece = {
                "SRIGHT": ["RIGHT", self.row, self.col+1, ["LR-RL", "LT-TL", "LB-BL"]],
                "SLEFT": ["LEFT", self.row, self.col-1, ["LR-RL", "RT-TR", "RB-BR"]],
                "SUP": ["UP", self.row-1, self.col, ["TB-BT", "LB-BL", "RB-BR"]],
                "SDOWN": ["DOWN", self.row+1, self.col, ["TB-BT", "LT-TL", "RT-TR"]]
            }
            for piece in currentPiece.keys():
                if self.piece == piece:
                    self.direction = currentPiece[piece][0]
                    row, col = currentPiece[piece][1], currentPiece[piece][2]
                    if self.game.grid[row][col] in currentPiece[piece][3]:
                        print(self.game.grid[row][col])
                        self.game.pieces[(row, col)].calcFlowDirection(self.direction)
                        self.game.pieces[(row, col)].active = True
                        return

    def updateImageAnimation(self):
        """Changes the image to reflect the updated animation image"""
        self.imgIndex += 1
        self.image = START[self.piece][self.imgIndex]

    def resetTimer(self, duration):
        """Resets the timer with a new time"""
        self.timer.duration = duration
        self.timer.activate()

    def draw(self, window):
        window.blit(self.image, self.rect)

class EndPiece:
    def __init__(self, game, piece, row, column, xoffset, yoffset, *args):
        self.game = game
        self.piece = piece
        self.row = row
        self.col = column
        self.xPos = xoffset + (self.col * CELLSIZE)
        self.yPos = yoffset + (self.row * CELLSIZE)
        self.end = "END"

        self.image = END[self.piece][0]
        self.rect = self.image.get_rect(topleft=(self.xPos, self.yPos))

    def update(self):
        pass

    def draw(self, window):
        window.blit(self.image, self.rect)

class Piece:
    def __init__(self, game, piece, row, col, xoffset, yoffset):
        self.game = game
        self.piece = piece
        self.row = row
        self.col = col
        self.xPos = xoffset + (self.col * CELLSIZE)
        self.yPos = yoffset + (self.row * CELLSIZE)
        self.imgIndex = 0

        self.image = PIPES[self.piece][0].convert_alpha()
        self.rect = self.image.get_rect(topleft=(self.xPos, self.yPos))

        self.timer = None

        self.active = False
        self.direction = None
        self.animImage = None
        self.start1 = True
        self.start2 = True

    def update(self):
        if not self.active:
            return

        self.timer.update()

        if self.timer.active == False and self.imgIndex < (len(FLOW[self.direction]) - 1):
            self.updateImageAnimation()
            self.resetTimer(FLOWTIME)

        if self.imgIndex == len(FLOW[self.direction]) - 1 and self.active == True:
            #self._calculate_next_piece_direction()
            pass

    def resetTimer(self, duration):
        """Resets the timer with a new time"""
        self.timer.duration = duration
        self.timer.activate()
        if self.start1:
            self.start1 = False
            return
        if not self.start1 and self.start2 == True:
            self.start2 = False

    def calcFlowDirection(self, lastDirection):
        cellDirect = {
            ("UP", "BT", "RT", "LT"): [["TB-BT", "LB-BL", "RB-BR"], {"TB-BT": "BT", "LB-BL": "BL", "RB-BR": "BR"}],
            ("DOWN", "TB", "RB", "LB"): [["TB-BT", "LT-TL", "RT-TR"], {"TB-BT": "TB", "LT-TL": "TL", "RT-TR": "TR"}],
            ("RIGHT", "LR", "TR", "BR"): [["LR-RL", "LB-BL", "LT-TL"], {"LR-RL": "LR", "LB-BL": "LB", "LT-TL": "LT"}],
            ("LEFT", "RL", "TL", "BL"): [["LR-RL", "RB-BR", "RT-TR"], {"LR-RL": "RL", "RB-BR": "RB", "RT-TR": "RT"}]
        }
        for celldir in cellDirect.keys():
            if lastDirection in celldir and self.piece in cellDirect[celldir][0]:
                self.direction = cellDirect[celldir][1][self.piece]

        self.timer = Timer(FLOWTIME)

    def updateImageAnimation(self):
        """Changes the image to reflect the updated water flow animation"""
        if self.start1 != True and self.start2 == True:
            self.animIndex = 0
        if self.start2 != True and self.start2 != True:
            self.imgIndex += 1
        if not self.start1 or not self.start2:
            self.animImage = FLOW[self.direction][self.imgIndex]

    def draw(self, window):
        if self.animImage:
            window.blit(self.animImage, self.rect)
        window.blit(self.image, self.rect)

class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.start_time = 0
        self.active = False
        self.current_time = 0

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        self.current_time = pygame.time.get_ticks()
        if self.current_time - self.start_time >= self.duration:
            self.deactivate()

#  Constants
SCREENWIDTH = 960
SCREENHEIGHT = 896
IMAGESIZE = (64, 64)
ROWS = 12
COLUMNS = 12
CELLSIZE = 64
FLOWTIME = 50
XOFFSET = 128
YOFFSET = 64

#  Assets
START = {
    "SRIGHT": loadImages("Assets/pipe_start_strip11.png", 11, 1, True, IMAGESIZE),
    "SLEFT": loadImages("Assets/pipe_start_strip11.png", 11, 1, True, IMAGESIZE, True, 180),
    "SUP":   loadImages("Assets/pipe_start_strip11.png", 11, 1, True, IMAGESIZE, True, 90),
    "SDOWN":   loadImages("Assets/pipe_start_strip11.png", 11, 1, True, IMAGESIZE, True, -90)
}
END = {
    "ERIGHT": loadImages("Assets/pipe_end.png", 1, 1, True, IMAGESIZE),
    "ELEFT":   loadImages("Assets/pipe_end.png", 1, 1, True, IMAGESIZE, True, 180),
    "EUP":   loadImages("Assets/pipe_end.png", 1, 1, True, IMAGESIZE, True, 90),
    "EDOWN":   loadImages("Assets/pipe_end.png", 1, 1, True, IMAGESIZE, True, -90)
}
PIPES = {
    "LR-RL": loadImages("Assets/horizontal/pipe_horizontal.png", 1, 1, True, IMAGESIZE,simg=True),
    "TB-BT": loadImages("Assets/vertical/pipe_vertical.png", 1, 1, True, IMAGESIZE,simg=True),
    "LT-TL": loadImages("Assets/top_left/pipe_corner_top_left.png", 1, 1, True, IMAGESIZE,simg=True),
    "LB-BL": loadImages("Assets/bottom_left/pipe_corner_bottom_left.png", 1, 1, True, IMAGESIZE,simg=True),
    "RT-TR": loadImages("Assets/top_right/pipe_corner_top_right.png", 1, 1, True, IMAGESIZE,simg=True),
    "RB-BR": loadImages("Assets/bottom_right/pipe_corner_bottom_right.png", 1, 1, True, IMAGESIZE,simg=True)
}
FLOW = {
    "LR": loadImages("Assets/horizontal/water_horizontal_left_strip11.png", 11, 1, True),
    "RL": loadImages("Assets/horizontal/water_horizontal_right_strip11.png", 11, 1, True),
    "TB": loadImages("Assets/vertical/water_vertical_top_strip11.png", 11, 1, True),
    "BT": loadImages("Assets/vertical/water_vertical_bottom_strip11.png", 11, 1, True),
    "LT": loadImages("Assets/top_left/water_corner_top_left_left_strip11.png", 11, 1, True),
    "TL": loadImages("Assets/top_left/water_corner_top_left_top_strip11.png", 11, 1, True),
    "LB": loadImages("Assets/bottom_left/water_corner_bottom_left_left_strip11.png", 11, 1, True),
    "BL": loadImages("Assets/bottom_left/water_corner_bottom_left_bottom_strip11.png", 11, 1, True),
    "RT": loadImages("Assets/top_right/water_corner_top_right_right_strip11.png", 11, 1, True),
    "TR": loadImages("Assets/top_right/water_corner_top_right_top_strip11.png", 11, 1, True),
    "RB": loadImages("Assets/bottom_right/water_corner_bottom_right_right_strip11.png", 11, 1, True),
    "BR": loadImages("Assets/bottom_right/water_corner_bottom_right_bottom_strip11.png", 11, 1, True)
}
BOARD = {
    "Dark": loadImages("Assets/board/BoardDark.png", 1, 1, True),
    "Light": loadImages("Assets/board/BoardLight.png", 1, 1, True)
}


if __name__=='__main__':
    game = Game()
    game.runGame()
    pygame.quit()
