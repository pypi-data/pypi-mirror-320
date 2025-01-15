import pygame
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple
import math
import json
import os
from datetime import datetime
from pathlib import Path
from rich.progress import Progress
import click

# Modern color scheme
COLORS = {
    'background': (245, 245, 245),  # Light gray
    'grid': (230, 230, 230),  # Subtle grid
    'grid_major': (210, 210, 210),  # Darker grid for major lines
    'unpaired': (180, 180, 180),  # Lighter gray for unpaired
    'paired': (46, 204, 113),  # Emerald green for paired
    'wrong_direction': (230, 126, 34),  # Carrot orange for wrong direction
    'selection': (52, 152, 219),  # Blue for selection
    'backbone': (44, 62, 80),  # Dark slate for backbone
    'hydrogen_bonds': (46, 204, 113),  # Same as paired (green) for bonds
    'text': (52, 73, 94),  # Wet asphalt for text
    'label_background': (255, 255, 255),  # White for labels
    'label_border': (52, 73, 94),  # Wet asphalt for label borders
    'scale_bg': (255, 255, 255),  # White for scale background
    'scale_shadow': (100, 100, 100),  # Shadow color
}

@dataclass
class Base:
    """Represents a single nucleotide base in the visualization."""
    nucleotide: str  # A, T, G, C, or U
    x: float
    y: float
    strand: int = 1
    is_five_prime: bool = True
    is_paired: bool = False
    is_dragging: bool = False
    
    def __post_init__(self):
        self.radius = 20
        self.color = COLORS['unpaired']
        self.target_x = self.x
        self.target_y = self.y
        
    def is_clicked(self, pos: Tuple[float, float]) -> bool:
        """Check if this base is clicked at the given position."""
        return ((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2) <= self.radius ** 2
    
    def update_color(self, paired: bool, correct_direction: bool):
        """Update the base color based on pairing state and direction."""
        if paired and correct_direction:
            self.color = COLORS['paired']  # Green for correct pairing
        elif paired:
            self.color = COLORS['wrong_direction']  # Orange for wrong direction
        else:
            self.color = COLORS['unpaired']  # Gray for unpaired
    
    def update_position(self, lerp_factor=0.3):
        """Smoothly move towards target position"""
        if self.is_dragging:
            # When dragging, position is set directly
            self.x = self.target_x
            self.y = self.target_y
        else:
            # When not dragging, smoothly interpolate
            self.x += (self.target_x - self.x) * lerp_factor
            self.y += (self.target_y - self.y) * lerp_factor
            
            # Snap to target if very close
            if abs(self.target_x - self.x) < 0.1 and abs(self.target_y - self.y) < 0.1:
                self.x = self.target_x
                self.y = self.target_y
    
    def __hash__(self):
        return hash((self.nucleotide, self.strand, id(self)))
        
    def __eq__(self, other):
        if not isinstance(other, Base):
            return False
        return id(self) == id(other)

class DNAVisualizer:
    def __init__(self, sequences: List[str], directions: List[str]):
        """Initialize the DNA/RNA sequence visualizer."""
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
        pygame.display.set_caption("DNA/RNA Visualizer")
        
        # Initialize strands
        self.strands = []
        spacing = 100
        for i, (seq, direction) in enumerate(zip(sequences, directions)):
            strand = []
            is_five_prime = (direction == '53')
            for j, base in enumerate(seq):
                x = 200 + j * 50
                y = 200 + i * spacing
                strand.append(Base(base, x, y, strand=i+1, is_five_prime=is_five_prime))
            self.strands.append(strand)
        
        # Store original positions for reset
        self.original_positions = []
        for strand in self.strands:
            for base in strand:
                self.original_positions.append((base, (base.x, base.y)))
        
        # Visualization state
        self.scroll_x = 0
        self.scroll_y = 0
        self.base_scale = 1.0
        self.selected_bases = []
        self.is_scaling = False
        self.scale_bar_rect = pygame.Rect(20, 20, 200, 20)
        
        # Selection box state
        self.selection_start = None
        self.selection_active = False
        
        # Save directory setup
        self.save_dir = Path.home() / '.dna_visualizer'
        self.save_dir.mkdir(exist_ok=True)
    
    def _can_pair(self, base1: Base, base2: Base) -> bool:
        """Check if bases can pair based on nucleotide compatibility."""
        if base1.strand == base2.strand:
            return False
            
        pairs = {
            'A': {'T', 'U'},
            'T': {'A'},
            'U': {'A'},
            'G': {'C'},
            'C': {'G'}
        }
        return (base2.nucleotide in pairs.get(base1.nucleotide, set()) or 
                base1.nucleotide in pairs.get(base2.nucleotide, set()))
    
    def _check_pairing(self):
        """Check base pairing and update colors."""
        # Reset all bases to unpaired state
        for strand in self.strands:
            for base in strand:
                base.is_paired = False
                base.update_color(False, False)
        
        # Check each base against bases in all other strands
        paired_bases = set()
        
        for i, strand1 in enumerate(self.strands):
            for base1 in strand1:
                if base1 in paired_bases:
                    continue
                    
                closest_base = None
                min_distance = float('inf')
                
                # Check against all other strands
                for j, strand2 in enumerate(self.strands):
                    if i == j:  # Don't check against same strand
                        continue
                    for base2 in strand2:
                        if base2 in paired_bases:
                            continue
                        if self._can_pair(base1, base2):
                            # Check horizontal distance first
                            dx = abs(base1.x - base2.x)
                            if dx < 50:  # Only check vertical distance if horizontally close
                                dy = abs(base1.y - base2.y)
                                if dy < 150:  # Allow more vertical distance for pairing
                                    distance = (dx * dx + dy * dy) ** 0.5
                                    if distance < min_distance:
                                        min_distance = distance
                                        closest_base = base2
                
                # Update pairing state and colors if a pair is found
                if closest_base:
                    base1.is_paired = True
                    closest_base.is_paired = True
                    paired_bases.add(base1)
                    paired_bases.add(closest_base)
                    
                    # Check if the pairing direction is correct
                    correct_direction = (base1.is_five_prime != closest_base.is_five_prime)
                    
                    # Update colors based on pairing and direction
                    base1.update_color(True, correct_direction)
                    closest_base.update_color(True, correct_direction)
    
    def draw(self):
        """Draw the current state of the visualization."""
        self.screen.fill(COLORS['background'])
        
        # Draw grid
        grid_size = int(50 * self.base_scale)
        width, height = self.screen.get_size()
        for x in range(0, width + grid_size, grid_size):
            adjusted_x = x - self.scroll_x % grid_size
            color = COLORS['grid_major'] if x % (grid_size * 5) == 0 else COLORS['grid']
            pygame.draw.line(self.screen, color, (adjusted_x, 0), (adjusted_x, height))
        for y in range(0, height + grid_size, grid_size):
            adjusted_y = y - self.scroll_y % grid_size
            color = COLORS['grid_major'] if y % (grid_size * 5) == 0 else COLORS['grid']
            pygame.draw.line(self.screen, color, (0, adjusted_y), (width, adjusted_y))
        
        # Draw backbone lines first
        for strand in self.strands:
            if len(strand) > 1:
                points = [(base.x - self.scroll_x, base.y - self.scroll_y) for base in strand]
                pygame.draw.lines(self.screen, COLORS['backbone'], False, points, 2)
        
        # Draw hydrogen bonds between paired bases
        for strand in self.strands:
            for base1 in strand:
                if base1.is_paired:
                    for other_strand in self.strands:
                        if other_strand != strand:
                            for base2 in other_strand:
                                if base2.is_paired and self._can_pair(base1, base2):
                                    dx = abs(base1.x - base2.x)
                                    if dx < 50:
                                        dy = abs(base1.y - base2.y)
                                        if dy < 150:
                                            screen_x1 = base1.x - self.scroll_x
                                            screen_y1 = base1.y - self.scroll_y
                                            screen_x2 = base2.x - self.scroll_x
                                            screen_y2 = base2.y - self.scroll_y
                                            pygame.draw.line(self.screen, COLORS['hydrogen_bonds'],
                                                         (screen_x1, screen_y1),
                                                         (screen_x2, screen_y2), 2)
                                            break
        
        # Draw bases and labels
        for strand in self.strands:
            for i, base in enumerate(strand):
                screen_x = base.x - self.scroll_x
                screen_y = base.y - self.scroll_y
                
                # Update position smoothly
                base.update_position()
                
                # Draw selection highlight
                if base in self.selected_bases:
                    pygame.draw.circle(self.screen, COLORS['selection'],
                                   (screen_x, screen_y), base.radius + 4)
                
                # Draw base circle
                pygame.draw.circle(self.screen, base.color,
                               (screen_x, screen_y), base.radius)
                
                # Draw base letter
                font = pygame.font.Font(None, 36)
                text = font.render(base.nucleotide, True, COLORS['text'])
                text_rect = text.get_rect(center=(screen_x, screen_y))
                self.screen.blit(text, text_rect)
                
                # Draw direction labels at ends
                if i == 0 or i == len(strand) - 1:
                    is_five = (i == 0 and base.is_five_prime) or (i == len(strand) - 1 and not base.is_five_prime)
                    label = "5'" if is_five else "3'"
                    label_text = pygame.font.Font(None, 24).render(label, True, COLORS['text'])
                    label_rect = label_text.get_rect(center=(screen_x, screen_y - base.radius - 15))
                    self.screen.blit(label_text, label_rect)
        
        # Draw scale bar
        pygame.draw.rect(self.screen, COLORS['backbone'], self.scale_bar_rect)
        scale_pos = (self.base_scale - 0.5) / 1.5  # Convert scale to 0-1 range
        handle_x = self.scale_bar_rect.x + scale_pos * self.scale_bar_rect.width
        handle_rect = pygame.Rect(handle_x - 5, self.scale_bar_rect.y - 5, 10, 30)
        pygame.draw.rect(self.screen, COLORS['selection'], handle_rect)
        
        pygame.display.flip()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    self.handle_scrolling(event.key)
                elif event.key == pygame.K_r:
                    self.reset_positions()
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_META:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.save_png()
                    else:
                        self.save_state()
                elif event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_META:
                    self.load_state()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.scale_bar_rect.collidepoint(event.pos):
                        self.is_scaling = True
                    else:
                        # Convert screen position to world position
                        world_pos = (event.pos[0] + self.scroll_x, event.pos[1] + self.scroll_y)
                        clicked_base = None
                        
                        # Check if clicked on a base
                        for strand in self.strands:
                            for base in strand:
                                if base.is_clicked(world_pos):
                                    clicked_base = base
                                    break
                            if clicked_base:
                                break
                        
                        # Handle base selection
                        if clicked_base:
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                if clicked_base not in self.selected_bases:
                                    self.selected_bases.append(clicked_base)
                            else:
                                self.selected_bases = [clicked_base]
                            clicked_base.is_dragging = True
                        else:
                            # Start selection box
                            self.selection_start = world_pos
                            self.selection_active = True
                            if not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                self.selected_bases = []
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.is_scaling = False
                    # Handle selection box
                    if self.selection_active:
                        world_pos = (event.pos[0] + self.scroll_x, event.pos[1] + self.scroll_y)
                        # Get bases in selection box
                        x1, y1 = min(self.selection_start[0], world_pos[0]), min(self.selection_start[1], world_pos[1])
                        x2, y2 = max(self.selection_start[0], world_pos[0]), max(self.selection_start[1], world_pos[1])
                        for strand in self.strands:
                            for base in strand:
                                if (x1 <= base.x <= x2 and y1 <= base.y <= y2 and 
                                    base not in self.selected_bases):
                                    self.selected_bases.append(base)
                        self.selection_active = False
                        self.selection_start = None
                    
                    # Snap dragged bases to grid
                    for base in self.selected_bases:
                        base.is_dragging = False
                        if not pygame.key.get_mods() & pygame.KMOD_META:  # Don't snap if Cmd/Ctrl is held
                            grid_size = int(50 * self.base_scale)
                            base.target_x = round(base.x / grid_size) * grid_size
                            base.target_y = round(base.y / grid_size) * grid_size
            
            elif event.type == pygame.MOUSEMOTION:
                if self.is_scaling:
                    # Update scale
                    self._update_scale(event.pos[0])
                elif any(base.is_dragging for base in self.selected_bases):
                    # Move selected bases
                    dx = event.rel[0]
                    dy = event.rel[1]
                    for base in self.selected_bases:
                        base.x += dx
                        base.y += dy
                        base.target_x = base.x
                        base.target_y = base.y
            
            elif event.type == pygame.VIDEORESIZE:
                width = max(800, event.w)
                height = max(600, event.h)
                self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        
        # Check base pairing after any movement
        self._check_pairing()
        return True
    
    def handle_scrolling(self, key):
        """Handle arrow key scrolling."""
        scroll_amount = 50
        if key == pygame.K_LEFT:
            self.scroll_x = max(0, self.scroll_x - scroll_amount)
        elif key == pygame.K_RIGHT:
            self.scroll_x = min(self.max_scroll_x, self.scroll_x + scroll_amount)
        elif key == pygame.K_UP:
            self.scroll_y = max(0, self.scroll_y - scroll_amount)
        elif key == pygame.K_DOWN:
            self.scroll_y = min(self.max_scroll_y, self.scroll_y + scroll_amount)
    
    def reset_positions(self):
        """Reset selected bases to their original positions."""
        if not self.selected_bases:
            return
            
        # Get all strands that have selected bases
        selected_strands = set()
        for base in self.selected_bases:
            for strand in self.strands:
                if base in strand:
                    selected_strands.add(tuple(strand))
                    break
        
        # Reset positions for all bases in selected strands
        for strand in selected_strands:
            for base in strand:
                for orig_base, (orig_x, orig_y) in self.original_positions:
                    if base == orig_base:
                        base.target_x = orig_x
                        base.target_y = orig_y
                        break
    
    def save_png(self):
        """Save the current view as a PNG file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.save_dir / f"dna_viz_{timestamp}.png"
        pygame.image.save(self.screen, str(filename))
        click.echo(f"Saved PNG to {filename}")
    
    def save_state(self):
        """Save the current state as a JSON file."""
        state = {
            'scroll_x': self.scroll_x,
            'scroll_y': self.scroll_y,
            'base_scale': self.base_scale,
            'strands': [
                [{'type': b.type, 'x': b.x, 'y': b.y, 'direction': b.direction}
                 for b in strand]
                for strand in self.strands
            ]
        }
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.save_dir / f"dna_state_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(state, f)
        click.echo(f"Saved state to {filename}")
    
    def load_state(self):
        """Load the most recent state file."""
        state_files = sorted(self.save_dir.glob("dna_state_*.json"))
        if not state_files:
            click.echo("No saved states found")
            return
        
        latest_state = state_files[-1]
        with open(latest_state) as f:
            state = json.load(f)
        
        self.scroll_x = state['scroll_x']
        self.scroll_y = state['scroll_y']
        self.base_scale = state['base_scale']
        
        for strand_data, strand in zip(state['strands'], self.strands):
            for base_data, base in zip(strand_data, strand):
                base.x = base_data['x']
                base.y = base_data['y']
        
        click.echo(f"Loaded state from {latest_state}")
    
    def _update_scale(self, mouse_x):
        """Update scale based on mouse position."""
        # Calculate scale from slider position
        scale_pos = (mouse_x - self.scale_bar_rect.x) / self.scale_bar_rect.width
        scale_pos = max(0, min(1, scale_pos))  # Clamp to 0-1 range
        self.base_scale = 0.5 + scale_pos * 1.5  # Scale from 0.5 to 2.0
        
        # Update base radius and snap all bases to new grid
        grid_size = int(50 * self.base_scale)
        for strand in self.strands:
            for base in strand:
                base.radius = int(20 * self.base_scale)
                # Snap to new grid size
                base.x = round(base.x / grid_size) * grid_size
                base.y = round(base.y / grid_size) * grid_size
                base.target_x = base.x
                base.target_y = base.y
    
    def run(self):
        """Main visualization loop."""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            pygame.time.Clock().tick(60)
        
        pygame.quit()
        sys.exit() 