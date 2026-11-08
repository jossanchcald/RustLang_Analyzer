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
                 | constant_declaration
                 | function_no_parameters
                 | function_parameters'''

def p_variable_declaration(p):
    '''variable_declaration : DECLARATION IDENTIFIER EQUAL value SEMICOLON
                            | DECLARATION MUT IDENTIFIER EQUAL value SEMICOLON
                            | DECLARATION IDENTIFIER COLON data_type SEMICOLON
                            | DECLARATION IDENTIFIER COLON data_type EQUAL value SEMICOLON
                            | DECLARATION MUT IDENTIFIER COLON data_type EQUAL value SEMICOLON'''

def p_constant_declaration(p):
    'constant_declaration : CONSTANT IDENTIFIER COLON data_type EQUAL value SEMICOLON'

def p_data_type(p):
    '''data_type : TYPE_I8
                 | TYPE_I16
                 | TYPE_I32
                 | TYPE_I64
                 | TYPE_I128
                 | TYPE_ISIZE
                 | TYPE_U8
                 | TYPE_U16
                 | TYPE_U32
                 | TYPE_U64
                 | TYPE_U128
                 | TYPE_USIZE
                 | TYPE_F32
                 | TYPE_F64
                 | TYPE_BOOL
                 | TYPE_CHAR
                 | TYPE_STR
                 | TYPE_STRING
                 | TYPE_VEC
                 | TYPE_HASHMAP
                 | TYPE_OPTION
                 | TYPE_RESULT'''

def p_value(p):
    '''value : INTEGER
            | FLOAT
            | CHAR
            | STRING
            | RAW_STRING
            | BOOLEAN
            | BYTE_LITERAL'''

# Inicio Leiner David Saltos Penafiel /////////////////////////////////////////////////////////////////////////

def p_func_no_parameters(p):
    'function_no_parameters : FUNCTION IDENTIFIER PARENL PARENR block'

def p_func_parameters(p):
    'function_parameters : FUNCTION IDENTIFIER PARENL parameters PARENR block'

# Uno o mas parametros separados por coma
def p_parameters(p):
    '''parameters : parameter
                  | parameters COMMA parameter'''

def p_parameter(p):
    '''parameter : IDENTIFIER COLON data_type
                 | MUT IDENTIFIER COLON data_type'''

# Bloque dentro de delimitadores 
def p_block(p):
    '''block : BRACEL BRACER
             | BRACEL body BRACER'''

def p_body(p):
    '''body : statement
            | body statement'''


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
