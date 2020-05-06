# Copyright (C) <2020>  <Michele Viotto>
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime
import os


def get_andamento_nazionale(latest=False):
    if latest is True:
        r = requests.get('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale-latest.json')
        return r.json()[0]
    else:
        r = requests.get('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json')
        return r.json()


def get_andamento_regionale(latest=False):
    if latest is True:
        r = requests.get('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni-latest.json')
        return r.json()
    else:
        r = requests.get('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni.json')
        return r.json()


def get_regioni():
    """
    Ritorna un dizionario diviso in nord, centro e sud e contine i nomi delle regioni
    """
    regioni = {
        "nord": [],
        "centro": [],
        "sud": []
    }
    for regione in get_andamento_regionale(latest=True):
        if regione['codice_regione'] <= 8:
            regioni['nord'].append(regione['denominazione_regione'])
        elif 9 <= regione['codice_regione'] <=13:
            regioni['centro'].append(regione['denominazione_regione'])
        else:
            regioni['sud'].append(regione['denominazione_regione'])

    return regioni


# grafico andamento positivi totali nazionale
def create_grafico_andamento_nazionale():
    plt.figure(figsize=(10, 6.3))
    xs = []
    ys = []
    ultimi_positivi = ""
    variazione_positivi = ""
    for giorno in get_andamento_nazionale():
        data = datetime.strptime(giorno["data"], "%Y-%m-%dT%H:%M:%S")
        data = data.strftime("%d-%m")
        xs.append(data)
        ultimi_positivi = format(giorno["totale_positivi"], ',d')
        variazione_positvi = format(giorno["variazione_totale_positivi"], ',d')
        ys.append(giorno["totale_positivi"])
    plt.plot(xs, ys)
    plt.xlabel('Giorno-Mese')
    plt.xticks(rotation=90)
    plt.ylabel('Totale positivi')
    plt.title(f"Totale attualmente positivi in Italia: {ultimi_positivi} [ {variazione_positvi} ]")
    plt.grid(axis='y')
    plt.savefig('grafici/nazionali/totali_positivi.png')

    return ys  # così posso richiamare la funzione nel grafico cumulativo


# grafico nuovi positivi giornalieri nazionale
def create_grafico_nuovi_positivi_nazionale():
    plt.figure(figsize=(15, 6.3))
    xs = []
    ys = []

    for giorno in get_andamento_nazionale():
        data = datetime.strptime(giorno["data"], "%Y-%m-%dT%H:%M:%S")
        data = data.strftime("%d-%m")
        xs.append(data)
        ys.append(giorno["nuovi_positivi"])

    plt.plot(xs, ys, marker='.')

    # aggiungere numero positivi ad ogni punto
    for x, y in zip(xs, ys):
        label = "{:,d}".format(y)
        plt.annotate(
            label, # text
            (x, y), # punto in cui viene aggiunta la label
            textcoords="offset points",
            xytext=(0, 10),
            ha="center"
            )

    plt.xlabel('Giorno-Mese')
    plt.xticks(rotation=90)
    plt.ylabel('Nuovi positivi')
    plt.title('Nuovi positivi in Italia')
    plt.savefig('grafici/nazionali/nuovi_positivi.png')

    return ys  # così posso richiamare la funzione nel grafico cumulativo


# grafico totale deceduti nazionale
def create_grafico_totale_deceduti_nazionale():
    plt.figure(figsize=(10, 6.3))
    xs = []
    ys = []
    ultimi_deceduti = ""

    for giorno in get_andamento_nazionale():
        data = datetime.strptime(giorno["data"], "%Y-%m-%dT%H:%M:%S")
        data = data.strftime("%d-%m")
        xs.append(data)
        ultimi_deceduti = format(giorno["deceduti"], ',d')
        ys.append(giorno["deceduti"])

    plt.plot(xs, ys)
    plt.xlabel('Giorno-Mese')
    plt.xticks(rotation=90)
    plt.ylabel('Totale decessi')
    plt.title('Totale deceduti in Italia: %s' % ultimi_deceduti)
    plt.savefig('grafici/nazionali/totale_deceduti.png')

    return ys  # così posso richiamare la funzione nel grafico cumulativo


# grafico cumulativo nazionale
def create_grafico_cumulativo_nazionale():
    xs = []
    ys_casi_totali = []
    ys_dimessi = []
    ys_attualmente_positivi = create_grafico_andamento_nazionale()
    ys_nuovi_positivi = create_grafico_nuovi_positivi_nazionale()
    ys_totale_deceduti = create_grafico_totale_deceduti_nazionale()

    for giorno in get_andamento_nazionale():
        data = datetime.strptime(giorno["data"], "%Y-%m-%dT%H:%M:%S")
        data = data.strftime("%d-%m")
        xs.append(data)
        ys_casi_totali.append(giorno["totale_casi"])
        ys_dimessi.append(giorno["dimessi_guariti"])

    plt.plot(xs, ys_casi_totali, label='Casi totali')
    plt.plot(xs, ys_attualmente_positivi, label='Attualmente positivi')
    plt.plot(xs, ys_nuovi_positivi, label='Nuovi positivi')
    plt.plot(xs, ys_totale_deceduti, label='Totale decessi')
    plt.plot(xs, ys_dimessi, label='Totale dimessi')

    plt.legend(loc='upper left')

    plt.xlabel('Giorno-Mese')
    plt.xticks(rotation=90)
    plt.title('Grafico cumulativo Covid-19 Italia')
    plt.savefig('grafici/nazionali/cumulativo.png')

    return
