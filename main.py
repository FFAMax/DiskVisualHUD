import tkinter as tk
import psutil
import time
import threading

# Overlay/Transparency settings
OVERLAY_MODE = True
OVERLAY_ALPHA = 0.5  # 50% transparency
SHOW_LABELS = False

WIDTH = 10
HEIGHT = 200
EXTRA_ROW_HEIGHT = 10
MAX_MB_PER_SEC = 200
BYTES_PER_PIXEL = (MAX_MB_PER_SEC * 1024 * 1024) / HEIGHT

DISKS = ['sda', 'sdb', 'sdc', 'sde', 'sdd', 'md0', 'md1']

data_read = {disk: [0] * WIDTH for disk in DISKS}
data_write = {disk: [0] * WIDTH for disk in DISKS}
data_delay = {disk: [0] * WIDTH for disk in DISKS}
data_queue = {disk: [0] * WIDTH for disk in DISKS}

def update_data():
    prev_stats = {}
    for disk in DISKS:
        prev = psutil.disk_io_counters(perdisk=True).get(disk)
        if prev is None:
            print(f"Disk {disk} not found.")
            prev_stats[disk] = None
        else:
            prev_stats[disk] = prev

    while True:
        time.sleep(1)
        curr_stats = psutil.disk_io_counters(perdisk=True)
        for disk in DISKS:
            prev = prev_stats.get(disk)
            curr = curr_stats.get(disk)
            if not prev or not curr:
                continue
            read_bytes = curr.read_bytes - prev.read_bytes
            write_bytes = curr.write_bytes - prev.write_bytes
            prev_stats[disk] = curr

            data_read[disk].pop(0)
            data_read[disk].append(read_bytes)
            data_write[disk].pop(0)
            data_write[disk].append(write_bytes)

            # Delay (ms): use weighted average if available, else 0
            delay = getattr(curr, 'read_time', 0) + getattr(curr, 'write_time', 0)
            delay_prev = getattr(prev, 'read_time', 0) + getattr(prev, 'write_time', 0)
            delay_val = max(0, delay - delay_prev)
            data_delay[disk].pop(0)
            data_delay[disk].append(delay_val)

            # Queue length: use 'busy_time' delta as a proxy if queue_length not available
            queue_val = getattr(curr, 'busy_time', 0) - getattr(prev, 'busy_time', 0)
            data_queue[disk].pop(0)
            data_queue[disk].append(max(0, queue_val))
        draw()

def draw():
    # Instead of deleting all, update lines in-place
    # We'll keep a cache of line ids for each disk and operation
    if not hasattr(draw, "line_ids"):
        draw.line_ids = {
            "read": {disk: [None]*WIDTH for disk in DISKS},
            "write": {disk: [None]*WIDTH for disk in DISKS},
            "delay": {disk: [None]*WIDTH for disk in DISKS},
            "queue": {disk: [None]*WIDTH for disk in DISKS},
            "vsep": [],
            "hsep": [],
            "labels": []
        }
        # Vertical separators
        for idx in range(1, len(DISKS)):
            x = idx * WIDTH
            line_id = canvas.create_line(x, 0, x, 2 * HEIGHT + 2 * EXTRA_ROW_HEIGHT + 20, fill='#222', width=1)
            draw.line_ids["vsep"].append(line_id)
        # Horizontal separators
        draw.line_ids["hsep"].append(canvas.create_line(0, HEIGHT, WIDTH * len(DISKS), HEIGHT, fill='#222', width=1))
        draw.line_ids["hsep"].append(canvas.create_line(0, 2 * HEIGHT, WIDTH * len(DISKS), 2 * HEIGHT, fill='#222', width=1))
        draw.line_ids["hsep"].append(canvas.create_line(0, 2 * HEIGHT + EXTRA_ROW_HEIGHT, WIDTH * len(DISKS), 2 * HEIGHT + EXTRA_ROW_HEIGHT, fill='#222', width=1))
        draw.line_ids["hsep"].append(canvas.create_line(0, 2 * HEIGHT + 2 * EXTRA_ROW_HEIGHT, WIDTH * len(DISKS), 2 * HEIGHT + 2 * EXTRA_ROW_HEIGHT, fill='#222', width=1))
        for idx, disk in enumerate(DISKS):
            x_offset = idx * WIDTH
            if SHOW_LABELS: label_id = canvas.create_text(x_offset + WIDTH // 2, 2 * HEIGHT + 2 * EXTRA_ROW_HEIGHT + 10, text=f"{disk}", fill='white', font=('Arial', 9))
            if SHOW_LABELS: draw.line_ids["labels"].append(label_id)

    # Update read graphs (top row)
    for idx, disk in enumerate(DISKS):
        x_offset = idx * WIDTH
        for i, value in enumerate(data_read[disk]):
            height = int(min(value / BYTES_PER_PIXEL, HEIGHT))
            y = HEIGHT - height
            line_id = draw.line_ids["read"][disk][i]
            if line_id is not None:
                canvas.coords(line_id, x_offset + i, HEIGHT, x_offset + i, y)
            else:
                draw.line_ids["read"][disk][i] = canvas.create_line(x_offset + i, HEIGHT, x_offset + i, y, fill='green')
    # Update write graphs (second row)
    for idx, disk in enumerate(DISKS):
        x_offset = idx * WIDTH
        for i, value in enumerate(data_write[disk]):
            height = int(min(value / BYTES_PER_PIXEL, HEIGHT))
            y = 2 * HEIGHT - height
            line_id = draw.line_ids["write"][disk][i]
            if line_id is not None:
                canvas.coords(line_id, x_offset + i, 2 * HEIGHT, x_offset + i, y)
            else:
                draw.line_ids["write"][disk][i] = canvas.create_line(x_offset + i, 2 * HEIGHT, x_offset + i, y, fill='orange')
    # Update delay graphs (third row, thin)
    max_delay = max([max(data_delay[disk]) for disk in DISKS] + [1])
    for idx, disk in enumerate(DISKS):
        x_offset = idx * WIDTH
        for i, value in enumerate(data_delay[disk]):
            height = int(min(value / max_delay * EXTRA_ROW_HEIGHT, EXTRA_ROW_HEIGHT))
            y = 2 * HEIGHT + EXTRA_ROW_HEIGHT - height
            line_id = draw.line_ids["delay"][disk][i]
            if line_id is not None:
                canvas.coords(line_id, x_offset + i, 2 * HEIGHT + EXTRA_ROW_HEIGHT, x_offset + i, y)
            else:
                draw.line_ids["delay"][disk][i] = canvas.create_line(x_offset + i, 2 * HEIGHT + EXTRA_ROW_HEIGHT, x_offset + i, y, fill='yellow')
    # Update queue graphs (fourth row, thin)
    max_queue = max([max(data_queue[disk]) for disk in DISKS] + [1])
    for idx, disk in enumerate(DISKS):
        x_offset = idx * WIDTH
        for i, value in enumerate(data_queue[disk]):
            height = int(min(value / max_queue * EXTRA_ROW_HEIGHT, EXTRA_ROW_HEIGHT))
            y = 2 * HEIGHT + 2 * EXTRA_ROW_HEIGHT - height
            line_id = draw.line_ids["queue"][disk][i]
            if line_id is not None:
                canvas.coords(line_id, x_offset + i, 2 * HEIGHT + 2 * EXTRA_ROW_HEIGHT, x_offset + i, y)
            else:
                draw.line_ids["queue"][disk][i] = canvas.create_line(x_offset + i, 2 * HEIGHT + 2 * EXTRA_ROW_HEIGHT, x_offset + i, y, fill='#0cf')

def run_gui():
    global canvas
    root = tk.Tk()
    root.title("Disk Read/Write Monitor (sda, sdb, sdc, sde, md0, md1)")
    root.resizable(False, False)
    canvas = tk.Canvas(root, width=WIDTH * len(DISKS), height=HEIGHT * 2 + EXTRA_ROW_HEIGHT * 2 + 20, bg='black', highlightthickness=0)
    canvas.pack()

    if OVERLAY_MODE:
        # Set window transparency (works on Windows and most Linux, not macOS)
        try:
            root.wm_attributes('-alpha', OVERLAY_ALPHA)
        except Exception:
            try:
                root.attributes('-alpha', OVERLAY_ALPHA)
            except Exception:
                pass
        # Always on top
        try:
            root.wm_attributes('-topmost', True)
        except Exception:
            try:
                root.attributes('-topmost', True)
            except Exception:
                pass
        # Remove window decorations (borderless)
        try:
            root.overrideredirect(True)
        except Exception:
            pass

        # Allow dragging the window with mouse
        def start_move(event):
            root._drag_start_x = event.x
            root._drag_start_y = event.y

        def do_move(event):
            x = root.winfo_x() + event.x - root._drag_start_x
            y = root.winfo_y() + event.y - root._drag_start_y
            root.geometry(f"+{x}+{y}")

        canvas.bind("<ButtonPress-1>", start_move)
        canvas.bind("<B1-Motion>", do_move)

    threading.Thread(target=update_data, daemon=True).start()
    root.mainloop()

run_gui()

