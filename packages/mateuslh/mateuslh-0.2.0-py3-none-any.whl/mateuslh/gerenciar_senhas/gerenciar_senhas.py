import os
import sqlite3
import curses
import subprocess

DATABASE = os.path.join(os.path.dirname(__file__), "clipboard_database.sqlite")

def _inicializar_banco():
    if not os.path.isfile(DATABASE):
        with sqlite3.connect(DATABASE) as conn:
            conn.execute("""
                CREATE TABLE registros (
                    chave TEXT PRIMARY KEY,
                    valor TEXT
                )
            """)
_inicializar_banco()

def _adicionar_registro(chave, valor):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute("INSERT INTO registros (chave, valor) VALUES (?, ?)", (chave, valor))
        return f"Registro '{chave}' adicionado!"
    except sqlite3.IntegrityError:
        return f"Erro: A chave '{chave}' já existe!"

def _listar_registros():
    with sqlite3.connect(DATABASE) as conn:
        return [row[0] for row in conn.execute("SELECT chave FROM registros")]

def _copiar_para_area_transferencia(chave):
    with sqlite3.connect(DATABASE) as conn:
        row = conn.execute("SELECT valor FROM registros WHERE chave = ?", (chave,)).fetchone()
        if row:
            subprocess.run(['xclip', '-selection', 'clipboard'], input=row[0].encode())
            return f"Registro '{chave}' copiado para a área de transferência!"
        return f"Registro '{chave}' não encontrado!"

def _deletar_registro(chave):
    with sqlite3.connect(DATABASE) as conn:
        result = conn.execute("DELETE FROM registros WHERE chave = ?", (chave,))
        return f"Registro '{chave}' deletado!" if result.rowcount > 0 else f"Registro '{chave}' não encontrado!"

def _menu_curses(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    current_row = 0
    menu = ["Incluir Registro", "Listar Registros", "Deletar Registro", "Sair"]
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        for idx, row in enumerate(menu):
            x = w // 2 - len(row) // 2
            y = h // 2 - len(menu) // 2 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, row)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(y, x, row)
                stdscr.attroff(curses.color_pair(2))
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if menu[current_row] == "Incluir Registro":
                _incluir_registro(stdscr)
            elif menu[current_row] == "Listar Registros":
                _listar_registros_curses(stdscr)
            elif menu[current_row] == "Deletar Registro":
                _deletar_registro_curses(stdscr)
            elif menu[current_row] == "Sair":
                break

def _incluir_registro(stdscr):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, "Digite a chave: ")
    chave = stdscr.getstr(1, 0).decode()
    stdscr.addstr(2, 0, "Digite o valor: ")
    valor = stdscr.getstr(3, 0).decode()
    mensagem = _adicionar_registro(chave, valor)
    stdscr.addstr(5, 0, mensagem)
    stdscr.addstr(6, 0, "Pressione qualquer tecla para voltar ao menu.")
    stdscr.getch()

def _listar_registros_curses(stdscr):
    registros = _listar_registros()
    current_row = 0
    while True:
        stdscr.clear()
        for idx, registro in enumerate(registros, start=1):
            if idx - 1 == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(idx, 0, registro)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(idx, 0, registro)
                stdscr.attroff(curses.color_pair(2))
        stdscr.addstr(len(registros) + 1, 0, "Pressione Enter para copiar ou ESC para sair.")
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(registros) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            mensagem = _copiar_para_area_transferencia(registros[current_row])
            stdscr.clear()
            stdscr.addstr(0, 0, mensagem)
            stdscr.addstr(2, 0, "Pressione qualquer tecla para voltar ao menu.")
            stdscr.getch()
            break
        elif key == 27:
            break

def _deletar_registro_curses(stdscr):
    registros = _listar_registros()
    current_row = 0
    while True:
        stdscr.clear()
        for idx, registro in enumerate(registros, start=1):
            if idx - 1 == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(idx, 0, registro)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(idx, 0, registro)
                stdscr.attroff(curses.color_pair(2))
        stdscr.addstr(len(registros) + 1, 0, "Pressione Enter para deletar ou ESC para sair.")
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(registros) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            mensagem = _deletar_registro(registros[current_row])
            stdscr.clear()
            stdscr.addstr(0, 0, mensagem)
            stdscr.addstr(2, 0, "Pressione qualquer tecla para voltar ao menu.")
            stdscr.getch()
            break
        elif key == 27:
            break

def run_password_manager():
    curses.wrapper(_menu_curses)


if __name__ == "__main__":
    run_password_manager()