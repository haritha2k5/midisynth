# visualize_ast.py - MidiSynth AST Visualizer
# Draws the Abstract Syntax Tree using matplotlib

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from lexer import tokenize
from parser import (Parser, ProgramNode, TempoNode, InstrumentNode,
                    PlayNode, RepeatNode, ChordNode)

# ---------------------------------------------------------------------------
# Color scheme - each node type gets its own color
# ---------------------------------------------------------------------------
NODE_COLORS = {
    'Program':    '#4A90D9',   # blue
    'Tempo':      '#7B68EE',   # purple
    'Instrument': '#20B2AA',   # teal
    'Play':       '#3CB371',   # green
    'Repeat':     '#FF8C00',   # orange
    'Chord':      '#DC143C',   # red
    'Note':       '#90EE90',   # light green
    'Duration':   '#FFD700',   # gold
}

# ---------------------------------------------------------------------------
# Tree node - used internally for layout calculation
# ---------------------------------------------------------------------------


class TreeNode:
    def __init__(self, label, color, children=None):
        self.label = label
        self.color = color
        self.children = children or []
        self.x = 0.0
        self.y = 0.0

# ---------------------------------------------------------------------------
# Convert AST nodes into TreeNode structure
# ---------------------------------------------------------------------------


def ast_to_tree(node):
    if isinstance(node, ProgramNode):
        children = [ast_to_tree(s) for s in node.statements]
        return TreeNode('Program', NODE_COLORS['Program'], children)

    elif isinstance(node, TempoNode):
        bpm_node = TreeNode(str(node.bpm), NODE_COLORS['Duration'])
        return TreeNode('TEMPO', NODE_COLORS['Tempo'], [bpm_node])

    elif isinstance(node, InstrumentNode):
        name_node = TreeNode(node.name, NODE_COLORS['Duration'])
        return TreeNode('INSTRUMENT', NODE_COLORS['Instrument'], [name_node])

    elif isinstance(node, PlayNode):
        note_node = TreeNode(node.note,     NODE_COLORS['Note'])
        dur_node = TreeNode(node.duration, NODE_COLORS['Duration'])
        return TreeNode('PLAY', NODE_COLORS['Play'], [note_node, dur_node])

    elif isinstance(node, RepeatNode):
        count_node = TreeNode(f'x{node.count}', NODE_COLORS['Duration'])
        body_nodes = [ast_to_tree(s) for s in node.body]
        return TreeNode('REPEAT', NODE_COLORS['Repeat'], [count_node] + body_nodes)

    elif isinstance(node, ChordNode):
        note_nodes = [TreeNode(n, NODE_COLORS['Note']) for n in node.notes]
        dur_node = TreeNode(node.duration, NODE_COLORS['Duration'])
        return TreeNode('CHORD', NODE_COLORS['Chord'], note_nodes + [dur_node])

    return TreeNode('?', '#aaaaaa')

# ---------------------------------------------------------------------------
# Layout algorithm - assigns x, y positions to each node
# ---------------------------------------------------------------------------


def assign_positions(node, depth=0, counter=[0]):
    """
    Simple left-to-right layout.
    Leaf nodes get sequential x positions.
    Parent nodes are centered over their children.
    """
    if not node.children:
        node.x = counter[0]
        node.y = -depth
        counter[0] += 1
    else:
        for child in node.children:
            assign_positions(child, depth + 1, counter)
        # Center parent over its children
        node.x = (node.children[0].x + node.children[-1].x) / 2
        node.y = -depth

# ---------------------------------------------------------------------------
# Draw the tree
# ---------------------------------------------------------------------------


def draw_tree(node, ax):
    """Recursively draw nodes and edges."""
    # Draw edges to children first (so nodes draw on top)
    for child in node.children:
        ax.plot([node.x, child.x], [node.y, child.y],
                color='#cccccc', linewidth=1.2, zorder=1)
        draw_tree(child, ax)

    # Draw node box
    box = mpatches.FancyBboxPatch(
        (node.x - 0.4, node.y - 0.25),
        width=0.8, height=0.45,
        boxstyle="round,pad=0.05",
        linewidth=1.2,
        edgecolor='white',
        facecolor=node.color,
        zorder=2,
        alpha=0.92
    )
    ax.add_patch(box)

    # Draw label
    ax.text(node.x, node.y, node.label,
            ha='center', va='center',
            fontsize=7, fontweight='bold',
            color='white', zorder=3)

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def visualize(ast):
    tree = ast_to_tree(ast)
    assign_positions(tree)

    fig, ax = plt.subplots(figsize=(22, 10))
    fig.patch.set_facecolor('#1e1e2e')
    ax.set_facecolor('#1e1e2e')

    draw_tree(tree, ax)

    # Axis cleanup
    ax.autoscale()
    ax.set_aspect('equal')
    ax.axis('off')

    # Title
    ax.set_title('MidiSynth — Abstract Syntax Tree',
                 color='white', fontsize=14, fontweight='bold', pad=15)

    # Legend
    legend_handles = [
        mpatches.Patch(color=NODE_COLORS['Program'],    label='Program root'),
        mpatches.Patch(color=NODE_COLORS['Tempo'],      label='TEMPO'),
        mpatches.Patch(color=NODE_COLORS['Instrument'], label='INSTRUMENT'),
        mpatches.Patch(color=NODE_COLORS['Play'],       label='PLAY'),
        mpatches.Patch(color=NODE_COLORS['Repeat'],     label='REPEAT'),
        mpatches.Patch(color=NODE_COLORS['Chord'],      label='CHORD'),
        mpatches.Patch(color=NODE_COLORS['Note'],       label='Note value'),
        mpatches.Patch(
            color=NODE_COLORS['Duration'],   label='Duration / literal'),
    ]
    ax.legend(handles=legend_handles,
              loc='upper right',
              fontsize=8,
              facecolor='#2e2e3e',
              labelcolor='white',
              edgecolor='#555555')

    plt.tight_layout()
    plt.savefig('ast_visualization.png', dpi=150, bbox_inches='tight',
                facecolor='#1e1e2e')
    print("AST saved as ast_visualization.png")
    plt.show()


if __name__ == '__main__':
    with open('input.msynth', 'r') as f:
        source = f.read()

    tokens = tokenize(source)
    ast = Parser(tokens).parse()
    visualize(ast)
