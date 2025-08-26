import pygame
import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random

class Particle4D:
    def __init__(self, x, y, z=0, w=0):
        self.x, self.y, self.z, self.w = x, y, z, w
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.vz = random.uniform(-2, 2)
        self.vw = random.uniform(-1, 1)  # 4th dimension velocity
        self.life = random.randint(60, 120)
        self.max_life = self.life
        self.color = (random.randint(100, 255), random.randint(100, 255), 255)
        self.size = random.uniform(2, 8)
        
    def update(self, time_factor):
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        self.w += self.vw * time_factor  # 4D movement
        self.life -= 1
        
        # 4D rotation effect on position
        rotation_4d = math.sin(self.w * 0.1) * 10
        self.x += math.cos(time_factor * 0.05) * rotation_4d * 0.1
        self.y += math.sin(time_factor * 0.05) * rotation_4d * 0.1
        
        return self.life > 0
    
    def draw(self, screen, time_factor):
        if self.life <= 0:
            return
            
        alpha = int((self.life / self.max_life) * 255)
        # 4D color shifting
        color_shift = int(50 * math.sin(self.w * 0.1 + time_factor * 0.1))
        r = max(0, min(255, self.color[0] + color_shift))
        g = max(0, min(255, self.color[1] + color_shift))
        b = max(0, min(255, self.color[2] + color_shift))
        
        # 4D size modulation
        size_mod = self.size * (1 + 0.3 * math.sin(self.w * 0.2))
        
        surf = pygame.Surface((int(size_mod * 2), int(size_mod * 2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (r, g, b, alpha), (int(size_mod), int(size_mod)), int(size_mod))
        screen.blit(surf, (self.x - size_mod, self.y - size_mod))

class HypercubeRenderer:
    def __init__(self):
        # 4D Hypercube vertices (tesseract)
        self.vertices_4d = []
        for i in range(16):  # 2^4 = 16 vertices for 4D cube
            x = 1 if (i & 1) else -1
            y = 1 if (i & 2) else -1
            z = 1 if (i & 4) else -1
            w = 1 if (i & 8) else -1
            self.vertices_4d.append([x, y, z, w])
        
        # Hypercube edges
        self.edges_4d = []
        for i in range(16):
            for j in range(i + 1, 16):
                # Connect vertices that differ by exactly one coordinate
                diff_count = sum(1 for k in range(4) if self.vertices_4d[i][k] != self.vertices_4d[j][k])
                if diff_count == 1:
                    self.edges_4d.append((i, j))
    
    def project_4d_to_2d(self, vertices_4d, rotation_angles, scale, center):
        # 4D rotation matrices
        angle_xy, angle_xz, angle_xw, angle_yz, angle_yw, angle_zw = rotation_angles
        
        projected = []
        for vertex in vertices_4d:
            x, y, z, w = vertex
            
            # Apply 4D rotations
            # XY rotation
            cos_xy, sin_xy = math.cos(angle_xy), math.sin(angle_xy)
            new_x = x * cos_xy - y * sin_xy
            new_y = x * sin_xy + y * cos_xy
            x, y = new_x, new_y
            
            # XZ rotation
            cos_xz, sin_xz = math.cos(angle_xz), math.sin(angle_xz)
            new_x = x * cos_xz - z * sin_xz
            new_z = x * sin_xz + z * cos_xz
            x, z = new_x, new_z
            
            # XW rotation (4th dimension)
            cos_xw, sin_xw = math.cos(angle_xw), math.sin(angle_xw)
            new_x = x * cos_xw - w * sin_xw
            new_w = x * sin_xw + w * cos_xw
            x, w = new_x, new_w
            
            # Project from 4D to 3D
            distance_4d = 3.0
            factor_4d = distance_4d / (distance_4d + w)
            x_3d = x * factor_4d
            y_3d = y * factor_4d
            z_3d = z * factor_4d
            
            # Project from 3D to 2D
            distance_3d = 4.0
            factor_3d = distance_3d / (distance_3d + z_3d)
            x_2d = int(center[0] + x_3d * scale * factor_3d)
            y_2d = int(center[1] + y_3d * scale * factor_3d)
            
            projected.append((x_2d, y_2d, z_3d))  # Keep z for depth sorting
        
        return projected
    
    def draw(self, screen, center, scale, rotation_angles, color):
        projected = self.project_4d_to_2d(self.vertices_4d, rotation_angles, scale, center)
        
        # Draw edges with depth-based transparency
        for edge in self.edges_4d:
            start_idx, end_idx = edge
            start_pos = projected[start_idx]
            end_pos = projected[end_idx]
            
            # Calculate depth-based alpha
            avg_depth = (start_pos[2] + end_pos[2]) / 2
            alpha = int(150 + 50 * math.tanh(avg_depth))
            alpha = max(50, min(255, alpha))
            
            # Glow effect
            for width in range(4, 1, -1):
                line_alpha = alpha // width
                surf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                pygame.draw.line(surf, (*color, line_alpha), start_pos[:2], end_pos[:2], width)
                screen.blit(surf, (0, 0))
        
        # Draw vertices
        for i, pos in enumerate(projected):
            vertex_alpha = int(200 + 55 * math.sin(i * 0.5))
            size = int(6 + 3 * math.sin(i * 0.3))
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, vertex_alpha), (size, size), size)
            screen.blit(surf, (pos[0] - size, pos[1] - size))

class DNAHelix:
    def __init__(self):
        self.angle_offset = 0
    
    def draw(self, screen, center, height, radius, time_factor):
        points_strand1 = []
        points_strand2 = []
        
        steps = 50
        for i in range(steps):
            t = i / steps
            y = center[1] + (t - 0.5) * height
            
            angle1 = t * 4 * math.pi + time_factor * 0.05
            angle2 = angle1 + math.pi
            
            x1 = center[0] + math.cos(angle1) * radius
            z1 = math.sin(angle1) * radius
            x2 = center[0] + math.cos(angle2) * radius
            z2 = math.sin(angle2) * radius
            
            # Simple 3D projection
            perspective1 = 200 / (200 + z1)
            perspective2 = 200 / (200 + z2)
            
            point1 = (int(x1 * perspective1), int(y))
            point2 = (int(x2 * perspective2), int(y))
            
            points_strand1.append(point1)
            points_strand2.append(point2)
            
            # Draw connecting rungs occasionally
            if i % 5 == 0:
                alpha = int(100 + 50 * math.sin(time_factor * 0.1 + i * 0.5))
                surf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                pygame.draw.line(surf, (100, 255, 100, alpha), point1, point2, 2)
                screen.blit(surf, (0, 0))
        
        # Draw DNA strands
        if len(points_strand1) > 1:
            for i in range(len(points_strand1) - 1):
                # Strand 1 (cyan)
                surf1 = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                pygame.draw.line(surf1, (0, 255, 255, 180), points_strand1[i], points_strand1[i + 1], 3)
                screen.blit(surf1, (0, 0))
                
                # Strand 2 (magenta)
                surf2 = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                pygame.draw.line(surf2, (255, 0, 255, 180), points_strand2[i], points_strand2[i + 1], 3)
                screen.blit(surf2, (0, 0))

class HandTrackingAR:
    def __init__(self):
        pygame.init()
        
        # Full HD display
        self.WIDTH, self.HEIGHT = 1920, 1080
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Advanced AR Interface")
        self.clock = pygame.time.Clock()
        
        # Colors
        self.CYAN = (0, 255, 255)
        self.ORANGE = (255, 165, 0)
        self.WHITE = (255, 255, 255)
        self.PURPLE = (180, 0, 255)
        self.GREEN = (100, 255, 100)
        self.RED = (255, 100, 100)
        
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Track both hands
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Camera setup for full resolution
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        # Animation systems
        self.time = 0
        self.particles_4d = []
        self.hypercube = HypercubeRenderer()
        self.dna_helix = DNAHelix()
        
        # Hand tracking data
        self.hands_data = []
        self.portal_positions = []
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Holographic effects
        self.holo_intensity = 1.0
        self.scan_line_pos = 0
    
    def cv2_to_pygame(self, cv_img):
        """Convert OpenCV image to Pygame surface"""
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        cv_img = np.rot90(cv_img)
        cv_img = np.flipud(cv_img)
        return pygame.surfarray.make_surface(cv_img)
    
    def draw_holographic_overlay(self, camera_surface):
        """Add holographic effects to camera feed"""
        # Create holographic scan lines
        scan_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        for y in range(0, self.HEIGHT, 4):
            alpha = int(30 * math.sin(self.time * 0.1 + y * 0.1))
            if alpha > 0:
                pygame.draw.line(scan_surface, (0, 255, 255, alpha), (0, y), (self.WIDTH, y), 1)
        
        # Moving scan line
        self.scan_line_pos = (self.scan_line_pos + 3) % self.HEIGHT
        for i in range(5):
            alpha = 100 - i * 20
            pygame.draw.line(scan_surface, (255, 255, 255, alpha), 
                           (0, self.scan_line_pos - i), (self.WIDTH, self.scan_line_pos - i), 2)
        
        camera_surface.blit(scan_surface, (0, 0))
        return camera_surface
    
    def draw_energy_field(self, center, radius, intensity=1.0):
        """Draw pulsating energy field around hands"""
        layers = 8
        for layer in range(layers):
            layer_radius = radius * (1 + layer * 0.2)
            alpha = int((intensity * 60) / (layer + 1))
            
            # Create pulsating effect
            pulse = math.sin(self.time * 0.1 + layer * 0.5) * 0.3 + 0.7
            actual_radius = layer_radius * pulse
            
            # Color gradient from center
            if layer < 3:
                color = (255, 255 - layer * 50, 0, alpha)  # Orange to red
            else:
                color = (255 - (layer - 3) * 40, 0, 255, alpha)  # Red to purple
            
            surf = pygame.Surface((actual_radius * 2, actual_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (int(actual_radius), int(actual_radius)), int(actual_radius))
            self.screen.blit(surf, (center[0] - actual_radius, center[1] - actual_radius))
    
    def draw_quantum_tunnels(self):
        """Draw quantum tunnel effects between hands"""
        if len(self.hands_data) >= 2:
            hand1_pos = self.hands_data[0]['center']
            hand2_pos = self.hands_data[1]['center']
            
            # Calculate tunnel points
            steps = 20
            for i in range(steps):
                t = i / steps
                
                # Base interpolation
                x = hand1_pos[0] + (hand2_pos[0] - hand1_pos[0]) * t
                y = hand1_pos[1] + (hand2_pos[1] - hand1_pos[1]) * t
                
                # Add quantum fluctuation
                noise_x = math.sin(self.time * 0.2 + i * 0.5) * 20
                noise_y = math.cos(self.time * 0.15 + i * 0.3) * 15
                
                x += noise_x
                y += noise_y
                
                # Tunnel width varies
                width = int(15 * math.sin(math.pi * t) + 5)
                
                # Color shifts through spectrum
                hue_shift = (self.time * 0.1 + i * 0.2) % 1.0
                r = int(255 * (0.5 + 0.5 * math.sin(hue_shift * 6.28)))
                g = int(255 * (0.5 + 0.5 * math.sin(hue_shift * 6.28 + 2.09)))
                b = int(255 * (0.5 + 0.5 * math.sin(hue_shift * 6.28 + 4.18)))
                
                # Particle effect along tunnel
                if random.random() < 0.3:
                    particle = Particle4D(x, y, random.uniform(-50, 50), random.uniform(-100, 100))
                    particle.color = (r, g, b)
                    self.particles_4d.append(particle)
                
                # Draw tunnel segment
                surf = pygame.Surface((width * 2, width * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (r, g, b, 150), (width, width), width)
                self.screen.blit(surf, (x - width, y - width))
    
    def draw_hand_constellation(self, landmarks):
        """Draw constellation patterns around hand"""
        if not landmarks:
            return
        
        points = [(int(lm.x * self.WIDTH), int(lm.y * self.HEIGHT)) for lm in landmarks]
        
        # Create constellation lines between specific points
        constellation_lines = [
            (0, 4), (0, 8), (0, 12), (0, 16), (0, 20),  # Palm to fingertips
            (4, 8), (8, 12), (12, 16), (16, 20),  # Fingertip connections
        ]
        
        for line in constellation_lines:
            if line[0] < len(points) and line[1] < len(points):
                start = points[line[0]]
                end = points[line[1]]
                
                # Draw constellation line with stars
                steps = 10
                for i in range(steps + 1):
                    t = i / steps
                    x = int(start[0] + (end[0] - start[0]) * t)
                    y = int(start[1] + (end[1] - start[1]) * t)
                    
                    # Twinkling stars
                    twinkle = math.sin(self.time * 0.3 + i + line[0]) * 0.5 + 0.5
                    size = int(2 + twinkle * 3)
                    
                    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (255, 255, 255, int(200 * twinkle)), (size, size), size)
                    self.screen.blit(surf, (x - size, y - size))
    
    def run(self):
        """Main application loop"""
        running = True
        
        while running:
            dt = self.clock.tick(60)
            self.time += 1
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
            
            # Capture camera frame
            success, frame = self.cap.read()
            if not success:
                continue
            
            # Flip and resize frame to full screen
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (self.WIDTH, self.HEIGHT))
            
            # Convert to pygame surface
            camera_surface = self.cv2_to_pygame(frame)
            
            # Apply holographic overlay to camera
            camera_surface = self.draw_holographic_overlay(camera_surface)
            
            # Draw camera feed as background
            self.screen.blit(camera_surface, (0, 0))
            
            # Process hand detection
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Clear hands data
            self.hands_data = []
            
            # Process detected hands
            if results.multi_hand_landmarks:
                for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # Calculate hand center
                    wrist = hand_landmarks.landmark[0]
                    hand_center = (int(wrist.x * self.WIDTH), int(wrist.y * self.HEIGHT))
                    
                    # Store hand data
                    hand_data = {
                        'center': hand_center,
                        'landmarks': hand_landmarks.landmark,
                        'id': i
                    }
                    self.hands_data.append(hand_data)
                    
                    # Draw energy field around hand
                    self.draw_energy_field(hand_center, 80, 1.5)
                    
                    # Draw hand constellation
                    self.draw_hand_constellation(hand_landmarks.landmark)
                    
                    # Spawn 4D particles at fingertips
                    fingertips = [4, 8, 12, 16, 20]
                    for tip_idx in fingertips:
                        if random.random() < 0.1:
                            tip = hand_landmarks.landmark[tip_idx]
                            tip_pos = (int(tip.x * self.WIDTH), int(tip.y * self.HEIGHT))
                            particle = Particle4D(tip_pos[0], tip_pos[1], 
                                                random.uniform(-100, 100), 
                                                random.uniform(-200, 200))
                            self.particles_4d.append(particle)
            
            # Draw quantum tunnels between hands
            self.draw_quantum_tunnels()
            
            # Update and draw 4D particles
            for particle in self.particles_4d[:]:
                if not particle.update(self.time):
                    self.particles_4d.remove(particle)
                else:
                    particle.draw(self.screen, self.time)
            
            # Draw 4D hypercube
            if self.hands_data:
                cube_center = self.hands_data[0]['center']
                cube_center = (cube_center[0] + 200, cube_center[1])
                rotation_angles = [
                    self.time * 0.01, self.time * 0.015, self.time * 0.008,
                    self.time * 0.012, self.time * 0.009, self.time * 0.011
                ]
                self.hypercube.draw(self.screen, cube_center, 60, rotation_angles, self.CYAN)
            
            # Draw DNA helix
            if len(self.hands_data) >= 1:
                dna_center = (self.hands_data[0]['center'][0] - 200, self.hands_data[0]['center'][1])
                self.dna_helix.draw(self.screen, dna_center, 300, 50, self.time)
            
            # Draw UI overlay
            self.draw_ui_overlay()
            
            # Update display
            pygame.display.flip()
        
        # Cleanup
        self.cap.release()
        pygame.quit()
    
    def draw_ui_overlay(self):
        """Draw futuristic UI overlay"""
        # Corner UI panels
        panels = [
            pygame.Rect(20, 20, 300, 100),  # Top left
            pygame.Rect(self.WIDTH - 320, 20, 300, 100),  # Top right
            pygame.Rect(20, self.HEIGHT - 120, 300, 100),  # Bottom left
        ]
        
        for i, panel in enumerate(panels):
            # Panel background
            surf = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
            pygame.draw.rect(surf, (20, 40, 80, 150), surf.get_rect())
            pygame.draw.rect(surf, self.CYAN, surf.get_rect(), 2)
            self.screen.blit(surf, panel.topleft)
            
            # Panel content
            if i == 0:  # Status panel
                text = f"HANDS DETECTED: {len(self.hands_data)}"
                text_surf = self.font_medium.render(text, True, self.GREEN)
                self.screen.blit(text_surf, (panel.x + 10, panel.y + 20))
                
                text2 = f"4D PARTICLES: {len(self.particles_4d)}"
                text_surf2 = self.font_small.render(text2, True, self.WHITE)
                self.screen.blit(text_surf2, (panel.x + 10, panel.y + 50))
            
            elif i == 1:  # Time panel
                text = f"QUANTUM TIME: {self.time}"
                text_surf = self.font_medium.render(text, True, self.PURPLE)
                self.screen.blit(text_surf, (panel.x + 10, panel.y + 20))
            
            elif i == 2:  # Controls panel
                text = "ESC TO EXIT"
                text_surf = self.font_medium.render(text, True, self.RED)
                self.screen.blit(text_surf, (panel.x + 10, panel.y + 40))

# Run the advanced AR interface
if __name__ == "__main__":
    try:
        print("Starting Advanced AR Interface...")
        print("Move your hands to see 4D effects!")
        print("Press ESC to exit")
        
        ar_interface = HandTrackingAR()
        ar_interface.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nRequired packages:")
        print("pip install pygame opencv-python mediapipe numpy")
    except KeyboardInterrupt:
        print("\nExiting...")
        pygame.quit()