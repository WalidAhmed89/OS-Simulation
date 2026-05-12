# process_api.py — Shared Process & Memory State
import json
import os
from ui.Memory import MemoryManager


JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processes.json")

# ── Memory manager
memory_manager = MemoryManager(total_memory=512)


# ── Process Class
class Process:
    def __init__(self, pid, name, burst_time, memory_size=32):
        self.pid = pid
        self.name = name
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.memory_size = memory_size
        self.state = "Ready"

    def to_dict(self):
        return {
            "pid": self.pid,
            "name": self.name,
            "burst_time": self.burst_time,
            "remaining_time": self.remaining_time,
            "memory_size": self.memory_size,
            "state": self.state,
        }

    @staticmethod
    def from_dict(d):
        p = Process(d["pid"], d["name"], d["burst_time"], d["memory_size"])
        p.remaining_time = d["remaining_time"]
        p.state = d["state"]
        return p


#  JSON helpers

def _load():
    if not os.path.exists(JSON_FILE):
        return [], 1
    try:
        with open(JSON_FILE, "r") as f:
            data = json.load(f)
        procs = [Process.from_dict(d) for d in data.get("processes", [])]
        counter = data.get("pid_counter", 1)
        return procs, counter
    except:
        return [], 1


def _save(process_list, pid_counter):
    data = {
        "pid_counter": pid_counter,
        "processes": [p.to_dict() for p in process_list]
    }
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=2)



def update_state(pid, new_state):
    process_list, pid_counter = _load()
    for p in process_list:
        if p.pid == pid:
            p.state = new_state
            _save(process_list, pid_counter)
            return


#  Public API
def spawn_process(name, burst_time=4, memory_size=32):
    process_list, pid_counter = _load()
    p = Process(pid_counter, name, burst_time, memory_size)
    address = memory_manager.allocate(p.pid, p.memory_size)
    if address is None:
        print(f"[process_api] No memory for '{name}'")
        return None
    process_list.append(p)
    _save(process_list, pid_counter + 1)
    return p


def finish_process(pid):
    process_list, pid_counter = _load()
    for p in process_list:
        if p.pid == pid:
            p.state = "Finished"
            p.remaining_time = 0
            memory_manager.deallocate(pid)
            _save(process_list, pid_counter)
            return p
    return None


def kill_process(pid):
    process_list, pid_counter = _load()
    memory_manager.deallocate(pid)
    process_list = [p for p in process_list if p.pid != pid]
    _save(process_list, pid_counter)


def clear_all():
    process_list, _ = _load()
    for p in process_list:
        memory_manager.deallocate(p.pid)
    _save([], 1)


def get_all():
    process_list, _ = _load()
    return process_list

def update_process(pid, state=None, remaining_time=None):
    process_list, pid_counter = _load()

    for p in process_list:
        if p.pid == pid:
            if state is not None:
                p.state = state
            if remaining_time is not None:
                p.remaining_time = remaining_time

            _save(process_list, pid_counter)
            return p
