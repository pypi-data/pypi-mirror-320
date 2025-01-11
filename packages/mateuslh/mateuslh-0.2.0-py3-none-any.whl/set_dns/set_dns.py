import curses
import subprocess


def _solicitar_senha(stdscr):
    curses.noecho()
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    mensagem = "Digite a senha do sudo:"
    x = w // 2 - len(mensagem) // 2
    y = h // 2 - 1
    stdscr.addstr(y, x, mensagem, curses.A_BOLD)
    stdscr.addstr(y + 2, x, "Pressione Enter após digitar a senha.")
    stdscr.refresh()
    stdscr.move(y + 1, x)
    senha = stdscr.getstr(y + 1, x, 20).decode('utf-8')
    curses.echo()
    return senha


def _copiar_dns_vpn(stdscr):
    senha = _solicitar_senha(stdscr)
    comando = f'echo {senha} | sudo -S cp /etc/resolv.dns-vpn.conf /etc/resolv.conf'
    resultado = subprocess.run(comando, shell=True, text=True, capture_output=True)
    if resultado.returncode == 0:
        return "Configuração DNS VPN aplicada com sucesso!"
    else:
        return f"Erro ao aplicar configuração DNS VPN: {resultado.stderr}"


def _copiar_dns_geral(stdscr):
    senha = _solicitar_senha(stdscr)
    comando = f'echo {senha} | sudo -S cp /etc/resolv.dns-geral.conf /etc/resolv.conf'
    resultado = subprocess.run(comando, shell=True, text=True, capture_output=True)
    if resultado.returncode == 0:
        return "Configuração DNS Geral aplicada com sucesso!"
    else:
        return f"Erro ao aplicar configuração DNS Geral: {resultado.stderr}"


def _menu_curses(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

    current_row = 0
    menu = ["DNS VPN", "DNS Geral", "Sair"]

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 0, "Escolha a configuração de DNS:", curses.A_BOLD)
        stdscr.attroff(curses.color_pair(1))

        for idx, row in enumerate(menu):
            x = w // 2 - len(row) // 2
            y = h // 2 - len(menu) // 2 + idx + 2
            if idx == current_row:
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(y, x, row)
                stdscr.attroff(curses.color_pair(2))
            else:
                stdscr.addstr(y, x, row)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if menu[current_row] == "DNS VPN":
                mensagem = _copiar_dns_vpn(stdscr)
                stdscr.clear()
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(0, 0, mensagem, curses.A_BOLD)
                stdscr.attroff(curses.color_pair(1))
                stdscr.addstr(2, 0, "Pressione qualquer tecla para voltar ao menu.")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == "DNS Geral":
                mensagem = _copiar_dns_geral(stdscr)
                stdscr.clear()
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(0, 0, mensagem, curses.A_BOLD)
                stdscr.attroff(curses.color_pair(1))
                stdscr.addstr(2, 0, "Pressione qualquer tecla para voltar ao menu.")
                stdscr.refresh()
                stdscr.getch()
            elif menu[current_row] == "Sair":
                break


def run_dns_manager():
    curses.wrapper(_menu_curses)
