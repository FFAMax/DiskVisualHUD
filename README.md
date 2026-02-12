<img width="66" height="514" alt="Screenshot from 2026-02-11 19-48-15" src="https://github.com/user-attachments/assets/eb62c671-b806-4209-806b-4701d9224707" />
<img width="66" height="514" alt="Screenshot from 2026-02-11 19-49-15" src="https://github.com/user-attachments/assets/fe124c67-46a5-4669-9a29-24d935cda923" />
<img width="66" height="514" alt="Screenshot from 2026-02-11 19-52-39" src="https://github.com/user-attachments/assets/ec877822-8214-45e6-bd52-bb7cb3801330" />
<img width="66" height="514" alt="Screenshot from 2026-02-11 19-52-49" src="https://github.com/user-attachments/assets/58a18a84-3401-4710-ae4a-a182ab48b6ab" />
(the last one - writing to 2 raid members and md itself while reading from another disk)

# Real-Time Disk I/O Visualizer

This Python script is a **Real-Time Disk I/O Visualizer** built with `tkinter` and `psutil`. It provides a high-density, vertical dashboard to monitor read/write speeds, latency, and queue depths across multiple disks simultaneously.

It is designed for users who need a lightweight, always-on-top overlay to keep an eye on storage performance—especially useful for monitoring RAID arrays or multi-disk servers during heavy I/O tasks.

---

## 🚀 Features

* **Multi-Disk Support:** Monitors a specific list of drives (e.g., `sda`, `sdb`, `md0`) in a side-by-side comparative view.
* **Four-Tier Visualization:**
    * **Green:** Read throughput.
    * **Orange:** Write throughput.
    * **Yellow:** Disk Delay (Latency proxy).
    * **Cyan:** Queue Depth (Busy time proxy).
* **Minimalist HUD Mode:** * **Transparency:** Adjustable alpha blending (default 50%).
    * **Borderless:** Runs without standard window decorations for a clean look.
    * **Always-on-Top:** Stays visible above other applications.
    * **Draggable:** Even without a title bar, you can click and drag the canvas to reposition it.
* **Resource Efficient:** Uses in-place canvas object updates rather than redrawing the entire scene every second.

---

## 🛠 How It Works

1. **Data Polling:** The script uses a background thread to poll `psutil.disk_io_counters()` every second.
2. **Delta Calculation:** It calculates the difference between current and previous polling cycles to determine the "per second" throughput.
3. **Dynamic Scaling:** * Read/Write heights are scaled against a defined `MAX_MB_PER_SEC` (default 200MB/s).
    * Delay and Queue rows are auto-scaled based on the current maximum value across all monitored disks.
4. **UI Threading:** The data processing runs on a daemon thread to ensure the GUI remains responsive and the "drag-to-move" functionality stays smooth.

---

## 📋 Requirements

* **Python 3.x**
* **psutil:** `pip install psutil`
* **Tkinter:** Usually pre-installed with Python (on Linux, you may need `sudo apt-get install python3-tk`).

---

## ⚙️ Configuration

You can customize the behavior by editing the constants at the top of `main.py`:

```python
OVERLAY_MODE = True      # Toggle borderless/always-on-top
OVERLAY_ALPHA = 0.5      # Transparency level (0.0 to 1.0)
WIDTH = 10               # Width of the graph for each disk
MAX_MB_PER_SEC = 200     # Adjust based on your SSD/HDD speed
DISKS = ['sda', 'sdb']   # List the disks you want to monitor
