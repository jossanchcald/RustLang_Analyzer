import ply.lex as lex
from ply.lex import TOKEN # Para creacion de regEx con variables
import re

# Lista global para almacenar los errores y posteriormente enviarlos al log
lexicalErrors = []

 # Diccionario de palabras reservadas
reserved_words = { 
    'if' : 'IF',
    'else' : 'ELSE',
    'fn' : 'FUNCTION',
    'let' : 'DECLARATION',
    'const' : 'CONSTANT',
    'static' : 'STATIC',
    'match' : 'MATCH',
    'for' : 'FOR',
    'while' : 'WHILE',
    'break' : 'BREAK',
    'continue' : 'CONTINUE',
    'loop' : 'LOOP',
    'return' : "RETURN",
    'mut' : 'MUT',
    'struct' : 'STRUCT',
    'self' : 'SELF'

}

tokens = [
    'INTEGER',
    #'FLOAT',
    #'ANYID_START'
    
    # Operadores
    'PLUS',
    'MINUS',
    'MULT',
    'DIV',
    'MOD',

    # Delimitadores
    'PARENR',
    'PARENL',
    'BRACER',
    'BRACEL',
    'BRACKR',
    'BRACKL',

    'IDENTIFIER'
] + list(reserved_words.values())

# Reglas de expresiones regulares para tokens simples
# Operadores 
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_MOD = r'%'

# Delimitadores
t_PARENL = r'\('
t_PARENR = r'\)'
t_BRACEL = r'\{'
t_BRACER = r'\}'
t_BRACKL = r'\['
t_BRACKR = r'\]'


# Caracteres ignorados (espacios y tabulaciones)
t_ignore = ' \t'

# Inicio Parte de Josue Sanchez Calderon
intSufix = r'(u8|u16|u32|u64|u128|usize|i8|i16|i32|i64|i128|isize)'
compiledIntSufix = re.compile(intSufix)

def removeSufix(text, sufix_re):
    return sufix_re.sub('', text)

hexDigit = r'[0-9a-fA-F]'
regexHex = fr'0x{hexDigit}({hexDigit}|_)*{intSufix}?'
@TOKEN(regexHex)
def t_INT_HEX(t):
    t.type = 'INTEGER'

    rawText = t.value
    rawTextNo_ = rawText.replace('_', '')
    cleanText = removeSufix(rawTextNo_, compiledIntSufix)
    
    t.value = int(cleanText, base=16)
    return t

binDigit = r'[01]'
regexBin = fr'0b{binDigit}({binDigit}|_)*{intSufix}?'
@TOKEN(regexBin)
def t_INT_BIN(t):
    t.type = 'INTEGER'

    rawText = t.value
    rawTextNo_ = rawText.replace('_', '')
    cleanText = removeSufix(rawTextNo_, compiledIntSufix)
    
    t.value = int(cleanText, base=2)
    return t

octDigit = r'[0-7]'
regexOct = fr'0o{octDigit}({octDigit}|_)*{intSufix}?'
@TOKEN(regexOct)
def t_INT_OCT(t):
    t.type = 'INTEGER'

    rawText = t.value
    rawTextNo_ = rawText.replace('_', '')
    cleanText = removeSufix(rawTextNo_, compiledIntSufix)
    
    t.value = int(cleanText, base=8)
    return t

decDigit = r'[0-9]'
regexDec = fr'{decDigit}({decDigit}|_)*{intSufix}?'
@TOKEN(regexDec)
def t_INT_DEC(t):
    t.type = 'INTEGER'

    rawText = t.value
    rawTextNo_ = rawText.replace('_', '')
    cleanText = removeSufix(rawTextNo_, compiledIntSufix)
    
    t.value = int(cleanText, base=10)
    return t

# Fin Parte de Josue Sanchez Calderon

# Inicio Parte de Leiner David Saltos Penafiel

regexID = r'[a-zA-Z_][a-zA-Z0-9_]*'
@TOKEN(regexID)
def t_IDENTIFIER(t):
    t.type = reserved_words.get(t.value, 'IDENTIFIER')
    return t



# regla para contar lineas para los mensajes de error
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    # Formato del error
    error_info = {
        "caracter": t.value[0],
        "linea": t.lexer.lineno,
        "posicion": t.lexpos
    }
    
    lexicalErrors.append(error_info)
    t.lexer.skip(1)


# Construccion del lexer
lexer = lex.lex()