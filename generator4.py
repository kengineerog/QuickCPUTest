import time
import os
import multiprocessing as mp
import psutil
import csv
import statistics
import matplotlib.pyplot as plt

# ================= CONFIG =================
RUNS = 3
WARMUP_SECONDS = 15
GEN_COUNT = 200_000
COMPUTE_ROUNDS = 32
BASE_DIR = "cpu_hash_runs"
# =========================================

# ================= UTIL =================
def format_hps(h):
    for unit, scale in [("TH/s",1e12),("GH/s",1e9),("MH/s",1e6),("KH/s",1e3)]:
        if h >= scale:
            return f"{h/scale:.3f} {unit}"
    return f"{h:.3f} H/s"

def get_run_dir():
    os.makedirs(BASE_DIR, exist_ok=True)
    i = 1
    while True:
        p = os.path.join(BASE_DIR, f"run{i}")
        if not os.path.exists(p):
            os.makedirs(p)
            return p
        i += 1

# ================= HEAVY MATH =================
def heavy_math(x):
    for _ in range(COMPUTE_ROUNDS):
        x = (x * 6364136223846793005 + 1) & 0xFFFFFFFFFFFFFFFF
        x ^= (x >> 13)
        x = ((x << 7) | (x >> 57)) & 0xFFFFFFFFFFFFFFFF
    return x

# ================= GLOBAL WARMUP =================
def warmup_worker(stop_time):
    x = 123456789
    while time.perf_counter() < stop_time:
        x = heavy_math(x)

def global_warmup(seconds):
    print("Warming up...")
    end = time.perf_counter() + seconds
    procs = []
    for _ in range(mp.cpu_count()):
        p = mp.Process(target=warmup_worker, args=(end,))
        p.start()
        procs.append(p)
    for i in range(seconds, 0, -1):
        print(f"{i} sec left")
        time.sleep(1)
    for p in procs:
        p.join()
    print("Warm-up complete. CPU fully saturated.\n")

# ================= CORE TEST =================
def run_core(core_id, run_dir, log):
    p = psutil.Process()
    try:
        p.cpu_affinity([core_id])
    except:
        pass

    # ---- GENERATE ----
    t0 = time.perf_counter()
    nums = [(i * 6364136223846793005) & 0xFFFFFFFFFFFFFFFF for i in range(GEN_COUNT)]
    t_gen = time.perf_counter() - t0

    # ---- WRITE ----
    file_path = os.path.join(run_dir, f"core_{core_id}.txt")
    t0 = time.perf_counter()
    with open(file_path, "w") as f:
        for n in nums:
            f.write(f"{n}\n")
    t_write = time.perf_counter() - t0

    # ---- LOAD TO RAM ----
    t0 = time.perf_counter()
    with open(file_path) as f:
        data = [int(x) for x in f]
    t_load = time.perf_counter() - t0
    os.remove(file_path)

    # ---- COMPUTE ----
    t0 = time.perf_counter()
    count = 0
    for x in data:
        _ = heavy_math(x)
        count += 1
    t_comp = time.perf_counter() - t0

    hps = count / t_comp
    log.append((core_id, hps, t_gen, t_write, t_load, t_comp))
    return hps, t_gen + t_write + t_load + t_comp

# ================= MULTICORE =================
def multi_worker(data, counter):
    local = 0
    for x in data:
        _ = heavy_math(x)
        local += 1
    counter.value = local

def run_multicore(run_dir, log):
    nums = [(i * 6364136223846793005) & 0xFFFFFFFFFFFFFFFF for i in range(GEN_COUNT)]
    data = nums[:]

    counters, procs = [], []
    start = time.perf_counter()

    for _ in range(mp.cpu_count()):
        c = mp.Value("Q", 0)
        p = mp.Process(target=multi_worker, args=(data, c))
        p.start()
        counters.append(c)
        procs.append(p)

    for p in procs:
        p.join()

    elapsed = time.perf_counter() - start
    total = sum(c.value for c in counters)
    hps = total / elapsed
    log.append(("multicore", hps, elapsed))
    return hps, elapsed

# ================= MAIN =================
if __name__ == "__main__":
    mp.freeze_support()
    cpu_count = mp.cpu_count()
    run_dir = get_run_dir()
    print("\n🔥 EXTREME CPU PIPELINE BENCH 🔥")
    print(f"Cores: {cpu_count}")
    print(f"Run dir: {run_dir}\n")

    # 🔥 ONE GLOBAL WARM-UP 🔥
    global_warmup(WARMUP_SECONDS)

    results = {f"core_{i}": [] for i in range(cpu_count)}
    results["multicore"] = []
    log_data = []

    for r in range(1, RUNS + 1):
        print(f"\n=== RUN {r} ===\n")

        for c in range(cpu_count):
            print(f"Core {c}")
            h, t = run_core(c, run_dir, log_data)
            results[f"core_{c}"].append(h)
            print(f"  {format_hps(h)} | {t:.2f}s")

        h, t = run_multicore(run_dir, log_data)
        results["multicore"].append(h)
        print(f"\nMulticore: {format_hps(h)} | {t:.2f}s\n")

    # ---- LOG ----
    with open(os.path.join(run_dir, "logs.txt"), "w") as f:
        for row in log_data:
            f.write(str(row) + "\n")

    # ---- CSV ----
    with open(os.path.join(run_dir, "summary.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Target", "Mean H/s", "Median H/s"])
        for k, v in results.items():
            w.writerow([k, statistics.mean(v), statistics.median(v)])

    # ---- GRAPHS ----
    for k, v in results.items():
        plt.figure()
        plt.plot(range(1, RUNS + 1), v, marker="o")
        plt.axhline(statistics.mean(v), linestyle="--", label="Mean")
        plt.axhline(statistics.median(v), linestyle=":", label="Median")
        plt.title(f"{k} — Hashrate")
        plt.ylabel("Hashes/sec")
        plt.xlabel("Run")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(run_dir, f"{k}_hashrate.png"))
        plt.close()

    # ---- P-core vs E-core vs Multicore comparison ----
    try:
        pcores = [results[f"core_{i}"] for i in range(4)]
        ecores = [results[f"core_{i}"] for i in range(4, cpu_count)]
        plt.figure()
        for i, pc in enumerate(pcores):
            plt.plot(range(1,RUNS+1), pc, marker="o", label=f"P-Core {i}")
        for i, ec in enumerate(ecores):
            plt.plot(range(1,RUNS+1), ec, marker="x", label=f"E-Core {i}")
        plt.plot(range(1,RUNS+1), results["multicore"], marker="*", label="Multicore")
        plt.title("P-Cores vs E-Cores vs Multicore Hashrate")
        plt.xlabel("Run")
        plt.ylabel("Hashes/sec")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(run_dir, "cores_vs_multicore.png"))
        plt.close()
    except Exception as e:
        print(f"Graphing P/E cores skipped: {e}")

    print("\n✅ Benchmark complete.")
