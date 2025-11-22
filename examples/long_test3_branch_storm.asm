# Tempestade de branches para gerar FLUSH + misprediction
ADD R5 R0 R0

BEQ R1 R2 2
ADD R10 R0 R0     # pode ser FLUSH
ADD R11 R0 R0     # pode ser FLUSH

BEQ R3 R4 -1
ADD R12 R0 R0     # especulado
ADD R13 R0 R0     # especulado

BEQ R1 R1 4       # sempre taken
ADD R14 R0 R0     # FLUSHADO
ADD R15 R0 R0     # FLUSHADO
ADD R16 R0 R0     # FLUSHADO
ADD R17 R0 R0     # FLUSHADO

MUL R20 R5 R5     # executa só após vários flush
ADD R21 R20 R5
