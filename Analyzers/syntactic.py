import ply.yacc as yacc
from Analyzers.lexical import tokens, findColumn
from collections import namedtuple

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
                 | function_parameters
                 | function_call SEMICOLON'''

# Precedencia en las operaciones - Josue Sanchez
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQUAL_TO', 'NOT_EQUAL_TO', 'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL_THAN', 'GREATER_EQUAL_THAN'), # Para que no sea valido a < b < c y asi
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV', 'MOD'),
    ('left', 'AS'),
    ('right', 'UMINUS', 'UNOT'), # tokens ficticios, para %prec
)

# Nodos
Literal = namedtuple('Literal', ['kind', 'value', 'line'])
Var = namedtuple('Var', ['name', 'line'])
BinOp = namedtuple('BinOp', ['op', 'left', 'right', 'line'])
UnaryOp = namedtuple('UnaryOp', ['op', 'operand', 'line'])
Cast = namedtuple('Cast', ['expr', 'type', 'line'])

def p_variable_declaration(p):
    '''variable_declaration : DECLARATION ident EQUAL expression SEMICOLON
                            | DECLARATION MUT ident EQUAL expression SEMICOLON
                            | DECLARATION ident COLON data_type SEMICOLON
                            | DECLARATION ident COLON data_type EQUAL expression SEMICOLON
                            | DECLARATION MUT ident COLON data_type EQUAL expression SEMICOLON
                            | DECLARATION MUT ident COLON data_type SEMICOLON'''

def p_constant_declaration(p):
    'constant_declaration : CONSTANT ident COLON data_type EQUAL expression SEMICOLON'

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
    p[0] = Literal(p.slice[1].type, p[1], p.lineno(1))

# Nombres de variables, constantes y parametros
def p_ident(p):
    '''ident : IDENTIFIER
             | RAW_IDENTIFIER'''
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1)) # el no terminal 'ident' conserva la línea del token

def p_expression_value(p):
    'expression : value'
    p[0] = p[1]

def p_expression_ident(p):
    'expression : ident'
    p[0] = Var(p[1], p.lineno(1))

def p_expression_call(p):
    'expression : function_call'
    p[0] = p[1]

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
    '''parameter : ident COLON data_type
                 | MUT ident COLON data_type'''

def p_function_call(p):
    '''function_call : IDENTIFIER PARENL PARENR
                     | IDENTIFIER PARENL arguments PARENR'''

def p_arguments(p):
    '''arguments : expression
                 | arguments COMMA expression'''

def p_block(p):
    '''block : BRACEL BRACER
             | BRACEL body BRACER'''

def p_body(p):
    '''body : statement
            | body statement'''

# Inicio parte de Josue Sanchez Calderon /////////////////////////////////////////////////////////////////////////

def p_expression_arithmetic(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULT expression
                  | expression DIV expression
                  | expression MOD expression'''
    p[0] = BinOp(p[2], p[1], p[3], p.lineno(2))

def p_expression_comparison(p):
    '''expression : expression EQUAL_TO expression
                  | expression NOT_EQUAL_TO expression
                  | expression LESS_THAN expression
                  | expression GREATER_THAN expression
                  | expression LESS_EQUAL_THAN expression
                  | expression GREATER_EQUAL_THAN expression'''
    p[0] = BinOp(p[2], p[1], p[3], p.lineno(2))

def p_expression_logical(p):
    '''expression : expression AND expression
                  | expression OR expression'''
    p[0] = BinOp(p[2], p[1], p[3], p.lineno(2))

def p_expression_unary_minus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = UnaryOp(p[1], p[2], p.lineno(1))

def p_expression_not(p):
    'expression : NOT expression %prec UNOT'
    p[0] = UnaryOp(p[1], p[2], p.lineno(1))

def p_expression_cast(p):
    'expression : expression AS data_type'
    p[0] = Cast(p[1], p[3], p.lineno(2))

def p_expression_group(p):
    'expression : PARENL expression PARENR'
    p[0] = p[2]

# Fin parte de Josue Sanchez Calderon /////////////////////////////////////////////////////////////////////////

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
