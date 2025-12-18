PAGE_SIZE = 4096

class TLB:
    def __init__(self, size=4):
        self.size = size
        self.entries = []  # list of (page, frame)

    def lookup(self, page):
        for i, (p, f) in enumerate(self.entries):
            if p == page:
                # move to front (most recently used)
                self.entries.pop(i)
                self.entries.insert(0, (p, f))
                return f
        return None

    def insert(self, page, frame):
        # remove if already exists
        self.entries = [(p, f) for (p, f) in self.entries if p != page]

        # remove the least recently used entry (end of list)
        if len(self.entries) >= self.size:
            self.entries.pop()
        self.entries.insert(0, (page, frame))

    def clear(self):
        self.entries = []


class PageTable:
    def __init__(self):
        self.table = {}  # page: {frame, dirty}

    def add_mapping(self, page, frame):
        self.table[page] = {
            "frame": frame,
            "dirty": False
        }

    def lookup(self, page):
        return self.table.get(page, None)

    def set_dirty(self, page):
        if page in self.table:
            self.table[page]["dirty"] = True

    def clear(self):
        self.table = {}


class BaseAlgorithm:
    def hit(self, frames, page): 
        pass

    def miss(self, frames, page): 
        pass

    def empty_slot(self, frames):
        for i in range(len(frames)):
            if frames[i] is None:
                return i
        return -1

    def reset(self):
        pass


class FIFO(BaseAlgorithm):
    def __init__(self):
        self.ptr = 0

    def hit(self, frames, page):
        pass

    def miss(self, frames, page):
        i = self.empty_slot(frames)
        if i != -1:
            frames[i] = page
            return None, i  
        else:
            old_page = frames[self.ptr]
            old_idx = self.ptr
            frames[self.ptr] = page
            self.ptr = (self.ptr + 1) % len(frames)
            return old_page, old_idx  

    def reset(self):
        self.ptr = 0


class LRU(BaseAlgorithm):
    def __init__(self, num_frames):
        self.stack = []
        self.size = num_frames

    def hit(self, frames, page):
        if page in self.stack:
            self.stack.remove(page)
        self.stack.insert(0, page)

    def miss(self, frames, page):
        i = self.empty_slot(frames)

        if i != -1:
            frames[i] = page
            self.stack.insert(0, page)
            return None, i
        else:
            old_page = None
            for candidate in reversed(self.stack):
                if candidate in frames:
                    old_page = candidate
                    break
            
            if old_page is None:
                old_page = frames[0]
                self.stack = [p for p in frames if p is not None]
            
            if old_page in self.stack:
                self.stack.remove(old_page)
            
            old_idx = frames.index(old_page)
            
            frames[old_idx] = page
            self.stack.insert(0, page)
            return old_page, old_idx

    def reset(self):
        self.stack = []


class Optimal(BaseAlgorithm):
    def __init__(self, trace):
        self.reference_string = [t[1] for t in trace]
        self.current_step = 0

    def hit(self, frames, page):
        self.current_step += 1

    def miss(self, frames, page):
        victim_idx = -1
        farthest_distance = -1
        
        empty = self.empty_slot(frames)
        if empty != -1:
            frames[empty] = page
            self.current_step += 1
            return None, empty

        for i, frame_page in enumerate(frames):
            try:
                next_use = self.reference_string.index(frame_page, self.current_step + 1)
                distance = next_use - self.current_step
            except ValueError:
                distance = float('inf')
            
            if distance > farthest_distance:
                farthest_distance = distance
                victim_idx = i
                
                if distance == float('inf'):
                    break
        
        old_page = frames[victim_idx]
        frames[victim_idx] = page
        self.current_step += 1
        return old_page, victim_idx

    def reset(self):
        self.current_step = 0

class VirtualMemory:
    def __init__(self, num_frames, algorithm, tlb_size=4):
        self.num_frames = num_frames
        self.frames = [None] * num_frames
        self.algorithm = algorithm

        self.tlb = TLB(tlb_size)
        self.page_table = PageTable()

        self.tlb_hits = 0
        self.tlb_misses = 0
        self.page_faults = 0
        self.hits = 0

    def access(self, page, mode="R"):
    
        frame = self.tlb.lookup(page)
        is_tlb_hit = False
        old_page = None
        frame_idx = -1
        status = ""

        if frame is not None:
            self.tlb_hits += 1
            self.hits += 1
            is_tlb_hit = True
            self.algorithm.hit(self.frames, page)
            frame_idx = frame
            status = "HIT (TLB)"
        else:
            self.tlb_misses += 1
            entry = self.page_table.lookup(page)

            if entry is not None:
                frame = entry["frame"]
                self.hits += 1
                self.algorithm.hit(self.frames, page)
                frame_idx = frame
                status = "HIT (Page Table)"
            else:
                self.page_faults += 1
                old_page, frame_idx = self.algorithm.miss(self.frames, page)
                
                self.page_table.add_mapping(page, frame_idx)

                if old_page is not None:
                    old_entry = self.page_table.lookup(old_page)
                    if old_entry and old_entry["dirty"]:
                        pass 
                    self.page_table.table.pop(old_page, None)
                    status = "FAULT (MISS)"
                else:
                    status = "FAULT (MISS)"

            self.tlb.insert(page, frame_idx)

        if mode == "W":
            self.page_table.set_dirty(page)

        return status, old_page, frame_idx, is_tlb_hit

    def reset(self):
        self.frames = [None] * self.num_frames
        self.tlb.clear()
        self.page_table.clear()
        self.algorithm.reset()
        self.tlb_hits = 0
        self.tlb_misses = 0
        self.page_faults = 0
        self.hits = 0


def read_trace_file(filename):
    trace = []
    try:
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    op, addr = parts[0], parts[1]
                    try:
                        addr = int(addr)
                        page = addr // PAGE_SIZE
                        trace.append((op.upper(), page))
                    except ValueError:
                        continue
                elif len(parts) == 1:
                    try:
                        page = int(parts[0])
                        trace.append(("R", page))
                    except ValueError:
                        continue
    except FileNotFoundError:
        return []
    return trace