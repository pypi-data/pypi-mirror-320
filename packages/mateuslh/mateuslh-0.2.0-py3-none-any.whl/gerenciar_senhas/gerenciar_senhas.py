import os
import curses
import subprocess

DATABASE = os.path.join(os.path.dirname(__file__), ".clipboard_database")
if not os.path.isfile(DATABASE):
    open(DATABASE, 'w').close()


def _adicionar_registro(chave, valor):
    with open(DATABASE, 'a') as db:
        db.write(f"{chave}={valor}\n")
    return f"Registro '{chave}' adicionado!"


def _listar_registros():
    with open(DATABASE, 'r') as db:
        return [linha.split('=')[0] for linha in db]


def _copiar_para_area_transferencia(chave):
    valor = None
    with open(DATABASE, 'r') as db:
        for linha in db:
            if linha.startswith(f"{chave}="):
                valor = linha.split('=', 1)[1].strip()
                break
    if valor:
        subprocess.run(['xclip', '-selection', 'clipboard'], input=valor.encode())
        return f"Registro '{chave}' copiado para a área de transferência!"
    else:
        return f"Registro '{chave}' não encontrado!"


def _deletar_registro(chave):
    registros = []
    with open(DATABASE, 'r') as db:
        registros = db.readlines()

    with open(DATABASE, 'w') as db:
        for linha in registros:
            if not linha.startswith(f"{chave}="):
                db.write(linha)

    return f"Registro '{chave}' deletado!"


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
    stdscr.clear()
    stdscr.addstr(0, 0, "Registros disponíveis:")
    while True:
        for idx, registro in enumerate(registros, start=1):
            if idx - 1 == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(idx, 0, registro)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(idx, 0, registro)
                stdscr.attroff(curses.color_pair(2))

        stdscr.addstr(len(registros) + 1, 0, "Pressione Enter para copiar ou seta para deletar o registro.")
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(registros) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # Copiar para área de transferência
            chave = registros[current_row]
            mensagem = _copiar_para_area_transferencia(chave)
            stdscr.clear()
            stdscr.addstr(0, 0, mensagem)
            stdscr.addstr(2, 0, "Pressione qualquer tecla para voltar ao menu.")
            stdscr.refresh()
            stdscr.getch()
            break
        elif key == 27:  # Escape para sair
            break


def _deletar_registro_curses(stdscr):
    registros = _listar_registros()
    current_row = 0
    stdscr.clear()
    stdscr.addstr(0, 0, "Selecione o registro para deletar:")
    while True:
        for idx, registro in enumerate(registros, start=1):
            if idx - 1 == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(idx, 0, registro)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(idx, 0, registro)
                stdscr.attroff(curses.color_pair(2))

        stdscr.addstr(len(registros) + 1, 0, "Pressione Enter para deletar ou qualquer tecla para voltar.")
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(registros) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:

            chave = registros[current_row]
            mensagem = _deletar_registro(chave)
            stdscr.clear()
            stdscr.addstr(0, 0, mensagem)
            stdscr.addstr(2, 0, "Pressione qualquer tecla para voltar ao menu.")
            stdscr.refresh()
            stdscr.getch()
            break
        elif key == 27:
            break


def run_password_manager():
    curses.wrapper(_menu_curses)
