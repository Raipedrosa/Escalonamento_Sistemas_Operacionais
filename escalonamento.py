import tkinter as tk
from tkinter import scrolledtext, ttk
from collections import deque

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

gantt_resultados = {}


def atualizar_grafico(titulo, execucoes):
    ax.clear()

    cores = {
        "P1": "skyblue",
        "P2": "lightgreen",
        "P3": "salmon"
    }

    tempos = set()

    for processo, inicio, duracao in execucoes:
        fim = inicio + duracao
        tempos.add(inicio)
        tempos.add(fim)

        ax.barh(
            y=0,
            width=duracao,
            left=inicio,
            height=0.5,
            color=cores.get(processo, "gray"),
            edgecolor="black"
        )
        ax.text(
            inicio + duracao / 2,
            0,
            processo,
            ha="center",
            va="center",
            fontweight="bold"
        )
### Marcações verticais nos instantes de início/fim de cada execução ###

    for t in sorted(tempos):
        ax.axvline(x=t, color="gray", linestyle="--", linewidth=0.7)

    ax.set_xticks(sorted(tempos))
    ax.set_title(titulo)
    ax.set_xlabel("Tempo")
    ax.set_yticks([])
    ax.set_xlim(left=0)

    fig.tight_layout()
    canvas.draw()



### Chamado ao clicar em um botão de algoritmo dentro de uma aba de cenário ###

def mostrar_grafico(chave):
    if chave in gantt_resultados:
        atualizar_grafico(chave, gantt_resultados[chave])
    else:
        ax.clear()
        ax.text(
            0.5, 0.5,
            "Clique em 'Executar Simulação' primeiro.",
            ha="center", va="center"
        )
        ax.set_xticks([])
        ax.set_yticks([])
        canvas.draw()



# Exibe resultados na área de texto e na tabela (Treeview)

def mostrar_resultados(nome_cenario, nome_algoritmo, resultados):
    texto.insert("end", f"\n=== {nome_cenario} | {nome_algoritmo} ===\n")
    texto.insert("end", "Processo | Espera | Término\n")

    soma = 0

    for r in resultados:
        texto.insert(
            "end",
            f"{r['nome']:8} | {r['espera']:6} | {r['termino']:7}\n"
        )
        soma += r["espera"]

        tabela.insert(
            "", "end",
            values=(nome_cenario, nome_algoritmo, r["nome"], r["espera"], r["termino"])
        )

    media = soma / len(resultados)
    texto.insert("end", f"Tempo médio de espera: {media:.2f}\n")
    texto.see("end")



############## FCFS ##############

def fcfs(processos):
    tempo = 0
    resultados = []
    gantt = []

    for p in processos:
        inicio = tempo
        espera = tempo
        tempo += p["cpu"]

        gantt.append((p["nome"], inicio, p["cpu"]))
        resultados.append({"nome": p["nome"], "espera": espera, "termino": tempo})

    return resultados, gantt


############## SJF ##############

def sjf(processos):
    ordenados = sorted(processos, key=lambda p: p["cpu"])

    tempo = 0
    resultados = []
    gantt = []

    for p in ordenados:
        inicio = tempo
        espera = tempo
        tempo += p["cpu"]

        gantt.append((p["nome"], inicio, p["cpu"]))
        resultados.append({"nome": p["nome"], "espera": espera, "termino": tempo})

    return resultados, gantt



### Prioridade (menor número = maior prioridade) ###

def prioridade(processos):
    ordenados = sorted(processos, key=lambda p: p["prioridade"])

    tempo = 0
    resultados = []
    gantt = []

    for p in ordenados:
        inicio = tempo
        espera = tempo
        tempo += p["cpu"]

        gantt.append((p["nome"], inicio, p["cpu"]))
        resultados.append({"nome": p["nome"], "espera": espera, "termino": tempo})

    return resultados, gantt



# ############## Round Robin ##############

def round_robin(processos, quantum):
    fila = deque()

    for p in processos:
        fila.append({"nome": p["nome"], "cpu": p["cpu"], "restante": p["cpu"]})

    tempo = 0
    gantt = []
    tempos_termino = {}

    while fila:
        atual = fila.popleft()
        inicio = tempo

        execucao = min(quantum, atual["restante"])
        tempo += execucao

        gantt.append((atual["nome"], inicio, execucao))
        atual["restante"] -= execucao

        if atual["restante"] == 0:
            tempos_termino[atual["nome"]] = tempo
        else:
            fila.append(atual)

    resultados = []
    for p in processos:
        termino = tempos_termino[p["nome"]]
        espera = termino - p["cpu"]
        resultados.append({"nome": p["nome"], "espera": espera, "termino": termino})

    return resultados, gantt



########## CENÁRIOS DO TRABALHO ##########

cenario1 = [
    {"nome": "P1", "cpu": 3, "prioridade": 1},
    {"nome": "P2", "cpu": 1, "prioridade": 1},
    {"nome": "P3", "cpu": 2, "prioridade": 1}
]

cenario2 = [
    {"nome": "P1", "cpu": 8, "prioridade": 1},
    {"nome": "P2", "cpu": 2, "prioridade": 1},
    {"nome": "P3", "cpu": 1, "prioridade": 1}
]

cenario3 = [
    {"nome": "P1", "cpu": 4, "prioridade": 3},
    {"nome": "P2", "cpu": 2, "prioridade": 1},
    {"nome": "P3", "cpu": 3, "prioridade": 2}
]

QUANTUM = 2

cenarios = [
    ("CENÁRIO 1 - Processos Curtos", cenario1),
    ("CENÁRIO 2 - Curtos e Longos", cenario2),
    ("CENÁRIO 3 - Prioridades Diferentes", cenario3)
]

ALGORITMOS = [
    ("FCFS", lambda procs: fcfs(procs)),
    ("SJF", lambda procs: sjf(procs)),
    ("PRIORIDADE", lambda procs: prioridade(procs)),
    (f"ROUND ROBIN (q={QUANTUM})", lambda procs: round_robin(procs, QUANTUM)),
]



########## Executar Algoritimos ###########

def executar_simulacao():
    texto.delete("1.0", "end")
    for item in tabela.get_children():
        tabela.delete(item)
    gantt_resultados.clear()

    for nome_cenario, dados in cenarios:
        for nome_algoritmo, funcao in ALGORITMOS:
            resultados, gantt = funcao(dados)
            mostrar_resultados(nome_cenario, nome_algoritmo, resultados)

            chave = f"{nome_cenario} | {nome_algoritmo}"
            gantt_resultados[chave] = gantt

    texto.insert("end", "\nSimulação concluída. Clique em uma aba de cenário e depois em um algoritmo para ver o gráfico.\n")

    
    primeira_chave = f"{cenarios[0][0]} | {ALGORITMOS[0][0]}"
    mostrar_grafico(primeira_chave)



######## INTERFACE VISUAL GRÁFICA (TKINTER) ########

janela = tk.Tk()
janela.title("Escalonamento de Processos")
janela.geometry("1000x850")


painel_controles = ttk.Frame(janela)
painel_controles.pack(fill="x", padx=10, pady=10)

btn_executar = ttk.Button(
    painel_controles,
    text="Executar Simulação",
    command=executar_simulacao
)
btn_executar.pack(side="left")


texto = scrolledtext.ScrolledText(janela, font=("Consolas", 10), height=10)
texto.pack(fill="both", expand=False, padx=10, pady=(0, 10))


tabela = ttk.Treeview(
    janela,
    columns=("cenario", "algoritmo", "processo", "espera", "termino"),
    show="headings",
    height=6
)

tabela.heading("cenario", text="Cenário")
tabela.heading("algoritmo", text="Algoritmo")
tabela.heading("processo", text="Processo")
tabela.heading("espera", text="Tempo de Espera")
tabela.heading("termino", text="Tempo de Término")

tabela.column("cenario", width=220)
tabela.column("algoritmo", width=160)
tabela.column("processo", width=80, anchor="center")
tabela.column("espera", width=110, anchor="center")
tabela.column("termino", width=110, anchor="center")

tabela.pack(fill="both", expand=False, padx=10, pady=(0, 10))


ttk.Label(janela, text="Selecione o cenário e o algoritmo para ver o gráfico de Gantt:").pack(
    anchor="w", padx=10
)

notebook = ttk.Notebook(janela)
notebook.pack(fill="x", padx=10, pady=(5, 10))

for nome_cenario, dados in cenarios:
    aba = ttk.Frame(notebook)
    notebook.add(aba, text=nome_cenario.split(" - ")[0])  

    for nome_algoritmo, _ in ALGORITMOS:
        chave = f"{nome_cenario} | {nome_algoritmo}"
        btn = ttk.Button(
            aba,
            text=nome_algoritmo,
            command=lambda c=chave: mostrar_grafico(c)
        )
        btn.pack(side="left", padx=5, pady=8)


fig, ax = plt.subplots(figsize=(8, 2.5))
fig.tight_layout()

canvas = FigureCanvasTkAgg(fig, master=janela)
canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))


mostrar_grafico("")

janela.mainloop()