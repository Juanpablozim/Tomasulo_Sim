"""
    Parser para instrucoes simples do MIPS
    
    Use:
    - Calculos:
      - ADD R1 R2 R3
      - SUB R1 R2 R3
      - MUL R1 R2 R3
      - DIV R1 R2 R3
    - Memoria:
      - LW R1 0 R2
      - SW R1 0 R2
    - Desvios:
      - BEQ R1 R2 3 # se R1==R2, pula 3 instrucoes pra frente
      - BNE R1 R2 3 # se R1!=R2, pula 3 instrucoes pra frente
    
    Funcionalidades extras: Ignora espacos em branco e comentarios
                            iniciados com #

    Returna:
        conjunto de strings 'op', 'dest', 'reg1', 'reg2', 'estado'
        ou None se for invalido ou comentario
    """

def parse_mips(line: str) -> dict:
    line = line.strip()
    
    #Ignora espacos e coments
    if not line or line.startswith('#'):
        return None
    
    # separa os parametros
    particao = line.split()
    
    if len(particao) < 4:
        return None
    
    # Para funcionar com minusculo e maiusculo
    op = particao[0].upper()
    
    # Operacoes de calculo
    if op in ['ADD', 'SUB', 'MUL', 'DIV']:
        return {
            'op': op,
            'dest': particao[1],
            'reg1': particao[2],
            'reg2': particao[3],
            'estado': 'espera'
        }
    
    # Operacoes de Memoria
    if op in ['LW', 'SW']:
        return {
            'op': op,
            'dest': particao[1],
            'reg1': particao[3],
            'reg2': 'R0',
            'offset': particao[2],
            'estado': 'espera'
        }
    
    # Operacoes de desvio
    if op in ['BEQ', 'BNE']:
        return {
            'op': op,
            'reg1': particao[1],
            'reg2': particao[2],
            'offset': int(particao[3]),
            'dest': 'R0',
            'estado': 'espera'
        }
    
    return None
