import curses

from gerenciar_senhas import run_password_manager
from matar_processo import run_kill_process
from set_dns import run_dns_manager

def _menu(stdscr):
    stdscr.clear()

    options = ["Gerenciar Senhas", "Matar Processo", "Configurar DNS", "Sair"]
    current_option = 0

    while True:
        for idx, option in enumerate(options):
            if idx == current_option:
                stdscr.addstr(idx, 0, option, curses.A_REVERSE)
            else:
                stdscr.addstr(idx, 0, option)
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(options) - 1:
            current_option += 1
        elif key == 10:
            if current_option == 0:
                run_password_manager()
            elif current_option == 1:
                run_kill_process()
            elif current_option == 2:
                run_dns_manager()
            elif current_option == 3:
                exit(0)
        elif key == 27:
            break

def mateuslh():
    curses.wrapper(_menu)

if __name__ == '__main__':
    mateuslh()