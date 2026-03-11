import pygame
import sys
import os
import re
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
        self.show_boundaries = False
        self.screen = pygame.display.set_mode((self.board_px + self.sidebar_px, self.board_px))
        pygame.display.set_caption("Go-Ray Engine: SGF Analyzer")
        
        self.engine = GoEngine()
        
        # Yeni Özellik Değişkenleri
        self.show_stones = True
        self.sgf_moves = []
        self.sgf_index = 0
        
        self.font = pygame.font.SysFont("Verdana", 14, bold=True)
        self.btn_font = pygame.font.SysFont("Verdana", 11, bold=True)
        self.clock = pygame.time.Clock()

        self.themes = [
            {
                "name": "KLASİK", "board": (220, 179, 92),
                "stone_b": (0, 0, 0), "stone_w": (245, 245, 245),
                "ray_b": (50, 50, 50), "ray_w": (220, 220, 220),
                "boundary": (200, 50, 50)
            },
            {
                "name": "NEON", "board": (30, 30, 40),
                "stone_b": (0, 229, 255), "stone_w": (255, 0, 127),
                "ray_b": (0, 150, 180), "ray_w": (180, 0, 90),
                "boundary": (255, 215, 0)
            },
            {
                "name": "MATCHA", "board": (143, 151, 121),
                "stone_b": (47, 79, 79), "stone_w": (255, 255, 224),
                "ray_b": (30, 50, 50), "ray_w": (200, 200, 180),
                "boundary": (255, 140, 0)
            }
        ]
        self.current_theme_idx = 0
        self.t = self.themes[self.current_theme_idx]

    def load_sgf(self, filename="game.sgf"):
        """SGF dosyasını okur ve hamleleri listeye yükler."""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read()
            
            # Regex ile ;B[pd] veya ;W[dp] formatındaki hamleleri yakala
            moves = re.findall(r';([BW])\[([a-s]{2})\]', content)
            self.sgf_moves = []
            
            for color, coords in moves:
                x = ord(coords[0]) - ord('a')
                y = ord(coords[1]) - ord('a')
                col = 'black' if color == 'B' else 'white'
                self.sgf_moves.append({'pos': (x, y), 'color': col})
                
            self.sgf_index = 0
            self.engine.moves = [] # Tahtayı sıfırla
            self.engine.current_turn = 'black'
            print(f"SGF Yüklendi: '{filename}' dosyasından {len(self.sgf_moves)} hamle okundu.")
        else:
            print(f"SGF Hatası: '{filename}' dosyası proje dizininde bulunamadı.")

    def draw_board(self, data):
        # 1. Aktif temayı değişkene ata
        self.t = self.themes[self.current_theme_idx]
        
        # Ekranın ana arka planı (Tahtanın dışı) koyu kalsın
        self.screen.fill((30, 30, 30)) 
        
        # 2. TAHTA RENGİ (Sabit renk yerine self.t['board'] kullanıyoruz)
        pygame.draw.rect(self.screen, self.t['board'], (0, 0, self.board_px, self.board_px))
        
        # Koordinatlar ve Izgara Çizgileri (Siyah kalması okunabilirliği artırır)
        for i in range(19):
            coord = self.font.render(str(i + 1), True, (0, 0, 0))
            self.screen.blit(coord, (self.offset + i * self.grid_size - 5, 25)) 
            self.screen.blit(coord, (25, self.offset + i * self.grid_size - 10)) 
            
            start = self.offset + i * self.grid_size
            pygame.draw.line(self.screen, (0, 0, 0), (start, self.offset), (start, self.board_px - self.offset), 1)
            pygame.draw.line(self.screen, (0, 0, 0), (self.offset, start), (self.board_px - self.offset, start), 1)

        for r in [3, 9, 15]:
            for c in [3, 9, 15]:
                pygame.draw.circle(self.screen, (0, 0, 0), (self.offset + c*self.grid_size, self.offset + r*self.grid_size), 5)

        # 3. IŞIN RENKLERİ (Siyah taşın ışını mı, beyazın mı?)
        for line in data['lines']:
            # Rengi temadaki 'ray_b' (siyah ışını) veya 'ray_w' (beyaz ışını) değerinden çekiyoruz
            color = self.t['ray_b'] if line['color'] == 'black' else self.t['ray_w']
            width = 2 if line['color'] == 'black' else 3
            s_pos = (self.offset + line['start'][0]*self.grid_size, self.offset + line['start'][1]*self.grid_size)
            e_pos = (self.offset + line['end'][0]*self.grid_size, self.offset + line['end'][1]*self.grid_size)
            pygame.draw.line(self.screen, color, s_pos, e_pos, width)

        # Kırmızı Noktalar (Kesişimler sabit kırmızı kalabilir, uyarıcıdır)
        for pt in data['red_points']:
            pos = (int(self.offset + pt[0]*self.grid_size), int(self.offset + pt[1]*self.grid_size))
            pygame.draw.circle(self.screen, (255, 0, 0), pos, 5)

        # 4. TAŞ RENKLERİ
        if self.show_stones:
            for m in data['moves']:
                pos = (int(self.offset + m['pos'][0]*self.grid_size), int(self.offset + m['pos'][1]*self.grid_size))
                # Rengi temadaki 'stone_b' veya 'stone_w' değerinden çekiyoruz
                color = self.t['stone_b'] if m['color'] == 'black' else self.t['stone_w']
                pygame.draw.circle(self.screen, color, pos, 15)
                # İkinci oyuncunun taşı arka planda kaybolmasın diye ince siyah bir çerçeve
                if m['color'] == 'white': 
                    pygame.draw.circle(self.screen, (0, 0, 0), pos, 15, 1)

        # 5. SINIR (CEPHE) ÇİZGİSİ RENGİ
        if self.show_boundaries and not self.show_stones:
            import math
            for i, pt1 in enumerate(data['red_points']):
                pos1 = (int(self.offset + pt1[0]*self.grid_size), int(self.offset + pt1[1]*self.grid_size))
                for pt2 in data['red_points'][i+1:]:
                    pos2 = (int(self.offset + pt2[0]*self.grid_size), int(self.offset + pt2[1]*self.grid_size))
                    
                    dist = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
                    if dist < 3.5:
                        # Çizgiyi çizerken rengi temadaki 'boundary' değerinden alıyoruz
                        pygame.draw.line(self.screen, self.t['boundary'], pos1, pos2, 4)

    def create_button(self, text, pos):
        # BOYUTLAR KÜÇÜLTÜLDÜ: 160x45 yerine 130x35
        rect = pygame.Rect(pos[0], pos[1], 130, 35)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, border_radius=4)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1, border_radius=4)
        
        # Yazı fontunu da bir tık küçültebiliriz (__init__ içindeki btn_font'u 10 yap)
        label = self.btn_font.render(text, True, (0, 0, 0))
        self.screen.blit(label, label.get_rect(center=rect.center))
        return rect

    def draw_sidebar(self):
        sidebar_x = self.board_px + 20
        self.t = self.themes[self.current_theme_idx] 
        
        # Butonlar listesine 2 yeni buton eklendi
        self.btn_load = self.create_button("SGF YÜKLE", (sidebar_x, 30))
        self.btn_prev = self.create_button("<< GERİ", (sidebar_x, 75))
        self.btn_next = self.create_button("İLERİ >>", (sidebar_x, 120))
        self.btn_end = self.create_button("SONA GİT", (sidebar_x, 165))       # YENİ: Oyunu bitirir
        self.btn_free = self.create_button("SERBEST MOD", (sidebar_x, 210))   # YENİ: Tahtayı sıfırlar
        
        self.btn_ghost = self.create_button("TAŞLARI GİZLE" if self.show_stones else "TAŞLARI GÖSTER", (sidebar_x, 255))
        self.btn_bounds = self.create_button("SINIRLARI ÇİZ" if not self.show_boundaries else "SINIRLARI GİZLE", (sidebar_x, 300))
        self.btn_mode = self.create_button(f"MOD: {self.engine.mode}", (sidebar_x, 345))
        self.btn_theme = self.create_button(f"TEMA: {self.t['name']}", (sidebar_x, 390))
        self.btn_save = self.create_button("KAYDET (PNG)", (sidebar_x, 435))
        
        # Yazıları aşağı kaydırdık
        txt_turn = self.font.render(f"SIRA: {self.engine.current_turn.upper()}", True, (255, 255, 255))
        txt_sgf = self.font.render(f"HAMLE: {self.sgf_index} / {len(self.sgf_moves)}", True, (255, 255, 255))
        self.screen.blit(txt_turn, (sidebar_x + 20, 490))
        self.screen.blit(txt_sgf, (sidebar_x + 20, 520))
        

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
                    
                    if self.btn_load.collidepoint(pos):
                        self.load_sgf("game.sgf") # Proje dizinindeki game.sgf dosyasını arar
                    
                    elif self.btn_prev.collidepoint(pos):
                        if self.sgf_index > 0:
                            self.engine.undo_move()
                            self.sgf_index -= 1

                    elif self.btn_bounds.collidepoint(pos):
                        self.show_boundaries = not self.show_boundaries
                        durum = "Açık" if self.show_boundaries else "Kapalı"
                        print(f"Sınır Çizgileri (Cephe Hattı): {durum}")
                    
                    elif self.btn_next.collidepoint(pos):
                        if self.sgf_index < len(self.sgf_moves):
                            mv = self.sgf_moves[self.sgf_index]
                            if self.engine.add_move(mv['pos'][0], mv['pos'][1], mv['color']):
                                self.sgf_index += 1
                    elif self.btn_end.collidepoint(pos):
                        # SGF yüklüyse, kalan tüm hamleleri otomatik oyna
                        if self.sgf_moves:
                            print("SGF: Hızlı sarım başlatıldı...")
                            while self.sgf_index < len(self.sgf_moves):
                                mv = self.sgf_moves[self.sgf_index]
                                
                                # 1. OPTİMİZASYON: Handikap ve Pas durumlarında motorun sırayı reddetmesini engelle
                                self.engine.current_turn = mv['color']
                                
                                # 2. Hamleyi motora işlet
                                self.engine.add_move(mv['pos'][0], mv['pos'][1], mv['color'])
                                
                                # 3. SONSUZ DÖNGÜ KİLİDİ: Hamle reddedilse bile indeksi kesinlikle artır
                                self.sgf_index += 1
                                
                            print(f"SGF: Oyunun son haline anında gidildi. (Hamle: {self.sgf_index})")
                    elif self.btn_free.collidepoint(pos):
                        # SGF takibini bırak, tahtayı tamamen sıfırla ve serbest oyuna dön
                        self.sgf_moves = []
                        self.sgf_index = 0
                        self.engine.moves = []
                        self.engine.current_turn = 'black'
                        self.redo_stack = []
                        print("Serbest Mod: Tahta temizlendi, normal oyuna geçildi.")

                    elif self.btn_ghost.collidepoint(pos):
                        self.show_stones = not self.show_stones
                        
                    elif self.btn_mode.collidepoint(pos):
                        self.engine.toggle_mode()
                    
                    elif self.btn_theme.collidepoint(pos):
                        self.current_theme_idx = (self.current_theme_idx + 1) % len(self.themes)
                        aktif_tema = self.themes[self.current_theme_idx]['name']

                    elif self.btn_save.collidepoint(pos):
                        board_rect = pygame.Rect(0, 0, self.board_px, self.board_px)
                        sub_surface = self.screen.subsurface(board_rect)
                        pygame.image.save(sub_surface, "go_board_capture.png")
                        print("PNG Kaydedildi: Sadece tahta alanı 'go_board_capture.png' olarak aktarıldı.")

                    # Manuel Hamle (Eğer SGF yüklenmemişse serbest oynamaya devam edebilirsin)
                    elif pos[0] < self.board_px:
                        x = round((pos[0] - self.offset) / self.grid_size)
                        y = round((pos[1] - self.offset) / self.grid_size)
                        if 0 <= x <= 18 and 0 <= y <= 18:
                            if self.engine.add_move(x, y, self.engine.current_turn):
                                # Manuel oynandığında SGF takibini sıfırla
                                self.sgf_moves = []
                                self.sgf_index = 0

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    GoUI().run()