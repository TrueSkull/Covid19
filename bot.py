# Copyright (C) <2020>  <Michele Viotto>
import botogram
import covid
from database import Covid19Database
import json
from datetime import datetime
import os
import schedule, time, threading
import yaml

config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)

bot = botogram.create(config.get('bot_token'))
db = Covid19Database(config.get('database'))

try:
    os.makedirs('grafici/nazionali')
    os.makedirs('grafici/regionali')
except OSError:
    pass


# COMANDI DEL BOT
@bot.command("start")
def start_command(chat, message, args):
    """Avvia il bot e manda il menù principale"""
    db.init()
    db.add_user(message.sender.id)
    chat.send(get_start_message(), attach=get_start_buttons())

@bot.command("help")
def help(chat, message, args):
    chat.send(get_start_message(), attach=get_start_buttons())

# admin menu
@bot.command("admin")
def admin_command(chat, message, args):
    """Mostra il menù per gli admin"""
    db.init()
    if db.is_admin(message.sender.id):
        db.set_setting(message.sender.id, "status", "")
        btns = botogram.Buttons()
        btns[0].callback("Invia messaggio globale", "callback_messaggio_globale")
        btns[1].callback("Chiudi", "callback_chiudi_pannello_admin")
        chat.send(
            "Benvenuto nel pannello admin.\n"
            "Clicca i tasti qui sotto per decidere cosa fare.",
            attach=btns
            )


# CALLBACK DEL BOT
@bot.callback("callback_start")
def callback_start(query, chat, message):
    """Menù principale da tastiera"""
    db.init()
    db.add_user(query.sender.id)
    message.edit(get_start_message(), attach=get_start_buttons())


@bot.callback("callback_ultimi_andamenti")
def callback_ultimi_andamenti(query, chat, message):
    """Menù per scegliere quale ultimo aggiornamento si vuole vedere"""
    btns = botogram.Buttons()
    btns[0].callback("🗄 Nazionale", "callback_ultimo_nazionale")
    btns[1].callback("🗳 Regionale", "callback_ultimo_regionale")
    btns[2].callback("◀️ Indietro", "callback_start")
    message.edit(
        "📂 Scegli quale ultimo andamento vuoi vedere tra *nazionale*"
        " o *regionale* con i *bottoni* qui sotto.", attach=btns
        )


@bot.callback("callback_ultimo_nazionale")
def callback_ultimo_nazionale(query, chat, message):
    """Messaggio per vedere l'ultimo andamento nazionale con numero
        nuovi casi rispetto al giorno precedente"""
    btns = botogram.Buttons()
    btns[0].callback("◀️ Indietro", "callback_ultimi_andamenti")
    # contiene json con tutti i dati dell'ultimo aggiornamento
    aggiornamento = covid.get_andamento_nazionale(latest=True)
    message.edit(get_andamento_message(aggiornamento, True), attach=btns)


# tre bottoni con divisione in tre zone
@bot.callback("callback_ultimo_regionale")
def callback_ultimo_regionale(query, chat, message):
    btns = botogram.Buttons()
    btns[0].callback("Nord", "callback_ultimo_regionale_zona", "nord")
    btns[1].callback("Centro", "callback_ultimo_regionale_zona", "centro")
    btns[2].callback("Sud", "callback_ultimo_regionale_zona", "sud")
    btns[3].callback("◀️ Indietro", "callback_ultimi_andamenti")
    message.edit(
        "🇮🇹 Seleziona dai *tasti* qui sotto la *zona* di cui vuoi vedere le *regioni*.",
        attach=btns
        )


# messaggio con i bottoni delle varie regioni in base alla zona scelta
@bot.callback("callback_ultimo_regionale_zona")
def callback_ultimo_regionale_zona(query, data, chat, message):
    btns = botogram.Buttons()
    regioni = covid.get_regioni()
    btn_line = 0
    for i in range(0, len(regioni[data]), 3):
        for k in range(0, 3):
            try:
                btns[btn_line].callback(
                    regioni[data][i],
                    "callback_ultimo_regione",
                    regioni[data][i] + "_" + data
                )
            except IndexError:
                pass
            i += 1
        btn_line += 1
    btns[btn_line].callback("◀️ Indietro", "callback_ultimo_regionale")

    message.edit(
        "📦 Seleziona dai *tasti* qui sotto la *regione* di cui vuoi vedere i *dati*.",
        attach=btns
    )


# ultimo andamento per singola regione
@bot.callback("callback_ultimo_regione")
def callback_ultimo_regione(query, data, chat, message):
    """Messaggio per vedere l'ultimo andamento regionale con numero
        nuovi casi rispetto al giorno precedente"""
    data = data.split('_') # 0: nome regione, 1: nome zona
    btns = botogram.Buttons()
    btns[0].callback("◀️ Indietro", "callback_ultimo_regionale_zona", data[1])
    # contiene json con tutti i dati dell'ultimo aggiornamento
    regioni = covid.get_andamento_regionale(latest=True)
    text = ""
    for regione in regioni:
        if regione["denominazione_regione"] == data[0]:
            text += (get_andamento_message(regione))

    message.edit(text,attach=btns)


# Info
@bot.callback("callback_bot_info")
def callback_bot_info(query, chat, message):
    btns = botogram.Buttons()
    btns[0].url("🔌 Fork", "https://github.com/xMicky24GIT/covid19ita-telegram-bot")
    btns[1].callback("◀️ Indietro", "callback_start")
    message.edit(
"🤖 Questo *bot* è stato sviluppato in *Python* ed è in continuo *aggiornamento*!\n\n"
"👮‍♂️ *Staff:*\n"
"• @Occupato.",
        attach=btns
        )


# Pannello admin
@bot.callback("callback_pannello_admin")
def callback_pannello_admin(query, chat, message):
    db.init()
    if db.is_admin(query.sender.id):
        db.set_setting(query.sender.id, "status", "")
        btns = botogram.Buttons()
        btns[0].callback("Invia messaggio globale", "callback_messaggio_globale")
        btns[1].callback("Chiudi", "callback_chiudi_pannello_admin")
        message.edit(
            "Benvenuto nel pannello admin.\n"
            "Clicca i tasti qui sotto per decidere cosa fare.",
            attach=btns
            )


@bot.callback("callback_chiudi_pannello_admin")
def callback_chiudi_pannello_admin(query, chat, message):
    message.delete()


@bot.callback("callback_messaggio_globale")
def callback_messaggio_globale(query, chat, message):
    db.init()
    if db.is_admin(query.sender.id):
        btns = botogram.Buttons()
        btns[0].callback("Annulla", "callback_pannello_admin")
        message.edit(
            "Invia ora il messaggio che vuoi inviare a tutti gli utenti.",
            attach=btns
            )
        db.set_setting(query.sender.id, "status", "send_global_message")


@bot.process_message
def send_global_message(chat, message):
    db.init()
    if db.is_admin(message.sender.id):
        if db.get_setting(message.sender.id, "status") == "send_global_message":
            db.set_setting(message.sender.id, "status", "")
            for user in db.get_users():
                bot.chat(user[0]).send(message.text)


# Impostazioni
@bot.callback("callback_impostazioni")
def callback_impostazioni(query, chat, message):
    db.init()
    btns = botogram.Buttons()
    if db.get_setting(query.sender.id, "notifications") == 1:
        btns[0].callback(
            "❌ Disabilita notifiche",
            "callback_impostazioni_notifche",
            "disabilita"
            )
    else:
        btns[0].callback(
            "✅ Abilita notifiche",
            "callback_impostazioni_notifche",
            "abilita"
            )
    btns[1].callback("◀️ Indietro", "callback_start")
    message.edit(
        "🔔 Da qui puoi gestire le varie *impostazioni* del *bot*.\n\n"
        "*Notifiche*: si tratta di un messaggio per *informarti* quando vengono"
        " pubblicati dei nuovi dati dalla *protezione civile*.",
        attach=btns
    )


@bot.callback("callback_impostazioni_notifche")
def callback_impostazioni_notifche(query, data, chat, message):
    db.init()
    if data == "disabilita":
        db.set_setting(query.sender.id, "notifications", 0)
        callback_impostazioni(query, chat, message)
    elif data == "abilita":
        db.set_setting(query.sender.id, "notifications", 1)
        callback_impostazioni(query, chat, message)


# FUNZIONI DI APPOGGIO
def get_start_message():
    return (
        "👋🏻 *Benvenuto!*\n"
        "\n"
        "— Grazie a questo *bot* puoi tenere traccia dell'andamento nazionale e regionale di tutto ciò che riguarda i numeri del *Covid19* in Italia.\n"
        "I dati vengono aggiornati circa alle 18:30 dalla *protezione civile*.\n"
        "Clicca uno dei *pulsanti* qui sotto per iniziare."
    )


def get_start_buttons():
    btns = botogram.Buttons()
    btns[0].callback("⌚️ Ultimi andamenti", "callback_ultimi_andamenti")
    btns[2].callback("ℹ️ Info", "callback_bot_info")
    btns[2].callback("⚙️ Impostazioni", "callback_impostazioni")

    return btns


def get_andamento_message(dati, nazione = False):
    # formatto la data per avere solo giorno-mese-anno
    data = datetime.strptime(dati["data"], "%Y-%m-%dT%H:%M:%S")
    data = data.strftime("%d-%m-%Y")

    return (  
        "_⏱ Last updated:_ _%s_\n\n"
        "Tamponi totali: *%s*\n"
        "Casi totali: *%s*\n"
        "Attualmente positivi: *%s*\n"
        "Totale ospedalizzati: *%s*\n"
        "Deceduti: *%s*\n"
        "Dimessi guariti: *%s*\n"
        "Nuovi casi positivi: *%s*\n"
        % (
            data, format(dati["tamponi"], ',d'),
            format(dati["totale_casi"], ',d'), format(dati["totale_positivi"], ',d'),
            format(dati["totale_ospedalizzati"], ',d'), format(dati["deceduti"], ',d'), format(dati["dimessi_guariti"], ',d'),
            format(dati["nuovi_positivi"], ',d')
            )
        )


# Notifica gli utenti di un update ai dati
def send_notifica():
    db.init()
    covid.create_grafico_cumulativo_nazionale()
    for user in db.get_users():
        if user[1]:
            bot.chat(user[0]).send(
                "🔎 Sono stati resi disponibili nuovi dati.\n"
                "Clicca /start per vederli.",
                )


def schedule_send_notfica():
    schedule.every().day.at("18:30").do(send_notifica)
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    if not os.path.isfile("grafici/nazionali/cumulativo.png"):
        covid.create_grafico_cumulativo_nazionale()
    notifications_thread = threading.Thread(target=schedule_send_notfica, args=())
    notifications_thread.start()
    bot.run()
    notifications_thread.do_run = False
    notifications_thread.join()
