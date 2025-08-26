# 🌀 Air Gesture 3D Painter - Advanced Hand Tracking Art Creation
# A complete application for creating 3D art using hand gestures in the air!
# BY - PARAS DHIMAN

import cv2
import numpy as np
import mediapipe as mp
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import math
import time
from collections import deque
import threading
from datetime import datetime

class AirGesture3DPainter:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        
        self.cap = None
        self.camera_running = False
        
        
        self.strokes_3d = []  
        self.current_stroke = []  
        self.z_depth = 0.5  
        
        
        self.drawing_modes = {
            'POINT': 0,
            'LINE': 1, 
            'RIBBON': 2,
            'SHAPE': 3,
            'ERASE': 4
        }
        self.current_mode = self.drawing_modes['LINE']
        self.current_color = (0, 255, 255)  
        self.brush_size = 3
        
        
        self.rotation_x = 0
        self.rotation_y = 0  
        self.rotation_z = 0
        self.zoom = 1.0
        self.view_center = np.array([320, 240, 0])  
        
        
        self.gesture_history = deque(maxlen=10)  
        self.last_gesture = None
        self.gesture_cooldown = 0
        
        
        self.glow_trails = deque(maxlen=50) 
        self.particle_effects = []
        
        
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("🌀 Air Gesture 3D Painter - Advanced Hand Tracking Art")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        self.create_control_panel()
        self.create_canvas_frame()
        self.create_status_panel()
        self.root.bind('<Key>', self.on_keypress)
        self.root.focus_set()
        
    def create_control_panel(self):
        control_frame = tk.Frame(self.root, bg='#2d2d2d', relief='raised', bd=2)
        control_frame.pack(side='left', fill='y', padx=5, pady=5)
        title_label = tk.Label(control_frame, text="🌀 3D Air Painter", 
                              font=('Arial', 16, 'bold'), fg='cyan', bg='#2d2d2d')
        title_label.pack(pady=10)
        
        camera_frame = tk.LabelFrame(control_frame, text="Camera", 
                                   fg='white', bg='#2d2d2d', font=('Arial', 10, 'bold'))
        camera_frame.pack(fill='x', padx=5, pady=5)
        
        self.start_button = tk.Button(camera_frame, text="🎥 Start Camera", 
                                     command=self.start_camera, bg='#4CAF50', fg='white')
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(camera_frame, text="⏹️ Stop Camera", 
                                    command=self.stop_camera, bg='#f44336', fg='white')
        self.stop_button.pack(pady=5)
        
        # Drawing mode controls
        mode_frame = tk.LabelFrame(control_frame, text="Drawing Mode", 
                                 fg='white', bg='#2d2d2d', font=('Arial', 10, 'bold'))
        mode_frame.pack(fill='x', padx=5, pady=5)
        
        # Mode selection buttons
        modes = [('✏️ Point', 'POINT'), ('📏 Line', 'LINE'), 
                ('🎀 Ribbon', 'RIBBON'), ('🔷 Shape', 'SHAPE'), ('🗑️ Erase', 'ERASE')]
        
        for text, mode in modes:
            btn = tk.Button(mode_frame, text=text, 
                          command=lambda m=mode: self.set_drawing_mode(m),
                          bg='#555', fg='white', width=12)
            btn.pack(pady=2)
            
        # Color controls
        color_frame = tk.LabelFrame(control_frame, text="Colors & Effects", 
                                  fg='white', bg='#2d2d2d', font=('Arial', 10, 'bold'))
        color_frame.pack(fill='x', padx=5, pady=5)
        
        self.color_button = tk.Button(color_frame, text="🎨 Choose Color", 
                                     command=self.choose_color, bg='#9C27B0', fg='white')
        self.color_button.pack(pady=5)
        
        # Brush size slider
        tk.Label(color_frame, text="Brush Size:", fg='white', bg='#2d2d2d').pack()
        self.brush_scale = tk.Scale(color_frame, from_=1, to=10, orient='horizontal',
                                   bg='#2d2d2d', fg='white', troughcolor='#555')
        self.brush_scale.set(3)
        self.brush_scale.pack(fill='x', padx=5)
        
        # 3D View controls
        view_frame = tk.LabelFrame(control_frame, text="3D View Controls", 
                                 fg='white', bg='#2d2d2d', font=('Arial', 10, 'bold'))
        view_frame.pack(fill='x', padx=5, pady=5)
        
        # Rotation controls
        rotation_controls = [
            ('Rotate X', self.rotate_x),
            ('Rotate Y', self.rotate_y), 
            ('Rotate Z', self.rotate_z),
            ('🔄 Reset View', self.reset_view)
        ]
        
        for text, command in rotation_controls:
            btn = tk.Button(view_frame, text=text, command=command,
                          bg='#607D8B', fg='white', width=12)
            btn.pack(pady=2)
            
        # Zoom slider
        tk.Label(view_frame, text="Zoom:", fg='white', bg='#2d2d2d').pack()
        self.zoom_scale = tk.Scale(view_frame, from_=0.1, to=3.0, resolution=0.1,
                                  orient='horizontal', bg='#2d2d2d', fg='white',
                                  troughcolor='#555')
        self.zoom_scale.set(1.0)
        self.zoom_scale.pack(fill='x', padx=5)
        
        # File operations
        file_frame = tk.LabelFrame(control_frame, text="File Operations", 
                                 fg='white', bg='#2d2d2d', font=('Arial', 10, 'bold'))
        file_frame.pack(fill='x', padx=5, pady=5)
        
        file_buttons = [
            ('💾 Save 3D Model', self.save_3d_model),
            ('🎬 Record Video', self.toggle_recording),
            ('🗑️ Clear All', self.clear_canvas),
            ('❓ Help', self.show_help)
        ]
        
        for text, command in file_buttons:
            btn = tk.Button(file_frame, text=text, command=command,
                          bg='#795548', fg='white', width=12)
            btn.pack(pady=2)
            
    def create_canvas_frame(self):
        """Create the main canvas area for video display"""
        self.canvas_frame = tk.Frame(self.root, bg='black', relief='sunken', bd=2)
        self.canvas_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Canvas for video display
        self.canvas = tk.Canvas(self.canvas_frame, bg='black', width=640, height=480)
        self.canvas.pack(expand=True, fill='both')
        
        # Add mouse bindings for manual 3D control
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<MouseWheel>', self.on_canvas_scroll)
        
        # Store mouse state
        self.mouse_start_pos = None
        
    def create_status_panel(self):
        """Create status bar at the bottom"""
        status_frame = tk.Frame(self.root, bg='#2d2d2d', height=30)
        status_frame.pack(side='bottom', fill='x')
        
        self.status_label = tk.Label(status_frame, text="Ready - Start camera to begin painting!",
                                   fg='lime', bg='#2d2d2d', anchor='w')
        self.status_label.pack(side='left', padx=10)
        
        self.fps_label = tk.Label(status_frame, text="FPS: 0", 
                                 fg='yellow', bg='#2d2d2d', anchor='e')
        self.fps_label.pack(side='right', padx=10)
        
    def start_camera(self):
        """Initialize and start the camera feed"""
        try:
            self.cap = cv2.VideoCapture(0)  # Use default camera
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open camera!")
                return
                
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.camera_running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
            # Start camera processing in separate thread
            self.camera_thread = threading.Thread(target=self.camera_loop)
            self.camera_thread.daemon = True
            self.camera_thread.start()
            
            self.update_status("Camera started - Move your hands to start painting!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
            
    def stop_camera(self):
        """Stop the camera and cleanup"""
        self.camera_running = False
        if self.cap:
            self.cap.release()
            
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.canvas.delete("all")
        self.update_status("Camera stopped")
        
    def camera_loop(self):
        """Main camera processing loop (runs in separate thread)"""
        while self.camera_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                    
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process the frame
                processed_frame = self.process_frame(frame)
                
                # Convert to PhotoImage for Tkinter
                frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                from PIL import Image, ImageTk
                image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image)
                
                # Update canvas on main thread
                self.root.after_idle(self.update_canvas, photo)
                
                # Calculate FPS
                self.calculate_fps()
                
                # Small delay to prevent overwhelming the GUI
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Camera loop error: {e}")
                break
                
    def process_frame(self, frame):
        """Process each camera frame for hand detection and 3D drawing"""
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        # Create a copy for drawing
        output_frame = frame.copy()
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw hand skeleton
                self.mp_draw.draw_landmarks(output_frame, hand_landmarks, 
                                          self.mp_hands.HAND_CONNECTIONS)
                
                # Extract hand information
                hand_info = self.extract_hand_info(hand_landmarks, frame.shape)
                
                # Detect gestures
                gesture = self.detect_gesture(hand_info)
                
                # Process drawing based on gesture
                self.process_drawing(hand_info, gesture, hand_idx)
                
                # Draw visual feedback
                self.draw_visual_feedback(output_frame, hand_info, gesture)
        
        # Draw 3D strokes on the frame
        self.render_3d_strokes(output_frame)
        
        # Add UI overlays
        self.draw_ui_overlays(output_frame)
        
        return output_frame
        
    def extract_hand_info(self, hand_landmarks, frame_shape):
        """Extract useful information from detected hand landmarks"""
        h, w = frame_shape[:2]
        
        # Convert normalized coordinates to pixel coordinates
        landmarks = []
        for lm in hand_landmarks.landmark:
            x = int(lm.x * w)
            y = int(lm.y * h)
            z = lm.z  # Relative depth
            landmarks.append([x, y, z])
            
        landmarks = np.array(landmarks)
        
        # Extract key points
        hand_info = {
            'landmarks': landmarks,
            'fingertips': {
                'thumb': landmarks[4],
                'index': landmarks[8], 
                'middle': landmarks[12],
                'ring': landmarks[16],
                'pinky': landmarks[20]
            },
            'palm_center': np.mean(landmarks[[0, 5, 9, 13, 17]], axis=0),
            'bounding_box': self.get_bounding_box(landmarks[:, :2]),
            'hand_size': self.calculate_hand_size(landmarks)
        }
        
        return hand_info
        
    def get_bounding_box(self, points):
        """Calculate bounding box of hand landmarks"""
        x_min, y_min = np.min(points, axis=0)
        x_max, y_max = np.max(points, axis=0)
        return [x_min, y_min, x_max - x_min, y_max - y_min]
        
    def calculate_hand_size(self, landmarks):
        """Calculate hand size for depth estimation"""
        # Distance between wrist and middle finger tip
        wrist = landmarks[0]
        middle_tip = landmarks[12]
        return np.linalg.norm(middle_tip - wrist)
        
    def detect_gesture(self, hand_info):
        """Detect hand gestures for tool switching"""
        landmarks = hand_info['landmarks']
        
        # Finger up/down detection
        fingers_up = self.get_fingers_up(landmarks)
        
        # Gesture classification
        if sum(fingers_up) == 1 and fingers_up[1]:  # Only index finger up
            return 'DRAW'
        elif sum(fingers_up) == 2 and fingers_up[1] and fingers_up[2]:  # Index + middle
            return 'RIBBON'  
        elif sum(fingers_up) == 0:  # Fist
            return 'STOP'
        elif sum(fingers_up) == 5:  # All fingers up (open palm)
            return 'ERASE'
        elif fingers_up[0] and sum(fingers_up) == 1:  # Only thumb up
            return 'COLOR_CHANGE'
        elif self.detect_pinch(hand_info):
            return 'PINCH'
        elif self.detect_circle_motion(hand_info):
            return 'ROTATE'
        else:
            return 'NEUTRAL'
            
    def get_fingers_up(self, landmarks):
        """Determine which fingers are raised"""
        fingers = []
        
        # Thumb (compare x coordinates)
        if landmarks[4][0] > landmarks[3][0]:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # Other fingers (compare y coordinates)
        for tip_id in [8, 12, 16, 20]:
            if landmarks[tip_id][1] < landmarks[tip_id - 2][1]:
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers
        
    def detect_pinch(self, hand_info):
        """Detect pinch gesture between thumb and index finger"""
        thumb_tip = hand_info['fingertips']['thumb']
        index_tip = hand_info['fingertips']['index']
        
        distance = np.linalg.norm(thumb_tip[:2] - index_tip[:2])
        return distance < 30  # Adjust threshold as needed
        
    def detect_circle_motion(self, hand_info):
        """Detect circular motion for rotation control"""
        # Store hand positions in a circular buffer
        self.gesture_history.append(hand_info['palm_center'][:2])
        
        if len(self.gesture_history) < 8:
            return False
            
        # Check if recent positions form a circular pattern
        positions = np.array(list(self.gesture_history))
        center = np.mean(positions, axis=0)
        
        # Calculate angles from center
        angles = []
        for pos in positions:
            angle = np.arctan2(pos[1] - center[1], pos[0] - center[0])
            angles.append(angle)
            
        # Check for significant rotation
        angle_changes = np.diff(angles)
        total_rotation = np.sum(angle_changes)
        
        return abs(total_rotation) > np.pi  # More than 180 degrees
        
    def process_drawing(self, hand_info, gesture, hand_idx):
        """Process drawing commands based on detected gesture"""
        if self.gesture_cooldown > 0:
            self.gesture_cooldown -= 1
            return
            
        # Get current drawing position
        index_tip = hand_info['fingertips']['index']
        
        # Calculate 3D coordinates
        pos_3d = self.convert_to_3d(index_tip, hand_info['hand_size'])
        
        # Handle different gestures
        if gesture == 'DRAW':
            self.add_to_current_stroke(pos_3d, hand_idx)
            self.current_mode = self.drawing_modes['LINE']
            
        elif gesture == 'RIBBON':
            self.add_to_current_stroke(pos_3d, hand_idx, ribbon=True)
            self.current_mode = self.drawing_modes['RIBBON']
            
        elif gesture == 'PINCH':
            self.place_3d_shape(pos_3d)
            self.gesture_cooldown = 10  # Prevent rapid placement
            
        elif gesture == 'COLOR_CHANGE':
            self.cycle_color()
            self.gesture_cooldown = 30
            
        elif gesture == 'ERASE':
            self.current_mode = self.drawing_modes['ERASE']
            self.erase_nearby_strokes(pos_3d)
            
        elif gesture == 'ROTATE':
            self.apply_rotation_gesture(hand_info)
            
        elif gesture == 'STOP':
            self.finish_current_stroke()
            
        # Update gesture history
        self.last_gesture = gesture
        
    def convert_to_3d(self, pos_2d, hand_size):
        """Convert 2D camera coordinates to 3D world coordinates"""
        x, y, z_rel = pos_2d
        
        # Normalize to -1 to 1 range
        x_norm = (x - 320) / 320  # Assuming 640px width
        y_norm = (y - 240) / 240  # Assuming 480px height
        
        # Estimate Z depth based on hand size (larger = closer)
        # Map hand size to depth (you may need to adjust these values)
        z_norm = 1.0 - min(max((hand_size - 50) / 100, 0), 1)
        
        return np.array([x_norm, y_norm, z_norm])
        
    def add_to_current_stroke(self, pos_3d, hand_idx, ribbon=False):
        """Add a point to the current stroke being drawn"""
        if not hasattr(self, 'current_stroke') or self.current_stroke is None:
            self.current_stroke = {
                'points': [],
                'color': self.current_color,
                'hand_id': hand_idx,
                'type': 'ribbon' if ribbon else 'line',
                'size': self.brush_scale.get(),
                'timestamp': time.time()
            }
            
        self.current_stroke['points'].append(pos_3d.copy())
        
        # Add to glow trail for visual effect
        self.glow_trails.append({
            'pos': pos_3d.copy(),
            'color': self.current_color,
            'birth_time': time.time(),
            'life': 1.0
        })
        
    def finish_current_stroke(self):
        """Finish the current stroke and add it to permanent storage"""
        if hasattr(self, 'current_stroke') and self.current_stroke and len(self.current_stroke['points']) > 1:
            self.strokes_3d.append(self.current_stroke.copy())
            
        self.current_stroke = None
        
    def place_3d_shape(self, pos_3d):
        """Place a 3D geometric shape at the specified position"""
        shape_types = ['cube', 'sphere', 'pyramid', 'cylinder']
        shape_type = shape_types[len(self.strokes_3d) % len(shape_types)]
        
        shape = {
            'type': 'shape',
            'shape_type': shape_type,
            'position': pos_3d.copy(),
            'color': self.current_color,
            'size': self.brush_scale.get() / 10.0,
            'timestamp': time.time()
        }
        
        self.strokes_3d.append(shape)
        
        # Add particle effect
        self.create_particle_effect(pos_3d, 'place')
        
    def erase_nearby_strokes(self, pos_3d, radius=0.1):
        """Erase strokes within a certain radius of the position"""
        strokes_to_remove = []
        
        for i, stroke in enumerate(self.strokes_3d):
            if stroke['type'] == 'shape':
                # Check distance to shape center
                if np.linalg.norm(stroke['position'] - pos_3d) < radius:
                    strokes_to_remove.append(i)
            else:
                # Check distance to stroke points
                for point in stroke['points']:
                    if np.linalg.norm(point - pos_3d) < radius:
                        strokes_to_remove.append(i)
                        break
                        
        # Remove strokes (in reverse order to maintain indices)
        for i in reversed(strokes_to_remove):
            del self.strokes_3d[i]
            
        if strokes_to_remove:
            self.create_particle_effect(pos_3d, 'erase')
            
    def cycle_color(self):
        """Cycle through predefined colors"""
        colors = [
            (0, 255, 255),    # Cyan
            (255, 0, 255),    # Magenta  
            (255, 255, 0),    # Yellow
            (0, 255, 0),      # Green
            (255, 0, 0),      # Red
            (255, 128, 0),    # Orange
            (128, 0, 255),    # Purple
            (255, 255, 255)   # White
        ]
        
        current_index = colors.index(self.current_color) if self.current_color in colors else 0
        next_index = (current_index + 1) % len(colors)
        self.current_color = colors[next_index]
        
    def apply_rotation_gesture(self, hand_info):
        """Apply rotation based on hand motion"""
        if len(self.gesture_history) >= 2:
            prev_pos = self.gesture_history[-2][:2]
            curr_pos = hand_info['palm_center'][:2]
            
            # Calculate rotation based on movement
            movement = curr_pos - prev_pos
            self.rotation_y += movement[0] * 0.01  # Horizontal movement -> Y rotation
            self.rotation_x += movement[1] * 0.01  # Vertical movement -> X rotation
            
    def render_3d_strokes(self, frame):
        """Render all 3D strokes onto the 2D frame"""
        h, w = frame.shape[:2]
        
        # Update zoom and rotation from GUI
        self.zoom = self.zoom_scale.get()
        
        # Render permanent strokes
        for stroke in self.strokes_3d:
            if stroke['type'] == 'shape':
                self.render_3d_shape(frame, stroke)
            else:
                self.render_3d_stroke(frame, stroke)
                
        # Render current stroke being drawn
        if hasattr(self, 'current_stroke') and self.current_stroke and len(self.current_stroke['points']) > 0:
            self.render_3d_stroke(frame, self.current_stroke)
            
        # Render glow trails
        self.render_glow_trails(frame)
        
        # Render particle effects
        self.render_particle_effects(frame)
        
    def render_3d_stroke(self, frame, stroke):
        """Render a single 3D stroke as connected lines"""
        if len(stroke['points']) < 2:
            return
            
        points_2d = []
        for point_3d in stroke['points']:
            point_2d = self.project_3d_to_2d(point_3d)
            points_2d.append(point_2d)
            
        # Draw connected lines with glow effect
        color = stroke['color']
        size = max(1, int(stroke['size'] * self.zoom))
        
        # Draw glow effect (larger, transparent)
        glow_color = tuple(int(c * 0.5) for c in color)
        for i in range(len(points_2d) - 1):
            cv2.line(frame, tuple(map(int, points_2d[i])), 
                    tuple(map(int, points_2d[i + 1])), glow_color, size + 4)
            
        # Draw main line
        for i in range(len(points_2d) - 1):
            cv2.line(frame, tuple(map(int, points_2d[i])), 
                    tuple(map(int, points_2d[i + 1])), color, size)
            
        # Draw ribbon effect for ribbon strokes
        if stroke.get('type') == 'ribbon' and len(points_2d) >= 3:
            self.render_ribbon_effect(frame, points_2d, color, size)
            
    def render_3d_shape(self, frame, shape):
        """Render a 3D geometric shape"""
        center_2d = self.project_3d_to_2d(shape['position'])
        color = shape['color']
        size = max(5, int(shape['size'] * 100 * self.zoom))
        
        if shape['shape_type'] == 'cube':
            # Draw a cube as a square with depth lines
            half_size = size // 2
            top_left = (int(center_2d[0] - half_size), int(center_2d[1] - half_size))
            bottom_right = (int(center_2d[0] + half_size), int(center_2d[1] + half_size))
            
            # Main square
            cv2.rectangle(frame, top_left, bottom_right, color, 2)
            
            # Depth lines
            offset = size // 4
            cv2.line(frame, top_left, (top_left[0] - offset, top_left[1] - offset), color, 2)
            cv2.line(frame, (bottom_right[0], top_left[1]), 
                    (bottom_right[0] - offset, top_left[1] - offset), color, 2)
            cv2.line(frame, (top_left[0], bottom_right[1]), 
                    (top_left[0] - offset, bottom_right[1] - offset), color, 2)
            cv2.line(frame, bottom_right, (bottom_right[0] - offset, bottom_right[1] - offset), color, 2)
            
        elif shape['shape_type'] == 'sphere':
            # Draw a sphere as a circle with shading
            radius = size // 2
            cv2.circle(frame, tuple(map(int, center_2d)), radius, color, 2)
            # Add inner circle for depth
            cv2.circle(frame, tuple(map(int, center_2d)), radius // 2, color, 1)
            
        elif shape['shape_type'] == 'pyramid':
            # Draw a pyramid as triangles
            base_size = size // 2
            height = int(size * 0.8)
            
            # Base points
            base_center = (int(center_2d[0]), int(center_2d[1] + height // 3))
            apex = (int(center_2d[0]), int(center_2d[1] - height // 2))
            
            # Triangle points
            left = (base_center[0] - base_size, base_center[1])
            right = (base_center[0] + base_size, base_center[1])
            back = (base_center[0] - base_size // 2, base_center[1] - base_size // 2)
            
            # Draw triangular faces
            cv2.line(frame, apex, left, color, 2)
            cv2.line(frame, apex, right, color, 2)
            cv2.line(frame, apex, back, color, 2)
            cv2.line(frame, left, right, color, 2)
            cv2.line(frame, left, back, color, 1)
            cv2.line(frame, right, back, color, 1)
            
        elif shape['shape_type'] == 'cylinder':
            # Draw a cylinder as an ellipse with lines
            radius_x = size // 2
            radius_y = size // 4
            height = size
            
            # Top ellipse
            top_center = (int(center_2d[0]), int(center_2d[1] - height // 2))
            cv2.ellipse(frame, top_center, (radius_x, radius_y), 0, 0, 360, color, 2)
            
            # Bottom ellipse
            bottom_center = (int(center_2d[0]), int(center_2d[1] + height // 2))
            cv2.ellipse(frame, bottom_center, (radius_x, radius_y), 0, 0, 360, color, 2)
            
            # Side lines
            cv2.line(frame, (top_center[0] - radius_x, top_center[1]), 
                    (bottom_center[0] - radius_x, bottom_center[1]), color, 2)
            cv2.line(frame, (top_center[0] + radius_x, top_center[1]), 
                    (bottom_center[0] + radius_x, bottom_center[1]), color, 2)
                    
    def render_ribbon_effect(self, frame, points_2d, color, size):
        """Render a ribbon/surface effect between points"""
        if len(points_2d) < 3:
            return
            
        # Create ribbon by drawing filled polygons between adjacent points
        ribbon_width = size + 10
        
        for i in range(len(points_2d) - 1):
            p1 = np.array(points_2d[i])
            p2 = np.array(points_2d[i + 1])
            
            # Calculate perpendicular vector for ribbon width
            direction = p2 - p1
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)
                perpendicular = np.array([-direction[1], direction[0]]) * ribbon_width
                
                # Create ribbon quad
                quad_points = np.array([
                    p1 + perpendicular,
                    p1 - perpendicular,
                    p2 - perpendicular,
                    p2 + perpendicular
                ], dtype=np.int32)
                
                # Fill with semi-transparent color
                overlay = frame.copy()
                cv2.fillPoly(overlay, [quad_points], color)
                cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)
                
    def render_glow_trails(self, frame):
        """Render glowing particle trails"""
        current_time = time.time()
        trails_to_remove = []
        
        for i, trail in enumerate(self.glow_trails):
            # Update trail life
            age = current_time - trail['birth_time']
            trail['life'] = max(0, 1.0 - age / 2.0)  # 2 second lifetime
            
            if trail['life'] <= 0:
                trails_to_remove.append(i)
                continue
                
            # Project to 2D and draw
            pos_2d = self.project_3d_to_2d(trail['pos'])
            
            # Calculate glow properties
            alpha = trail['life']
            radius = int(8 * alpha * self.zoom)
            color = tuple(int(c * alpha) for c in trail['color'])
            
            if radius > 0:
                # Draw glow circle
                overlay = frame.copy()
                cv2.circle(overlay, tuple(map(int, pos_2d)), radius, color, -1)
                cv2.addWeighted(frame, 1 - alpha * 0.5, overlay, alpha * 0.5, 0, frame)
                
        # Remove expired trails
        for i in reversed(trails_to_remove):
            del self.glow_trails[i]
            
    def render_particle_effects(self, frame):
        """Render particle effects for special events"""
        current_time = time.time()
        effects_to_remove = []
        
        for i, effect in enumerate(self.particle_effects):
            age = current_time - effect['birth_time']
            if age > effect['lifetime']:
                effects_to_remove.append(i)
                continue
                
            # Update particles
            for particle in effect['particles']:
                particle['pos'] += particle['velocity']
                particle['velocity'] *= 0.98  # Slow down over time
                
                # Project and draw
                pos_2d = self.project_3d_to_2d(particle['pos'])
                alpha = 1.0 - (age / effect['lifetime'])
                
                if alpha > 0:
                    color = tuple(int(c * alpha) for c in particle['color'])
                    cv2.circle(frame, tuple(map(int, pos_2d)), 
                             max(1, int(3 * alpha)), color, -1)
                             
        # Remove expired effects
        for i in reversed(effects_to_remove):
            del self.particle_effects[i]
            
    def create_particle_effect(self, pos_3d, effect_type='place'):
        """Create a particle effect at the specified 3D position"""
        num_particles = 20 if effect_type == 'place' else 15
        
        particles = []
        for _ in range(num_particles):
            # Random velocity
            velocity = np.random.randn(3) * 0.02
            if effect_type == 'erase':
                velocity *= -1  # Particles move inward
                
            particle = {
                'pos': pos_3d.copy(),
                'velocity': velocity,
                'color': self.current_color if effect_type == 'place' else (255, 100, 100)
            }
            particles.append(particle)
            
        effect = {
            'particles': particles,
            'birth_time': time.time(),
            'lifetime': 1.5,
            'type': effect_type
        }
        
        self.particle_effects.append(effect)
        
    def project_3d_to_2d(self, point_3d):
        """Project 3D coordinates to 2D screen coordinates with rotation and zoom"""
        x, y, z = point_3d
        
        # Apply 3D rotation matrices
        # Rotation around X-axis
        cos_x, sin_x = np.cos(self.rotation_x), np.sin(self.rotation_x)
        y_rot = y * cos_x - z * sin_x
        z_rot = y * sin_x + z * cos_x
        y = y_rot
        z = z_rot
        
        # Rotation around Y-axis  
        cos_y, sin_y = np.cos(self.rotation_y), np.sin(self.rotation_y)
        x_rot = x * cos_y + z * sin_y
        z_rot = -x * sin_y + z * cos_y
        x = x_rot
        z = z_rot
        
        # Rotation around Z-axis
        cos_z, sin_z = np.cos(self.rotation_z), np.sin(self.rotation_z)
        x_rot = x * cos_z - y * sin_z
        y_rot = x * sin_z + y * cos_z
        x = x_rot
        y = y_rot
        
        # Apply perspective projection
        focal_length = 1.0
        perspective_scale = focal_length / (focal_length + z)
        
        # Convert to screen coordinates
        screen_x = (x * perspective_scale * self.zoom * 200) + 320  # Center at 320
        screen_y = (y * perspective_scale * self.zoom * 200) + 240  # Center at 240
        
        return np.array([screen_x, screen_y])
        
    def draw_visual_feedback(self, frame, hand_info, gesture):
        """Draw visual feedback on the frame"""
        # Draw fingertip markers
        for finger, pos in hand_info['fingertips'].items():
            x, y = int(pos[0]), int(pos[1])
            color = (0, 255, 0) if finger == 'index' else (255, 255, 255)
            cv2.circle(frame, (x, y), 5, color, -1)
            
        # Draw gesture indicator
        palm_center = tuple(map(int, hand_info['palm_center'][:2]))
        
        gesture_colors = {
            'DRAW': (0, 255, 255),      # Cyan
            'RIBBON': (255, 0, 255),    # Magenta
            'PINCH': (255, 255, 0),     # Yellow
            'ERASE': (255, 0, 0),       # Red
            'COLOR_CHANGE': (0, 255, 0), # Green
            'ROTATE': (255, 128, 0),    # Orange
            'NEUTRAL': (128, 128, 128)  # Gray
        }
        
        color = gesture_colors.get(gesture, (255, 255, 255))
        cv2.circle(frame, palm_center, 20, color, 3)
        
        # Draw gesture text
        cv2.putText(frame, gesture, (palm_center[0] - 30, palm_center[1] - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                   
        # Draw Z-depth indicator
        bbox = hand_info['bounding_box']
        depth_text = f"Depth: {hand_info['hand_size']:.0f}"
        cv2.putText(frame, depth_text, (int(bbox[0]), int(bbox[1]) - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                   
    def draw_ui_overlays(self, frame):
        """Draw UI overlays and information"""
        h, w = frame.shape[:2]
        
        # Draw coordinate system indicator
        origin = (50, h - 50)
        
        # X-axis (red)
        cv2.arrowedLine(frame, origin, (origin[0] + 30, origin[1]), (0, 0, 255), 2)
        cv2.putText(frame, "X", (origin[0] + 35, origin[1] + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Y-axis (green)
        cv2.arrowedLine(frame, origin, (origin[0], origin[1] - 30), (0, 255, 0), 2)
        cv2.putText(frame, "Y", (origin[0] - 10, origin[1] - 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Draw current mode indicator
        mode_names = {v: k for k, v in self.drawing_modes.items()}
        current_mode_name = mode_names.get(self.current_mode, "UNKNOWN")
        
        cv2.putText(frame, f"Mode: {current_mode_name}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.current_color, 2)
                   
        # Draw stroke count
        cv2.putText(frame, f"Strokes: {len(self.strokes_3d)}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                   
        # Draw rotation info
        cv2.putText(frame, f"Rotation: X{self.rotation_x:.1f} Y{self.rotation_y:.1f} Z{self.rotation_z:.1f}", 
                   (10, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Draw zoom info
        cv2.putText(frame, f"Zoom: {self.zoom:.1f}x", (10, h - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                   
        # Draw crosshair at center
        center = (w // 2, h // 2)
        cv2.line(frame, (center[0] - 10, center[1]), (center[0] + 10, center[1]), (100, 100, 100), 1)
        cv2.line(frame, (center[0], center[1] - 10), (center[0], center[1] + 10), (100, 100, 100), 1)
        
    def update_canvas(self, photo):
        """Update the canvas with new frame"""
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=photo)
        self.canvas.image = photo  # Keep a reference
        
    def calculate_fps(self):
        """Calculate and update FPS"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:  # Update every second
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_start_time = current_time
            
            # Update FPS label on main thread
            self.root.after_idle(lambda: self.fps_label.config(text=f"FPS: {self.current_fps}"))
            
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        
   
    def set_drawing_mode(self, mode):
        self.current_mode = self.drawing_modes[mode]
        self.update_status(f"Drawing mode: {mode}")
        
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Drawing Color")
        if color[0]: 
            r, g, b = color[0]
            self.current_color = (int(b), int(g), int(r))
            self.update_status(f"Color changed to RGB({int(r)}, {int(g)}, {int(b)})")
            
    def rotate_x(self):
        self.rotation_x += 0.1
        
    def rotate_y(self): 
        self.rotation_y += 0.1
        
    def rotate_z(self):
        self.rotation_z += 0.1
        
    def reset_view(self):
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.zoom_scale.set(1.0)
        self.update_status("View reset")
        
    def clear_canvas(self):
        if messagebox.askyesno("Confirm", "Clear all drawings?"):
            self.strokes_3d.clear()
            self.glow_trails.clear()
            self.particle_effects.clear()
            self.current_stroke = None
            self.update_status("Canvas cleared")
            
    def save_3d_model(self):
        if not self.strokes_3d:
            messagebox.showwarning("Warning", "No drawings to save!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".obj",
            filetypes=[("OBJ files", "*.obj"), ("All files", "*.*")],
            title="Save 3D Model"
        )
        
        if filename:
            try:
                self.export_to_obj(filename)
                messagebox.showinfo("Success", f"3D model saved to {filename}")
                self.update_status(f"Model saved: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save model: {str(e)}")
                
    def export_to_obj(self, filename):
        with open(filename, 'w') as f:
            f.write("# 3D Air Gesture Painting Export\n")
            f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total strokes: {len(self.strokes_3d)}\n\n")
            
            vertex_count = 1  
            
            for stroke_idx, stroke in enumerate(self.strokes_3d):
                f.write(f"# Stroke {stroke_idx + 1}\n")
                f.write(f"g stroke_{stroke_idx + 1}\n")
                
                if stroke['type'] == 'shape':
                 
                    center = stroke['position']
                    size = stroke['size']
                    
                    if stroke['shape_type'] == 'cube':
                       
                        for dx in [-size, size]:
                            for dy in [-size, size]:
                                for dz in [-size, size]:
                                    f.write(f"v {center[0] + dx} {center[1] + dy} {center[2] + dz}\n")
                        base = vertex_count
                        faces = [
                            [0, 1, 3, 2], [4, 6, 7, 5], [0, 2, 6, 4],
                            [1, 5, 7, 3], [0, 4, 5, 1], [2, 3, 7, 6]
                        ]
                        for face in faces:
                            f.write(f"f {' '.join(str(base + i) for i in face)}\n")
                        vertex_count += 8
                        
                elif len(stroke['points']) > 1:
                    for point in stroke['points']:
                        f.write(f"v {point[0]} {point[1]} {point[2]}\n")
                    if len(stroke['points']) > 1:
                        indices = list(range(vertex_count, vertex_count + len(stroke['points'])))
                        f.write(f"l {' '.join(map(str, indices))}\n")
                    
                    vertex_count += len(stroke['points'])
                
                f.write("\n")
                
    def toggle_recording(self):
        messagebox.showinfo("Info", "Video recording feature coming soon!")
        
    def show_help(self):
        help_text = """
🌀 Air Gesture 3D Painter - Help

GESTURES:
• Index finger up: Draw lines in 3D space
• Two fingers up: Draw ribbons/surfaces  
• Fist (no fingers): Stop drawing
• Open palm: Erase mode - wave to erase nearby strokes
• Thumbs up: Cycle through colors
• Pinch (thumb + index): Place 3D shapes
• Circle motion: Rotate the 3D view

MOUSE CONTROLS:
• Click + Drag: Manually rotate view
• Scroll wheel: Zoom in/out

KEYBOARD SHORTCUTS:
• Space: Clear all drawings
• R: Reset view
• S: Save 3D model
• C: Choose color
• 1-5: Switch drawing modes

TIPS:
• Move hand closer/farther to draw at different depths
• Use both hands for complex creations
• Try drawing slowly for smooth lines
• Save your creations as OBJ files for 3D printing!

©SoftwareLabs™

Created with ❤ by PARAS DHIMAN.

COPYRIGHTS 2025.
        """
        
        messagebox.showinfo("Help - Air Gesture 3D Painter", help_text)
        
    def on_keypress(self, event):
        key = event.keysym.lower()
        
        if key == 'space':
            self.clear_canvas()
        elif key == 'r':
            self.reset_view()
        elif key == 's':
            self.save_3d_model()
        elif key == 'c':
            self.choose_color()
        elif key in '12345':
            modes = ['POINT', 'LINE', 'RIBBON', 'SHAPE', 'ERASE']
            if int(key) <= len(modes):
                self.set_drawing_mode(modes[int(key) - 1])
                
    def on_canvas_click(self, event):
        self.mouse_start_pos = (event.x, event.y)
        
    def on_canvas_drag(self, event):
        if self.mouse_start_pos:
            dx = event.x - self.mouse_start_pos[0]
            dy = event.y - self.mouse_start_pos[1]
            
            self.rotation_y += dx * 0.01
            self.rotation_x += dy * 0.01
            
            self.mouse_start_pos = (event.x, event.y)
            
    def on_canvas_scroll(self, event):
        if event.delta > 0:
            self.zoom_scale.set(min(3.0, self.zoom_scale.get() + 0.1))
        else:
            self.zoom_scale.set(max(0.1, self.zoom_scale.get() - 0.1))
            
    def run(self):
        try:
            self.update_status("Ready! Click 'Start Camera' to begin painting in 3D space!")
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Application error: {str(e)}")
        finally:
            if self.camera_running:
                self.stop_camera()
                
def main():
    try:
        required_packages = ['cv2', 'mediapipe', 'numpy', 'PIL']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
                
        if missing_packages:
            print("Missing required packages:")
            for package in missing_packages:
                if package == 'cv2':
                    print("- opencv-python (install with: pip install opencv-python)")
                elif package == 'PIL':
                    print("- Pillow (install with: pip install Pillow)")
                else:
                    print(f"- {package} (install with: pip install {package})")
            print("\nInstall missing packages and run again!")
            return
        app = AirGesture3DPainter()
        app.run()
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        print("\nMake sure you have a working webcam and all required packages installed!")

if __name__ == "__main__":
    main()

# ©SoftwareLabs™
# BY - PARAS DHIMAN

