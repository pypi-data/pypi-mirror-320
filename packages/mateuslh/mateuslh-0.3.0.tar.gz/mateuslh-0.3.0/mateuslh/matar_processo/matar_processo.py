import curses
import subprocess
import os

def _obter_apps_abertos():
    try:
        resultado = subprocess.run(['wmctrl', '-lp'], capture_output=True, text=True)
        janelas = resultado.stdout.strip().split('\n')
        apps = []
        
        for janela in janelas:
            partes = janela.split()
            if len(partes) < 5:
                continue
            
            pid = partes[2]
            titulo_janela = " ".join(partes[4:])
            
            # Obtém o nome do aplicativo pelo PID
            try:
                nome_app = subprocess.run(['ps', '-p', pid, '-o', 'comm='], capture_output=True, text=True)
                nome_app = nome_app.stdout.strip()
                apps.append((pid, nome_app, titulo_janela))
            except Exception:
                continue
        
        return apps
    except FileNotFoundError:
        return None

def _exibir_menu(stdscr, apps):
    curses.curs_set(0)
    current_row = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Use as setas para navegar e ENTER para matar o processo. Pressione 'q' para sair.")
        stdscr.addstr(1, 0, "=" * 80)

        for idx, app in enumerate(apps):
            if idx == current_row:
                stdscr.addstr(idx + 2, 0, f"> {app[1]} (PID: {app[0]}) - {app[2]}", curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 2, 0, f"  {app[1]} (PID: {app[0]}) - {app[2]}")

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(apps) - 1:
            current_row += 1
        elif key == ord('q'):
            break
        elif key == 10:  # Enter key
            pid = apps[current_row][0]
            stdscr.addstr(len(apps) + 3, 0, f"Matando o processo {pid}...")
            stdscr.refresh()
            try:
                os.kill(int(pid), 9)  # Envia o sinal SIGKILL
                stdscr.addstr(len(apps) + 4, 0, f"Processo {pid} encerrado com sucesso.")
                stdscr.refresh()
                apps.pop(current_row)
                if current_row >= len(apps):
                    current_row = len(apps) - 1
            except Exception as e:
                stdscr.addstr(len(apps) + 4, 0, f"Erro ao encerrar o processo: {e}")
                stdscr.refresh()
            stdscr.getch()

def run_kill_process():
    apps = _obter_apps_abertos()
    if apps is None:
        print("wmctrl não está instalado. Instale com: sudo apt install wmctrl")
        return
    elif not apps:
        print("Nenhum aplicativo aberto encontrado.")
        return

    curses.wrapper(_exibir_menu, apps)
