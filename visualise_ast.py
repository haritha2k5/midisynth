# visualize_ast.py - MidiSynth AST Visualizer
# Draws the Abstract Syntax Tree using matplotlib

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from lexer import tokenize
from parser import (Parser, ProgramNode, TempoNode, InstrumentNode,
                    PlayNode, RepeatNode, ChordNode)

# ---------------------------------------------------------------------------
# Color scheme
# ---------------------------------------------------------------------------
NODE_COLORS = {
    'Program':    '#4A90D9',
    'Tempo':      '#7B68EE',
    'Instrument': '#20B2AA',
    'Play':       '#3CB371',
    'Repeat':     '#FF8C00',
    'Chord':      '#DC143C',
    'Note':       '#57A65A',
    'Duration':   '#C8A200',
    'Literal':    '#888888',
}

# ---------------------------------------------------------------------------
# Internal tree node for layout
# ---------------------------------------------------------------------------


class TreeNode:
    def __init__(self, label, color, children=None):
        self.label = label
        self.color = color
        self.children = children or []
        self.x = 0.0
        self.y = 0.0
        self.width = 0.0

# ---------------------------------------------------------------------------
# Convert AST to TreeNode
# ---------------------------------------------------------------------------


def ast_to_tree(node):
    if isinstance(node, ProgramNode):
        children = [ast_to_tree(s) for s in node.statements]
        return TreeNode('Program', NODE_COLORS['Program'], children)
    elif isinstance(node, TempoNode):
        return TreeNode('TEMPO', NODE_COLORS['Tempo'],
                        [TreeNode(str(node.bpm), NODE_COLORS['Literal'])])
    elif isinstance(node, InstrumentNode):
        return TreeNode('INSTRUMENT', NODE_COLORS['Instrument'],
                        [TreeNode(node.name, NODE_COLORS['Literal'])])
    elif isinstance(node, PlayNode):
        return TreeNode('PLAY', NODE_COLORS['Play'], [
            TreeNode(node.note,     NODE_COLORS['Note']),
            TreeNode(node.duration, NODE_COLORS['Duration']),
        ])
    elif isinstance(node, RepeatNode):
        count_node = TreeNode(f'x{node.count}', NODE_COLORS['Literal'])
        body_nodes = [ast_to_tree(s) for s in node.body]
        return TreeNode('REPEAT', NODE_COLORS['Repeat'], [count_node] + body_nodes)
    elif isinstance(node, ChordNode):
        note_nodes = [TreeNode(n, NODE_COLORS['Note']) for n in node.notes]
        dur_node = TreeNode(node.duration, NODE_COLORS['Duration'])
        return TreeNode('CHORD', NODE_COLORS['Chord'], note_nodes + [dur_node])
    return TreeNode('?', '#aaaaaa')


# ---------------------------------------------------------------------------
# Layout: Reingold-Tilford inspired - compute subtree widths first
# ---------------------------------------------------------------------------
LEAF_SEP = 1.2   # horizontal gap between leaves
LEVEL_SEP = 1.6   # vertical gap between levels


def compute_width(node):
    if not node.children:
        node.width = LEAF_SEP
    else:
        for c in node.children:
            compute_width(c)
        node.width = sum(c.width for c in node.children)


def assign_positions(node, x_offset=0, depth=0):
    node.y = -depth * LEVEL_SEP
    if not node.children:
        node.x = x_offset + node.width / 2
    else:
        cursor = x_offset
        for child in node.children:
            assign_positions(child, cursor, depth + 1)
            cursor += child.width
        node.x = (node.children[0].x + node.children[-1].x) / 2

# ---------------------------------------------------------------------------
# Draw
# ---------------------------------------------------------------------------


def draw_tree(node, ax):
    for child in node.children:
        ax.annotate('', xy=(child.x, child.y + 0.22),
                    xytext=(node.x, node.y - 0.22),
                    arrowprops=dict(arrowstyle='->', color='#555577',
                                    lw=1.0, connectionstyle='arc3,rad=0.0'),
                    zorder=1)
        draw_tree(child, ax)

    # Node box
    box_w, box_h = 0.95, 0.42
    box = mpatches.FancyBboxPatch(
        (node.x - box_w / 2, node.y - box_h / 2),
        width=box_w, height=box_h,
        boxstyle='round,pad=0.06',
        linewidth=1.0,
        edgecolor='#ffffff33',
        facecolor=node.color,
        zorder=2,
        alpha=0.95,
    )
    ax.add_patch(box)

    # Truncate long labels
    label = node.label if len(node.label) <= 8 else node.label[:7] + '.'
    ax.text(node.x, node.y, label,
            ha='center', va='center',
            fontsize=6.5, fontweight='bold',
            color='white', zorder=3)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def visualize(ast):
    tree = ast_to_tree(ast)
    compute_width(tree)
    assign_positions(tree)

    # Canvas size based on tree width
    tree_w = tree.width
    tree_h = 4 * LEVEL_SEP + 1

    fig_w = max(24, tree_w * 0.55)
    fig_h = max(6,  tree_h * 1.1)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    draw_tree(tree, ax)

    ax.autoscale()
    ax.set_aspect('equal')
    ax.axis('off')
    ax.margins(0.02)

    ax.set_title('MidiSynth — Abstract Syntax Tree (Happy Birthday)',
                 color='white', fontsize=13, fontweight='bold', pad=12)

    legend_handles = [
        mpatches.Patch(color=NODE_COLORS['Program'],    label='Program root'),
        mpatches.Patch(color=NODE_COLORS['Tempo'],      label='TEMPO'),
        mpatches.Patch(color=NODE_COLORS['Instrument'], label='INSTRUMENT'),
        mpatches.Patch(color=NODE_COLORS['Play'],       label='PLAY'),
        mpatches.Patch(color=NODE_COLORS['Repeat'],     label='REPEAT'),
        mpatches.Patch(color=NODE_COLORS['Chord'],      label='CHORD'),
        mpatches.Patch(color=NODE_COLORS['Note'],       label='Note value'),
        mpatches.Patch(color=NODE_COLORS['Duration'],   label='Duration'),
        mpatches.Patch(color=NODE_COLORS['Literal'],    label='Literal'),
    ]
    ax.legend(handles=legend_handles, loc='upper right',
              fontsize=8, facecolor='#2e2e4e',
              labelcolor='white', edgecolor='#444466')

    plt.tight_layout()
    plt.savefig('ast_visualization.png', dpi=150,
                bbox_inches='tight', facecolor='#1a1a2e')
    print("AST saved as ast_visualization.png")
    plt.show()


if __name__ == '__main__':
    with open('input.msynth', 'r') as f:
        source = f.read()

    tokens = tokenize(source)
    ast = Parser(tokens).parse()
    visualize(ast)
