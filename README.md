# Simulador de Tomasulo com Especulação de Branches

Um brinde a Tomasulo

**Trabalho 2 - Arquitetura de Computadores 3**
Implementação de um simulador do algoritmo de Tomasulo com suporte a especulação de branches e mecanismo de FLUSH.

---

## 📋 Características

- ✅ **Algoritmo de Tomasulo completo** com 4 estágios de pipeline
- ✅ **Especulação de branches** com estratégia "Predict Not Taken"
- ✅ **Mecanismo de FLUSH** para recuperação de misprediction
- ✅ **5 Reservation Stations** (3 Add/Sub, 2 Mult/Div)
- ✅ **8 entradas no ROB** (Reorder Buffer)
- ✅ **16 registradores** (R0-R15)
- ✅ **Interface gráfica PyQt6** com visualização em tempo real
- ✅ **Console de log** mostrando todos os eventos do pipeline

---

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Requisitos:**
- Python 3.11 ou superior
- PyQt6 >= 6.6.0

### 2. Rodar o Simulador

```bash
python -m src.main
```

Ou alternativamente:

```bash
python src/main.py
```

### 3. Usar a Interface Gráfica

1. **📂 Carregar Programa**: Clique para selecionar um arquivo `.asm` (exemplos em `examples/`)
2. **▶️ Step**: Executa um ciclo de clock por vez
3. **⏩ Run**: Executa automaticamente até o fim (0.3s por ciclo)
4. **🔄 Reset**: Recarrega o programa atual do início

---

## 📝 Programas de Exemplo

### `test1.asm` - Dependências RAW
Testa dependências Read-After-Write entre instruções:
```assembly
ADD R1 R2 R3    # R1 = 5 + 10 = 15
ADD R4 R1 R5    # R4 = 15 + 2 = 17 (depende de R1)
```

### `test2.asm` - Latências Diferentes
Testa instruções com latências variadas (ADD=2, MUL=4):
```assembly
ADD R1 R2 R3    # 2 ciclos
MUL R4 R5 R6    # 4 ciclos
```

### `test3_branch.asm` - Branch Misprediction ⚠️ CRÍTICO
Demonstra especulação e FLUSH quando branch é mispredicted:
```assembly
ADD R4 R0 R0    # Commitado
BEQ R1 R2 3     # Taken! (predição: not taken → MISPREDICTION!)
ADD R5 R0 R0    # especulado (FLUSHED)
ADD R6 R0 R0    # especulado (FLUSHED)
ADD R7 R0 R0    # especulado (FLUSHED)
MUL R8 R3 R3    # Commitado após flush (R8=100)
```

**Resultado esperado:**
- R4 = 0 (committed antes do branch)
- R5, R6, R7 = inalterados (flushed!)
- R8 = 100 (executado após flush)
- Flush count = 1

---

## 📊 Métricas Exibidas

### Ciclo
Número total de ciclos de clock executados.

### IPC (Instructions Per Cycle)
```
IPC = Instruções Committed / Ciclos Totais
```
Ideal: ~1.0 (uma instrução por ciclo)  
Real: ~0.25-0.40 (devido a dependências e latências)

### Bolhas
Número de ciclos em que nenhuma instrução foi issued devido a:
- **Hazard estrutural**: Todas as RS ocupadas
- **Hazard de dados**: Operandos não prontos

### Flushes 🔥
Número de vezes que o pipeline foi flushed devido a branch misprediction.  
**REQUISITO CRÍTICO**: Este valor deve ser > 0 ao executar `test3_branch.asm`!

---

## 🎨 Interface Gráfica

### Reservation Stations
- **Amarelo**: RS ocupada (busy)
- **Branco**: RS livre

### Reorder Buffer (ROB)
- **Verde**: 🟢 HEAD (próxima instrução a commitar)
- **Azul**: 🔵 TAIL (próxima posição a alocar)
- **Branco**: Entrada livre

### Registradores
- **Preto**: Valor pronto
- **Vermelho**: Aguardando resultado (mostra `ROB#X`)

### Console de Log
Console escuro mostrando os últimos 20 eventos:
- `Issued ADD at PC=X` - Instrução despachada
- `BEQ resolved: 5==5? True` - Branch resolvido
- `FLUSH! Branch mispredicted` - Pipeline flushed!
- `Committed ADD` - Instrução retired

---

## 🔧 Arquitetura do Pipeline

### Estágios (ordem CRÍTICA):

1. **Commit** (Stage 1) 
   - Retire instrução no HEAD do ROB
   - **ÚNICO estágio que escreve em registradores!**
   - Detecta branch misprediction
   - Chama `flush()` se necessário

2. **Write Result** (Stage 2)
   - Calcula resultado da operação
   - Resolve branches (compara registradores)
   - Broadcast para ROB e RS esperando

3. **Execute** (Stage 3)
   - Decrementa latências das RS com operandos prontos
   - RS com `cycles=0` → estado `ready`

4. **Issue** (Stage 4)
   - Despacha próxima instrução para RS/ROB
   - Implementa "Predict Not Taken" para branches
   - Incrementa PC (especulativamente)

---

## 🔥 Especulação de Branches

### Estratégia: Predict Not Taken
- Sempre assume que branch **NÃO** será taken
- Continua issuing instruções sequenciais (PC+1)

### Quando há Misprediction:
1. Branch é resolvido em **Write Result** (compara operandos)
2. Branch chega ao HEAD do ROB em **Commit**
3. Commit detecta: "Predição = Not Taken, Realidade = Taken"
4. **FLUSH!**

### O que o FLUSH faz:
1. Limpa todas as Reservation Stations
2. Limpa todas as entradas do ROB (exceto HEAD)
3. Reseta TAIL para `HEAD + 1`
4. Limpa todos os `reg_status[i]` (nenhum registro esperando)
5. Redireciona PC para o target correto (`PC = target_pc`)

**Resultado**: Todas as instruções especuladas são descartadas!

---

## 🧪 Testes Automatizados

### Testar Engine (sem GUI)
```bash
python test_tomasulo.py
```

Testa:
- Execução de test1.asm e test2.asm
- Separação entre Commit e Write Result
- Valores finais dos registradores

### Testar Branch + FLUSH 🔥
```bash
python test_branch_flush.py
```

**Teste CRÍTICO** que valida:
- ✅ FLUSH detectado quando branch é taken
- ✅ R5/R6/R7 permanecem inalterados (speculated, não committed)
- ✅ R8 = 100 (executado após flush)
- ✅ Flush count = 1

---

## 📁 Estrutura do Projeto

```
Trabalho2/
├── src/
│   ├── simulator/
│   │   ├── instruction.py       # Parser MIPS (ADD, BEQ, etc.)
│   │   └── tomasulo_engine.py   # Engine principal (4 stages + flush)
│   ├── gui/
│   │   └── main_window.py       # Interface PyQt6
│   └── main.py                  # Entry point
├── examples/
│   ├── test1.asm                # RAW dependencies
│   ├── test2.asm                # Different latencies
│   └── test3_branch.asm         # Branch misprediction 🔥
├── docs/
│   └── sprint-artifacts/        # User stories e tech spec
├── test_tomasulo.py             # Testes do engine
├── test_branch_flush.py         # Teste de FLUSH 🔥
├── requirements.txt             # PyQt6
└── README.md                    # Este arquivo
```

---

## 🎯 Instruções Suportadas
___________________________________________________________________________________
|  Inst   | Formato            | Latência  | Descrição                            |
|---------|--------------------|-----------|--------------------------------------|
|  `ADD`  | `ADD Rd Rs Rt`     | 2 ciclos  | Rd = Rs + Rt                         |
|  `SUB`  | `SUB Rd Rs Rt`     | 2 ciclos  | Rd = Rs - Rt                         |
|  `MUL`  | `MUL Rd Rs Rt`     | 4 ciclos  | Rd = Rs * Rt                         |
|  `DIV`  | `DIV Rd Rs Rt`     | 10 ciclos | Rd = Rs / Rt                         |
|  `LOAD` | `LW Rd offset Rs`  | 3 ciclos  | Rd = Mem[Rs + offset] (simplificado) |
| `STORE` | `SW Rs offset Rd`  | 2 ciclos  | Mem[Rd + offset] = Rs (simplificado) |
|  `BEQ`  | `BEQ Rs Rt offset` | 1 ciclo   | Se Rs == Rt, PC = PC + 1 + offset    |
|  `BNE`  | `BNE Rs Rt offset` | 1 ciclo   | Se Rs != Rt, PC = PC + 1 + offset    |
|_________|______________________|___________|______________________________________|

**Nota**: LOAD/STORE são simplificados (sem cache real), apenas para demonstração.

---

## ⚠️ Observações Importantes

### 1. Completion Check
Simulação completa quando:
- `PC >= len(instructions)` (nenhuma instrução para issue)
- `ROB vazio` (todas instruções committed)

Após FLUSH, algumas instruções são descartadas, então **não podemos** usar `instructions_committed >= len(instructions)`.

### 2. Ordem dos Estágios
A ordem **Commit → Write Result → Execute → Issue** é CRÍTICA!
- Commit deve acontecer ANTES para garantir in-order retirement
- Issue por último para refletir especulação correta

### 3. Branch Resolution
Branches são resolvidos em **Write Result** (não em Execute) porque:
- Precisam ler valores dos registradores (Vj, Vk)
- Calculam target_pc = `pc_when_issued + 1 + offset`
- Misprediction só é detectada em **Commit**

---


---

## 👨‍💻 Autor

**Luis Fernando**
**Luiz Gabriel**
**Juan Ramos**
**Julia Roque**
Arquitetura de Computadores 3 - 6º Período  
Trabalho 2 - Simulador Tomasulo com Branch Speculation

---

## 🔍 Debugging Tips

### GUI não abre?
```bash
# Verificar se PyQt6 está instalado
pip list | grep PyQt6

# Reinstalar se necessário
pip install --upgrade PyQt6
```

### ModuleNotFoundError?
```bash
# Sempre rodar com -m a partir da raiz do projeto
python -m src.main

# Ou adicionar ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:."  # Linux/Mac
$env:PYTHONPATH = "." ; python src/main.py  # Windows PowerShell
```

### Flush não está funcionando?
- Verifique se R1 e R2 são iguais (branch deve ser taken)
- Procure por "FLUSH!" no console de log
- Confirme que Flush count > 0 nas métricas

---

**Última atualização**: Novembro 2025  
**Versão**: 1.0 (Story 4 - Branch Speculation completo)
