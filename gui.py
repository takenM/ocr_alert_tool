import tkinter as tk
from tkinter import messagebox
import threading
from monitor import Monitor

class OCRAlertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Alert Tool")
        self.root.geometry("500x500")
        
        # Variables
        self.threshold_var = tk.StringVar(value="1000")
        self.monitor_area = None # (x1, y1, x2, y2)
        self.is_monitoring = False
        self.monitor = Monitor()
        
        # GUI Components
        self.create_widgets()

    def create_widgets(self):
        # Threshold Input
        tk.Label(self.root, text="基準値 (以上でアラート):").pack(pady=10)
        tk.Entry(self.root, textvariable=self.threshold_var).pack(pady=5)
        
        # Area Selection
        tk.Button(self.root, text="ご希望の監視エリアの設定", command=self.start_area_selection).pack(pady=10)
        self.area_label = tk.Label(self.root, text="エリア: 未設定")
        self.area_label.pack(pady=5)
        
        # Start/Stop Button
        self.toggle_btn = tk.Button(self.root, text="監視開始", command=self.toggle_monitoring, state=tk.DISABLED)
        self.toggle_btn.pack(pady=20)
        
        # Debug Log Area
        tk.Label(self.root, text="デバッグログ:").pack(anchor="w", padx=10)
        from tkinter import scrolledtext
        self.log_area = scrolledtext.ScrolledText(self.root, height=10, state='disabled')
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def log(self, message):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END) # Auto scroll
        self.log_area.config(state='disabled')

    def start_area_selection(self):
        self.root.iconify() # Minimize main window
        
        # Use mss to get all monitor details
        import mss
        with mss.mss() as sct:
            monitors = sct.monitors[1:] # Skip index 0 (all combined)
        
        self.overlays = []
        
        # Shared state for selection
        self.selection_data = {
            "start_x": None,
            "start_y": None,
            "rect_ids": {}, # map overlay -> rect_id
            "active_overlay": None # which overlay is currently being dragged
        }

        for i, mon in enumerate(monitors):
            self.create_overlay(mon, i)

    def create_overlay(self, mon, idx):
        selection_window = tk.Toplevel(self.root)
        
        # Geometry for this specific monitor
        geo = f"{mon['width']}x{mon['height']}+{mon['left']}+{mon['top']}"
        selection_window.geometry(geo)
        selection_window.overrideredirect(True)
        selection_window.attributes("-topmost", True)
        
        # Transparency
        import platform
        system = platform.system()
        if system == "Darwin":
            selection_window.attributes("-alpha", 0.3)
            selection_window.configure(bg="black")
            selection_window.lift()
            selection_window.focus_force()
        elif system == "Windows":
            selection_window.attributes("-alpha", 0.3)
            selection_window.configure(bg="black")
        else:
            selection_window.attributes("-alpha", 0.3)
        
        # Canvas
        canvas = tk.Canvas(selection_window, cursor="cross", bg="black", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Store overlay reference
        overlay_obj = {
            "window": selection_window,
            "canvas": canvas,
            "mon": mon,
            "idx": idx
        }
        self.overlays.append(overlay_obj)
        
        # Event Handlers (Capture scope with defaults)
        def on_mouse_down(event, obj=overlay_obj):
            self.selection_data["active_overlay"] = obj
            # Global screen coordinates
            self.selection_data["start_x"] = obj["mon"]["left"] + event.x
            self.selection_data["start_y"] = obj["mon"]["top"] + event.y
            
            # Clear existing rects in all overlays
            # rect_ids is now keyed by monitor index
            for idx_key in self.selection_data["rect_ids"]:
                # Find the overlay for this idx to get its canvas
                # (A bit inefficient but safe)
                target_ov = next((o for o in self.overlays if o["idx"] == idx_key), None)
                if target_ov:
                    target_ov["canvas"].delete(self.selection_data["rect_ids"][idx_key])
            self.selection_data["rect_ids"].clear()

        def on_mouse_drag(event, obj=overlay_obj):
            if self.selection_data["active_overlay"] is not obj:
                return # Only handle drag on the active screen for now
            
            # Start is in global coords, need to convert to local for drawing
            start_x_global = self.selection_data["start_x"]
            start_y_global = self.selection_data["start_y"]
            
            # Convert global start to local start
            local_start_x = start_x_global - obj["mon"]["left"]
            local_start_y = start_y_global - obj["mon"]["top"]
            
            # Current mouse pos (event.x, event.y) is already local
            current_x_local = event.x
            current_y_local = event.y
            
            c = obj["canvas"]
            idx = obj["idx"]
            
            if idx not in self.selection_data["rect_ids"]:
                # Create new rectangle
                self.selection_data["rect_ids"][idx] = c.create_rectangle(
                    local_start_x, local_start_y, current_x_local, current_y_local, 
                    outline="white", width=3 # Thicker line
                )
            else:
                # Update existing
                rect_id = self.selection_data["rect_ids"][idx]
                c.coords(rect_id, local_start_x, local_start_y, current_x_local, current_y_local)

        def on_mouse_up(event, obj=overlay_obj):
            if self.selection_data["active_overlay"] is not obj:
                return

            end_x = obj["mon"]["left"] + event.x
            end_y = obj["mon"]["top"] + event.y
            
            x1, y1 = self.selection_data["start_x"], self.selection_data["start_y"]
            x2, y2 = end_x, end_y
            
            # Normalize
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])
            
            self.monitor_area = (x1, y1, x2, y2)
            self.area_label.config(text=f"エリア: ({x1}, {y1}) - ({x2}, {y2})")
            self.log(f"監視エリア設定完了: {x1},{y1} - {x2},{y2}")
            self.toggle_btn.config(state=tk.NORMAL)
            
            # Close all overlays
            for ov in self.overlays:
                ov["window"].destroy()
            self.overlays = []
            self.root.deiconify()
        
        def on_escape(event):
             for ov in self.overlays:
                ov["window"].destroy()
             self.overlays = []
             self.root.deiconify()

        canvas.bind("<Button-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)
        selection_window.bind("<Escape>", on_escape)
        
        # Instruction Text
        canvas.create_text(
            mon["width"]//2, mon["height"]//2, 
            text="ここをドラッグして選択", 
            font=("Arial", 24), fill="white"
        )

    def toggle_monitoring(self):
        if not self.is_monitoring:
            try:
                threshold = float(self.threshold_var.get())
            except ValueError:
                messagebox.showerror("エラー", "基準値には数値を入力してください")
                return
                
            self.is_monitoring = True
            self.toggle_btn.config(text="監視停止")
            self.log(f"監視を開始しました (基準値: {threshold})")
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self.run_monitoring, args=(threshold,), daemon=True)
            self.monitor_thread.start()
        else:
            self.is_monitoring = False
            self.toggle_btn.config(text="監視開始")
            self.log("監視を停止しました")

    def run_monitoring(self, threshold):
        
        def callback(val, text):
            # Update GUI from thread
            self.log(f"Raw: {repr(text)} -> Val: {val}")
            
            if val >= threshold:
                self.root.after(0, lambda: self.show_alert(val))
                return True # Stop monitoring request
            return False # Continue monitoring

        while self.is_monitoring:
            should_stop = self.monitor.process(self.monitor_area, callback)
            if should_stop:
                self.is_monitoring = False
                self.root.after(0, lambda: self.toggle_btn.config(text="監視開始"))
                break
    
    def show_alert(self, val):
        # Play sound (Cross-platform)
        import platform
        system = platform.system()
        
        try:
            if system == "Windows":
                import winsound
                winsound.PlaySound(winsound.SND_ALIAS)
            elif system == "Darwin": # macOS
                # Play system alert sound
                import os
                os.system("afplay /System/Library/Sounds/Glass.aiff")
            else:
                # Linux/Other: Simple beep
                print("\a")
        except Exception:
            print("Alert sound failed")
            
        response = messagebox.askyesno("アラート", f"基準値を超えました！\n値: {val}\n\n監視を続けますか？")
        if response:
            # Restart monitoring
            self.toggle_btn.invoke() # Simple restart
        else:
            self.log("終了しました")
