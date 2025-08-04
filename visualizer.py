import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Color map for monad states
STATE_COLORS = {
    'solid': 'blue',
    'liquid': 'cyan',
    'glow': 'yellow',
    'gas': 'orange',
    'goal': 'green',
    None: 'white'
}

def render_grid(grid, tick=0):
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    data = np.zeros((height, width, 3))

    for y in range(height):
        for x in range(width):
            monad = grid[y][x]
            color_name = STATE_COLORS.get(monad.state if monad else None, 'grey')
            try:
                rgb = plt.colors.to_rgb(color_name)
            except:
                rgb = (0.5, 0.5, 0.5)
            data[y, x] = rgb

    plt.imshow(data, interpolation='nearest')
    plt.title(f"Monad Playground - Tick {tick}")
    plt.axis('off')

    # Add legend
    legend_elements = [mpatches.Patch(color=c, label=s if s else "None")
                       for s, c in STATE_COLORS.items()]
    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # Click inspection
    def on_click(event):
        if event.inaxes:
            col = int(event.xdata + 0.5)
            row = int(event.ydata + 0.5)
            if 0 <= row < height and 0 <= col < width:
                monad = grid[row][col]
                if monad:
                    print(f"Clicked monad at ({col}, {row}):")
                    print(f"  state   = {monad.state}")
                    print(f"  memory  = {monad.memory}")
                    print(f"  trace   = {monad.trace_log if hasattr(monad, 'trace_log') else 'N/A'}")

    plt.gcf().canvas.mpl_connect('button_press_event', on_click)
    plt.show()


def run_simulation(sim, steps=10, delay=0.5):
    import time
    for i in range(steps):
        sim.step()
        render_grid(sim.grid, sim.tick_count)
        time.sleep(delay)
