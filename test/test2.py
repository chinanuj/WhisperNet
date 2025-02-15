import threading
import time

def worker():
    print(f"Thread {threading.current_thread().name} starting")
    time.sleep(2)  # Simulate some work
    print(f"Thread {threading.current_thread().name} finished")

# Create two threads
threads = []
for i in range(2):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

print("All threads completed!")