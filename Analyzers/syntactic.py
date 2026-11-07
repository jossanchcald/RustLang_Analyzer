import ply.yacc as yacc
from Analyzers.lexical import tokens, findColumn

syntacticErrors = []

# Regla inicial para que se pueda leer mas de una linea
def p_program(p):
    '''program : statement
               | program statement'''


# Aqui poner los tipos de sentencias. SI crean una nueva funcion deben de ponerla aqui 
def p_statement(p):
    '''statement : variable_declaration
                 | constant_declaration'''

def p_variable_declaration(p):
    '''variable_declaration : DECLARATION IDENTIFIER EQUAL value SEMICOLON
                            | DECLARATION MUT IDENTIFIER EQUAL value SEMICOLON
                            | DECLARATION IDENTIFIER COLON TYPE SEMICOLON
                            | DECLARATION IDENTIFIER COLON TYPE EQUAL value SEMICOLON
                            | DECLARATION MUT IDENTIFIER COLON TYPE EQUAL value SEMICOLON'''

def p_constant_declaration(p):
    'constant_declaration : CONSTANT IDENTIFIER COLON TYPE EQUAL value SEMICOLON'

def p_value(p):
    '''value : INTEGER
            | FLOAT
            | CHAR
            | STRING
            | RAW_STRING
            | BOOLEAN
            | BYTE_LITERAL'''

# Error rule for syntax errors
def p_error(p):
    if p:
        column = findColumn(p.lexer.lexdata, p.lexpos)
        mensaje = f"Error de sintaxis en token [{p.type}] -> {p.value} (Línea {p.lineno}, Columna {column})"
    else:
        mensaje = "Error de sintaxis: fin de entrada inesperado"
    syntacticErrors.append(mensaje)

# Build the parser
parser = yacc.yacc()
