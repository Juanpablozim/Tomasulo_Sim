import copy

# Definicoes iniciais
numRegs = 32 # Numero de registradores

class TomasuloEngine:
    """
    Simulador do algoritmo de Tomasulo.
    """
    
    def __init__(self):
        # Para salvar stepbacks
        self.history = []
        
        # Latencia de cada oper
        self.LATENCIAS = {
            'ADD': 2, 'SUB': 2,
            'MUL': 4, 'DIV': 10,
            'LW': 3, 'SW': 2,
            'BEQ': 1, 'BNE': 1
        }
        
        # Estacao de Reserva (5 total: 3 Add/Sub, 2 Mult/Div)
        self.rs = [
            {'name': 'Add1', 'busy': False, 'op': None, 'vj': 0, 'vk': 0, 'qj': None, 'qk': None, 'dest': None, 'cycles': 0, 'rob_index': None, 'pc_when_issued': None},
            {'name': 'Add2', 'busy': False, 'op': None, 'vj': 0, 'vk': 0, 'qj': None, 'qk': None, 'dest': None, 'cycles': 0, 'rob_index': None, 'pc_when_issued': None},
            {'name': 'Add3', 'busy': False, 'op': None, 'vj': 0, 'vk': 0, 'qj': None, 'qk': None, 'dest': None, 'cycles': 0, 'rob_index': None, 'pc_when_issued': None},
            {'name': 'Mult1', 'busy': False, 'op': None, 'vj': 0, 'vk': 0, 'qj': None, 'qk': None, 'dest': None, 'cycles': 0, 'rob_index': None, 'pc_when_issued': None},
            {'name': 'Mult2', 'busy': False, 'op': None, 'vj': 0, 'vk': 0, 'qj': None, 'qk': None, 'dest': None, 'cycles': 0, 'rob_index': None, 'pc_when_issued': None},
        ]
        
        # Buffer de Reordenamento (8 entradas)
        self.rob = [
            {'busy': False, 'instruction': None, 'estado': 'espera', 'value': None, 'dest': None, 'should_branch': False, 'target_pc': None}
            for _ in range(8)
        ]
        self.rob_head = 0  # Aponta para a próxima instrução a ser commitada
        self.rob_tail = 0  # Aponta para a próxima entrada livre
        
        self.registers = [0] * numRegs
        self.reg_status = [None] * numRegs
        
        # Estado da simulação
        self.cycle = 0
        self.instructions = []
        self.pc = 0
        self.instructions_committed = 0
        self.bubble_cycles = 0
        self.flush_count = 0
        self.log_messages = []

    def create_snapshot(self):
        """Cria um snapshot profundo do estado atual."""
        return {
            'cycle': self.cycle,
            'pc': self.pc,
            'rs': copy.deepcopy(self.rs),
            'rob': copy.deepcopy(self.rob),
            'rob_head': self.rob_head,
            'rob_tail': self.rob_tail,
            'registers': list(self.registers),      
            'reg_status': list(self.reg_status),    
            'instructions_committed': self.instructions_committed,
            'bubble_cycles': self.bubble_cycles,
            'flush_count': self.flush_count,
            'log_messages': list(self.log_messages) 
        }

    def restore_snapshot(self, snap):
        """Restaura o estado a partir de um snapshot."""
        self.cycle = snap['cycle']
        self.pc = snap['pc']
        self.rs = copy.deepcopy(snap['rs'])
        self.rob = copy.deepcopy(snap['rob'])
        self.rob_head = snap['rob_head']
        self.rob_tail = snap['rob_tail']
        self.registers = list(snap['registers'])
        self.reg_status = list(snap['reg_status'])
        self.instructions_committed = snap['instructions_committed']
        self.bubble_cycles = snap['bubble_cycles']
        self.flush_count = snap['flush_count']
        self.log_messages = list(snap['log_messages'])

    def step(self):
        """Executa um ciclo e salva o histórico."""
        # Salva o estado ATUAL no histórico antes de modificá-lo
        self.history.append(self.create_snapshot())

        # Executa a lógica do pipeline
        self.commit()
        self.write_result()
        self.execute()
        self.issue()
        
        # Incrementa o ciclo
        self.cycle += 1

    def step_back(self):
        """Volta um ciclo no simulador (Desfaz o último step)."""
        if not self.history:
            return
        
        # Pega o último estado salvo
        last_state = self.history.pop()
        
        # Restaura as variáveis
        self.restore_snapshot(last_state)
        
        # Adiciona log para feedback visual
        self.log_messages.append(f"--- STEP BACK executado. Voltando para Ciclo {self.cycle} ---")
        
    def reset(self):
        current_instructions = self.instructions
        
        self.__init__()
        
        self.instructions = current_instructions
        
        # Valores iniciais para testes
        self.registers[2] = 5   # R2 = 5
        self.registers[3] = 10  # R3 = 10
        self.registers[5] = 2   # R5 = 2
        self.registers[6] = 3   # R6 = 3
    
    def load_program(self, instructions):
        self.reset()
        self.instructions = [inst for inst in instructions if inst is not None]
    
    def issue(self):
        if self.pc >= len(self.instructions):
            return
        
        instruction = self.instructions[self.pc]
        op = instruction['op']
        
        # Seleciona RS livre
        rs_index = None
        if op in ['ADD', 'SUB']:
            for i in range(3):
                if not self.rs[i]['busy']:
                    rs_index = i
                    break
        elif op in ['MUL', 'DIV']:
            for i in range(3, 5):
                if not self.rs[i]['busy']:
                    rs_index = i
                    break
        elif op in ['LW', 'SW']:
            for i in range(3):
                if not self.rs[i]['busy']:
                    rs_index = i
                    break
        elif op in ['BEQ', 'BNE']:
            for i in range(3):
                if not self.rs[i]['busy']:
                    rs_index = i
                    break
        
        # Se não há RS ou se o ROB (apontado pelo tail) está ocupado (ROB cheio)
        if rs_index is None or self.rob[self.rob_tail]['busy']:
            self.bubble_cycles += 1
            return
        
        # Aloca RS
        rs = self.rs[rs_index]
        rs['busy'] = True
        rs['op'] = op
        rs['cycles'] = self.LATENCIAS.get(op, 1)
        rs['rob_index'] = self.rob_tail
        rs['pc_when_issued'] = self.pc
        
        dest_reg = int(instruction['dest'][1:]) if instruction['dest'] else 0
        reg1_reg = int(instruction['reg1'][1:]) if instruction['reg1'] else 0
        reg2_reg = int(instruction['reg2'][1:]) if instruction['reg2'] else 0
        
        # Dependencias de reg1
        if self.reg_status[reg1_reg] is None:
            rs['vj'] = self.registers[reg1_reg]
            rs['qj'] = None
        else:
            rs['vj'] = None
            rs['qj'] = self.reg_status[reg1_reg]
        
        # Dependencias de reg2
        if self.reg_status[reg2_reg] is None:
            rs['vk'] = self.registers[reg2_reg]
            rs['qk'] = None
        else:
            rs['vk'] = None
            rs['qk'] = self.reg_status[reg2_reg]
        
        # Aloca ROB
        rob_entry = self.rob[self.rob_tail]
        rob_entry['busy'] = True
        rob_entry['instruction'] = instruction
        rob_entry['estado'] = 'executing'
        rob_entry['dest'] = dest_reg
        rob_entry['value'] = None
        rob_entry['should_branch'] = False
        rob_entry['target_pc'] = None
        
        if op not in ['BEQ', 'BNE', 'SW']:
            self.reg_status[dest_reg] = self.rob_tail
        
        self.pc += 1
        self.rob_tail = (self.rob_tail + 1) % 8
        
        self.log_messages.append(f"{op} Despachado em PC={self.pc-1}")
    
    def execute(self):
        for rs in self.rs:
            if not rs['busy']:
                continue
            
            if rs['qj'] is None and rs['qk'] is None:
                if rs['cycles'] > 0:
                    rs['cycles'] -= 1
    
    def write_result(self):
        for rs in self.rs:
            if not rs['busy'] or rs['cycles'] > 0 or rs['qj'] is not None or rs['qk'] is not None:
                continue
            
            op = rs['op']
            vj = rs['vj']
            vk = rs['vk']
            rob_index = rs['rob_index']
            
            result = 0
            
            if op == 'ADD':
                result = vj + vk
            elif op == 'SUB':
                result = vj - vk
            elif op == 'MUL':
                result = vj * vk
            elif op == 'DIV':
                result = vj // vk if vk != 0 else 0
            elif op in ['LW', 'SW']:
                result = vj + vk
            elif op == 'BEQ':
                should_branch = (vj == vk)
                instruction = self.rob[rob_index]['instruction']
                pc_when_issued = rs['pc_when_issued']
                target_pc = pc_when_issued + 1 + instruction['offset']
                
                self.rob[rob_index]['should_branch'] = should_branch
                self.rob[rob_index]['target_pc'] = target_pc
                result = 0
                self.log_messages.append(f"BEQ resolvido: {vj}=={vk}? {should_branch}, ir para PC={target_pc}")
            elif op == 'BNE':
                should_branch = (vj != vk)
                instruction = self.rob[rob_index]['instruction']
                pc_when_issued = rs['pc_when_issued']
                target_pc = pc_when_issued + 1 + instruction['offset']
                
                self.rob[rob_index]['should_branch'] = should_branch
                self.rob[rob_index]['target_pc'] = target_pc
                result = 0
                self.log_messages.append(f"BNE resolvido: {vj}!={vk}? {should_branch}, ir para PC={target_pc}")
            
            # Atualiza ROB
            rob_entry = self.rob[rob_index]
            rob_entry['value'] = result
            rob_entry['estado'] = 'ready'
            
            for espera_rs in self.rs:
                if espera_rs['busy']:
                    if espera_rs['qj'] == rob_index:
                        espera_rs['vj'] = result
                        espera_rs['qj'] = None
                    if espera_rs['qk'] == rob_index:
                        espera_rs['vk'] = result
                        espera_rs['qk'] = None
            
            # Libera a RS atual
            rs['busy'] = False
            rs['op'] = None
            rs['vj'] = 0
            rs['vk'] = 0
            rs['qj'] = None
            rs['qk'] = None
            rs['dest'] = None
            rs['cycles'] = 0
    
    def commit(self):
        rob_entry = self.rob[self.rob_head]
        
        if not rob_entry['busy'] or rob_entry['estado'] != 'ready':
            return
        
        instruction = rob_entry['instruction']
        op = instruction['op'] if instruction else None
        
        if op in ['BEQ', 'BNE']:
            predicted_taken = False 
            actual_should_branch = rob_entry['should_branch']
            
            if actual_should_branch != predicted_taken:
                # Erro de predição: FLUSH
                target_pc = rob_entry['target_pc']
                self.log_messages.append(f"FLUSH! predicao errada de branch, pulando para PC={target_pc}")
                self.flush(target_pc)
                self.flush_count += 1
                return
            
            self.clean_rob_entry(rob_entry)
            self.rob_head = (self.rob_head + 1) % 8
            self.instructions_committed += 1
            self.log_messages.append(f"{op} Commitado")
            return
        
        # Instruções normais: Escreve no Register File
        dest_reg = rob_entry['dest']
        if dest_reg is not None and dest_reg < numRegs:
            self.registers[dest_reg] = rob_entry['value']
            if self.reg_status[dest_reg] == self.rob_head:
                self.reg_status[dest_reg] = None
        
        self.clean_rob_entry(rob_entry)
        
        self.rob_head = (self.rob_head + 1) % 8
        self.instructions_committed += 1
        self.log_messages.append(f"{op} Commitado")

    def clean_rob_entry(self, entry):
        """Helper para limpar entrada do ROB"""
        entry['busy'] = False
        entry['instruction'] = None
        entry['estado'] = 'espera'
        entry['value'] = None
        entry['dest'] = None
        entry['should_branch'] = False
        entry['target_pc'] = None

    def flush(self, correct_pc):
        for rs in self.rs:
            rs['busy'] = False
            rs['op'] = None
            rs['vj'] = 0
            rs['vk'] = 0
            rs['qj'] = None
            rs['qk'] = None
            rs['dest'] = None
            rs['cycles'] = 0

        for i in range(8):
            self.clean_rob_entry(self.rob[i])
            
        self.rob_head = 0
        self.rob_tail = 0
        
        for i in range(numRegs):
            self.reg_status[i] = None
        
        self.pc = correct_pc
        
        self.log_messages.append(f"PC redirecionado para {correct_pc} (Pipeline Flush)")
    
    def is_complete(self):
        pc_done = self.pc >= len(self.instructions)
        rob_empty = not self.rob[self.rob_head]['busy']
        
        return pc_done and rob_empty
    
    def get_metrics(self):
        ipc = self.instructions_committed / self.cycle if self.cycle > 0 else 0
        return {
            'cycles': self.cycle,
            'instructions': self.instructions_committed,
            'ipc': ipc,
            'bubbles': self.bubble_cycles,
            'flushes': self.flush_count
        }