# Errores semanticos guardados como (linea, texto)
semanticErrors = []

# Tabla de simbolos
tabla_simbolos = {
    "funciones": {}, # nombre -> tipo de retorno ('unit' si no devuelve nada)
    "constantes": {}, # nombre -> tipo
    "structs": {}, # nombre -> {campo: tipo}
    "ambitos": [{"nombre": "global", "simbolos": {}}],
}

# Funcion actual y cantidad de ciclos abiertos
contexto = {"funcion": None, "ciclos": 0, "breaks": []}
pila_funciones = []

ENTEROS = {'i8', 'i16', 'i32', 'i64', 'i128', 'isize', 'u8', 'u16', 'u32', 'u64', 'u128', 'usize'}
DECIMALES = {'f32', 'f64'}
PLURAL_CLASE = {'entero': 'enteros', 'decimal': 'decimales', 'bool': 'booleanos',
                'char': 'caracteres', 'cadena': 'cadenas'}
METODOS_CONOCIDOS = {'len': 'usize', 'to_string': 'String'}


def reiniciarSemantica():
    semanticErrors.clear()
    tabla_simbolos["funciones"].clear()
    tabla_simbolos["constantes"].clear()
    contexto["funcion"] = None
    contexto["ciclos"] = 0
    contexto["breaks"] = []
    pila_funciones.clear()
    tabla_simbolos["structs"].clear()
    reiniciarAmbitos()  # Semantico (David)

def agregarErrorSemantico(linea, mensaje, prefijo="Error semántico"):
    item = (linea, f"{prefijo} (línea {linea}): {mensaje}")
    if item not in semanticErrors:
        semanticErrors.append(item)


# Devuelve los errores ordenados por linea
def listaErroresSemanticos():
    return [texto for _, texto in sorted(semanticErrors, key=lambda e: e[0])]


# Tipos: 'int' y 'float' son literales sin sufijo, None es tipo desconocido
def claseDeTipo(tipo):
    if isinstance(tipo, tuple):
        return None
    if tipo in ENTEROS or tipo == 'int':
        return 'entero'
    if tipo in DECIMALES or tipo == 'float':
        return 'decimal'
    if tipo == 'bool':
        return 'bool'
    if tipo == 'char':
        return 'char'
    if tipo in ('str', 'String'):
        return 'cadena'
    return None


def nombreDeTipo(tipo):
    if tipo == 'int':
        return 'i32'
    if tipo == 'float':
        return 'f64'
    if tipo == 'unit':
        return '()'
    if isinstance(tipo, tuple):
        return 'arreglo'
    return str(tipo)


def tiposCompatibles(actual, esperado):
    ca, ce = claseDeTipo(actual), claseDeTipo(esperado)
    if ca is None or ce is None:
        return True
    if ca != ce:
        return False
    if ca == 'entero' and actual in ENTEROS and esperado in ENTEROS:
        return actual == esperado
    if ca == 'decimal' and actual in DECIMALES and esperado in DECIMALES:
        return actual == esperado
    return True


def tipoLiteral(tokenType, valor):
    if tokenType in ('INTEGER', 'FLOAT'):
        sufijo = (valor.suffix or '').lstrip('_')
        if sufijo:
            return sufijo
        return 'int' if tokenType == 'INTEGER' else 'float'
    if tokenType == 'BOOLEAN':
        return 'bool'
    if tokenType in ('STRING', 'RAW_STRING'):
        return 'str'
    if tokenType == 'CHAR':
        return 'char'
    if tokenType == 'BYTE_LITERAL':
        return 'u8'
    return None


# Tipo resultante de una operacion aritmetica
def aritmetica(a, b):
    ca, cb = claseDeTipo(a), claseDeTipo(b)
    if ca is None or cb is None:
        return None
    if ca == 'cadena' and cb == 'cadena':
        return 'String'
    if ca == cb and ca in ('entero', 'decimal'):
        return b if a in ('int', 'float') else a
    return None


def buscarVariable(nombre):
    ficha = buscarSimbolo(nombre)  # Semantico (David). Busca en la pila de ambitos, del mas interno al global
    if ficha is not None:
        return ficha["tipo"]
    return tabla_simbolos["constantes"].get(nombre)


# Devuelve ('array', tipo, problema). problema se llena si un elemento es de otro tipo diferente en el arreglo.
def tipoArreglo(elementos, linea):
    base, problema = None, None
    for tipo in elementos:
        if isinstance(tipo, tuple):
            if problema is None and len(tipo) > 2:
                problema = tipo[2]
            continue
        clase = claseDeTipo(tipo)
        if clase is None:
            continue
        if base is None:
            base = tipo
        elif problema is None and clase != claseDeTipo(base):
            problema = (linea, PLURAL_CLASE[claseDeTipo(base)], nombreDeTipo(tipo))
    return ('array', base, problema)


def iniciarFuncion(nombre, linea):
    verificarFuncionRepetida(nombre, linea)  # Semantico (David). Regla Identificadores 6: antes de registrarla
    pila_funciones.append((contexto["funcion"], contexto["ciclos"], contexto["breaks"]))
    contexto["funcion"] = {"nombre": nombre, "linea": linea, "tiene_ret": False, "ret": None}
    contexto["ciclos"] = 0
    contexto["breaks"] = []
    tabla_simbolos["funciones"][nombre] = 'unit'
    abrirAmbito(nombre)  # Semantico (David). Cada funcion tiene su propio ambito
    declararParametrosPendientes()  # Semantico (David). Los parametros se leyeron antes que la cabecera


def terminarFuncion():
    if pila_funciones:
        contexto["funcion"], contexto["ciclos"], contexto["breaks"] = pila_funciones.pop()
    else:
        contexto["funcion"], contexto["ciclos"], contexto["breaks"] = None, 0, []
    cerrarAmbito()  # Semantico (David). Antes se vaciaban todas las variables; ahora solo las de esta funcion


def entrarCiclo():
    contexto["ciclos"] += 1
    contexto["breaks"].append(False)


# Devuelve True si el ciclo tuvo un break
def salirCiclo():
    contexto["ciclos"] = max(0, contexto["ciclos"] - 1)
    return contexto["breaks"].pop() if contexto["breaks"] else False


def marcarBreak():
    if contexto["breaks"]:
        contexto["breaks"][-1] = True


def bloqueDevuelve(sentencias):
    return any(s.get('devuelve') for s in sentencias)

# Inicio parte de Josue Sanchez Calderon: asignacion de tipos ////////////////////////////////////

# Tipo que devuelve una llamada a funcion
class TipoLlamada(str):
    funcion = None

def tipoLlamada(nombre):
    tipo = tabla_simbolos["funciones"].get(nombre)
    if tipo is None:
        return None
    resultado = TipoLlamada(tipo)
    resultado.funcion = nombre
    return resultado


# Para mostrar '&str' en los mensajes
def nombreParaMensaje(tipo):
    return '&str' if tipo == 'str' else nombreDeTipo(tipo)


# Para las variables, el valor debe tener el tipo que espera la variable
def verificarTipoAsignado(nombre, esperado, actual, linea, accion):
    if esperado is None or actual is None:
        return

    if isinstance(actual, TipoLlamada):
        if actual == 'unit':
            if claseDeTipo(esperado) is not None:
                agregarErrorSemantico(linea, f"la función '{actual.funcion}' devuelve el tipo unitario '()' "
                                             f"y no puede asignarse a una variable de tipo '{nombreParaMensaje(esperado)}'")
        elif not tiposCompatibles(actual, esperado):
            agregarErrorSemantico(linea, f"la función '{actual.funcion}' devuelve el tipo '{nombreParaMensaje(actual)}' "
                                         f"y no puede asignarse a una variable de tipo '{nombreParaMensaje(esperado)}'")
        return

    if not tiposCompatibles(actual, esperado):
        if verificarConversionImplicita(actual, esperado, linea):  # Semantico (David). Regla Conversion 1: numerico a numerico
            return
        agregarErrorSemantico(linea, f"tipos incompatibles en la {accion} de '{nombre}', "
                                     f"tipo esperado '{nombreParaMensaje(esperado)}'")


def declararVariable(nombre, mutable, tipoDeclarado, tieneValor, tipoValor, linea):
    if tipoDeclarado is not None and tieneValor:
        verificarTipoAsignado(nombre, tipoDeclarado, tipoValor, linea, 'declaración')

    if isinstance(tipoValor, TipoLlamada):
        tipoValor = str(tipoValor)
    # Semantico (David). Tipo y mutabilidad se guardan en una ficha dentro del ambito actual,
    # junto con el estado de inicializacion (regla Identificadores 5)
    tipo = tipoDeclarado if tipoDeclarado is not None else tipoValor
    estado = 'mut' if mutable else ('inmut' if tieneValor else 'sin_valor')
    declararSimbolo(crearFicha(nombre, tipo, estado, tieneValor, linea))


def declararConstante(nombre, tipoDeclarado, tipoValor, linea):
    verificarTipoAsignado(nombre, tipoDeclarado, tipoValor, linea, 'declaración')

    if verificarConstanteDeclarada(nombre, linea):
        tabla_simbolos["constantes"][nombre] = tipoDeclarado

# Operador: '=', '+=', '-=', '*=', '/=' o '%='
def verificarAsignacion(nombre, operador, tipoValor, linea):
    ficha = buscarSimbolo(nombre)  # Semantico (David). La variable se busca en la pila de ambitos
    if ficha is not None:
        estado = ficha["estado"] # None es parametro o variable de for asi q no se revisa
        if estado == 'inmut' or (estado == 'sin_valor' and operador != '='):
            agregarErrorSemantico(linea, f"no se puede modificar la variable inmutable '{nombre}'")
        elif estado == 'sin_valor':
            ficha["estado"] = 'inmut' # la primera asignacion si se permite
        verificarInicializadaCompuesta(ficha, operador, linea)  # Semantico (David). Regla Identificadores 5: 'x += 1' sin valor
        ficha["inicializada"] = True  # Semantico (David). Ya recibio un valor (regla Identificadores 5)
        verificarTipoAsignado(nombre, ficha["tipo"], tipoValor, linea, 'asignación')
    elif nombre in tabla_simbolos["constantes"]:
        agregarErrorSemantico(linea, f"no se puede modificar la constante '{nombre}'")
    else:
        verificarUsoVariable(nombre, linea)  # Semantico (David). Regla Identificadores 3: asignar a algo no declarado


def definirStruct(nombre, campos):
    tabla_simbolos["structs"][nombre] = dict(campos)


# campos: lista de (nombre_campo, tipo_del_valor, linea)
def verificarCamposStruct(nombreStruct, campos):
    definicion = tabla_simbolos["structs"].get(nombreStruct)
    if definicion is None:
        return
    for campo, tipo, linea in campos:
        esperado = definicion.get(campo)
        if esperado is None or tipo is None or tiposCompatibles(tipo, esperado):
            continue
        agregarErrorSemantico(linea, f"el campo '{campo}' de la estructura '{nombreStruct}' espera un valor "
                                     f"de tipo '{nombreParaMensaje(esperado)}', pero se asignó '{nombreParaMensaje(tipo)}'")

# Fin parte de Josue Sanchez Calderon ////////////////////////////////////////////////////////////

# Inicio parte de Leiner David Saltos Penafiel ///////////////////////////////////////////////////

historial_simbolos = []

def crearFicha(nombre, tipo, estado, inicializada, linea):
    return {
        "nombre": nombre,
        "tipo": tipo,
        "estado": estado,
        "inicializada": inicializada,
        "ambito": None,
        "linea": linea,
    }


def abrirAmbito(nombre):
    tabla_simbolos["ambitos"].append({"nombre": nombre, "simbolos": {}})

def cerrarAmbito():
    if len(tabla_simbolos["ambitos"]) > 1:
        ambito = tabla_simbolos["ambitos"].pop()
        historial_simbolos.extend(ambito["simbolos"].values())

def textoAmbitoActual():
    return " > ".join(ambito["nombre"] for ambito in tabla_simbolos["ambitos"])


def declararSimbolo(ficha):
    ficha["ambito"] = textoAmbitoActual()
    tabla_simbolos["ambitos"][-1]["simbolos"][ficha["nombre"]] = ficha

def buscarSimbolo(nombre):
    for ambito in reversed(tabla_simbolos["ambitos"]):
        if nombre in ambito["simbolos"]:
            return ambito["simbolos"][nombre]
    return None

def existioAntes(nombre):
    return any(ficha["nombre"] == nombre for ficha in historial_simbolos)


def reiniciarAmbitos():
    tabla_simbolos["ambitos"].clear()
    tabla_simbolos["ambitos"].append({"nombre": "global", "simbolos": {}})
    historial_simbolos.clear()
    parametros_pendientes.clear()
    variable_for_pendiente.clear()
    usos_pendientes.clear()
    llamadas_pendientes.clear()

parametros_pendientes = []

def agregarParametroPendiente(nombre, tipo, linea):
    # estado None: Josue no revisa la mutabilidad de los parametros. Inicializada: el valor llega en la llamada
    parametros_pendientes.append(crearFicha(nombre, tipo, None, True, linea))

def declararParametrosPendientes():
    for ficha in parametros_pendientes:
        # Regla 6: el ambito de la funcion (o closure) acaba de abrirse, asi que si el nombre ya esta
        # en el, es porque otro parametro de la misma lista se llama igual
        if ficha["nombre"] in tabla_simbolos["ambitos"][-1]["simbolos"]:
            agregarErrorSemantico(ficha["linea"], f"repetición de variables parámetros: '{ficha['nombre']}'")
            continue
        declararSimbolo(ficha)
    parametros_pendientes.clear()

# Con un error de sintaxis, los parametros ya leidos pertenecen a una cabecera que PLY descarto
# (por ejemplo '|x x + 1'). Si no se borran, se pegarian a la siguiente funcion o closure
def descartarParametrosPendientes():
    parametros_pendientes.clear()


# Variable del for. Pasa lo mismo que con los parametros: en 'for i in 0..5', PLY completa 'i'
# antes que la cabecera del for. Se guarda aqui y se declara cuando se abre el ambito del for
variable_for_pendiente = []

def agregarVariableForPendiente(nombre, linea):
    # tipo None: no se conoce. estado None: Josue no revisa su mutabilidad. Inicializada: toma cada valor del rango
    variable_for_pendiente.append(crearFicha(nombre, None, None, True, linea))

# Se llama desde la cabecera del for: abre su ambito y mete ahi la variable (si la hay; 'for _ in' no tiene)
def abrirAmbitoFor():
    abrirAmbito("for")
    for ficha in variable_for_pendiente:
        declararSimbolo(ficha)
    variable_for_pendiente.clear()

# Regla Identificadores 3 (David)
usos_pendientes = []  # (nombre, linea)

def verificarUsoVariable(nombre, linea):
    ficha = buscarSimbolo(nombre)
    if ficha is not None:                      # variable visible en algun ambito abierto
        # Regla 5: existe, pero se declaro sin valor y todavia no se le asigno uno
        if not ficha["inicializada"]:
            agregarErrorSemantico(linea, f"la variable '{nombre}' se utiliza antes de haber sido inicializada",
                                  "Error semántico de identificadores")
        return
    if nombre in tabla_simbolos["constantes"]: # constante ya declarada
        return
    # Regla 1
    if existioAntes(nombre):                   # existio, pero en un ambito ya cerrado
        agregarErrorSemantico(linea, f"la variable '{nombre}' no es visible en este ámbito")
        return
    usos_pendientes.append((nombre, linea))

def verificarUsosPendientes():
    for nombre, linea in usos_pendientes:
        if nombre in tabla_simbolos["constantes"]: # era una constante declarada mas abajo
            continue
        agregarErrorSemantico(linea, f"la variable '{nombre}' no ha sido declarada")
    usos_pendientes.clear()

# Regla 4
def verificarConstanteDeclarada(nombre, linea):
    if nombre in tabla_simbolos["constantes"]:
        agregarErrorSemantico(linea, f"la constante '{nombre}' ya fue declarada en este ámbito")
        return False
    return True

# Regla 5: 'x += 1' lee el valor de x antes de cambiarlo, asi que x ya debe tener valor.
# Solo para 'mut': si es 'sin_valor', Josue ya reporta que no se puede modificar
def verificarInicializadaCompuesta(ficha, operador, linea):
    if operador != '=' and ficha["estado"] == 'mut' and not ficha["inicializada"]:
        agregarErrorSemantico(linea, f"la variable '{ficha['nombre']}' se utiliza antes de haber sido inicializada",
                              "Error semántico de identificadores")

# Regla 6: dos funciones con el mismo nombre. Se llama antes de que iniciarFuncion la registre
def verificarFuncionRepetida(nombre, linea):
    if nombre in tabla_simbolos["funciones"]:
        agregarErrorSemantico(linea, f"la función '{nombre}' ya fue declarada")

# Regla 2: funcion llamada sin estar declarada. Como la regla 3, se revisa al final,
# porque en Rust una funcion puede declararse mas abajo de donde se llama
llamadas_pendientes = []  # (nombre, linea)

def verificarLlamadaFuncion(nombre, linea):
    if nombre in tabla_simbolos["funciones"]: # ya declarada
        return
    if buscarSimbolo(nombre) is not None:     # variable visible, por ejemplo un closure: add(1, 2)
        return
    llamadas_pendientes.append((nombre, linea))

def verificarLlamadasPendientes():
    for nombre, linea in llamadas_pendientes:
        if nombre in tabla_simbolos["funciones"]: # se declaro mas abajo
            continue
        agregarErrorSemantico(linea, f"la función '{nombre}' no está declarada")
    llamadas_pendientes.clear()


# Conversiones con 'as'. origen: tipo de la expresion; destino: tipo escrito despues de 'as'.
# Se revisan de la regla mas especifica a la mas general (6, 5 y 2) y se reporta solo un error
def verificarConversionAs(origen, destino, linea):
    co, cd = claseDeTipo(origen), claseDeTipo(destino)
    if co is None or cd is None: # tipo desconocido (None, tupla, struct...): no se reporta nada
        return
    nombreOrigen, nombreDestino = nombreParaMensaje(origen), nombreParaMensaje(destino)

    # Regla Conversion 6: nada se convierte a bool con 'as' (salvo bool as bool, que no cambia nada)
    if cd == 'bool' and co != 'bool':
        agregarErrorSemantico(linea, f"no se puede convertir un valor de tipo '{nombreOrigen}' a 'bool' "
                                     f"mediante el operador 'as'", "Error semántico de conversión")
        return

    # Regla Conversion 5: char <-> flotante y bool -> flotante
    if (co == 'char' and cd == 'decimal') or (co == 'decimal' and cd == 'char') \
            or (co == 'bool' and cd == 'decimal'):
        agregarErrorSemantico(linea, f"conversión inválida con 'as' de tipo '{nombreOrigen}' a tipo '{nombreDestino}'")
        return

    # Regla Conversion 2: solo se permite lo de esta lista
    numerico = ('entero', 'decimal')
    valida = (
        (co in numerico and cd in numerico)       # numerico <-> numerico
        or (origen == 'u8' and cd == 'char')      # u8 -> char (otro entero no: '65 as char' falla en Rust)
        or (co in ('char', 'bool') and cd == 'entero')  # char o bool -> entero
        or (co == cd and co in ('char', 'bool'))  # char as char, bool as bool (no cambian nada)
    )
    if not valida:
        agregarErrorSemantico(linea, "conversión inválida con as")


# Regla Conversion 1: Rust no convierte numeros solos de un tipo a otro ('let b: f64 = a;' con a: i32).
# Se llama desde verificarTipoAsignado (de Josue) cuando los tipos ya resultaron incompatibles.
# Devuelve True si era este caso, para que Josue no reporte ademas "tipos incompatibles".
# Los literales sin sufijo ('int'/'float', como 'let x: f64 = 5;') se dejan con el mensaje de Josue:
# ahi no hay un valor de otro tipo numerico que convertir, sino un literal mal escrito
def verificarConversionImplicita(actual, esperado, linea):
    numerico = ('entero', 'decimal')
    if claseDeTipo(actual) not in numerico or claseDeTipo(esperado) not in numerico:
        return False
    if actual in ('int', 'float'):
        return False
    agregarErrorSemantico(linea, f"conversión implícita no permitida de '{nombreDeTipo(actual)}' a '{nombreDeTipo(esperado)}'")
    return True


# Fin parte de Leiner David Saltos Penafiel ///////////////////////////////////////////////////