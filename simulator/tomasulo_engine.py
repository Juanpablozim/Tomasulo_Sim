import copy

# Definicoes iniciais
numRegs = 32 # Numero de registradores

class TomasuloEngine:
    """
    Simple Tomasulo algorithm simulator.
    Uses dicts and lists for academic simplicity.
    """
    
    def __init__(self):
        # Para salvar stepbacks
        self.history = []
        
        # Latencia de cada oper
        self.LATENCIAS = {
            'ADD': 2,
            'SUB': 2,
            'MUL': 4,
            'DIV': 10,
            'LW': 3,
            'SW': 2
        }
        
        # Estacao de Reserva (5 total: 3 Add/Sub, 2 Mult/Div)
        self.rs = [
            {'name': 'Add1', 'busy': False, 'op': None, 'vj': 0, 'vk': 0, 'qj': None, 'qk': None, 'dest': None, 'cycles': 0},
            {'name': 'Add2', 'busy': False, 'op': None, 'vj': 0, 'vk': 0, 'qj': None, 'qk': None, 'dest': None, 'cycles': 0},
            {'name': 'Add3', 'busy': False, 'op': None, 'vj': 0, 'vk': 0, 'qj': None, 'qk': None, 'dest': None, 'cycles': 0},
            {'name': 'Mult1', 'busy': False, 'op': None, 'vj': 0, 'vk': 0, 'qj': None, 'qk': None, 'dest': None, 'cycles': 0},
            {'name': 'Mult2', 'busy': False, 'op': None, 'vj': 0, 'vk': 0, 'qj': None, 'qk': None, 'dest': None, 'cycles': 0},
        ]
        
        # Buffer de Reordenamento (8 entradas)
        self.rob = [
            {'busy': False, 'instruction': None, 'estado': 'espera', 'value': None, 'dest': None}
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

    def snapshot(self):
        """Cria um snapshot profundo do estado para possibilitar stepBack."""
        return {
            'PC': self.PC,
            'clock': self.clock,
            'instr_buffer': copy.deepcopy(self.instr_buffer),
            'RS': copy.deepcopy(self.RS),
            'REG': copy.deepcopy(self.REG),
            'ROB': copy.deepcopy(self.ROB),
            'CDB': copy.deepcopy(self.CDB),
        }

    def restore(self, snap):
        """Restaura um snapshot."""
        self.PC = snap['PC']
        self.clock = snap['clock']
        self.instr_buffer = copy.deepcopy(snap['instr_buffer'])
        self.RS = copy.deepcopy(snap['RS'])
        self.REG = copy.deepcopy(snap['REG'])
        self.ROB = copy.deepcopy(snap['ROB'])
        self.CDB = copy.deepcopy(snap['CDB'])

    def step(self):
        """Executa um ciclo e salva o estado anterior para permitir stepBack."""
        # Salva o estado antes de executar o ciclo
        self.history.append(self.snapshot())

        # sua lógica atual de step aqui:
        self.issue()
        self.execute()
        self.writeback()
        self.clock += 1

    def stepBack(self):
        """Volta um ciclo no simulador."""
        if not self.history:
            print("⚠ Não há estado anterior para retornar.")
            return
        
        last = self.history.pop()
        self.restore(last)
        print(f"🟡 Retornou 1 ciclo. Ciclo atual: {self.clock}")
        
    def reset(self):
        """Reset simulator to initial estado."""
        self.__init__()
    
    def load_program(self, instructions):
        self.reset()
        self.instructions = [inst for inst in instructions if inst is not None]
        
        #Valores iniciais para testes
        self.registers[2] = 5   # R2 = 5
        self.registers[3] = 10  # R3 = 10
        self.registers[5] = 2   # R5 = 2
        self.registers[6] = 3   # R6 = 3
    
    def step(self):
        self.commit()
        self.write_result()
        self.execute()
        self.issue()
        self.cycle += 1
    
    def issue(self):
        if self.pc >= len(self.instructions):
            return
        
        instruction = self.instructions[self.pc]
        op = instruction['op']
        
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
        
        if rs_index is None or self.rob[self.rob_tail]['busy']:
            self.bubble_cycles += 1
            return
        
        rs = self.rs[rs_index]
        rs['busy'] = True
        rs['op'] = op
        rs['cycles'] = self.LATENCIAS.get(op, 1)
        rs['rob_index'] = self.rob_tail
        rs['pc_when_issued'] = self.pc
        
        dest_reg = int(instruction['dest'][1:])
        reg1_reg = int(instruction['reg1'][1:])
        reg2_reg = int(instruction['reg2'][1:])
        
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
        
        rob_entry = self.rob[self.rob_tail]
        rob_entry['busy'] = True
        rob_entry['instruction'] = instruction
        rob_entry['estado'] = 'executing'
        rob_entry['dest'] = dest_reg
        rob_entry['value'] = None
        rob_entry['should_branch'] = False
        rob_entry['target_pc'] = None
        
        if op not in ['BEQ', 'BNE']:
            self.reg_status[dest_reg] = self.rob_tail
        
        self.pc += 1
        self.rob_tail = (self.rob_tail + 1) % 8
        
        self.log_messages.append(f"Issued {op} at PC={self.pc-1}")
    
    def execute(self):
        for rs in self.rs:
            if not rs['busy']:
                continue
            
            if rs['qj'] is None and rs['qk'] is None:
                if rs['cycles'] > 0:
                    rs['cycles'] -= 1
    
    def write_result(self):
        for rs in self.rs:
            if not rs['busy'] or rs['cycles'] > 0:
                continue
            
            op = rs['op']
            vj = rs['vj']
            vk = rs['vk']
            rob_index = rs['rob_index']
            
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
                
                self.log_messages.append(f"BEQ resolved: {vj}=={vk}? {should_branch}, target PC={target_pc}")
            elif op == 'BNE':
                should_branch = (vj != vk)
                instruction = self.rob[rob_index]['instruction']
                pc_when_issued = rs['pc_when_issued']
                target_pc = pc_when_issued + 1 + instruction['offset']
                
                self.rob[rob_index]['should_branch'] = should_branch
                self.rob[rob_index]['target_pc'] = target_pc
                result = 0
                
                self.log_messages.append(f"BNE resolved: {vj}!={vk}? {should_branch}, target PC={target_pc}")
            else:
                result = 0
            
            rob_index = rs['rob_index']
            self.rob[rob_index]['value'] = result
            self.rob[rob_index]['estado'] = 'ready'
            
            for espera_rs in self.rs:
                if espera_rs['qj'] == rob_index:
                    espera_rs['vj'] = result
                    espera_rs['qj'] = None
                if espera_rs['qk'] == rob_index:
                    espera_rs['vk'] = result
                    espera_rs['qk'] = None
            
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
            predicted_not_taken = True
            actual_should_branch = rob_entry['should_branch']
            
            if actual_should_branch:
                target_pc = rob_entry['target_pc']
                self.log_messages.append(f"🔥 FLUSH! Branch mispredicted, jumping to PC={target_pc}")
                self.flush(target_pc)
                self.flush_count += 1
            
            rob_entry['busy'] = False
            rob_entry['instruction'] = None
            rob_entry['estado'] = 'espera'
            rob_entry['value'] = None
            rob_entry['dest'] = None
            
            self.rob_head = (self.rob_head + 1) % 8
            self.instructions_committed += 1
            self.log_messages.append(f"Committed {op}")
            return
        
        dest_reg = rob_entry['dest']
        self.registers[dest_reg] = rob_entry['value']
        
        if self.reg_status[dest_reg] == self.rob_head:
            self.reg_status[dest_reg] = None
        
        rob_entry['busy'] = False
        rob_entry['instruction'] = None
        rob_entry['estado'] = 'espera'
        rob_entry['value'] = None
        rob_entry['dest'] = None
        
        self.rob_head = (self.rob_head + 1) % 8
        self.instructions_committed += 1
        self.log_messages.append(f"Committed {op}")
    
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

        tail_index = self.rob_head
        for i in range(8):
            if i != self.rob_head:
                self.rob[i]['busy'] = False
                self.rob[i]['instruction'] = None
                self.rob[i]['estado'] = 'espera'
                self.rob[i]['value'] = None
                self.rob[i]['dest'] = None
        
        self.rob_tail = (self.rob_head + 1) % 8
        
        for i in range(numRegs):
            self.reg_status[i] = None
        
        self.pc = correct_pc
        
        self.log_messages.append(f"Pipeline flushed, PC redirected to {correct_pc}")
    
    def is_complete(self):
        pc_done = self.pc >= len(self.instructions)
        
        rob_empty = all(not entry['busy'] for entry in self.rob)
        
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