from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import TextArea, Box, Label
from prompt_toolkit.layout import HSplit, VSplit, Window
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document

import random
import time

# Funzione per generare un output casuale
def generate_output():
    return f"Output casuale: {random.randint(1, 100)}"

# Funzione che si occupa dell'output che scorre
def update_output(output_area, output_buffer):
    while True:
        time.sleep(1)
        output_buffer.insert_text(generate_output() + '\n', cursor_position=0)
        output_area.render()

# Creazione della finestra di output
output_buffer = Buffer()
output_area = Window(content=output_buffer)

# Creazione della finestra di input
input_buffer = Buffer(multiline=False, complete_while_typing=True)
input_area = TextArea(buffer=input_buffer, height=3)

# Layout dell'applicazione con una finestra di output che scorre e una finestra di input fissa
root_container = HSplit([
    output_area,
    input_area,
])

# Funzioni per gestire l'input dell'utente (puoi aggiungere delle azioni personalizzate)
def handle_input(event):
    text = input_buffer.text
    print(f"Input ricevuto: {text}")
    input_buffer.clear()

# Creazione dei Keybindings
kb = KeyBindings()
kb.add('c-c')(lambda event: event.app.exit())  # Ctrl+C per uscire

# Applicazione
application = Application(
    layout=root_container,
    key_bindings=kb,
    full_screen=True
)

# Avvia l'aggiornamento dell'output in un thread separato
import threading
thread = threading.Thread(target=update_output, args=(output_area, output_buffer))
thread.daemon = True
thread.start()

# Avvia l'applicazione
application.run()
