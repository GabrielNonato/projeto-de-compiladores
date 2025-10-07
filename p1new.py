import string
from typing import List, Dict, Tuple
from collections import deque
from enum import Enum, auto

# -----------------------------
# Definições de Tipos de Token
# -----------------------------
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

# -----------------------------
# Estrutura de Token
# -----------------------------
class Token:
    def __init__(self, token_type, lexeme, line):
        self.type = token_type
        self.lexeme = lexeme
        self.line = line

    def __repr__(self):
        return f"Token({self.type.name}, '{self.lexeme}', line={self.line})"

# -----------------------------
# Tabela de Símbolos Simples
# -----------------------------
class TabelaSimbolo:
    def __init__(self):
        self.simbolos = {}

    def declare(self, nome, tipo, linha):
        if nome in self.simbolos:
            raise Exception(f"Erro semântico: variável '{nome}' já declarada (linha {linha})")
        self.simbolos[nome] = {"type": tipo, "linha": linha}

    def exists(self, nome):
        return nome in self.simbolos

# -----------------------------
# Gerador de Código (MaqHipo)
# -----------------------------
class EntradaTS:
    def __init__(self, lexema, end_rel, prim_instr=-1):
        self.lexema = lexema
        self.tipo = "double"
        self.end_rel = end_rel
        self.prim_instr = prim_instr

class GeradorDeCodigo:
    def __init__(self):
        self.codigo_c = []
        self.ts = {}
        self.contador_end_rel = 0

    def emit(self, instrucao):
        """Adiciona uma instrução ao código C e retorna o endereço da instrução."""
        self.codigo_c.append(f"{instrucao}")
        return len(self.codigo_c) - 1

    def declarar_variavel(self, id_lexema):
        """Registra na TS do gerador e emite ALME 1."""
        if id_lexema in self.ts:
            raise Exception(f"Erro Semântico (Gerador): Variável '{id_lexema}' já declarada.")
        entrada = EntradaTS(id_lexema, self.contador_end_rel)
        self.ts[id_lexema] = entrada
        self.contador_end_rel += 1
        self.emit("ALME 1")

    def buscar_entrada(self, id_lexema):
        return self.ts.get(id_lexema)

    def backpatch(self, endereco_linha, destino):
        instrucao = self.codigo_c[endereco_linha]
        partes = instrucao.split()
        if len(partes) == 2 and partes[1] == 'P_PENDENTE':
            self.codigo_c[endereco_linha] = f"{partes[0]} {destino}"
        else:
            raise Exception(f"Erro Interno: Backpatch em instrução inválida: {instrucao}")

    def imprimir_codigo_objeto(self):
        print("\n" + "="*40)
        print("Código Objeto para MaqHipo")
        print("="*40)
        for i, instrucao in enumerate(self.codigo_c):
            print(f"{i}. {instrucao}")
        print("="*40)

    def salvar(self, nome_arquivo="codigo.maq"):
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            for instr in self.codigo_c:
                f.write(instr + "\n")

# -----------------------------
# Estados do AFD (Lexer)
# -----------------------------
class LexerState(Enum):
    START = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    ASSIGN_OR_EQUAL = auto()
    RELATIONAL_OP = auto()
    ERROR = auto()

# -----------------------------
# Classe Lexer (mantida do seu Código 2)
# -----------------------------
class Lexer:
    def __init__(self, source):
        self.source = source
        self.index = 0
        self.line = 1
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

    def _try_read_print(self):
        pos_backup = self.index
        lexeme = ""
        expected = ".out.println"
        for ch in expected:
            if self.is_at_end() or self.peek() != ch:
                self.index = pos_backup
                return ""
            lexeme += self.advance()
        return lexeme

    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.index]

    def advance(self):
        if self.is_at_end():
            return '\0'
        c = self.source[self.index]
        self.index += 1
        if c == '\n':
            self.line += 1
        return c

    def is_at_end(self):
        return self.index >= len(self.source)

    def skip_whitespace(self):
        while not self.is_at_end() and self.peek().isspace():
            self.advance()

    def get_next_token(self):
        self.skip_whitespace()
        if self.is_at_end():
            return Token(TokenType.END_OF_FILE, "", self.line)

        state = LexerState.START
        lexeme = ""
        token_start_line = self.line

        while True:
            if self.is_at_end():
                if state == LexerState.IDENTIFIER:
                    if lexeme == "System":
                        lexeme_full = lexeme + self._try_read_print()
                        if lexeme_full == "System.out.println":
                            return Token(TokenType.KEYWORD_PRINT, lexeme_full, token_start_line)
                        else:
                            return Token(TokenType.KEYWORD_ID, lexeme_full, token_start_line)
                    return Token(self.keywords.get(lexeme, TokenType.KEYWORD_ID), lexeme, token_start_line)
                elif state == LexerState.NUMBER:
                    return Token(TokenType.KEYWORD_NUMBER, lexeme, token_start_line)
                else:
                    return Token(TokenType.UNKNOWN, lexeme, token_start_line)

            c = self.peek()

            if state == LexerState.START:
                if c.isalpha():
                    lexeme += self.advance()
                    state = LexerState.IDENTIFIER
                elif c.isdigit():
                    lexeme += self.advance()
                    state = LexerState.NUMBER
                elif c == '=':
                    lexeme += self.advance()
                    state = LexerState.ASSIGN_OR_EQUAL
                elif c in ['<', '>', '!']:
                    lexeme += self.advance()
                    state = LexerState.RELATIONAL_OP
                else:
                    self.advance()
                    return {
                        '{': Token(TokenType.KEYWORD_LBRACE, '{', token_start_line),
                        '}': Token(TokenType.KEYWORD_RBRACE, '}', token_start_line),
                        '/': Token(TokenType.KEYWORD_DIV, '/', token_start_line),
                        '+': Token(TokenType.KEYWORD_PLUS, '+', token_start_line),
                        ';': Token(TokenType.KEYWORD_SEMICOLON, ';', token_start_line),
                        '(': Token(TokenType.KEYWORD_LPAR, '(', token_start_line),
                        ')': Token(TokenType.KEYWORD_RPAR, ')', token_start_line),
                        '[': Token(TokenType.KEYWORD_LCOL, '[', token_start_line),
                        ']': Token(TokenType.KEYWORD_RCOL, ']', token_start_line),
                        ',': Token(TokenType.KEYWORD_COMMA, ',', token_start_line),
                        '-': Token(TokenType.KEYWORD_SUB, '-', token_start_line),
                        '*': Token(TokenType.KEYWORD_MULT, '*', token_start_line),
                    }.get(c, Token(TokenType.UNKNOWN, c, token_start_line))

            elif state == LexerState.IDENTIFIER:
                if c.isalnum() or c == '_':
                    lexeme += self.advance()
                elif lexeme == "System" and c == '.':
                    lexeme_full = lexeme + self._try_read_print()
                    if lexeme_full == "System.out.println":
                        return Token(TokenType.KEYWORD_PRINT, lexeme_full, token_start_line)
                    else:
                        return Token(TokenType.KEYWORD_ID, lexeme_full, token_start_line)
                else:
                    return Token(self.keywords.get(lexeme, TokenType.KEYWORD_ID), lexeme, token_start_line)

            elif state == LexerState.RELATIONAL_OP:
                c = self.peek()
                if lexeme == '<':
                    if c == '=':
                        self.advance()
                        return Token(TokenType.KEYWORD_LE, "<=", token_start_line)
                    return Token(TokenType.KEYWORD_L, "<", token_start_line)
                elif lexeme == '>':
                    if c == '=':
                        self.advance()
                        return Token(TokenType.KEYWORD_GE, ">=", token_start_line)
                    return Token(TokenType.KEYWORD_G, ">", token_start_line)
                elif lexeme == '!':
                    if c == '=':
                        self.advance()
                        return Token(TokenType.KEYWORD_DIF, "!=", token_start_line)

            elif state == LexerState.NUMBER:
                if c.isdigit():
                    lexeme += self.advance()
                elif c == '.' and '.' not in lexeme:
                    lexeme += self.advance()
                else:
                    return Token(TokenType.KEYWORD_NUMBER, lexeme, token_start_line)

            elif state == LexerState.ASSIGN_OR_EQUAL:
                if c == '=':
                    lexeme += self.advance()
                    return Token(TokenType.KEYWORD_EQUAL, lexeme, token_start_line)
                return Token(TokenType.KEYWORD_ATBR, lexeme, token_start_line)

# ----------------------------------------------------------------
# Tabela LL(1)
# ----------------------------------------------------------------
tabela: Dict[Tuple[str, str], List[str]] = {}

def construir_tabela():
    tabela.clear()

    # PROG -> public class id { public static void main ( String [ ] id ) { ACTION_INPP CMDS ACTION_PARA } }
    tabela[("PROG", "KEYWORD_PUBLIC")] = [
        "KEYWORD_PUBLIC","KEYWORD_CLASS","KEYWORD_ID","KEYWORD_LBRACE",
        "KEYWORD_PUBLIC","KEYWORD_STATIC","KEYWORD_VOID","KEYWORD_MAIN",
        "KEYWORD_LPAR","KEYWORD_STRING","KEYWORD_LCOL","KEYWORD_RCOL","KEYWORD_ID","KEYWORD_RPAR",
        "KEYWORD_LBRACE","ACTION_INPP","CMDS","ACTION_PARA","KEYWORD_RBRACE","KEYWORD_RBRACE"
    ]

    # DC -> VAR MAIS_CMDS
    tabela[("DC", "KEYWORD_TDOUBLE")] = ["VAR","MAIS_CMDS"]

    # VAR -> TIPO VARS
    tabela[("VAR", "KEYWORD_TDOUBLE")] = ["TIPO","VARS"]

    # VARS -> id ACTION_DECL_VAR MAIS_VAR
    tabela[("VARS", "KEYWORD_ID")] = ["KEYWORD_ID","ACTION_DECL_VAR","MAIS_VAR"]

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

    # CMD_COND -> if ( CONDICAO ) ACTION_DSVF { CMDS } ACTION_DSVI ACTION_BACKPATCH_DSVF PFALSA
    tabela[("CMD_COND", "KEYWORD_IF")] = [
        "KEYWORD_IF","KEYWORD_LPAR","CONDICAO","KEYWORD_RPAR",
        "ACTION_DSVF",
        "KEYWORD_LBRACE","CMDS","KEYWORD_RBRACE",
        "ACTION_DSVI","ACTION_BACKPATCH_DSVF","PFALSA"
    ]
    # CMD_COND -> while ( CONDICAO ) ACTION_DSVF_WHILE { CMDS } ACTION_DSVI_WHILE ACTION_BACKPATCH_DSVF
    tabela[("CMD_COND", "KEYWORD_WHILE")] = [
        "KEYWORD_WHILE",
        "ACTION_MARK_WHILE_START",
        "KEYWORD_LPAR","CONDICAO","KEYWORD_RPAR",
        "ACTION_DSVF_WHILE",
        "KEYWORD_LBRACE","CMDS","KEYWORD_RBRACE",
        "ACTION_DSVI_WHILE","ACTION_BACKPATCH_DSVF"
    ]

    # CMD -> System.out.println ( EXPRESSAO ) ACTION_IMPR | id RESTO_IDENT
    tabela[("CMD", "KEYWORD_PRINT")] = ["KEYWORD_PRINT","KEYWORD_LPAR","EXPRESSAO","KEYWORD_RPAR","ACTION_IMPR"]
    tabela[("CMD", "KEYWORD_ID")] = ["KEYWORD_ID","RESTO_IDENT"]  # RESTO_IDENT will contain ARMZ action

    # PFALSA -> else { CMDS } | λ
    tabela[("PFALSA", "KEYWORD_ELSE")] = ["KEYWORD_ELSE","KEYWORD_LBRACE","CMDS","KEYWORD_RBRACE","ACTION_BACKPATCH_DSVI"]
    # FOLLOW(PFALSA)
    for tk in ["KEYWORD_PRINT","KEYWORD_ID","KEYWORD_IF","KEYWORD_WHILE","KEYWORD_TDOUBLE","KEYWORD_RBRACE"]:
        tabela.setdefault(("PFALSA", tk), [])

    # RESTO_IDENT -> = EXP_IDENT ACTION_ARMZ
    tabela[("RESTO_IDENT", "KEYWORD_ATBR")] = ["KEYWORD_ATBR","EXP_IDENT","ACTION_ARMZ"]

    # EXP_IDENT -> lerDouble() ACTION_LEIT | EXPRESSAO
    tabela[("EXP_IDENT", "KEYWORD_READ")] = ["KEYWORD_READ","KEYWORD_LPAR","KEYWORD_RPAR","ACTION_LEIT"]
    # If expression starts with op_un (like '-'), ID or NUMBER or LPAR
    tabela[("EXP_IDENT", "KEYWORD_SUB")] = ["EXPRESSAO"]
    tabela[("EXP_IDENT", "KEYWORD_ID")] = ["EXPRESSAO"]
    tabela[("EXP_IDENT", "KEYWORD_NUMBER")] = ["EXPRESSAO"]
    tabela[("EXP_IDENT", "KEYWORD_LPAR")] = ["EXPRESSAO"]

    # CONDICAO -> EXPRESSAO RELACAO EXPRESSAO ACTION_REL
    tabela[("CONDICAO", "KEYWORD_SUB")] = ["EXPRESSAO","RELACAO","EXPRESSAO","ACTION_REL"]
    tabela[("CONDICAO", "KEYWORD_ID")] = ["EXPRESSAO","RELACAO","EXPRESSAO","ACTION_REL"]
    tabela[("CONDICAO", "KEYWORD_NUMBER")] = ["EXPRESSAO","RELACAO","EXPRESSAO","ACTION_REL"]
    tabela[("CONDICAO", "KEYWORD_LPAR")] = ["EXPRESSAO","RELACAO","EXPRESSAO","ACTION_REL"]

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

    # FATOR -> id ACTION_CRVL | numero_real ACTION_CRCT | ( EXPRESSAO )
    tabela[("FATOR", "KEYWORD_ID")] = ["KEYWORD_ID","ACTION_CRVL"]
    tabela[("FATOR", "KEYWORD_NUMBER")] = ["KEYWORD_NUMBER","ACTION_CRCT"]
    tabela[("FATOR", "KEYWORD_LPAR")] = ["KEYWORD_LPAR","EXPRESSAO","KEYWORD_RPAR"]

    # OUTROS_TERMOS -> OP_AD TERMO ACTION_OP_AD OUTROS_TERMOS | λ
    tabela[("OUTROS_TERMOS", "KEYWORD_SUB")] = ["OP_AD","TERMO","ACTION_OP_AD","OUTROS_TERMOS"]
    tabela[("OUTROS_TERMOS", "KEYWORD_PLUS")] = ["OP_AD","TERMO","ACTION_OP_AD","OUTROS_TERMOS"]
    # FOLLOW(OUTROS_TERMOS)
    for tk in ["KEYWORD_EQUAL","KEYWORD_DIF","KEYWORD_GE","KEYWORD_LE","KEYWORD_G","KEYWORD_L","KEYWORD_RPAR","KEYWORD_SEMICOLON"]:
        tabela[("OUTROS_TERMOS", tk)] = []

    # OP_AD -> + | -
    tabela[("OP_AD", "KEYWORD_SUB")] = ["KEYWORD_SUB"]
    tabela[("OP_AD", "KEYWORD_PLUS")] = ["KEYWORD_PLUS"]

    # MAIS_FATORES -> OP_MUL FATOR ACTION_OP_MUL MAIS_FATORES | λ
    tabela[("MAIS_FATORES", "KEYWORD_MULT")] = ["OP_MUL","FATOR","ACTION_OP_MUL","MAIS_FATORES"]
    tabela[("MAIS_FATORES", "KEYWORD_DIV")] = ["OP_MUL","FATOR","ACTION_OP_MUL","MAIS_FATORES"]
    # FOLLOW(MAIS_FATORES)
    for tk in ["KEYWORD_SUB","KEYWORD_PLUS","KEYWORD_EQUAL","KEYWORD_DIF","KEYWORD_GE","KEYWORD_LE","KEYWORD_G","KEYWORD_L","KEYWORD_RPAR","KEYWORD_SEMICOLON"]:
        tabela[("MAIS_FATORES", tk)] = []

    # OP_MUL -> * | /
    tabela[("OP_MUL", "KEYWORD_MULT")] = ["KEYWORD_MULT"]
    tabela[("OP_MUL", "KEYWORD_DIV")] = ["KEYWORD_DIV"]

# -----------------------------
# Analisador Semântico Integrado + Parser LL(1) (com geração integrada)
# -----------------------------
tabelaDeSimbolos = TabelaSimbolo()
gerador = GeradorDeCodigo()

def token_type_to_string(ttype):
    return ttype.name

def analisar(tokens: List[Token]) -> bool:
    tokens = deque(tokens)
    tokens.append(Token(TokenType.END_OF_FILE, "", tokens[-1].line if tokens else 1))

    pilha = deque()
    pilha.append("$")
    pilha.append("PROG")

    # Pilhas/estruturas auxiliares para semântica e geração
    sem_stack = []            # Armazena lexemas/valores temporários (ids, numbers, operadores)
    dsvf_stack = []           # endereços DSVF pendentes
    dsvi_stack = []           # endereços DSVI pendentes (if)
    while_start_stack = []    # endereços de início da condição do while

    processando_declaracao = False
    ignorando_identificadores = 2

    while pilha:
        topo = pilha[-1]
        atual_token = tokens[0]
        atual = token_type_to_string(atual_token.type)

        # Se topo for um ACTION_* -> executa ação semântica / geração
        if isinstance(topo, str) and topo.startswith("ACTION_"):
            pilha.pop()
            # Executa a ação correspondente
            try:
                executar_acao(topo, sem_stack, dsvf_stack, dsvi_stack, while_start_stack, tokens, gerador)
            except Exception as e:
                print(f"Erro de ação '{topo}': {e}")
                return False
            continue

        # Se topo for símbolo terminal (string começando KEYWORD_ ou END_OF_FILE)
        if isinstance(topo, str) and (topo.startswith("KEYWORD_") or topo == "END_OF_FILE"):
            # Se tokens vazios?
            if topo == atual:
                # Ao consumir token, executa empilhamento semântico (se necessário) antes de remover
                # Ex: ID, NUMBER, operadores, relacionais, etc.
                if atual_token.type == TokenType.KEYWORD_ID:
                    sem_stack.append(("ID", atual_token.lexeme, atual_token.line))
                elif atual_token.type == TokenType.KEYWORD_NUMBER:
                    sem_stack.append(("NUMBER", atual_token.lexeme, atual_token.line))
                elif atual_token.type in (TokenType.KEYWORD_PLUS, TokenType.KEYWORD_SUB,
                                          TokenType.KEYWORD_MULT, TokenType.KEYWORD_DIV,
                                          TokenType.KEYWORD_EQUAL, TokenType.KEYWORD_DIF,
                                          TokenType.KEYWORD_GE, TokenType.KEYWORD_LE,
                                          TokenType.KEYWORD_G, TokenType.KEYWORD_L):
                    # operador/relacional: empilha lexema (por exemplo '+', '-', '==')
                    sem_stack.append(("OP", atual_token.lexeme, atual_token.line))
                # Remove token e desempilha símbolo terminal
                pilha.pop()
                tokens.popleft()
                # Ajustes do analisador semântico original
                if topo in ["VAR", "TIPO"]:
                    processando_declaracao = True
                if topo == "KEYWORD_SEMICOLON" and processando_declaracao:
                    processando_declaracao = False
                continue
            else:
                print(f"Erro de sintaxe: token inesperado '{atual}' ('{atual_token.lexeme}'), esperado '{topo}' na linha {atual_token.line}")
                return False
            
        if topo == "$" and atual == "END_OF_FILE":
            gerador.salvar("programa.maq")
            gerador.imprimir_codigo_objeto()
            print("\n--- Análise Sintática, Semântica e Geração de Código (integrada) ---")
            print("Análise concluída com sucesso!")
            break

        # Se topo é um não-terminal (string)
        if isinstance(topo, str):
            chave = (topo, atual)
            if chave in tabela:
                pilha.pop()
                producao = tabela[chave]
                # empilha a produção em ordem inversa
                for simbolo in reversed(producao):
                    if simbolo != "":
                        pilha.append(simbolo)
                # Quando pushamos um não-terminal que controla declaração, o analisador
                # original já gerencia tabelaDeSimbolos (verificação de declaração/usos).
                # Mantemos essa verificação original: se topo for KEYWORD_ID, etc.
                # (A lógica original do seu código 2 já fazia verificações fora deste loop;
                #  aqui mantemos as ações e gerador integradas.)
                continue
            else:
                print(f"Erro de sintaxe: nenhuma regra para topo '{topo}' com token '{atual}' na linha {atual_token.line}")
                return False

        print(f"Erro interno: tipo desconhecido no topo da pilha '{topo}'")
        return False

    # fim do while: se chegou aqui e tudo consumido corretamente
    # Emitir imprime e salvar o código
    gerador.imprimir_codigo_objeto()
    gerador.salvar("codigo.maq")
    return True

# -----------------------------
# Implementação das ações (ACTION_*)
# -----------------------------
def executar_acao(acao, sem_stack, dsvf_stack, dsvi_stack, while_start_stack, tokens, gerador):
    """
    Executa ações semânticas e de geração de código.
    sem_stack: pilha semântica com tuplas ("ID"/"NUMBER"/"OP", lexema, linha)
    dsvf_stack, dsvi_stack, while_start_stack: pilhas auxiliares
    tokens: deque atual (para obter posição/linha quando necessário)
    gerador: instância de GeradorDeCodigo
    """
    # Funções auxiliares
    def pop_id():
        # retira o último ID válido da sem_stack
        for i in range(len(sem_stack)-1, -1, -1):
            tag, lex, ln = sem_stack[i]
            if tag == "ID":
                sem_stack.pop(i)
                return lex, ln
        raise Exception("ID esperado na pilha semântica para ação")

    def pop_number():
        for i in range(len(sem_stack)-1, -1, -1):
            tag, lex, ln = sem_stack[i]
            if tag == "NUMBER":
                sem_stack.pop(i)
                return lex, ln
        raise Exception("NUMBER esperado na pilha semântica para ação")

    def pop_op():
        for i in range(len(sem_stack)-1, -1, -1):
            tag, lex, ln = sem_stack[i]
            if tag == "OP":
                sem_stack.pop(i)
                return lex
        raise Exception("OP esperado na pilha semântica para ação")

    # Map de ações
    if acao == "ACTION_INPP":
        gerador.emit("INPP")

    elif acao == "ACTION_PARA":
        gerador.emit("PARA")

    elif acao == "ACTION_DECL_VAR":
        # O ID correspondente foi consumido anteriormente e empilhado em sem_stack
        # pop do ID e declarar na TS do gerador (emite ALME 1)
        idlex, ln = pop_id()
        gerador.declarar_variavel(idlex)

    elif acao == "ACTION_CRVL":
        # FATOR: id -> gerar CRVL pos_rel
        idlex, ln = pop_id()
        entrada = gerador.buscar_entrada(idlex)
        if not entrada:
            raise Exception(f"Erro semântico (gerador): variável '{idlex}' não declarada (linha {ln})")
        gerador.emit(f"CRVL {entrada.end_rel}")

    elif acao == "ACTION_CRCT":
        # FATOR: número -> CRCT valor
        numlex, ln = pop_number()
        gerador.emit(f"CRCT {numlex}")

    elif acao == "ACTION_IMPR":
        gerador.emit("IMPR")

    elif acao == "ACTION_LEIT":
        gerador.emit("LEIT")

    elif acao == "ACTION_ARMZ":
        # Assignment: precisa do nome do id que foi deixado na sem_stack quando se chamou VAR/KEYWORD_ID em CMD
        # Neste ponto o ID já foi consumido e colocado na sem_stack anteriormente (na produção CMD -> KEYWORD_ID RESTO_IDENT)
        # então procurar último ID
        # NOTA: nós não removemos ID na ação RESTO_IDENT até agora; então pop_id() aqui devolve o id.
        idlex, ln = pop_id()
        entrada = gerador.buscar_entrada(idlex)
        if not entrada:
            raise Exception(f"Erro semântico (gerador): variável '{idlex}' não declarada (linha {ln})")
        gerador.emit(f"ARMZ {entrada.end_rel}")

    elif acao == "ACTION_OP_AD":
        # Opera sobre a operação aritmética binária aditiva.
        op = pop_op()
        if op == '+':
            gerador.emit("SOMA")
        elif op == '-':
            gerador.emit("SUBT")
        else:
            raise Exception(f"Operador ad inválido: {op}")

    elif acao == "ACTION_OP_MUL":
        op = pop_op()
        if op == '*':
            gerador.emit("MULT")
        elif op == '/':
            gerador.emit("DIVI")
        else:
            raise Exception(f"Operador mul inválido: {op}")

    elif acao == "ACTION_REL":
        # Usada depois de CONDICAO -> EXPRESSAO RELACAO EXPRESSAO
        rel = pop_op()
        op_map = {
            '<': 'CPME', '>': 'CPMA', '==': 'CPIG',
            '!=': 'CDES', '<=': 'CPMI', '>=': 'CMAI'
        }
        if rel not in op_map:
            raise Exception(f"Operador relacional desconhecido: {rel}")
        gerador.emit(op_map[rel])

    elif acao == "ACTION_DSVF":
        # IF: emite DSVF P_PENDENTE e guarda endereço para backpatch
        addr = gerador.emit("DSVF P_PENDENTE")
        dsvf_stack.append(addr)

    elif acao == "ACTION_DSVI":
        # IF: emite DSVI P_PENDENTE e guarda endereço (para pular o else)
        addr = gerador.emit("DSVI P_PENDENTE")
        dsvi_stack.append(addr)

    elif acao == "ACTION_BACKPATCH_DSVF":
        # Para IF e WHILE: backpatch DSVF com o endereço atual
        if not dsvf_stack:
            raise Exception("Backpatch DSVF sem endereço pendente.")
        addr = dsvf_stack.pop()
        destino = len(gerador.codigo_c)
        gerador.backpatch(addr, destino)

    elif acao == "ACTION_BACKPATCH_DSVI":
        # Para o caso 'else': backpatch DSVI com o endereço atual
        if not dsvi_stack:
            # Se não há DSVI, apenas return (sem else)
            return
        addr = dsvi_stack.pop()
        destino = len(gerador.codigo_c)
        gerador.backpatch(addr, destino)

    elif acao == "ACTION_MARK_WHILE_START":
        # Colocar endereço do início da condição (próxima instrução)
        start = len(gerador.codigo_c)
        while_start_stack.append(start)

    elif acao == "ACTION_DSVF_WHILE":
        # Enquanto: depois da condição -> DSVF P_PENDENTE (loop para sair)
        addr = gerador.emit("DSVF P_PENDENTE")
        dsvf_stack.append(addr)

    elif acao == "ACTION_DSVI_WHILE":
        # Enquanto: ao final do corpo, gera DSVI endereco_condicao (volta para condição)
        if not while_start_stack:
            raise Exception("ACTION_DSVI_WHILE sem marca de início do while.")
        start_addr = while_start_stack.pop()
        gerador.emit(f"DSVI {start_addr}")

    else:
        raise Exception(f"Ação desconhecida: {acao}")

# -----------------------------
# Execução Principal (script)
# -----------------------------
if __name__ == "__main__":
    # Lê arquivo de teste (como seu Código 2 original fazia)
    try:
        with open("codigoTestarp1.txt", "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print("Erro ao abrir o arquivo codigoTestarp1.txt")
        exit(1)

    # Tokenização
    lexer = Lexer(code)
    tokens_lexicos = []
    while True:
        token = lexer.get_next_token()
        tokens_lexicos.append(token)
        if token.type == TokenType.END_OF_FILE:
            break

    # Constrói tabela LL(1) (com actions incluídas)
    construir_tabela()

    # print("--- Tokens ---")
    # for t in tokens_lexicos:
    #     print(t)
    # print("--------------\n")

    print("--- Análise Sintática, Semântica e Geração de Código (integrada) ---")
    resultado = analisar(tokens_lexicos)
    if resultado:
        print("\n✔ Análise e geração concluídas com sucesso!")
    else:
        print("\n✖ Análise ou geração falhou.")
