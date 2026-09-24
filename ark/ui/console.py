"""Optional tkinter vault console. Headless-safe: skip without DISPLAY."""

from __future__ import annotations

import os
import sys
import time

from ark.config import LIMITATION, SECURITY_LEVELS
from ark.engine.cleanup import close_session
from ark.engine.encrypt import encrypt_file
from ark.engine.decrypt import decrypt_file
from ark.engine.ops import enc_path_for_id
from ark.engine.vault_session import open_or_create_vault
from ark.security.errors import uniform_failure_message
from ark.security.virus import VirusFlagged
from ark.ui.colors import FOCUS, system_theme
from ark.utils import resolve_data_dir
from ark.vault.layout import blocks_root, exports_root
from ark.vault.manifest import load_manifest, save_manifest
from ark.vault.naming import new_file_id


def has_display() -> bool:
    if sys.platform == "win32":
        return True
    if sys.platform == "darwin":
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def _vault_tag(session) -> str:
    return os.path.basename(session.vault_dir)


def _ring(widget, theme: dict) -> None:
    widget.configure(
        highlightthickness=2,
        highlightcolor=FOCUS,
        highlightbackground=theme["line"],
    )


def _primary(parent, theme: dict, text: str, command):
    import tkinter as tk

    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=theme["gold"],
        fg=theme["on_gold"],
        activebackground=theme["gold"],
        activeforeground=theme["on_gold"],
        relief="flat",
        padx=12,
        pady=8,
    )
    _ring(button, theme)
    return button


def _ghost(parent, theme: dict, text: str, command):
    import tkinter as tk

    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=theme["panel"],
        fg=theme["fg"],
        activebackground=theme["bg"],
        activeforeground=theme["fg"],
        relief="flat",
        padx=12,
        pady=8,
    )
    _ring(button, theme)
    return button


def launch_login_safe(data_dir: str | None = None) -> None:
    if not has_display():
        raise RuntimeError("No display is available, so the desktop console cannot open. Try: ark ui")
    try:
        import tkinter as tk
    except ModuleNotFoundError:
        raise RuntimeError(
            "The desktop console needs Tk, and it is not installed here. Try: ark ui"
        ) from None
    try:
        launch_login(data_dir=data_dir)
    except tk.TclError:
        raise RuntimeError("The desktop console could not open a window. Try: ark ui") from None


def launch_login(data_dir: str | None = None) -> None:
    import tkinter as tk
    from tkinter import messagebox

    resolved = resolve_data_dir(data_dir)
    theme = system_theme()

    class LoginWindow(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("The ARK")
            self.minsize(360, 280)
            self.configure(bg=theme["bg"])

            tk.Label(
                self,
                text="The ARK",
                bg=theme["bg"],
                fg=theme["fg"],
                font=("TkDefaultFont", 16, "bold"),
            ).pack(anchor="w", padx=16, pady=(16, 0))
            tk.Label(
                self,
                text="Keep files on this computer. The phrase is the login.",
                bg=theme["bg"],
                fg=theme["muted"],
                wraplength=340,
                justify="left",
            ).pack(anchor="w", padx=16, pady=(4, 12))
            tk.Label(self, text="Phrase", bg=theme["bg"], fg=theme["fg"]).pack(anchor="w", padx=16)
            self.phrase_entry = tk.Entry(
                self, width=36, show="•", bg=theme["panel"], fg=theme["fg"], insertbackground=theme["fg"]
            )
            _ring(self.phrase_entry, theme)
            self.phrase_entry.pack(fill="x", padx=16, pady=(4, 12))
            self.phrase_entry.focus_set()

            self.level_var = tk.StringVar(value=SECURITY_LEVELS[0])
            self.advanced_open = False
            self.advanced = tk.Frame(self, bg=theme["bg"])
            tk.Label(self.advanced, text="When this vault locks itself", bg=theme["bg"], fg=theme["fg"]).pack(
                anchor="w"
            )
            om = tk.OptionMenu(self.advanced, self.level_var, *SECURITY_LEVELS)
            om.config(
                bg=theme["panel"],
                fg=theme["fg"],
                activebackground=theme["panel"],
                activeforeground=theme["fg"],
            )
            _ring(om, theme)
            om["menu"].config(bg=theme["panel"], fg=theme["fg"])
            om.pack(fill="x", pady=(4, 4))
            tk.Label(
                self.advanced,
                text="This only changes the lock timer.",
                bg=theme["bg"],
                fg=theme["muted"],
            ).pack(anchor="w", pady=(0, 8))

            _primary(self, theme, "Open vault", self.unlock).pack(fill="x", padx=16, pady=(0, 8))
            row = tk.Frame(self, bg=theme["bg"])
            row.pack(fill="x", padx=16, pady=(0, 8))
            _ghost(row, theme, "Advanced", self.toggle_advanced).pack(side="left")
            _ghost(row, theme, "About", self.about).pack(side="left", padx=(8, 0))
            tk.Label(self, text="Aziel Eliab", bg=theme["bg"], fg=theme["muted"]).pack(
                anchor="w", padx=16, pady=(4, 16)
            )
            self.bind("<Return>", lambda e: self.unlock())

        def toggle_advanced(self):
            if self.advanced_open:
                self.advanced.pack_forget()
                self.advanced_open = False
                return
            self.advanced.pack(fill="x", padx=16, pady=(0, 8), before=self.winfo_children()[-1])
            self.advanced_open = True

        def about(self):
            messagebox.showinfo("About The ARK", LIMITATION)

        def unlock(self):
            phrase = self.phrase_entry.get()
            if not phrase:
                messagebox.showerror(
                    "The ARK",
                    "A phrase is required. Type a phrase, then choose Open vault.",
                )
                return
            try:
                level = self.level_var.get() or "normal"
                session = open_or_create_vault(resolved, phrase, level)
            except Exception:
                messagebox.showerror(
                    "The ARK",
                    uniform_failure_message() + " Try the phrase again.",
                )
                return
            finally:
                try:
                    self.phrase_entry.delete(0, tk.END)
                except Exception:
                    pass
            self.destroy()
            launch_console(session)

    app = LoginWindow()
    app.mainloop()


def launch_console(session):
    import tkinter as tk
    from tkinter import filedialog, messagebox

    theme = system_theme()

    class ConsoleWindow(tk.Tk):
        def __init__(self, session):
            super().__init__()
            self.session = session
            self.title("The ARK")
            self.geometry("720x480")
            self.minsize(360, 320)
            self.configure(bg=theme["bg"])
            self.protocol("WM_DELETE_WINDOW", self._on_close)

            self.vault_tag = _vault_tag(session)
            self.blocks_root = blocks_root(session.vault_dir)
            self.exp_dir = exports_root(session.vault_dir)
            self.manifest = load_manifest(session)
            self.entries = self.manifest.get("entries", {})

            top = tk.Frame(self, bg=theme["bg"])
            top.pack(fill="x", padx=16, pady=(16, 8))
            tk.Label(top, text="Your files", bg=theme["bg"], fg=theme["fg"], font=("TkDefaultFont", 16, "bold")).pack(
                anchor="w"
            )
            tk.Label(
                top,
                text=f"Vault {self.vault_tag[:12]}…",
                bg=theme["bg"],
                fg=theme["muted"],
            ).pack(anchor="w")

            self.listbox = tk.Listbox(
                self,
                bg=theme["panel"],
                fg=theme["fg"],
                selectbackground=theme["gold"],
                selectforeground=theme["on_gold"],
                activestyle="none",
                relief="flat",
            )
            _ring(self.listbox, theme)
            self.listbox.pack(fill="both", expand=True, padx=16, pady=8)

            actions = tk.Frame(self, bg=theme["bg"])
            actions.pack(fill="x", padx=16)
            _primary(actions, theme, "Add a file", self.encrypt_pick).pack(side="left")
            _ghost(actions, theme, "Save a copy", self.decrypt_selected).pack(side="left", padx=(8, 0))

            self.status = tk.Label(
                self,
                text="Vault open. Add a file when you are ready.",
                anchor="w",
                bg=theme["bg"],
                fg=theme["muted"],
            )
            self.status.pack(fill="x", padx=16, pady=(8, 16))
            self.refresh_list()

        def _on_close(self):
            close_session(self.session)
            self.destroy()

        def refresh_list(self):
            self.listbox.delete(0, tk.END)
            for fid, meta in self.entries.items():
                name = meta.get("name") or "(unnamed)"
                self.listbox.insert(tk.END, f"{name}  —  {fid}.ark")

        def _current_file_id(self):
            sel = self.listbox.curselection()
            if not sel:
                return None
            display = self.listbox.get(sel[0])
            if " —  " not in display:
                return None
            tail = display.split(" —  ", 1)[1].strip()
            return tail[:-4] if tail.lower().endswith(".ark") else None

        def _persist_manifest(self):
            self.manifest["entries"] = self.entries
            save_manifest(self.session, self.manifest)

        def encrypt_pick(self):
            in_path = filedialog.askopenfilename(title="Select file to encrypt")
            if not in_path:
                return
            try:
                orig_name = os.path.basename(in_path)
                fid = new_file_id()
                out_path = enc_path_for_id(self.session.vault_dir, fid)
                encrypt_file(self.session, in_path, out_path)
                self.entries[fid] = {"name": orig_name, "color": "", "created_at": int(time.time())}
                self._persist_manifest()
            except VirusFlagged:
                messagebox.showerror(
                    "The ARK",
                    "Blocked (Mode E). This file was not stored. Try a different file.",
                )
                return
            except Exception:
                messagebox.showerror(
                    "The ARK",
                    uniform_failure_message() + " Try a different file.",
                )
                return
            self.refresh_list()
            self.status.config(text="Stored. It is in the list above.")

        def decrypt_selected(self):
            fid = self._current_file_id()
            if not fid:
                messagebox.showinfo("The ARK", "Select a file in the list, then choose Save a copy.")
                return
            in_path = enc_path_for_id(self.session.vault_dir, fid)
            meta = self.entries.get(fid, {})
            suggested_name = meta.get("name") or (fid + ".out")
            out_path = filedialog.asksaveasfilename(
                title="Save decrypted file as", initialfile=os.path.basename(suggested_name)
            )
            if not out_path:
                return
            try:
                decrypt_file(self.session, in_path, out_path)
                self.status.config(text=f"Decrypted: {out_path}")
            except Exception:
                messagebox.showerror(
                    "The ARK",
                    uniform_failure_message() + " Check the phrase by opening the vault again.",
                )

    app = ConsoleWindow(session)
    app.mainloop()
