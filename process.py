# process.py

class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time  
        self.waiting_time = 0
        self.turnaround_time = 0

# İleride eklenecekler için iskelet
class Scheduler:
    def add_process(self, process):
        pass

    def run(self):
        pass