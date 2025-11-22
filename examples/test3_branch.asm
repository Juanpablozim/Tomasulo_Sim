ADD R4 R0 R0    # Committado
BEQ R1 R2 3     # Taken! (predição: not taken → MISPREDICTION!)
ADD R5 R0 R0    # especulado (FLUSHED)
ADD R6 R0 R0    # especulado (FLUSHED)
ADD R7 R0 R0    # especulado (FLUSHED)
MUL R8 R3 R3    # Committed após flush (R8=100)