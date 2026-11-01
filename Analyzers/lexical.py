import ply.lex as lex
from ply.lex import TOKEN # Para creacion de regEx con variables
import regex as re

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
    'self' : 'SELF',

    'true': 'BOOLEAN_T',
    'false' : 'BOOLEAN_F'

}

tokens = [
    'INTEGER',
    'FLOAT',
    'CHAR',
    #'STRING',
    'BOOLEAN',
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

# Inicio parte de Josue Sanchez Calderon

def removeSufix(text, sufix_re):
    return sufix_re.sub('', text)


# Characters
regexSingleCharUnicodeStandard = r'[\U00000000-\U0000D7FF\U0000E000-\U0010FFFF]'
regexChar = fr'\'{regexSingleCharUnicodeStandard}\''

@TOKEN(regexChar)
def t_CHAR(t):
    t.value = str(t.value)

    return t


# Integers
intSufix = r'(u8|u16|u32|u64|u128|usize|i8|i16|i32|i64|i128|isize)'
compiledIntSufix = re.compile(intSufix)

hexDigit = r'[0-9a-fA-F]'
regexHex = fr'0x{hexDigit}({hexDigit}|_)*{intSufix}?'
binDigit = r'[01]'
regexBin = fr'0b{binDigit}({binDigit}|_)*{intSufix}?'
octDigit = r'[0-7]'
regexOct = fr'0o{octDigit}({octDigit}|_)*{intSufix}?'
decDigit = r'[0-9]'
regexDec = fr'{decDigit}({decDigit}|_)*{intSufix}?'

# Floating point
floatSufix = r'(f32|f64)'
compiledFloatSufix = re.compile(floatSufix)

floatExp = fr'[eE][+\-]?[_]*{regexDec}({regexDec}|_)*'
floatBranch1 = fr'({regexDec}+(\.{regexDec}+)?{floatExp}){floatSufix}?'
floatBranch2 = fr'({regexDec}+(\.{regexDec}+)){floatSufix}?'
floatBranch3 = fr'{regexDec}+\.(?![\._a-zA-Z])'
floatBranch4 = fr'{regexDec}+{floatSufix}'
regexFloat = fr'({floatBranch1})|({floatBranch2})|({floatBranch3})|({floatBranch4})'


@TOKEN(regexFloat)
def t_FLOAT(t):

    rawText = t.value
    rawTextNo_ = rawText.replace('_', '')
    cleanText = removeSufix(rawTextNo_, compiledFloatSufix)
    
    t.value = float(cleanText)
    return t


@TOKEN(regexHex)
def t_INT_HEX(t):
    t.type = 'INTEGER'

    rawText = t.value
    rawTextNo_ = rawText.replace('_', '')
    cleanText = removeSufix(rawTextNo_, compiledIntSufix)
    
    t.value = int(cleanText, base=16)
    return t


@TOKEN(regexBin)
def t_INT_BIN(t):
    t.type = 'INTEGER'

    rawText = t.value
    rawTextNo_ = rawText.replace('_', '')
    cleanText = removeSufix(rawTextNo_, compiledIntSufix)
    
    t.value = int(cleanText, base=2)
    return t


@TOKEN(regexOct)
def t_INT_OCT(t):
    t.type = 'INTEGER'

    rawText = t.value
    rawTextNo_ = rawText.replace('_', '')
    cleanText = removeSufix(rawTextNo_, compiledIntSufix)
    
    t.value = int(cleanText, base=8)
    return t


@TOKEN(regexDec)
def t_INT_DEC(t):
    t.type = 'INTEGER'

    rawText = t.value
    rawTextNo_ = rawText.replace('_', '')
    cleanText = removeSufix(rawTextNo_, compiledIntSufix)
    
    t.value = int(cleanText, base=10)
    return t



# # Strings TODO sin terminar
# regexString = fr'(\"){regexSingleCharUnicodeStandard}{regexSingleCharUnicodeStandard}+(\")'

# @TOKEN(regexString)
# def t_STRING(t):
#     t.value = str(t.value)

#     return t


# Fin parte de Josue Sanchez Calderon

# Inicio Parte de Leiner David Saltos Penafiel

regexID = r'[a-zA-Z_][a-zA-Z0-9_]*'
@TOKEN(regexID)
def t_IDENTIFIER(t):
    t.type = reserved_words.get(t.value, 'IDENTIFIER')

    if ((t.type == 'BOOLEAN_T') | (t.type == 'BOOLEAN_F')): # Booleans (Josue)
        t.type = "BOOLEAN"

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