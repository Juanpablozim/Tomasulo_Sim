"""
Simulador do algoritmo de Tomasulo
Projeto acadêmico para a disciplina de Arquitetura de Computadores
"""

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
import subprocess
import sys

# ------------
# MAIN
# ------------
def main():
    """Iniciar a interface gráfica do simulador Tomasulo."""
    app = QApplication(sys.argv)
    
    # Definir metadados da aplicação
    app.setApplicationName("Simulador Tomasulo")
    app.setOrganizationName("AC3 - Trabalho2")
    
    # Criar e mostrar a janela principal
    window = MainWindow()
    window.show()
    
    # Iniciar o loop de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()