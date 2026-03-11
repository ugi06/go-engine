import math

class GoEngine:
    def __init__(self, grid_size=19):
        self.grid_size = grid_size
        self.moves = [] 
        self.mode = "BARRIER"
        self.current_turn = "black"  # Sıra takibini buraya sabitledik

    def add_move(self, x, y, color):
        # 1. Sıra kontrolü: Gelen renk beklenen renk mi?
        if color != self.current_turn:
            return False
            
        if any(m['pos'] == (x, y) for m in self.moves):
            return False
            
        self.moves.append({'pos': (x, y), 'color': color})
        self.process_logic_captures(x, y, color)
        
        # 2. SADECE hamle başarılıysa sırayı değiştir
        self.current_turn = "white" if self.current_turn == "black" else "black"
        return True

    def undo_move(self):
        if self.moves:
            last_move = self.moves.pop()
            # 3. Geri alındığında sırayı geri alınan renge döndür
            self.current_turn = last_move['color']

    def process_logic_captures(self, last_x, last_y, last_color):
        opp_color = "white" if last_color == "black" else "black"
        
        # Önce rakip grupları kontrol et (Go kuralı: Rakip nefesi biterse önce o gider)
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = last_x + dx, last_y + dy
            if self._get_stone_color(nx, ny) == opp_color:
                self._capture_if_dead(nx, ny, opp_color)
        
        # Sonra kendi grubunu kontrol et (İntihar kontrolü)
        self._capture_if_dead(last_x, last_y, last_color)

    def _get_stone_color(self, x, y):
        for m in self.moves:
            if m['pos'] == (x, y): return m['color']
        return None

    def _capture_if_dead(self, x, y, color):
        group = []
        queue = [(x, y)]
        liberties = 0
        visited = set()

        # Grubun tüm taşlarını ve toplam nefesini (boş komşu kare) bul
        while queue:
            curr = queue.pop(0)
            if curr in visited: continue
            visited.add(curr)
            group.append(curr)
            
            cx, cy = curr
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < 19 and 0 <= ny < 19:
                    c = self._get_stone_color(nx, ny)
                    if c is None:
                        liberties += 1
                    elif c == color and (nx, ny) not in visited:
                        queue.append((nx, ny))
        
        # Eğer grubun hiç boş komşusu (liberty) kalmamışsa sil
        if liberties == 0:
            self.moves = [m for m in self.moves if m['pos'] not in group]

    def get_analysis_data(self):
        # IŞIN GEOMETRİSİ (Sadece Görsel ve Alan İçin - Patlamaya sebep olmaz)
        rays = []
        for i, m in enumerate(self.moves):
            mx, my = float(m['pos'][0]), float(m['pos'][1])
            dirs = []
            if self.mode == "BARRIER": dirs = [(0,1),(0,-1),(1,0),(-1,0)]
            elif self.mode == "DIAGONAL": dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
            elif self.mode == "SUPER_RAY": dirs = [(0,1),(0,-1),(1,0),(-1,0), (1,1),(1,-1),(-1,1),(-1,-1)]
            
            for d_idx, (dx, dy) in enumerate(dirs):
                dist = self._get_bound(mx, my, dx, dy)
                rays.append({'start': (mx, my), 'dir': (dx, dy), 'color': m['color'], 'limit': dist})

        cand = []
        for i in range(len(rays)):
            for j in range(i + 1, len(rays)):
                r1, r2 = rays[i], rays[j]
                if r1['color'] == r2['color']: continue
                
                if r1['dir'][0] == -r2['dir'][0] and r1['dir'][1] == -r2['dir'][1]:
                    vx, vy = r2['start'][0]-r1['start'][0], r2['start'][1]-r1['start'][1]
                    if abs(vx*r1['dir'][1]-vy*r1['dir'][0]) < 0.001 and (vx*r1['dir'][0]+vy*r1['dir'][1]) > 0:
                        d = math.sqrt(vx**2+vy**2)
                        cand.append({'r1':i, 'r2':j, 't1':d/2, 't2':d/2, 'pos':(r1['start'][0]+r1['dir'][0]*d/2, r1['start'][1]+r1['dir'][1]*d/2)})
                else:
                    res = self._intersect(r1, r2)
                    if res and res[0]>0.0001 and res[1]>0.0001:
                        cand.append({'r1':i, 'r2':j, 't1':res[0], 't2':res[1], 'pos':res[2]})

        cand.sort(key=lambda x: min(x['t1'], x['t2']))
        red = []
        for c in cand:
            r1, r2 = rays[c['r1']], rays[c['r2']]
            if c['t1'] < r1['limit'] and c['t2'] < r2['limit']:
                r1['limit'], r2['limit'] = c['t1'], c['t2']
                red.append(c['pos'])

        return {
            "mode": self.mode, 
            "lines": [{'start':r['start'], 'end':(r['start'][0]+r['dir'][0]*r['limit'], r['start'][1]+r['dir'][1]*r['limit']), 'color':r['color']} for r in rays], 
            "red_points": red, 
            "moves": self.moves
        }

    def _get_bound(self, x, y, dx, dy):
        tc = []
        if dx > 0: tc.append((18-x)/dx)
        elif dx < 0: tc.append((0-x)/dx)
        if dy > 0: tc.append((18-y)/dy)
        elif dy < 0: tc.append((0-y)/dy)
        return min(tc) if tc else 25.0

    def _intersect(self, r1, r2):
        x1, y1 = r1['start']; v1x, v1y = r1['dir']; x2, y2 = r2['start']; v2x, v2y = r2['dir']
        det = v2x*v1y - v2y*v1x
        if abs(det) < 0.001: return None
        t1 = (v2x*(y2-y1)-v2y*(x2-x1))/det; t2 = (v1x*(y2-y1)-v1y*(x2-x1))/det
        return t1, t2, (x1+v1x*t1, y1+v1y*t1)
    
    def toggle_mode(self):
        modes = ["BARRIER", "DIAGONAL", "SUPER_RAY"]
        # Mevcut modun listedeki yerini bul ve bir sonrakine geç
        current_idx = modes.index(self.mode)
        self.mode = modes[(current_idx + 1) % len(modes)]
        print(f"Mod Değiştirildi: {self.mode}") # Terminalden takip etmek için