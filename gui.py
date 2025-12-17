import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from classes import VirtualMemory, FIFO, LRU, read_trace_file

class VirtualMemorySimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("✦ Virtual Memory Paging Simulator ✦")
        self.root.geometry("1350x800")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)
        
        # Variables
        self.num_frames = tk.IntVar(value=3)
        self.algorithm_var = tk.StringVar(value="FIFO")
        self.speed_var = tk.DoubleVar(value=0.5)
        self.trace_file = tk.StringVar(value="")
        
        # Simulation state
        self.vm = None
        self.trace = []
        self.current_step = 0
        self.is_running = False
        self.simulation_thread = None
        
        # Create GUI
        self.create_gui()
        
    def create_gui(self):
        # Main title
        title_frame = tk.Frame(self.root, bg="#1a1a2e")
        title_frame.pack(pady=15)
        
        title_label = tk.Label(
            title_frame,
            text=" Virtual Memory Paging Simulator",
            font=("Arial", 24, "bold"),
            fg="#87CEEB",
            bg="#1a1a2e"
        )
        title_label.pack()
        
        # Main container
        main_container = tk.Frame(self.root, bg="#1a1a2e")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Configuration
        self.create_config_panel(main_container)
        
        # Middle panel - Memory Frames & Simulation Report
        self.create_middle_panel(main_container)
        
        # Right panel - Performance Chart
        self.create_performance_panel(main_container)
        
        # Bottom panel - Algorithm Trace Log
        self.create_trace_log_panel()
        
    def create_config_panel(self, parent):
        config_frame = tk.Frame(parent, bg="#2d2d44", relief=tk.RAISED, bd=2)
        config_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Header
        header = tk.Label(
            config_frame,
            text="⚙️ Configuration Panel",
            font=("Arial", 14, "bold"),
            fg="#87CEEB",
            bg="#2d2d44"
        )
        header.pack(pady=15, padx=20)
        
        # Total Memory Frames
        frames_label = tk.Label(
            config_frame,
            text="Total Memory Frames",
            font=("Arial", 10),
            fg="#CCCCCC",
            bg="#2d2d44"
        )
        frames_label.pack(anchor=tk.W, padx=20, pady=(10, 2))
        
        frames_entry = tk.Entry(
            config_frame,
            textvariable=self.num_frames,
            font=("Arial", 12),
            bg="#1a1a2e",
            fg="white",
            insertbackground="white",
            width=25
        )
        frames_entry.pack(padx=20, pady=5)
        
        # Trace File Selection
        file_label = tk.Label(
            config_frame,
            text="Trace File",
            font=("Arial", 10),
            fg="#CCCCCC",
            bg="#2d2d44"
        )
        file_label.pack(anchor=tk.W, padx=20, pady=(15, 2))
        
        file_frame = tk.Frame(config_frame, bg="#2d2d44")
        file_frame.pack(padx=20, pady=5, fill=tk.X)
        
        self.file_entry = tk.Entry(
            file_frame,
            textvariable=self.trace_file,
            font=("Arial", 10),
            bg="#1a1a2e",
            fg="white",
            insertbackground="white",
            width=18
        )
        self.file_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        browse_btn = tk.Button(
            file_frame,
            text="📁",
            font=("Arial", 10),
            bg="#4a4a6a",
            fg="white",
            command=self.browse_file
        )
        browse_btn.pack(side=tk.LEFT)
        
        # Page Reference String Display (from file)
        ref_label = tk.Label(
            config_frame,
            text="Page Reference String (from file)",
            font=("Arial", 10),
            fg="#CCCCCC",
            bg="#2d2d44"
        )
        ref_label.pack(anchor=tk.W, padx=20, pady=(15, 2))
        
        self.ref_string_label = tk.Label(
            config_frame,
            text="No file loaded",
            font=("Arial", 10),
            fg="#888888",
            bg="#1a1a2e",
            width=30,
            wraplength=250,
            justify=tk.LEFT
        )
        self.ref_string_label.pack(padx=20, pady=5)
        
        # Paging Algorithm
        algo_label = tk.Label(
            config_frame,
            text="Paging Algorithm",
            font=("Arial", 10),
            fg="#CCCCCC",
            bg="#2d2d44"
        )
        algo_label.pack(anchor=tk.W, padx=20, pady=(15, 2))
        
        algo_combo = ttk.Combobox(
            config_frame,
            textvariable=self.algorithm_var,
            values=["FIFO", "LRU"],
            font=("Arial", 12),
            width=23,
            state="readonly"
        )
        algo_combo.pack(padx=20, pady=5)
        
        # Simulation Speed
        speed_label = tk.Label(
            config_frame,
            text="Simulation Speed (Delay in seconds)",
            font=("Arial", 10),
            fg="#CCCCCC",
            bg="#2d2d44"
        )
        speed_label.pack(anchor=tk.W, padx=20, pady=(15, 2))
        
        speed_scale = tk.Scale(
            config_frame,
            from_=0.1,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            bg="#2d2d44",
            fg="white",
            highlightthickness=0,
            troughcolor="#1a1a2e",
            length=200
        )
        speed_scale.pack(padx=20, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(config_frame, bg="#2d2d44")
        btn_frame.pack(pady=20, padx=20, fill=tk.X)
        
        self.run_btn = tk.Button(
            btn_frame,
            text="▶ RUN SIMULATION",
            font=("Arial", 12, "bold"),
            bg="#87CEEB",
            fg="#1a1a2e",
            activebackground="#a8d8ea",
            command=self.run_simulation,
            width=20,
            height=2
        )
        self.run_btn.pack(pady=5)
        
        self.stop_btn = tk.Button(
            btn_frame,
            text="⏹ STOP",
            font=("Arial", 12, "bold"),
            bg="#ff6b6b",
            fg="white",
            activebackground="#ff8787",
            command=self.stop_simulation,
            width=20,
            height=2,
            state=tk.DISABLED
        )
        self.stop_btn.pack(pady=5)
        
        self.reset_btn = tk.Button(
            btn_frame,
            text="🔄 RESET",
            font=("Arial", 12, "bold"),
            bg="#4a4a6a",
            fg="white",
            activebackground="#6a6a8a",
            command=self.reset_simulation,
            width=20,
            height=2
        )
        self.reset_btn.pack(pady=5)

    def create_middle_panel(self, parent):
        middle_frame = tk.Frame(parent, bg="#1a1a2e")
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Main Memory Frames
        frames_panel = tk.Frame(middle_frame, bg="#2d2d44", relief=tk.RAISED, bd=2)
        frames_panel.pack(fill=tk.X, pady=5)
        
        frames_header = tk.Label(
            frames_panel,
            text="Main Memory Frames",
            font=("Arial", 14, "bold"),
            fg="#FFB6C1",
            bg="#2d2d44"
        )
        frames_header.pack(pady=10)
        
        self.status_label = tk.Label(
            frames_panel,
            text="Current Reference: - | Status: -",
            font=("Arial", 10),
            fg="#CCCCCC",
            bg="#2d2d44"
        )
        self.status_label.pack(pady=5)
        
        # Frame boxes container
        self.frames_container = tk.Frame(frames_panel, bg="#2d2d44")
        self.frames_container.pack(pady=15, padx=20)
        
        self.frame_labels = []
        self.create_frame_boxes(3)  # Default 3 frames
        
        # Simulation Report
        report_panel = tk.Frame(middle_frame, bg="#2d2d44", relief=tk.RAISED, bd=2)
        report_panel.pack(fill=tk.BOTH, expand=True, pady=5)
        
        report_header = tk.Label(
            report_panel,
            text="📋 Simulation Report",
            font=("Arial", 14, "bold"),
            fg="#87CEEB",
            bg="#2d2d44"
        )
        report_header.pack(pady=10)
        
        # Report text
        report_frame = tk.Frame(report_panel, bg="#2d2d44")
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.report_text = tk.Text(
            report_frame,
            font=("Consolas", 10),
            bg="#1a1a2e",
            fg="#CCCCCC",
            height=8,
            width=45,
            state=tk.DISABLED
        )
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        report_scroll = tk.Scrollbar(report_frame, command=self.report_text.yview)
        report_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.config(yscrollcommand=report_scroll.set)

    def create_frame_boxes(self, num):
        # Clear existing
        for widget in self.frames_container.winfo_children():
            widget.destroy()
        self.frame_labels = []
        
        for i in range(num):
            frame_box = tk.Frame(
                self.frames_container,
                bg="#1a1a2e",
                relief=tk.RAISED,
                bd=2,
                width=70,
                height=70
            )
            frame_box.pack(side=tk.LEFT, padx=5)
            frame_box.pack_propagate(False)
            
            label = tk.Label(
                frame_box,
                text="",
                font=("Arial", 20, "bold"),
                fg="white",
                bg="#1a1a2e"
            )
            label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.frame_labels.append((frame_box, label))

    def create_performance_panel(self, parent):
        perf_frame = tk.Frame(parent, bg="#2d2d44", relief=tk.RAISED, bd=2)
        perf_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Header
        perf_header = tk.Label(
            perf_frame,
            text="🧠 Performance Chart",
            font=("Arial", 14, "bold"),
            fg="#FFB6C1",
            bg="#2d2d44"
        )
        perf_header.pack(pady=10)
        
        sub_header = tk.Label(
            perf_frame,
            text="Current Performance",
            font=("Arial", 10),
            fg="#CCCCCC",
            bg="#2d2d44"
        )
        sub_header.pack()
        
        # Chart canvas
        self.chart_canvas = tk.Canvas(
            perf_frame,
            width=200,
            height=300,
            bg="#1a1a2e",
            highlightthickness=0
        )
        self.chart_canvas.pack(pady=20, padx=20)
        
        # Draw initial chart
        self.draw_chart(0, 0)
        
        # Stats labels
        stats_frame = tk.Frame(perf_frame, bg="#2d2d44")
        stats_frame.pack(pady=10)
        
        self.hits_label = tk.Label(
            stats_frame,
            text="Hits: 0",
            font=("Arial", 12),
            fg="#87CEEB",
            bg="#2d2d44"
        )
        self.hits_label.pack()
        
        self.faults_label = tk.Label(
            stats_frame,
            text="Faults: 0",
            font=("Arial", 12),
            fg="#FFB6C1",
            bg="#2d2d44"
        )
        self.faults_label.pack()
        
        self.hit_rate_label = tk.Label(
            stats_frame,
            text="Hit Rate: 0%",
            font=("Arial", 12, "bold"),
            fg="#98FB98",
            bg="#2d2d44"
        )
        self.hit_rate_label.pack(pady=10)

    def draw_chart(self, hits, faults):
        self.chart_canvas.delete("all")
        
        # Chart dimensions
        chart_x = 30
        chart_y = 20
        chart_width = 140
        chart_height = 220
        bar_width = 50
        
        # Max value for scaling
        max_val = max(hits, faults, 1)
        
        # Draw bars
        # Hits bar
        hits_height = (hits / max_val) * chart_height if max_val > 0 else 0
        self.chart_canvas.create_rectangle(
            chart_x, chart_y + chart_height - hits_height,
            chart_x + bar_width, chart_y + chart_height,
            fill="#1a1a2e", outline="#87CEEB", width=2
        )
        self.chart_canvas.create_text(
            chart_x + bar_width // 2, chart_y + chart_height - hits_height - 15,
            text=str(hits), fill="#87CEEB", font=("Arial", 12, "bold")
        )
        self.chart_canvas.create_text(
            chart_x + bar_width // 2, chart_y + chart_height + 15,
            text="Hits", fill="#CCCCCC", font=("Arial", 10)
        )
        
        # Faults bar
        faults_height = (faults / max_val) * chart_height if max_val > 0 else 0
        faults_x = chart_x + bar_width + 30
        self.chart_canvas.create_rectangle(
            faults_x, chart_y + chart_height - faults_height,
            faults_x + bar_width, chart_y + chart_height,
            fill="#FFB6C1", outline="#FFB6C1", width=2
        )
        self.chart_canvas.create_text(
            faults_x + bar_width // 2, chart_y + chart_height - faults_height - 15,
            text=str(faults), fill="#FFB6C1", font=("Arial", 12, "bold")
        )
        self.chart_canvas.create_text(
            faults_x + bar_width // 2, chart_y + chart_height + 15,
            text="Faults", fill="#CCCCCC", font=("Arial", 10)
        )

    def create_trace_log_panel(self):
        log_frame = tk.Frame(self.root, bg="#2d2d44", relief=tk.RAISED, bd=2)
        log_frame.pack(fill=tk.X, padx=20, pady=10)
        
        log_header = tk.Label(
            log_frame,
            text="📋 Algorithm Trace Log",
            font=("Arial", 14, "bold"),
            fg="#87CEEB",
            bg="#2d2d44"
        )
        log_header.pack(anchor=tk.W, padx=10, pady=10)
        
        log_container = tk.Frame(log_frame, bg="#2d2d44")
        log_container.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.log_text = tk.Text(
            log_container,
            font=("Consolas", 10),
            bg="#1a1a2e",
            fg="#98FB98",
            height=6,
            state=tk.DISABLED
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        log_scroll = tk.Scrollbar(log_container, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scroll.set)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Trace File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.trace_file.set(filename)
            self.load_trace_file()

    def load_trace_file(self):
        filename = self.trace_file.get()
        if filename:
            self.trace = read_trace_file(filename)
            if self.trace:
                # Display page reference string
                pages = [str(t[1]) for t in self.trace]
                ref_str = " ".join(pages[:20])
                if len(pages) > 20:
                    ref_str += " ..."
                self.ref_string_label.config(text=ref_str, fg="#98FB98")
                self.log_message(f"Loaded {len(self.trace)} page references from file")
            else:
                self.ref_string_label.config(text="Error loading file", fg="#ff6b6b")
                self.log_message("Error: Could not load trace file")

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_report(self, message):
        self.report_text.config(state=tk.NORMAL)
        self.report_text.insert(tk.END, message + "\n")
        self.report_text.see(tk.END)
        self.report_text.config(state=tk.DISABLED)

    def update_frames_display(self, frames, highlight_idx=-1, is_fault=False):
        for i, (box, label) in enumerate(self.frame_labels):
            if frames[i] is not None:
                label.config(text=str(frames[i]))
                if i == highlight_idx:
                    if is_fault:
                        box.config(bg="#FFB6C1")  # Pink for fault
                        label.config(bg="#FFB6C1", fg="#1a1a2e")
                    else:
                        box.config(bg="#98FB98")  # Green for hit
                        label.config(bg="#98FB98", fg="#1a1a2e")
                else:
                    box.config(bg="#1a1a2e")
                    label.config(bg="#1a1a2e", fg="white")
            else:
                label.config(text="")
                box.config(bg="#1a1a2e")
                label.config(bg="#1a1a2e")

    def run_simulation(self):
        if not self.trace:
            messagebox.showerror("Error", "Please load a trace file first!")
            return
        
        try:
            num_frames = self.num_frames.get()
            if num_frames < 1:
                raise ValueError("Frames must be at least 1")
        except:
            messagebox.showerror("Error", "Invalid number of frames!")
            return
        
        # Update frame boxes
        self.create_frame_boxes(num_frames)
        
        # Create algorithm
        algo_name = self.algorithm_var.get()
        if algo_name == "FIFO":
            algorithm = FIFO()
        else:
            algorithm = LRU(num_frames)
        
        # Create VM
        self.vm = VirtualMemory(num_frames, algorithm, tlb_size=4)
        self.current_step = 0
        self.is_running = True
        
        # Update UI
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Clear logs
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete(1.0, tk.END)
        self.report_text.config(state=tk.DISABLED)
        
        self.log_message(f"--- Starting Simulation: {algo_name} ---")
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()

    def simulation_loop(self):
        while self.is_running and self.current_step < len(self.trace):
            op, page = self.trace[self.current_step]
            
            # Access memory
            status, old_page, frame_idx, is_tlb_hit = self.vm.access(page, op)
            
            # Update UI (thread-safe)
            self.root.after(0, self.update_step, page, status, old_page, frame_idx)
            
            self.current_step += 1
            time.sleep(self.speed_var.get())
        
        if self.is_running:
            self.root.after(0, self.simulation_complete)

    def update_step(self, page, status, old_page, frame_idx):
        is_fault = "FAULT" in status
        
        # Update status label
        self.status_label.config(text=f"Current Reference: {page} | Status: {status}")
        
        # Update frames display
        self.update_frames_display(self.vm.frames, frame_idx, is_fault)
        
        # Log message
        mem_str = str([f if f is not None else "-" for f in self.vm.frames])
        if old_page is not None:
            self.log_message(f"[{status}] Page {page} : Replace {old_page} with {page}. Memory: {mem_str}")
        else:
            self.log_message(f"[{status}] Page {page} : Insert: {page}. Memory: {mem_str}")
        
        # Update chart
        self.draw_chart(self.vm.hits, self.vm.page_faults)
        
        # Update stats
        self.hits_label.config(text=f"Hits: {self.vm.hits}")
        self.faults_label.config(text=f"Faults: {self.vm.page_faults}")
        
        total = self.vm.hits + self.vm.page_faults
        if total > 0:
            hit_rate = (self.vm.hits / total) * 100
            self.hit_rate_label.config(text=f"Hit Rate: {hit_rate:.1f}%")

    def simulation_complete(self):
        self.is_running = False
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Final report
        self.log_message("--- Simulation Complete ---")
        self.update_report("\n=== FINAL STATISTICS ===")
        self.update_report(f"Total Accesses: {self.vm.hits + self.vm.page_faults}")
        self.update_report(f"Page Faults: {self.vm.page_faults}")
        self.update_report(f"Hits: {self.vm.hits}")
        self.update_report(f"TLB Hits: {self.vm.tlb_hits}")
        self.update_report(f"TLB Misses: {self.vm.tlb_misses}")
        
        total = self.vm.hits + self.vm.page_faults
        if total > 0:
            fault_rate = (self.vm.page_faults / total) * 100
            hit_rate = (self.vm.hits / total) * 100
            self.update_report(f"Page Fault Rate: {fault_rate:.2f}%")
            self.update_report(f"Hit Rate: {hit_rate:.2f}%")

    def stop_simulation(self):
        self.is_running = False
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log_message("--- Simulation Stopped ---")

    def reset_simulation(self):
        self.is_running = False
        self.current_step = 0
        
        if self.vm:
            self.vm.reset()
        
        # Reset UI
        self.status_label.config(text="Current Reference: - | Status: -")
        for box, label in self.frame_labels:
            label.config(text="")
            box.config(bg="#1a1a2e")
            label.config(bg="#1a1a2e", fg="white")
        
        self.draw_chart(0, 0)
        self.hits_label.config(text="Hits: 0")
        self.faults_label.config(text="Faults: 0")
        self.hit_rate_label.config(text="Hit Rate: 0%")
        
        # Clear logs
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete(1.0, tk.END)
        self.report_text.config(state=tk.DISABLED)
        
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualMemorySimulatorGUI(root)
    root.mainloop()