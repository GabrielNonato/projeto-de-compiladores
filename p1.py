from typing import List, Dict, Tuple
from collections import deque
from enum import Enum, auto


# Definições de Tipos de Token

class TokenType(Enum):
    KEYWORD_PUBLIC = auto()
    KEYWORD_CLASS = auto()
    KEYWORD_ID = auto()
    KEYWORD_LBRACE = auto()
    KEYWORD_RBRACE = auto()
    KEYWORD_STATIC = auto()
    KEYWORD_VOID = auto()
    KEYWORD_MAIN = auto()
    KEYWORD_LPAR = auto()
    KEYWORD_RPAR = auto()
    KEYWORD_STRING = auto()
    KEYWORD_LCOL = auto()
    KEYWORD_RCOL = auto()
    KEYWORD_COMMA = auto()
    KEYWORD_TDOUBLE = auto()
    KEYWORD_SEMICOLON = auto()
    KEYWORD_IF = auto()
    KEYWORD_WHILE = auto()
    KEYWORD_PRINT = auto()
    KEYWORD_ELSE = auto()
    KEYWORD_ATBR = auto()
    KEYWORD_READ = auto()
    KEYWORD_EQUAL = auto()
    KEYWORD_DIF = auto()
    KEYWORD_GE = auto()
    KEYWORD_LE = auto()
    KEYWORD_G = auto()
    KEYWORD_L = auto()
    KEYWORD_SUB = auto()
    KEYWORD_NUMBER = auto()
    KEYWORD_PLUS = auto()
    KEYWORD_MULT = auto()
    KEYWORD_DIV = auto()
    END_OF_FILE = auto()
    UNKNOWN = auto()


# Estrutura de Token

class Token:
    def __init__(self, tipo, lexema, linha):
        self.tipo = tipo
        self.lexema = lexema
        self.linha = linha


# Gerador de Código (MaqHipo)

class EntradaTS:
    def __init__(self, lexema, endRel, primeiraInstrucao=-1):
        self.lexema = lexema
        self.endRel = endRel
        self.primeiraInstrucao = primeiraInstrucao

class GeradorDeCodigo:
    def __init__(self):
        self.codigo_c = []
        self.ts = {}
        self.contadorEndRel = 0

    def adicionar(self, instrucao):
        """Adiciona uma instrução ao código C e retorna o endereço da instrução."""
        self.codigo_c.append(f"{instrucao}")
        return len(self.codigo_c) - 1

    def declararVariavel(self, lexema):
        """Registra na TS do gerador e adicionar ALME 1."""
        if lexema in self.ts:
            raise Exception(f"Erro Semântico: Variável '{lexema}' já declarada.")
        entrada = EntradaTS(lexema, self.contadorEndRel)
        self.ts[lexema] = entrada
        self.contadorEndRel += 1
        self.adicionar("ALME 1")

    def buscarEntrada(self, lexema):
        return self.ts.get(lexema)

    def backpatch(self, enderecoLinha, destino):
        instrucao = self.codigo_c[enderecoLinha]
        partes = instrucao.split()
        if len(partes) == 2 and partes[1] == 'END_A_DECLARAR':
            self.codigo_c[enderecoLinha] = f"{partes[0]} {destino}"
        else:
            raise Exception(f"Erro Interno: instrução inválida: {instrucao}")

    def salvar(self, nome_arquivo="codigoCompilado.txt"):
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            for instr in self.codigo_c:
                f.write(instr + "\n")


# Estados do AFD

class LexerState(Enum):
    INICIAL = auto()
    IDENTIFICADORES = auto()
    NUMERO = auto()
    ATRIBUICAO_OU_IGUALDADE = auto()
    OPERADORES_RELACIONAIS = auto()
    ERROR = auto()

# Classe Lexer

class Lexer:
    def __init__(self, source):
        self.source = source
        self.index = 0
        self.linha = 1
        self.keywords = {
            "public": TokenType.KEYWORD_PUBLIC,
            "class": TokenType.KEYWORD_CLASS,
            "static": TokenType.KEYWORD_STATIC,
            "void": TokenType.KEYWORD_VOID,
            "main": TokenType.KEYWORD_MAIN,
            "String": TokenType.KEYWORD_STRING,
            "double": TokenType.KEYWORD_TDOUBLE,
            "if": TokenType.KEYWORD_IF,
            "else": TokenType.KEYWORD_ELSE,
            "while": TokenType.KEYWORD_WHILE,
            "System.out.println": TokenType.KEYWORD_PRINT,
            "lerDouble": TokenType.KEYWORD_READ,
        }

    def verificarPrint(self):
        casoNao = self.index
        lexema = ""
        expected = ".out.println"
        for ch in expected:
            if self.fimLexema() or self.peek() != ch:
                self.index = casoNao
                return ""
            lexema += self.proximo()
        return lexema

    def peek(self):
        if self.fimLexema():
            return '\0'
        return self.source[self.index]

    def proximo(self):
        if self.fimLexema():
            return '\0'
        c = self.source[self.index]
        self.index += 1
        if c == '\n':
            self.linha += 1
        return c

    def fimLexema(self):
        return self.index >= len(self.source)

    def ignoraEspaco(self):
        while not self.fimLexema() and self.peek().isspace():
            self.proximo()

    def proximoToken(self):
        self.ignoraEspaco()
        if self.fimLexema():
            return Token(TokenType.END_OF_FILE, "", self.linha)

        estado = LexerState.INICIAL
        lexema = ""
        linhaToken = self.linha

        while True:
            if self.fimLexema():
                if estado == LexerState.IDENTIFICADORES:
                    if lexema == "System":
                        lexemaCompleto = lexema + self.verificarPrint()
                        if lexemaCompleto == "System.out.println":
                            return Token(TokenType.KEYWORD_PRINT, lexemaCompleto, linhaToken)
                        else:
                            return Token(TokenType.KEYWORD_ID, lexemaCompleto, linhaToken)
                    return Token(self.keywords.get(lexema, TokenType.KEYWORD_ID), lexema, linhaToken)
                elif estado == LexerState.NUMERO:
                    return Token(TokenType.KEYWORD_NUMBER, lexema, linhaToken)
                else:
                    return Token(TokenType.UNKNOWN, lexema, linhaToken)

            c = self.peek()

            if estado == LexerState.INICIAL:
                if c.isalpha():
                    lexema += self.proximo()
                    estado = LexerState.IDENTIFICADORES
                elif c.isdigit():
                    lexema += self.proximo()
                    estado = LexerState.NUMERO
                elif c == '=':
                    lexema += self.proximo()
                    estado = LexerState.ATRIBUICAO_OU_IGUALDADE
                elif c in ['<', '>', '!']:
                    lexema += self.proximo()
                    estado = LexerState.OPERADORES_RELACIONAIS
                else:
                    self.proximo()
                    return {
                        '{': Token(TokenType.KEYWORD_LBRACE, '{', linhaToken),
                        '}': Token(TokenType.KEYWORD_RBRACE, '}', linhaToken),
                        '/': Token(TokenType.KEYWORD_DIV, '/', linhaToken),
                        '+': Token(TokenType.KEYWORD_PLUS, '+', linhaToken),
                        ';': Token(TokenType.KEYWORD_SEMICOLON, ';', linhaToken),
                        '(': Token(TokenType.KEYWORD_LPAR, '(', linhaToken),
                        ')': Token(TokenType.KEYWORD_RPAR, ')', linhaToken),
                        '[': Token(TokenType.KEYWORD_LCOL, '[', linhaToken),
                        ']': Token(TokenType.KEYWORD_RCOL, ']', linhaToken),
                        ',': Token(TokenType.KEYWORD_COMMA, ',', linhaToken),
                        '-': Token(TokenType.KEYWORD_SUB, '-', linhaToken),
                        '*': Token(TokenType.KEYWORD_MULT, '*', linhaToken),
                    }.get(c, Token(TokenType.UNKNOWN, c, linhaToken))

            elif estado == LexerState.IDENTIFICADORES:
                if c.isalnum() or c == '_':
                    lexema += self.proximo()
                elif lexema == "System" and c == '.':
                    lexemaCompleto = lexema + self.verificarPrint()
                    if lexemaCompleto == "System.out.println":
                        return Token(TokenType.KEYWORD_PRINT, lexemaCompleto, linhaToken)
                    else:
                        return Token(TokenType.KEYWORD_ID, lexemaCompleto, linhaToken)
                else:
                    return Token(self.keywords.get(lexema, TokenType.KEYWORD_ID), lexema, linhaToken)

            elif estado == LexerState.OPERADORES_RELACIONAIS:
                c = self.peek()
                if lexema == '<':
                    if c == '=':
                        self.proximo()
                        return Token(TokenType.KEYWORD_LE, "<=", linhaToken)
                    return Token(TokenType.KEYWORD_L, "<", linhaToken)
                elif lexema == '>':
                    if c == '=':
                        self.proximo()
                        return Token(TokenType.KEYWORD_GE, ">=", linhaToken)
                    return Token(TokenType.KEYWORD_G, ">", linhaToken)
                elif lexema == '!':
                    if c == '=':
                        self.proximo()
                        return Token(TokenType.KEYWORD_DIF, "!=", linhaToken)

            elif estado == LexerState.NUMERO:
                if c.isdigit():
                    lexema += self.proximo()
                elif c == '.' and '.' not in lexema:
                    lexema += self.proximo()
                else:
                    return Token(TokenType.KEYWORD_NUMBER, lexema, linhaToken)

            elif estado == LexerState.ATRIBUICAO_OU_IGUALDADE:
                if c == '=':
                    lexema += self.proximo()
                    return Token(TokenType.KEYWORD_EQUAL, lexema, linhaToken)
                return Token(TokenType.KEYWORD_ATBR, lexema, linhaToken)

# Tabela LL(1) Preditiva

tabela: Dict[Tuple[str, str], List[str]] = {}

def construir_tabela():
    tabela.clear()

    # PROG -> public class id { public static void main ( String [ ] id ) { GERAR_CODIGO_INPP CMDS GERAR_CODIGO_PARA } }
    tabela[("PROG", "KEYWORD_PUBLIC")] = [
        "KEYWORD_PUBLIC","KEYWORD_CLASS","KEYWORD_ID","KEYWORD_LBRACE",
        "KEYWORD_PUBLIC","KEYWORD_STATIC","KEYWORD_VOID","KEYWORD_MAIN",
        "KEYWORD_LPAR","KEYWORD_STRING","KEYWORD_LCOL","KEYWORD_RCOL","KEYWORD_ID","KEYWORD_RPAR",
        "KEYWORD_LBRACE","GERAR_CODIGO_INPP","CMDS","GERAR_CODIGO_PARA","KEYWORD_RBRACE","KEYWORD_RBRACE"
    ]

    # DC -> VAR MAIS_CMDS
    tabela[("DC", "KEYWORD_TDOUBLE")] = ["VAR","MAIS_CMDS"]

    # VAR -> TIPO VARS
    tabela[("VAR", "KEYWORD_TDOUBLE")] = ["TIPO","VARS"]

    # VARS -> id GERAR_CODIGO_DECL_VAR MAIS_VAR
    tabela[("VARS", "KEYWORD_ID")] = ["KEYWORD_ID","GERAR_CODIGO_DECL_VAR","MAIS_VAR"]

    # MAIS_VAR -> , VARS | λ
    tabela[("MAIS_VAR", "KEYWORD_COMMA")] = ["KEYWORD_COMMA","VARS"]
    tabela[("MAIS_VAR", "KEYWORD_SEMICOLON")] = []  # FOLLOW(MAIS_VAR)

    # TIPO -> double
    tabela[("TIPO", "KEYWORD_TDOUBLE")] = ["KEYWORD_TDOUBLE"]

    # CMDS -> CMD MAIS_CMDS | CMD_COND CMDS | DC | λ
    tabela[("CMDS", "KEYWORD_PRINT")] = ["CMD","MAIS_CMDS"]
    tabela[("CMDS", "KEYWORD_ID")] = ["CMD","MAIS_CMDS"]
    tabela[("CMDS", "KEYWORD_IF")] = ["CMD_COND","CMDS"]
    tabela[("CMDS", "KEYWORD_WHILE")] = ["CMD_COND","CMDS"]
    tabela[("CMDS", "KEYWORD_TDOUBLE")] = ["DC"]
    tabela[("CMDS", "KEYWORD_RBRACE")] = []  # FOLLOW(CMDS)

    # MAIS_CMDS -> ; CMDS
    tabela[("MAIS_CMDS", "KEYWORD_SEMICOLON")] = ["KEYWORD_SEMICOLON","CMDS"]

    # CMD_COND -> if ( CONDICAO ) GERAR_CODIGO_DSVF { CMDS } GERAR_CODIGO_DSVI GERAR_CODIGO_BACKPATCH_DSVF PFALSA
    tabela[("CMD_COND", "KEYWORD_IF")] = [
        "KEYWORD_IF","KEYWORD_LPAR","CONDICAO","KEYWORD_RPAR",
        "GERAR_CODIGO_DSVF",
        "KEYWORD_LBRACE","CMDS","KEYWORD_RBRACE",
        "GERAR_CODIGO_DSVI","GERAR_CODIGO_BACKPATCH_DSVF","PFALSA"
    ]
    # CMD_COND -> while ( CONDICAO ) GERAR_CODIGO_DSVF_WHILE { CMDS } GERAR_CODIGO_DSVI_WHILE GERAR_CODIGO_BACKPATCH_DSVF
    tabela[("CMD_COND", "KEYWORD_WHILE")] = [
        "KEYWORD_WHILE",
        "GERAR_CODIGO_MARQUE_WHILE_START",
        "KEYWORD_LPAR","CONDICAO","KEYWORD_RPAR",
        "GERAR_CODIGO_DSVF_WHILE",
        "KEYWORD_LBRACE","CMDS","KEYWORD_RBRACE",
        "GERAR_CODIGO_DSVI_WHILE","GERAR_CODIGO_BACKPATCH_DSVF"
    ]

    # CMD -> System.out.println ( EXPRESSAO ) GERAR_CODIGO_IMPR | id RESTO_IDENT
    tabela[("CMD", "KEYWORD_PRINT")] = ["KEYWORD_PRINT","KEYWORD_LPAR","EXPRESSAO","KEYWORD_RPAR","GERAR_CODIGO_IMPR"]
    tabela[("CMD", "KEYWORD_ID")] = ["KEYWORD_ID","RESTO_IDENT"]  # RESTO_IDENT

    # PFALSA -> else { CMDS } | λ
    tabela[("PFALSA", "KEYWORD_ELSE")] = ["KEYWORD_ELSE","KEYWORD_LBRACE","CMDS","KEYWORD_RBRACE","GERAR_CODIGO_BACKPATCH_DSVI"]
    # FOLLOW(PFALSA)
    for tk in ["KEYWORD_PRINT","KEYWORD_ID","KEYWORD_IF","KEYWORD_WHILE","KEYWORD_TDOUBLE","KEYWORD_RBRACE"]:
        tabela.setdefault(("PFALSA", tk), [])

    # RESTO_IDENT -> = EXP_IDENT GERAR_CODIGO_ARMZ
    tabela[("RESTO_IDENT", "KEYWORD_ATBR")] = ["KEYWORD_ATBR","EXP_IDENT","GERAR_CODIGO_ARMZ"]

    # EXP_IDENT -> lerDouble() GERAR_CODIGO_LEIT | EXPRESSAO
    tabela[("EXP_IDENT", "KEYWORD_READ")] = ["KEYWORD_READ","KEYWORD_LPAR","KEYWORD_RPAR","GERAR_CODIGO_LEIT"]
    tabela[("EXP_IDENT", "KEYWORD_SUB")] = ["EXPRESSAO"]
    tabela[("EXP_IDENT", "KEYWORD_ID")] = ["EXPRESSAO"]
    tabela[("EXP_IDENT", "KEYWORD_NUMBER")] = ["EXPRESSAO"]
    tabela[("EXP_IDENT", "KEYWORD_LPAR")] = ["EXPRESSAO"]

    # CONDICAO -> EXPRESSAO RELACAO EXPRESSAO GERAR_CODIGO_REL
    tabela[("CONDICAO", "KEYWORD_SUB")] = ["EXPRESSAO","RELACAO","EXPRESSAO","GERAR_CODIGO_REL"]
    tabela[("CONDICAO", "KEYWORD_ID")] = ["EXPRESSAO","RELACAO","EXPRESSAO","GERAR_CODIGO_REL"]
    tabela[("CONDICAO", "KEYWORD_NUMBER")] = ["EXPRESSAO","RELACAO","EXPRESSAO","GERAR_CODIGO_REL"]
    tabela[("CONDICAO", "KEYWORD_LPAR")] = ["EXPRESSAO","RELACAO","EXPRESSAO","GERAR_CODIGO_REL"]

    # RELACAO -> == | != | >= | <= | > | <
    tabela[("RELACAO", "KEYWORD_EQUAL")] = ["KEYWORD_EQUAL"]
    tabela[("RELACAO", "KEYWORD_DIF")] = ["KEYWORD_DIF"]
    tabela[("RELACAO", "KEYWORD_GE")] = ["KEYWORD_GE"]
    tabela[("RELACAO", "KEYWORD_LE")] = ["KEYWORD_LE"]
    tabela[("RELACAO", "KEYWORD_G")] = ["KEYWORD_G"]
    tabela[("RELACAO", "KEYWORD_L")] = ["KEYWORD_L"]

    # EXPRESSAO -> TERMO OUTROS_TERMOS
    tabela[("EXPRESSAO", "KEYWORD_SUB")] = ["TERMO","OUTROS_TERMOS"]
    tabela[("EXPRESSAO", "KEYWORD_ID")] = ["TERMO","OUTROS_TERMOS"]
    tabela[("EXPRESSAO", "KEYWORD_NUMBER")] = ["TERMO","OUTROS_TERMOS"]
    tabela[("EXPRESSAO", "KEYWORD_LPAR")] = ["TERMO","OUTROS_TERMOS"]

    # TERMO -> OP_UN FATOR MAIS_FATORES
    tabela[("TERMO", "KEYWORD_SUB")] = ["OP_UN","FATOR","MAIS_FATORES"]
    tabela[("TERMO", "KEYWORD_ID")] = ["OP_UN","FATOR","MAIS_FATORES"]
    tabela[("TERMO", "KEYWORD_NUMBER")] = ["OP_UN","FATOR","MAIS_FATORES"]
    tabela[("TERMO", "KEYWORD_LPAR")] = ["OP_UN","FATOR","MAIS_FATORES"]

    # OP_UN -> - | λ
    tabela[("OP_UN", "KEYWORD_SUB")] = ["KEYWORD_SUB"]
    for tk in ["KEYWORD_ID","KEYWORD_NUMBER","KEYWORD_LPAR"]:
        tabela[("OP_UN", tk)] = []

    # FATOR -> id GERAR_CODIGO_CRVL | numero_real GERAR_CODIGO_CRCT | ( EXPRESSAO )
    tabela[("FATOR", "KEYWORD_ID")] = ["KEYWORD_ID","GERAR_CODIGO_CRVL"]
    tabela[("FATOR", "KEYWORD_NUMBER")] = ["KEYWORD_NUMBER","GERAR_CODIGO_CRCT"]
    tabela[("FATOR", "KEYWORD_LPAR")] = ["KEYWORD_LPAR","EXPRESSAO","KEYWORD_RPAR"]

    # OUTROS_TERMOS -> OP_AD TERMO GERAR_CODIGO_OP_AD OUTROS_TERMOS | λ
    tabela[("OUTROS_TERMOS", "KEYWORD_SUB")] = ["OP_AD","TERMO","GERAR_CODIGO_OP_AD","OUTROS_TERMOS"]
    tabela[("OUTROS_TERMOS", "KEYWORD_PLUS")] = ["OP_AD","TERMO","GERAR_CODIGO_OP_AD","OUTROS_TERMOS"]
    # FOLLOW(OUTROS_TERMOS)
    for tk in ["KEYWORD_EQUAL","KEYWORD_DIF","KEYWORD_GE","KEYWORD_LE","KEYWORD_G","KEYWORD_L","KEYWORD_RPAR","KEYWORD_SEMICOLON"]:
        tabela[("OUTROS_TERMOS", tk)] = []

    # OP_AD -> + | -
    tabela[("OP_AD", "KEYWORD_SUB")] = ["KEYWORD_SUB"]
    tabela[("OP_AD", "KEYWORD_PLUS")] = ["KEYWORD_PLUS"]

    # MAIS_FATORES -> OP_MUL FATOR GERAR_CODIGO_OP_MUL MAIS_FATORES | λ
    tabela[("MAIS_FATORES", "KEYWORD_MULT")] = ["OP_MUL","FATOR","GERAR_CODIGO_OP_MUL","MAIS_FATORES"]
    tabela[("MAIS_FATORES", "KEYWORD_DIV")] = ["OP_MUL","FATOR","GERAR_CODIGO_OP_MUL","MAIS_FATORES"]
    # FOLLOW(MAIS_FATORES)
    for tk in ["KEYWORD_SUB","KEYWORD_PLUS","KEYWORD_EQUAL","KEYWORD_DIF","KEYWORD_GE","KEYWORD_LE","KEYWORD_G","KEYWORD_L","KEYWORD_RPAR","KEYWORD_SEMICOLON"]:
        tabela[("MAIS_FATORES", tk)] = []

    # OP_MUL -> * | /
    tabela[("OP_MUL", "KEYWORD_MULT")] = ["KEYWORD_MULT"]
    tabela[("OP_MUL", "KEYWORD_DIV")] = ["KEYWORD_DIV"]


# Analisador Sintatico + O resto

gerador = GeradorDeCodigo()

def token_tipo_to_string(tipo):
    return tipo.name

def analisar(tokens: List[Token]) -> bool:
    tokens = deque(tokens)
    tokens.append(Token(TokenType.END_OF_FILE, "", tokens[-1].linha if tokens else 1))

    pilha = deque()
    pilha.append("$")
    pilha.append("PROG")

    semPilha = []            
    dsvfPilha = []          
    dsviPilha = []           
    whileComecoPilha = []    

    processandoDeclaracao = False

    while pilha:
        topo = pilha[-1]
        tokenAtual = tokens[0]
        atual = token_tipo_to_string(tokenAtual.tipo)

        # Se topo for um GERAR_CODIGO_
        if isinstance(topo, str) and topo.startswith("GERAR_CODIGO_"):
            pilha.pop()
            try:
                executar_acao(topo, semPilha, dsvfPilha, dsviPilha, whileComecoPilha, tokens, gerador)
            except Exception as e:
                print(f"Erro de ação '{topo}': {e}")
                return False
            continue

        # Se topo for símbolo terminal
        if isinstance(topo, str) and (topo.startswith("KEYWORD_") or topo == "END_OF_FILE"):
            if topo == atual:
                if tokenAtual.tipo == TokenType.KEYWORD_ID:
                    semPilha.append(("ID", tokenAtual.lexema, tokenAtual.linha))
                elif tokenAtual.tipo == TokenType.KEYWORD_NUMBER:
                    semPilha.append(("NUMBER", tokenAtual.lexema, tokenAtual.linha))
                elif tokenAtual.tipo in (TokenType.KEYWORD_PLUS, TokenType.KEYWORD_SUB,
                                          TokenType.KEYWORD_MULT, TokenType.KEYWORD_DIV,
                                          TokenType.KEYWORD_EQUAL, TokenType.KEYWORD_DIF,
                                          TokenType.KEYWORD_GE, TokenType.KEYWORD_LE,
                                          TokenType.KEYWORD_G, TokenType.KEYWORD_L):
                    semPilha.append(("OP", tokenAtual.lexema, tokenAtual.linha))
                pilha.pop()
                tokens.popleft()

                if topo in ["VAR", "TIPO"]:
                    processandoDeclaracao = True
                if topo == "KEYWORD_SEMICOLON" and processandoDeclaracao:
                    processandoDeclaracao = False
                continue
            else:
                print(f"Erro de sintaxe: token inesperado '{atual}' ('{tokenAtual.lexema}'), esperado '{topo}' na linha {tokenAtual.linha}")
                return False
            
        if topo == "$" and atual == "END_OF_FILE":
            gerador.salvar("codigoCompilado.txt")
            print("Análise concluída com sucesso!")
            break

        # Se topo é um não-terminal
        if isinstance(topo, str):
            chave = (topo, atual)
            if chave in tabela:
                pilha.pop()
                producao = tabela[chave]
                for simbolo in reversed(producao):
                    if simbolo != "":
                        pilha.append(simbolo)
                continue
            else:
                print(f"Erro de sintaxe: nenhuma regra para topo '{topo}' com token '{atual}' na linha {tokenAtual.linha}")
                return False

        print(f"Erro interno: tipo desconhecido no topo da pilha '{topo}'")
        return False

    return True


# Implementação de GERAR_CODIGO_

def executar_acao(acao, semPilha, dsvfPilha, dsviPilha, whileComecoPilha, tokens, gerador):

    def popId():
        for i in range(len(semPilha)-1, -1, -1):
            tag, lex, ln = semPilha[i]
            if tag == "ID":
                semPilha.pop(i)
                return lex, ln
        raise Exception("ID esperado na pilha semântica para ação")

    def popNumber():
        for i in range(len(semPilha)-1, -1, -1):
            tag, lex, ln = semPilha[i]
            if tag == "NUMBER":
                semPilha.pop(i)
                return lex, ln
        raise Exception("NUMBER esperado na pilha semântica para ação")

    def popOp():
        for i in range(len(semPilha)-1, -1, -1):
            tag, lex, ln = semPilha[i]
            if tag == "OP":
                semPilha.pop(i)
                return lex
        raise Exception("OP esperado na pilha semântica para ação")

    if acao == "GERAR_CODIGO_INPP":
        gerador.adicionar("INPP")

    elif acao == "GERAR_CODIGO_PARA":
        gerador.adicionar("PARA")

    elif acao == "GERAR_CODIGO_DECL_VAR":
        idlex, ln = popId()
        gerador.declararVariavel(idlex)

    elif acao == "GERAR_CODIGO_CRVL":
        idlex, ln = popId()
        entrada = gerador.buscarEntrada(idlex)
        if not entrada:
            raise Exception(f"Erro semântico (gerador): variável '{idlex}' não declarada (linha {ln})")
        gerador.adicionar(f"CRVL {entrada.endRel}")

    elif acao == "GERAR_CODIGO_CRCT":
        numlex, ln = popNumber()
        gerador.adicionar(f"CRCT {numlex}")

    elif acao == "GERAR_CODIGO_IMPR":
        gerador.adicionar("IMPR")

    elif acao == "GERAR_CODIGO_LEIT":
        gerador.adicionar("LEIT")

    elif acao == "GERAR_CODIGO_ARMZ":
        idlex, ln = popId()
        entrada = gerador.buscarEntrada(idlex)
        if not entrada:
            raise Exception(f"Erro semântico (gerador): variável '{idlex}' não declarada (linha {ln})")
        gerador.adicionar(f"ARMZ {entrada.endRel}")

    elif acao == "GERAR_CODIGO_OP_AD":
        op = popOp()
        if op == '+':
            gerador.adicionar("SOMA")
        elif op == '-':
            gerador.adicionar("SUBT")
        else:
            raise Exception(f"Operador ad inválido: {op}")

    elif acao == "GERAR_CODIGO_OP_MUL":
        op = popOp()
        if op == '*':
            gerador.adicionar("MULT")
        elif op == '/':
            gerador.adicionar("DIVI")
        else:
            raise Exception(f"Operador mul inválido: {op}")

    elif acao == "GERAR_CODIGO_REL":
        rel = popOp()
        op_map = {
            '<': 'CPME', '>': 'CPMA', '==': 'CPIG',
            '!=': 'CDES', '<=': 'CPMI', '>=': 'CMAI'
        }
        if rel not in op_map:
            raise Exception(f"Operador relacional desconhecido: {rel}")
        gerador.adicionar(op_map[rel])

    elif acao == "GERAR_CODIGO_DSVF":
        addr = gerador.adicionar("DSVF END_A_DECLARAR")
        dsvfPilha.append(addr)

    elif acao == "GERAR_CODIGO_DSVI":
        addr = gerador.adicionar("DSVI END_A_DECLARAR")
        dsviPilha.append(addr)

    elif acao == "GERAR_CODIGO_BACKPATCH_DSVF":
        if not dsvfPilha:
            raise Exception("Backpatch DSVF sem endereço pendente.")
        addr = dsvfPilha.pop()
        destino = len(gerador.codigo_c)
        gerador.backpatch(addr, destino)

    elif acao == "GERAR_CODIGO_BACKPATCH_DSVI":
        if not dsviPilha:
            return
        addr = dsviPilha.pop()
        destino = len(gerador.codigo_c)
        gerador.backpatch(addr, destino)

    elif acao == "GERAR_CODIGO_MARQUE_WHILE_START":
        start = len(gerador.codigo_c)
        whileComecoPilha.append(start)

    elif acao == "GERAR_CODIGO_DSVF_WHILE":
        addr = gerador.adicionar("DSVF END_A_DECLARAR")
        dsvfPilha.append(addr)

    elif acao == "GERAR_CODIGO_DSVI_WHILE":
        if not whileComecoPilha:
            raise Exception("GERAR_CODIGO_DSVI_WHILE sem marca de início do while.")
        start_addr = whileComecoPilha.pop()
        gerador.adicionar(f"DSVI {start_addr}")

    else:
        raise Exception(f"Ação desconhecida: {acao}")

# Execução Principal (script)

if __name__ == "__main__":
    try:
        with open("codigoPraCompilar.txt", "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print("Erro ao abrir o arquivo codigoPraCompilar.txt")
        exit(1)

    # Analise Lexica
    lexer = Lexer(code)
    tokensGerados = []
    while True:
        token = lexer.proximoToken()
        tokensGerados.append(token)
        if token.tipo == TokenType.END_OF_FILE:
            break

    construir_tabela()

    # print("--- Tokens ---")
    # for t in tokensGerados:
    #     print(t)

    print("--- Análise Sintática, Semântica e Geração de Código ---")
    resultado = analisar(tokensGerados)
    if resultado:
        print("\nCódigo compilado com sucesso.")
    else:
        print("\nOcorreu um erro.")
