import ply.lex as lex
from ply.lex import TOKEN 
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
    'STRING',
    'BOOLEAN',
    'BYTE_LITERAL',
    
    # Operadores
    'PLUS',
    'MINUS',
    'MULT',
    'DIV',
    'MOD',

    # Comparadores
    'EQUAL_TO',
    'NOT_EQUAL_TO',
    'GREATER_THAN',
    'LESS_THAN',
    'GREATER_EQUAL_THAN',
    'LESS_EQUAL_THAN',

    # Delimitadores
    'PARENR',
    'PARENL',
    'BRACER',
    'BRACEL',
    'BRACKR',
    'BRACKL',

    # Asignacion
    'EQUAL',
    'PLUS_EQUAL',
    'MINUS_EQUAL',
    'TIMES_EQUAL',
    'DIV_EQUAL',
    'MOD_EQUAL',

    # Operadores logicos
    'AND',
    'OR',
    'NOT',

    'ARROW',
    'COLON',
    'SEMICOLON',
    'COMMA',
    'IDENTIFIER',
    'RAW_IDENTIFIER',
    'UNDERSCORE'
] + list(reserved_words.values())

# Reglas de expresiones regulares para tokens simples
# Operadores 
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_MOD = r'%'

#Comparadores
t_EQUAL_TO = r'='
t_NOT_EQUAL_TO = r'!='
t_GREATER_THAN = r'>'
t_LESS_THAN = r'<'
t_GREATER_EQUAL_THAN = r'>='
t_LESS_EQUAL_THAN = r'<='

# Delimitadores
t_PARENL = r'\('
t_PARENR = r'\)'
t_BRACEL = r'\{'
t_BRACER = r'\}'
t_BRACKL = r'\['
t_BRACKR = r'\]'

# Asignacion
t_EQUAL = r'='
t_PLUS_EQUAL = r'\+='
t_MINUS_EQUAL = r'-='
t_TIMES_EQUAL = r'\*='
t_DIV_EQUAL = r'/='
t_MOD_EQUAL = r'%='


# Operadores logicos 
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'

t_ARROW = r'\->'
t_COLON = r':'
t_SEMICOLON = r';'
t_COMMA = r','

# Caracteres ignorados (espacios y tabulaciones)
t_ignore = ' \t'





# Inicio parte de Josue Sanchez Calderon

def removeSufix(text, sufix_re):
    return sufix_re.sub('', text)

# Regex of Integers
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

# Regex of Floating point
floatSufix = r'(f32|f64)'
compiledFloatSufix = re.compile(floatSufix)

floatExp = fr'([eE][+\-]?[_]*{regexDec}({regexDec}|_)*)'
floatBranch1 = fr'({regexDec}+(\.{regexDec}+)?{floatExp}){floatSufix}?'
floatBranch2 = fr'({regexDec}+(\.{regexDec}+)){floatSufix}?'
floatBranch3 = fr'{regexDec}+\.(?![\._a-zA-Z])'
floatBranch4 = fr'{regexDec}+{floatSufix}'
regexFloat = fr'({floatBranch1})|({floatBranch2})|({floatBranch3})|({floatBranch4})'

# Regex of Escapes
regexSimpleEscape = r'\\(0|t|n|r|\"|\'|\\)'
regex8bitEscape = fr'\\(x{hexDigit}{{2}})'
regex7bitEscape = fr'\\(x{octDigit}{hexDigit})'
regexUnicodeEscape = fr'\\(u\{{({hexDigit}(_)*){{1,6}}\}})'
regexStrContEscape = r'\\(\U0000000A)\s*'

regexCharEscape = fr'{regexSimpleEscape}|{regex7bitEscape}|{regexUnicodeEscape}'
regexByteEscape = fr'({regex8bitEscape}|{regexSimpleEscape})'

# Regex of Characters
regexSingleCharUnicodeStandard = r'[\U00000000-\U0000D7FF\U0000E000-\U0010FFFF]'
regexSCUSCharAccepted = r'[\U00000000-\U00000008\U0000000B\U0000000C\U0000000E-\U00000026\U00000028-\U0000005B\U0000005D-\U0000D7FF\U0000E000-\U0010FFFF]'
regexChar = fr'\'({regexSCUSCharAccepted}|{regexCharEscape})\''

# Regex of Byte Literals
regexASCIICharAccepted = r'[\x00-\x08\x0B-\x0C\x0E-\x26\x28-\x5B\x5D-\x7F]'
regexByteLiteral = fr'b\'({regexASCIICharAccepted}|{regexByteEscape})\''

# Regex of Strings
regexSCUSStringAccepted = r'[\U00000000-\U0000000C\U0000000E-\U00000021\U00000023-\U0000005B\U0000005D-\U0000D7FF\U0000E000-\U0010FFFF]'
regexString = fr'\"({regexSCUSStringAccepted}|{regexCharEscape}|{regexStrContEscape})*\"'

regexRawString = fr''


# Char
@TOKEN(regexChar)
def t_CHAR(t):

    cleanText = t.value + ""
    if (t.value != "\'_\'"):
        rawText = t.value
        cleanText = rawText.replace('_', '')

    t.value = str(cleanText)
    return t


# Strings
@TOKEN(regexString)
def t_STRING(t):

    cleanText = t.value + ""
    if (str.find(t.value, "\\\U0000000A")):
        rawText = cleanText.replace("\\\U0000000A", "")
        cleanText = rawText

    t.value = str(cleanText)
    return t


# Byte literal
@TOKEN(regexByteLiteral)
def t_BYTE_LITERAL(t):

    t.value = str(t.value)
    return t


# Float
@TOKEN(regexFloat)
def t_FLOAT(t):

    rawText = t.value
    rawTextNo_ = rawText.replace('_', '')
    cleanText = removeSufix(rawTextNo_, compiledFloatSufix)
    
    t.value = float(cleanText)
    return t


#Integers
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

# Fin parte de Josue Sanchez Calderon





# Inicio parte de Jared Beltran

# Columna de una posicion dentro del texto que se analiza
def findColumn(lexdata, lexpos):
    lineStart = lexdata.rfind('\n', 0, lexpos) + 1
    return lexpos - lineStart + 1


def addLexicalError(lexdata, lineno, lexpos, lexeme, message):
    lexicalErrors.append({
        "caracter": lexeme,
        "linea": lineno,
        "columna": findColumn(lexdata, lexpos),
        "posicion": lexpos,
        "mensaje": f"Error léxico (línea {lineno}, columna {findColumn(lexdata, lexpos)}): {message}"
    })

# Guion bajo solo no es un identificador valido en Rust
@TOKEN(r'_(?![a-zA-Z0-9_])')
def t_UNDERSCORE(t):
    return t

# Raw identifier
# Antes de t_IDENTIFIER: si no, el lexer toma la 'r' como un identificador
regexRawID = r'r\#[a-zA-Z_][a-zA-Z0-9_]*'
rawIDReserved = ('crate', 'self', 'super', 'Self', '_')

@TOKEN(regexRawID)
def t_RAW_IDENTIFIER(t):
    name = t.value[2:]
    if name in rawIDReserved:
        addLexicalError(t.lexer.lexdata, t.lexer.lineno, t.lexpos, t.value,
                        f"'{t.value}' no es un raw identifier válido ('{name}' no puede usarse con r#)")
        return None
    return t

# Fin parte de Jared Beltran

# Inicio Parte de Leiner David Saltos Penafiel

regexID = r'[a-zA-Z_][a-zA-Z0-9_]*'
@TOKEN(regexID)
def t_IDENTIFIER(t):
    t.type = reserved_words.get(t.value, 'IDENTIFIER')

    if ((t.type == 'BOOLEAN_T') | (t.type == 'BOOLEAN_F')):
        t.type = "BOOLEAN"

    return t



# Regla para contar lineas para los mensajes de error
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


# Errores
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