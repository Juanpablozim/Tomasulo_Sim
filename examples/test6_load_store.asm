# Testa dependências e ordem entre LOAD e STORE
STORE R1 0(R2)    # Mem[R2] = R1
LOAD  R3 0(R2)    # R3 depende do store (RAW via memória)
LOAD  R4 4(R2)    # Acessa endereço diferente (independente)
STORE R5 4(R2)    # Escreve no endereço do LOAD acima (WAR na memória)
