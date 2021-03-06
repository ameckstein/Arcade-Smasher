"""
Asteroid Smasher

Shoot space rocks in this demo program created with
Python and the Arcade library.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.asteroid_smasher
"""
import copy
import random
import math
import arcade
import os
import random


from datetime import datetime
from typing import cast

STARTING_ASTEROID_COUNT = 1
SCALE = 0.5
OFFSCREEN_SPACE = 0
# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 600
SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()
SCREEN_TITLE = "Asteroid Smasher"
LEFT_LIMIT = -OFFSCREEN_SPACE
RIGHT_LIMIT = SCREEN_WIDTH + OFFSCREEN_SPACE
BOTTOM_LIMIT = -OFFSCREEN_SPACE
TOP_LIMIT = SCREEN_HEIGHT + OFFSCREEN_SPACE
LIVES = 15
LIB_BASE_PATH = os.path.dirname(__file__) + '/lib/'
PLAYER_THRUST = 0.01
#
# def angle_of_vector(x, y):
#     return math.degrees(math.atan2(-y, x))
#
# def angle_of_line(x1, y1, x2, y2):
#     return math.degrees(math.atan2(-y1-y2, x2-x1))

# def vector_angle(x1,y1,x2,y2):
#     delta_y = ((y2)-(y1))**2
#     delta_x = ((x2)-(x1))**2
#     radian = math.atan2(delta_y, delta_x)**(1/2)
#     degrees = radian*(180/math.pi)
#
#     return degrees
#
# def azimuthAngle( x1, y1, x2, y2):
#     angle = 0.0;
#     dx = x2 - x1
#     dy = y2 - y1
#     if x2 == x1:
#         angle = math.pi / 2.0
#     if y2 == y1 :
#         angle = 0.0
#     elif y2 < y1 :
#         angle = 3.0 * math.pi / 2.0
#     elif x2 > x1 and y2 > y1:
#         angle = math.atan(dx / dy)
#     elif x2 > x1 and y2 < y1 :
#         angle = math.pi / 2 + math.atan(-dy / dx)
#     elif x2 < x1 and y2 < y1 :
#         angle = math.pi + math.atan(dx / dy)
#     elif x2 < x1 and y2 > y1 :
#         angle = 3.0 * math.pi / 2.0 + math.atan(dy / -dx)
#     return (angle * 180 / math.pi)
#
# def AngleBtw2Points(x1, y1, x2, y2):
#       changeInX = x2 - x1
#       changeInY = y2 - y1
#       return math.degrees(math.atan2(changeInY,changeInX)) #remove degrees if you want your answer in radians

def get_center_screen_cordinates():
    screen_center_x = math.floor(arcade.window_commands.get_display_size()[0] / 2)
    screen_center_y = math.floor(arcade.window_commands.get_display_size()[1] / 2)

    return (screen_center_x, screen_center_y)

def GetAngleBtwn2Points(x1, y1, x2, y2):
    '''
    Finds angle between two points in 2d space
    :param x1: starting x cord 
    :param y1: starting y cord 
    :param x2: target x cord 
    :param y2: target y cord
    :return: float degrees
    '''
    # https://www.youtube.com/watch?v=3DeW-7vbc50&ab_channel=NealHoltschulte
    radians = math.atan2((y1 - y2) , (x1 - x2))
    return math.degrees(radians)  + 90 # I dont know why, but add 90 to result

def CombineSpritelists(Sprint_List1: arcade.SpriteList(), Sprint_List2: arcade.SpriteList()):
    '''
    Takes 2 spritelists and combines them into a single list
    :param Sprint_List1 1st spritelist:
    :param Sprint_List2 second spritelist:
    :return combined sprite_list:
    '''

    #Return_List = copy.deepcopy(Sprint_List1)

    Return_List = SuperSpriteList()

    for Sprite1 in Sprint_List1:
        Return_List.append(Sprite1)
    for Sprite2 in Sprint_List2:
        if Sprite2 not in Return_List:
            Return_List.append(Sprite2)

    return Return_List

#def CombineListofSpriteLists(List_of_Sprite_Lists: ()):

class SuperSprite(arcade.Sprite):
    """
    arcade.Sprite with additional attributes for our game

    Derives from arcade.Sprite.
    """
    def __init__(self, filename=LIB_BASE_PATH + "enemy_A.png", scale=1):
        """ Set up the space ship. """

        # Call the parent Sprite constructor
        super().__init__(filename, scale)

        # Image offset angle for movement and other stuff, based on sprite image front and orientation.
        self.image_angle_offset = float(0)

        # where did sprite originate from? Used for bullets so ship can't shoot itself
        self.originating_source = self

        # represents what type of sprite this is. Used for differentiating sprite objects
        self.sprite_class = None
        self.sprite_subclass = None
        self.health = 0
        self.power_ups=[]
        self.firing_on = False
        self.last_fire = datetime.now()


class SuperSpriteList(arcade.SpriteList):
    """
    arcade.SuperSpriteList with additional functionality for our game

    Derives from arcade.Sprite.
    """

    def __init__(
            self,
            use_spatial_hash=None,
            spatial_hash_cell_size=128,
            is_static=False,
            atlas: "TextureAtlas" = None,
            capacity: int = 100,
            lazy: bool = False,
            visible: bool = True,
    ):

        super().__init__(use_spatial_hash,
            spatial_hash_cell_size,
            is_static,
            atlas,
            capacity,
            lazy,
            visible)


    def ListLenGetSprite(self, sprite_class: str):

        sprite_count = 0
        for sprite in self:
            if sprite.sprite_class == sprite_class:
                sprite_count+=1

        return sprite_count

    def ListSubsetSprite(self, sprite_class: str, visible: bool = True):

        list_subset = []#SuperSpriteList()

        for sprite in self:
            if not sprite_class and sprite.visible == visible:
                list_subset.append(sprite)
            elif sprite.sprite_class == sprite_class and sprite.visible == visible:
                list_subset.append(sprite)

        return list_subset

    def get_closest_sprite_notself(self, sprite: SuperSprite, tpl_sprite_class_to_check=[], tpl_sprite_class_to_ignore=[]): #-> Optional[Tuple[Sprite, float]]:
        """
        Given a Sprite and SpriteList, returns the closest sprite, and its distance.
    
        :param Sprite sprite: Target sprite
        :param SpriteList sprite_list: List to search for closest sprite.
    
        :return: Closest sprite.
        :rtype: Sprite
        """
        if len(self) == 0:
            return None

        min_pos = 0
        if self[0] == sprite:
            min_pos = 1
            if len(self) <= min_pos:
                return None

        min_distance = arcade.get_distance_between_sprites(sprite, self[min_pos])

        for i in range(min_pos, len(self)):
            if self[i] != sprite and self[i].sprite_class not in tpl_sprite_class_to_ignore:
                #print(sprite, self[i], self[min_pos], i, min_pos)
                if (tpl_sprite_class_to_check and self[i].sprite_class in tpl_sprite_class_to_check) \
                or not tpl_sprite_class_to_check:
                    distance = arcade.get_distance_between_sprites(sprite, self[i])
                    if distance < min_distance:
                        min_pos = i
                        min_distance = distance

        return self[min_pos], min_distance

    # def get_sprite_dict(self, sprite: SuperSprite):
    #
    #     sprite_dict = {}
    #     for i in self:
    #         sprite_dict[sprite]['center_x'] = i.center_x
    #         sprite_dict[sprite]['center_y'] = i.center_y




class TurningSprite(SuperSprite):
    """ Sprite that sets its angle to the direction it is traveling in. """
    def update(self):
        """ Move the sprite """
        super().update()
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))


class ShipSprite(SuperSprite):
    """
    Sprite that represents our space ship.

    Derives from arcade.Sprite.
    """
    def __init__(self, filename, scale):
        """ Set up the space ship. """

        # Call the parent Sprite constructor
        super().__init__(filename, scale)

        # Info on where we are going.
        # Angle comes in automatically from the parent class.
        self.thrust = 0
        self.speed = 0
        self.max_speed = 4
        self.drag = 0.05
        self.respawning = 0
        self.angle = 0
        self.respawn_count = 0
        self.guid = "Player"

        self.sprite_class = "Player"
        self.sprite_subclass = "Player1"

        # Mark that we are respawning.
        self.respawn()

    def respawn(self):
        """
        Called when we die and need to make a new ship.
        'respawning' is an invulnerability timer.
        """
        if self.respawn_count == 0:
            respawn_cordinates = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]
        else:
            respawn_cordinates = [random.randint(5, SCREEN_WIDTH - 5), random.randint(5, SCREEN_HEIGHT - 5)]

        self.respawn_count+=1

       # print(respawn_cordinates)
        # If we are in the middle of respawning, this is non-zero.
        print(f'Crash {self.speed}')
        self.respawning = 1
        self.center_x = respawn_cordinates[0]
        self.center_y = respawn_cordinates[1]

        # self.center_x = SCREEN_WIDTH / 2
        # self.center_y = SCREEN_HEIGHT / 2
        self.angle = 0
        self.speed = 0
        self.change_x = 0
        self.change_y = 0
        print(f'Respawn {self.speed}')
        #self.speed = 0

    def update(self):
        """
        Update our position and other particulars.
        """
        if self.respawning:
            self.respawning += 1
            self.alpha = self.respawning
            if self.respawning > 100:
                self.respawning = 0
                self.alpha = 255
        if self.speed > 0:
            self.speed -= self.drag
            if self.speed < 0:
                self.speed = 0

        if self.speed < 0:
            #self.speed += self.drag
            if self.speed > 0:
                self.speed = 0

        self.speed += self.thrust
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed:
            self.speed = -self.max_speed

        # self.change_x = -math.sin(math.radians(self.angle)) * self.speed
        # self.change_y = math.cos(math.radians(self.angle)) * self.speed
        # self.change_x = self.speed #  (self.speed * 1) + self.center_x #+ self.velocity[0] * self.center_x
        # self.change_y = self.speed # (self.speed * 1) + self.center_y # + self.velocity[1] * self.center_y

        if self.thrust == 0:
            self.change_x = self.velocity[0] #  (self.speed * 1) + self.center_x #+ self.velocity[0] * self.center_x
            self.change_y = self.velocity[1] # (self.speed * 1) + self.center_y # + self.velocity[1] * self.center_y

        #     self.change_x = self.speed * -self.velocity[0]  #  (self.speed * 1) + self.center_x #+ self.velocity[0] * self.center_x
        #     self.change_y = self.speed * self.velocity[1]  # (self.speed * 1) + self.center_y # + self.velocity[1] * self.center_y
        # #
        else:
            # self.change_x = -math.sin(math.radians(self.angle)) * self.speed
            # self.change_y = math.cos(math.radians(self.angle)) * self.speed
            self.forward(speed=self.thrust)

        #     self.change_x = -math.sin(math.radians(self.angle)) * self.speed
        #     self.change_y = math.cos(math.radians(self.angle)) * self.speed

        #     self.change_x = -math.sin(math.radians(self.angle)) * self.thrust * self.speed
        #     self.change_y = math.cos(math.radians(self.angle)) * self.thrust * self.speed

        self.center_x += self.change_x
        self.center_y += self.change_y

        # If the ship goes off-screen, move it to the other side of the window
        if self.right < 0:
            self.left = SCREEN_WIDTH

        if self.left > SCREEN_WIDTH:
            self.right = 0

        if self.bottom < 0:
            self.top = SCREEN_HEIGHT

        if self.top > SCREEN_HEIGHT:
            self.bottom = 0

        """ Call the parent class. """
        super().update()

class EnemyShip(SuperSprite):
    """ Sprite that represents an enemy ship. """

    def __init__(self, image_file_name:str() = LIB_BASE_PATH + "enemy_A.png", scale=float(), character=str() ):
        super().__init__(image_file_name, scale=scale)

        self.size = 0
        self.speed = .5
        self.last_fire = datetime.now()
        self.orientation = 1

        self.enemy_sound1 = LIB_BASE_PATH + "spaceEngine_000.ogg"
        self.enemy_sound2 = LIB_BASE_PATH + "spaceEngine_001.ogg"
        self.enemy_sound3 = LIB_BASE_PATH + "spaceEngine_003.ogg"
        self.enemy_sound4 = LIB_BASE_PATH + "spaceEngine_004.ogg"
        self.enemy_laser1 = LIB_BASE_PATH + "laser.png"
        self.sound = arcade.Sound(file_name=self.enemy_sound1, streaming=False)
        self.media_player = None
        self.sprite_class = 'Enemy_Ship'
        self.sprite_subclass = None
        self.character = character

        self.enemy_dict = {
                                 'Barry': {'Hunt_Type': 'Player', 'Max_Shoot_Speed': 6, 'Min_Shoot_Speed': 3, 'Intelligence': 3, 'Preservation': 3, 'Accuracy': 8, 'Image_File': LIB_BASE_PATH + "enemy_A.png", 'Sound_File': LIB_BASE_PATH + "spaceEngine_000.ogg", 'Image_Offset': 0, 'Color':(255,255,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75, 'Laser_Color': 'Purple'},
                                 'Larry': {'Hunt_Type': 'All', 'Max_Shoot_Speed': 15, 'Min_Shoot_Speed': 3, 'Intelligence': 3, 'Preservation': 3, 'Accuracy': 10, 'Image_File': LIB_BASE_PATH + "enemy_B.png", 'Sound_File': LIB_BASE_PATH + "spaceEngine_001.ogg", 'Image_Offset': 0, 'Color':(98,255,0), 'Power_ups': ['All'], 'Powerup_freq': 0.75, 'Laser_Color': 'Purple'},
                                 'Marry': {'Hunt_Type': 'Asteroid', 'Max_Shoot_Speed': 3, 'Min_Shoot_Speed': 3, 'Intelligence': 5, 'Preservation': 5, 'Accuracy': 6, 'Image_File': LIB_BASE_PATH + "enemy_C.png", 'Sound_File': LIB_BASE_PATH + "spaceEngine_002.ogg", 'Image_Offset': 0, 'Color':(255,0,98), 'Power_ups': ['All'], 'Powerup_freq': 0.75, 'Laser_Color': 'Purple'},
                                 'Harry': {'Hunt_Type': 'Asteroid', 'Max_Shoot_Speed': 3, 'Min_Shoot_Speed': 3, 'Intelligence': 6, 'Preservation': 6, 'Accuracy': 8, 'Image_File': LIB_BASE_PATH + "enemy_D.png", 'Sound_File': LIB_BASE_PATH + "spaceEngine_003.ogg", 'Image_Offset': 0, 'Color':(255,0,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75, 'Laser_Color': 'Purple'},
                                 'Garry': {'Hunt_Type': 'Asteroid', 'Max_Shoot_Speed': 4, 'Min_Shoot_Speed': 3, 'Intelligence': 4, 'Preservation': 4, 'Accuracy': 9, 'Image_File': LIB_BASE_PATH + "enemy_E.png", 'Sound_File': LIB_BASE_PATH + "spaceEngine_002.ogg", 'Image_Offset': 0, 'Color':(0,128,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75, 'Laser_Color': 'Purple'},
                                 'Fred': {'Hunt_Type': 'Random', 'Max_Shoot_Speed': 3, 'Min_Shoot_Speed': 1, 'Intelligence': 0, 'Preservation': 0, 'Accuracy': 10, 'Image_File': LIB_BASE_PATH + "ship_sidesB.png", 'Sound_File': LIB_BASE_PATH + "spaceEngine_001.ogg", 'Image_Offset': 0, 'Color':(3, 252, 252), 'Power_ups': ['All'], 'Powerup_freq': 0.75, 'Laser_Color': 'Purple'}
                          }
        #print(self.enemy_dict)

        range_count = 0
        #print(len(self.enemy_dict))
        if not self.character:
            rand_char = random.randrange(start=1,stop=len(self.enemy_dict))
            for char in self.enemy_dict:
                if range_count==rand_char:
                    self.sprite_subclass = char
                    self.character = char
                    break
                range_count+=1

        # print(LIB_BASE_PATH + "enemy_C.png")
        # print(self.enemy_dict[char]['Image_File'])
        #self.sprite_subclass = char
        self.hunt_type = self.enemy_dict[self.character]['Hunt_Type']
        self.max_shoot_speed = self.enemy_dict[self.character]['Max_Shoot_Speed']
        self.min_shoot_speed = self.enemy_dict[self.character]['Min_Shoot_Speed']
        self.intelligence = self.enemy_dict[self.character]['Intelligence']
        self.preservation = self.enemy_dict[self.character]['Preservation']
        self.accuracy = self.enemy_dict[self.character]['Accuracy']
        self.texture = arcade.load_texture(file_name=self.enemy_dict[self.character]['Image_File'], hit_box_algorithm='Detailed')
        self.sound = arcade.Sound(file_name=self.enemy_dict[self.character]['Sound_File'], streaming=False) #self.enemy_dict[char]['Sound_File']
        self.image_offset = self.enemy_dict[self.character]['Image_Offset']
        self.color = self.enemy_dict[self.character]['Color']
        self.power_ups = self.enemy_dict[self.character]['Power_ups']
        self.powerup_freq = self.enemy_dict[self.character]['Powerup_freq']
        # print(self.enemy_dict)
        print(self.sprite_subclass)

        self.playsound()

    #add disable method to keep from moving, play sound, or shooting

    def playsound(self):
        self.media_player = self.sound.play(loop=True)

    def stopsound(self):
        self.sound.stop(player=self.media_player)

    def kill(self):
        self.stopsound()

    def fire_laser(self, angle=float()):
        pass

    def update(self):
        """Move Ship Around"""
        #print(f'{self.sprite_subclass}, {self.orientation}, {self.change_x}, {self.change_y} ')
        #print(self.orientation)
        if self.orientation == 1:  # left to right
            self.change_x = self.speed
            self.change_y = 0

        elif self.orientation == 2:  # right to left
            self.change_x = - self.speed
            self.change_y = 0
            #print(f'orientation: Update:{self.orientation}, {self.center_x}, {self.center_y}, {SCREEN_WIDTH}, {SCREEN_HEIGHT}')


        elif self.orientation == 3:  # top to bottom
            self.change_x = 0
            self.change_y = self.speed

        else:  # bottom to top
            self.change_x = 0
            self.change_y = - self.speed

        #forward(speed: float = 1.0) Set a Sprite???s position to speed by its angle :param speed: speed factor


        self.center_x += self.change_x
        self.center_y += self.change_y

        # If the ship goes off-screen, move it to the other side of the window
        # if self.right < 0:
        #     self.left = SCREEN_WIDTH
        #
        # if self.left > SCREEN_WIDTH:
        #     self.right = 0
        #
        # if self.bottom < 0:
        #     self.top = SCREEN_HEIGHT
        #
        # if self.top > SCREEN_HEIGHT:
        #     self.bottom = 0



        super().update()

#--
class Powerup(SuperSprite):
    """ Sprite that represents an enemy ship. """

    def __init__(self, image_file_name=LIB_BASE_PATH + "enemy_A.png", scale=float(), powerup_name=str() ):
        super().__init__(image_file_name, scale=scale)

        self.size = 0
        self.speed = 0.5 #+ (random.randrange(0,10) * 0.1)
        self.angle = 0

        #self.sound = arcade.Sound(file_name=self.enemy_sound1, streaming=False)
        self.media_player = None
        self.sprite_class = 'Powerup'
        self.sprite_subclass = None

        self.powerup_dict = {
                                 'Life': {'Image_File': LIB_BASE_PATH + "powerupBlue_life.png", 'Sound_File': None, 'Image_Offset': 0, 'Color':(255,255,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75},
                                 'Shield': {'Image_File': LIB_BASE_PATH + "powerupBlue_shield.png", 'Sound_File': None, 'Image_Offset': 0, 'Color':(255,255,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75},
                                 #'Invincible': {'Image_File': LIB_BASE_PATH + "powerupBlue_star.png", 'Sound_File': None, 'Image_Offset': 0, 'Color':(255,255,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75},
                                 'Machine_Gun': {'Image_File': LIB_BASE_PATH + "powerupBlue_RapidFire.png", 'Sound_File': None, 'Image_Offset': 0, 'Color':(255,255,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75},
                          }

        range_count = 0
        if not powerup_name:
            rand_char = random.randint(a=1,b=len(self.powerup_dict))
            for powerup in self.powerup_dict:
                range_count+=1
                if range_count==rand_char:
                    self.sprite_subclass = powerup
                    print(f'{rand_char}, {self.sprite_subclass}, {len(self.powerup_dict)}')
                    break

        self.texture = arcade.load_texture(file_name=self.powerup_dict[powerup]['Image_File'], hit_box_algorithm='Detailed')
        if 'Sound_File' in self.powerup_dict[self.sprite_subclass] and self.powerup_dict[powerup]['Sound_File']:
            self.sound = arcade.Sound(file_name=self.powerup_dict[powerup]['Sound_File'], streaming=False) #self.powerup_dict[powerup]['Sound_File']
        self.image_offset = self.powerup_dict[powerup]['Image_Offset']
        self.color = self.powerup_dict[powerup]['Color']
        # print(self.powerup_dict)
        # print(self.sprite_subclass)

        #self.playsound()

    def playsound(self):
        self.media_player = self.sound.play(loop=True)

    def stopsound(self):
        pass
        #self.sound.stop(player=self.media_player)

    def kill(self):
        self.stopsound()

    def fire_laser(self, angle=float()):
        pass

    def update(self):
        """Move Ship Around"""
        #print(f'{self.sprite_subclass}, {self.orientation}, {self.change_x}, {self.change_y} ')
        #print(self.orientation)
        # self.forward(speed=self.speed)

        super().update()

#!--
class Satellite(SuperSprite):
    """ Sprite that represents an enemy ship. """

    def __init__(self, image_file_name=str(), scale=float(), character=str() ):
        super().__init__(image_file_name, scale=scale)

        self.size = 0
        self.speed = 0.5 + (random.randrange(0,10) * 0.1)
        self.last_fire = datetime.now()
        self.orientation = 1

        #self.sound = arcade.Sound(file_name=self.enemy_sound1, streaming=False)
        self.media_player = None
        self.sprite_class = 'Satellite'
        self.sprite_subclass = None

        self.enemy_dict = {
                                 'Jerry': {'Image_File': LIB_BASE_PATH + "Station_A.png", 'Sound_File': None, 'Image_Offset': 0, 'Color':(255,255,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75},
                                 'Merry': {'Image_File': LIB_BASE_PATH + "Station_B.png", 'Sound_File': None, 'Image_Offset': 0, 'Color':(255,255,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75},
                                 'Ferry': {'Image_File': LIB_BASE_PATH + "Station_C.png", 'Sound_File': None, 'Image_Offset': 0, 'Color':(255,255,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75},
                                 'Kerry': {'Image_File': LIB_BASE_PATH + "Station_A.png", 'Sound_File': None, 'Image_Offset': 0, 'Color':(34,0,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75},
                                 'Nerry': {'Image_File': LIB_BASE_PATH + "Station_B.png", 'Sound_File': None, 'Image_Offset': 0, 'Color':(250,82,255), 'Power_ups': ['All'], 'Powerup_freq': 0.75},
                                 'Werry': {'Image_File': LIB_BASE_PATH + "Station_C.png", 'Sound_File': None, 'Image_Offset': 0, 'Color':(23,169,0), 'Power_ups': ['All'], 'Powerup_freq': 0.75},
                          }
        #print(self.enemy_dict)

        range_count = 0
        #print(len(self.enemy_dict))
        if not character:
            rand_char = random.randrange(start=1,stop=len(self.enemy_dict))
            for char in self.enemy_dict:
                if range_count==rand_char:
                    self.sprite_subclass = char
                    break
                range_count+=1

        #print(LIB_BASE_PATH + "enemy_C.png")
        self.sprite_subclass = char
        self.texture = arcade.load_texture(file_name=self.enemy_dict[char]['Image_File'], hit_box_algorithm='Detailed')
        if 'Sound_File' in self.enemy_dict[self.sprite_subclass] and self.enemy_dict[char]['Sound_File']:
            self.sound = arcade.Sound(file_name=self.enemy_dict[char]['Sound_File'], streaming=False) #self.enemy_dict[char]['Sound_File']
        self.image_offset = self.enemy_dict[char]['Image_Offset']
        self.color = self.enemy_dict[char]['Color']
        self.power_ups = self.enemy_dict[char]['Power_ups']
        self.powerup_freq = self.enemy_dict[char]['Powerup_freq']
        # print(self.enemy_dict)
        #print(self.sprite_subclass)

        #self.playsound()

    def playsound(self):
        self.media_player = self.sound.play(loop=True)

    def stopsound(self):
        pass
        #self.sound.stop(player=self.media_player)

    def kill(self):
        self.stopsound()

    def fire_laser(self, angle=float()):
        pass

    def update(self):
        """Move Ship Around"""
        #print(f'{self.sprite_subclass}, {self.orientation}, {self.change_x}, {self.change_y} ')
        #print(self.orientation)
        if self.orientation == 1:  # left to right
            self.change_x = self.speed
            self.change_y = 0

        elif self.orientation == 2:  # right to left
            self.change_x = - self.speed
            self.change_y = 0
            #print(f'orientation: Update:{self.orientation}, {self.center_x}, {self.center_y}, {SCREEN_WIDTH}, {SCREEN_HEIGHT}')


        elif self.orientation == 3:  # top to bottom
            self.change_x = 0
            self.change_y = self.speed

        else:  # bottom to top
            self.change_x = 0
            self.change_y = - self.speed

        #forward(speed: float = 1.0) Set a Sprite???s position to speed by its angle :param speed: speed factor


        self.center_x += self.change_x
        self.center_y += self.change_y

        # If the ship goes off-screen, move it to the other side of the window
        # if self.right < 0:
        #     self.left = SCREEN_WIDTH
        #
        # if self.left > SCREEN_WIDTH:
        #     self.right = 0
        #
        # if self.bottom < 0:
        #     self.top = SCREEN_HEIGHT
        #
        # if self.top > SCREEN_HEIGHT:
        #     self.bottom = 0



        super().update()


#--



class AsteroidSprite(SuperSprite):
    """ Sprite that represents an asteroid. """

    def __init__(self, image_file_name, scale):
        super().__init__(image_file_name, scale=scale)
        self.size = 0
        self.sprite_class = 'Asteroid'
        self.sprite_subclass = None

    def update(self):
        """ Move the asteroid around. """
        if self.visible:
            super().update()
            if self.center_x < LEFT_LIMIT:
                self.center_x = RIGHT_LIMIT
            if self.center_x > RIGHT_LIMIT:
                self.center_x = LEFT_LIMIT
            if self.center_y > TOP_LIMIT:
                self.center_y = BOTTOM_LIMIT
            if self.center_y < BOTTOM_LIMIT:
                self.center_y = TOP_LIMIT


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=False)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.frame_count = 0

        self.game_over = False

        # Sprite lists
        self.player_sprite_list = arcade.SpriteList(use_spatial_hash=True)
        self.asteroid_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_ship_list = arcade.SpriteList(use_spatial_hash=True)
        self.bullet_list = arcade.SpriteList(use_spatial_hash=True)
        self.ship_life_list = arcade.SpriteList()

        #self.mytexture = arcade.load_texture(file_name=LIB_BASE_PATH+"ship_A_H.png", hit_box_algorithm='Detailed')

        self.velocity = 0
        # Set up the player
        self.score = 0
        self.player_sprite = None
        #self.lives = 13

        # Sounds
        self.laser_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound1 = arcade.load_sound(":resources:sounds/explosion1.wav")
        self.hit_sound2 = arcade.load_sound(":resources:sounds/explosion2.wav")
        self.hit_sound3 = arcade.load_sound(":resources:sounds/hit1.wav")
        self.hit_sound4 = arcade.load_sound(":resources:sounds/hit2.wav")
        self.enemy_sound1 = arcade.load_sound(LIB_BASE_PATH + "spaceEngine_000.ogg")
        self.enemy_sound2 = arcade.load_sound(LIB_BASE_PATH + "spaceEngine_001.ogg")
        self.enemy_sound3 = arcade.load_sound(LIB_BASE_PATH + "spaceEngine_002.ogg")
        self.enemy_sound4 = arcade.load_sound(LIB_BASE_PATH + "spaceEngine_003.ogg")

        self.hit_list_sprites = {'Class': {}, 'SubClass':{}, 'GUID':{}} #Dict of hit lists by type
        self.non_hit_list_sprites = {'Class':{}, 'SubClass':{}, 'GUID':{}} #Dict of hit pairs to be ignored by type

        self.hit_list_sprites['Class']['Player'] = ['Enemy_Ship', 'Player',  'Asteroid', 'Bullet', 'Satellite', 'Powerup']
        self.hit_list_sprites['Class']['Enemy_Ship'] = ['Enemy_Ship', 'Player',  'Asteroid', 'Bullet', 'Satellite', 'Powerup', 'Shield']
        self.hit_list_sprites['Class']['Asteroid'] = ['Enemy_Ship', 'Player',  'Asteroidx', 'Bullet', 'Shield']
        self.hit_list_sprites['Class']['Bullet'] = ['Enemy_Ship', 'Player',  'Asteroid', 'Bullet', 'Satellite', 'Shield']
        self.hit_list_sprites['Class']['Shield'] = ['Enemy_Ship', 'Player',  'Asteroid', 'Bullet', 'Satellite', 'Shield']

        self.round_dict = {
                            1: {'Astroids': [3,0,0], 'Enemy_Ship_Rate': 5, 'Enemy_Fire_Rate': 1.0, 'Satellite_Rate':  5,
                                'Max_Enemies': 1, 'Max_Satellites':  1, 'Powerups':[]},
                            2: {'Astroids': [3,2,0], 'Enemy_Ship_Rate': 10, 'Enemy_Fire_Rate': 1.0, 'Satellite_Rate': 10,
                                'Max_Enemies': 1, 'Max_Satellites': 1, 'Powerups': []},
                            3: {'Astroids': [4,2,1], 'Enemy_Ship_Rate': 15, 'Enemy_Fire_Rate': 1.0, 'Satellite_Rate': 15,
                                'Max_Enemies': 1, 'Max_Satellites': 1, 'Powerups': []},
                            4: {'Astroids': [4,5,3], 'Enemy_Ship_Rate': 20, 'Enemy_Fire_Rate': 1.0, 'Satellite_Rate': 20,
                                'Max_Enemies': 1, 'Max_Satellites': 1, 'Powerups': []},
                            5: {'Astroids': [5,3,3], 'Enemy_Ship_Rate': 25, 'Enemy_Fire_Rate': 1.0, 'Satellite_Rate': 25,
                                'Max_Enemies': 1, 'Max_Satellites': 1, 'Powerups': []},
                            6: {'Astroids': [5,5,4], 'Enemy_Ship_Rate': 30, 'Enemy_Fire_Rate': 1.0, 'Satellite_Rate': 30,
                                'Max_Enemies': 2, 'Max_Satellites': 1, 'Powerups': []},
                            7: {'Astroids': [6,3,2], 'Enemy_Ship_Rate': 35, 'Enemy_Fire_Rate': 1.0, 'Satellite_Rate': 35,
                                'Max_Enemies': 2, 'Max_Satellites': 1, 'Powerups': []},
                            8: {'Astroids': [6,6,5], 'Enemy_Ship_Rate': 40, 'Enemy_Fire_Rate': 1.0, 'Satellite_Rate': 40,
                                'Max_Enemies': 2, 'Max_Satellites': 1, 'Powerups': []},
                            9: {'Astroids': [7,7,5], 'Enemy_Ship_Rate': 45, 'Enemy_Fire_Rate': 1.0, 'Satellite_Rate': 45,
                                'Max_Enemies': 2, 'Max_Satellites': 1, 'Powerups': []},
                           10: {'Astroids': [7,8,6], 'Enemy_Ship_Rate': 50, 'Enemy_Fire_Rate': 1.0, 'Satellite_Rate': 50,
                                'Max_Enemies': 3, 'Max_Satellites': 2, 'Powerups': []}
                    }
        self.round = 1
        # self.max_enemies = self.round_dict[self.round]['Max_Enemies']
        # self.max_satellites = self.round_dict[self.round]['Max_Satellites']
        # self.enemy_generate_rate = self.round_dict[self.round]['Enemy_Ship_Rate']
        # self.satellite_rate = self.round_dict[self.round]['Satellite_Rate']
        # self.astroids=self.round_dict[self.round]['Astroids']
        #
        self.resource_lib_dict = {
            'Images':
                {
                    'Large_Meteor':
                    {'Image_List':
                        [[":resources:images/space_shooter/meteorGrey_big1.png",0.5],
                         [":resources:images/space_shooter/meteorGrey_big2.png",0.5],
                         [":resources:images/space_shooter/meteorGrey_big3.png",0.5],
                         [":resources:images/space_shooter/meteorGrey_big4.png",0.5],
                         [LIB_BASE_PATH + "meteor_detailedLarge.png",0.5],
                         [LIB_BASE_PATH + "meteor_squareDetailedLarge.png",0.5]]
                    },
                    'Medium_Meteor':
                    {'Image_List':
                    [[":resources:images/space_shooter/meteorGrey_med1.png",0.5],
                     [":resources:images/space_shooter/meteorGrey_med2.png",0.5]]
                    },
                    'Small_Meteor':
                    {'Image_List':
                    [[":resources:images/space_shooter/meteorGrey_small1.png",0.5],
                     [":resources:images/space_shooter/meteorGrey_small2.png",0.5],
                      [LIB_BASE_PATH + "meteor_squareSmall.png",0.5],
                      [LIB_BASE_PATH + "meteor_squareDetailedSmall.png",0.5]]
                    },
                    'Tiny_Meteor':
                    {'Image_List':
                    [[":resources:images/space_shooter/meteorGrey_tiny1.png",0.5],
                             [":resources:images/space_shooter/meteorGrey_tiny2.png",0.5]]
                    },
                    'bullet':
                        {'Blue':[[":resources:images/space_shooter/laserBlue01.png", 0.75]],
                        'Purple': [[LIB_BASE_PATH + "Purple_laser2_H.png", 0.25]]}
                }
        }

    def start_new_round(self, round=0):
        #clear game prite list

        if round <= 0:
            self.round += 1
            print('!', round)
        else:
            self.round = round
            print('?', round)
        print(self.round)
        self.clear_game_sprites()


        for i in range(self.round_dict[self.round]['Astroids'][0]):
            image_no = random.randrange(len(self.resource_lib_dict['Images']['Large_Meteor']['Image_List']))
            print(self.resource_lib_dict['Images']['Large_Meteor']['Image_List'][1])
            enemy_sprite = AsteroidSprite(self.resource_lib_dict['Images']['Large_Meteor']['Image_List'][image_no][0]
                                          , self.resource_lib_dict['Images']['Large_Meteor']['Image_List'] [image_no][1])
            enemy_sprite.guid = "Asteroid"

            enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)
            enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)

            enemy_sprite.change_x = random.random() * 2 - 1
            enemy_sprite.change_y = random.random() * 2 - 1

            enemy_sprite.change_angle = (random.random() - 0.5) * 2
            enemy_sprite.size = 4
            self.game_sprite_list.append(enemy_sprite)

        for i in range(self.round_dict[self.round]['Astroids'][1]):
            image_no = random.randrange(len(self.resource_lib_dict['Images']['Medium_Meteor']['Image_List'][0]))
            enemy_sprite = AsteroidSprite(self.resource_lib_dict['Images']['Medium_Meteor']['Image_List'][image_no][0]
                                          , self.resource_lib_dict['Images']['Medium_Meteor']['Image_List'][image_no][1])
            enemy_sprite.guid = "Asteroid"

            enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)
            enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)

            enemy_sprite.change_x = random.random() * 2 - 1
            enemy_sprite.change_y = random.random() * 2 - 1

            enemy_sprite.change_angle = (random.random() - 0.5) * 2
            enemy_sprite.size = 4
            self.game_sprite_list.append(enemy_sprite)

        for i in range(self.round_dict[self.round]['Astroids'][2]):
            image_no = random.randrange(len(self.resource_lib_dict['Images']['Small_Meteor']['Image_List']))
            enemy_sprite = AsteroidSprite(self.resource_lib_dict['Images']['Small_Meteor']['Image_List'][image_no][0]
                                          , self.resource_lib_dict['Images']['Small_Meteor']['Image_List'][image_no][1])
            enemy_sprite.guid = "Asteroid"

            enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)
            enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)

            enemy_sprite.change_x = random.random() * 2 - 1
            enemy_sprite.change_y = random.random() * 2 - 1

            enemy_sprite.change_angle = (random.random() - 0.5) * 2
            enemy_sprite.size = 4
            self.game_sprite_list.append(enemy_sprite)

    def clear_game_sprites(self):

        for sprite in self.game_sprite_list:
            if sprite.sprite_class != 'Player':
                sprite_index = self.game_sprite_list.index(sprite)
                self.game_sprite_list.pop(sprite_index)

    def predraw_sprites(self):

        place_x_cord = arcade.window_commands.get_display_size()[0] + 50
        place_y_cord = arcade.window_commands.get_display_size()[0] + 50


        for i in range(self.round_dict[self.round]['Astroids'][0]):
            image_no = random.randrange(len(self.resource_lib_dict['Images']['Large_Meteor']['Image_List']))
            enemy_sprite = AsteroidSprite(self.resource_lib_dict['Images']['Large_Meteor']['Image_List'][image_no][0]
                                          , self.resource_lib_dict['Images']['Large_Meteor']['Image_List'][image_no][1])
            enemy_sprite.guid = "Asteroid"

            enemy_sprite.center_y = place_y_cord
            enemy_sprite.center_x = place_x_cord
            place_x_cord = enemy_sprite.right + 50

            enemy_sprite.size = 4
            enemy_sprite.visible = False
            self.game_sprite_list.append(enemy_sprite)

        sprite_count = 3
        sprite_count = (self.round_dict[self.round]['Astroids'][0] * 3) + self.round_dict[self.round]['Astroids'][1]

        for i in range(sprite_count):
            image_no = random.randrange(len(self.resource_lib_dict['Images']['Medium_Meteor']['Image_List'][0]))
            enemy_sprite = AsteroidSprite(self.resource_lib_dict['Images']['Medium_Meteor']['Image_List'][image_no][0]
                                          ,self.resource_lib_dict['Images']['Medium_Meteor']['Image_List'][image_no][1])
            enemy_sprite.guid = "Asteroid"

            enemy_sprite.center_y = place_y_cord
            enemy_sprite.center_x = place_x_cord
            place_x_cord = enemy_sprite.right + 50

            enemy_sprite.size = 3
            enemy_sprite.visible = False
            self.game_sprite_list.append(enemy_sprite)

        sprite_count = (self.round_dict[self.round]['Astroids'][0] * 3 * 3) + \
                       (self.round_dict[self.round]['Astroids'][1]  * 3) + \
                       (self.round_dict[self.round]['Astroids'][2] )

        for i in range(sprite_count):
            image_no = random.randrange(len(self.resource_lib_dict['Images']['Small_Meteor']['Image_List']))
            enemy_sprite = AsteroidSprite(self.resource_lib_dict['Images']['Small_Meteor']['Image_List'][image_no][0]
                                          , self.resource_lib_dict['Images']['Small_Meteor']['Image_List'][image_no][1])
            enemy_sprite.guid = "Asteroid"

            enemy_sprite.center_y = place_y_cord
            enemy_sprite.center_x = place_x_cord
            place_x_cord = enemy_sprite.right + 50

            enemy_sprite.size = 2
            enemy_sprite.visible = False
            self.game_sprite_list.append(enemy_sprite)

        sprite_count = (self.round_dict[self.round]['Astroids'][0] * 3 * 3 * 3) + \
                       (self.round_dict[self.round]['Astroids'][1]  * 3 * 3) + \
                       (self.round_dict[self.round]['Astroids'][2] * 3)

        for i in range(sprite_count):
            image_no = random.randrange(len(self.resource_lib_dict['Images']['Tiny_Meteor']['Image_List']))
            enemy_sprite = AsteroidSprite(self.resource_lib_dict['Images']['Tiny_Meteor']['Image_List'][image_no][0]
                                          , self.resource_lib_dict['Images']['Tiny_Meteor']['Image_List'][image_no][1])
            enemy_sprite.guid = "Asteroid"

            enemy_sprite.center_y = place_y_cord
            enemy_sprite.center_x = place_x_cord
            place_x_cord = enemy_sprite.right + 50

            enemy_sprite.size = 2
            enemy_sprite.visible = False
            self.game_sprite_list.append(enemy_sprite)

        #satalite_Sprite = sat
        sprite_count = self.round_dict[self.round]['Max_Enemies']

        enemy_sprite = EnemyShip()
        enemy_dict = enemy_sprite.enemy_dict
        enemy_sprite.kill()

        for i in range(self.round_dict[self.round]['Max_Enemies']):
            for x in enemy_dict:
                enemy_sprite = EnemyShip(character=x)
                enemy_sprite.center_y = place_y_cord
                enemy_sprite.center_x = place_x_cord
                place_x_cord = enemy_sprite.right + 50
                enemy_sprite.visible = False
                self.game_sprite_list.append(enemy_sprite)

        #enemy_dict
        print(len(self.game_sprite_list))
        # for i in range(1,50):
        #     image_no = random.randrange(len(self.resource_lib_dict['Images']['bullet']['Blue']))
        #     bullet_sprite = TurningSprite(self.resource_lib_dict['Images']['bullet']['Blue'][image_no][0]
        #                                   , self.resource_lib_dict['Images']['bullet']['Blue'][image_no][1])
        #     bullet_sprite.guid = "Bullet"
        #     self.game_sprite_list_waiting_room.append()
        #
        #     self.round_dict



    def start_new_game(self):
        """ Set up the game and initialize the variables. """

        self.frame_count = 0
        self.game_over = False


        # Sprite lists
        self.game_sprite_list = SuperSpriteList(use_spatial_hash=True)
        self.game_sprite_list_waiting_room = SuperSpriteList(use_spatial_hash=False)
        # self.player_sprite_list = arcade.SpriteList(use_spatial_hash=True)
        # self.asteroid_list = arcade.SpriteList(use_spatial_hash=True)
        # self.bullet_list = arcade.SpriteList(use_spatial_hash=True)
        self.ship_life_list = arcade.SpriteList()
        # self.enemy_ship_list = arcade.SpriteList(use_spatial_hash=True)

        # Set up the player
        self.score = 0
        self.player_sprite = ShipSprite(LIB_BASE_PATH+"ship_A_H.png", SCALE * 1.5)
        #self.player_sprite = ShipSprite(":resources:images/space_shooter/"
        #                                "playerShip1_orange.png",
        #                                SCALE)
        self.game_sprite_list.append(self.player_sprite)
        self.lives = LIVES

        # Set up the little icons that represent the player lives.
        cur_pos = 10
        for i in range(self.lives):
            life = SuperSprite(":resources:images/space_shooter/"
                                 "playerLife1_orange.png",
                                 SCALE)
            life.center_x = cur_pos + life.width
            life.center_y = life.height
            cur_pos += life.width
            self.ship_life_list.append(life)

        self.predraw_sprites()
        self.start_new_round()

        # # Make the asteroids
        # image_list = (":resources:images/space_shooter/meteorGrey_big1.png",
        #               ":resources:images/space_shooter/meteorGrey_big2.png",
        #               ":resources:images/space_shooter/meteorGrey_big3.png",
        #               ":resources:images/space_shooter/meteorGrey_big4.png")
        # for i in range(STARTING_ASTEROID_COUNT):
        #     image_no = random.randrange(4)
        #     enemy_sprite = AsteroidSprite(image_list[image_no], SCALE)
        #     enemy_sprite.guid = "Asteroid"
        #
        #     enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)
        #     enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)
        #
        #     enemy_sprite.change_x = random.random() * 2 - 1
        #     enemy_sprite.change_y = random.random() * 2 - 1
        #
        #     enemy_sprite.change_angle = (random.random() - 0.5) * 2
        #     enemy_sprite.size = 4
        #     self.game_sprite_list.append(enemy_sprite)

    def on_draw(self):
        """
        Render the screen.
        """


        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.


        self.game_sprite_list.draw()
        # self.asteroid_list.draw()
        self.ship_life_list.draw()
        # self.bullet_list.draw()
        # self.player_sprite_list.draw()
        # self.enemy_ship_list.draw()
        self.velocity = self.player_sprite.velocity
        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 100, arcade.color.WHITE, 13)

        output = f"Asteroid Count: {self.game_sprite_list.ListLenGetSprite(sprite_class='Asteroid')}"
        arcade.draw_text(output, 10, 80, arcade.color.WHITE, 13)

        if self.game_sprite_list.get_closest_sprite_notself(sprite=self.player_sprite, tpl_sprite_class_to_ignore=['Bullet']):
            output = str(self.game_sprite_list.get_closest_sprite_notself(sprite=self.player_sprite, tpl_sprite_class_to_ignore=['Bullet'])[0].sprite_class)
            output+= ', ' + str(self.game_sprite_list.get_closest_sprite_notself(sprite=self.player_sprite, tpl_sprite_class_to_ignore=['Bullet'])[1])
            arcade.draw_text(output, 10, 60, arcade.color.WHITE, 13)

        # output = f"Velocity: {round(self.velocity[0],2)}:{round(self.velocity[1],2)} Thrust {self.player_sprite.thrust} Speed {round(self.player_sprite.speed, 2)} Angle: {round(math.radians(self.player_sprite.angle), 2)}"
        # arcade.draw_text(output, 10, 60, arcade.color.WHITE, 13)
        #
        # output = f"Change: {round(self.player_sprite.change_x,2)}, {round(self.player_sprite.change_y,2)} Center: {round(self.player_sprite.center_x,2)}, {round(self.player_sprite.center_y,2)} Player Boundries: {round(self.player_sprite.boundary_left or 0, 2)}, {round(self.player_sprite.boundary_right or 0,2)}"
        # arcade.draw_text(output, 10, 40, arcade.color.WHITE, 13)


    def on_key_press(self, symbol, modifiers):
        """ Called whenever a key is pressed. """
        # Shoot if the player hit the space bar and we aren't respawning.
        if not self.player_sprite.respawning and symbol == arcade.key.SPACE:
            self.fire_bullet(firing_sprite=self.player_sprite, fire_angles=[self.player_sprite.angle])#, self.player_sprite.angle-180 ])
            self.player_sprite.firing_on = True

            # bullet_sprite = TurningSprite(":resources:images/space_shooter/"
            #                               "laserBlue01.png",
            #                               SCALE)
            # bullet_sprite.guid = "Bullet"
            #
            # bullet_sprite.sprite_class = 'Bullet'
            # bullet_sprite.sprite_subclass = 'Player_Bullet'
            # bullet_sprite.originating_source = self.player_sprite
            #
            # bullet_speed = 13
            # bullet_sprite.change_y = \
            #     math.cos(math.radians(self.player_sprite.angle-90)) * bullet_speed
            # bullet_sprite.change_x = \
            #     -math.sin(math.radians(self.player_sprite.angle-90)) \
            #     * bullet_speed
            #
            # bullet_sprite.center_x = self.player_sprite.center_x
            # bullet_sprite.center_y = self.player_sprite.center_y + 2
            # bullet_sprite.update()
            #
            # self.game_sprite_list.append(bullet_sprite)
            #
            # arcade.play_sound(self.laser_sound)

        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = 3
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = -3
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = PLAYER_THRUST
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = -PLAYER_THRUST

    def on_key_release(self, symbol, modifiers):
        """ Called whenever a key is released. """
        if symbol == arcade.key.LEFT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.RIGHT:
            self.player_sprite.change_angle = 0
        elif symbol == arcade.key.UP:
            self.player_sprite.thrust = 0
        elif symbol == arcade.key.DOWN:
            self.player_sprite.thrust = 0
        elif symbol == arcade.key.SPACE:
            self.player_sprite.firing_on = False

    def fire_bullet(self, firing_sprite=SuperSprite(),fire_angles: []=[], fire_speed: float=15, laser_Color: str() ='Blue'):
        if len(fire_angles) == 0:
            fire_angles.append(firing_sprite.angle)
        print(fire_angles)

        for fire_angle in fire_angles:
            image_no = random.randrange(len(self.resource_lib_dict['Images']['bullet'][laser_Color]))
            bullet_sprite = TurningSprite(self.resource_lib_dict['Images']['bullet'][laser_Color][image_no][0]
                                          , self.resource_lib_dict['Images']['bullet'][laser_Color][image_no][1]*SCALE)
            bullet_sprite.guid = "Bullet"

            bullet_sprite.sprite_class = 'Bullet'
            bullet_sprite.sprite_subclass = firing_sprite.sprite_class + '_Bullet'  #'Player_Bullet'
            bullet_sprite.originating_source = firing_sprite

            #bullet_speed = 13
            bullet_sprite.change_y = \
                math.cos(math.radians(fire_angle - 90)) * fire_speed
            bullet_sprite.change_x = \
                -math.sin(math.radians(fire_angle - 90)) \
                * fire_speed

            bullet_sprite.center_x = firing_sprite.center_x
            bullet_sprite.center_y = firing_sprite.center_y + 2
            bullet_sprite.update()

            self.game_sprite_list.append(bullet_sprite)

        arcade.play_sound(self.laser_sound)

    def draw_ship_life_list(self):
        for life in self.ship_life_list:
            self.ship_life_list.pop().remove_from_sprite_lists()

        # Set up the little icons that represent the player lives.
        cur_pos = 10
        for i in range(self.lives):
            life = SuperSprite(":resources:images/space_shooter/"
                                 "playerLife1_orange.png",
                                 SCALE)
            life.center_x = cur_pos + life.width
            life.center_y = life.height
            cur_pos += life.width
            self.ship_life_list.append(life)



    def split_asteroid(self, asteroid: AsteroidSprite):
        """ Split an asteroid into chunks. """
        x = asteroid.center_x
        y = asteroid.center_y
        self.score += 1

        if asteroid.size == 4:
            for i in range(3):
                image_no = random.randrange(len(self.resource_lib_dict['Images']['Medium_Meteor']['Image_List']))
                enemy_sprite = AsteroidSprite(self.resource_lib_dict['Images']['Medium_Meteor']['Image_List'][image_no][0]
                                            , self.resource_lib_dict['Images']['Medium_Meteor']['Image_List'][image_no][1])
                enemy_sprite.guid = "Asteroid"

                random_x_factor = random.randrange(-50, 50, 1)
                random_y_factor = random.randrange(-50, 50, 1)
                enemy_sprite.center_y = y + random_y_factor
                enemy_sprite.center_x = x + random_x_factor

                enemy_sprite.change_x = random.random() * 2.5 - 1.25
                enemy_sprite.change_y = random.random() * 2.5 - 1.25

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 3

                self.game_sprite_list.append(enemy_sprite)
                self.hit_sound1.play()

        elif asteroid.size == 3:
            for i in range(3):
                image_no = random.randrange(len(self.resource_lib_dict['Images']['Small_Meteor']['Image_List']))
                enemy_sprite = AsteroidSprite(self.resource_lib_dict['Images']['Small_Meteor']['Image_List'][image_no][0]
                                              , self.resource_lib_dict['Images']['Small_Meteor']['Image_List'][image_no][1])
                enemy_sprite.guid = "Asteroid"

                random_x_factor = random.randrange(-50, 50, 1)
                random_y_factor = random.randrange(-50, 50, 1)
                enemy_sprite.center_y = y + random_y_factor
                enemy_sprite.center_x = x + random_x_factor

                enemy_sprite.change_x = random.random() * 3 - 1.5
                enemy_sprite.change_y = random.random() * 3 - 1.5

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 2

                self.game_sprite_list.append(enemy_sprite)
                self.hit_sound2.play()

        elif asteroid.size == 2:
            for i in range(3):
                image_no = random.randrange(len(self.resource_lib_dict['Images']['Tiny_Meteor']['Image_List']))
                enemy_sprite = AsteroidSprite(self.resource_lib_dict['Images']['Tiny_Meteor']['Image_List'][image_no][0]
                                              , self.resource_lib_dict['Images']['Tiny_Meteor']['Image_List'][image_no][1])
                enemy_sprite.guid = "Asteroid"

                random_x_factor = random.randrange(-50, 50, 1)
                random_y_factor = random.randrange(-50, 50, 1)
                enemy_sprite.center_y = y + random_y_factor
                enemy_sprite.center_x = x + random_x_factor

                enemy_sprite.change_x = random.random() * 3.5 - 1.75
                enemy_sprite.change_y = random.random() * 3.5 - 1.75

                enemy_sprite.change_angle = (random.random() - 0.5) * 2
                enemy_sprite.size = 1

                self.game_sprite_list.append(enemy_sprite)
                self.hit_sound3.play()

        elif asteroid.size == 1:
            self.hit_sound4.play()

    def fire_enemy_laser(self, fire_angle: float=5.0, fire_speed: float=15, fire_frequency: float=3):

        for enemy in self.game_sprite_list.ListSubsetSprite(sprite_class='Enemy_Ship'):
            sec_since_last_fire = (datetime.now() - enemy.last_fire).total_seconds()
            #print(sec_since_last_fire)
            #total_seconds = difference.total_seconds()

            if  sec_since_last_fire >= fire_frequency: #len(self.enemy_ship_list) > 0 and
                self.fire_bullet(firing_sprite=enemy, fire_angles=[fire_angle],fire_speed=fire_speed, laser_Color='Purple')
                # bullet_sprite = TurningSprite(LIB_BASE_PATH +
                #                               "Blue_Laser2_H.png",
                #                               SCALE*.25)
                #
                # bullet_sprite.sprite_class = 'Bullet'
                # bullet_sprite.sprite_subclass = 'Enemy_Bullet'
                # bullet_sprite.originating_source = enemy
                #
                # #bullet_sprite.angle = 45
                # bullet_sprite.guid = "Enemy_Bullet"
                # #print(bullet_sprite.guid)
                # bullet_speed = fire_speed
                # bullet_sprite.change_y = \
                #     math.cos(math.radians(fire_angle)) * bullet_speed
                # bullet_sprite.change_x = \
                #     -math.sin(math.radians(fire_angle)) \
                #     * bullet_speed
                #
                # bullet_sprite.center_x = enemy.center_x #+ enemy.size  # self.player_sprite.center_x
                # bullet_sprite.center_y =    enemy.center_y #top #+ 1  # self.enemy_ship_list[0].center_y + self.enemy_ship_list[0].size
                # #print(f'{bullet_sprite.center_x}, {bullet_sprite.center_y}')
                # bullet_sprite.update()
                #
                # self.game_sprite_list.append(bullet_sprite)
                #
                # arcade.play_sound(self.laser_sound)
                enemy.last_fire = datetime.now()
                #print('enemy Fire')

    def update_powerups(self):
 #       print(f'get_center_screen_cordinates: {get_center_screen_cordinates()}')

        for powerup in self.game_sprite_list.ListSubsetSprite(sprite_class='Powerup'):
            #print(f'Powersup Speed: {powerup.speed}, {powerup.change_x}')
            if powerup.speed <=0:
                powerup.speed=1
            powerup.change_y = \
                math.cos(math.radians(powerup.angle - 90)) * powerup.speed
            powerup.change_x = \
                -math.sin(math.radians(powerup.angle - 90)) \
                * powerup.speed

            powerup.update()

    def update_satellites(self):

        # random generation of enemies
        if len(self.game_sprite_list.ListSubsetSprite(sprite_class='Satellite')) < self.round_dict[self.round]['Max_Satellites']:
            if random.randint(1, 1000)  <= self.round_dict[self.round]['Satellite_Rate']:
                Satellite_sprite = Satellite(scale=SCALE * 1.5, image_file_name=LIB_BASE_PATH + "enemy_A.png")

                size = max(Satellite_sprite.width, Satellite_sprite.height)

                Satellite_sprite.orientation = random.randrange(1,4)
                #Satellite_sprite.orientation = 4
                #print(f'orientation: {Satellite_sprite.orientation}, {Satellite_sprite.center_x}, {Satellite_sprite.center_y}')
                if Satellite_sprite.orientation == 1: # left to right
                    Satellite_sprite.center_y = random.randrange(SCREEN_HEIGHT) + 0  # size
                    Satellite_sprite.center_x = 1 + max(Satellite_sprite.width, Satellite_sprite.height)

                elif Satellite_sprite.orientation == 2: # right to left
                    Satellite_sprite.center_y = random.randrange(1, SCREEN_HEIGHT) + 0  # size
                    Satellite_sprite.center_x = SCREEN_WIDTH - 100 - max(Satellite_sprite.width, Satellite_sprite.height)
                    #print(f'{Satellite_sprite.center_x}, {Satellite_sprite.center_y}')
                elif Satellite_sprite.orientation == 3: # top to bottom
                    Satellite_sprite.center_y = max(Satellite_sprite.width, Satellite_sprite.height) + 0  # size
                    Satellite_sprite.center_x = random.randrange(SCREEN_WIDTH) + 0 #max(Satellite_sprite.width, Satellite_sprite.height) + SCREEN_WIDTH

                else: # bottom to top
                    Satellite_sprite.center_y = SCREEN_HEIGHT - max(Satellite_sprite.width, Satellite_sprite.height) + 0  # size
                    Satellite_sprite.center_x = random.randrange(SCREEN_WIDTH) + 0 #max(Satellite_sprite.width, Satellite_sprite.height) + SCREEN_WIDTH

                Satellite_sprite.angle = 0

                self.game_sprite_list.append(Satellite_sprite)

                #print(f'Satellite_sprite: {Satellite_sprite.sprite_class}, {Satellite_sprite.sprite_subclass}')

                #print(enemy_sprite.sprite_subclass)
                #print('enemy.enemy_dict', enemy_sprite.enemy_dict[enemy_sprite.sprite_subclass])


    def update_enemies(self):

        # random generation of enemies
        if len(self.game_sprite_list.ListSubsetSprite(sprite_class='Enemy_Ship')) < self.round_dict[self.round]['Max_Enemies']:
            if random.randint(1, 1000)  <= self.round_dict[self.round]['Enemy_Ship_Rate']:
                enemy_sprite = EnemyShip(scale=SCALE * 1.5, image_file_name=LIB_BASE_PATH + "enemy_A.png")

                size = max(enemy_sprite.width, enemy_sprite.height)

                enemy_sprite.orientation = random.randrange(1,4)
                #enemy_sprite.orientation = 4
                #print(f'orientation: {enemy_sprite.orientation}, {enemy_sprite.center_x}, {enemy_sprite.center_y}')
                if enemy_sprite.orientation == 1: # left to right
                    enemy_sprite.center_y = random.randrange(SCREEN_HEIGHT) + 0  # size
                    enemy_sprite.center_x = 1 + max(enemy_sprite.width, enemy_sprite.height)

                elif enemy_sprite.orientation == 2: # right to left
                    enemy_sprite.center_y = random.randrange(1, SCREEN_HEIGHT) + 0  # size
                    enemy_sprite.center_x = SCREEN_WIDTH - 100 - max(enemy_sprite.width, enemy_sprite.height)
                  #  print(f'{enemy_sprite.center_x}, {enemy_sprite.center_y}')
                elif enemy_sprite.orientation == 3: # top to bottom
                    enemy_sprite.center_y = max(enemy_sprite.width, enemy_sprite.height) + 0  # size
                    enemy_sprite.center_x = random.randrange(SCREEN_WIDTH) + 0 #max(enemy_sprite.width, enemy_sprite.height) + SCREEN_WIDTH

                else: # bottom to top
                    enemy_sprite.center_y = SCREEN_HEIGHT - max(enemy_sprite.width, enemy_sprite.height) + 0  # size
                    enemy_sprite.center_x = random.randrange(SCREEN_WIDTH) + 0 #max(enemy_sprite.width, enemy_sprite.height) + SCREEN_WIDTH

                enemy_sprite.angle = 0

                self.game_sprite_list.append(enemy_sprite)

                #print(enemy_sprite.sprite_subclass)
                #print('enemy.enemy_dict', enemy_sprite.enemy_dict[enemy_sprite.sprite_subclass])

        sprite_dict={}
        for enemy in self.game_sprite_list.ListSubsetSprite(sprite_class='Enemy_Ship'):
            for sprite in self.game_sprite_list:
                if sprite != enemy:
                    if  sprite.sprite_class != 'Bullet' \
                        and ('All' not in sprite_dict \
                            or sprite_dict['All']['distance'] > arcade.get_distance_between_sprites(sprite, enemy)):
                        sprite_dict.update({'All':
                                            {'sprite':sprite, 'distance':arcade.get_distance_between_sprites(sprite, enemy)
                                             ,'Angle': GetAngleBtwn2Points(x1=enemy.center_x, y1=enemy.center_y,
                                                                 x2=sprite.center_x, y2=sprite.center_y)
                                             ,'center_x':sprite.center_x, 'center_y':sprite.center_y
                                             ,'class':sprite.sprite_class, 'subclass':sprite.sprite_subclass,
                                             }
                                        })
                        #loop through intersect object types, not seperate
                    if ('Asteroid' not in sprite_dict or \
                            sprite_dict['Asteroid']['distance'] > arcade.get_distance_between_sprites(sprite, enemy)) \
                                and sprite.sprite_class == 'Asteroid' :
                            sprite_dict.update({'Asteroid':
                                            {'sprite':sprite, 'distance':arcade.get_distance_between_sprites(sprite, enemy)
                                             ,'Angle': GetAngleBtwn2Points(x1=enemy.center_x, y1=enemy.center_y,
                                                                 x2=sprite.center_x, y2=sprite.center_y)
                                             ,'center_x':sprite.center_x, 'center_y':sprite.center_y
                                             ,'class':sprite.sprite_class, 'subclass':sprite.sprite_subclass,
                                             }
                                        })
                    if ('Player' not in sprite_dict or \
                            sprite_dict['Player']['distance'] > arcade.get_distance_between_sprites(sprite, enemy)) \
                                and sprite.sprite_class in ('Player', 'Enemy_Ship') :
                            sprite_dict.update({'Player':
                                            {'sprite':sprite, 'distance':arcade.get_distance_between_sprites(sprite, enemy)
                                             ,'Angle': GetAngleBtwn2Points(x1=enemy.center_x, y1=enemy.center_y,
                                                                 x2=sprite.center_x, y2=sprite.center_y)
                                             ,'center_x':sprite.center_x, 'center_y':sprite.center_y
                                             ,'class':sprite.sprite_class, 'subclass':sprite.sprite_subclass,
                                             }
                                        })
                    if sprite.sprite_class != 'Bullet' and\
                            ('Random' not in sprite_dict or \
                            random.randrange(1,10) <=3):
                            sprite_dict.update({'Random':
                                            {'sprite':sprite, 'distance':arcade.get_distance_between_sprites(sprite, enemy)
                                             ,'Angle': GetAngleBtwn2Points(x1=enemy.center_x, y1=enemy.center_y,
                                                                 x2=sprite.center_x, y2=sprite.center_y)
                                             ,'center_x':sprite.center_x, 'center_y':sprite.center_y
                                             ,'class':sprite.sprite_class, 'subclass':sprite.sprite_subclass,
                                             }
                                        })
                    if  sprite.sprite_class == 'Bullet' \
                        and ('Bullet' not in sprite_dict \
                            or sprite_dict['Bullet']['distance'] > arcade.get_distance_between_sprites(sprite, enemy)):
                        sprite_dict.update({'Bullet':
                                            {'sprite':sprite, 'distance':arcade.get_distance_between_sprites(sprite, enemy)
                                             ,'Angle': GetAngleBtwn2Points(x1=enemy.center_x, y1=enemy.center_y,
                                                                 x2=sprite.center_x, y2=sprite.center_y)
                                             ,'center_x':sprite.center_x, 'center_y':sprite.center_y
                                             ,'class':sprite.sprite_class, 'subclass':sprite.sprite_subclass,
                                             }
                                        })

            # print(enemy.sprite_subclass)
            # print('sprite_dict', sprite_dict)
            # print('enemy.enemy_dict', enemy.enemy_dict)
            hunt_type = enemy.enemy_dict[enemy.sprite_subclass]['Hunt_Type']
            #print(enemy.sprite_subclass, hunt_type)
            if hunt_type in sprite_dict:
                #print(sprite_dict[hunt_type]['sprite'])
                # angle = GetAngleBtwn2Points(x1=enemy.center_x, y1=enemy.center_y, x2=sprite_dict[hunt_type]['center_x'],
                #                             y2=sprite_dict[hunt_type]['center_y'])

                # fire_frequency = enemy.enemy_dict[enemy.sprite_subclass]['Max_Shoot_Speed'] \
                #                  - enemy.enemy_dict[enemy.sprite_subclass]['Min_Shoot_Speed'] /

                fire_adjustment_angle = 0
                if random.randrange(1, 10) > enemy.enemy_dict[enemy.sprite_subclass]['Accuracy']:
                    fire_adjustment_angle = random.randrange(1, 10)
                    #print(f'Fire Angle Adjusted by {fire_adjustment_angle}')
                #print(f'{sprite_dict[hunt_type]["class"]} Distance {sprite_dict[hunt_type]["distance"]}')

                enemy_speed_diff = enemy.enemy_dict[enemy.sprite_subclass]['Max_Shoot_Speed'] - enemy.enemy_dict[enemy.sprite_subclass]['Min_Shoot_Speed']
                if not enemy_speed_diff:
                    enemy_speed_diff = 1

                enemy_speed_buckets = 800 / 10
                preservation_speed_buckets = 300 / 10

                if sprite_dict['All']['distance']  <= enemy.enemy_dict[enemy.sprite_subclass]['Preservation'] * preservation_speed_buckets:
                    hunt_type = 'All'
                    #print('Preservation!')


                if sprite_dict[hunt_type]['distance'] <= 100:
                    enemy_fire_frequency = enemy.enemy_dict[enemy.sprite_subclass]['Max_Shoot_Speed']
                else:
                    enemy_fire_frequency = math.floor(sprite_dict[hunt_type]['distance'] / enemy_speed_buckets)
                    #enemy_fire_frequency = enemy_speed_buckets * enemy.enemy_dict[enemy.sprite_subclass]['Min_Shoot_Speed']

                if enemy_fire_frequency > enemy.enemy_dict[enemy.sprite_subclass]['Max_Shoot_Speed']:
                    enemy_fire_frequency = enemy.enemy_dict[enemy.sprite_subclass]['Max_Shoot_Speed']
                if enemy_fire_frequency < enemy.enemy_dict[enemy.sprite_subclass]['Min_Shoot_Speed']:
                    enemy_fire_frequency = enemy.enemy_dict[enemy.sprite_subclass]['Min_Shoot_Speed']

                #print(f'enemy_fire_frequency {enemy_fire_frequency}, {enemy.enemy_dict[enemy.sprite_subclass]["Min_Shoot_Speed"]}, {enemy.enemy_dict[enemy.sprite_subclass]["Max_Shoot_Speed"]}, {sprite_dict[hunt_type]["distance"]} ')


                self.fire_enemy_laser(fire_angle=sprite_dict[hunt_type]['Angle'] + fire_adjustment_angle, fire_speed=15, fire_frequency=enemy_fire_frequency)
    def update_player_powerups(self):

        for shield in self.game_sprite_list.ListSubsetSprite(sprite_class='Shield'):
            shield.center_x = shield.originating_source.center_x
            shield.center_y = shield.originating_source.center_y

    def apply_player_powerup(self, powerup=Powerup()):
        print(powerup.sprite_subclass)
        if powerup.sprite_subclass == 'Life': # or 1==1:
            self.lives += 1
            self.draw_ship_life_list()

        if powerup.sprite_subclass == 'Shield' : # or 1 == 1:
            # print(f'Shield powerup! {self.player_sprite.center_x},{self.player_sprite.center_y}')
            #self.start_render()
            #mycircle = arcade.draw_circle_outline(center_x = self.player_sprite.center_x, center_y = self.player_sprite.center_y, radius=250, color=(255,255,255))
            shield_sprite = TurningSprite(LIB_BASE_PATH +"Blue_Circle.png",
                                          SCALE)
            shield_sprite.guid = "Shield"
            shield_sprite.center_x = self.player_sprite.center_x
            shield_sprite.center_y = self.player_sprite.center_y

            shield_sprite.sprite_class = 'Shield'
            shield_sprite.sprite_subclass = 'Blue'
            shield_sprite.health = 3
            shield_sprite.originating_source = self.player_sprite
            self.game_sprite_list.append(shield_sprite)
            #arcade.finish_render()
            #arcade.run()
            #self.on_draw()
            #arcade.draw_line(self.player_sprite.center_x, CENTER_Y, x, y, arcade.color.OLIVE, 4)
            #self.player_sprite.lives += 1

        if powerup.sprite_subclass == 'Machine_Gun':#  or 1 == 1:
            self.player_sprite.power_ups.append('Machine_Gun')
            #print(f'!!!{self.player_sprite.power_ups}')

    def on_update(self, x):
        """ Move everything """
        self.frame_count += 1

        self.update_enemies()
        self.update_satellites()
        self.update_powerups()
        self.update_player_powerups()

        if self.player_sprite.firing_on \
                and 'Machine_Gun' in self.player_sprite.power_ups\
                and (datetime.now()-self.player_sprite.last_fire).total_seconds() >=0.1:
            self.fire_bullet(firing_sprite=self.player_sprite, fire_angles=[self.player_sprite.angle])
            self.player_sprite.last_fire = datetime.now()
#         if random.randint(1, 100) == 100 and self.game_sprite_list.ListLenGetSprite(sprite_class='Enemy_Ship') == 0:
#             #random_enemy_draw = True
#             #print('!RANDOM!')
#             image_list = (LIB_BASE_PATH + "enemy_A.png",
#                           LIB_BASE_PATH + "enemy_B.png",
#                           LIB_BASE_PATH + "enemy_C.png",
#                           LIB_BASE_PATH + "enemy_D.png",
#                           LIB_BASE_PATH + "enemy_E.png")
#
#             image_no = random.randrange(len(image_list))
#             enemy_sprite = EnemyShip(scale=SCALE * 1.5, image_file_name=image_list[image_no])
#             print(image_list[image_no])
#             size = max(enemy_sprite.width, enemy_sprite.height)
#
#             enemy_sprite.center_y = random.randrange(SCREEN_HEIGHT) + 0# size
#             enemy_sprite.center_x = 1 + size
#             enemy_sprite.angle = 0
#
#             #print(f'Enemy:{enemy_sprite.center_x}, {enemy_sprite.center_y}, {image_list[image_no]}, {size}')
#
#             self.game_sprite_list.append(enemy_sprite)
#             #self.enemy_sound1.play()
#
#
# #        if len(self.enemy_ship_list) > 0 and int(datetime.now().strftime("%S")) % 3 == 0 and int(datetime.now().strftime("%f")[:-3]) <=15:
#         #if len(self.enemy_ship_list) > 0:
#         for enemy in self.game_sprite_list.ListSubsetSprite(sprite_class='Enemy_Ship'):
#             #print('FIRE', int(datetime.now().strftime("%f")[:-3]))
#
#             #CombineSpritelists(self.player_sprite_list , self.asteroid_list)
#             nearest_obj = self.game_sprite_list.get_closest_sprite_notself(sprite=enemy, tpl_sprite_class_to_ignore=['Bullet'] ) #CombineSpritelists(self.player_sprite_list , self.asteroid_list))[0] #
#             # print('?', nearest_obj[0].sprite_class, enemy.sprite_class, nearest_obj[1])
#             #print(enemy.sprite_class, nearest_obj[0].sprite_class, self.hit_list_sprites['Class'][enemy.sprite_class])
#             if nearest_obj and enemy.sprite_class in self.hit_list_sprites['Class']:
#                 if nearest_obj[0].sprite_class in self.hit_list_sprites['Class'][enemy.sprite_class]:
#                 #and nearest_obj.sprite_class not in self.non_hit_list_sprites  :
#
#                     #print('!', nearest_obj[0].sprite_class, enemy.sprite_class, nearest_obj[1])
#
#                     angle=GetAngleBtwn2Points(x1=enemy.center_x, y1=enemy.center_y, x2=nearest_obj[0].center_x, y2=nearest_obj[0].center_y)
#                     enemy.angle = angle
#
#                     self.fire_enemy_laser(fire_angle=enemy.angle, fire_speed=15, fire_frequency=3)

        if not self.game_over:
            self.game_sprite_list.update()
            # self.asteroid_list.update()
            # self.bullet_list.update()
            # self.player_sprite_list.update()
            # self.enemy_ship_list.update()

            # collision_list = self.asteroid_list + self.enemy_ship_list

            if len(self.game_sprite_list.ListSubsetSprite(sprite_class='Asteroid')) == 0:
                self.start_new_round()

            for enemy_ship in self.game_sprite_list.ListSubsetSprite(sprite_class='Enemy_Ship'):
                #print(enemy_ship.center_x, enemy_ship.center_y )
                size = max(enemy_ship.width, enemy_ship.height)
                if enemy_ship.center_x < 0 - size:
                    enemy_ship.remove_from_sprite_lists()
                    enemy_ship.kill()
                if enemy_ship.center_x > SCREEN_WIDTH + size:
                    enemy_ship.remove_from_sprite_lists()
                    enemy_ship.kill()
                if enemy_ship.center_y < 0 - size:
                    enemy_ship.remove_from_sprite_lists()
                    enemy_ship.kill()
                if enemy_ship.center_y > SCREEN_HEIGHT + size:
                    enemy_ship.remove_from_sprite_lists()
                    enemy_ship.kill()


            #for bullet in self.game_sprite_list.ListSubsetSprite(sprite_class='Bullet'):
            for base_object in self.game_sprite_list:
                if base_object.sprite_class in ('Bullet', 'Enemy_Ship', 'Satellite', 'Powerup'):
                    # Remove bullet/enemy_ship if it goes off-screen
                    size = max(base_object.width, base_object.height)
                    if base_object.center_x < 0 - size:
                        base_object.remove_from_sprite_lists()
                    if base_object.center_x > SCREEN_WIDTH + size:
                        base_object.remove_from_sprite_lists()
                    if base_object.center_y < 0 - size:
                        base_object.remove_from_sprite_lists()
                    if base_object.center_y > SCREEN_HEIGHT + size:
                        base_object.remove_from_sprite_lists()

                if base_object in self.game_sprite_list:
                    collisions = arcade.check_for_collision_with_list(base_object, self.game_sprite_list)
                    elg_collision = False
                    kill_base_obj = True

                    for collision_obj in collisions:
                        kill_collision_obj = True





                        # if base_object.sprite_class != 'Asteroid':
                        #print(f'!base_object.sprite_class: {base_object.sprite_class}, collision_obj.sprite_class: {collision_obj.sprite_class}')
                        if base_object.sprite_class in self.hit_list_sprites['Class']:
                            if collision_obj.sprite_class in self.hit_list_sprites['Class'][base_object.sprite_class]:
                                elg_collision = True
                                if collision_obj.originating_source == base_object.originating_source:
                                    collision_same_base_objects = True
                                    elg_collision = False
                                elif collision_obj == base_object.originating_source:
                                    collision_same_base_objects = True
                                    elg_collision = False
                                elif collision_obj.originating_source == base_object:
                                    collision_same_base_objects = True
                                    elg_collision = False
                                else:
                                    collision_same_base_objects = False
                        else:
                                elg_collision = False

                        if collision_obj.sprite_class == 'Player' and self.player_sprite.respawning:
                            elg_collision = False

                        #print('?', elg_collision, collision_obj.sprite_class)
                        #print('??', base_object.sprite_class)
                        if elg_collision and base_object.originating_source != collision_obj\
                                and collision_obj.originating_source != base_object:
                            print('#', elg_collision, base_object, base_object.originating_source, collision_obj, collision_obj.originating_source)

                            if collision_obj.sprite_class == 'Asteroid':
                                #print('!', collision_obj.guid, collision_obj.sprite_class)
                                self.split_asteroid(cast(AsteroidSprite ,collision_obj))

                            if base_object.sprite_class == 'Asteroid':
                                #print('!', base_object.guid, base_object.sprite_class)
                                self.split_asteroid(cast(AsteroidSprite ,base_object))

                            if collision_obj.sprite_class == 'Shield' or base_object.sprite_class == 'Shield':
                                 print(f'Collision: {collision_obj.sprite_class}, {base_object.sprite_class}, {collision_obj.originating_source}, {base_object.originating_source}, {collision_same_base_objects} ')

                            if collision_obj.sprite_class == 'Shield' and not collision_same_base_objects:
                                print('!', collision_obj.guid, collision_obj.sprite_class)
                                collision_obj.health-=1
                                if collision_obj.health < 1:
                                    kill_collision_obj = True
                                else:
                                    kill_collision_obj = False

                            if base_object.sprite_class == 'Shield' and not collision_same_base_objects:
                                print('!', base_object.guid, base_object.sprite_class)
                                collision_obj.health-=1
                                if collision_obj.health < 1:
                                    kill_base_obj = True
                                else:
                                    kill_base_obj = False


                            if collision_obj.sprite_class == 'Satellite' and base_object.sprite_class=='Bullet':
                                #print(f'{collision_obj.sprite_class} collision {base_object.sprite_class}\n{collision_obj.enemy_dict}')
                                if collision_obj.powerup_freq * 100 >= random.randrange(1,100):
                                    print('POWErUP!')
                                    powerup_sprite = Powerup(scale=SCALE * 1.5, image_file_name=LIB_BASE_PATH + "enemy_A.png")
                                    powerup_sprite.center_x = collision_obj.center_x
                                    powerup_sprite.center_y = collision_obj.center_y
                                    powerup_sprite.angle = GetAngleBtwn2Points(x1=get_center_screen_cordinates()[0], y1=get_center_screen_cordinates()[1],
                                                                 x2=powerup_sprite.center_x, y2=powerup_sprite.center_y) - 90 + random.randrange(-10,10)
                                    self.game_sprite_list.append(powerup_sprite)

                            if base_object.sprite_class == 'Satellite' and collision_obj.sprite_class=='Bullet':
                                #print(f'{base_object.sprite_class} collision {collision_obj.sprite_class}\n{base_object.enemy_dict} {base_object.powerup_freq * 100}')
                                if base_object.powerup_freq * 100 >= random.randrange(1,100):
                                    print('POWErUP!')
                                    powerup_sprite = Powerup(scale=SCALE * 1.5, image_file_name=LIB_BASE_PATH + "enemy_A.png")
                                    powerup_sprite.center_x = base_object.center_x
                                    powerup_sprite.center_y = base_object.center_y
                                    powerup_sprite.angle = GetAngleBtwn2Points(x1=get_center_screen_cordinates()[0], y1=get_center_screen_cordinates()[1],
                                                                 x2=powerup_sprite.center_x, y2=powerup_sprite.center_y) - 90 + random.randrange(-10,10)
                                    self.game_sprite_list.append(powerup_sprite)

                            if base_object.sprite_class == 'Player' and collision_obj.sprite_class=='Powerup':
                                #print(f'PU:{base_object.sprite_class} collision {collision_obj.sprite_class}')
                                kill_base_obj = False
                                kill_collision_obj = True
                                self.apply_player_powerup(collision_obj)

                            if collision_obj.sprite_class == 'Player' and base_object.sprite_class=='Powerup':
                                #print(f'PU2:{base_object.sprite_class} collision {collision_obj.sprite_class}')
                                kill_base_obj = True
                                kill_collision_obj = False
                                self.apply_player_powerup(collision_obj)

                            if (collision_obj.sprite_class == 'Player' and kill_collision_obj)\
                                    or (base_object.sprite_class == 'Player' and kill_base_obj):
                                #print('Player hit:',collision_obj.sprite_class, base_object.sprite_class, self.lives)
                                if self.lives > 0:
                                    self.lives -= 1
                                    self.player_sprite.respawn()
                                    self.ship_life_list.pop().remove_from_sprite_lists()
                                    print("Crash")
                                    if collision_obj.sprite_class == 'Player':
                                        kill_collision_obj = False
                                    if base_object.sprite_class == 'Player':
                                        kill_base_obj = False
                                else:
                                    self.game_over = True
                                    print("Game over")

                            if kill_collision_obj:
                                collision_obj.remove_from_sprite_lists()
                                collision_obj.kill()
                            if kill_base_obj:
                                base_object.remove_from_sprite_lists()
                                base_object.kill()





def main():
    """ Start the game """
    window = MyGame()
    window.start_new_game()
    arcade.run()


if __name__ == "__main__":
    main()