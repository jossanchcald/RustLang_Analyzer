# Errores semanticos guardados como (linea, texto)
semanticErrors = []

# Tabla de simbolos: nombre -> tipo
tabla_simbolos = {
    "variables": {},
    "funciones": {}, # 'unit' si no devuelve nada
    "constantes": {},
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
    tabla_simbolos["variables"].clear()
    tabla_simbolos["funciones"].clear()
    tabla_simbolos["constantes"].clear()
    contexto["funcion"] = None
    contexto["ciclos"] = 0
    contexto["breaks"] = []
    pila_funciones.clear()


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
    if nombre in tabla_simbolos["variables"]:
        return tabla_simbolos["variables"][nombre]
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
    pila_funciones.append((contexto["funcion"], contexto["ciclos"], contexto["breaks"]))
    contexto["funcion"] = {"nombre": nombre, "linea": linea, "tiene_ret": False, "ret": None}
    contexto["ciclos"] = 0
    contexto["breaks"] = []
    tabla_simbolos["funciones"][nombre] = 'unit'


def terminarFuncion():
    if pila_funciones:
        contexto["funcion"], contexto["ciclos"], contexto["breaks"] = pila_funciones.pop()
    else:
        contexto["funcion"], contexto["ciclos"], contexto["breaks"] = None, 0, []
    tabla_simbolos["variables"].clear()


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