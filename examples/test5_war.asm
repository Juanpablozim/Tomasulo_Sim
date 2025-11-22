# Testa dependência WAR (Write-After-Read)
MUL R3 R1 R2      # Lê R1
ADD R1 R4 R5      # Escreve R1 (WAR com a instrução acima)
SUB R6 R3 R1      # Usa resultados renomeados
