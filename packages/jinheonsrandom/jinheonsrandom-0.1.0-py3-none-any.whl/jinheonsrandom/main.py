import random


class JinheonsRandom:
    @staticmethod
    def dice_roll(jujak: bool = False):
        return random.random() < 49 / 100 if jujak else random.random() < 50 / 100
