"""Optional tkinter vault console. Headless-safe: skip without DISPLAY."""

from __future__ import annotations

import os
import sys
import time

from ark.config import SECURITY_LEVELS
from ark.engine.cleanup import close_session
from ark.engine.encrypt import encrypt_file
from ark.engine.decrypt import decrypt_file
from ark.engine.ops import enc_path_for_id
from ark.engine.vault_session import open_or_create_vault
from ark.security.errors import uniform_failure_message
from ark.ui.colors import PALETTE, THEME_BG, THEME_FG, THEME_PANEL, normalize_color, tag_to_hex
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


def _safe_tag_hex(tag: str) -> str:
    hx = tag_to_hex(tag)
    if hx.lower() in ("#000", "#000000"):
        return "#bbb"
    return hx or THEME_FG


def launch_login_safe(data_dir: str | None = None) -> None:
    if not has_display():
        raise RuntimeError("No display. Use `ark ui` (loopback HTTP) instead of `ark console`.")
    launch_login(data_dir=data_dir)


def launch_login(data_dir: str | None = None) -> None:
    import tkinter as tk
    from tkinter import messagebox

    resolved = resolve_data_dir(data_dir)

    class LoginWindow(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("ARK - Unlock")
            self.resizable(False, False)
            self.configure(bg=THEME_BG)

            tk.Label(self, text="Phrase (this IS the login)", bg=THEME_BG, fg=THEME_FG).grid(
                row=0, column=0, padx=10, pady=(10, 4), sticky="w"
            )
            self.phrase_entry = tk.Entry(
                self, width=38, show="•", bg=THEME_PANEL, fg=THEME_FG, insertbackground=THEME_FG
            )
            self.phrase_entry.grid(row=1, column=0, padx=10, pady=(0, 10))
            self.phrase_entry.focus_set()

            tk.Label(self, text="Security level", bg=THEME_BG, fg=THEME_FG).grid(
                row=2, column=0, padx=10, pady=(0, 4), sticky="w"
            )
            self.level_var = tk.StringVar(value=SECURITY_LEVELS[0])
            om = tk.OptionMenu(self, self.level_var, *SECURITY_LEVELS)
            om.config(
                bg=THEME_PANEL,
                fg=THEME_FG,
                activebackground=THEME_PANEL,
                activeforeground=THEME_FG,
                highlightthickness=0,
            )
            om["menu"].config(bg=THEME_PANEL, fg=THEME_FG)
            om.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

            tk.Button(
                self,
                text="Unlock",
                command=self.unlock,
                bg=THEME_PANEL,
                fg=THEME_FG,
                activebackground=THEME_BG,
                activeforeground=THEME_FG,
            ).grid(row=4, column=0, padx=10, pady=(0, 12), sticky="ew")
            self.bind("<Return>", lambda e: self.unlock())

        def unlock(self):
            phrase = self.phrase_entry.get()
            if not phrase:
                messagebox.showerror("ARK", "A phrase is required.")
                return
            try:
                level = self.level_var.get() or "normal"
                session = open_or_create_vault(resolved, phrase, level)
            except Exception:
                messagebox.showerror("ARK", uniform_failure_message())
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

    class ConsoleWindow(tk.Tk):
        def __init__(self, session):
            super().__init__()
            self.session = session
            self.title("ARK - Vault Console")
            self.geometry("820x520")
            self.configure(bg=THEME_BG)
            self.protocol("WM_DELETE_WINDOW", self._on_close)

            self.vault_tag = _vault_tag(session)
            self.blocks_root = blocks_root(session.vault_dir)
            self.exp_dir = exports_root(session.vault_dir)
            self.manifest = load_manifest(session)
            self.entries = self.manifest.get("entries", {})

            top = tk.Frame(self, bg=THEME_BG)
            top.pack(fill="x", padx=10, pady=10)
            tk.Label(top, text=f"Vault: {self.vault_tag[:12]}…", bg=THEME_BG, fg=THEME_FG).pack(side="left")

            mid = tk.Frame(self, bg=THEME_BG)
            mid.pack(fill="both", expand=True, padx=10)
            self.listbox = tk.Listbox(
                mid, bg=THEME_PANEL, fg=THEME_FG, selectbackground="#333333", activestyle="none"
            )
            self.listbox.pack(side="left", fill="both", expand=True)

            right = tk.Frame(mid, width=260, bg=THEME_BG)
            right.pack(side="right", fill="y", padx=(10, 0))
            tk.Button(right, text="Encrypt File…", command=self.encrypt_pick, bg=THEME_PANEL, fg=THEME_FG).pack(
                fill="x", pady=4
            )
            tk.Button(
                right, text="Decrypt Selected…", command=self.decrypt_selected, bg=THEME_PANEL, fg=THEME_FG
            ).pack(fill="x", pady=4)
            tk.Button(right, text="Refresh", command=self.refresh_list, bg=THEME_PANEL, fg=THEME_FG).pack(
                fill="x", pady=4
            )

            self.status = tk.Label(self, text="Not a kernel. Local deniable vault.", anchor="w", bg=THEME_BG, fg=THEME_FG)
            self.status.pack(fill="x", padx=10, pady=(6, 10))
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
            except Exception:
                messagebox.showerror("ARK", uniform_failure_message())
                return
            self.refresh_list()

        def decrypt_selected(self):
            fid = self._current_file_id()
            if not fid:
                messagebox.showinfo("ARK", "Select an encrypted item first.")
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
                messagebox.showerror("ARK", uniform_failure_message())

    app = ConsoleWindow(session)
    app.mainloop()
