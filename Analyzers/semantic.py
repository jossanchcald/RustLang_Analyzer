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
    reiniciarAmbitos()  # Usado en pila de ámbitos (Leiner)

def agregarErrorSemantico(linea, mensaje, prefijo="Error semántico", columna=None):
    # Usado en mensajes con columna (Leiner)
    posicion = f"línea {linea}" if columna is None else f"línea {linea}, columna {columna}"
    item = (linea, f"{prefijo} ({posicion}): {mensaje}")
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
    ficha = buscarSimbolo(nombre)  # Usado en pila de ámbitos (Leiner)
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


def iniciarFuncion(nombre, linea, columna=None):
    verificarFuncionRepetida(nombre, linea, columna)  # Regla Identificadores 6 (Leiner)
    pila_funciones.append((contexto["funcion"], contexto["ciclos"], contexto["breaks"]))
    contexto["funcion"] = {"nombre": nombre, "linea": linea, "tiene_ret": False, "ret": None}
    contexto["ciclos"] = 0
    contexto["breaks"] = []
    tabla_simbolos["funciones"][nombre] = 'unit'
    abrirAmbito(nombre)  # pila de ámbitos (Leiner)
    declararParametrosPendientes()  # pila de ámbitos (Leiner)


def terminarFuncion():
    if pila_funciones:
        contexto["funcion"], contexto["ciclos"], contexto["breaks"] = pila_funciones.pop()
    else:
        contexto["funcion"], contexto["ciclos"], contexto["breaks"] = None, 0, []
    cerrarAmbito()  # pila de ámbitos (Leiner)


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
def verificarTipoAsignado(nombre, esperado, actual, linea, accion, columna=None):
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
        if verificarConversionImplicita(actual, esperado, linea, columna):  # Regla Conversión 1 (Leiner)
            return
        agregarErrorSemantico(linea, f"tipos incompatibles en la {accion} de '{nombre}', "
                                     f"tipo esperado '{nombreParaMensaje(esperado)}'")


def declararVariable(nombre, mutable, tipoDeclarado, tieneValor, tipoValor, linea, columna=None):
    if tipoDeclarado is not None and tieneValor:
        verificarTipoAsignado(nombre, tipoDeclarado, tipoValor, linea, 'declaración', columna)

    if isinstance(tipoValor, TipoLlamada):
        tipoValor = str(tipoValor)
    # pila de ámbitos (Leiner)
    tipo = tipoDeclarado if tipoDeclarado is not None else tipoValor
    estado = 'mut' if mutable else ('inmut' if tieneValor else 'sin_valor')
    declararSimbolo(crearFicha(nombre, tipo, estado, tieneValor, linea))


def declararConstante(nombre, tipoDeclarado, tipoValor, linea, columna=None):
    verificarTipoAsignado(nombre, tipoDeclarado, tipoValor, linea, 'declaración', columna)

    if verificarConstanteDeclarada(nombre, linea, columna):
        tabla_simbolos["constantes"][nombre] = tipoDeclarado

# Operador: '=', '+=', '-=', '*=', '/=' o '%='
def verificarAsignacion(nombre, operador, tipoValor, linea, columna=None):
    ficha = buscarSimbolo(nombre)  # pila de ámbitos (Leiner)
    if ficha is not None:
        estado = ficha["estado"] # None es parametro o variable de for asi q no se revisa
        if estado == 'inmut' or (estado == 'sin_valor' and operador != '='):
            agregarErrorSemantico(linea, f"no se puede modificar la variable inmutable '{nombre}'")
        elif estado == 'sin_valor':
            ficha["estado"] = 'inmut' # la primera asignacion si se permite
        verificarInicializadaCompuesta(ficha, operador, linea, columna)  # Regla Identificadores 5 (Leiner)
        ficha["inicializada"] = True  # Regla Identificadores 5 (Leiner)
        verificarTipoAsignado(nombre, ficha["tipo"], tipoValor, linea, 'asignación', columna)
    elif nombre in tabla_simbolos["constantes"]:
        agregarErrorSemantico(linea, f"no se puede modificar la constante '{nombre}'")
    else:
        verificarUsoVariable(nombre, linea, columna)  # Regla Identificadores 3 (Leiner)


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

# Usado en mensajes con columna
def errorIdentificadores(linea, columna, mensaje):
    agregarErrorSemantico(linea, mensaje, "Error semántico de identificadores", columna)

def errorConversion(linea, columna, mensaje):
    agregarErrorSemantico(linea, mensaje, "Error semántico de conversión", columna)


# Usado en pila de ámbitos
historial_simbolos = []

def crearFicha(nombre, tipo, estado, inicializada, linea, columna=None):
    return {
        "nombre": nombre,
        "tipo": tipo,
        "estado": estado,
        "inicializada": inicializada,
        "ambito": None,
        "linea": linea,
        "columna": columna,
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


# Usado en parámetros de funciones
parametros_pendientes = []

def agregarParametroPendiente(nombre, tipo, linea, columna=None):
    parametros_pendientes.append(crearFicha(nombre, tipo, None, True, linea, columna))

def declararParametrosPendientes():
    for ficha in parametros_pendientes:
        # Regla Identificadores 6 (Leiner)
        if ficha["nombre"] in tabla_simbolos["ambitos"][-1]["simbolos"]:
            errorIdentificadores(ficha["linea"], ficha["columna"], f"repetición de variables parámetros: '{ficha['nombre']}'")
            continue
        declararSimbolo(ficha)
    parametros_pendientes.clear()

# Usado en recuperación de errores sintácticos
def descartarParametrosPendientes():
    parametros_pendientes.clear()


# Usado en ámbito del for
variable_for_pendiente = []

def agregarVariableForPendiente(nombre, linea):
    variable_for_pendiente.append(crearFicha(nombre, None, None, True, linea))

def abrirAmbitoFor():
    abrirAmbito("for")
    for ficha in variable_for_pendiente:
        declararSimbolo(ficha)
    variable_for_pendiente.clear()


# Regla Identificadores 3 (Leiner)
usos_pendientes = []

def verificarUsoVariable(nombre, linea, columna=None):
    ficha = buscarSimbolo(nombre)
    if ficha is not None:
        # Regla Identificadores 5 (Leiner)
        if not ficha["inicializada"]:
            errorIdentificadores(linea, columna, f"la variable '{nombre}' se utiliza antes de haber sido inicializada")
        return
    if nombre in tabla_simbolos["constantes"]:
        return
    # Regla Identificadores 1 (Leiner)
    if existioAntes(nombre):
        errorIdentificadores(linea, columna, f"la variable '{nombre}' no es visible en este ámbito")
        return
    usos_pendientes.append((nombre, linea, columna))

# Regla Identificadores 3 (Leiner)
def verificarUsosPendientes():
    for nombre, linea, columna in usos_pendientes:
        if nombre in tabla_simbolos["constantes"]:
            continue
        errorIdentificadores(linea, columna, f"la variable '{nombre}' no ha sido declarada")
    usos_pendientes.clear()

# Regla Identificadores 4 (Leiner)
def verificarConstanteDeclarada(nombre, linea, columna=None):
    if nombre in tabla_simbolos["constantes"]:
        errorIdentificadores(linea, columna, f"la constante '{nombre}' ya fue declarada en este ámbito")
        return False
    return True

# Regla Identificadores 5 (Leiner)
def verificarInicializadaCompuesta(ficha, operador, linea, columna=None):
    if operador != '=' and ficha["estado"] == 'mut' and not ficha["inicializada"]:
        errorIdentificadores(linea, columna, f"la variable '{ficha['nombre']}' se utiliza antes de haber sido inicializada")

# Regla Identificadores 6 (Leiner)
def verificarFuncionRepetida(nombre, linea, columna=None):
    if nombre in tabla_simbolos["funciones"]:
        errorIdentificadores(linea, columna, f"la función '{nombre}' ya fue declarada")

# Regla Identificadores 2 (Leiner)
llamadas_pendientes = []

def verificarLlamadaFuncion(nombre, linea, columna=None):
    if nombre in tabla_simbolos["funciones"]:
        return
    if buscarSimbolo(nombre) is not None:
        return
    llamadas_pendientes.append((nombre, linea, columna))

def verificarLlamadasPendientes():
    for nombre, linea, columna in llamadas_pendientes:
        if nombre in tabla_simbolos["funciones"]:
            continue
        errorIdentificadores(linea, columna, f"la función '{nombre}' no está declarada")
    llamadas_pendientes.clear()


def verificarConversionAs(origen, destino, linea, columna=None):
    co, cd = claseDeTipo(origen), claseDeTipo(destino)
    if co is None or cd is None:
        return
    nombreOrigen, nombreDestino = nombreParaMensaje(origen), nombreParaMensaje(destino)

    # Regla Conversión 6 (Leiner)
    if cd == 'bool' and co != 'bool':
        errorConversion(linea, columna, f"no se puede convertir un valor de tipo '{nombreOrigen}' a 'bool' "
                                        f"mediante el operador 'as'")
        return

    # Regla Conversión 5 (Leiner)
    if (co == 'char' and cd == 'decimal') or (co == 'decimal' and cd == 'char') \
            or (co == 'bool' and cd == 'decimal'):
        errorConversion(linea, columna, f"conversión inválida con 'as' de tipo '{nombreOrigen}' a tipo '{nombreDestino}'")
        return

    # Regla Conversión 2 (Leiner)
    numerico = ('entero', 'decimal')
    valida = (
        (co in numerico and cd in numerico)
        or (origen == 'u8' and cd == 'char')
        or (co in ('char', 'bool') and cd == 'entero')
        or (co == cd and co in ('char', 'bool'))
    )
    if not valida:
        errorConversion(linea, columna, "conversión inválida con as")


# Regla Conversión 1 (Leiner)
def verificarConversionImplicita(actual, esperado, linea, columna=None):
    numerico = ('entero', 'decimal')
    if claseDeTipo(actual) not in numerico or claseDeTipo(esperado) not in numerico:
        return False
    if actual in ('int', 'float'):
        return False
    errorConversion(linea, columna, f"conversión implícita no permitida de '{nombreDeTipo(actual)}' a '{nombreDeTipo(esperado)}'")
    return True


# Fin parte de Leiner David Saltos Penafiel ///////////////////////////////////////////////////
