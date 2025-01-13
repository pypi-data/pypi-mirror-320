import sys
import time
import threading
from colorama import init, Fore, Style

# Inicializa o suporte a cores no Windows
init(autoreset=True)


class AnimationConsole:
    def __init__(self, text="Loading", color=Fore.GREEN, color_frame=Fore.BLUE):
        """
        Cria uma animação de loading com uma mensagem colorida no console.
        :param text: Texto inicial da mensagem de loading.
        :param color: Cor do texto, usando Fore do colorama.
        """
        self._color_frame = color_frame
        self._text = text
        self._color = color
        self._running = False
        self._animation_thread = None
        self._frames = ["-", "\\", "|", "/"]
        self._index = 0

    def start(self):
        """
        Inicia a animação no console.
        """
        if self._running:
            return  # Previne múltiplas execuções
        self._running = True
        self._animation_thread = threading.Thread(target=self._animate, daemon=True)
        self._animation_thread.start()

    def stop(self):
        """
        Para a animação no console.
        """
        self._running = False
        if self._animation_thread:
            self._animation_thread.join()
        sys.stdout.write("\r" + " " * (len(self._text) + 20) + "\r")  # Limpa a linha

    def update_message(self, new_text, new_color=None):
        """
        Atualiza a mensagem exibida junto à animação.
        :param new_text: Novo texto a ser exibido.
        :param new_color: Nova cor para o texto (opcional).
        """
        self._text = new_text
        if new_color:
            self._color = new_color

    def _animate(self):
        """
        Animação interna do console.
        """
        while self._running:
            frame = self._frames[self._index]
            self._index = (self._index + 1) % len(self._frames)
            sys.stdout.write(
                f"\r{self._color}{self._text}{Style.RESET_ALL} {self._color_frame}{frame}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
