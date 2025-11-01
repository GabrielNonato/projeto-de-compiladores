class Instrucao:
    def __init__(self, instrucao, argumento=None):
        self.instrucao = instrucao
        self.argumento = argumento

    def __repr__(self):
        return f"Instrucao({self.instrucao!r}, {self.argumento!r})"
    

def carregar_codigo(arquivo):
    C = []
    with open(arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue  

            partes = linha.split()
            instrucao = partes[0]
            argumento = None

            if len(partes) > 1:
                token = partes[1]
                try:
                    argumento = int(token)  
                except ValueError:
                    argumento = token       

            C.append(Instrucao(instrucao, argumento))
    return C

if __name__ == "__main__":
    C = carregar_codigo("codigoCompilado.txt")

    D = []

    i = 0 
    s = 0 

    while i < len(C):

        if C[i].instrucao == 'INPP':
            s = -1

        elif C[i].instrucao == 'ALME':
            D.extend([0] * C[i].argumento)
            s += C[i].argumento

        elif C[i].instrucao == 'CRCT':
            s = s + 1
            D.append(C[i].argumento) 

        elif C[i].instrucao == 'CRVL':
            s = s + 1
            D.append(D[C[i].argumento])

        elif C[i].instrucao == 'SOMA':
            D[s-1] = D[s-1] + D[s]
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'SUBT':
            D[s-1] = D[s-1] - D[s]
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'MULT':
            D[s-1] = D[s-1] * D[s]
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'DIVI':
            D[s-1] = D[s-1] // D[s]
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'INVE':
            D[s] = -D[s]

        elif C[i].instrucao == 'CONJ':
            if (D[s-1] == 1 and D[s] == 1):
                D[s-1] = 1
            else:
                D[s-1] = 0
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'DISJ':
            if (D[s-1] == 1 or D[s] == 1):
                D[s-1] = 1
            else:
                D[s-1] = 0
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'NEGA':
            D[s] = 1 - D[s]

        elif C[i].instrucao == 'CPME':
            if (D[s-1] < D[s]):
                D[s-1] = 1
            else:
                D[s-1] = 0
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'CPMA':
            if (D[s-1] > D[s]):
                D[s-1] = 1
            else:
                D[s-1] = 0
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'CPIG':
            if (D[s-1] == D[s]):
                D[s-1] = 1
            else:
                D[s-1] = 0
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'CDES':
            if (D[s-1] != D[s]):
                D[s-1] = 1
            else:
                D[s-1] = 0
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'CPMI':
            if (D[s-1] <= D[s]):
                D[s-1] = 1
            else:
                D[s-1] = 0
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'CMAI':
            if (D[s-1] >= D[s]):
                D[s-1] = 1
            else:
                D[s-1] = 0
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'ARMZ':
            D[C[i].argumento] = D[s]
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'DSVI':
            i = C[i].argumento - 1

        elif C[i].instrucao == 'DSVF':
            if D[s] == 0:
                i = C[i].argumento - 1
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'LEIT':
            s = s + 1
            print('Digite um valor: ')
            D.append(float(input()))

        elif C[i].instrucao == 'IMPR':
            print(D[s])
            D.pop()
            s = s - 1

        elif C[i].instrucao == 'PARA':
            break
        else:
            print("ERRO DURANTE A EXECUÇÃO DO PROGRAMA")
            break

        i += 1