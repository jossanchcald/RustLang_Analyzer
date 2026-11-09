import ply.yacc as yacc
from Analyzers.lexical import tokens, findColumn
from collections import namedtuple

syntacticErrors = []

# Regla inicial para que se pueda leer mas de una linea
def p_program(p):
    '''program : statement
               | program statement'''

# Las alternativas 'error SEMICOLON' y 'error block' (Jared) recuperan el analisis tras una sentencia invalida
def p_statement(p):
    '''statement : variable_declaration
                 | constant_declaration
                 | function_no_parameters
                 | function_parameters
                 | function_call SEMICOLON
                 | loop_statement
                 | struct_definition
                 | enum_definition
                 | print_statement
                 | input_statement
                 | assignment
                 | if_statement
                 | while_statement
                 | break_statement
                 | continue_statement
                 | return_statement
                 | function_return
                 | error SEMICOLON
                 | error block'''

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
    '''variable_declaration : DECLARATION ident EQUAL initializer SEMICOLON
                            | DECLARATION MUT ident EQUAL initializer SEMICOLON
                            | DECLARATION ident COLON data_type SEMICOLON
                            | DECLARATION ident COLON data_type EQUAL initializer SEMICOLON
                            | DECLARATION MUT ident COLON data_type EQUAL initializer SEMICOLON
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

def p_data_type_referencia(p):
    '''data_type : AMPERSAND data_type
                 | AMPERSAND MUT data_type'''

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

def p_loop_statement(p):
    'loop_statement : LOOP block'

def p_struct_definition(p):
    '''struct_definition : STRUCT IDENTIFIER BRACEL struct_fields BRACER
                         | STRUCT IDENTIFIER BRACEL struct_fields COMMA BRACER'''

def p_struct_fields(p):
    '''struct_fields : struct_field
                     | struct_fields COMMA struct_field'''

def p_struct_field(p):
    'struct_field : IDENTIFIER COLON data_type'

def p_initializer(p):
    '''initializer : expression
                   | struct_instance'''

def p_struct_instance(p):
    'struct_instance : IDENTIFIER BRACEL field_values BRACER'

def p_field_values(p):
    '''field_values : field_value
                    | field_values COMMA field_value'''

def p_field_value(p):
    'field_value : IDENTIFIER COLON expression'

def p_enum_definition(p):
    '''enum_definition : ENUM IDENTIFIER BRACEL enum_variants BRACER
                       | ENUM IDENTIFIER BRACEL enum_variants COMMA BRACER'''

def p_enum_variants(p):
    '''enum_variants : IDENTIFIER
                     | enum_variants COMMA IDENTIFIER'''

def p_print_statement(p):
    '''print_statement : PRINTLN NOT PARENL STRING PARENR SEMICOLON
                       | PRINTLN NOT PARENL STRING COMMA arguments PARENR SEMICOLON'''

def p_expression_string_new(p):
    'expression : TYPE_STRING DOUBLE_COLON IDENTIFIER PARENL PARENR'
    if p[3] != 'new':
        column = findColumn(p.lexer.lexdata, p.lexpos(3))
        syntacticErrors.append(f"Error de sintaxis en token [IDENTIFIER] -> {p[3]} (Línea {p.lineno(3)}, Columna {column})")

def p_expression_reference(p):
    'expression : AMPERSAND expression %prec UMINUS'
    p[0] = UnaryOp(p[1], p[2], p.lineno(1))

def p_expression_mutable_reference(p):
    'expression : AMPERSAND MUT expression %prec UMINUS'
    p[0] = UnaryOp('&mut', p[3], p.lineno(1))

def p_input_statement(p):
    'input_statement : IDENTIFIER DOUBLE_COLON IDENTIFIER DOUBLE_COLON IDENTIFIER PARENL PARENR PERIOD IDENTIFIER PARENL AMPERSAND MUT ident PARENR PERIOD IDENTIFIER PARENL STRING PARENR SEMICOLON'
    for position, name in ((1, 'std'), (3, 'io'), (5, 'stdin'), (9, 'read_line'), (16, 'expect')):
        if p[position] != name:
            column = findColumn(p.lexer.lexdata, p.lexpos(position))
            syntacticErrors.append(f"Error de sintaxis en token [IDENTIFIER] -> {p[position]} (Línea {p.lineno(position)}, Columna {column})")
            break

# Fin parte de Leiner David Saltos Penafiel ///////////////////////////////////////////////////////////////////////////

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

# Inicio parte de Jared Selim Beltran Martinez /////////////////////////////////////////////////////////

# Guarda un error sintactico propio con la linea y la columna del token numero 'index' de la regla
def addSyntacticError(p, index, message):
    line = p.lineno(index)
    column = findColumn(p.lexer.lexdata, p.lexpos(index))
    syntacticErrors.append(f"Error sintáctico (línea {line}, columna {column}): {message}")

# 1. Asignacion simple
# Ejemplo: total = 50;
def p_assignment(p):
    'assignment : ident EQUAL expression SEMICOLON'

# 2. Condicionales
# La condicion es una 'expression'
# 'else if' es un else seguido de otro if_statement
def p_if_statement(p):
    '''if_statement : IF expression block
                    | IF expression block ELSE block
                    | IF expression block ELSE if_statement'''

# Cuando falla la condicion o faltan las llaves, aqui PLY descarta tokens hasta la '{' y sigue desde ahi para que pueda avanzar
def p_if_error(p):
    'if_statement : IF error block'
    addSyntacticError(p, 1, "'if' mal formado: se esperaba una condición seguida de un bloque entre llaves")

# 3. Bucle while, break y continue
def p_while_statement(p):
    'while_statement : WHILE expression block'

def p_while_error(p):
    'while_statement : WHILE error block'
    addSyntacticError(p, 1, "'while' mal formado: se esperaba una condición seguida de un bloque entre llaves")

# break puede llevar un valor (para loop): break; o break 5;
def p_break_statement(p):
    '''break_statement : BREAK SEMICOLON
                       | BREAK expression SEMICOLON'''

def p_continue_statement(p):
    'continue_statement : CONTINUE SEMICOLON'

# 4. Arreglos y Tuplas
def p_array_literal(p):
    '''array_literal : BRACKL BRACKR
                     | BRACKL expression_list BRACKR
                     | BRACKL expression_list COMMA BRACKR
                     | BRACKL expression SEMICOLON expression BRACKR'''

# Tupla: (), (1,), ("Carlos", 20, 1.75)
def p_tuple_literal(p):
    '''tuple_literal : PARENL PARENR
                     | PARENL expression COMMA PARENR
                     | PARENL expression COMMA expression_list PARENR
                     | PARENL expression COMMA expression_list COMMA PARENR'''

# Lista de expresiones separadas por coma
def p_expression_list(p):
    '''expression_list : expression
                       | expression_list COMMA expression'''

# Arreglos y tuplas se pueden usar como cualquier expresion (por ejemplo, un arreglo dentro de otro)
def p_expression_estructuras(p):
    '''expression : array_literal
                  | tuple_literal'''
    p[0] = p[1]

# 5. Funciones con retorno
# fn sumar(a: i32, b: i32) -> i32 { return a + b; }
def p_function_return(p):
    '''function_return : FUNCTION IDENTIFIER PARENL PARENR ARROW data_type return_block
                       | FUNCTION IDENTIFIER PARENL parameters PARENR ARROW data_type return_block'''

# Cuerpo de la funcion: admite una expresion final sin punto y coma, que es el valor devuelto
def p_return_block(p):
    '''return_block : BRACEL BRACER
                    | BRACEL body BRACER
                    | BRACEL expression BRACER
                    | BRACEL body expression BRACER'''

# return; o return expresion;
def p_return_statement(p):
    '''return_statement : RETURN SEMICOLON
                        | RETURN expression SEMICOLON'''

# Fin parte de Jared Selim Beltran Martinez ///////////////////////////////////////////////////////////////

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