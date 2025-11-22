# Testa dependência WAW (Write-After-Write)
ADD R1 R2 R3      # Primeira escrita em R1
MUL R1 R4 R5      # Segunda escrita em R1 (WAW)
ADD R6 R1 R7      # Usa o valor final de R1
