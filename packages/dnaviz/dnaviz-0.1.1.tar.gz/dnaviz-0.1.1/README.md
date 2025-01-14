# DNAviz 🧬

An simple interactive DNA/RNA sequence visualization tool. Useful to check the structures or binding of complex sequences to ensure the correct pairing.

![PyPI version](https://img.shields.io/pypi/v/dnaviz)
![Python versions](https://img.shields.io/pypi/pyversions/dnaviz)

## Features

- 🧬 Interactive DNA/RNA sequence visualization
- 🔄 Real-time base pairing detection
- 🖱️ Drag-and-drop base manipulation
- 📏 Dynamic scaling with grid snapping
- 💾 Save/load visualization states
- 📸 Export as PNG

## Installation

```bash
pip install dnaviz
```

## Quick Start

```bash
# Basic DNA sequence visualization
dnaviz ATGC GCTA

# RNA sequence with specified directions
dnaviz AUGC GCAU -d 53 -d 35

# Multiple strands
dnaviz ATGC GCTA TACG -d 53 -d 35 -d 53
```

## Interactive Controls

### Mouse Controls
- **Click and Drag**: Move bases
- **Shift + Click**: Select multiple bases
- **Click and Drag Scale Bar**: Adjust visualization scale
- **Click and Drag Empty Space**: Selection box

### Keyboard Shortcuts
- **Arrow Keys**: Scroll the view
- **R**: Reset selected strand positions
- **Cmd/Ctrl + S**: Save current state
- **Shift + Cmd/Ctrl + S**: Save as PNG
- **Cmd/Ctrl + L**: Load last saved state
- **ESC**: Quit

## File Management

- Save files are stored in `~/.dna_visualizer/`
- PNG exports include timestamps
- State files are saved as JSON with timestamps

## Base Pairing Rules

- A pairs with T (DNA) or U (RNA)
- G pairs with C
- Correct pairing is shown in green
- Incorrect direction pairing is shown in orange
- Unpaired bases are shown in gray

## Examples

### Basic DNA Visualization
```bash
dnaviz ATGC GCTA
```

### RNA Sequence
```bash
dnaviz AUGC GCAU
```

### Multiple Strands with Directions
```bash
dnaviz ATGC GCTA TACG -d 53 -d 35 -d 53
```
