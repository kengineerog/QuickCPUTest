# QuickCPUTest

run "pip install psutil matplotlib" to install the packages matplotlib and psutil. You can just do git clone to clone this whole thing! Also, V2 is the best so far, I put V1 in there just so you guys can see how it used to be before I really locked in and got to work.

I wanted to do a really quick CPU test, using CLI, so I decided to do just that! I made my own little python tester, and you have to run "pip install psutil matplotlib" in the terminal before running this scrip, it makes it's own folders, look, it'll be there somewhere!


This is a sample output from my dell inspirion 15 3520, with an 12th gen Intel Core i5-1235U, with 2 P cores and 8 E cores. There seems to be two "Ghost" CPU cores, Core 0 and 11, but there are 2 extra cores, V cores, so yes this completly works! This is a demo benchmark output:
🔥 EXTREME CPU PIPELINE BENCH 🔥
Cores: 12
Run dir: cpu_hash_runs\run4

Warming up...
15 sec left
14 sec left
13 sec left
12 sec left
11 sec left
10 sec left
9 sec left
8 sec left
7 sec left
6 sec left
5 sec left
4 sec left
3 sec left
2 sec left
1 sec left
Warm-up complete. CPU fully saturated.


=== RUN 1 ===

Core 0
  87.896 KH/s | 2.65s
Core 1
  87.309 KH/s | 2.53s
Core 2
  97.980 KH/s | 2.26s
Core 3
  105.859 KH/s | 2.07s
Core 4
  60.843 KH/s | 3.58s
Core 5
  60.242 KH/s | 3.66s
Core 6
  58.042 KH/s | 3.76s
Core 7
  58.774 KH/s | 3.70s
Core 8
  56.588 KH/s | 3.84s
Core 9
  58.178 KH/s | 3.73s
Core 10
  57.598 KH/s | 3.77s
Core 11
  60.309 KH/s | 3.64s

Multicore: 45.246 KH/s | 53.04s


=== RUN 2 ===

Core 0
  121.334 KH/s | 1.83s
Core 1
  120.890 KH/s | 1.85s
Core 2
  118.909 KH/s | 1.86s
Core 3
  113.442 KH/s | 1.95s
Core 4
  62.815 KH/s | 3.47s
Core 5
  62.992 KH/s | 3.48s
Core 6
  61.679 KH/s | 3.54s
Core 7
  60.351 KH/s | 3.63s
Core 8
  61.715 KH/s | 3.56s
Core 9
  58.476 KH/s | 3.70s
Core 10
  59.791 KH/s | 3.65s
Core 11
  61.561 KH/s | 3.54s

Multicore: 46.817 KH/s | 51.26s


=== RUN 3 ===

Core 0
  59.989 KH/s | 3.75s
Core 1
  107.494 KH/s | 2.09s
Core 2
  116.950 KH/s | 1.88s
Core 3
  102.354 KH/s | 2.13s
Core 4
  62.160 KH/s | 3.49s
Core 5
  61.892 KH/s | 3.56s
Core 6
  60.766 KH/s | 3.59s
Core 7
  62.092 KH/s | 3.54s
Core 8
  61.033 KH/s | 3.56s
Core 9
  61.618 KH/s | 3.53s
Core 10
  63.301 KH/s | 3.46s
Core 11
  62.290 KH/s | 3.50s

Multicore: 45.212 KH/s | 53.08s


✅ Benchmark complete.
