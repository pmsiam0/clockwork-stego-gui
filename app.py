import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from clockcodec import encode_message_to_svg, decode_svg

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clockwork Stego")
        self.geometry("720x520")
        self.resizable(False, False)
        self._build()

    def _build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)

        enc = ttk.Frame(nb)
        dec = ttk.Frame(nb)
        nb.add(enc, text="Encode")
        nb.add(dec, text="Decode")

        enc_main = ttk.Frame(enc, padding=16)
        enc_main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(enc_main, text="Message").grid(row=0, column=0, sticky="w")
        self.msg = tk.Text(enc_main, height=10, width=70, wrap="word")
        self.msg.grid(row=1, column=0, columnspan=3, pady=(4,12))

        ttk.Label(enc_main, text="Passphrase (optional)").grid(row=2, column=0, sticky="w")
        self.passphrase_enc = ttk.Entry(enc_main, width=40, show="")
        self.passphrase_enc.grid(row=3, column=0, sticky="w", pady=(4,12))

        ttk.Label(enc_main, text="Columns").grid(row=2, column=1, sticky="w")
        self.cols_var = tk.IntVar(value=16)
        self.cols = ttk.Spinbox(enc_main, from_=4, to=64, textvariable=self.cols_var, width=6)
        self.cols.grid(row=3, column=1, sticky="w", padx=(8,0))

        btn_row = ttk.Frame(enc_main)
        btn_row.grid(row=4, column=0, columnspan=3, pady=(8,0), sticky="w")

        save_btn = ttk.Button(btn_row, text="Encode → Save SVG", command=self._encode)
        save_btn.pack(side=tk.LEFT)

        dec_main = ttk.Frame(dec, padding=16)
        dec_main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(dec_main, text="Input SVG").grid(row=0, column=0, sticky="w")
        self.infile_var = tk.StringVar()
        inrow = ttk.Frame(dec_main)
        inrow.grid(row=1, column=0, columnspan=3, sticky="we", pady=(4,12))
        self.infile_entry = ttk.Entry(inrow, textvariable=self.infile_var, width=60)
        self.infile_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(inrow, text="Browse", command=self._browse_in).pack(side=tk.LEFT, padx=(8,0))

        ttk.Label(dec_main, text="Passphrase (optional)").grid(row=2, column=0, sticky="w")
        self.passphrase_dec = ttk.Entry(dec_main, width=40, show="")
        self.passphrase_dec.grid(row=3, column=0, sticky="w", pady=(4,12))

        ttk.Label(dec_main, text="Decoded Output").grid(row=4, column=0, sticky="w")
        self.out = tk.Text(dec_main, height=12, width=70, wrap="word")
        self.out.grid(row=5, column=0, columnspan=3, pady=(4,12))

        act_row = ttk.Frame(dec_main)
        act_row.grid(row=6, column=0, columnspan=3, sticky="w")
        ttk.Button(act_row, text="Decode", command=self._decode).pack(side=tk.LEFT)

        for f in (enc_main, dec_main):
            for i in range(3):
                f.columnconfigure(i, weight=1)

    def _browse_in(self):
        p = filedialog.askopenfilename(filetypes=[("SVG files","*.svg"), ("All files","*.*")])
        if p:
            self.infile_var.set(p)

    def _encode(self):
        m = self.msg.get("1.0", tk.END).rstrip("\n")
        if not m:
            messagebox.showwarning("Clockwork Stego", "Enter a message")
            return
        cols = int(self.cols_var.get())
        p = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG files","*.svg")])
        if not p:
            return
        k = self.passphrase_enc.get().strip()
        try:
            encode_message_to_svg(m, p, key_passphrase=k if k else None, cols=cols)
            messagebox.showinfo("Clockwork Stego", "Saved SVG")
        except Exception as e:
            messagebox.showerror("Clockwork Stego", str(e))

    def _decode(self):
        p = self.infile_var.get().strip()
        if not p:
            messagebox.showwarning("Clockwork Stego", "Choose an input SVG")
            return
        k = self.passphrase_dec.get().strip()
        try:
            data = decode_svg(p, key_passphrase=k if k else None)
            try:
                s = data.decode("utf-8")
            except:
                s = data.hex()
            self.out.delete("1.0", tk.END)
            self.out.insert("1.0", s)
        except Exception as e:
            messagebox.showerror("Clockwork Stego", str(e))

if __name__ == "__main__":
    App().mainloop()
