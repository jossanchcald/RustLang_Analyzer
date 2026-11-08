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
    'enum' : 'ENUM',
    'in' : 'IN',
    'as' : 'AS',

    'true': 'BOOLEAN_T',
    'false' : 'BOOLEAN_F'
}

# Nombres de los tipos de datos
typesNames = {
    'i8', 'i16', 'i32', 'i64', 'i128', 'isize',
    'u8', 'u16', 'u32', 'u64', 'u128', 'usize',
    'f32', 'f64',
    'bool', 'char', 'str',
    'String', 'Vec', 'HashMap', 'Option', 'Result'
}

tokens = [
    'INTEGER',
    'FLOAT',
    'CHAR',
    'STRING',
    'RAW_STRING',
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
    'DOUBLE_COLON',
    'RANGE',
    'PERIOD',
    'AMPERSAND',
    'PIPE',
    'TYPE',
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
t_EQUAL_TO = r'(==)'
t_NOT_EQUAL_TO = r'!='
t_GREATER_THAN = r'>'
t_LESS_THAN = r'<'
t_GREATER_EQUAL_THAN = r'>='
t_LESS_EQUAL_THAN = r'<='

# Delimitadores
t_PARENL = r'\('
t_PARENR = r'\)'
t_BRACEL = r'{'
t_BRACER = r'}'
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
t_AND = r'(&&)'
t_OR = r'(\|\|)'
t_NOT = r'!'

t_ARROW = r'(\->)'
t_COLON = r':'
t_SEMICOLON = r';'
t_COMMA = r','
t_DOUBLE_COLON = r'(::)'
t_PERIOD = r'(\.)'
t_AMPERSAND = r'&'
t_PIPE = r'\|'
t_RANGE = r'(\.\.)'

# Caracteres ignorados (espacios y tabulaciones)
t_ignore = ' \t'





# Inicio parte de Josue Sanchez Calderon //////////////////////////////////////////////////////////////////////////////////////////////////

def removeSufix(text, sufix_re):
    return sufix_re.sub('', text)

regexIdChar = r'[a-zA-Z0-9_]'
numEnd = fr'(?!{regexIdChar})'

# Regex of Integers
intSufix = r'(?:u8|u16|u32|u64|u128|usize|i8|i16|i32|i64|i128|isize)'
compiledIntSufix = re.compile(intSufix + r'$')

hexDigit = r'[0-9a-fA-F]'
regexHex = fr'0x_*{hexDigit}({hexDigit}|_)*{intSufix}?{numEnd}'
binDigit = r'[01]'
regexBin = fr'0b_*{binDigit}({binDigit}|_)*{intSufix}?{numEnd}'
octDigit = r'[0-7]'
regexOct = fr'0o_*{octDigit}({octDigit}|_)*{intSufix}?{numEnd}'
decDigit = r'[0-9]'
decDigits = fr'{decDigit}({decDigit}|_)*'
regexDec = fr'{decDigits}{intSufix}?{numEnd}(?!\.{decDigit})'

compiledInvalidDecimal = re.compile(r'(?P<int>[0-9][0-9_]*)(?P<frac>\.[0-9][0-9_]*)?(?P<exp>[eE][+\-]?[0-9_]*)?(?P<rest>[0-9a-zA-Z_]*)')
compiledBaseDigits = {'x': re.compile(r'[0-9a-fA-F_]*'),
                      'b': re.compile(r'[01_]*'),
                      'o': re.compile(r'[0-7_]*')}

# Regex of Floating point
floatSufix = r'(?:f32|f64)'
compiledFloatSufix = re.compile(floatSufix + r'$')

floatExp = fr'[eE][+\-]?_*{decDigit}(?:{decDigit}|_)*'
floatBranch1 = fr'{decDigits}(?:\.{decDigits})?{floatExp}{floatSufix}?'
floatBranch2 = fr'{decDigits}\.{decDigits}{floatSufix}?'
floatBranch3 = fr'{decDigits}\.(?![\._a-zA-Z0-9])'
floatBranch4 = fr'{decDigits}{floatSufix}'
regexFloat = fr'(?:{floatBranch1}|{floatBranch2}|{floatBranch3}|{floatBranch4}){numEnd}'

# Regex of Escapes
regexSimpleEscape = r'\\(0|t|n|r|\"|\'|\\)'
regex8bitEscape = fr'\\x{hexDigit}{{2}}'
regex7bitEscape = fr'\\x{octDigit}{hexDigit}'
regexUnicodeEscape = fr'\\u{{({hexDigit}(_)*){{1,6}}}}'
regexStrContEscape = r'\\\n\s*(?!\s)'

regexCharEscape = fr'{regexSimpleEscape}|{regex7bitEscape}|{regexUnicodeEscape}'
regexByteEscape = fr'({regex8bitEscape}|{regexSimpleEscape})'

# Regex of Characters
def isCharUnicodeStandard(c):
    if c <= 0x10FFFF and not (0xD800 <= c <= 0xDFFF):
        return True
    return False

regexSCUSCharAccepted = r'[^\t\r\n\'\\\ud800-\udfff]'
regexChar = fr'\'({regexSCUSCharAccepted}|{regexCharEscape})\''

compiledClosedChar = re.compile(r"\'(?:\\.|[^\'\\\n])*\'")
compiledCharXEscape = re.compile(fr"\\x(?P<xEscapeContent>{hexDigit}{{2}})")
compiledCharUEscape = re.compile(r"\\u{(?P<unicodeContent>[^}]*)}")
compiledUnicodeDigits = re.compile(fr"(?:{hexDigit}_*){{1,6}}")

# Regex of Byte Literals
regexASCIICharAccepted = r'[\x00-\x08\x0B-\x0C\x0E-\x26\x28-\x5B\x5D-\x7F]'
regexByteLiteral = fr'b\'({regexASCIICharAccepted}|{regexByteEscape})\''

compiledClosedByteLit = re.compile(r"b\'(?:\\.|[^\'\\\n])*\'")
compiledByteLitXEscape = re.compile(fr"\\x(?P<xByteContent>{hexDigit}{{2}})")

# Regex of Strings
regexSCUSStringAccepted = r'[^\r"\\\ud800-\udfff]'
regexString = fr'\"({regexSCUSStringAccepted}|{regexCharEscape}|{regexStrContEscape})*\"'

compiledClosedString = re.compile(r'\"(?:\\[\s\S]|[^\"\\])*\"')
compiledStringEscape = re.compile(r'\\(?:(?P<cont>\n\s*)|u\{(?P<uContent>[^}]*)\}|[\s\S])')
compiledAnyStringEscape = re.compile(r'\\(?:x[0-9a-fA-F]{0,2}|u\{[^}\"]*\}|[\s\S])|\r')

def replaceStringEscape(m):
    if m.group('cont') is not None:
        return ''
    return m.group(0)

# Regex of Raw Strings
regexSCUSRawStringAccepted = r'[^\r"\ud800-\udfff]'
regexSCUSRawHashedAccepted = r'[^\r\ud800-\udfff]'

regexRSSimple = fr'r\"{regexSCUSRawStringAccepted}*\"'
regexRSHashed = fr'r(?P<hashes>\#+)\"(?:{regexSCUSRawHashedAccepted})*?\"(?P=hashes)'
regexRawString = fr'(?:{regexRSSimple})|(?:{regexRSHashed})'


# Byte literal
@TOKEN(regexByteLiteral)
def t_BYTE_LITERAL(t):
    return t

regexInvalidByteLiteral = r"b\'(?:\\.|[^\'\\\n])*\'?"
@TOKEN(regexInvalidByteLiteral)
def t_INVALID_BYTE_LITERAL(t):
    val = t.value
    content = val[2:-1]
    msg = "byte literal inválido"

    if not compiledClosedByteLit.fullmatch(val):
        msg = "byte literal sin cerrar (falta ' )"

    elif content == "":
        msg = "byte literal vacío"

    elif content[0] != "\\":
        if any(ord(c) > 127 for c in content):
            msg = "byte literal inválido (solo se permiten caracteres ASCII)"
        elif len(content) == 1:
            msg = "el \\t y el \\r deben escribirse como escapes"
        else:
            msg = "un byte literal solo puede contener un byte o codepoint"

    else:
        kind = content[1]
        end = None

        if kind == 'x':
            escapeCont = compiledByteLitXEscape.match(content)
            if not escapeCont:
                msg = "escape \\x inválido (requiere exactamente 2 dígitos hexadecimales)"
            else:
                end = escapeCont.end()

        elif kind == 'u':
            msg = "escape \\u no está permitido en byte literal"

        elif kind in "nrt\\0\'\"":
            end = 2

        else:
            msg = f"secuencia de escape desconocida '\\{kind}'"

        if end is not None and end != len(content):
            msg = "un byte literal solo puede contener un byte o codepoint"

    addLexicalError(t.lexer.lexdata, t.lexer.lineno, t.lexpos, val, msg)
    return None


# Raw string
@TOKEN(regexRawString)
def t_RAW_STRING(t):
    t.lexer.lineno += t.value.count('\n')
    return t

regexInvalidRawString = r'r\#*\"(?s:.*)'
@TOKEN(regexInvalidRawString)
def t_INVALID_RAW_STRING(t):
    val = t.value
    n = val.index('"') - 1 # Cantidad de # de apertura
    start = n + 2
    closing = '"' + '#' * n
    end = val.find(closing, start)

    if end == -1: # No cierra nunca
        consumed = val
        content = None
    else:
        consumed = val[:end + len(closing)]
        content = val[start:end]

    if n > 255:
        msg = "demasiados '#' en raw string (máximo 255)"
    elif content is None:
        msg = f"raw string sin cerrar (se esperaba '\"{'#' * n}')"
    elif re.search(r'\r(?!\n)', content):
        msg = "CR (\\r) suelto no permitido en raw string"
    else:
        msg = "raw string inválido"

    # Se devuelve al lexer lo que no pertenece
    t.lexer.lexpos = t.lexpos + len(consumed)

    addLexicalError(t.lexer.lexdata, t.lexer.lineno, t.lexpos,
                    consumed.split('\n', 1)[0], msg)
    t.lexer.lineno += consumed.count('\n')
    return None

regexInvalidRawDelimiter = r'r\#{2,}(?![\"\#])(?:[^\W\d]\w*)?'
@TOKEN(regexInvalidRawDelimiter)
def t_INVALID_RAW_DELIMITER(t):
    addLexicalError(t.lexer.lexdata, t.lexer.lineno, t.lexpos, t.value,
                    f"delimitador de raw string inválido '{t.value}'. "
                    "Solo se permiten '#' antes de '\"'")
    return None


# Fin parte de Josue Sanchez Calderon //////////////////////////////////////////////////////////////////////////////////////////////////


# Inicio parte de Jared Selim Beltran Martinez //////////////////////////////////////////////////////////////////////////////////////////////////

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

# Raw identifier invalido.
regexInvalidRawID = r'r\#(?![a-zA-Z_"\#])'

@TOKEN(regexInvalidRawID)
def t_INVALID_RAW_IDENTIFIER(t):
    addLexicalError(t.lexer.lexdata, t.lexer.lineno, t.lexpos, t.value,
                    "raw identifier inválido. Después de 'r#' debe ir un nombre (letra o '_')")
    return None

# Fin parte de Jared Selim Beltran Martinez //////////////////////////////////////////////////////////////////////////////////////////////////


# Inicio parte de Josue Sanchez Calderon //////////////////////////////////////////////////////////////////////////////////////////////////

# Char
@TOKEN(regexChar)
def t_CHAR(t):
    val = t.value
    content = val[1:-1]
    unicodeEscape = compiledCharUEscape.fullmatch(content)

    if unicodeEscape:
        c = int(unicodeEscape.group('unicodeContent').replace('_',''), 16)

        if not isCharUnicodeStandard(c):
            addLexicalError(t.lexer.lexdata, t.lexer.lineno, t.lexpos, t.value,
                            "escape unicode no es un valor escalar Unicode válido, rango válido: \\u{0}-\\u{d7ff} y \\u{e000}-\\u{10ffff}")
            return None

        t.value = val.replace('_', '')

    return t

regexInvalidChar = r"\'(?:\\.|[^\'\\\n])*\'?"
@TOKEN(regexInvalidChar)
def t_INVALID_CHAR(t):
    val = t.value
    content = val[1:-1]
    msg = "char inválido"

    if not compiledClosedChar.fullmatch(val):
        msg = "char sin cerrar (falta ' )"

    elif content == "":
        msg = "char vacío \'\'"

    elif content[0] != "\\":
        if len(content) == 1:
            msg = "el \\t y el \\r deben escribirse como escapes"
        else:
            msg = "un char solo puede contener un carácter"

    else:
        kind = content[1] # Letra despues del \ para saber el tipo de escape
        end = None # Fin del escape

        if kind == 'x':
            escapeCont = compiledCharXEscape.match(content)
            if not escapeCont:
                msg = "escape \\x inválido (requiere exactamente 2 dígitos hexadecimales)"
            elif int(escapeCont.group('xEscapeContent'), 16) > 0x7F:
                msg = "escape \\x fuera de rango en char (máximo \\x7F)"
            else:
                end = escapeCont.end()

        elif kind == 'u':
            escapeCont = compiledCharUEscape.match(content)
            if not escapeCont:
                msg = "escape \\u inválido (formato esperado: \\u{XXXXXX})"
            elif not compiledUnicodeDigits.fullmatch(escapeCont.group('unicodeContent')):
                msg = "escape \\u{...} inválido (requiere de 1 a 6 dígitos hexadecimales)"
            else:
                c = int(escapeCont.group('unicodeContent').replace('_', ''), 16)
                if c > 0x10FFFF or 0xD800 <= c <= 0xDFFF:
                    msg = "escape \\u{...} no es un valor escalar Unicode válido"
                else:
                    end = escapeCont.end()

        elif kind in "nrt\\0\'\"":
            end = 2

        else:
            msg = f"secuencia de escape desconocida '\\{kind}'"

        if end is not None and end != len(content):
            msg = "un char solo puede contener un carácter"

    addLexicalError(t.lexer.lexdata, t.lexer.lineno, t.lexpos, val, msg)
    return None


# String
@TOKEN(regexString)
def t_STRING(t):
    val = t.value
    firstLine = t.lexer.lineno
    valid = True

    # Se recorren los escapes de izquierda a derecha, para poder detectarlos todos
    for m in compiledStringEscape.finditer(val):
        if m.group('uContent') is not None:
            c = int(m.group('uContent').replace('_', ''), 16)
            if not isCharUnicodeStandard(c):
                addLexicalError(t.lexer.lexdata, firstLine + val.count('\n', 0, m.start()),
                                t.lexpos + m.start(), m.group(0),
                                "escape unicode no es un valor escalar Unicode válido, rango válido: \\u{0}-\\u{d7ff} y \\u{e000}-\\u{10ffff}")
                valid = False

    t.lexer.lineno += val.count('\n')
    if not valid:
        return None

    # Elimina \ + \n + espacios de la sgte linea, cumpliendo el formato
    t.value = compiledStringEscape.sub(replaceStringEscape, val)
    return t

regexInvalidString = r'\"(?:\\[\s\S]?|[^\"\\])*\"?'
@TOKEN(regexInvalidString)
def t_INVALID_STRING(t):
    val = t.value
    firstLine = t.lexer.lineno

    if not compiledClosedString.fullmatch(val):
        addLexicalError(t.lexer.lexdata, firstLine, t.lexpos,
                        val.split('\n', 1)[0], "string sin cerrar (falta \")")
    else:
        problems = []

        for m in compiledAnyStringEscape.finditer(val):
            esc = m.group(0)
            msg = None

            if esc == '\r':
                msg = "CR literal no permitido en string (use el escape \\r)"
            else:
                kind = esc[1]

                if kind == 'x':
                    if len(esc) != 4:
                        msg = "escape \\x inválido (requiere exactamente 2 dígitos hexadecimales)"
                    elif int(esc[2:], 16) > 0x7F:
                        msg = "escape \\x fuera de rango en string (máximo \\x7F)"

                elif kind == 'u':
                    u = compiledCharUEscape.fullmatch(esc)
                    if not u:
                        msg = "escape \\u inválido (formato esperado: \\u{XXXXXX})"
                    elif not compiledUnicodeDigits.fullmatch(u.group('unicodeContent')):
                        msg = "escape \\u{...} inválido (requiere de 1 a 6 dígitos hexadecimales)"
                    elif not isCharUnicodeStandard(int(u.group('unicodeContent').replace('_', ''), 16)):
                        msg = "escape \\u{...} no es un valor escalar Unicode válido, rango válido: \\u{0}-\\u{d7ff} y \\u{e000}-\\u{10ffff}"

                elif kind == '\r':
                    msg = "CR literal no permitido en string (use el escape \\r)"

                elif kind not in "nrt\\0\'\"\n":
                    msg = f"secuencia de escape desconocida '{esc}'"

            if msg is not None:
                problems.append((m.start(), esc if esc != '\r' else '\\r', msg))

        if not problems:
            problems.append((0, val.split('\n', 1)[0], "string inválido"))

        for idx, lexeme, msg in problems:
            addLexicalError(t.lexer.lexdata, firstLine + val.count('\n', 0, idx),
                            t.lexpos + idx, lexeme, msg)

    t.lexer.lineno += val.count('\n')
    return None


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

regexInvalidNumber = (r'0[xob][0-9a-zA-Z_]*|[0-9][0-9_]*(?:\.[0-9][0-9_]*)?(?:[eE][+\-]?[0-9_]*)?[0-9a-zA-Z_]*')
numberBases = {'x': 16, 'b': 2, 'o': 8}

@TOKEN(regexInvalidNumber)
def t_INVALID_NUMBER(t):
    val = t.value
    msg = "literal numérico inválido"

    # Con prefijo de base 0x, 0b, 0o
    if val[:2] in ('0x', '0b', '0o'):
        kind = val[1]
        base = numberBases[kind]
        body = val[2:]
        digits = compiledBaseDigits[kind].match(body).group(0) # Calidos
        remainder = body[len(digits):] # Sobrante

        if remainder and remainder[0] in '0123456789':
            msg = f"dígito '{remainder[0]}' inválido en número entero de base {base}"
        elif digits.strip('_') == '':
            msg = f"número entero de base {base} sin dígitos válidos (se esperaba al menos uno después de '0{kind}')"
        else:
            msg = f"sufijo '{remainder}' inválido en número entero de base {base}"

    # Decimal entero o float
    else:
        m = compiledInvalidDecimal.fullmatch(val)
        isFloat = m.group('frac') is not None or m.group('exp') is not None
        exp = m.group('exp')
        rest = m.group('rest')

        if exp is not None and exp[1:].lstrip('+-').strip('_') == '':
            msg = "exponente sin dígitos (se esperaba al menos un dígito después de 'e')"

        elif rest:
            if isFloat and compiledIntSufix.match(rest):
                msg = f"sufijo '{rest}' inválido en un float (solo se permiten f32 y f64)"
            elif isFloat:
                msg = f"sufijo '{rest}' inválido en literal float (solo se permiten f32 y f64)"
            else:
                msg = f"sufijo '{rest}' inválido en literal entero (ej: u8, i32, usize, f64)"

    addLexicalError(t.lexer.lexdata, t.lexer.lineno, t.lexpos, val, msg)
    return None

# Fin parte de Josue Sanchez Calderon //////////////////////////////////////////////////////////////////////////////////////////////////

# Inicio parte de Jared Beltran //////////////////////////////////////////////////////////////////////////////////////////////////

# Estado exclusivo para recorrer los comentarios de bloque, ademas permite anidarlos
states = (
    ('comment', 'exclusive'),
)

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

# Debe llamarse al terminar de recorrer los tokens, porque avisa de comentarios de bloque sin cerrar al final del codigo
def checkUnclosedComments():
    if lexer.lexstate == 'comment':
        for (line, pos) in reversed(lexer.commentStack):
            addLexicalError(lexer.lexdata, line, pos, '/*',
                            "comentario de bloque sin cerrar (falta '*/')")
        lexer.commentStack = []
        lexer.begin('INITIAL')

# Guion bajo solo no es un identificador valido en Rust
@TOKEN(r'_(?![a-zA-Z0-9_])')
def t_UNDERSCORE(t):
    return t

# Comentarios
# Inicio comentario de una linea. No incluye saltos de linea
def t_LINE_COMMENT(t):
    r'//[^\n]*'
    pass


# Inicio de comentario de bloque, aqui pasa al estado 'comment'
def t_COMMENT_START(t):
    r'/\*'
    t.lexer.commentStack = [(t.lexer.lineno, t.lexpos)]
    t.lexer.begin('comment')


# Apertura anidada dentro de un comentario
def t_comment_open(t):
    r'/\*'
    t.lexer.commentStack.append((t.lexer.lineno, t.lexpos))


# Dentro de un comentario al momento de su cierre. Si todos estan cerrados vuelve al estado Inicial
def t_comment_close(t):
    r'\*/'
    t.lexer.commentStack.pop()
    if not t.lexer.commentStack:
        t.lexer.begin('INITIAL')


def t_comment_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


# Cualquier otro contenido del comentario se descarta como se pidio en la asignacion (AV)
def t_comment_content(t):
    r'[^/*\n]+|[/*]'
    pass

# Estandar que pide PLY para manejar errores

t_comment_ignore = ''

def t_comment_error(t):
    t.lexer.skip(1)

# Fin parte de Jared Beltran //////////////////////////////////////////////////////////////////////////////////////////////////

# Inicio Parte de Leiner David Saltos Penafiel //////////////////////////////////////////////////////////////////////////////////////////////////

regexID = r'[a-zA-Z_][a-zA-Z0-9_]*'
@TOKEN(regexID)
def t_IDENTIFIER(t):
    t.type = reserved_words.get(t.value, 'IDENTIFIER')

    if ((t.type == 'BOOLEAN_T') | (t.type == 'BOOLEAN_F')):
        t.type = "BOOLEAN"

    elif ((t.type == 'IDENTIFIER') & (t.value in typesNames)):
        t.type = 'TYPE'

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