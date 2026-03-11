import pygame
import sys
import math
from engine import GoEngine

# Renkler
BOARD_COLOR = (220, 179, 92)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
BTN_COLOR = (200, 200, 200)
RAY_WHITE = (245, 245, 245)

class GoUI:
    def __init__(self):
        pygame.init()
        self.grid_size = 35  
        self.offset = 60     
        self.board_px = 18 * self.grid_size + self.offset * 2
        self.sidebar_px = 220
        self.screen = pygame.display.set_mode((self.board_px + self.sidebar_px, self.board_px))
        pygame.display.set_caption("Go Influence Analysis")
        
        self.engine = GoEngine()
        self.redo_stack = []
        self.font = pygame.font.SysFont("Verdana", 14, bold=True)
        self.btn_font = pygame.font.SysFont("Verdana", 11, bold=True)
        self.clock = pygame.time.Clock()

    def draw_board(self, data):
        self.screen.fill((30, 30, 30)) 
        pygame.draw.rect(self.screen, BOARD_COLOR, (0, 0, self.board_px, self.board_px))
        
        # Koordinatlar ve Izgara
        for i in range(19):
            coord = self.font.render(str(i), True, BLACK)
            self.screen.blit(coord, (self.offset + i * self.grid_size - 5, 25)) # Üst
            self.screen.blit(coord, (25, self.offset + i * self.grid_size - 10)) # Sol
            
            start = self.offset + i * self.grid_size
            pygame.draw.line(self.screen, BLACK, (start, self.offset), (start, self.board_px - self.offset), 1)
            pygame.draw.line(self.screen, BLACK, (self.offset, start), (self.board_px - self.offset, start), 1)

        # Hoshi Noktaları
        for r in [3, 9, 15]:
            for c in [3, 9, 15]:
                pygame.draw.circle(self.screen, BLACK, (self.offset + c*self.grid_size, self.offset + r*self.grid_size), 5)

        # Işınlar
        for line in data['lines']:
            color = BLACK if line['color'] == 'black' else RAY_WHITE
            width = 2 if line['color'] == 'black' else 3
            s_pos = (self.offset + line['start'][0]*self.grid_size, self.offset + line['start'][1]*self.grid_size)
            e_pos = (self.offset + line['end'][0]*self.grid_size, self.offset + line['end'][1]*self.grid_size)
            pygame.draw.line(self.screen, color, s_pos, e_pos, width)

        # Kırmızı Noktalar
        for pt in data['red_points']:
            pos = (int(self.offset + pt[0]*self.grid_size), int(self.offset + pt[1]*self.grid_size))
            pygame.draw.circle(self.screen, RED, pos, 5)

        # Taşlar
        for m in data['moves']:
            pos = (int(self.offset + m['pos'][0]*self.grid_size), int(self.offset + m['pos'][1]*self.grid_size))
            pygame.draw.circle(self.screen, BLACK if m['color'] == 'black' else WHITE, pos, 15)
            if m['color'] == 'white': pygame.draw.circle(self.screen, BLACK, pos, 15, 1)

    def draw_sidebar(self):
        sidebar_x = self.board_px + 20
        # Butonlar
        self.btn_undo = self.create_button("GERİ AL", (sidebar_x, 60))
        self.btn_redo = self.create_button("İLERİ SAR", (sidebar_x, 120))
        self.btn_save = self.create_button("KAYDET (PNG)", (sidebar_x, 180))
        self.btn_mode = self.create_button(f"MOD: {self.engine.mode}", (sidebar_x, 240))
        
        # Sıra Göstergesi
        turn_color = BLACK if self.engine.current_turn == "black" else WHITE
        pygame.draw.circle(self.screen, turn_color, (sidebar_x + 20, 320), 10)
        if self.engine.current_turn == "white": pygame.draw.circle(self.screen, BLACK, (sidebar_x + 20, 320), 10, 1)
        txt = self.font.render(f"SIRA: {self.engine.current_turn.upper()}", True, WHITE)
        self.screen.blit(txt, (sidebar_x + 40, 312))

    def create_button(self, text, pos):
        rect = pygame.Rect(pos[0], pos[1], 160, 45)
        pygame.draw.rect(self.screen, BTN_COLOR, rect, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, rect, 1, border_radius=5)
        label = self.btn_font.render(text, True, BLACK)
        self.screen.blit(label, label.get_rect(center=rect.center))
        return rect

    def run(self):
        while True:
            data = self.engine.get_analysis_data()
            self.draw_board(data)
            self.draw_sidebar()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    if self.btn_undo.collidepoint(pos):
                        self.engine.undo_move()
                    elif self.btn_redo.collidepoint(pos):
                        # İleri sarma mantığı buraya redo_stack ile eklenebilir
                        pass
                    elif self.btn_save.collidepoint(pos):
                        pygame.image.save(self.screen, "snapshot.png")
                    elif self.btn_mode.collidepoint(pos):
                        self.engine.toggle_mode() # Hata burada alınıyordu, düzeldi.
                    elif pos[0] < self.board_px:
                        x = round((pos[0] - self.offset) / self.grid_size)
                        y = round((pos[1] - self.offset) / self.grid_size)
                        if 0 <= x <= 18 and 0 <= y <= 18:
                            self.engine.add_move(x, y, self.engine.current_turn)

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    GoUI().run()