import time
from random import randint
import multiprocessing as mp
import threading
import psutil
import csv
import os
import statistics
import matplotlib.pyplot as plt

# ================= CONFIG =================
TOP_RUNLEVEL = 500_000_000
STEP = 5
MONITOR_INTERVAL = 1.0
BASE_DIR = "stress_runs"
# =========================================

# ============ FOLDER HANDLING ==============
def ensure_base_dirs():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "analysis"), exist_ok=True)

def create_run_folder():
    run_id = 1
    while True:
        path = os.path.join(BASE_DIR, f"run{run_id}")
        if not os.path.exists(path):
            os.makedirs(path)
            return path
        run_id += 1

ensure_base_dirs()
RUN_DIR = create_run_folder()
LOG_FILE = os.path.join(RUN_DIR, "cpu_stress_log.csv")

# ============ PI TEMP =====================
def read_pi_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000.0
    except:
        return None

# ============ LOGGER ======================
def init_log():
    with open(LOG_FILE, "w", newline="") as f:
        csv.writer(f).writerow([
            "time",
            "mode",
            "cpu_total",
            "avg_freq_mhz",
            "temperature_c",
            "power_w"
        ])

def log_row(row):
    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow(row)

# ============ SYSTEM MONITOR ===============
def system_monitor(stop_event, label):
    psutil.cpu_percent()
    psutil.cpu_freq()

    last_battery = psutil.sensors_battery()
    last_time = time.time()

    while not stop_event.is_set():
        now = time.time()

        cpu_total = psutil.cpu_percent(interval=None)
        freqs = psutil.cpu_freq()
        avg_freq = freqs.current if freqs else None

        # Battery-based power estimate
        battery = psutil.sensors_battery()
        power = None
        if battery and not battery.power_plugged and last_battery:
            dt = now - last_time
            dp = last_battery.percent - battery.percent
            if dt > 0 and dp > 0:
                power = (dp / 100.0) * 50 * (3600 / dt)

        last_battery = battery
        last_time = now

        temp = read_pi_temp()

        log_row([now, label, cpu_total, avg_freq, temp, power])

        print(
            f"[{label}] CPU {cpu_total:5.1f}% | "
            f"AVG {avg_freq if avg_freq else 'N/A'} MHz | "
            f"TEMP {temp if temp else 'N/A'} | "
            f"PWR {power if power else 'N/A'}"
        )

        time.sleep(MONITOR_INTERVAL)

# ================= WORKLOAD =================
def stress_loop(start, end):
    r = start
    while r < end:
        r += STEP
        _ = randint(-10**20, 10**20) * randint(-10**20, 10**20)

# ================= GRAPHING =================
def plot_run(log_file, out_dir):
    times, cpu, freq = [], [], []

    with open(log_file) as f:
        reader = csv.DictReader(f)
        t0 = None
        for row in reader:
            t = float(row["time"])
            if t0 is None:
                t0 = t
            times.append(t - t0)
            cpu.append(float(row["cpu_total"]))
            freq.append(float(row["avg_freq_mhz"]) if row["avg_freq_mhz"] else None)

    def save_plot(data, title, ylabel, name):
        if not any(v is not None for v in data):
            return
        plt.figure()
        plt.plot(times, data)
        plt.title(title)
        plt.xlabel("Time (s)")
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.savefig(os.path.join(out_dir, name))
        plt.close()

    save_plot(cpu, "CPU Usage", "CPU %", "cpu_usage.png")
    save_plot(freq, "Average Frequency", "MHz", "cpu_frequency.png")

# ============ MULTI-RUN ANALYSIS ===========
def analyze_runs():
    analysis_dir = os.path.join(BASE_DIR, "analysis")
    run_dirs = sorted(d for d in os.listdir(BASE_DIR) if d.startswith("run"))

    single_times = []
    multi_times = []

    for rd in run_dirs:
        summary = os.path.join(BASE_DIR, rd, "summary.txt")
        if not os.path.exists(summary):
            continue
        with open(summary) as f:
            lines = f.readlines()
            single_times.append(float(lines[0].split(":")[1]))
            multi_times.append(float(lines[1].split(":")[1]))

    if not single_times or not multi_times:
        return

    with open(os.path.join(analysis_dir, "summary.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "average", "median"])
        writer.writerow([
            "single_thread_time",
            statistics.mean(single_times),
            statistics.median(single_times)
        ])
        writer.writerow([
            "multi_thread_time",
            statistics.mean(multi_times),
            statistics.median(multi_times)
        ])
        writer.writerow([
            "speedup",
            statistics.mean(
                s / m for s, m in zip(single_times, multi_times)
            ),
            statistics.median(
                s / m for s, m in zip(single_times, multi_times)
            )
        ])

# ================= MAIN =================
if __name__ == "__main__":
    print(f"Run directory: {RUN_DIR}\n")
    init_log()

    # ---------- SINGLE ----------
    stop = threading.Event()
    mon = threading.Thread(target=system_monitor, args=(stop, "SINGLE"), daemon=True)
    mon.start()

    t0 = time.perf_counter()
    stress_loop(0, TOP_RUNLEVEL)
    single_time = time.perf_counter() - t0

    stop.set()
    mon.join()

    # ---------- MULTI ----------
    stop = threading.Event()
    mon = threading.Thread(target=system_monitor, args=(stop, "MULTI"), daemon=True)
    mon.start()

    t0 = time.perf_counter()
    cores = mp.cpu_count()
    chunk = TOP_RUNLEVEL // cores
    procs = []

    for i in range(cores):
        s = i * chunk
        e = TOP_RUNLEVEL if i == cores - 1 else (i + 1) * chunk
        p = mp.Process(target=stress_loop, args=(s, e))
        procs.append(p)
        p.start()

    for p in procs:
        p.join()

    multi_time = time.perf_counter() - t0
    stop.set()
    mon.join()

    # ---------- SAVE SUMMARY ----------
    with open(os.path.join(RUN_DIR, "summary.txt"), "w") as f:
        f.write(f"single_time:{single_time}\n")
        f.write(f"multi_time:{multi_time}\n")
        f.write(f"speedup:{single_time / multi_time}\n")

    plot_run(LOG_FILE, RUN_DIR)
    analyze_runs()

    print("\nRun complete.")
    print(f"Single-thread: {single_time:.2f}s")
    print(f"Multi-core  : {multi_time:.2f}s")
    print(f"Speedup     : {single_time / multi_time:.2f}x")
    print("Averages & median updated in stress_runs/analysis/")
