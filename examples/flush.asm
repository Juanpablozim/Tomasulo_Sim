# Comparação: R2 (5) != R5 (2) -> VERDADEIRO
# O desvio DEVE acontecer (pular 3 instruções)
# O simulador prevê que NÃO vai acontecer e carrega as instruções abaixo (Especulação)
BNE R2 R5 3

# --- ZONA DE ESPECULAÇÃO (Será Flushada) ---
# Estas instruções entrarão no ROB enquanto o BNE é calculado
# Quando o BNE for commitado, elas serão apagadas
ADD R1 R2 R3
SUB R1 R2 R3
MUL R1 R2 R3

# --- ALVO CORRETO ---
# O simulador deve retomar a execução aqui após o flush
LW R6 0 R2