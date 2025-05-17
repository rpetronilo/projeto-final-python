import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

def conectar():
    return sqlite3.connect('advocacia.db')

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colaborador_id INTEGER,
            cliente TEXT NOT NULL,
            descricao TEXT NOT NULL,
            data TEXT NOT NULL,
            horas REAL NOT NULL,
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
        )
    ''')
    conn.commit()
    conn.close()

def inserir_colaborador():
    nome = entry_colaborador.get()
    if nome:
        conn = conectar()
        c = conn.cursor()
        c.execute('INSERT INTO colaboradores (nome) VALUES (?)', (nome,))
        conn.commit()
        conn.close()
        entry_colaborador.delete(0, tk.END)
        atualizar_colaboradores()
        messagebox.showinfo('Sucesso', 'Colaborador cadastrado.')
    else:
        messagebox.showerror('Erro', 'Informe o nome do colaborador.')

def atualizar_colaboradores():
    conn = conectar()
    c = conn.cursor()
    c.execute('SELECT id, nome FROM colaboradores')
    colaboradores = c.fetchall()
    combo_colaborador['values'] = [f"{c[0]} - {c[1]}" for c in colaboradores]
    conn.close()

def registrar_tarefa():
    colab_text = combo_colaborador.get()
    cliente = entry_cliente.get()
    descricao = entry_descricao.get()
    data = entry_data.get()
    horas = entry_horas.get()

    if colab_text and cliente and descricao and data and horas:
        try:
            horas = float(horas)
            colab_id = int(colab_text.split(" - ")[0])
            conn = conectar()
            c = conn.cursor()
            c.execute('''
                INSERT INTO tarefas (colaborador_id, cliente, descricao, data, horas)
                VALUES (?, ?, ?, ?, ?)
            ''', (colab_id, cliente, descricao, data, horas))
            conn.commit()
            conn.close()
            messagebox.showinfo('Sucesso', 'Tarefa registrada.')
            mostrar_tarefas()
        except ValueError:
            messagebox.showerror('Erro', 'Horas deve ser um número.')
    else:
        messagebox.showerror('Erro', 'Preencha todos os campos.')

def mostrar_tarefas():
    for row in tree.get_children():
        tree.delete(row)
    conn = conectar()
    c = conn.cursor()
    c.execute('''
        SELECT t.id, c.nome, t.cliente, t.descricao, t.data, t.horas
        FROM tarefas t
        JOIN colaboradores c ON t.colaborador_id = c.id
    ''')
    tarefas = c.fetchall()
    for tarefa in tarefas:
        tree.insert('', 'end', values=tarefa)
    conn.close()

def calcular_total():
    periodo = combo_periodo.get()
    query = '''
        SELECT SUM(horas)
        FROM tarefas
        WHERE strftime(?, data) = strftime(?, date('now'))
    '''
    formato = {
        'Hoje': '%Y-%m-%d',
        'Esta Semana': '%W',
        'Este Mês': '%m'
    }

    if periodo in formato:
        conn = conectar()
        c = conn.cursor()
        c.execute(query, (formato[periodo], formato[periodo]))
        total = c.fetchone()[0]
        conn.close()
        label_resultado.config(text=f"Total de horas ({periodo}): {total or 0:.2f}")
    else:
        messagebox.showwarning('Aviso', 'Selecione um período válido.')

# INTERFACE GRÁFICA
janela = tk.Tk()
janela.title("Controle de Horas - Advocacia & Associados")

# Cadastro de colaborador
frame1 = tk.LabelFrame(janela, text="Cadastrar Colaborador")
frame1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
entry_colaborador = tk.Entry(frame1)
entry_colaborador.pack(side=tk.LEFT, padx=5, pady=5)
btn_add_colaborador = tk.Button(frame1, text="Adicionar", command=inserir_colaborador)
btn_add_colaborador.pack(side=tk.LEFT, padx=5)

# Registro de tarefas
frame2 = tk.LabelFrame(janela, text="Registrar Tarefa")
frame2.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

tk.Label(frame2, text="Colaborador:").grid(row=0, column=0)
combo_colaborador = ttk.Combobox(frame2)
combo_colaborador.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame2, text="Cliente:").grid(row=1, column=0)
entry_cliente = tk.Entry(frame2)
entry_cliente.grid(row=1, column=1)

tk.Label(frame2, text="Descrição:").grid(row=2, column=0)
entry_descricao = tk.Entry(frame2)
entry_descricao.grid(row=2, column=1)

tk.Label(frame2, text="Data (YYYY-MM-DD):").grid(row=3, column=0)
entry_data = tk.Entry(frame2)
entry_data.grid(row=3, column=1)
entry_data.insert(0, datetime.now().strftime('%Y-%m-%d'))

tk.Label(frame2, text="Horas trabalhadas:").grid(row=4, column=0)
entry_horas = tk.Entry(frame2)
entry_horas.grid(row=4, column=1)

btn_salvar_tarefa = tk.Button(frame2, text="Salvar Tarefa", command=registrar_tarefa)
btn_salvar_tarefa.grid(row=5, column=0, columnspan=2, pady=10)

# Lista de tarefas
columns = ('ID', 'Colaborador', 'Cliente', 'Descrição', 'Data', 'Horas')
tree = ttk.Treeview(janela, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=2, column=0, padx=10, pady=10)

# Relatórios
frame3 = tk.LabelFrame(janela, text="Relatórios")
frame3.grid(row=3, column=0, padx=10, pady=10)

combo_periodo = ttk.Combobox(frame3, values=["Hoje", "Esta Semana", "Este Mês"])
combo_periodo.grid(row=0, column=0, padx=5, pady=5)
btn_calcular = tk.Button(frame3, text="Calcular Horas", command=calcular_total)
btn_calcular.grid(row=0, column=1, padx=5)
label_resultado = tk.Label(frame3, text="Total de horas: 0")
label_resultado.grid(row=1, column=0, columnspan=2)

criar_tabelas()
atualizar_colaboradores()
mostrar_tarefas()

janela.mainloop()
