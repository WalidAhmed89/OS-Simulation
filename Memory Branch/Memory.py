class MemoryManager:
    def __init__(self, total_memory=256):
        self.total_memory = total_memory
        self.free_list = [(0, total_memory)] 
        self.allocated = {}  

    def allocate(self, pid, size):
        for i, (start, block_size) in enumerate(self.free_list):
            if block_size >= size:
                self.allocated[pid] = (start, size)
                if block_size == size:
                    del self.free_list[i]
                else:
                    self.free_list[i] = (start + size, block_size - size)
                return start
        return None

    def deallocate(self, pid):
        if pid not in self.allocated:
            return
        start, size = self.allocated.pop(pid)
        self.free_list.append((start, size))
        self.free_list.sort()
        merged = []
        for block in self.free_list:
            if not merged:
                merged.append(list(block))
            else:
                prev_start, prev_size = merged[-1]
                curr_start, curr_size = block
                if prev_start + prev_size == curr_start:
                    merged[-1][1] += curr_size
                else:
                    merged.append(list(block))
        self.free_list = [tuple(b) for b in merged]

    def get_free_memory(self):
        return sum(size for _, size in self.free_list)

    def draw_memory_map(self, canvas, width=400, height=100):
        canvas.delete("all")
        canvas.create_rectangle(0, 0, width, height, fill="#2b2b2b", outline="white")
        for pid, (start, size) in self.allocated.items():
            x1 = (start / self.total_memory) * width
            x2 = ((start + size) / self.total_memory) * width
            canvas.create_rectangle(x1, 0, x2, height, fill="#e74c3c", outline="white")
            if x2 - x1 > 20:
                canvas.create_text((x1 + x2) / 2, height / 2,
                                   text=f"P{pid}", fill="white", font=("Arial", 8))
        canvas.create_rectangle(0, 0, width, height, outline="white", width=2)