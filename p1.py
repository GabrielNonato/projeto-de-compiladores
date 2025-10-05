import string
from typing import List, Dict, Tuple
from collections import deque

# -----------------------------
# Definições de Tipos de Token
# -----------------------------
from enum import Enum, auto

class TokenType(Enum):
    # Palavras-chave
    KEYWORD_PUBLIC = auto()     #public
    KEYWORD_CLASS = auto()      #class
    KEYWORD_ID = auto()         #id
    KEYWORD_LBRACE = auto()     # {
    KEYWORD_RBRACE = auto()     # }
    KEYWORD_STATIC = auto()     #static
    KEYWORD_VOID = auto()       #void
    KEYWORD_MAIN = auto()       #main
    KEYWORD_LPAR = auto()       # (
    KEYWORD_RPAR = auto()       # )
    KEYWORD_STRING = auto()     #string
    KEYWORD_LCOL = auto()       # [
    KEYWORD_RCOL = auto()       # ]
    KEYWORD_COMMA = auto()      # ,
    KEYWORD_TDOUBLE = auto()    # double
    KEYWORD_SEMICOLON = auto()  # ;
    KEYWORD_IF = auto()         # if
    KEYWORD_WHILE = auto()      # while
    KEYWORD_PRINT = auto()      # System.out.println
    KEYWORD_ELSE = auto()       # else
    KEYWORD_ATBR = auto()       # =
    KEYWORD_READ = auto()       # lerDouble
    KEYWORD_EQUAL = auto()      # ==
    KEYWORD_DIF = auto()        # !=
    KEYWORD_GE = auto()         # >=
    KEYWORD_LE = auto()         # <=
    KEYWORD_G = auto()          # >
    KEYWORD_L = auto()          # <
    KEYWORD_SUB = auto()        # -
    KEYWORD_NUMBER = auto()     # numero_real
    KEYWORD_PLUS = auto()       # +
    KEYWORD_MULT = auto()       # *
    KEYWORD_DIV = auto()        # /

    # Fim de arquivo e Desconhecido
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
    

# -----------------------------
# Estados do AFD
# -----------------------------
class LexerState(Enum):
    START = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    ASSIGN_OR_EQUAL = auto()
    RELATIONAL_OP = auto()
    ERROR = auto()

# -----------------------------
# Classe Lexer
# -----------------------------
class Lexer:
    def __init__(self, source):
        self.source = source
        self.index = 0
        self.line = 1

        # Mapeamento de palavras-chave
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
    # -----------------------------
    # Método auxiliar para ler "System.out.println"
    # -----------------------------
    def _try_read_print(self):
        pos_backup = self.index
        lexeme = ""

        expected = ".out.println"
        for ch in expected:
            if self.is_at_end() or self.peek() != ch:
                self.index = pos_backup  # desfaz leitura parcial
                return ""
            lexeme += self.advance()

        return lexeme

    # Funções auxiliares
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

    # -----------------------------
    # Função Principal de Leitura
    # -----------------------------
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
                # Verifica se é System.out.println
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

            # Estado inicial
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
                        ';': Token(TokenType.KEYWORD_SEMICOLON, ';', token_start_line),
                        '-': Token(TokenType.KEYWORD_SUB, '-', token_start_line),
                        '*': Token(TokenType.KEYWORD_MULT, '*', token_start_line),
                    }.get(c, Token(TokenType.UNKNOWN, c, token_start_line))

            elif state == LexerState.IDENTIFIER:
                if c.isalnum() or c == '_':
                    lexeme += self.advance()
                elif lexeme == "System" and c == '.':
                    # tenta ler "System.out.println"
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
                elif c == '.' and '.' not in lexeme:  # allow only one dot
                    lexeme += self.advance()
                else:
                    return Token(TokenType.KEYWORD_NUMBER, lexeme, token_start_line)

            elif state == LexerState.ASSIGN_OR_EQUAL:
                if c == '=':
                    lexeme += self.advance()
                    return Token(TokenType.KEYWORD_EQUAL, lexeme, token_start_line)
                return Token(TokenType.KEYWORD_ATBR, lexeme, token_start_line)
            
# ANALISADOR SINTATICO

tabela: Dict[Tuple[str, str], List[str]] = {}
            
def construir_tabela():
    """
    Constrói a tabela LL(1) com base nas produções da gramática.
    Exemplo inicial (gramática simples, substitua pelos tokens KEYWORD_ conforme seu lexer)
    """

    # PROG          -> public class id {  public static void main ( String [ ] id ) {  <CMDS> } } 
    tabela[("PROG", "KEYWORD_PUBLIC")] = [
        "KEYWORD_PUBLIC",
        "KEYWORD_CLASS",
        "KEYWORD_ID",
        "KEYWORD_LBRACE",
        "KEYWORD_PUBLIC",
        "KEYWORD_STATIC",
        "KEYWORD_VOID",
        "KEYWORD_MAIN",
        "KEYWORD_LPAR",
        "KEYWORD_STRING",
        "KEYWORD_LCOL",
        "KEYWORD_RCOL",
        "KEYWORD_ID",
        "KEYWORD_RPAR",
        "KEYWORD_LBRACE",
        "CMDS",   # ← este é um NÃO-TERMINAL, mantido assim
        "KEYWORD_RBRACE",
        "KEYWORD_RBRACE"
    ]

    # DC            -> <VAR> <MAIS_CMDS>
    tabela[("DC", "KEYWORD_TDOUBLE")] = ["VAR", "MAIS_CMDS"]

    #VAR           -> <TIPO> <VARS>
    tabela[("VAR", "KEYWORD_TDOUBLE")] = ["TIPO", "VARS"]

    #VARS          -> id<MAIS_VAR>
    tabela[("VARS", "KEYWORD_ID")] = ["KEYWORD_ID", "MAIS_VAR"]

    #MAIS_VAR      -> ,<VARS> | λ
    tabela[("MAIS_VAR", "KEYWORD_COMMA")] = ["KEYWORD_COMMA", "VARS"]

    tabela[("MAIS_VAR", "KEYWORD_SEMICOLON")] = []  # FOLLOW(MAIS_VAR)

    #TIPO          -> double
    tabela[("TIPO", "KEYWORD_TDOUBLE")] = ["KEYWORD_TDOUBLE"]

    #CMDS          -> <CMD><MAIS_CMDS> | <CMD_COND><CMDS> | <DC> | λ
    tabela[("CMDS", "KEYWORD_PRINT")] = ["CMD","MAIS_CMDS"]
    tabela[("CMDS", "KEYWORD_ID")] = ["CMD","MAIS_CMDS"]
    tabela[("CMDS", "KEYWORD_IF")] = ["CMD_COND","CMDS"]
    tabela[("CMDS", "KEYWORD_WHILE")] = ["CMD_COND","CMDS"]
    tabela[("CMDS", "KEYWORD_TDOUBLE")] = ["DC"]

    tabela[("CMDS", "KEYWORD_RBRACE")] = [] # FOLLOW(CMDS)

    #MAIS_CMDS     -> ;<CMDS>
    tabela[("MAIS_CMDS", "KEYWORD_SEMICOLON")] = ["KEYWORD_SEMICOLON","CMDS"]

    #CMD_COND      -> if (  <CONDICAO> )  {<CMDS>} <PFALSA> | while (  <CONDICAO> )  {<CMDS>}
    tabela[("CMD_COND", "KEYWORD_IF")] = ["KEYWORD_IF","KEYWORD_LPAR","CONDICAO","KEYWORD_RPAR","KEYWORD_LBRACE","CMDS","KEYWORD_RBRACE","PFALSA"]
    tabela[("CMD_COND", "KEYWORD_WHILE")] = ["KEYWORD_WHILE","KEYWORD_LPAR","CONDICAO","KEYWORD_RPAR","KEYWORD_LBRACE","CMDS","KEYWORD_RBRACE"]

    #CMD           -> System.out.println (<EXPRESSAO>) | id <RESTO_IDENT>
    tabela[("CMD", "KEYWORD_PRINT")] = ["KEYWORD_PRINT","KEYWORD_LPAR","EXPRESSAO","KEYWORD_RPAR"]
    tabela[("CMD", "KEYWORD_ID")] = ["KEYWORD_ID","RESTO_IDENT"]

    #PFALSA        -> else { <CMDS> } | λ
    tabela[("PFALSA", "KEYWORD_ELSE")] = ["KEYWORD_ELSE","KEYWORD_LBRACE","CMDS","KEYWORD_RBRACE"]
    tabela[("PFALSA", "KEYWORD_PRINT")] = [] # FOLLOW(PFALSA)
    tabela[("PFALSA", "KEYWORD_ID")] = [] # FOLLOW(PFALSA)
    tabela[("PFALSA", "KEYWORD_IF")] = [] # FOLLOW(PFALSA)
    tabela[("PFALSA", "KEYWORD_WHILE")] = [] # FOLLOW(PFALSA)
    tabela[("PFALSA", "KEYWORD_TDOUBLE")] = [] # FOLLOW(PFALSA)
    tabela[("PFALSA", "KEYWORD_RBRACE")] = [] # FOLLOW(PFALSA)

    #RESTO_IDENT   -> = <EXP_IDENT>
    tabela[("RESTO_IDENT", "KEYWORD_ATBR")] = ["KEYWORD_ATBR","EXP_IDENT"]

    #EXP_IDENT     -> <EXPRESSAO> | lerDouble()
    tabela[("EXP_IDENT", "KEYWORD_READ")] = ["KEYWORD_READ","KEYWORD_LPAR","KEYWORD_RPAR"]
    tabela[("EXP_IDENT", "KEYWORD_SUB")] = ["EXPRESSAO"]
    tabela[("EXP_IDENT", "KEYWORD_ID")] = ["EXPRESSAO"]
    tabela[("EXP_IDENT", "KEYWORD_NUMBER")] = ["EXPRESSAO"]

    #CONDICAO      -> <EXPRESSAO> <RELACAO> <EXPRESSAO>
    tabela[("CONDICAO", "KEYWORD_SUB")] = ["EXPRESSAO","RELACAO","EXPRESSAO"]
    tabela[("CONDICAO", "KEYWORD_ID")] = ["EXPRESSAO","RELACAO","EXPRESSAO"]
    tabela[("CONDICAO", "KEYWORD_NUMBER")] = ["EXPRESSAO","RELACAO","EXPRESSAO"]
    tabela[("CONDICAO", "KEYWORD_LPAR")] = ["EXPRESSAO","RELACAO","EXPRESSAO"]

    #RELACAO       -> == | != | >= | <= | > | <
    tabela[("RELACAO", "KEYWORD_EQUAL")] = ["KEYWORD_EQUAL"]
    tabela[("RELACAO", "KEYWORD_DIF")] = ["KEYWORD_DIF"]
    tabela[("RELACAO", "KEYWORD_GE")] = ["KEYWORD_GE"]
    tabela[("RELACAO", "KEYWORD_LE")] = ["KEYWORD_LE"]
    tabela[("RELACAO", "KEYWORD_G")] = ["KEYWORD_G"]
    tabela[("RELACAO", "KEYWORD_L")] = ["KEYWORD_L"]

    #EXPRESSAO     -> <TERMO> <OUTROS_TERMOS>
    tabela[("EXPRESSAO", "KEYWORD_SUB")] = ["TERMO","OUTROS_TERMOS"]
    tabela[("EXPRESSAO", "KEYWORD_ID")] = ["TERMO","OUTROS_TERMOS"]
    tabela[("EXPRESSAO", "KEYWORD_NUMBER")] = ["TERMO","OUTROS_TERMOS"]
    tabela[("EXPRESSAO", "KEYWORD_LPAR")] = ["TERMO","OUTROS_TERMOS"]

    #TERMO         -> <OP_UN> <FATOR> <MAIS_FATORES>
    tabela[("TERMO", "KEYWORD_SUB")] = ["OP_UN","FATOR","MAIS_FATORES"]
    tabela[("TERMO", "KEYWORD_ID")] = ["OP_UN","FATOR","MAIS_FATORES"]
    tabela[("TERMO", "KEYWORD_NUMBER")] = ["OP_UN","FATOR","MAIS_FATORES"]
    tabela[("TERMO", "KEYWORD_LPAR")] = ["OP_UN","FATOR","MAIS_FATORES"]

    #OP_UN         -> - | λ
    tabela[("OP_UN", "KEYWORD_SUB")] = ["KEYWORD_SUB"]
    tabela[("OP_UN", "KEYWORD_ID")] = [] # FOLLOW(OP_UN)
    tabela[("OP_UN", "KEYWORD_NUMBER")] = [] # FOLLOW(OP_UN)
    tabela[("OP_UN", "KEYWORD_LPAR")] = [] # FOLLOW(OP_UN)
  

    #FATOR         -> id | numero_real | (<EXPRESSAO>)
    tabela[("FATOR", "KEYWORD_ID")] = ["KEYWORD_ID"]
    tabela[("FATOR", "KEYWORD_NUMBER")] = ["KEYWORD_NUMBER"]
    tabela[("FATOR", "KEYWORD_LPAR")] = ["KEYWORD_LPAR","EXPRESSAO","KEYWORD_RPAR"]

    #OUTROS_TERMOS -> <OP_AD> <TERMO> <OUTROS_TERMOS> | λ
    tabela[("OUTROS_TERMOS", "KEYWORD_SUB")] = ["OP_AD","TERMO","OUTROS_TERMOS"]
    tabela[("OUTROS_TERMOS", "KEYWORD_PLUS")] = ["OP_AD","TERMO","OUTROS_TERMOS"]
    tabela[("OUTROS_TERMOS", "KEYWORD_EQUAL")] = [] # FOLLOW(OUTROS_TERMOS)
    tabela[("OUTROS_TERMOS", "KEYWORD_DIF")] = [] # FOLLOW(OUTROS_TERMOS)
    tabela[("OUTROS_TERMOS", "KEYWORD_GE")] = [] # FOLLOW(OUTROS_TERMOS)
    tabela[("OUTROS_TERMOS", "KEYWORD_LE")] = [] # FOLLOW(OUTROS_TERMOS)
    tabela[("OUTROS_TERMOS", "KEYWORD_G")] = [] # FOLLOW(OUTROS_TERMOS)
    tabela[("OUTROS_TERMOS", "KEYWORD_L")] = [] # FOLLOW(OUTROS_TERMOS)
    tabela[("OUTROS_TERMOS", "KEYWORD_RPAR")] = [] # FOLLOW(OUTROS_TERMOS)
    tabela[("OUTROS_TERMOS", "KEYWORD_SEMICOLON")] = [] # FOLLOW(OUTROS_TERMOS)

    #OP_AD         -> + | -
    tabela[("OP_AD", "KEYWORD_SUB")] = ["KEYWORD_SUB"]
    tabela[("OP_AD", "KEYWORD_PLUS")] = ["KEYWORD_PLUS"]

    #MAIS_FATORES  -> <OP_MUL> <FATOR> <MAIS_FATORES> | λ
    tabela[("MAIS_FATORES", "KEYWORD_MULT")] = ["OP_MUL","FATOR","MAIS_FATORES"]
    tabela[("MAIS_FATORES", "KEYWORD_DIV")] = ["OP_MUL","FATOR","MAIS_FATORES"]
    tabela[("MAIS_FATORES", "KEYWORD_SUB")] = [] # FOLLOW(MAIS_FATORES)
    tabela[("MAIS_FATORES", "KEYWORD_PLUS")] = [] # FOLLOW(MAIS_FATORES)
    tabela[("MAIS_FATORES", "KEYWORD_EQUAL")] = [] # FOLLOW(MAIS_FATORES)
    tabela[("MAIS_FATORES", "KEYWORD_DIF")] = [] # FOLLOW(MAIS_FATORES)
    tabela[("MAIS_FATORES", "KEYWORD_GE")] = [] # FOLLOW(MAIS_FATORES)
    tabela[("MAIS_FATORES", "KEYWORD_LE")] = [] # FOLLOW(MAIS_FATORES)
    tabela[("MAIS_FATORES", "KEYWORD_G")] = [] # FOLLOW(MAIS_FATORES)
    tabela[("MAIS_FATORES", "KEYWORD_L")] = [] # FOLLOW(MAIS_FATORES)
    tabela[("MAIS_FATORES", "KEYWORD_RPAR")] = [] # FOLLOW(MAIS_FATORES)
    tabela[("MAIS_FATORES", "KEYWORD_SEMICOLON")] = [] # FOLLOW(MAIS_FATORES)


    #OP_MUL         -> + | -
    tabela[("OP_MUL", "KEYWORD_MULT")] = ["KEYWORD_MULT"]
    tabela[("OP_MUL", "KEYWORD_DIV")] = ["KEYWORD_DIV"]

# -----------------------------
# Função principal de análise
# -----------------------------
def analisar(tokens: List[str]) -> bool:
    """
    Realiza a análise sintática LL(1) sobre a lista de tokens fornecida.
    Retorna True se a sequência for aceita pela gramática.
    """

    tokens = deque(tokens)  # lista de tokens
    tokens.append("END_OF_FILE")  # marcador de fim da entrada como string

    pilha = deque()
    pilha.append("$")  # símbolo de fim
    pilha.append("PROG")  # símbolo inicial

    i = 0

    while pilha:
        i+=1
        topo = pilha[-1]   # topo da pilha
        atual = tokens[0]  # próximo token da entrada (string)


        # Caso de aceitação
        if topo == "$" and atual == "END_OF_FILE":
            print("✔ Análise sintática concluída com sucesso!")
            return True

        # Se topo for terminal (começa com "KEYWORD_" ou "END_OF_FILE")
        elif topo.startswith("KEYWORD_") or topo == "END_OF_FILE":
            if topo == atual:
                pilha.pop()
                tokens.popleft()
            else:
                print(f"Erro de sintaxe: token inesperado '{atual}', esperado '{topo}'")
                return False

        # Se topo for um não-terminal (string)
        elif isinstance(topo, str):
            chave = (topo, atual)
            if chave in tabela:
                pilha.pop()
                producao = tabela[chave]
                for simbolo in reversed(producao):
                    if simbolo != "":  # ignora ε
                        pilha.append(simbolo)
            else:
                print(f"Erro de sintaxe: nenhuma regra para topo '{topo}' com token '{atual}'")
                return False
        else:
            print(f"Erro interno: tipo desconhecido no topo da pilha '{topo}'")
            return False

    return False


# -----------------------------
# Execução Principal
# -----------------------------
def token_type_to_string(ttype):
    return ttype.name

if __name__ == "__main__":
    try:
        with open("codigoTestarp1.txt", "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print("Erro ao abrir o arquivo codigoTestar.txt")
        exit(1)

    lexer = Lexer(code)
    tokens_lexicos = []  # Armazena todos os tokens

    # print("--- Análise Léxica Simplificada com Parênteses ---")
    while True:
        token = lexer.get_next_token()
        tokens_lexicos.append(token_type_to_string(token.type))  # Armazena token
        # print(f"Linha {token.line}: {token_type_to_string(token.type)} -> '{token.lexeme}'")
        if token.type == TokenType.END_OF_FILE:
            break
    # print("--- Fim da Análise ---")
    construir_tabela()
    print("--- Análise Sintática ---")
    analisar(tokens_lexicos)
    # print(tokens_lexicos)

