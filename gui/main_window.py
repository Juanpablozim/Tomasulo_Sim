from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QFileDialog, QGridLayout, QHeaderView, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.simulator.tomasulo_engine import TomasuloEngine
from src.simulator.instruction import parse_mips

# ============= COLOR CONSTANTS =============
# Main colors
COLOR_BACKGROUND = "#f5f5f5"
COLOR_WHITE = "#ffffff"
COLOR_TEXT_PRIMARY = "#2c3e50"
COLOR_TEXT_SECONDARY = "#7f8c8d"

# Button colors
COLOR_BTN_LOAD = "#2ecc71"
COLOR_BTN_LOAD_HOVER = "#27ae60"
COLOR_BTN_LOAD_PRESSED = "#1e8449"

COLOR_BTN_STEP = "#3498db"
COLOR_BTN_STEP_HOVER = "#2980b9"
COLOR_BTN_STEP_PRESSED = "#21618c"

COLOR_BTN_RUN = "#e74c3c"
COLOR_BTN_RUN_HOVER = "#c0392b"
COLOR_BTN_RUN_PRESSED = "#a93226"

COLOR_BTN_BACK = "#f39c12"
COLOR_BTN_BACK_HOVER = "#d68910"
COLOR_BTN_BACK_PRESSED = "#b9770e"

COLOR_BTN_RESET = "#95a5a6"
COLOR_BTN_RESET_HOVER = "#7f8c8d"
COLOR_BTN_RESET_PRESSED = "#707b7c"

COLOR_BTN_DISABLED = "#bdc3c7"

# Table colors
COLOR_TABLE_BORDER = "#e0e0e0"
COLOR_TABLE_HEADER = "#34495e"
COLOR_TABLE_GRIDLINE = "#ecf0f1"

# Highlight colors for tables
COLOR_RS_BUSY = "#7a2822"  # Yellow for busy RS
COLOR_ROB_HEAD = "#118611"  # Green for HEAD
COLOR_ROB_TAIL = "#1d5469"  # Blue for TAIL
COLOR_ROB_READY = "#ffcc00"  # Yellow for ready to commit
COLOR_ROB_EXECUTING = "#4d4d4d"  # Gray for executing

# Register colors
COLOR_REG_NORMAL_BG = "#ffffff"
COLOR_REG_NORMAL_BORDER = "#e0e0e0"
COLOR_REG_NORMAL_TEXT = "#2c3e50"

COLOR_REG_WAITING_BG = "#ffcccc"
COLOR_REG_WAITING_BORDER = "#ff6666"
COLOR_REG_WAITING_TEXT = "#cc0000"

# Console colors
COLOR_CONSOLE_BG = "#282c34"
COLOR_CONSOLE_TEXT = "#ffffff"
COLOR_CONSOLE_BORDER = "#21252b"


class MainWindow(QMainWindow):
    """
    Simple PyQt6 GUI for Tomasulo simulator.
    Shows RS, ROB, registers with step-by-step execution.
    """
    
    def __init__(self):
        super().__init__()
        self.engine = TomasuloEngine()
        self.current_program_path = None
        
        # Extend registers to 32
        while len(self.engine.registers) < 32:
            self.engine.registers.append(0)
        while len(self.engine.reg_status) < 32:
            self.engine.reg_status.append(None)
            
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Simulador Tomasulo - Trabalho AC3")
        self.setGeometry(100, 100, 1600, 900)
        
        # Set modern color scheme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_BACKGROUND};
            }}
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # === CONTROL BUTTONS ===
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_load = QPushButton("CARREGAR PROGRAMA")
        self.btn_step = QPushButton("STEP ->")
        self.btn_run = QPushButton("RUN")
        self.btn_step_back = QPushButton("<- STEP BACK")
        self.btn_reset = QPushButton("RESETAR")
        
        self.btn_load.clicked.connect(self.load_program)
        self.btn_step.clicked.connect(self.step)
        self.btn_run.clicked.connect(self.run)
        self.btn_step_back.clicked.connect(self.step_back)
        self.btn_reset.clicked.connect(self.reset)
        
        # Apply button styles
        self.btn_load.setStyleSheet(f"""
            QPushButton {{
                padding: 12px 24px;
                font-size: 12px;
                font-weight: 700;
                border: none;
                border-radius: 6px;
                color: white;
                background-color: {COLOR_BTN_LOAD};
            }}
            QPushButton:hover {{
                background-color: {COLOR_BTN_LOAD_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BTN_LOAD_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_BTN_DISABLED};
            }}
        """)
        
        self.btn_step.setStyleSheet(f"""
            QPushButton {{
                padding: 12px 24px;
                font-size: 12px;
                font-weight: 700;
                border: none;
                border-radius: 6px;
                color: white;
                background-color: {COLOR_BTN_STEP};
            }}
            QPushButton:hover {{
                background-color: {COLOR_BTN_STEP_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BTN_STEP_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_BTN_DISABLED};
            }}
        """)
        
        self.btn_run.setStyleSheet(f"""
            QPushButton {{
                padding: 12px 24px;
                font-size: 12px;
                font-weight: 700;
                border: none;
                border-radius: 6px;
                color: white;
                background-color: {COLOR_BTN_RUN};
            }}
            QPushButton:hover {{
                background-color: {COLOR_BTN_RUN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BTN_RUN_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_BTN_DISABLED};
            }}
        """)
        
        self.btn_step_back.setStyleSheet(f"""
            QPushButton {{
                padding: 12px 24px;
                font-size: 12px;
                font-weight: 700;
                border: none;
                border-radius: 6px;
                color: white;
                background-color: {COLOR_BTN_BACK};
            }}
            QPushButton:hover {{
                background-color: {COLOR_BTN_BACK_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BTN_BACK_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_BTN_DISABLED};
            }}
        """)
        
        self.btn_reset.setStyleSheet(f"""
            QPushButton {{
                padding: 12px 24px;
                font-size: 12px;
                font-weight: 700;
                border: none;
                border-radius: 6px;
                color: white;
                background-color: {COLOR_BTN_RESET};
            }}
            QPushButton:hover {{
                background-color: {COLOR_BTN_RESET_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BTN_RESET_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_BTN_DISABLED};
            }}
        """)
        
        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_step)
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_step_back)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()
        
        main_layout.addLayout(btn_layout)
        
        # === METRICS ===
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)
        
        self.lbl_cycle = QLabel("Ciclo: 0")
        self.lbl_ipc = QLabel("IPC: 0.00")
        self.lbl_bubbles = QLabel("Bolhas: 0")
        self.lbl_flushes = QLabel("Flushes: 0")
        
        metrics_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        
        for lbl in [self.lbl_cycle, self.lbl_ipc, self.lbl_bubbles, self.lbl_flushes]:
            lbl.setFont(metrics_font)
            lbl.setStyleSheet(f"""
                padding: 14px 20px;
                background-color: {COLOR_WHITE};
                border: 2px solid {COLOR_TABLE_BORDER};
                border-radius: 8px;
                color: {COLOR_TEXT_PRIMARY};
                font-size: 13px;
            """)
            lbl.setMinimumWidth(150)
        
        metrics_layout.addWidget(self.lbl_cycle)
        metrics_layout.addWidget(self.lbl_ipc)
        metrics_layout.addWidget(self.lbl_bubbles)
        metrics_layout.addWidget(self.lbl_flushes)
        metrics_layout.addStretch()
        
        main_layout.addLayout(metrics_layout)
        
        # === MAIN CONTENT: TABLES ON LEFT, REGISTERS ON RIGHT ===
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # Left side: Tables
        tables_layout = QVBoxLayout()
        tables_layout.setSpacing(15)
        
        # === Estação de Reserva (RS) ===
        rs_label = QLabel("Estação de Reserva (RS)")
        rs_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        tables_layout.addWidget(rs_label)
        
        self.rs_table = QTableWidget(5, 5)
        self.rs_table.setHorizontalHeaderLabels(["Nome", "Busy", "Op", "Operandos", "Ciclos"])
        self.rs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rs_table.setMaximumHeight(220)
        self.rs_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLOR_WHITE};
                border: 2px solid {COLOR_TABLE_BORDER};
                border-radius: 8px;
                gridline-color: {COLOR_TABLE_GRIDLINE};
            }}
            QHeaderView::section {{
                background-color: {COLOR_TABLE_HEADER};
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
        """)
        
        tables_layout.addWidget(self.rs_table)
        
        # === Buffer de Reordenamento (ROB) ===
        rob_label = QLabel("Buffer de Reordenamento (ROB)")
        rob_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        tables_layout.addWidget(rob_label)
        
        self.rob_table = QTableWidget(8, 5)
        self.rob_table.setHorizontalHeaderLabels(["#", "Busy", "Instrução", "Estado", "Value"])
        self.rob_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rob_table.setMaximumHeight(300)
        self.rob_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLOR_WHITE};
                border: 2px solid {COLOR_TABLE_BORDER};
                border-radius: 8px;
                gridline-color: {COLOR_TABLE_GRIDLINE};
            }}
            QHeaderView::section {{
                background-color: {COLOR_TABLE_HEADER};
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
        """)
        
        tables_layout.addWidget(self.rob_table)
        
        # === CONSOLE LOG ===
        console_label = QLabel("Console de Eventos")
        console_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        tables_layout.addWidget(console_label)
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                font-weight: bold;
                background-color: {COLOR_CONSOLE_BG};
                color: {COLOR_CONSOLE_TEXT};
                border: 2px solid {COLOR_CONSOLE_BORDER};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        self.log_console.setPlainText("Aguardando programa...\n")
        
        tables_layout.addWidget(self.log_console)
        
        content_layout.addLayout(tables_layout, 70)  # 70% width
        
        # Right side: Registers
        registers_layout = QVBoxLayout()
        registers_layout.setSpacing(10)
        
        reg_label = QLabel("Registradores (R0-R31)")
        reg_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLOR_TEXT_PRIMARY};")
        registers_layout.addWidget(reg_label)
        
        # Create register table
        self.reg_table = QTableWidget(32, 2)
        self.reg_table.setHorizontalHeaderLabels(["Reg", "Valor"])
        self.reg_table.verticalHeader().setVisible(False)
        self.reg_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.reg_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.reg_table.setColumnWidth(0, 60)
        self.reg_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLOR_WHITE};
                border: 2px solid {COLOR_TABLE_BORDER};
                border-radius: 8px;
                gridline-color: {COLOR_TABLE_GRIDLINE};
            }}
            QHeaderView::section {{
                background-color: {COLOR_TABLE_HEADER};
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
        """)
        
        # Initialize register cells
        mono_font = QFont("Consolas", 10, QFont.Weight.Medium)
        for i in range(32):
            # Register name
            name_item = QTableWidgetItem(f"R{i}")
            name_item.setFont(mono_font)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.reg_table.setItem(i, 0, name_item)
            
            # Register value
            value_item = QTableWidgetItem("0")
            value_item.setFont(mono_font)
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.reg_table.setItem(i, 1, value_item)
        
        registers_layout.addWidget(self.reg_table)
        
        content_layout.addLayout(registers_layout, 30)  # 30% width
        
        main_layout.addLayout(content_layout)
        
        # Initial UI update
        self.update_ui()
    
    def load_program(self):
        """Load MIPS program from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Carregar Programa MIPS",
            "examples",
            "Assembly Files (*.asm);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            program = [parse_mips(line) for line in lines]
            program = [inst for inst in program if inst is not None]
            
            if not program:
                self.statusBar().showMessage("Nenhuma instrução válida encontrada!", 3000)
                return
            
            self.engine.load_program(program)
            self.current_program_path = file_path
            self.update_ui()
            
            self.statusBar().showMessage(f"Programa carregado: {len(program)} instruções", 3000)
        
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao carregar: {str(e)}", 5000)
    
    def step(self):
        """Execute one cycle."""
        if not self.engine.instructions:
            self.statusBar().showMessage("Nenhum programa carregado!", 3000)
            return
        
        if self.engine.is_complete():
            self.statusBar().showMessage("Simulação completa!", 3000)
            return
        
        self.engine.step()
        self.update_ui()

    def step_back(self):
        """Volta um ciclo na simulação."""
        if not self.engine.history:
            self.statusBar().showMessage("Não há estado anterior para voltar!", 3000)
            return

        try:
            self.engine.step_back()
            self.update_ui()
            self.statusBar().showMessage("Voltou 1 ciclo", 2000)
        except Exception as e:
            self.statusBar().showMessage(f"Erro no step_back: {str(e)}", 3000)
    
    def run(self):
        """Execute until completion with delay for visualization."""
        if not self.engine.instructions:
            self.statusBar().showMessage("Nenhum programa carregado!", 3000)
            return
        
        if self.engine.is_complete():
            self.statusBar().showMessage("Simulação já completa!", 3000)
            return
        
        max_cycles = 100
        cycles = 0
        
        while not self.engine.is_complete() and cycles < max_cycles:
            self.engine.step()
            self.update_ui()
            
            # Small delay for visualization
            time.sleep(0.3)
            
            # Process events to keep UI responsive
            from PyQt6.QtWidgets import QApplication
            QApplication.processEvents()
            
            cycles += 1
        
        if cycles >= max_cycles:
            self.statusBar().showMessage("Limite de ciclos atingido!", 3000)
        else:
            self.statusBar().showMessage("Simulação completa!", 3000)
    
    def reset(self):
        """Reset simulation with current program."""
        if self.current_program_path:
            # Reload same program
            with open(self.current_program_path, 'r') as f:
                lines = f.readlines()
            
            program = [parse_mips(line) for line in lines]
            program = [inst for inst in program if inst is not None]
            
            self.engine.load_program(program)
            self.update_ui()
            
            self.statusBar().showMessage("Simulação resetada", 2000)
        else:
            self.statusBar().showMessage("Nenhum programa carregado para resetar!", 3000)
    
    def update_ui(self):
        """Update all UI elements from engine state."""
        # === UPDATE METRICS ===
        metrics = self.engine.get_metrics()
        self.lbl_cycle.setText(f"Ciclo: {metrics['cycles']}")
        self.lbl_ipc.setText(f"IPC: {metrics['ipc']:.2f}")
        self.lbl_bubbles.setText(f"Bolhas: {metrics['bubbles']}")
        self.lbl_flushes.setText(f"Flushes: {metrics['flushes']}")
        
        # === UPDATE RS TABLE ===
        for i, rs in enumerate(self.engine.rs):
            # Name
            self.rs_table.setItem(i, 0, QTableWidgetItem(rs['name']))
            
            # Busy
            busy_text = "Sim" if rs['busy'] else "Não"
            self.rs_table.setItem(i, 1, QTableWidgetItem(busy_text))
            
            # Op
            op_text = rs['op'] if rs['op'] else "-"
            self.rs_table.setItem(i, 2, QTableWidgetItem(op_text))
            
            # Operands
            if rs['busy']:
                vj_text = str(rs['vj']) if rs['qj'] is None else f"ROB#{rs['qj']}"
                vk_text = str(rs['vk']) if rs['qk'] is None else f"ROB#{rs['qk']}"
                operands = f"{vj_text}, {vk_text}"
            else:
                operands = "-"
            self.rs_table.setItem(i, 3, QTableWidgetItem(operands))
            
            # Cycles
            cycles_text = str(rs['cycles']) if rs['busy'] else "-"
            self.rs_table.setItem(i, 4, QTableWidgetItem(cycles_text))
            
            # Color: Yellow if busy
            bg_color = QColor(COLOR_RS_BUSY) if rs['busy'] else QColor(COLOR_WHITE)
            for col in range(5):
                self.rs_table.item(i, col).setBackground(bg_color)
                self.rs_table.item(i, col).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if rs['busy']:
                    font = self.rs_table.item(i, col).font()
                    font.setBold(True)
                    self.rs_table.item(i, col).setFont(font)
        
        # === UPDATE ROB TABLE ===
        for i in range(8):
            entry = self.engine.rob[i]
            
            # Determine badge and color
            badge = ""
            if i == self.engine.rob_head:
                badge = "[HEAD] "
                bg_color = QColor(COLOR_ROB_HEAD)
            elif i == self.engine.rob_tail:
                badge = "[TAIL] "
                bg_color = QColor(COLOR_ROB_TAIL)
            elif entry['busy'] and entry['estado'] == 'ready':
                bg_color = QColor(COLOR_ROB_READY)
            elif entry['busy']:
                bg_color = QColor(COLOR_ROB_EXECUTING)
            else:
                bg_color = QColor(COLOR_WHITE)
            
            # # Column
            self.rob_table.setItem(i, 0, QTableWidgetItem(f"{badge}{i}"))
            
            # Busy
            busy_text = "Sim" if entry['busy'] else "Não"
            self.rob_table.setItem(i, 1, QTableWidgetItem(busy_text))
            
            # Instruction
            if entry['instruction']:
                inst = entry['instruction']
                inst_text = f"{inst['op']} {inst['dest']} {inst['reg1']} {inst['reg2']}"
            else:
                inst_text = "-"
            self.rob_table.setItem(i, 2, QTableWidgetItem(inst_text))
            
            # State
            state_text = entry['estado'].capitalize() if entry['busy'] else "-"
            self.rob_table.setItem(i, 3, QTableWidgetItem(state_text))
            
            # Value
            value_text = str(entry['value']) if entry['value'] is not None else "-"
            self.rob_table.setItem(i, 4, QTableWidgetItem(value_text))
            
            # Apply background color to all columns
            for col in range(5):
                self.rob_table.item(i, col).setBackground(bg_color)
                self.rob_table.item(i, col).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if badge:  # Bold for HEAD/TAIL
                    font = self.rob_table.item(i, col).font()
                    font.setBold(True)
                    self.rob_table.item(i, col).setFont(font)
        
        # === UPDATE REGISTERS TABLE ===
        for i in range(32):
            val = self.engine.registers[i] if i < len(self.engine.registers) else 0
            qi = self.engine.reg_status[i] if i < len(self.engine.reg_status) else None
            
            # Update register name (column 0)
            name_item = self.reg_table.item(i, 0)
            name_item.setText(f"R{i}")
            
            # Update register value (column 1)
            value_item = self.reg_table.item(i, 1)
            if qi is not None:
                value_item.setText(f"{val} (ROB#{qi})")
                name_item.setBackground(QColor(COLOR_REG_WAITING_BG))
                name_item.setForeground(QColor(COLOR_REG_WAITING_TEXT))
                value_item.setBackground(QColor(COLOR_REG_WAITING_BG))
                value_item.setForeground(QColor(COLOR_REG_WAITING_TEXT))
                
                # Bold font for waiting registers
                font = value_item.font()
                font.setBold(True)
                value_item.setFont(font)
                name_item.setFont(font)
            else:
                value_item.setText(f"{val}")
                name_item.setBackground(QColor(COLOR_REG_NORMAL_BG))
                name_item.setForeground(QColor(COLOR_REG_NORMAL_TEXT))
                value_item.setBackground(QColor(COLOR_REG_NORMAL_BG))
                value_item.setForeground(QColor(COLOR_REG_NORMAL_TEXT))
                
                # Normal font
                font = value_item.font()
                font.setBold(False)
                value_item.setFont(font)
                name_item.setFont(font)
        
        # === UPDATE LOG CONSOLE ===
        if self.engine.log_messages:
            # Show last 20 messages
            recent_logs = self.engine.log_messages[-20:]
            log_text = "\n".join([f"[Ciclo {self.engine.cycle}] {msg}" for msg in recent_logs])
            self.log_console.setPlainText(log_text)
            # Auto-scroll to bottom
            self.log_console.verticalScrollBar().setValue(
                self.log_console.verticalScrollBar().maximum()
            )

        # === ENABLE/DISABLE STEP BACK ===
        self.btn_step_back.setEnabled(len(self.engine.history) > 0)