import ply.yacc as yacc
from Analyzers.lexical import tokens, findColumn
from collections import namedtuple
from Analyzers.semantic import *

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
                 | error block
                 | for_statement
                 | method_call SEMICOLON'''
    # Semantico (Jared). Aqui cada sentencia deja en p[0] un descriptor; 'devuelve' indica si garantiza devolver un valor
    if isinstance(p[1], dict) and 'clase' in p[1]:
        p[0] = p[1]
    elif p.slice[1].type in ('function_call', 'method_call'):
        p[0] = {'clase': 'expr_semi', 'linea': p.lineno(2)}
    else:
        p[0] = {'clase': 'otro'}

# Precedencia en las operaciones - Josue Sanchez
precedence = (
    ('nonassoc', 'CLOSURE'), # el cuerpo de un closure abarca toda la expresión que sigue
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQUAL_TO', 'NOT_EQUAL_TO', 'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL_THAN', 'GREATER_EQUAL_THAN'), # Para que no sea valido a < b < c y asi
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV', 'MOD'),
    ('left', 'AS'),
    ('right', 'UMINUS', 'UNOT'), # tokens ficticios, para %prec
    ('left', 'PERIOD'), # llamada a método, es más importante (-a.abs() es -(a.abs()))
)

def p_variable_declaration(p):
    '''variable_declaration : DECLARATION ident EQUAL initializer SEMICOLON
                            | DECLARATION MUT ident EQUAL initializer SEMICOLON
                            | DECLARATION ident COLON data_type SEMICOLON
                            | DECLARATION ident COLON data_type EQUAL initializer SEMICOLON
                            | DECLARATION MUT ident COLON data_type EQUAL initializer SEMICOLON
                            | DECLARATION MUT ident COLON data_type SEMICOLON'''
    # Semantico (Jared). Aqui guarda el tipo de la variable en la tabla (el declarado, o el del valor inicial)
    # y revisa que un arreglo tenga todos sus elementos del mismo tipo (Asignacion de tipo 4)
    nombre = tipoDeclarado = tipoValor = None
    for i in range(1, len(p)):
        simbolo = p.slice[i].type
        if simbolo == 'ident':
            nombre = p[i]
        elif simbolo == 'data_type':
            tipoDeclarado = p[i]
        elif simbolo == 'initializer':
            tipoValor = p[i]
    reglaAsignacion4(nombre, tipoValor)
    tabla_simbolos["variables"][nombre] = tipoDeclarado if tipoDeclarado is not None else tipoValor

def p_constant_declaration(p):
    'constant_declaration : CONSTANT ident COLON data_type EQUAL expression SEMICOLON'
    tabla_simbolos["constantes"][p[2]] = p[4]  # Semantico (Jared). Aqui se guarda el tipo de la constante

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
    p[0] = p[1]  # Semantico (Jared). Aqui el tipo escrito en el codigo ('i32', 'bool'...) sube por p[0]

def p_data_type_referencia(p):
    '''data_type : AMPERSAND data_type
                 | AMPERSAND MUT data_type'''
    p[0] = p[len(p) - 1]  # Semantico (Jared). Aqui una referencia tiene el tipo de lo referenciado

def p_value(p):
    '''value : INTEGER
             | FLOAT
             | CHAR
             | STRING
             | RAW_STRING
             | BOOLEAN
             | BYTE_LITERAL'''
    p[0] = tipoLiteral(p.slice[1].type, p[1])  # Semantico (Jared). Aqui el tipo del literal sube por p[0]

# Nombres de variables, constantes y parametros
def p_ident(p):
    '''ident : IDENTIFIER
             | RAW_IDENTIFIER'''
    p[0] = p[1]
    #p.set_lineno(0, p.lineno(1)) # el no terminal 'ident' conserva la línea del token, útil para los nodos

def p_expression_value(p):
    'expression : value'
    p[0] = p[1]

def p_expression_ident(p):
    'expression : ident'
    p[0] = buscarVariable(p[1])  # Semantico (Jared). Aqui el tipo de la variable segun la tabla de simbolos

def p_expression_call(p):
    'expression : function_call'
    p[0] = p[1]


# Inicio Leiner David Saltos Penafiel /////////////////////////////////////////////////////////////////////////

# Semantico (Jared). Aqui la cabecera 'fn nombre(...)' es una regla propia (function_head_np / function_head_p, mas abajo)
# para saber en que funcion estamos antes de leer el cuerpo
def p_func_no_parameters(p):
    'function_no_parameters : function_head_np block'
    terminarFuncion()

def p_func_parameters(p):
    'function_parameters : function_head_p block'
    terminarFuncion()

def p_parameters(p):
    '''parameters : parameter
                  | parameters COMMA parameter'''

def p_parameter(p):
    '''parameter : ident COLON data_type
                 | MUT ident COLON data_type'''
    # Semantico (Jared). Aqui el parametro entra a la tabla de simbolos con su tipo
    tabla_simbolos["variables"][p[len(p) - 3]] = p[len(p) - 1]

def p_function_call(p):
    '''function_call : IDENTIFIER PARENL PARENR
                     | IDENTIFIER PARENL arguments PARENR'''
    p[0] = tabla_simbolos["funciones"].get(p[1])  # Semantico (Jared). Aqui se obtiene el tipo que devuelve la funcion

def p_arguments(p):
    '''arguments : expression
                 | arguments COMMA expression'''

def p_block(p):
    '''block : BRACEL BRACER
             | BRACEL body BRACER'''
    # Semantico (Jared). Aqui el bloque deja la lista de sentencias y si garantiza devolver un valor
    sentencias = p[2] if len(p) == 4 else []
    p[0] = {'sentencias': sentencias, 'devuelve': bloqueDevuelve(sentencias)}

def p_body(p):
    '''body : statement
            | body statement'''
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]  # Semantico (Jared). Aqui se arma la lista de sentencias

# Semantico (Jared). Aqui 'loop' tambien cuenta como ciclo para break / continue
def p_loop_header(p):
    'loop_header : LOOP'
    entrarCiclo()

def p_loop_statement(p):
    'loop_statement : loop_header block'
    huboBreak = salirCiclo()
    p[0] = {'clase': 'loop', 'devuelve': not huboBreak}  # un loop sin break nunca termina

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
    p[0] = p[1]  # Semantico (Jared). Aqui el tipo del valor inicial sube

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
    p[0] = 'String'  # Semantico (Jared)

def p_expression_reference(p):
    'expression : AMPERSAND expression %prec UMINUS'
    p[0] = p[2]  # Semantico (Jared)

def p_expression_mutable_reference(p):
    'expression : AMPERSAND MUT expression %prec UMINUS'
    p[0] = p[3]  # Semantico (Jared)

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
    p[0] = aritmetica(p[1], p[3])  # Semantico (Jared). Aqui el tipo del resultado

def p_expression_comparison(p):
    '''expression : expression EQUAL_TO expression
                  | expression NOT_EQUAL_TO expression
                  | expression LESS_THAN expression
                  | expression GREATER_THAN expression
                  | expression LESS_EQUAL_THAN expression
                  | expression GREATER_EQUAL_THAN expression'''
    p[0] = 'bool'  # Semantico (Jared)

def p_expression_logical(p):
    '''expression : expression AND expression
                  | expression OR expression'''
    p[0] = 'bool'  # Semantico (Jared)

def p_expression_unary_minus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = p[2]  # Semantico (Jared)

def p_expression_not(p):
    'expression : NOT expression %prec UNOT'
    p[0] = p[2] if claseDeTipo(p[2]) == 'entero' else 'bool'  # Semantico (Jared)

def p_expression_cast(p):
    'expression : expression AS data_type'
    p[0] = p[3]  # Semantico (Jared). Aqui el resultado tiene el tipo al que se convierte

def p_expression_group(p):
    'expression : PARENL expression PARENR'
    p[0] = p[2]

# += -= *=
def p_assignment_compound(p):
    '''assignment : ident PLUS_EQUAL expression SEMICOLON
                  | ident MINUS_EQUAL expression SEMICOLON
                  | ident TIMES_EQUAL expression SEMICOLON
                  | ident DIV_EQUAL expression SEMICOLON
                  | ident MOD_EQUAL expression SEMICOLON'''

# for con rango o coleccion
# Semantico (Jared). Aqui la cabecera del for es una regla propia para contar el ciclo antes de leer el cuerpo
def p_for_statement(p):
    'for_statement : for_header block'
    salirCiclo()

def p_for_header(p):
    'for_header : FOR for_variable IN for_iterable'
    entrarCiclo()

def p_for_error(p):
    'for_header : FOR error'
    addSyntacticError(p, 1, "'for' mal formado: se esperaba 'for variable in rango_o_colección { ... }'")
    entrarCiclo()

# Un for puede ser, for x in y puede ser for _ in
def p_for_variable(p):
    '''for_variable : ident
                    | UNDERSCORE'''
    if p.slice[1].type == 'ident':
        tabla_simbolos["variables"][p[1]] = None  # Semantico (Jared). Aqui la variable del for existe, su tipo no se conoce

# Un rango (a..b) o cualquier expresión que sea una colección
def p_for_iterable(p):
    '''for_iterable : expression
                    | expression RANGE expression
                    | expression RANGE_INCLUSIVE expression'''

# Llamadas a métodos v.iter(), x.to_string(), v.push(1)
def p_method_call(p):
    '''method_call : expression PERIOD IDENTIFIER PARENL PARENR
                   | expression PERIOD IDENTIFIER PARENL arguments PARENR'''
    p[0] = METODOS_CONOCIDOS.get(p[3])  # Semantico (Jared). Aqui solo se conoce el tipo de algunos metodos (len, to_string)

def p_expression_method(p):
    'expression : method_call'
    p[0] = p[1]

# vec![1, 2, 3], vec![0; 10], vec![]
def p_expression_vec(p):
    'expression : VEC_MACRO array_literal'
    p[0] = 'Vec'  # Semantico (Jared)

# String::from("...")
def p_expression_string_from(p):
    'expression : TYPE_STRING DOUBLE_COLON IDENTIFIER PARENL expression PARENR'
    if p[3] != 'from':
        addSyntacticError(p, 3, f"se esperaba 'from' después de 'String::', se encontró '{p[3]}'")
    p[0] = 'String'  # Semantico (Jared)

# Closures: |a, b| a + b   |x: i32| -> i32 { x + 1 }
def p_expression_closure(p):
    '''expression : PIPE closure_params PIPE expression %prec CLOSURE
                  | PIPE closure_params PIPE return_block
                  | PIPE closure_params PIPE ARROW data_type return_block
                  | OR expression %prec CLOSURE
                  | OR return_block
                  | OR ARROW data_type return_block'''

def p_closure_params(p):
    '''closure_params : closure_param
                      | closure_params COMMA closure_param'''

def p_closure_param(p):
    '''closure_param : ident
                     | ident COLON data_type'''

# Fin parte de Josue Sanchez Calderon /////////////////////////////////////////////////////////////////////////



# Inicio parte de Jared Selim Beltran Martinez /////////////////////////////////////////////////////////

# Guarda un error sintactico propio con la linea y la columna del token numero 'index' de la regla
def addSyntacticError(p, index, message):
    line = p.lineno(index)
    column = findColumn(p.lexer.lexdata, p.lexpos(index))
    syntacticErrors.append(f"Error sintáctico (línea {line}, columna {column}): {message}")

# ---------------------------------------------------------------------------------------------
# Reglas semanticas de Jared. Cada una es una funcion; las llaman las reglas p_... de mas abajo.
# El tipo sube por p[0], se consulta la tabla de simbolos y se guarda el error.
# ---------------------------------------------------------------------------------------------

# Regla Control 1 (Jared). Aqui la condicion de if / else if / while debe ser de tipo bool
def reglaControl1(palabra, tipo, linea):
    if tipo is not None and claseDeTipo(tipo) not in (None, 'bool'):
        agregarErrorSemantico(linea, f"la condición de {palabra} debe ser de tipo bool, pero se recibió {nombreDeTipo(tipo)}")

# Regla Control 2 (Jared). Aqui else debe ir despues de un if (se llama desde p_error, mas abajo)
def reglaControl2(linea):
    agregarErrorSemantico(linea, "la estructura else debe estar precedida por una estructura if")

# Regla Control 3 (Jared). Aqui break solo puede usarse dentro de un ciclo
def reglaControl3(linea):
    if contexto["ciclos"] == 0:
        agregarErrorSemantico(linea, "la instrucción ‘break’ solo puede utilizarse dentro de un ciclo")

# Regla Control 4 (Jared). Aqui la funcion main no puede declarar un tipo de retorno
def reglaControl4(funcion, tipo, linea):
    if funcion["nombre"] == 'main':
        agregarErrorSemantico(linea, f"el tipo de retorno {nombreDeTipo(tipo)} no es válido para la función ‘main’")

# Regla Control 5 (Jared). Aqui continue solo puede usarse dentro de un ciclo
def reglaControl5(linea):
    if contexto["ciclos"] == 0:
        agregarErrorSemantico(linea, "palabra reservada continue ubicada fuera de bucle")

# Regla Asignacion de tipo 4 (Jared). Aqui todos los elementos de un arreglo deben ser del mismo tipo
def reglaAsignacion4(nombre, tipo):
    if isinstance(tipo, tuple) and len(tipo) > 2 and tipo[2]:
        linea, esperado, encontrado = tipo[2]
        agregarErrorSemantico(linea, f"el arreglo ‘{nombre}’ requiere elementos {esperado}; se encontró un valor {encontrado}")

# Regla Retorno 1 (Jared). Aqui el valor devuelto debe tener el tipo declarado en la funcion
def reglaRetorno1(tipoActual, tipoDeclarado, linea):
    if not tiposCompatibles(tipoActual, tipoDeclarado):
        agregarErrorSemantico(linea, f"el tipo de retorno {nombreDeTipo(tipoActual)} no coincide con el tipo declarado {nombreDeTipo(tipoDeclarado)}")

# Regla Retorno 2 (Jared). Aqui una funcion con '-> T' debe terminar con una expresion final sin ';'
def reglaRetorno2(tipoDeclarado, linea):
    agregarErrorSemantico(linea, f"la función espera un retorno de tipo {nombreDeTipo(tipoDeclarado)}")

# Regla Retorno 3 (Jared). Aqui una funcion sin '->' no puede devolver un valor
def reglaRetorno3(linea):
    agregarErrorSemantico(linea, "se retorna valor en una función que no define retorno")

# Regla Retorno 4 (Jared). Aqui return solo puede estar dentro del cuerpo de una funcion
def reglaRetorno4(linea):
    agregarErrorSemantico(linea, "la instrucción ‘return’ se encuentra fuera del cuerpo de una función")

# Regla Retorno 5 (Jared). Aqui con tipo de retorno, todos los caminos deben devolver un valor (if sin else)
def reglaRetorno5(funcion):
    agregarErrorSemantico(funcion["linea"], f"la función ‘{funcion['nombre']}’ puede finalizar sin devolver un valor de tipo {nombreDeTipo(funcion['ret'])}",
                          prefijo="Error semántico de retorno")

# Regla Retorno 6 (Jared). Aqui en un if / else, las dos ramas deben devolver el tipo declarado
def reglaRetorno6(funcion):
    agregarErrorSemantico(funcion["linea"], "la función definida no devuelve un valor en todos los caminos de ejecución")


# 1. Asignacion simple
# Ejemplo: total = 50;
def p_assignment(p):
    'assignment : ident EQUAL expression SEMICOLON'
    reglaAsignacion4(p[1], p[3])

# 2. Condicionales
# La condicion es una 'expression'
# 'else if' es un else seguido de otro if_statement
# El if deja en p[0] si tiene else y si todas sus ramas devuelven valor (para las reglas de Retorno 5 y 6)
def p_if_statement(p):
    '''if_statement : IF expression block
                    | IF expression block ELSE block
                    | IF expression block ELSE if_statement'''
    reglaControl1('if', p[2], p.lineno(1))
    conElse, devuelve = False, False
    if len(p) > 4:
        if p.slice[5].type == 'block':
            conElse, devuelve = True, p[3]['devuelve'] and p[5]['devuelve']
        elif isinstance(p[5], dict):
            conElse, devuelve = p[5]['con_else'], p[3]['devuelve'] and p[5]['devuelve']
    p[0] = {'clase': 'if', 'con_else': conElse, 'devuelve': devuelve}

# Cuando falla la condicion o faltan las llaves, aqui PLY descarta tokens hasta la '{' y sigue desde ahi para que pueda avanzar
def p_if_error(p):
    'if_statement : IF error block'
    addSyntacticError(p, 1, "'if' mal formado: se esperaba una condición seguida de un bloque entre llaves")

# 3. Bucle while, break y continue
# La cabecera 'while condicion' es una regla propia, asi al reconocerla ya sabemos que lo que sigue esta dentro de un ciclo
def p_while_header(p):
    'while_header : WHILE expression'
    reglaControl1('while', p[2], p.lineno(1))
    entrarCiclo()

def p_while_error(p):
    'while_header : WHILE error'
    addSyntacticError(p, 1, "'while' mal formado: se esperaba una condición seguida de un bloque entre llaves")
    entrarCiclo()

def p_while_statement(p):
    'while_statement : while_header block'
    salirCiclo()

# break puede llevar un valor (para loop): break; o break 5;
def p_break_statement(p):
    '''break_statement : BREAK SEMICOLON
                       | BREAK expression SEMICOLON'''
    reglaControl3(p.lineno(1))
    marcarBreak()

def p_continue_statement(p):
    'continue_statement : CONTINUE SEMICOLON'
    reglaControl5(p.lineno(1))

# 4. Arreglos y Tuplas
# El arreglo deja en p[0] ('array', tipo_de_sus_elementos, problema); quien lo recibe (let o asignacion) lo revisa
def p_array_literal(p):
    '''array_literal : BRACKL BRACKR
                     | BRACKL expression_list BRACKR
                     | BRACKL expression_list COMMA BRACKR
                     | BRACKL expression SEMICOLON expression BRACKR'''
    if len(p) == 3:
        p[0] = ('array', None, None)
    elif len(p) == 6:
        p[0] = ('array', p[2], None)   # [valor; cantidad]
    else:
        p[0] = tipoArreglo(p[2], p.lineno(1))

# Tupla: (), (1,), ("Carlos", 20, 1.75)
def p_tuple_literal(p):
    '''tuple_literal : PARENL PARENR
                     | PARENL expression COMMA PARENR
                     | PARENL expression COMMA expression_list PARENR
                     | PARENL expression COMMA expression_list COMMA PARENR'''
    p[0] = 'tuple'

# Lista de expresiones separadas por coma. Deja en p[0] la lista con el tipo de cada una
def p_expression_list(p):
    '''expression_list : expression
                       | expression_list COMMA expression'''
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

# Arreglos y tuplas se pueden usar como cualquier expresion (por ejemplo, un arreglo dentro de otro)
def p_expression_estructuras(p):
    '''expression : array_literal
                  | tuple_literal'''
    p[0] = p[1]

# 5. Funciones con retorno
# fn sumar(a: i32, b: i32) -> i32 { return a + b; }
# La cabecera (function_head_np / function_head_p) y el '-> tipo' (ret_spec) son reglas propias,
# asi, cuando se lee el cuerpo, ya se sabe en que funcion estamos y que tipo debe devolver
def p_function_head_np(p):
    'function_head_np : FUNCTION IDENTIFIER PARENL PARENR'
    iniciarFuncion(p[2], p.lineno(2))

def p_function_head_p(p):
    'function_head_p : FUNCTION IDENTIFIER PARENL parameters PARENR'
    iniciarFuncion(p[2], p.lineno(2))

def p_ret_spec(p):
    'ret_spec : ARROW data_type'
    funcion = contexto["funcion"]
    if funcion is not None:
        funcion["tiene_ret"] = True
        funcion["ret"] = p[2]
        tabla_simbolos["funciones"][funcion["nombre"]] = p[2]
        reglaControl4(funcion, p[2], p.lineno(1))
    p[0] = p[2]

# Al terminar el cuerpo se revisan las reglas de Retorno 1, 2, 5 y 6
def p_function_return(p):
    '''function_return : function_head_np ret_spec return_block
                       | function_head_p ret_spec return_block'''
    funcion, cuerpo = contexto["funcion"], p[3]
    if funcion is not None:
        tipoDeclarado = funcion["ret"]
        if cuerpo['tiene_cola']:
            reglaRetorno1(cuerpo['cola_tipo'], tipoDeclarado, cuerpo['linea_cola'])
        elif not bloqueDevuelve(cuerpo['sentencias']):
            # Ningun camino garantiza un valor, asi que se mira la ultima sentencia para elegir el mensaje
            if cuerpo['cola_semi']:
                ultima = {'clase': 'expr_semi', 'linea': cuerpo['linea_semi']}
            else:
                ultima = cuerpo['sentencias'][-1] if cuerpo['sentencias'] else None
            if ultima is None:
                reglaRetorno2(tipoDeclarado, cuerpo['linea_fin'])
            elif ultima['clase'] == 'expr_semi':
                reglaRetorno2(tipoDeclarado, ultima['linea'])
            elif ultima['clase'] == 'if' and ultima['con_else']:
                reglaRetorno6(funcion)
            else:
                reglaRetorno5(funcion)
    terminarFuncion()

# Cuerpo de la funcion. Admite una expresion final sin punto y coma, que es el valor devuelto.
# Las dos ultimas alternativas (expresion final CON ';') se aceptan para poder avisar el error de Retorno 2
def p_return_block(p):
    '''return_block : BRACEL BRACER
                    | BRACEL body BRACER
                    | BRACEL expression BRACER
                    | BRACEL body expression BRACER
                    | BRACEL expression SEMICOLON BRACER
                    | BRACEL body expression SEMICOLON BRACER'''
    simbolos = [p.slice[i].type for i in range(1, len(p))]
    cuerpo = {'sentencias': [], 'tiene_cola': False, 'cola_tipo': None, 'linea_cola': p.lineno(1),
              'cola_semi': False, 'linea_semi': p.lineno(1), 'linea_fin': p.lineno(len(p) - 1)}
    if 'body' in simbolos:
        cuerpo['sentencias'] = p[simbolos.index('body') + 1]
    if 'expression' in simbolos:
        posicion = simbolos.index('expression') + 1
        linea = p.lineno(posicion) or p.lineno(1)
        if 'SEMICOLON' in simbolos:
            cuerpo['cola_semi'], cuerpo['linea_semi'] = True, linea
        else:
            cuerpo['tiene_cola'], cuerpo['cola_tipo'], cuerpo['linea_cola'] = True, p[posicion], linea
    p[0] = cuerpo

# return; o return expresion;
def p_return_statement(p):
    '''return_statement : RETURN SEMICOLON
                        | RETURN expression SEMICOLON'''
    funcion = contexto["funcion"]
    conValor = len(p) == 4
    if funcion is None:
        reglaRetorno4(p.lineno(1))
    elif not funcion["tiene_ret"]:
        if conValor:
            reglaRetorno3(p.lineno(1))
    elif not conValor:
        reglaRetorno2(funcion["ret"], p.lineno(1))
    else:
        reglaRetorno1(p[2], funcion["ret"], p.lineno(1))
    p[0] = {'clase': 'return', 'devuelve': True}

# const X: i32 = return 10;  (se acepta en la gramatica para avisar el error de Retorno 4)
def p_constant_return(p):
    'constant_declaration : CONSTANT ident COLON data_type EQUAL RETURN expression SEMICOLON'
    reglaRetorno4(p.lineno(6))

# Fin parte de Jared Selim Beltran Martinez ///////////////////////////////////////////////////////////////

# Error rule for syntax errors
def p_error(p):
    if p and p.type == 'ELSE':
        reglaControl2(p.lineno)  # Semantico (Jared). Aqui un else que no sigue a un if
    if p:
        column = findColumn(p.lexer.lexdata, p.lexpos)
        mensaje = f"Error de sintaxis en token [{p.type}] -> {p.value} (Línea {p.lineno}, Columna {column})"
    else:
        mensaje = "Error de sintaxis: fin de entrada inesperado"
    syntacticErrors.append(mensaje)

# Build the parser
parser = yacc.yacc()