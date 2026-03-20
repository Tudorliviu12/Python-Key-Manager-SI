from database import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def incarcare_date():
    for rand in tabel.get_children():
        tabel.delete(rand)
    fisiere = get_fisiere()
    for f in fisiere:
        tabel.insert("", tk.END, values=(f[0], f[1], f[4], f[5]))

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

    id_cheie = 999 #de modificat pt etapa urm
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
    update_fisier(id_fisier, None, "Decriptat")
    incarcare_date()
    click_tabel(None)

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

init_db()
fereastra = tk.Tk()
fereastra.title("Sistem de management al cheilor de criptare")
fereastra.geometry("600x450")

titlu = tk.Label(fereastra, text="Fisiere", font=("Arial", 16, "bold"))
titlu.pack(pady=10)

coloane = ("ID", "Nume Fisier", "Stare", "ID Cheie")
tabel = ttk.Treeview(fereastra, columns=coloane, show="headings")

for col in coloane:
    tabel.heading(col, text=col)
    tabel.column(col, width=100)

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

label_algo = tk.Label(panou_cript, text="Algoritm de criptare:")
label_algo.grid(row=0, column=0, padx=5, pady=5)

combo_alg = ttk.Combobox(panou_cript, values=["AES", "RSA"], state="readonly", width=10)
combo_alg.current(0)
combo_alg.grid(row=0, column=1, padx=5, pady=5)

btn_cripteaza = tk.Button(panou_cript, text="Criptare", command=buton_criptare, bg="lavender", state=tk.DISABLED)
btn_cripteaza.grid(row=0, column=2, padx=10, pady=10)

btn_decripteaza = tk.Button(panou_cript, text="Decriptare", command=buton_decriptare, bg="lavender", state=tk.DISABLED)
btn_decripteaza.grid(row=0, column=3, padx=10, pady=10)

fereastra.mainloop()