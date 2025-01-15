#!/usr/bin/env python3
import click
from rich.console import Console
from rich.table import Table
from typing import Tuple
from .visualizer import DNAVisualizer

console = Console()

@click.command()
@click.argument('sequences', nargs=-1, required=True)
@click.option('--direction', '-d', multiple=True, type=click.Choice(['53', '35']),
          help="Direction for each sequence (53 for 5'->3', 35 for 3'->5'). Must match number of sequences.")
def main(sequences: Tuple[str], direction: Tuple[str]) -> None:
    """
    Interactive DNA/RNA sequence visualization tool.
    
    Keyboard shortcuts:
    - Arrow keys: Scroll the view
    - R: Reset selected strand positions
    - Cmd/Ctrl + S: Save current state
    - Shift + Cmd/Ctrl + S: Save as PNG
    - Cmd/Ctrl + L: Load last saved state
    - ESC: Quit
    
    Mouse controls:
    - Click and drag: Move bases
    - Shift + Click: Select multiple bases
    - Click and drag empty space: Select multiple bases in area
    - Cmd/Ctrl + drag: Move bases without snapping to grid
    """
    if len(sequences) < 1:
        console.print("[red]Error:[/red] Please provide at least one sequence", style="bold")
        return
    
    # Convert directions tuple to list
    directions_list = list(direction)
    
    if directions_list and len(directions_list) != len(sequences):
        console.print("[red]Error:[/red] Number of directions must match number of sequences", style="bold")
        return
        
    sequences = [seq.upper() for seq in sequences]
    
    if not all(all(base in 'ATGCU' for base in seq) for seq in sequences):
        console.print("[red]Error:[/red] Sequences must contain only A, T, G, C, or U", style="bold")
        return

    # If no directions provided, use default alternating pattern
    if not directions_list:
        directions_list = ['53' if i % 2 == 0 else '35' for i in range(len(sequences))]
    
    # Create sequence-direction pairs and reverse 3'->5' sequences
    sequences = [seq[::-1] if dir == '35' else seq for seq, dir in zip(sequences, directions_list)]
    seq_data = list(zip(sequences, directions_list))
    
    # Display sequence information
    table = Table(title="DNA/RNA Sequences", show_header=True, header_style="bold magenta")
    table.add_column("Sequence #", style="dim")
    table.add_column("Sequence", style="cyan")
    table.add_column("Direction", style="green")
    
    for i, (seq, direction) in enumerate(seq_data, 1):
        direction_str = "5'->3'" if direction == '53' else "3'->5'"
        table.add_row(str(i), seq, direction_str)
    
    console.print(table)
    
    visualizer = DNAVisualizer(sequences, directions_list)
    visualizer.run()

if __name__ == '__main__':
    main() 