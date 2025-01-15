#           game.py          #
# Written By GQX, Retire2053 #

# < Importations > #
# <<< Foreign Importations >>> #
import pygame
import pygame_menu
from random import randrange, choice
from multiprocessing.queues import Queue
from multiprocessing import Process
from warnings import warn
from PIL.Image import open as image
from copy import deepcopy
from json import load, dump
from traceback import print_exc as printException
from subprocess import run
from os.path import exists
# <<< Internal Importations >>> #
from py2048.data import *
from py2048.error import *

# < Main Class > #
class Py2048(Process):
    """
        # Py2048
        - tips: this discription uses MarkDown format, you can read the formatted version on https://pypi.org/project/py2048/ if the application you are using can't display it well
        ### Descriptions:
        This is a simple 2048 game on Python.  
        This class is based on pygame.  
        You can use the parameter "API" to control the game with your program.  
        Before initialize, You can use  
        >>> Py2048Instance()  
        or  
        >>> "Py2048Instance.start()"  
        to start main loop.  
        Start the main loop won't block your program, because this class is a child class of multiprocessing.Process.  
        ### Parameters:
        - API(bool, default False): set it to True when you want to control the game with your program. You must set those "......API" parameters when you set "API" to True  
        - operateAPI(multiprocessing.queues.Queue default None): operations  

    """
    # << Main Function >> #
    def __init__(
        self,
        #size : int = 4,
        name : str = "",
        operateAPI : Queue = None,
        getPuzzleAPI : Queue = None,
        endless : bool = False,
        debug : bool = False
    ):
        self.__debug = debug
        self.__print("[Info]Launch: Py2048 v1.0.0")
        self.__print("[Info]Initialize main module: Multiprocessing")
        super().__init__(target=self.__main, args=(4, name, operateAPI, getPuzzleAPI, endless))
        self.__print("[Info]Initialized OK")

    def __main(
        self,
        size : int = 4,
        name : str = "",
        operateAPI : Queue = None,
        getPuzzleAPI : Queue = None,
        endless : bool = False
    ):
        try:
            # <<< Assertions >>> #
            self.__print("[Info]Initialize main module: Pygame Pygame_menu")
            if operateAPI or getPuzzleAPI:
                if not (isinstance(operateAPI, Queue) and isinstance(getPuzzleAPI, Queue)):
                    raise TypeError("operateAPI and getPuzzleAPI must be instances of multiprocessing.queues.Queue")
                self.__API = True
            else:
                self.__API = False
            # <<< Varibles >>> #
            pygame.init()
            self.__steps = 0
            self.__score = 0
            self.__font = pygame.font.Font(FONTPATH, 100)  # 使用SourceCodePro, 大小为100
            self.__endless = endless
            self.__operateAPI = operateAPI
            self.__getPuzzleAPI = getPuzzleAPI
            self.__name = name
            self.__size = size
            self.__blocks = [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ]
            pygame.display.set_caption("Py2048", "Py2048")
            self.__clock = pygame.time.Clock()
            self.__window = pygame.display.set_mode((830, 1060), pygame.RESIZABLE)
            self.__pictures = [pygame.image.load(path) for path in PICTURES]
            self.__command = None
            if exists(SCORELIST):
                self.__scoreList = load(open(SCORELIST))
            else:
                self.__scoreList = []
            if self.__API:
                self.__status = "playing"
            else:
                self.__status = "selecting"
            self.__menu = pygame_menu.Menu("Welcome To Py2048", 830, 1060, theme=pygame_menu.themes.THEME_DARK)
            self.__nameInput = self.__menu.add.text_input('Player Name: ')
            self.__difficultySelector = self.__menu.add.selector('Difficulty: ', [("Easy",), ("Normal",)])
            self.__endlessSelector = self.__menu.add.selector("Endless: ", [("False", False), ("True", True)])
            self.__musicSelector = self.__menu.add.selector("Music: ", [("Enable",), ("Disable",)])
            self.__volumeSelector = self.__menu.add.selector("Music Volume: ", [(str(i) + "%", i / 100) for i in range(10, 101, 10)])
            self.__menu.add.button('Start', self.__startGame)
            self.__menu.add.button('Quit', exit)
            self.__buttonRects = {}
            self.__wait = 0
            self.__name = ""
            self.__difficulty = "Easy"
            musicValue = 0
            volumeValue = 0
            pygame.mixer.init()
            pygame.mixer.music.load(BGM)

            if not exists(TMPDIR):
                if run(["mkdir", TMPDIR]).returncode:
                    raise ShellError(f"error occured in shell command: \"mkdir {TMPDIR}\"")
            self.__randAddBlock()
            self.__randAddBlock()
            self.__updateWindowInfo()
            pygame.mixer.music.play(-1)

            self.__print("[Info]Initialized OK")
            self.__print("[Info]Start main loop")
            self.__print("[Info]Status: \"selecting\"")

            # <<< Main Loop >>> #
            while True:
                for line in self.__blocks:
                    for column in line:
                        if column == 4096:
                            warn("This version of Py2048 cannot display 4096, aborting game...", UserWarning)
                            self.__status = "failed"
                # <<<< Event Handler >>>> # 
                events = pygame.event.get()
                for event in events:
                    # <<<< Quit >>>> #
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        raise SystemExit # exit
                    # <<<< Window Resized By User >>>> #
                    if event.type == pygame.VIDEORESIZE:
                        self.__updateWindowInfo()
                        self.__updatePictures()

                    if self.__status == "display" and event.type == pygame.MOUSEBUTTONDOWN:
                        if self.__buttonRects["Restart"].collidepoint(event.pos):
                            self.__reInitialize()

                if self.__status == "selecting":
                    self.__menu.update(events)
                    if self.__musicSelector.get_value()[1] != musicValue:
                        if musicValue: # self.__musicSelector.get_value()[1] == 0
                            self.__print("[Info]Play music")
                            pygame.mixer.music.play(-1)
                            musicValue = 0
                        else: # self.__musicSelector.get_value()[1] == 1
                            self.__print("[Info]Stop music")
                            pygame.mixer.music.stop()
                            musicValue = 1

                    if self.__volumeSelector.get_value()[0][1] != volumeValue:
                        volumeValue = self.__volumeSelector.get_value()[0][1]
                        pygame.mixer.music.set_volume(volumeValue)
                        self.__print(f"[Info]Change music volume to {volumeValue * 100}%")

                    self.__menu.draw(self.__window)

                # <<<< Playing >>>> #
                elif self.__status == "playing":

                    self.__command = None

                    if self.__API:
                        if not self.__operateAPI.empty():
                            command = self.__operateAPI.get()
                            self.__print(f"[Info]Received command: {command}")
                            if command == "exit":
                                break
                            if command not in DIRECTIONS:
                                raise CommandError(f"invalid command: {command}")
                            self.__command = command
                    else:
                        pressedKeys = pygame.key.get_pressed()
                        for pygameKey, key in ((pygame.K_LEFT, LEFT), (pygame.K_RIGHT, RIGHT), (pygame.K_DOWN, DOWN), (pygame.K_UP, UP)):
                            if pressedKeys[pygameKey]:
                                self.__print(f"[Info]Received command: {key}")
                                self.__command = key
                                break

                    if self.__moveBlocks(self.__command):
                        self.__randAddBlock()
                        self.__updateStatus()
                    self.__drawBackGround()
                    self.__blitBlocks()
                    self.__drawBottomBar()

                    if self.__command and self.__API:
                        self.__getPuzzleAPI.put((self.__status, self.__steps, self.__score, self.__blocks))

                # <<<< Failed >>>> #
                elif self.__status == "failed":
                    self.__window = pygame.display.set_mode((800, 1020))
                    self.__window.fill(BLACKGREY)
                    self.__drawTitleWhenFailed()
                    self.__drawScoreList()
                    self.__print("[Info]Change status to \"wait-display\"")
                    self.__status = "wait-display"
                    self.__wait = 5
                
                elif "wait" in self.__status:
                    if self.__wait > 0:
                        self.__wait -= 0.1
                    else:
                        self.__status = self.__status[5:]
                        self.__print(f"[Info]Change status to {self.__status}")

                elif self.__status == "display":
                    if (self.__winWidth, self.__winHeight) != (830, 1060):
                        self.__window = pygame.display.set_mode((830, 1060))
                        self.__updateWindowInfo()
                        self.__updatePictures()
                        self.__drawBackGround()
                        self.__blitBlocks()
                        self.__drawBottomBar()
                        self.__drawRestartButton()

                else:
                    raise TaskScheduleError("There are no running UI tasks")

                pygame.display.flip()
                self.__clock.tick(10)
            pygame.quit()
        except KeyboardInterrupt:
            print("[Info]Interrupted")
        except SystemExit:
            print("[Info]Exited")
        except Exception as exception:
            printException()
            print(f"[Fatal]{exception}")
        finally:
            self.__quit()

    # <<< Other Functions >>> #
    def __drawRestartButton(self):
        buttonRect = pygame.Rect(600, 850, 200, 200)
        pygame.draw.rect(self.__window, RED, buttonRect)
        self.__window.blit(self.__font.render("RE", True, WHITE),
                           pygame.Rect(600, 850, 250, 100))
        self.__window.blit(self.__font.render("TRY", True, WHITE),
                           pygame.Rect(600, 950, 250, 100))
        self.__buttonRects["Restart"] = buttonRect

    def __drawScoreList(self): # 220
        for idx, nameAndScore in enumerate(self.__scoreList):
            if len(nameAndScore[0]) > 6:
                name = nameAndScore[0][:4] + ".."
            else:
                name = nameAndScore[0]
            self.__window.blit(self.__font.render(f"{idx + 1} {name} {nameAndScore[1]}", True, WHITE), pygame.Rect(0, 220 + 100 * idx, 800, 100))

    def __drawTitleWhenFailed(self):
        for idx, nameAndScore in enumerate(self.__scoreList):
            if nameAndScore[1] >= self.__score:
                continue
            self.__scoreList.insert(idx, (self.__name, self.__score))
            if len(self.__scoreList) > 8:
                self.__scoreList.pop()
            rank = idx
            break
        else:
            if len(self.__scoreList) < 8:
                rank = len(self.__scoreList)
                self.__scoreList.append((self.__name, self.__score))
            else:
                rank = -1
        if rank == -1:
            text = "Try Again"
        else:
            text = "Good Job!"
        self.__window.blit(self.__font.render(text, True, WHITE),
                           pygame.Rect(0, 0, 800, 100))
        if rank == -1:
            text = "NOT On List"
        else:
            if rank > 2: # > 3
                text = f"You: The {rank + 1}nd"
            else:
                text = f"You: The {["1st", "2nd", "3rd"][rank]}"
        
        self.__window.blit(self.__font.render(text, True, WHITE),
                            pygame.Rect(0, 110, 800, 100))
                    

    def __randAddBlock(self) -> None:
        while True:
            locX, locY = (randrange(0, self.__size), randrange(0, self.__size))
            if self.__blocks[locY][locX]: continue
            if self.__difficulty == "Easy":
                self.__blocks[locY][locX] = 2
            else:
                self.__blocks[locY][locX] = choice((2, 4))
            break

    def __drawBackGround(self) -> None:
        if self.__endless:
            self.__window.fill(ORANGE)
        else:
            self.__window.fill(WHITE) # fill background to white
        for i in range(1, 5):
            pygame.draw.line(self.__window, BLACK, (0, self.__blockLineSize * i - 5), (self.__squareSize, self.__blockLineSize * i - 5), 10)
            pygame.draw.line(self.__window, BLACK, (self.__blockLineSize * i - 5, 0), (self.__blockLineSize * i - 5, self.__squareSize), 10)

    def __blitBlocks(self) -> None:
        pictureIndex = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072]
        for lineN, line in enumerate(self.__blocks):
            for columnN, column in enumerate(line):
                if column:
                    self.__window.blit(self.__pictures[pictureIndex.index(column)],
                                       pygame.Rect(columnN * self.__blockLineSize, lineN * self.__blockLineSize,
                                                   self.__blockSize, self.__blockSize))

    def __moveBlocks(self, direction : str, test : bool = False) -> None:
        # - This Function is Written By Retire2053, the others are Written by GQX - #
        def getNeighbor(i, j, direction):
            if direction==LEFT: return i, j-1
            elif direction == RIGHT: return i, j+1
            elif direction == UP: return i-1, j
            elif direction == DOWN: return i+1, j
        
        def possibleActionDetect(i, j):
            # blank cell detection
            if self.__blocks[i][j]==0: return FREEZE
            
            # edge detection
            if direction==LEFT and j==0: return FREEZE
            if direction == RIGHT and j==self.__size-1: return FREEZE
            if direction == UP and i==0: return FREEZE
            if direction == DOWN and i==self.__size-1: return FREEZE

            # neigbour detection
            neighbor_i, neighbor_j = getNeighbor(i, j, direction)
            if self.__blocks[neighbor_i][neighbor_j] == 0 : return MOVE
            if self.__blocks[neighbor_i][neighbor_j] == self.__blocks[i][j]: return MERGE
            
            return FREEZE
        
        def move(i, j, direction):
            neighbor_i, neighbor_j = getNeighbor(i, j, direction)
            self.__blocks[neighbor_i][neighbor_j] = self.__blocks[i][j]
            self.__blocks[i][j] = 0

        def merge(i, j, direction, protected_pos):
            v = self.__blocks[i][j]
            merged_i, merged_j = getNeighbor(i, j, direction)
            
            if len(protected_pos)==0 or (merged_i, merged_j) not in protected_pos:
                self.__blocks[merged_i][merged_j] = 2 * v
                self.__blocks[i][j] = 0
                protected_pos.append((merged_i, merged_j))
                return True, 2 * v
            else: return False, 0

        # <<< moveBlocks-Main >>> #
        if direction:
            if test:
                blocksCopy = deepcopy(self.__blocks)
            protected_pos = []
            j_range = list(range(self.__size))
            action_count = 0
            for i in range(self.__size):
                if direction==LEFT or direction==UP:
                    j = 0
                    each_offset = 1
                elif direction==RIGHT or direction==DOWN:
                    j = self.__size-1
                    each_offset = -1
                
                while j in j_range:
                    if direction == LEFT or direction == RIGHT: x, y = i, j 
                    else: y, x = i, j 
                    action_possible = possibleActionDetect(x, y)
                    if action_possible == MOVE:
                        move(x, y, direction)
                        j -= each_offset
                        action_count += 1
                    elif action_possible == MERGE:
                        ret, value_add = merge(x, y, direction, protected_pos)
                        if ret:
                            action_count += 1
                            if not test:
                                self.__score += value_add
                        else: 
                            j+=each_offset
                    else:
                        j+=each_offset
            if action_count:
                if test:
                    self.__blocks = blocksCopy
                if not test:
                    self.__steps += 1
                return True
            else:
                return False

    def __updateStatus(self) -> None:
        if not self.__endless:
            for line in self.__blocks:
                for column in line:
                    if column == 2048:
                        self.__status = "success"
                        return
        for direction in DIRECTIONS:
            if self.__moveBlocks(direction, True):
                self.__status = "playing"
                break
        else:
            self.__status = "failed"
    
    def __drawBottomBar(self):
        self.__window.blit(self.__font.render(f"score:{self.__score}", True, BLACK),
                           pygame.Rect(0, self.__squareSize, self.__winWidth, 100))
        if self.__status == "display":
            text = "Game Over"
        elif self.__endless:
            text = "Endless " + self.__difficulty
        else:
            text = self.__difficulty
        self.__window.blit(self.__font.render(text, True, BLACK),
                           pygame.Rect(0, self.__squareSize + 100, self.__winWidth, 100))

    def __updateWindowInfo(self):
        self.__winWidth, self.__winHeight = self.__window.get_size()
        if self.__winWidth > self.__winHeight - 230:
            self.__squareSize = self.__winHeight - 230
        else: # winHeight - 230 > winWidth or winHeight - 230 == winWidth
            self.__squareSize = self.__winWidth
        
        self.__blockLineSize = self.__squareSize // 4
        self.__lineSize = self.__blockLineSize // 21
        self.__blockSize = self.__blockLineSize - self.__lineSize
    
    def __updatePictures(self):
        for idx, path in enumerate(PICTURES):
            try:
                image(path).resize((self.__blockSize, self.__blockSize)).save(f"{TMPDIR}tmp.png")
            except ValueError:
                pass
            self.__pictures[idx] = pygame.image.load(f"{TMPDIR}tmp.png")

    def __reInitialize(self):
        self.__blocks = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        self.__window = pygame.display.set_mode((830, 1060), pygame.RESIZABLE)
        self.__status = "selecting"
        self.__score = 0
        self.__steps = 0
        self.__difficulty = "Easy"
        self.__randAddBlock()
        self.__randAddBlock()

    def __startGame(self):
        self.__print("[Info]Change status to \"playing\"")
        self.__status = "playing"
        self.__menu.close()
        self.__name = self.__nameInput.get_value()
        self.__difficulty = self.__difficultySelector.get_value()[0][0]
        self.__endless = self.__endlessSelector.get_value()[0][1]

    def __print(self, text : str):
        if self.__debug:
            print(text)

    def __quit(self):
        dump(self.__scoreList, open(SCORELIST, "w"), indent=4)

    def __str__(self):
        return f"""Py2048(
status:{self.__status}
score:{self.__score}
steps:{self.__steps}
blocks:
{self.__blocks})"""
    
    def __hash__(self):
        return super().__hash__()
    
    def __call__(self) -> None:
        self.start()
    
    def __getattr__(self, name):
        warn(f"You are accessing a nonexistent attribute: {name}", UserWarning)