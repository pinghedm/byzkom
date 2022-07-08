from typing import Optional
import math
import random
from enum import Enum, auto
from time import time
import pygame
from characters import CharacterInfo

pygame.font.init()
font = pygame.font.Font(None, 14)


class FighterVerticalState(Enum):
    STANDING = auto()
    CROUCHING = auto()
    JUMPING = auto()


class FighterHorizontalState(Enum):
    STILL = auto()
    GOING_LEFT = auto()
    GOING_RIGHT = auto()


class FighterAttackState(Enum):
    NEUTRAL = auto()
    KICKING = auto()
    PUNCHING = auto()
    BLOCKING = auto()


StateVector = tuple[FighterVerticalState, FighterHorizontalState, FighterAttackState]

STANDING_SPEED = 5
CROUCHING_SPEED = 2


class Fighter:
    def __init__(self, character: CharacterInfo, initial_position: tuple[int, int]):
        self.clock = pygame.time.Clock()
        self.character = character
        self.position = initial_position
        self.health_position = (initial_position[0], 10)
        self.state: StateVector = (
            FighterVerticalState.STANDING,
            FighterHorizontalState.STILL,
            FighterAttackState.NEUTRAL,
        )
        self.health = 100

        character_surface = pygame.Surface((50, 100)).convert()
        self.character_surface = character_surface
        self._reset_character()

    def _reset_character(self):
        self.character_surface.fill((0, 0, 0))
        self.character_surface.fill((255, 255, 255), rect=(2, 2, 46, 96))

        text = font.render(self.character.name, True, (0, 0, 0))
        textpos = text.get_rect(
            centerx=self.character_surface.get_width() / 2,
            centery=self.character_surface.get_height() / 2,
        )
        self.character_surface.blit(text, textpos)

    def draw(self, target_surface: pygame.Surface):
        target_surface.blit(self.character_surface, self.position)
        self.draw_healthbar(target_surface)

    def draw_healthbar(self, target_surface: pygame.Surface):
        health_surface = pygame.Surface((100, 20)).convert()
        health_surface.fill((255, 255, 255))
        health_surface.fill(
            (
                0,
                0,
                0,
            ),
            rect=(0, 0, self.health, 20),
        )
        target_surface.blit(health_surface, self.health_position)
        text = font.render(str([s.name for s in self.state]), True, (0, 0, 0))
        target_surface.blit(
            text, (self.health_position[0], self.health_position[1] + 20)
        )

    def take_damage(self, damage):
        (*_, cur_attack) = self.state
        if cur_attack == FighterAttackState.BLOCKING:
            damage = 0
        self.health -= damage

    def ai_update_state(self, enemy: "Fighter"):
        if math.floor(time()) % 2 == 0:
            new_state: StateVector = (
                random.choice(list(FighterVerticalState)),
                random.choice(
                    [
                        FighterHorizontalState.GOING_LEFT,
                        FighterHorizontalState.GOING_LEFT,
                        FighterHorizontalState.STILL,
                        FighterHorizontalState.GOING_RIGHT,
                    ]
                ),  # slightly bias to going left
                random.choice(list(FighterAttackState)),
            )
            self.update_state(enemy, new_state)

    def update_state(
        self,
        enemy: "Fighter",
        new_state: Optional[StateVector] = None,
    ):
        (cur_vert, cur_horiz, cur_attack), (new_vert, new_horiz, new_attack) = (
            self.state,
            self.state,
        )
        (cur_x, cur_y), (new_x, new_y) = self.position, self.position
        if not new_state:
            keyboard_state = pygame.key.get_pressed()

            desired_direction = (
                FighterHorizontalState.GOING_LEFT
                if keyboard_state[pygame.K_LEFT]
                else (
                    FighterHorizontalState.GOING_RIGHT
                    if keyboard_state[pygame.K_RIGHT]
                    else FighterHorizontalState.STILL
                )
            )

            desired_vertical = (
                FighterVerticalState.JUMPING
                if keyboard_state[pygame.K_UP]
                else (
                    FighterVerticalState.CROUCHING
                    if keyboard_state[pygame.K_DOWN]
                    else FighterVerticalState.STANDING
                )
            )

            desired_attack = (
                FighterAttackState.PUNCHING
                if keyboard_state[pygame.K_z]
                else (
                    FighterAttackState.KICKING
                    if keyboard_state[pygame.K_c]
                    else (
                        FighterAttackState.BLOCKING
                        if keyboard_state[pygame.K_x]
                        else FighterAttackState.NEUTRAL
                    )
                )
            )

            new_horiz = desired_direction
            new_attack = desired_attack
            new_vert = desired_vertical
        else:
            new_vert, new_horiz, new_attack = new_state
        # transitions
        # you can attack from any vertical position, but it stops horizontal motion
        # you can move left or right from crouching or standing (different horiz speeds)
        # if you are crouching and want to jump well allow it.
        # if youre jumping you have to land before you can change any position

        touching_enemy = self.character_surface.get_rect(
            left=self.position[0], top=self.position[1]
        ).colliderect(
            enemy.character_surface.get_rect(
                left=enemy.position[0], top=enemy.position[1]
            )
        )

        if new_horiz == FighterHorizontalState.GOING_LEFT:
            new_x = cur_x - STANDING_SPEED
        elif new_horiz == FighterHorizontalState.GOING_RIGHT:
            if not touching_enemy:
                new_x = cur_x + STANDING_SPEED
        if new_x < 0:
            new_x = 0
        elif new_x > 500:
            new_x = 500

        if self._can_damage_enemy(enemy, (new_vert, new_horiz, new_attack)):
            damage = 10 if FighterAttackState.KICKING else 5
            enemy.take_damage(damage)

        self.state = new_vert, new_horiz, new_attack
        self.position = new_x, new_y
        self.clock.tick(30)

    def _can_damage_enemy(self, enemy, desired_state):
        own_vert = desired_state[0]
        own_attack = desired_state[2]

        enemy_vert = enemy.state[0]

        if own_attack in [FighterAttackState.BLOCKING, FighterAttackState.NEUTRAL]:
            return False

        attack_range = 50 + (
            8 if own_attack == FighterAttackState.KICKING else 3
        )  # 50 is char width
        print(self.position[0], enemy.position[0])
        in_range = abs(self.position[0] - enemy.position[0]) <= attack_range

        # you connect if you are crouching and they are crouched or standing OR if you are standing and they are standing OR if you are jumping and they are jumping or standing
        compatible_state = (
            (
                FighterVerticalState.CROUCHING
                and enemy_vert != FighterVerticalState.JUMPING
            )
            or (
                own_vert == FighterVerticalState.STANDING
                and enemy_vert == FighterVerticalState.STANDING
            )
            or (
                own_vert == FighterVerticalState.JUMPING
                and enemy_vert != FighterVerticalState.CROUCHING
            )
        )

        return compatible_state and in_range
