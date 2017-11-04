#!/usr/bin/env python3

# File: main.py 
# Description: Main tetris file
# Author: Pavel Benáček <pavel.benacek@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygame
import pdb

import random
import math
import block
import constants

class Tetris(object):
    """
    The class with the tetris game.
    """

    def __init__(self,rx,ry):
        """
        Parameters:
            - rx - resolution x
            - ry - resolution y
        """
        # Remember the resolution
        self.resx = rx
        self.resy = ry
        # Boards to draw
        self.board_up    = pygame.Rect(0,constants.BOARD_UP_MARGIN,rx,constants.BOARD_HEIGHT)
        self.board_down  = pygame.Rect(0,ry-constants.BOARD_HEIGHT,rx,constants.BOARD_HEIGHT)
        self.board_left  = pygame.Rect(0,constants.BOARD_UP_MARGIN,constants.BOARD_HEIGHT,ry)
        self.board_right = pygame.Rect(rx-constants.BOARD_HEIGHT,constants.BOARD_UP_MARGIN,constants.BOARD_HEIGHT,ry)
        # List of used blocks
        self.blk_list    = []
        # Compute start indexes
        self.start_x = math.ceil(rx/2.0)
        self.start_y = constants.BOARD_UP_MARGIN + constants.BOARD_HEIGHT + 5
        # Prepare blocks 
        self.block_data = (
            ([[0,0],[1,0],[2,0],[3,0]],constants.RED),
            ([[0,0],[0,1],[1,1],[1,2]],constants.GREEN),
            ([[0,0],[1,0],[2,0],[2,1]],constants.BLUE),
            ([[0,0],[0,1],[1,0],[1,1]],constants.ORANGE),
            ([[0,0],[0,1],[1,1],[1,2]],constants.GOLD),
            ([[0,0],[1,0],[2,0],[1,1]],constants.PURPLE),
            ([[0,0],[0,1],[1,1],[2,1]],constants.CYAN)
        )

    def apply_action(self):
        """
        Get the event and process it.
        """
        # Take the event
        for ev in pygame.event.get():
            # Check if the close button was fired
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.unicode == 'q'):
                self.done = True
            # Detect the key events
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_DOWN:
                    self.active_block.move(0,constants.BHEIGHT)
                if ev.key == pygame.K_LEFT:
                    self.active_block.move(-constants.BWIDTH,0)
                if ev.key == pygame.K_RIGHT:
                    self.active_block.move(constants.BWIDTH,0)
                if ev.key == pygame.K_SPACE:
                    self.active_block.rotate()
       
            # Detect if movement is detected
            if ev.type == constants.TIMER_MOVE_EVENT:
                self.active_block.move(0,constants.BHEIGHT)
       
    def run(self):
        # Initialize the game
        pygame.init()
        pygame.font.init()
        self.myfont = pygame.font.SysFont(pygame.font.get_default_font(),constants.FONT_SIZE)
        self.screen = pygame.display.set_mode((self.resx,self.resy))
        pygame.display.set_caption("Tetris")
        # Setup the time to move every few milisencos
        pygame.time.set_timer(constants.TIMER_MOVE_EVENT,constants.MOVE_TICK)
        # The main game loop
        self.done = False
        self.game_over = False
        self.new_block = True
        while not(self.done) and not(self.game_over):
            # Get the block and run the game logic
            self.get_block()
            self.game_logic()
            # Move the block down and update the screen
            self.draw_game()
        # Display the game_over and wait for a keypress
        if self.game_over:
            self.print_game_over()
        # Disable the screen
        pygame.font.quit()
        pygame.display.quit()        
   
    def print_game_over(self):
        """
        Print the game over string
        """
        # Print the game over text
        string = "Game Over"
        size_x,size_y = self.myfont.size(string)
        txt_surf = self.myfont.render(string,False,(255,255,255))
        self.screen.blit(txt_surf,(self.resx/2-size_x/2,self.resy/2))

        string = "Press q to continue"
        nsize_x,nsize_y = self.myfont.size(string)
        txt_surf = self.myfont.render(string,False,(255,255,255))
        self.screen.blit(txt_surf,(self.resx/2-nsize_x/2,self.resy/2+5+size_y))
        pygame.display.flip()

        # Wait untill the space is pressed
        while True: 
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.unicode == 'q'):
                    return

    def block_colides(self):
        """
        Check if the block colides with any other block
        """
        for blk in self.blk_list:
            # Check if the block is not the same
            if blk == self.active_block:
                continue 
            # Detect situations
            if(blk.check_collision(self.active_block.shape)):
                return True
        return False

    def game_logic(self):
        """
        Implement the game logic
        """
        # Remember the current configuration and try to 
        # apply the action
        self.active_block.backup()
        self.apply_action()
        # Border logic, check if we colide with down border or any
        # other borders. Also detect if we can move down
        down_board  = self.active_block.check_collision([self.board_down])
        any_border  = self.active_block.check_collision([self.board_left,self.board_up,self.board_right])
        block_any   = self.block_colides()
        # Restore the configuration if any collision was detected
        # Also, generate new block if down collision was detected.
        if down_board or any_border or block_any:
            self.active_block.restore()
        # So far so good, sample the previous state and try to move down. After that, detect
        # the the insertion of new block. The block new block is inserted if we reached the boarder
        # or we cannot move down.
        self.active_block.backup()
        self.active_block.move(0,constants.BHEIGHT)
        can_move_down = not self.block_colides()  
        self.active_block.restore()
        
        # If we are on the respawn and we cannot move --> bang!
        if not can_move_down and (self.start_x == self.active_block.x and self.start_y == self.active_block.y):
            self.game_over = True
        
        # Detect if can insert new block 
        if down_board or not can_move_down:
            self.new_block = True

    def draw_board(self):
        """
        Draw the white board around the box.
        """
        pygame.draw.rect(self.screen,constants.WHITE,self.board_up)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_down)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_left)
        pygame.draw.rect(self.screen,constants.WHITE,self.board_right)

    def get_block(self):
        """
        Add the new block into the game if is required
        """
        if self.new_block:
            # Get the block and add it into the block list(static for now)
            tmp = random.randint(0,len(self.block_data)-1)
            data = self.block_data[tmp]
            self.active_block = block.Block(data[0],self.start_x,self.start_y,self.screen,data[1])
            self.blk_list.append(self.active_block)
            self.new_block = False

    def draw_game(self):
        """
        Draw the whole scene
        """
        self.screen.fill((0,0,0))
        self.draw_board()
        # Draw all elements in the board
        for blk in self.blk_list:
            blk.draw()
        # Draw everything
        pygame.display.flip()

if __name__ == "__main__":
    Tetris(450,600).run()
