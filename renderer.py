import pygame

class Renderer:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.cell = 35
        self.offset_x = (width - 18 * self.cell) // 2
        self.offset_y = (height - 60 - 18 * self.cell) // 2

    def draw(self, analysis):
        self.screen.fill((210, 180, 110))
        
        # Grid
        for i in range(19):
            pygame.draw.line(self.screen, (170, 150, 100), 
                             (self.offset_x + i*35, self.offset_y), 
                             (self.offset_x + i*35, self.offset_y + 18*35), 1)
            pygame.draw.line(self.screen, (170, 150, 100), 
                             (self.offset_x, self.offset_y + i*35), 
                             (self.offset_x + 18*35, self.offset_y + i*35), 1)

        # Işınlar (Tam temas çizimi)
        for l in analysis.get("lines", []):
            sx = self.offset_x + l['start'][0] * 35
            sy = self.offset_y + l['start'][1] * 35
            ex = self.offset_x + l['end'][0] * 35
            ey = self.offset_y + l['end'][1] * 35
            
            color = (0, 0, 0) if l['color'] == "BLACK" else (255, 255, 255)
            # Kalınlık farkı temasın gücünü gösterir
            pygame.draw.line(self.screen, color, (sx, sy), (ex, ey), 1 if l['color']=="BLACK" else 2)

        # Taşlar
        for m in analysis.get("moves", []):
            px = int(self.offset_x + m['pos'][0] * 35)
            py = int(self.offset_y + m['pos'][1] * 35)
            pygame.draw.circle(self.screen, (0,0,0) if m['color']=="BLACK" else (255,255,255), (px, py), 15)