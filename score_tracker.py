import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ScoreTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Score Tracker")
        self.root.geometry("920x700")
        self.root.resizable(False, False)

        self.sections = {}
        self.data_file = "score_data.json"

        self.section_name_var = tk.StringVar()
        self.score_var = tk.StringVar()
        self.total_var = tk.StringVar()

        self.score_table = None
        self.selected_score_index = None

        self.set_dark_theme()
        self.create_scrollable_window()
        self.create_widgets()
        self.load_data()
        self.populate_sections_listbox()

    def set_dark_theme(self):
        self.root.configure(bg="#2b2b2b")
        style = ttk.Style()
        style.theme_use("default")
        style.configure(".", background="#2b2b2b", foreground="white", fieldbackground="#3c3f41")
        style.configure("TLabel", background="#2b2b2b", foreground="white")
        style.configure("TFrame", background="#2b2b2b")
        style.configure("TEntry", fieldbackground="#3c3f41", foreground="white")
        style.configure("TButton", background="#3c3f41", foreground="white")
        style.configure("Treeview", background="#3c3f41", fieldbackground="#3c3f41", foreground="white")
        style.map("Treeview", background=[('selected', '#4e5052')], foreground=[('selected', 'white')])

    def create_scrollable_window(self):

        canvas = tk.Canvas(self.root, bg="#2b2b2b", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)


        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)


        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))


        self.scroll_frame = ttk.Frame(canvas)
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        self.canvas_window = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

    def create_widgets(self):
        main_frame = ttk.Frame(self.scroll_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=5)

        self.graph_frame = ttk.LabelFrame(main_frame, text="Section Overview")
        self.graph_frame.pack(side="right", fill="both", expand=True, padx=5)

        section_frame = ttk.LabelFrame(left_frame, text="Manage Sections")
        section_frame.pack(pady=5, fill="x")

        ttk.Entry(section_frame, textvariable=self.section_name_var, width=25).pack(pady=2)
        ttk.Button(section_frame, text="Add Section", command=self.add_section).pack(fill="x", pady=1)
        ttk.Button(section_frame, text="Remove Section", command=self.remove_section).pack(fill="x", pady=1)
        ttk.Button(section_frame, text="Rename Section", command=self.rename_section).pack(fill="x", pady=1)

        self.section_listbox = tk.Listbox(left_frame, height=10, bg="#3c3f41", fg="white", selectbackground="#606366")
        self.section_listbox.pack(fill="x", pady=5)
        self.section_listbox.bind("<<ListboxSelect>>", self.display_section_data)

        score_frame = ttk.LabelFrame(left_frame, text="Add Score")
        score_frame.pack(pady=5, fill="x")

        ttk.Label(score_frame, text="Score:").pack(anchor="w")
        ttk.Entry(score_frame, textvariable=self.score_var, width=10).pack(fill="x", pady=2)
        ttk.Label(score_frame, text="Out of:").pack(anchor="w")
        ttk.Entry(score_frame, textvariable=self.total_var, width=10).pack(fill="x", pady=2)
        ttk.Button(score_frame, text="Add Score", command=self.add_score).pack(pady=5, fill="x")

        score_action_frame = ttk.LabelFrame(left_frame, text="Score Actions")
        score_action_frame.pack(pady=5, fill="x")

        ttk.Button(score_action_frame, text="Edit Selected Score", command=self.edit_selected_score).pack(fill="x", pady=2)
        ttk.Button(score_action_frame, text="Delete Selected Score", command=self.delete_selected_score).pack(fill="x", pady=2)

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.sections, f)

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.sections = json.load(f)
                for key in self.sections:
                    self.sections[key] = [tuple(score) for score in self.sections[key]]

    def populate_sections_listbox(self):
        self.section_listbox.delete(0, tk.END)
        for section in self.sections:
            self.section_listbox.insert(tk.END, section)

    def add_section(self):
        name = self.section_name_var.get().strip()
        if name and name not in self.sections:
            self.sections[name] = []
            self.section_listbox.insert(tk.END, name)
            self.section_name_var.set("")
            self.save_data()
        else:
            messagebox.showerror("Error", "Invalid or duplicate section name")

    def remove_section(self):
        selected = self.section_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "No section selected")
            return
        section = self.section_listbox.get(selected)
        if messagebox.askyesno("Confirm", f"Delete section '{section}'?"):
            del self.sections[section]
            self.section_listbox.delete(selected)
            self.display_section_data()
            self.save_data()

    def rename_section(self):
        selected = self.section_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "No section selected")
            return
        old_name = self.section_listbox.get(selected)
        new_name = simpledialog.askstring("Rename Section", f"Enter new name for '{old_name}':")
        if new_name and new_name not in self.sections:
            self.sections[new_name] = self.sections.pop(old_name)
            self.section_listbox.delete(selected)
            self.section_listbox.insert(selected, new_name)
            self.save_data()
        else:
            messagebox.showerror("Error", "Invalid or duplicate section name")

    def add_score(self):
        try:
            selected = self.section_listbox.curselection()
            if not selected:
                messagebox.showwarning("Warning", "No section selected")
                return
            section = self.section_listbox.get(selected)
            score = int(self.score_var.get().strip())
            total = int(self.total_var.get().strip())
            if total == 0:
                raise ValueError("Total cannot be zero")
            self.sections[section].append((score, total))
            self.score_var.set("")
            self.total_var.set("")
            self.display_section_data()
            self.save_data()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def display_section_data(self, event=None):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.score_table = None
        self.selected_score_index = None

        selected = self.section_listbox.curselection()
        if not selected:
            return

        section = self.section_listbox.get(selected)
        scores = self.sections[section]

        if not scores:
            ttk.Label(self.graph_frame, text="No scores yet.").pack()
            return

        attempts = list(range(1, len(scores) + 1))
        given_scores = [s for s, t in scores]
        total_scores = [t for s, t in scores]

        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(5, 2.5))

        ax.plot(attempts, given_scores, marker='o', color='cyan', label='Score')
        ax.plot(attempts, total_scores, marker='x', linestyle='--', color='orange', label='Total')

        ax.set_title(f"Scores in {section}", color='white')
        ax.set_xlabel("Attempt", color='white')
        ax.set_ylabel("Score", color='white')
        ax.tick_params(colors='white')
        ax.grid(True, color='gray')
        ax.legend()

        ttk.Label(self.graph_frame, text=f"Latest Score: {given_scores[-1]} / {total_scores[-1]}").pack(anchor="w", padx=10)
        ttk.Label(self.graph_frame, text=f"Improvement: {given_scores[-1] - given_scores[0]}").pack(anchor="w", padx=10)
        ttk.Label(self.graph_frame, text=f"Average: {sum(given_scores) / len(given_scores):.2f}").pack(anchor="w", padx=10)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5)

        table_container = ttk.Frame(self.graph_frame)
        table_container.pack(fill="both", expand=False, pady=5)
        table_container.config(height=180)

        cols = ("Attempt", "Score", "Total")
        tree = ttk.Treeview(table_container, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        for i, (score, total) in enumerate(scores, 1):
            tree.insert("", "end", values=(i, score, total))

        tree.bind("<<TreeviewSelect>>", self.on_score_selected)

        vsb = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.score_table = tree

    def on_score_selected(self, event):
        selected = event.widget.selection()
        if selected:
            item = event.widget.item(selected[0])
            self.selected_score_index = int(item['values'][0]) - 1

    def edit_selected_score(self):
        if self.selected_score_index is None:
            messagebox.showwarning("Warning", "No score selected")
            return
        section = self.section_listbox.get(self.section_listbox.curselection())
        score, total = self.sections[section][self.selected_score_index]
        new_score = simpledialog.askinteger("Edit Score", "Enter new score:", initialvalue=score)
        new_total = simpledialog.askinteger("Edit Total", "Enter new total:", initialvalue=total)
        if new_score is not None and new_total:
            if new_total == 0:
                messagebox.showerror("Error", "Total cannot be zero")
                return
            self.sections[section][self.selected_score_index] = (new_score, new_total)
            self.display_section_data()
            self.save_data()

    def delete_selected_score(self):
        if self.selected_score_index is None:
            messagebox.showwarning("Warning", "No score selected")
            return
        section = self.section_listbox.get(self.section_listbox.curselection())
        if messagebox.askyesno("Confirm Delete", "Delete the selected score?"):
            del self.sections[section][self.selected_score_index]
            self.selected_score_index = None
            self.display_section_data()
            self.save_data()

if __name__ == "__main__":
    root = tk.Tk()

    window_width = 920
    window_height = 700

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    icon_path = os.path.join(os.path.dirname(__file__), "score.ico")
    try:
        root.iconbitmap(icon_path)
    except Exception as e:
        print("Icon not loaded:", e)
    app = ScoreTracker(root)
    root.mainloop()
