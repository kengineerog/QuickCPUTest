print("Importing necessary modules...")
from random import randint
import time
time.sleep(1)
print("Modules imported successfully.")
time.sleep(1)

runlevel = 0
toprunlevel = 100000000
print("Initialization complete.")
time.sleep(1)
print("Preparing to start generation...")
time.sleep(1)
print("Starting Generation Process...")
time.sleep(1)
print(f"Generating up to {toprunlevel} numbers.")
time.sleep(1)
print("This may take a while...")
time.sleep(1)
print("The shorter the time, the better it is!")
time.sleep(1)
print("Test starting in 3...")
time.sleep(1)
print("Test starting in 2...")
time.sleep(1)  
print("Test Starting in 1...")
time.sleep(1)
print("Starting Timer...")
start_time = time.perf_counter()

while runlevel < toprunlevel:
    runlevel += 5
    genrunnum = randint(-10101001010101001001, 10101001010100101010001)
    ogamarunnum = randint(-10101001010101001001, 10101001010100101010001)
    oshitarunnum = genrunnum * ogamarunnum
    if runlevel % 100000 == 0:
        print(f"Generated Number {runlevel}: {oshitarunnum}")

end_time = time.perf_counter()
elapsed = end_time - start_time
print(f"Finished. Total time: {elapsed:.4f} seconds")

