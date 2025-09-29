import sys
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import time
import json
import os
from datetime import datetime, timedelta

CATEGORIES_FILE = 'resources/categories.json'
DATA_FILE = '../time_registration_data.json'

ILIONX_RED = '#E8004C'
ILIONX_DARK = '#212529'


def load_categories():
    if os.path.exists(CATEGORIES_FILE):
        try:
            with open(CATEGORIES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    return [
    "ACP",
    "Application Packaging",
    "Azure Kubernetes Platform",
    "Connected Hosting",
    "Identity Access Management",
    "iDP",
    "Local support",
    "M365 beheer",
    "Networking",
    "PAM",
    "SASE as a Service"
]


def save_categories(categories):
    try:
        with open(CATEGORIES_FILE, 'w') as f:
            json.dump(categories, f, indent=4)
    except IOError as e:
        messagebox.showerror("Fout", f"Kon categorieën niet opslaan: {e}")


class CategoryManager:
    def __init__(self, master, app_instance):
        self.master = master
        self.app = app_instance

        self.dialog = ttk.Toplevel(master, resizable=(False, False))
        self.dialog.title("Beheer Categorieën")

        self.dialog.transient(master)
        self.dialog.grab_set()

        dialog_width = 450
        dialog_height = 450
        master.update_idletasks()
        master_window_x = master.winfo_x()
        master_window_y = master.winfo_y()
        master_width = master.winfo_width()
        master_height = master.winfo_height()
        new_x = master_window_x + (master_width // 2) - (dialog_width // 2)
        new_y = master_window_y + (master_height // 2) - (dialog_height // 2)
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{new_x}+{new_y}")

        self.categories = load_categories()

        master_frame = ttk.Frame(self.dialog, padding=20, bootstyle="light")
        master_frame.pack(fill='both', expand=True)

        list_frame = ttk.Frame(master_frame)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))

        self.listbox = tk.Listbox(list_frame, height=10, font=('Inter', 11), fg=ILIONX_DARK, selectmode=tk.SINGLE)
        self.listbox.pack(side=LEFT, fill='both', expand=True, padx=(0, 5))
        self.listbox.bind('<<ListboxSelect>>', self.on_select_category)

        list_scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.listbox.yview, bootstyle="round")
        list_scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=list_scrollbar.set)

        self.refresh_listbox()

        input_frame = ttk.Frame(master_frame)
        input_frame.pack(fill='x', pady=5)

        self.new_category_var = tk.StringVar()
        self.category_entry = ttk.Entry(input_frame, textvariable=self.new_category_var, bootstyle="light")
        self.category_entry.pack(side=LEFT, fill='x', expand=True, padx=(0, 5))

        button_frame = ttk.Frame(master_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        button_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(button_frame, text="Toevoegen", command=self.add_category, bootstyle="primary").grid(row=0,
                                                                                                            column=0,
                                                                                                            padx=5,
                                                                                                            sticky='ew')
        ttk.Button(button_frame, text="Update", command=self.update_category, bootstyle="info-outline").grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=5,
                                                                                                            sticky='ew')
        ttk.Button(button_frame, text="Verwijder", command=self.delete_category, bootstyle="danger").grid(row=0,
                                                                                                            column=2,
                                                                                                            padx=5,
                                                                                                            sticky='ew')

        ttk.Button(master_frame, text="Sluiten & Vernieuwen", command=self.close_manager, style="Action.TButton").pack(
            pady=20, fill='x')

    def refresh_listbox(self):
        self.listbox.delete(0, END)
        for category in self.categories:
            self.listbox.insert(END, category)

    def on_select_category(self, event):
        try:
            index = self.listbox.curselection()[0]
            selected_category = self.listbox.get(index)
            self.new_category_var.set(selected_category)
        except IndexError:
            pass

    def add_category(self):
        new_cat = self.new_category_var.get().strip()
        if new_cat and new_cat not in self.categories:
            self.categories.append(new_cat)
            save_categories(self.categories)
            self.refresh_listbox()
            self.new_category_var.set("")
        else:
            messagebox.showwarning("Fout", "Voer een unieke categorie naam in.")

    def update_category(self):
        try:
            index = self.listbox.curselection()[0]
            old_cat = self.listbox.get(index)
            new_cat = self.new_category_var.get().strip()

            if new_cat and new_cat != old_cat:
                self.categories[index] = new_cat
                save_categories(self.categories)
                self.refresh_listbox()
                self.new_category_var.set("")
            else:
                messagebox.showwarning("Fout", "Voer een geldige, gewijzigde naam in.")
        except IndexError:
            messagebox.showwarning("Fout", "Selecteer eerst een categorie om te bewerken.")

    def delete_category(self):
        try:
            index = self.listbox.curselection()[0]
            category_to_delete = self.listbox.get(index)

            if messagebox.askyesno("Verwijder Categorie",
                                   f"Weet je zeker dat je '{category_to_delete}' wilt verwijderen?"):
                del self.categories[index]
                save_categories(self.categories)
                self.refresh_listbox()
                self.new_category_var.set("")
                self.app.refresh_category_buttons()

        except IndexError:
            messagebox.showwarning("Fout", "Selecteer eerst een categorie om te verwijderen.")

    def close_manager(self):
        self.app.refresh_category_buttons()
        self.dialog.destroy()


class TimeRegistrationApp:
    def __init__(self, master):
        self.master = master
        master.title("Tijd Registratie Tool")

        s = ttk.Style()

        bg_light = '#F8F9FA'
        fg_dark = ILIONX_DARK
        primary_color = ILIONX_RED
        danger_color = '#C82333'

        s.configure("Action.TButton",
                    font=('Inter', 11, 'bold'),
                    padding=(15, 10),
                    foreground='white',
                    background=primary_color,
                    focusthickness=0)
        s.map("Action.TButton",
              background=[('active', primary_color)],
              foreground=[('active', 'white')])

        s.configure("Category.Outline.TButton",
                    font=('Inter', 11),
                    padding=(15, 10),
                    foreground=fg_dark,
                    background='white',
                    borderwidth=1,
                    bordercolor=fg_dark,
                    focusthickness=0)
        s.map("Category.Outline.TButton",
              background=[('active', primary_color)],
              foreground=[('active', 'white')],
              bordercolor=[('active', primary_color)])

        s.configure("Danger.Action.TButton",
                    font=('Inter', 11, 'bold'),
                    padding=(15, 10),
                    foreground='white',
                    background=danger_color,
                    focusthickness=0)
        s.map("Danger.Action.TButton",
              background=[('active', danger_color)],
              foreground=[('active', 'white')])

        s.configure("Status.TLabel",
                    padding=(15, 15),
                    font=('Inter', 12, 'italic'),
                    foreground=primary_color,
                    background=bg_light)

        s.configure("Header.TLabel",
                    font=('Inter', 24, 'bold'),
                    foreground=fg_dark,
                    background='white')

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(2, weight=1)

        self.current_category = None
        self.start_time = None

        self.categories = load_categories()
        self.session_data = self.load_data()
        self.user_id = os.environ.get('USERNAME', 'Gebruiker')

        header_frame = ttk.Frame(master, padding=(20, 10), style='Header.TLabel')
        header_frame.grid(row=0, column=0, sticky='ew')
        header_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(header_frame, text="Tijd Registratie Tool", style="Header.TLabel").grid(row=0, column=0, pady=5)

        self.status_var = tk.StringVar(value="Selecteer een categorie om te starten.")
        ttk.Label(master, textvariable=self.status_var,
                  style="Status.TLabel",
                  anchor='w').grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 15))

        content_frame = ttk.Frame(master, padding=(0, 0))
        content_frame.grid(row=2, column=0, sticky='nsew', padx=20, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        header_controls = ttk.Frame(content_frame)
        header_controls.grid(row=0, column=0, pady=(0, 10), sticky='ew')
        header_controls.columnconfigure(0, weight=1)

        ttk.Label(header_controls, text="Registratie Categorieën", style="Header.TLabel",
                  font=('Inter', 14, 'bold')).grid(
            row=0, column=0, sticky='w')

        ttk.Button(header_controls, text="Beheer Categorieën", command=lambda: CategoryManager(self.master, self),
                   bootstyle="outline-primary").grid(row=0, column=1, padx=10, sticky='e')

        canvas_frame = ttk.Frame(content_frame)
        canvas_frame.grid(row=1, column=0, sticky='nsew')
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)

        self.category_canvas = tk.Canvas(canvas_frame, height=420, highlightthickness=0, bg='white')
        self.category_canvas.grid(row=0, column=0, sticky='nsew')

        category_scrollbar = ttk.Scrollbar(canvas_frame, orient=VERTICAL, command=self.category_canvas.yview,
                                             bootstyle="round")
        category_scrollbar.grid(row=0, column=1, sticky='ns')

        self.category_canvas.configure(yscrollcommand=category_scrollbar.set)

        self.inner_frame = ttk.Frame(self.category_canvas, bootstyle="light")

        self.canvas_window_id = self.category_canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.category_canvas.bind('<Enter>', self._bind_mousewheel)
        self.category_canvas.bind('<Leave>', self._unbind_mousewheel)
        self.category_canvas.bind('<Configure>', self._on_canvas_resize)

        self.refresh_category_buttons()

        action_frame = ttk.Frame(master, padding=(0, 0))
        action_frame.grid(row=3, column=0, sticky='ew', padx=20, pady=15)

        action_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ttk.Button(action_frame, text="STOP Registratie", command=self.stop_tracking,
                   style="Danger.Action.TButton").grid(row=0, column=0, padx=5, sticky='ew')

        ttk.Button(action_frame, text="Toon Dagoverzicht", command=self.generate_summary_dialog,
                   style="Action.TButton").grid(row=0, column=1, padx=5, sticky='ew')

        ttk.Button(action_frame, text="RESET ALLE Data", command=self.reset_data,
                   style="Action.TButton").grid(row=0, column=2, padx=5, sticky='ew')

        self.update_display()

    def refresh_category_buttons(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        self.categories = load_categories()

        for category in self.categories:
            btn = ttk.Button(self.inner_frame, text=category,
                             style="Category.Outline.TButton",
                             command=lambda c=category: self.start_tracking(c),
                             cursor='hand2')
            btn.pack(fill='x', expand=True, pady=(5, 5), padx=10)

        self.inner_frame.update_idletasks()
        self._on_frame_configure(None)

    def _on_frame_configure(self, event):
        self.category_canvas.configure(scrollregion=self.category_canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        canvas_width = event.width
        self.category_canvas.itemconfig(self.canvas_window_id, width=canvas_width)

    def _on_mousewheel(self, event):
        self.category_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self, event):
        self.category_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.category_canvas.unbind_all("<MouseWheel>")

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {}
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return {}
        except (json.JSONDecodeError, IOError) as e:
            return {}

    def save_data(self):
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.session_data, f, indent=4)
        except IOError as e:
            print(f"Error saving data: {e}")

    def get_today_data(self):
        today_date = datetime.now().strftime("%Y-%m-%d")
        if today_date not in self.session_data:
            self.session_data[today_date] = {category: 0 for category in self.categories}
        return self.session_data[today_date]

    def format_time(self, seconds):
        td = timedelta(seconds=int(seconds))
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def start_tracking(self, new_category):
        self.stop_tracking()

        self.current_category = new_category
        self.start_time = time.time()

        self.status_var.set(f"▶️ Registreren: {self.current_category}\nVerstreken: 00:00:00")

        today_data = self.get_today_data()
        if new_category not in today_data:
            today_data[new_category] = 0

    def stop_tracking(self):
        if self.current_category is not None:
            end_time = time.time()
            duration = end_time - self.start_time

            today_data = self.get_today_data()
            if self.current_category in today_data:
                today_data[self.current_category] += duration
            else:
                today_data[self.current_category] = duration

            self.save_data()

            self.current_category = None
            self.start_time = None
            self.status_var.set("Taak gestopt. Selecteer een nieuwe categorie om te starten.")
        else:
            self.status_var.set("Geen categorie loopt momenteel.")

    def update_display(self):
        if self.current_category is not None:
            elapsed_seconds = time.time() - self.start_time
            formatted_time = self.format_time(elapsed_seconds)
            self.status_var.set(f"▶️ Registreren: {self.current_category}\nVerstreken: {formatted_time}")

        self.master.after(1000, self.update_display)

    def reset_data(self):
        if messagebox.askyesno("Bevestig Reset",
                               "Weet je zeker dat je ALLE geregistreerde tijd permanent wilt verwijderen? Dit kan niet ongedaan gemaakt worden."):
            self.stop_tracking()
            self.session_data = {}

            try:
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                messagebox.showinfo("Reset Succesvol", "Alle tijdregistratie data is gewist.")
                self.status_var.set("Alle data gewist. Selecteer een categorie om te starten.")
            except IOError as e:
                messagebox.showerror("Fout", f"Fout bij verwijderen data: {e}.")

    def generate_summary(self):
        self.stop_tracking()

        today_data = self.get_today_data()
        summary_lines = [f"Dagelijks Tijdsoverzicht: {datetime.now().strftime('%Y-%m-%d')}\n",
                            "--------------------------------------------------"]

        total_time_seconds = 0

        current_categories = load_categories()

        sorted_data = sorted(today_data.items(), key=lambda item: current_categories.index(item[0]) if item[
                                                                                                                  0] in current_categories else 1000)

        for category, seconds in sorted_data:
            if seconds > 0:
                formatted_duration = self.format_time(seconds)
                summary_lines.append(f"{category:<30}: {formatted_duration}")
                total_time_seconds += seconds

        if total_time_seconds == 0:
            summary_lines.append("\nEr is vandaag geen tijd geregistreerd.")
            return "\n".join(summary_lines)

        summary_lines.append("--------------------------------------------------")
        summary_lines.append(f"TOTALE GEREGISTREERDE TIJD: {self.format_time(total_time_seconds)}")

        return "\n".join(summary_lines)

    def generate_summary_dialog(self):
        summary_text = self.generate_summary()

        dialog = ttk.Toplevel(self.master, resizable=(False, False))
        dialog.title("Dagelijks Tijdsoverzicht")

        dialog_width = 480
        dialog_height = 500
        self.master.update_idletasks()
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        new_x = master_x + (master_width // 2) - (dialog_width // 2)
        new_y = master_y + (master_height // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{new_x}+{new_y}")

        summary_frame = ttk.Frame(dialog, padding=20, bootstyle="light")
        summary_frame.pack(fill='both', expand=True, padx=15, pady=15)

        ttk.Label(summary_frame, text="Dagelijks Tijdsoverzicht", font=('Inter', 16, 'bold'),
                  foreground=ILIONX_DARK).pack(pady=(0, 10))

        text_scroll_frame = ttk.Frame(summary_frame)
        text_scroll_frame.pack(fill='both', expand=True)

        summary_box = tk.Text(text_scroll_frame, wrap=tk.WORD, height=12, width=40,
                                font=('Courier', 10), bg='#F8F9FA', fg=ILIONX_DARK,
                                insertbackground=ILIONX_DARK, relief=tk.FLAT, bd=0, padx=10, pady=10)

        summary_scrollbar = ttk.Scrollbar(text_scroll_frame, orient=VERTICAL, command=summary_box.yview,
                                             bootstyle="round")
        summary_scrollbar.pack(side=RIGHT, fill=Y)
        summary_box.configure(yscrollcommand=summary_scrollbar.set)
        summary_box.pack(side=LEFT, fill='both', expand=True)

        summary_box.insert(tk.END, summary_text)
        summary_box.config(state=tk.DISABLED)

        ttk.Button(summary_frame, text="Sluiten", command=dialog.destroy,
                   style="Action.TButton").pack(pady=(15, 0))

        dialog.transient(self.master)
        dialog.grab_set()
        self.master.wait_window(dialog)


if __name__ == "__main__":
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath("..")

        return os.path.join(base_path, relative_path)

    root = ttk.Window(themename="litera")
    root.geometry("720x920")

    ico_icon_path = resource_path("resources/icon.ico")

    try:
        root.iconbitmap(ico_icon_path)
    except tk.TclError:
        print("WAARSCHUWING: ICO-icoon niet gevonden.")

    app = TimeRegistrationApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.stop_tracking(), app.save_data(), root.destroy()])
    root.mainloop()