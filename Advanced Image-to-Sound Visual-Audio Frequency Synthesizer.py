"""
Advanced Image-to-Sound Visual-Audio Frequency Synthesizer
==========================================================

This project converts images into audio representations using advanced techniques:
- Color analysis and clustering
- Musical scale mapping
- Real-time audio synthesis
- Spectral analysis and visualization
- Multiple synthesis modes
"""
import os
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '3'
import numpy as np
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import pygame
import wave
import struct
import colorsys


from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
import json
from datetime import datetime

import sys
import traceback

def show_console_debug():
    def excepthook(exc_type, exc_value, exc_tb):
        traceback.print_exception(exc_type, exc_value, exc_tb)
    sys.excepthook = excepthook


class AdvancedImageSoundSynthesizer:
    """
    Advanced Image-to-Sound Synthesizer with multiple synthesis modes,
    color analysis, and real-time audio generation.
    """
    
    def __init__(self):
        # Initialize pygame mixer for audio
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        # Audio parameters
        self.sample_rate = 44100
        self.duration = 0.1  # Duration per pixel/chunk in seconds
        self.volume = 0.3
        
        # Musical scales (frequencies in Hz)
        self.scales = {
            'major': [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88],  # C Major
            'minor': [261.63, 293.66, 311.13, 349.23, 392.00, 415.30, 466.16],  # C Minor
            'pentatonic': [261.63, 293.66, 329.63, 392.00, 440.00],  # C Pentatonic
            'blues': [261.63, 311.13, 349.23, 369.99, 392.00, 466.16],  # C Blues
            'chromatic': [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88]
        }
        
        # Color mapping strategies
        self.color_strategies = {
            'hue_mapping': self._map_hue_to_frequency,
            'brightness_mapping': self._map_brightness_to_frequency,
            'dominant_color': self._map_dominant_color,
            'rgb_weighted': self._map_rgb_weighted,
            'color_clustering': self._map_color_clusters
        }
        
        # Synthesis modes
        self.synthesis_modes = {
            'sine': self._generate_sine_wave,
            'sawtooth': self._generate_sawtooth_wave,
            'square': self._generate_square_wave,
            'triangle': self._generate_triangle_wave,
            'noise': self._generate_noise_wave
        }
        
        # Current settings
        self.current_image = None
        self.current_audio = None
        self.current_scale = 'major'
        self.current_strategy = 'hue_mapping'
        self.current_synthesis = 'sine'
        self.grid_size = 16
        
        # Analysis results
        self.color_analysis = {}
        self.frequency_map = {}
        
        self.setup_gui()
    
    def setup_gui(self):
        """Create the advanced GUI interface"""
        self.root = tk.Tk()
        self.root.title("Advanced Image-to-Sound Synthesizer")
        self.root.geometry("1200x800")
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Main tab
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Main")
        
        # Analysis tab
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Analysis")
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        self.setup_main_tab()
        self.setup_analysis_tab()
        self.setup_settings_tab()
    
    def setup_main_tab(self):
        """Setup the main interface tab"""
        # Left panel for image
        left_frame = ttk.Frame(self.main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Image display
        ttk.Label(left_frame, text="Image Preview").pack(pady=5)
        self.image_label = ttk.Label(left_frame, text="No image loaded", 
                                   background='lightgray', width=40)
        self.image_label.pack(pady=5, padx=5)
        
        # Image controls
        img_controls = ttk.Frame(left_frame)
        img_controls.pack(pady=10)
        
        ttk.Button(img_controls, text="Load Image", 
                  command=self.load_image).pack(side='left', padx=5)
        ttk.Button(img_controls, text="Process Image", 
                  command=self.process_image).pack(side='left', padx=5)
        
        # Right panel for audio controls
        right_frame = ttk.Frame(self.main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Audio controls
        ttk.Label(right_frame, text="Audio Controls").pack(pady=5)
        
        audio_controls = ttk.Frame(right_frame)
        audio_controls.pack(pady=10)
        
        ttk.Button(audio_controls, text="Generate Audio", 
                  command=self.generate_audio).pack(side='left', padx=5)
        ttk.Button(audio_controls, text="Play Audio", 
                  command=self.play_audio).pack(side='left', padx=5)
        ttk.Button(audio_controls, text="Stop Audio", 
                  command=self.stop_audio).pack(side='left', padx=5)
        
        # Save controls
        save_controls = ttk.Frame(right_frame)
        save_controls.pack(pady=10)
        
        ttk.Button(save_controls, text="Save Audio", 
                  command=self.save_audio).pack(side='left', padx=5)
        ttk.Button(save_controls, text="Export Analysis", 
                  command=self.export_analysis).pack(side='left', padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(right_frame, mode='determinate')
        self.progress.pack(pady=10, fill='x')
        
        # Status
        self.status_label = ttk.Label(right_frame, text="Ready")
        self.status_label.pack(pady=5)
    
    def setup_analysis_tab(self):
        """Setup the analysis visualization tab"""
        # Color analysis display
        analysis_notebook = ttk.Notebook(self.analysis_frame)
        analysis_notebook.pack(fill='both', expand=True)
        
        # Color distribution tab
        color_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(color_frame, text="Color Analysis")
        
        # Frequency mapping tab
        freq_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(freq_frame, text="Frequency Mapping")
        
        # Spectral analysis tab
        spectral_frame = ttk.Frame(analysis_notebook)
        analysis_notebook.add(spectral_frame, text="Spectral Analysis")
        
        # Create matplotlib figures
        self.setup_analysis_plots(color_frame, freq_frame, spectral_frame)
    
    def setup_analysis_plots(self, color_frame, freq_frame, spectral_frame):
        """Setup matplotlib plots for analysis"""
        # Color analysis plot
        self.color_fig, self.color_ax = plt.subplots(figsize=(8, 6))
        self.color_canvas = FigureCanvasTkAgg(self.color_fig, color_frame)
        self.color_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Frequency mapping plot
        self.freq_fig, self.freq_ax = plt.subplots(figsize=(8, 6))
        self.freq_canvas = FigureCanvasTkAgg(self.freq_fig, freq_frame)
        self.freq_canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Spectral analysis plot
        self.spectral_fig, self.spectral_ax = plt.subplots(figsize=(8, 6))
        self.spectral_canvas = FigureCanvasTkAgg(self.spectral_fig, spectral_frame)
        self.spectral_canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def setup_settings_tab(self):
        """Setup the settings configuration tab"""
        # Audio settings
        audio_frame = ttk.LabelFrame(self.settings_frame, text="Audio Settings")
        audio_frame.pack(fill='x', padx=10, pady=5)
        
        # Musical scale selection
        ttk.Label(audio_frame, text="Musical Scale:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.scale_var = tk.StringVar(value=self.current_scale)
        scale_combo = ttk.Combobox(audio_frame, textvariable=self.scale_var, 
                                  values=list(self.scales.keys()), state='readonly')
        scale_combo.grid(row=0, column=1, padx=5, pady=5)
        scale_combo.bind('<<ComboboxSelected>>', self.update_scale)
        
        # Synthesis mode selection
        ttk.Label(audio_frame, text="Synthesis Mode:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.synthesis_var = tk.StringVar(value=self.current_synthesis)
        synthesis_combo = ttk.Combobox(audio_frame, textvariable=self.synthesis_var,
                                     values=list(self.synthesis_modes.keys()), state='readonly')
        synthesis_combo.grid(row=1, column=1, padx=5, pady=5)
        synthesis_combo.bind('<<ComboboxSelected>>', self.update_synthesis)
        
        # Volume control
        ttk.Label(audio_frame, text="Volume:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.volume_var = tk.DoubleVar(value=self.volume)
        volume_scale = ttk.Scale(audio_frame, from_=0.0, to=1.0, variable=self.volume_var,
                               orient='horizontal', command=self.update_volume)
        volume_scale.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        # Image processing settings
        image_frame = ttk.LabelFrame(self.settings_frame, text="Image Processing")
        image_frame.pack(fill='x', padx=10, pady=5)
        
        # Color mapping strategy
        ttk.Label(image_frame, text="Color Strategy:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.strategy_var = tk.StringVar(value=self.current_strategy)
        strategy_combo = ttk.Combobox(image_frame, textvariable=self.strategy_var,
                                    values=list(self.color_strategies.keys()), state='readonly')
        strategy_combo.grid(row=0, column=1, padx=5, pady=5)
        strategy_combo.bind('<<ComboboxSelected>>', self.update_strategy)
        
        # Grid size for processing
        ttk.Label(image_frame, text="Grid Size:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.grid_var = tk.IntVar(value=self.grid_size)
        grid_scale = ttk.Scale(image_frame, from_=8, to=64, variable=self.grid_var,
                             orient='horizontal', command=self.update_grid_size)
        grid_scale.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Duration per note
        ttk.Label(image_frame, text="Note Duration (s):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.duration_var = tk.DoubleVar(value=self.duration)
        duration_scale = ttk.Scale(image_frame, from_=0.05, to=1.0, variable=self.duration_var,
                                 orient='horizontal', command=self.update_duration)
        duration_scale.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
    
    def load_image(self):
        """Load an image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        
        if file_path:
            try:
                self.current_image = cv2.imread(file_path)
                self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
                
                # Display image
                self.display_image()
                self.update_status("Image loaded successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def display_image(self):
        """Display the current image in the GUI"""
        if self.current_image is not None:
            # Resize image for display
            display_image = cv2.resize(self.current_image, (300, 300))
            
            # Convert to PIL Image for tkinter
            pil_image = Image.fromarray(display_image)
            photo = ImageTk.PhotoImage(pil_image)
            
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
    
    def process_image(self):
        """Process the current image for audio generation"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        try:
            self.update_status("Processing image...")
            self.progress['value'] = 0
            
            # Resize image to manageable size
            processed_image = cv2.resize(self.current_image, (self.grid_size, self.grid_size))
            
            # Perform color analysis
            self.color_analysis = self.analyze_colors(processed_image)
            
            # Generate frequency mapping
            self.frequency_map = self.generate_frequency_mapping(processed_image)
            
            # Update analysis visualizations
            self.update_analysis_plots()
            
            self.progress['value'] = 100
            self.update_status("Image processed successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")
            self.update_status("Processing failed")
    
    def analyze_colors(self, image):
        """Perform comprehensive color analysis"""
        analysis = {}
        
        # Color distribution
        colors = image.reshape(-1, 3)
        analysis['color_distribution'] = self.get_color_distribution(colors)
        
        # Dominant colors using K-means
        if len(colors) > 0:
            n_colors = min(8, len(np.unique(colors.view(np.dtype((np.void, colors.dtype.itemsize*colors.shape[1]))))))
            if n_colors > 1:
                kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
                kmeans.fit(colors)
                analysis['dominant_colors'] = kmeans.cluster_centers_
                analysis['color_labels'] = kmeans.labels_
        
        # HSV analysis
        hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        analysis['hsv_distribution'] = {
            'hue': np.mean(hsv_image[:,:,0]),
            'saturation': np.mean(hsv_image[:,:,1]),
            'value': np.mean(hsv_image[:,:,2])
        }
        
        # Brightness analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        analysis['brightness'] = {
            'mean': np.mean(gray),
            'std': np.std(gray),
            'min': np.min(gray),
            'max': np.max(gray)
        }
        
        return analysis
    
    def get_color_distribution(self, colors):
        """Calculate color distribution statistics"""
        return {
            'mean_rgb': np.mean(colors, axis=0),
            'std_rgb': np.std(colors, axis=0),
            'unique_colors': len(np.unique(colors.view(np.dtype((np.void, colors.dtype.itemsize*colors.shape[1]))))),
            'color_variance': np.var(colors, axis=0)
        }
    
    def generate_frequency_mapping(self, image):
        """Generate frequency mapping based on current strategy"""
        strategy_func = self.color_strategies[self.current_strategy]
        return strategy_func(image)
    
    def _map_hue_to_frequency(self, image):
        """Map hue values to frequencies"""
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        frequencies = []
        
        for row in hsv:
            freq_row = []
            for pixel in row:
                hue = pixel[0] / 180.0  # Normalize hue to 0-1
                scale_idx = int(hue * (len(self.scales[self.current_scale]) - 1))
                freq = self.scales[self.current_scale][scale_idx]
                freq_row.append(freq)
            frequencies.append(freq_row)
        
        return np.array(frequencies)
    
    def _map_brightness_to_frequency(self, image):
        """Map brightness values to frequencies"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        frequencies = []
        
        for row in gray:
            freq_row = []
            for pixel in row:
                brightness = pixel / 255.0  # Normalize to 0-1
                scale_idx = int(brightness * (len(self.scales[self.current_scale]) - 1))
                freq = self.scales[self.current_scale][scale_idx]
                freq_row.append(freq)
            frequencies.append(freq_row)
        
        return np.array(frequencies)
    
    def _map_dominant_color(self, image):
        """Map based on dominant color in each region"""
        if 'dominant_colors' not in self.color_analysis:
            return self._map_hue_to_frequency(image)
        
        dominant_colors = self.color_analysis['dominant_colors']
        frequencies = []
        
        for row in image:
            freq_row = []
            for pixel in row:
                # Find closest dominant color
                distances = cdist([pixel], dominant_colors)
                closest_idx = np.argmin(distances)
                
                # Map to frequency
                freq_idx = closest_idx % len(self.scales[self.current_scale])
                freq = self.scales[self.current_scale][freq_idx]
                freq_row.append(freq)
            frequencies.append(freq_row)
        
        return np.array(frequencies)
    
    def _map_rgb_weighted(self, image):
        """Map RGB values with weighted formula to frequencies"""
        frequencies = []
        
        for row in image:
            freq_row = []
            for pixel in row:
                # Weighted RGB to single value
                weighted_value = (0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]) / 255.0
                scale_idx = int(weighted_value * (len(self.scales[self.current_scale]) - 1))
                freq = self.scales[self.current_scale][scale_idx]
                freq_row.append(freq)
            frequencies.append(freq_row)
        
        return np.array(frequencies)
    
    def _map_color_clusters(self, image):
        """Map based on color clustering"""
        if 'color_labels' not in self.color_analysis:
            return self._map_hue_to_frequency(image)
        
        labels = self.color_analysis['color_labels'].reshape(image.shape[:2])
        frequencies = []
        
        for row in labels:
            freq_row = []
            for label in row:
                freq_idx = label % len(self.scales[self.current_scale])
                freq = self.scales[self.current_scale][freq_idx]
                freq_row.append(freq)
            frequencies.append(freq_row)
        
        return np.array(frequencies)
    
    def generate_audio(self):
        """Generate audio from the processed image"""
        if self.frequency_map is None or len(self.frequency_map) == 0:
            messagebox.showwarning("Warning", "Please process an image first")
            return
        
        try:
            self.update_status("Generating audio...")
            self.progress['value'] = 0
            
            # Generate audio data
            audio_data = self.synthesize_audio(self.frequency_map)
            
            # Store audio data
            self.current_audio = audio_data
            
            self.progress['value'] = 100
            self.update_status("Audio generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate audio: {str(e)}")
            self.update_status("Audio generation failed")
    
    def synthesize_audio(self, frequency_map):
        """Synthesize audio from frequency mapping"""
        synthesis_func = self.synthesis_modes[self.current_synthesis]
        
        audio_segments = []
        total_pixels = frequency_map.size
        
        for i, freq in enumerate(frequency_map.flatten()):
            # Update progress
            self.progress['value'] = (i / total_pixels) * 100
            self.root.update_idletasks()
            
            # Generate audio segment for this frequency
            segment = synthesis_func(freq, self.duration, self.volume)
            audio_segments.append(segment)
        
        # Combine all segments
        return np.concatenate(audio_segments)
    
    def _generate_sine_wave(self, frequency, duration, volume):
        """Generate a sine wave"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = volume * np.sin(2 * np.pi * frequency * t)
        return wave
    
    def _generate_sawtooth_wave(self, frequency, duration, volume):
        """Generate a sawtooth wave"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = volume * 2 * (t * frequency - np.floor(t * frequency + 0.5))
        return wave
    
    def _generate_square_wave(self, frequency, duration, volume):
        """Generate a square wave"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = volume * np.sign(np.sin(2 * np.pi * frequency * t))
        return wave
    
    def _generate_triangle_wave(self, frequency, duration, volume):
        """Generate a triangle wave"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = volume * 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        return wave
    
    def _generate_noise_wave(self, frequency, duration, volume):
        """Generate filtered noise based on frequency"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        noise = np.random.normal(0, volume, len(t))
        
        # Simple low-pass filter based on frequency
        cutoff = frequency / self.sample_rate
        alpha = cutoff / (1 + cutoff)
        
        filtered_noise = np.zeros_like(noise)
        filtered_noise[0] = noise[0]
        
        for i in range(1, len(noise)):
            filtered_noise[i] = alpha * noise[i] + (1 - alpha) * filtered_noise[i-1]
        
        return filtered_noise
    
    def play_audio(self):
        """Play the generated audio"""
        if self.current_audio is None:
            messagebox.showwarning("Warning", "Please generate audio first")
            return
        
        try:
            # Convert to pygame format
            audio_data = (self.current_audio * 32767).astype(np.int16)
            sound = pygame.sndarray.make_sound(np.stack((audio_data, audio_data), axis=-1))
            sound.play()
            
            self.update_status("Playing audio...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play audio: {str(e)}")
    
    def stop_audio(self):
        """Stop audio playback"""
        pygame.mixer.stop()
        self.update_status("Audio stopped")
    
    def save_audio(self):
        """Save the generated audio to a WAV file"""
        if self.current_audio is None:
            messagebox.showwarning("Warning", "Please generate audio first")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Audio",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")]
        )
        
        if file_path:
            try:
                # Convert to 16-bit integers
                audio_data = (self.current_audio * 32767).astype(np.int16)
                
                # Save as WAV file
                with wave.open(file_path, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(audio_data.tobytes())
                
                messagebox.showinfo("Success", f"Audio saved to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save audio: {str(e)}")
    
    def export_analysis(self):
        """Export analysis results to JSON"""
        if not self.color_analysis:
            messagebox.showwarning("Warning", "Please process an image first")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Analysis",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            try:
                # Prepare data for JSON export
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'settings': {
                        'scale': self.current_scale,
                        'strategy': self.current_strategy,
                        'synthesis': self.current_synthesis,
                        'grid_size': self.grid_size,
                        'duration': self.duration,
                        'volume': self.volume
                    },
                    'color_analysis': self.serialize_analysis(self.color_analysis),
                    'frequency_stats': self.get_frequency_stats()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Analysis exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export analysis: {str(e)}")
    
    def serialize_analysis(self, analysis):
        """Convert numpy arrays to lists for JSON serialization"""
        serialized = {}
        for key, value in analysis.items():
                    if isinstance(value, np.ndarray):
                        serialized[key] = value.tolist()
                    elif isinstance(value, (np.integer, np.int64, np.uint8)):
                        serialized[key] = int(value)
                    elif isinstance(value, (np.floating, np.float32, np.float64)):
                        serialized[key] = float(value)
                    elif isinstance(value, dict):
                        serialized[key] = self.serialize_analysis(value)
                    else:
                        serialized[key] = value
        return serialized
    
    def get_frequency_stats(self):
        """Get statistics about the frequency mapping"""
        if self.frequency_map is None:
            return {}
        
        freqs = self.frequency_map.flatten()
        return {
            'min_frequency': float(np.min(freqs)),
            'max_frequency': float(np.max(freqs)),
            'mean_frequency': float(np.mean(freqs)),
            'std_frequency': float(np.std(freqs)),
            'unique_frequencies': len(np.unique(freqs))
        }
    
    def update_analysis_plots(self):
        """Update the analysis visualization plots"""
        if not self.color_analysis:
            return
        
        # Update color analysis plot
        self.update_color_plot()
        
        # Update frequency mapping plot
        self.update_frequency_plot()
        
        # Update spectral analysis plot
        self.update_spectral_plot()
    
    def update_color_plot(self):
        """Update the color analysis plot"""
        self.color_ax.clear()
        
        if 'dominant_colors' in self.color_analysis:
            colors = self.color_analysis['dominant_colors'] / 255.0
            
            # Create color palette visualization
            for i, color in enumerate(colors):
                self.color_ax.bar(i, 1, color=color, width=0.8)
            
            self.color_ax.set_title('Dominant Colors')
            self.color_ax.set_xlabel('Color Index')
            self.color_ax.set_ylabel('Relative Intensity')
        
        self.color_canvas.draw()
    
    def update_frequency_plot(self):
        """Update the frequency mapping plot"""
        self.freq_ax.clear()
        
        if self.frequency_map is not None:
            # Create frequency heatmap
            im = self.freq_ax.imshow(self.frequency_map, cmap='viridis', aspect='auto')
            self.freq_ax.set_title('Frequency Mapping')
            self.freq_ax.set_xlabel('X Position')
            self.freq_ax.set_ylabel('Y Position')
            
            # Add colorbar
        self.freq_fig.colorbar(im, ax=self.freq_ax, label='Frequency (Hz)')

        
        self.freq_canvas.draw()
    
    def update_spectral_plot(self):
        """Update the spectral analysis plot"""
        self.spectral_ax.clear()
        
        if self.current_audio is not None:
            # Perform FFT analysis
            fft = np.fft.fft(self.current_audio)
            frequencies = np.fft.fftfreq(len(fft), 1/self.sample_rate)
            
            # Plot magnitude spectrum
            magnitude = np.abs(fft)
            self.spectral_ax.plot(frequencies[:len(frequencies)//2], 
                                magnitude[:len(magnitude)//2])
            
            self.spectral_ax.set_title('Audio Spectrum')
            self.spectral_ax.set_xlabel('Frequency (Hz)')
            self.spectral_ax.set_ylabel('Magnitude')
            self.spectral_ax.set_xlim(0, 2000)  # Focus on audible range
        
        self.spectral_canvas.draw()
    
    def update_scale(self, event=None):
        """Update the musical scale"""
        self.current_scale = self.scale_var.get()
        self.update_status(f"Scale changed to {self.current_scale}")
    
    def update_synthesis(self, event=None):
        """Update the synthesis mode"""
        self.current_synthesis = self.synthesis_var.get()
        self.update_status(f"Synthesis mode changed to {self.current_synthesis}")
    
    def update_volume(self, value):
        """Update the volume"""
        self.volume = float(value)
        self.update_status(f"Volume set to {self.volume:.2f}")
    
    def update_strategy(self, event=None):
        """Update the color mapping strategy"""
        self.current_strategy = self.strategy_var.get()
        self.update_status(f"Color strategy changed to {self.current_strategy}")
    
    def update_grid_size(self, value):
        """Update the grid size"""
        self.grid_size = int(float(value))
        self.update_status(f"Grid size set to {self.grid_size}x{self.grid_size}")
    
    def update_duration(self, value):
        """Update the note duration"""
        self.duration = float(value)
        self.update_status(f"Note duration set to {self.duration:.3f}s")
    
    def update_status(self, message):
        """Update the status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


class AudioEffectsProcessor:
    """
    Advanced audio effects processor for enhanced sound synthesis
    """
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
    
    def add_reverb(self, audio, room_size=0.5, damping=0.5, wet_level=0.3):
        """Add reverb effect to audio"""
        # Simple reverb using multiple delayed copies
        delays = [0.03, 0.05, 0.08, 0.11, 0.15]  # Delay times in seconds
        decay_factors = [0.6, 0.4, 0.3, 0.2, 0.1]
        
        reverb_audio = audio.copy()
        
        for delay, decay in zip(delays, decay_factors):
            delay_samples = int(delay * self.sample_rate)
            if delay_samples < len(audio):
                delayed_audio = np.zeros_like(audio)
                delayed_audio[delay_samples:] = audio[:-delay_samples] * decay * room_size
                reverb_audio += delayed_audio
        
        # Mix dry and wet signals
        return audio * (1 - wet_level) + reverb_audio * wet_level
    
    def add_echo(self, audio, delay_time=0.3, decay=0.5, num_echoes=3):
        """Add echo effect to audio"""
        echo_audio = audio.copy()
        
        for i in range(1, num_echoes + 1):
            delay_samples = int(delay_time * i * self.sample_rate)
            if delay_samples < len(audio):
                delayed_audio = np.zeros_like(audio)
                delayed_audio[delay_samples:] = audio[:-delay_samples] * (decay ** i)
                echo_audio += delayed_audio
        
        return echo_audio
    
    def add_distortion(self, audio, gain=2.0, threshold=0.5):
        """Add distortion effect to audio"""
        # Soft clipping distortion
        amplified = audio * gain
        distorted = np.tanh(amplified / threshold) * threshold
        return distorted
    
    def add_chorus(self, audio, rate=1.5, depth=0.002, num_voices=3):
        """Add chorus effect to audio"""
        chorus_audio = audio.copy()
        
        for i in range(1, num_voices + 1):
            # Create slightly delayed and pitch-modulated version
            delay_samples = int(depth * self.sample_rate * np.sin(2 * np.pi * rate * i / self.sample_rate))
            
            if len(delay_samples) > 0:
                delayed_audio = np.zeros_like(audio)
                # Simple chorus approximation
                phase_shift = int(i * 0.01 * self.sample_rate)
                if phase_shift < len(audio):
                    delayed_audio[phase_shift:] = audio[:-phase_shift] * 0.5
                    chorus_audio += delayed_audio
        
        return chorus_audio / num_voices


class ImageFeatureExtractor:
    """
    Advanced image feature extraction for more sophisticated audio mapping
    """
    
    def __init__(self):
        pass
    
    def extract_texture_features(self, image):
        """Extract texture features using local binary patterns"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Calculate local binary pattern
        radius = 1
        n_points = 8
        
        # Simple LBP approximation
        lbp = np.zeros_like(gray)
        for i in range(radius, gray.shape[0] - radius):
            for j in range(radius, gray.shape[1] - radius):
                center = gray[i, j]
                pattern = 0
                for k in range(n_points):
                    angle = 2 * np.pi * k / n_points
                    x = int(i + radius * np.cos(angle))
                    y = int(j + radius * np.sin(angle))
                    if x >= 0 and x < gray.shape[0] and y >= 0 and y < gray.shape[1]:
                        if gray[x, y] >= center:
                            pattern |= (1 << k)
                lbp[i, j] = pattern
        
        return {
            'mean_texture': np.mean(lbp),
            'texture_variance': np.var(lbp),
            'texture_histogram': np.histogram(lbp, bins=256)[0]
        }
    
    def extract_edge_features(self, image):
        """Extract edge features using Canny edge detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        return {
            'edge_density': np.sum(edges) / (edges.shape[0] * edges.shape[1]),
            'edge_distribution': np.histogram(edges, bins=256)[0],
            'edge_strength': np.mean(edges[edges > 0]) if np.any(edges) else 0
        }
    
    def extract_shape_features(self, image):
        """Extract basic shape features"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Find contours
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate features
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            
            # Convex hull
            hull = cv2.convexHull(largest_contour)
            hull_area = cv2.contourArea(hull)
            
            solidity = area / hull_area if hull_area > 0 else 0
            
            return {
                'area': area,
                'perimeter': perimeter,
                'solidity': solidity,
                'aspect_ratio': self.calculate_aspect_ratio(largest_contour),
                'compactness': 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
            }
        
        return {
            'area': 0,
            'perimeter': 0,
            'solidity': 0,
            'aspect_ratio': 1,
            'compactness': 0
        }
    
    def calculate_aspect_ratio(self, contour):
        """Calculate aspect ratio of a contour"""
        x, y, w, h = cv2.boundingRect(contour)
        return w / h if h > 0 else 1


class AdvancedSynthesizer:
    """
    Advanced synthesizer with multiple oscillators and modulation
    """
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
    
    def generate_fm_synthesis(self, carrier_freq, modulator_freq, modulation_index, duration, amplitude):
        """Generate FM synthesis audio"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # FM synthesis: carrier modulated by modulator
        modulator = np.sin(2 * np.pi * modulator_freq * t)
        carrier = np.sin(2 * np.pi * carrier_freq * t + modulation_index * modulator)
        
        return amplitude * carrier
    
    def generate_am_synthesis(self, carrier_freq, modulator_freq, modulation_depth, duration, amplitude):
        """Generate AM synthesis audio"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # AM synthesis: carrier amplitude modulated by modulator
        modulator = np.sin(2 * np.pi * modulator_freq * t)
        carrier = np.sin(2 * np.pi * carrier_freq * t)
        
        return amplitude * carrier * (1 + modulation_depth * modulator)
    
    def generate_subtractive_synthesis(self, frequency, duration, amplitude, cutoff_freq=1000):
        """Generate subtractive synthesis with filtering"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Start with rich harmonic content (sawtooth)
        wave = amplitude * 2 * (t * frequency - np.floor(t * frequency + 0.5))
        
        # Apply simple low-pass filter
        filtered_wave = self.apply_lowpass_filter(wave, cutoff_freq)
        
        return filtered_wave
    
    def apply_lowpass_filter(self, audio, cutoff_freq):
        """Apply a simple low-pass filter"""
        # Simple exponential moving average filter
        alpha = cutoff_freq / (cutoff_freq + self.sample_rate / (2 * np.pi))
        
        filtered = np.zeros_like(audio)
        filtered[0] = audio[0]
        
        for i in range(1, len(audio)):
            filtered[i] = alpha * audio[i] + (1 - alpha) * filtered[i-1]
        
        return filtered
    
    def generate_granular_synthesis(self, base_freq, duration, amplitude, grain_size=0.01, grain_density=100):
        """Generate granular synthesis audio"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        output = np.zeros_like(t)
        
        grain_samples = int(grain_size * self.sample_rate)
        
        # Generate grains
        for i in range(grain_density):
            # Random grain position
            grain_start = np.random.randint(0, len(t) - grain_samples)
            
            # Random frequency variation
            grain_freq = base_freq * (1 + 0.1 * np.random.randn())
            
            # Generate grain
            grain_t = np.linspace(0, grain_size, grain_samples)
            grain = amplitude * np.sin(2 * np.pi * grain_freq * grain_t)
            
            # Apply envelope
            envelope = np.exp(-grain_t * 10)  # Exponential decay
            grain *= envelope
            
            # Add to output
            output[grain_start:grain_start + grain_samples] += grain
        
        return output


# Example usage and advanced features demonstration
if __name__ == "__main__":
    # Create the advanced synthesizer
    synthesizer = AdvancedImageSoundSynthesizer()
    
    # Run the application
    synthesizer.run()

show_console_debug()
"""
Advanced Features Included:

1. **Multiple Color Mapping Strategies:**
   - Hue-based mapping
   - Brightness-based mapping
   - Dominant color analysis
   - RGB weighted mapping
   - K-means color clustering

2. **Advanced Audio Synthesis:**
   - Multiple waveform types (sine, sawtooth, square, triangle, noise)
   - FM synthesis
   - AM synthesis
   - Subtractive synthesis
   - Granular synthesis

3. **Audio Effects Processing:**
   - Reverb
   - Echo
   - Distortion
   - Chorus

4. **Advanced Image Analysis:**
   - Texture feature extraction
   - Edge detection analysis
   - Shape feature extraction
   - Color distribution analysis

5. **Professional GUI:**
   - Tabbed interface
   - Real-time visualization
   - Interactive controls
   - Progress tracking

6. **Data Export/Import:**
   - Save audio as WAV files
   - Export analysis results as JSON
   - Comprehensive logging

7. **Scalability Features:**
   - Configurable grid sizes
   - Multiple musical scales
   - Adjustable parameters
   - Real-time parameter changes

To use this advanced version:

1. Install required dependencies:
   pip install numpy opencv-python pillow pygame matplotlib scikit-learn scipy

2. Run the application:
   python image_sound_synthesizer.py

3. Load an image, configure settings, process the image, and generate audio

The application provides a professional-grade interface for converting images to audio
with multiple synthesis modes, advanced analysis, and comprehensive export capabilities.
"""

