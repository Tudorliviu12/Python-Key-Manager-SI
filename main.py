from database import *
import tkinter as tk
import subprocess
import os
from tkinter import ttk, filedialog, messagebox
from cryptography_logic import *

def incarcare_date():
    for rand in tabel.get_children():
        tabel.delete(rand)
    fisiere = get_fisiere()
    for f in fisiere:
        hash_short = f[3][:15] + "..." if f[3] else "None"
        tabel.insert("", tk.END, values=(f[0], f[1], f[4], f[5], hash_short))

def buton_adauga_fisier():
    path = filedialog.askopenfilename(title="Alege fisierul de introdus in database")
    if path:
        nume_fisier = path.split("/")[-1]
        adauga_fisier(nume_fisier, path)
        incarcare_date()

def buton_delete_fisier():
    select = tabel.selection()
    if not select:
        return
    rand = tabel.item(select[0])
    id_fisier = rand["values"][0]
    nume_fisier = rand["values"][1]
    raspuns = messagebox.askyesno("Stergere", f"Sigur vrei sa stergi fisierul {nume_fisier}?")

    if raspuns:
        delete_fisier(id_fisier)
        incarcare_date()
        btn_sterge.config(state=tk.DISABLED)
        btn_cripteaza.config(state=tk.DISABLED)
        btn_decripteaza.config(state=tk.DISABLED)
        print(f"Fisierul {rand['values'][1]} a fost sters")

def buton_criptare():
    select = tabel.selection()
    if not select:
        return
    rand = tabel.item(select[0])
    id_fisier = rand["values"][0]
    algoritm = combo_alg.get()

    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute("SELECT path FROM fisiere WHERE id_fisier = ?", (id_fisier,))
    path_original = c.fetchone()[0]
    conn.close()

    id_algoritm = 1 if algoritm == 'AES' else 2
    alegere_cheie = combo_cheie.get()
    if alegere_cheie == "Noua":
        id_cheie, cheie_hex, iv_hex = generare_cheie(id_algoritm)
        update_combo_chei()

    else:
        id_cheie_str = alegere_cheie.split()[0]
        id_cheie = int(id_cheie_str)
        date_cheie = get_detalii_cheie(id_cheie)
        cheie_hex, iv_hex = date_cheie

    path_criptat = path_original + ".enc"
    platforma = combo_platforma.get()
    if "Python" in platforma:
        try:
            if "RSA" in algoritm:
                if not path_original.endswith(".txt"):
                    messagebox.showerror("Eroare", "RSA Python are nevoie de fisier txt")
                    return
                criptare_python_rsa(path_original, path_criptat, iv_hex)
            else:
                criptare_python_aes(path_original, path_criptat, cheie_hex, iv_hex)

            os.remove(path_original)
            stare_noua = f"Criptat cu {algoritm} (Cryptography)"
            update_fisier(id_fisier, id_cheie, stare_noua)
            incarcare_date()
            return  # IMPORTANT: ieșim aici ca să nu mai încerce și cu OpenSSL jos
        except Exception as e:
            messagebox.showerror("Eroare Python", str(e))
            return

    comanda_openssl = []
    if algoritm == "AES":
        comanda_openssl = [
            r"C:\Program Files\Git\usr\bin\openssl.exe", "enc", "-aes-256-cbc",
            "-in", path_original, "-out", path_criptat,
            "-K", cheie_hex, "-iv", iv_hex
        ]
    elif algoritm == "RSA":
        if not path_original.endswith(".txt"):
            messagebox.showerror("Eroare", "Pentru RSA e nevoie de un fisier txt")
            return
        comanda_openssl = [
            r"C:\Program Files\Git\usr\bin\openssl.exe", "pkeyutl", "-encrypt",
            "-pubin", "-inkey", iv_hex,
            "-in", path_original, "-out", path_criptat
        ]

    try:
        subprocess.run(comanda_openssl, check=True)
        print("Fisier criptat")
        os.remove(path_original)
    except subprocess.CalledProcessError:
        print("Eroare la criptare")
        return

    stare_noua = f"Criptat cu {algoritm}"
    update_fisier(id_fisier, id_cheie, stare_noua)
    incarcare_date()
    click_tabel(None)


def buton_decriptare():
    select = tabel.selection()
    if not select:
        return
    rand = tabel.item(select[0])
    id_fisier = rand["values"][0]

    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute("SELECT path, id_cheie_activa FROM fisiere WHERE id_fisier = ?", (id_fisier,))
    date_fisier = c.fetchone()
    conn.close()

    if not date_fisier or not date_fisier[1]:
        messagebox.showwarning("Eroare", "Fisierul nu are o cheie activa/nu e criptat")
        return

    path_criptat = date_fisier[0] + ".enc"
    path_decriptat = date_fisier[0]
    id_cheie = date_fisier[1]

    date_cheie = get_detalii_cheie(id_cheie)
    cheie_hex, iv_hex = date_cheie
    stare_curenta = rand["values"][2]

    if "(Cryptography)" in stare_curenta:
        try:
            if "RSA" in stare_curenta:
                decriptare_python_rsa(path_criptat, path_decriptat, cheie_hex)
            else:
                decriptare_python_aes(path_criptat, path_decriptat, cheie_hex, iv_hex)
            os.remove(path_criptat)
            update_fisier(id_fisier, None, "Decriptat")
            incarcare_date()
            print("Fisier decriptat cu Python")
            messagebox.showinfo("Succes", "Fisier decriptat cu framework-ul Python!")
            return
        except Exception as e:
            messagebox.showerror("Eroare", f"Decriptare esuata (Python): {e}")
            return

    comanda_openssl = []
    if "AES" in stare_curenta:
        comanda_openssl = [
            r"C:\Program Files\Git\usr\bin\openssl.exe", "enc", "-d", "-aes-256-cbc",
            "-in", path_criptat, "-out", path_decriptat,
            "-K", cheie_hex, "-iv", iv_hex
        ]
    elif "RSA" in stare_curenta:
        comanda_openssl = [
            r"C:\Program Files\Git\usr\bin\openssl.exe", "pkeyutl", "-decrypt",
            "-inkey", cheie_hex,
            "-in", path_criptat, "-out", path_decriptat
        ]

    try:
        subprocess.run(comanda_openssl, check=True)
        os.remove(path_criptat)
        update_fisier(id_fisier, None, "Decriptat")
        incarcare_date()
        print("Fisier decriptat")
        messagebox.showinfo("Succes", "Fisier decriptat")
    except subprocess.CalledProcessError:
        messagebox.showerror("Eroare", "Decriptare esuata")

def open_debug_chei():
    fereastra_debug = tk.Toplevel(fereastra)
    fereastra_debug.title("Tabela Chei")
    fereastra_debug.geometry("850x300")
    coloane_debug = ("ID", "Valoare Cheie / Private.pem", "Biti", "IV / Public.pem", "ID Algoritm")
    tabel_debug = ttk.Treeview(fereastra_debug, columns=coloane_debug, show="headings")
    for col in coloane_debug:
        tabel_debug.heading(col, text=col)
        if col == "ID" or col == "ID Algoritm" or col == "Biti":
            tabel_debug.column(col, width=80, anchor="center")
        else:
            tabel_debug.column(col, width=300)
    tabel_debug.pack(fill="both", expand=True, padx=10, pady=10)
    chei_db = get_all_chei_debug()
    for c in chei_db:
        tabel_debug.insert("", tk.END, values=(c[0], c[1], c[2], c[3], c[4]))


def click_tabel(event):
    select = tabel.selection()
    if select:
        btn_sterge.config(state=tk.NORMAL)
        rand = tabel.item(select[0])
        stare_curenta = rand["values"][2]

        if stare_curenta == "Decriptat":
            btn_cripteaza.config(state=tk.NORMAL)
            btn_decripteaza.config(state=tk.DISABLED)
        else:
            btn_cripteaza.config(state=tk.DISABLED)
            btn_decripteaza.config(state=tk.NORMAL)
    else:
        btn_sterge.config(state=tk.DISABLED)
        btn_cripteaza.config(state=tk.DISABLED)
        btn_decripteaza.config(state=tk.DISABLED)

def update_combo_chei():
    chei_existente = get_toate_cheile()
    combo_cheie['values'] = ["Noua"] + chei_existente
    combo_cheie.current(0)

init_db()
fereastra = tk.Tk()
fereastra.title("Sistem de management al cheilor de criptare")
fereastra.geometry("600x550")

titlu = tk.Label(fereastra, text="Fisiere", font=("Arial", 16, "bold"))
titlu.pack(pady=10)

coloane = ("ID", "Nume Fisier", "Stare", "ID Cheie", "Hash")
tabel = ttk.Treeview(fereastra, columns=coloane, show="headings")

for col in coloane:
    tabel.heading(col, text=col)
    if col == "ID" or col=="ID Cheie":
        tabel.column(col, width=60)
    elif col == "Hash" or col == "Stare":
        tabel.column(col, width=120)
    else:
        tabel.column(col, width=150)

tabel.pack(pady=20, fill="x", padx=20)
tabel.bind("<<TreeviewSelect>>", click_tabel)

panou_btn = tk.Frame(fereastra)
panou_btn.pack(pady=5)

btn_refresh = tk.Button(panou_btn, text="Incarca Database-ul", command=incarcare_date, bg="lightblue")
btn_refresh.grid(row=0, column=0, padx=10, pady = 10)

btn_adauga = tk.Button(panou_btn, text="Adauga Fisier", command=buton_adauga_fisier, bg="lightblue")
btn_adauga.grid(row=0, column=1, padx=10, pady = 10)

btn_sterge = tk.Button(panou_btn, text="Sterge Fisier", command=buton_delete_fisier, bg="lightblue", state=tk.DISABLED)
btn_sterge.grid(row=0, column=2, padx=10, pady = 10)

panou_cript = tk.Frame(fereastra)
panou_cript.pack(pady=20)

label_algo = tk.Label(panou_cript, text="Algoritm:")
label_algo.grid(row=0, column=0, padx=5, pady=5)

combo_alg = ttk.Combobox(panou_cript, values=["AES", "RSA"], state="readonly", width=10)
combo_alg.current(0)
combo_alg.grid(row=0, column=1, padx=5, pady=5)

label_plat = tk.Label(panou_cript, text="Platforma:")
label_plat.grid(row=0, column=2, padx=5, pady=5)

combo_platforma = ttk.Combobox(panou_cript, values=["OpenSSL", "Python - Cryptography"], state="readonly", width=10)
combo_platforma.current(0)
combo_platforma.grid(row=0, column=3, padx=5, pady=5)

label_cheie = tk.Label(panou_cript, text="Cheie:")
label_cheie.grid(row=0, column=4, padx=5, pady=5)

combo_cheie = ttk.Combobox(panou_cript, state="readonly", width=10)
combo_cheie.grid(row=0, column=5, padx=5, pady=5)

update_combo_chei()

btn_cripteaza = tk.Button(panou_cript, text="Criptare", command=buton_criptare, bg="lavender", state=tk.DISABLED)
btn_cripteaza.grid(row=1, column=2, padx=10, pady=10)

btn_decripteaza = tk.Button(panou_cript, text="Decriptare", command=buton_decriptare, bg="lavender", state=tk.DISABLED)
btn_decripteaza.grid(row=1, column=3, padx=10, pady=10)

btn_debug = tk.Button(fereastra, text="Vezi Cheile din DB", command=open_debug_chei, bg="lightblue")
btn_debug.pack(pady=20)

fereastra.mainloop()