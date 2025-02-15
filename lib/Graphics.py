import curses
import sys

def main(stdscr):
    # Inizializza la finestra
    curses.curs_set(1)  # Mostra il cursore
    stdscr.clear()

    # Definisci l'altezza per la parte di input
    max_y, max_x = stdscr.getmaxyx()
    input_height = 3

    # Crea una finestra per l'input nella parte inferiore
    input_window = curses.newwin(input_height, max_x, max_y - input_height, 0)

    # Loop principale
    while True:
        # Disegna un messaggio nella parte superiore del terminale (normale)
        print("Questa è la parte superiore del terminale.")
        print("Puoi scrivere qualsiasi cosa qui e scrollare normalmente.")
        print("L'area sotto sarà per l'input.")

        # Pulisce la finestra dell'input
        input_window.clear()
        input_window.addstr(1, 1, "Scrivi qui: ")

        # Gestisci l'input da tastiera
        input_window.refresh()

        # Rileva il testo di input
        input_text = ""
        while True:
            key = input_window.getch()
            
            if key == 10:  # Enter
                break
            elif key == 27:  # Escape
                return  # Esce dal programma
            elif key == 127:  # Backspace
                input_text = input_text[:-1]
            else:
                input_text += chr(key)  # Aggiungi il carattere digitato

            # Rimuove la vecchia stringa di input
            input_window.clear()
            input_window.addstr(1, 1, "Scrivi qui: " + input_text)
            input_window.refresh()

        # Mostra il testo di input nel terminale normale (in basso, non tramite curses)
        print(f"Testo immesso: {input_text}")
        print("-" * 40)

# Avvia l'applicazione con curses
if __name__ == "__main__":
    curses.wrapper(main)
