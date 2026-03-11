import pygame
import json
import os
from datetime import datetime

class Utils:
    @staticmethod
    def save_screenshot(screen):
        if not os.path.exists("captures"): os.makedirs("captures")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pygame.image.save(screen, f"captures/go_{timestamp}.png")
        print("Ekran görüntüsü 'captures' klasörüne kaydedildi.")

    @staticmethod
    def save_game_data(moves):
        if not os.path.exists("saves"): os.makedirs("saves")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"saves/game_{timestamp}.json", 'w') as f:
            json.dump(moves, f)
        print("Oyun verisi 'saves' klasörüne kaydedildi.")