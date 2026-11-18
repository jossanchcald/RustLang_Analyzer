import re
import tkinter as tk
from tkinter import ttk, filedialog, font as tkfont
from pathlib import Path

from datetime import datetime
from Analyzers.lexical import lexer, lexicalErrors, checkUnclosedComments, findColumn
from Analyzers.syntactic import parser, syntacticErrors
from Analyzers import semantic
import gatitos

CARPETA = Path(__file__).resolve().parent
EJEMPLOS = CARPETA / "Algorithms"
IMAGENES = CARPETA / "Imagenes"
NOMBRE_LOG = "interfaz"  # nombre que llevan los logs generados desde la interfaz
LOGS = CARPETA / "Logs"
ALTO_GATITO = 72  # alto maximo (en pixeles) de las imagenes de la carpeta Imagenes/gatitos

# Colores de la interfaz
FONDO = "#fde6ee"
PUNTOS = "#f7c4d6"
TARJETA = "#ffffff"
BORDE = "#f0d3de"
TEXTO = "#1f2925"
TEXTO_SUAVE = "#66716b"
ACENTO = "#f9c6d8"
ACENTO_TEXTO = "#8a2350"
ROJO = "#d93c3c"
ROJO_SUAVE = "#fdeaea"
CODIGO_FONDO = "#f6f1f4"

CATEGORIAS = {
    "Léxico": {"fondo": "#fdf0d2", "texto": "#9a5b00"},
    "Sintáctico": {"fondo": "#e2edfc", "texto": "#1f4fb8"},
    "Semántico": {"fondo": "#ece6fb", "texto": "#6a3fc4"},
}

# Modos que se pueden elegir en el desplegable del boton de analisis
MODOS = {
    "completo": "Análisis completo",
    "lexico": "Solo léxico",
    "sintactico": "Solo sintáctico",
    "semantico": "Solo semántico",
}

# Categorias de error que informa cada modo
ANALIZA = {
    "completo": ("Léxico", "Sintáctico", "Semántico"),
    "lexico": ("Léxico",),
    "sintactico": ("Sintáctico",),
    "semantico": ("Semántico",),
}


# ---------------------------------------------------------------------------------------------
# Analisis: ejecuta los analizadores pedidos y devuelve los errores y los simbolos como listas
# ---------------------------------------------------------------------------------------------

PREFIJO_ERROR = re.compile(r"^Error[^(]*\([^)]*\):\s*")
POSICION = re.compile(r"[Ll]ínea (\d+)(?:, [Cc]olumna (\d+))?")


def separarMensaje(texto):
    # 'Error semántico (línea 5, columna 9): mensaje' -> (5, 9, 'mensaje')
    posicion = POSICION.search(texto)
    linea = int(posicion.group(1)) if posicion else None
    columna = int(posicion.group(2)) if posicion and posicion.group(2) else None
    return linea, columna, PREFIJO_ERROR.sub("", texto)


def mensajeSintactico(texto, lineas):
    linea, columna, mensaje = separarMensaje(texto)
    token = re.match(r"Error de sintaxis en token \[(\w+)\] -> (.*) \(Línea", texto)
    if token:
        mensaje = f"token inesperado '{token.group(2)}'"
        anterior = linea - 1 if linea else 0
        while anterior > 0 and not lineas[anterior - 1].strip():
            anterior -= 1
        if anterior > 0 and lineas[anterior - 1].rstrip()[-1:] not in (';', '{', '}', ','):
            mensaje += f", ¿falta ';' al final de la línea {anterior}?"
    elif "fin de entrada" in texto:
        linea = len(lineas)
    return linea, columna, mensaje


def lineasDeclaracion(tokens, palabra):
    # Linea donde se declara cada nombre que sigue a 'const' o 'fn'
    lineas = {}
    for i in range(len(tokens) - 1):
        if tokens[i].type == palabra and tokens[i + 1].type == 'IDENTIFIER':
            lineas.setdefault(tokens[i + 1].value, tokens[i + 1].lineno)
    return lineas


def textoTipo(tipo):
    if tipo is None:
        return "?"
    return semantic.nombreParaMensaje(tipo)


def analizar(codigo, modo="completo"):
    # modo: 'completo', 'lexico', 'sintactico' o 'semantico'
    # El analisis semantico ocurre mientras el parser reconoce las reglas, por eso 'sintactico' y 'semantico'
    # ejecutan el mismo recorrido del parser; la diferencia es que errores y logs se informan solo del pedido
    lineas = codigo.split("\n")
    errores = []
    conLexico = modo in ("completo", "lexico")
    conSintactico = modo in ("completo", "sintactico")
    conSemantico = modo in ("completo", "semantico")

    # Lexico (siempre se tokeniza porque es barato; solo se informa si el modo lo incluye)
    lexicalErrors.clear()
    lexer.begin('INITIAL')
    lexer.lineno = 1
    lexer.input(codigo)
    tokens = list(lexer)
    checkUnclosedComments()
    erroresLexicos = [dict(e) for e in lexicalErrors]
    if conLexico:
        for error in erroresLexicos:
            errores.append({"categoria": "Léxico", "linea": error["linea"], "columna": error["columna"],
                            "mensaje": PREFIJO_ERROR.sub("", error["mensaje"])})

    # Sintactico y semantico (el parser corre solo si el modo no es 'lexico')
    if modo != "lexico":
        syntacticErrors.clear()
        semantic.reiniciarSemantica()
        lexicalErrors.clear()
        lexer.begin('INITIAL')
        lexer.lineno = 1
        parser.parse(codigo, lexer=lexer, tracking=True)
        # Si el programa quedo incompleto (por ejemplo, un comentario sin cerrar), el parser no llega a la regla
        # inicial y las variables y funciones pendientes no se revisan; aqui se revisan siempre
        semantic.verificarUsosPendientes()
        semantic.verificarLlamadasPendientes()
        if conSintactico:
            for texto in syntacticErrors:
                linea, columna, mensaje = mensajeSintactico(texto, lineas)
                errores.append({"categoria": "Sintáctico", "linea": linea, "columna": columna, "mensaje": mensaje})
        if conSemantico:
            for linea, texto in semantic.semanticErrors:
                _, columna, mensaje = separarMensaje(texto)
                errores.append({"categoria": "Semántico", "linea": linea, "columna": columna, "mensaje": mensaje})

    textoLogs = guardarLogs(codigo, tokens, erroresLexicos, modo)
    if modo == "semantico" and syntacticErrors:
        textoLogs += " · ⚠ hay errores sintácticos"
    errores.sort(key=lambda e: (e["linea"] or 0, e["columna"] or 0))
    for error in errores:
        numero = error["linea"]
        error["fragmento"] = lineas[numero - 1].strip() if numero and numero <= len(lineas) else ""

    filasTokens = [(t.type, str(t.value), t.lineno, findColumn(codigo, t.lexpos)) for t in tokens] if conLexico else []
    simbolos = tablaSimbolos(tokens) if conSemantico else []
    return errores, simbolos, textoLogs, filasTokens


def rutaLogUnica(prefijo, formato, ahora):
    # Si ya existe un log del mismo tipo en el mismo minuto, agrega -2, -3... para no sobrescribirlo
    base = f"{prefijo}-{NOMBRE_LOG}-{ahora.strftime(formato)}"
    ruta = LOGS / f"{base}.txt"
    numero = 2
    while ruta.exists():
        ruta = LOGS / f"{base}-{numero}.txt"
        numero += 1
    return ruta


def guardarLogs(codigo, tokens, erroresLexicos, modo):
    # Los mismos logs que genera main.py (lexico, sintactico y semantico), pero solo los del modo elegido
    ahora = datetime.now()
    LOGS.mkdir(parents=True, exist_ok=True)
    pendientes = []

    if modo in ("completo", "lexico"):
        lexico = ["[[[[[ TOKENS RECONOCIDOS ]]]]]"]
        for tok in tokens:
            lexico.append(f"[{tok.type}] -> {tok.value} (Línea {tok.lineno}, Columna {findColumn(codigo, tok.lexpos)})")
        if erroresLexicos:
            lexico.append("\n [[[[[ ERRORES LÉXICOS ]]]]]")
            lexico += [e["mensaje"] for e in erroresLexicos]
        pendientes.append(("lexico", lexico, '%d-%m-%Y-%Hh%M'))

    if modo in ("completo", "sintactico"):
        sintactico = ["[[[[[ ERRORES SINTÁCTICOS ]]]]]"] + (list(syntacticErrors) or ["No se encontraron errores sintácticos."])
        pendientes.append(("sintactico", sintactico, '%d-%m-%Y-%Hh%M'))

    if modo in ("completo", "semantico"):
        semantico = ["[[[[[ ERRORES SEMÁNTICOS ]]]]]"] + (semantic.listaErroresSemanticos() or ["No se encontraron errores semánticos."])
        pendientes.append(("semantico", semantico, '%d%m%Y-%Hh%M'))

    for prefijo, contenido, formato in pendientes:
        rutaLogUnica(prefijo, formato, ahora).write_text("\n".join(contenido), encoding="utf-8")

    cantidad = len(pendientes)
    palabra = "logs guardados" if cantidad != 1 else "log guardado"
    return f"{cantidad} {palabra} en Logs/ ({ahora.strftime('%Hh%M')})"


def tablaSimbolos(tokens):
    simbolos = []
    lineasConst = lineasDeclaracion(tokens, 'CONSTANT')
    lineasFn = lineasDeclaracion(tokens, 'FUNCTION')

    for nombre, tipo in semantic.tabla_simbolos["constantes"].items():
        simbolos.append((nombre, textoTipo(tipo), "const", "global", lineasConst.get(nombre, "")))

    for nombre, retorno in semantic.tabla_simbolos["funciones"].items():
        tipo = "fn()" if retorno in (None, 'unit') else f"fn() -> {textoTipo(retorno)}"
        simbolos.append((nombre, tipo, "no", "global", lineasFn.get(nombre, "")))

    fichas = list(semantic.historial_simbolos)
    for ambito in semantic.tabla_simbolos["ambitos"]:
        fichas.extend(ambito["simbolos"].values())
    for ficha in fichas:
        mutable = "sí" if ficha.get("estado") == 'mut' else "no"
        ambito = (ficha.get("ambito") or "global").replace("global > ", "")
        simbolos.append((ficha["nombre"], textoTipo(ficha.get("tipo")), mutable, ambito, ficha.get("linea") or ""))

    simbolos.sort(key=lambda s: s[4] if isinstance(s[4], int) else 0)
    return simbolos


# ---------------------------------------------------------------------------------------------
# Interfaz grafica
# ---------------------------------------------------------------------------------------------

def elegirFuente(opciones, tamano, peso="normal"):
    disponibles = set(tkfont.families())
    for nombre in opciones:
        if nombre in disponibles:
            return (nombre, tamano, peso)
    return ("TkDefaultFont", tamano, peso)


class Tarjeta(tk.Frame):
    # Panel blanco con titulo, como los recuadros de la imagen
    def __init__(self, padre, titulo, derecha=None, fuentes=None):
        super().__init__(padre, bg=TARJETA, highlightbackground=BORDE, highlightthickness=1)
        cabecera = tk.Frame(self, bg=TARJETA)
        cabecera.pack(fill="x", padx=14, pady=(10, 8))
        self.titulo = tk.Label(cabecera, text=titulo, bg=TARJETA, fg=TEXTO, font=fuentes["titulo"])
        self.titulo.pack(side="left")
        self.derecha = tk.Frame(cabecera, bg=TARJETA)
        self.derecha.pack(side="right")
        if derecha:
            tk.Label(self.derecha, text=derecha, bg=TARJETA, fg=TEXTO_SUAVE, font=fuentes["pequena"]).pack()
        tk.Frame(self, bg=BORDE, height=1).pack(fill="x")
        self.cuerpo = tk.Frame(self, bg=TARJETA)
        self.cuerpo.pack(fill="both", expand=True)


class Editor(tk.Frame):
    # Area de texto con numeros de linea y un punto rojo en las lineas con error
    def __init__(self, padre, fuente):
        super().__init__(padre, bg=TARJETA)
        self.lineasError = set()
        self.margen = tk.Canvas(self, width=48, bg=TARJETA, highlightthickness=0)
        self.margen.pack(side="left", fill="y")
        self.barra = ttk.Scrollbar(self, orient="vertical", command=self.desplazar)
        self.barra.pack(side="right", fill="y")
        self.texto = tk.Text(self, font=fuente, bg=TARJETA, fg=TEXTO, insertbackground=TEXTO, relief="flat",
                             wrap="none", undo=True, padx=8, pady=6, borderwidth=0, highlightthickness=0,
                             yscrollcommand=self.alDesplazar, spacing1=2, spacing3=2)
        self.texto.pack(side="left", fill="both", expand=True)
        self.texto.tag_configure("linea_error", background=ROJO_SUAVE)
        self.texto.tag_configure("subrayado", underline=True, underlinefg=ROJO, foreground=TEXTO)
        self.texto.tag_configure("seleccion", background="#f8c9c9")
        self.fuente = fuente
        for evento in ("<KeyRelease>", "<ButtonRelease-1>", "<Configure>", "<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.texto.bind(evento, lambda e: self.after_idle(self.dibujarMargen), add="+")

    def desplazar(self, *args):
        self.texto.yview(*args)
        self.dibujarMargen()

    def alDesplazar(self, inicio, fin):
        self.barra.set(inicio, fin)
        self.dibujarMargen()

    def dibujarMargen(self):
        self.margen.delete("all")
        indice = self.texto.index("@0,0")
        while True:
            info = self.texto.dlineinfo(indice)
            if info is None:
                break
            y = info[1] + info[3] // 2
            numero = int(indice.split(".")[0])
            if numero in self.lineasError:
                self.margen.create_oval(8, y - 4, 16, y + 4, fill=ROJO, outline=ROJO)
            self.margen.create_text(40, y, anchor="e", text=str(numero), fill=TEXTO_SUAVE, font=self.fuente)
            siguiente = self.texto.index(f"{indice}+1line")
            if siguiente == indice:
                break
            indice = siguiente

    def obtener(self):
        return self.texto.get("1.0", "end-1c")

    def poner(self, codigo):
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", codigo)
        self.limpiarMarcas()

    def limpiarMarcas(self):
        for marca in ("linea_error", "subrayado", "seleccion"):
            self.texto.tag_remove(marca, "1.0", "end")
        self.lineasError = set()
        self.dibujarMargen()

    def marcarErrores(self, errores):
        self.limpiarMarcas()
        for error in errores:
            linea, columna = error["linea"], error["columna"]
            if not linea:
                continue
            self.lineasError.add(linea)
            self.texto.tag_add("linea_error", f"{linea}.0", f"{linea}.0+1line")
            if columna:
                contenido = self.texto.get(f"{linea}.0", f"{linea}.end")
                inicio = columna - 1
                palabra = re.match(r'"[^"]*"|\w+|\S', contenido[inicio:])
                fin = inicio + (len(palabra.group(0)) if palabra else 1)
                self.texto.tag_add("subrayado", f"{linea}.{inicio}", f"{linea}.{fin}")
        self.dibujarMargen()

    def irALinea(self, linea):
        self.texto.tag_remove("seleccion", "1.0", "end")
        self.texto.tag_add("seleccion", f"{linea}.0", f"{linea}.0+1line")
        self.texto.see(f"{linea}.0")
        self.texto.mark_set("insert", f"{linea}.0")
        self.texto.focus_set()
        self.dibujarMargen()


class ListaDesplazable(tk.Frame):
    # Contenedor con barra de desplazamiento para las tarjetas de errores
    def __init__(self, padre):
        super().__init__(padre, bg=TARJETA)
        self.lienzo = tk.Canvas(self, bg=TARJETA, highlightthickness=0)
        barra = ttk.Scrollbar(self, orient="vertical", command=self.lienzo.yview)
        self.interior = tk.Frame(self.lienzo, bg=TARJETA)
        self.ventana = self.lienzo.create_window((0, 0), window=self.interior, anchor="nw")
        self.lienzo.configure(yscrollcommand=barra.set)
        self.lienzo.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.interior.bind("<Configure>", lambda e: self.lienzo.configure(scrollregion=self.lienzo.bbox("all")))
        self.lienzo.bind("<Configure>", lambda e: self.lienzo.itemconfigure(self.ventana, width=e.width))
        for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.lienzo.bind_all(evento, self.rueda, add="+")

    def rueda(self, evento):
        if not str(evento.widget).startswith(str(self)):
            return
        if evento.num == 4:
            paso = -1
        elif evento.num == 5:
            paso = 1
        else:
            paso = -1 if evento.delta > 0 else 1
        self.lienzo.yview_scroll(paso, "units")

    def vaciar(self):
        for hijo in self.interior.winfo_children():
            hijo.destroy()
        self.lienzo.yview_moveto(0)


class Interfaz(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizador de Rust")
        self.geometry("1320x840")
        self.minsize(1000, 620)
        self.configure(bg=FONDO)

        texto = ["Segoe UI", "Inter", "Helvetica", "Arial"]
        codigo = ["Consolas", "JetBrains Mono", "DejaVu Sans Mono", "Courier New"]
        self.fuentes = {
            "marca": elegirFuente(texto, 12, "bold"),
            "titulo": elegirFuente(texto, 10, "bold"),
            "normal": elegirFuente(texto, 10),
            "pequena": elegirFuente(texto, 9),
            "chip": elegirFuente(texto, 8, "bold"),
            "codigo": elegirFuente(codigo, 11),
            "codigo_pequeno": elegirFuente(codigo, 9),
        }
        self.errores = []
        self.filtro = "Todos"
        self.archivo = "programa.rs"
        self.analizado = False
        self.modoAnalizado = "completo"  # modo del ultimo analisis ejecutado
        self.varModo = tk.StringVar(value="completo")  # modo elegido en el desplegable
        self.estilos()
        self.cargarImagenes()
        self.construirCabecera()
        self.construirCuerpo()
        self.mostrarDiagnostico()

    def estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        estilo.configure("Treeview", background=TARJETA, fieldbackground=TARJETA, foreground=TEXTO,
                         rowheight=26, borderwidth=0, font=self.fuentes["codigo_pequeno"])
        estilo.configure("Treeview.Heading", background=TARJETA, foreground=TEXTO_SUAVE, relief="flat",
                         font=self.fuentes["chip"], borderwidth=0)
        estilo.map("Treeview", background=[("selected", ACENTO)], foreground=[("selected", ACENTO_TEXTO)])
        estilo.map("Treeview.Heading", background=[("active", TARJETA)])
        estilo.configure("TScrollbar", background=FONDO, troughcolor=TARJETA, bordercolor=TARJETA,
                         arrowcolor=TEXTO_SUAVE, relief="flat")

    def boton(self, padre, texto, comando, principal=False):
        colores = (ACENTO, ACENTO_TEXTO, "#f5b3cb") if principal else (TARJETA, TEXTO, "#eef1ef")
        boton = tk.Button(padre, text=texto, command=comando, bg=colores[0], fg=colores[1],
                          activebackground=colores[2], activeforeground=colores[1], relief="flat",
                          font=self.fuentes["titulo"] if principal else self.fuentes["normal"],
                          padx=14, pady=6, cursor="hand2", highlightthickness=1,
                          highlightbackground=ACENTO if principal else BORDE, borderwidth=0)
        return boton

    def construirCabecera(self):
        cabecera = tk.Frame(self, bg=TARJETA, highlightbackground=BORDE, highlightthickness=1)
        cabecera.pack(fill="x")
        izquierda = tk.Frame(cabecera, bg=TARJETA)
        izquierda.pack(side="left", padx=16, pady=10)
        tk.Label(izquierda, text="{ }", bg=ACENTO, fg=ACENTO_TEXTO, font=self.fuentes["titulo"],
                 width=3, pady=4).pack(side="left", padx=(0, 10))
        nombres = tk.Frame(izquierda, bg=TARJETA)
        nombres.pack(side="left")
        tk.Label(nombres, text="Analizador de Rust", bg=TARJETA, fg=TEXTO, font=self.fuentes["marca"]).pack(anchor="w")
        tk.Label(nombres, text="Léxico · Sintáctico · Semántico", bg=TARJETA, fg=TEXTO_SUAVE,
                 font=self.fuentes["pequena"]).pack(anchor="w")

        derecha = tk.Frame(cabecera, bg=TARJETA)
        derecha.pack(side="right", padx=16)
        self.lienzoGato = tk.Canvas(cabecera, height=80, bg=TARJETA, highlightthickness=0)
        self.lienzoGato.pack(side="left", fill="x", expand=True)
        self.gato = None
        self.lienzoGato.bind("<Configure>", self.ubicarGato)
        self.boton(derecha, "Abrir archivo", self.abrirArchivo).pack(side="left", padx=4)
        self.botonEjemplos = self.boton(derecha, "Algoritmos", self.mostrarEjemplos)
        self.botonEjemplos.pack(side="left", padx=4)
        self.boton(derecha, "Limpiar", self.limpiar).pack(side="left", padx=4)

        # Boton dividido: a la izquierda ejecuta el analisis elegido, a la derecha el desplegable para elegirlo
        division = tk.Frame(derecha, bg="#f5b3cb")
        division.pack(side="left", padx=(4, 0))
        self.botonAnalizar = self.boton(division, f"▶ {MODOS[self.varModo.get()]}", self.analizarCodigo, principal=True)
        self.botonAnalizar.configure(width=15)  # ancho fijo para que no se mueva al cambiar de modo
        self.botonAnalizar.pack(side="left")
        self.botonModo = self.boton(division, "▾", self.mostrarModos, principal=True)
        self.botonModo.configure(padx=1)
        self.botonModo.pack(side="left", padx=(1, 0))

    def construirCuerpo(self):
        cuerpo = tk.Canvas(self, bg=FONDO, highlightthickness=0)
        cuerpo.pack(fill="both", expand=True)
        self.fondo = cuerpo

        self.tarjetaEditor = Tarjeta(cuerpo, "1. Editor de código · programa.rs", "Escribe o pega tu código aquí",
                                     self.fuentes)
        self.editor = Editor(self.tarjetaEditor.cuerpo, self.fuentes["codigo"])
        self.editor.pack(fill="both", expand=True)

        tarjetaTabla = Tarjeta(cuerpo, "3. Tabla de símbolos y tokens", fuentes=self.fuentes)
        self.avisoLogs = tk.Label(tarjetaTabla.derecha, text="", bg=TARJETA, fg=TEXTO_SUAVE, font=self.fuentes["pequena"])
        self.avisoLogs.pack()
        # Dos vistas en el mismo panel: la tabla de simbolos y la lista de tokens del analizador lexico
        selector = tk.Frame(tarjetaTabla.cuerpo, bg=TARJETA)
        selector.pack(fill="x", padx=10, pady=(8, 0))
        self.botonesVista = {}
        for nombre in ("Símbolos", "Tokens"):
            boton = tk.Button(selector, text=nombre, command=lambda n=nombre: self.cambiarVista(n), relief="flat",
                              font=self.fuentes["normal"], padx=10, pady=3, cursor="hand2", highlightthickness=1,
                              borderwidth=0)
            boton.pack(side="left", padx=(0, 6))
            self.botonesVista[nombre] = boton
        self.vistas = {}
        self.tabla = self.crearTabla(tarjetaTabla.cuerpo, "Símbolos", ("NOMBRE", "TIPO", "MUTABLE", "ÁMBITO", "LÍNEA"),
                                     (150, 150, 90, 170, 60))
        self.tablaTokens = self.crearTabla(tarjetaTabla.cuerpo, "Tokens", ("TOKEN", "LEXEMA", "LÍNEA", "COLUMNA"),
                                           (190, 230, 70, 80))
        self.tabla.bind("<<TreeviewSelect>>", lambda e: self.alElegirFila(self.tabla, 4))
        self.tablaTokens.bind("<<TreeviewSelect>>", lambda e: self.alElegirFila(self.tablaTokens, 2))
        self.vista = "Símbolos"
        self.cambiarVista("Símbolos")

        tarjetaDiagnostico = Tarjeta(cuerpo, "2. Diagnóstico", fuentes=self.fuentes)
        self.contador = tk.Label(tarjetaDiagnostico.derecha, text="", bg=ROJO_SUAVE, fg=ROJO,
                                 font=self.fuentes["chip"], padx=8, pady=2)
        self.contador.pack()
        self.filtros = tk.Frame(tarjetaDiagnostico.cuerpo, bg=TARJETA)
        self.filtros.pack(fill="x", padx=12, pady=(10, 6))
        self.lista = ListaDesplazable(tarjetaDiagnostico.cuerpo)
        self.lista.pack(fill="both", expand=True, padx=(12, 4), pady=(0, 10))

        self.ventanas = [cuerpo.create_window(0, 0, window=t, anchor="nw")
                         for t in (self.tarjetaEditor, tarjetaTabla, tarjetaDiagnostico)]
        self.pendiente = None
        cuerpo.bind("<Configure>", lambda e: self.programarFondo())

    # Fondo rosado con puntos, tarjetas y gatitos en el espacio libre de abajo
    def programarFondo(self):
        if self.pendiente:
            self.after_cancel(self.pendiente)
        self.pendiente = self.after(60, self.dibujarFondo)

    def dibujarFondo(self):
        c = self.fondo
        ancho, alto = c.winfo_width(), c.winfo_height()
        margen, separacion, abajo = 18, 14, 82
        c.delete("decoracion")
        if self.mosaico is not None:
            paso_x, paso_y = self.mosaico.width(), self.mosaico.height()
            for x in range(0, ancho, paso_x):
                for y in range(0, alto, paso_y):
                    c.create_image(x, y, image=self.mosaico, anchor="nw", tags="decoracion")

        util = ancho - 2 * margen - separacion
        izquierda = int(util * 0.6)
        derecha = util - izquierda
        altoUtil = alto - margen - abajo
        altoEditor = int((altoUtil - separacion) * 0.6)
        altoTabla = altoUtil - separacion - altoEditor
        editor, tabla, diagnostico = self.ventanas
        c.coords(editor, margen, margen)
        c.itemconfigure(editor, width=izquierda, height=altoEditor)
        c.coords(tabla, margen, margen + altoEditor + separacion)
        c.itemconfigure(tabla, width=izquierda, height=altoTabla)
        c.coords(diagnostico, margen + izquierda + separacion, margen)
        c.itemconfigure(diagnostico, width=derecha, height=altoUtil)

        piso = alto - 8
        if self.imagenesGatitos:
            # Las imagenes de Imagenes/gatitos se reparten a lo ancho del espacio de abajo
            espacio = (ancho - 2 * margen) / len(self.imagenesGatitos)
            for i, imagen in enumerate(self.imagenesGatitos):
                c.create_image(margen + espacio * (i + 0.5), alto, image=imagen, anchor="s", tags="decoracion")
        else:
            gatitos.gatoDormido(c, margen + 70, piso, 0.8, "gris", tags=("decoracion",))
            gatitos.gatoHeroe(c, int(ancho * 0.36), piso, 0.75, "naranja", tags=("decoracion",))
            gatitos.gatoEstambre(c, int(ancho * 0.6), piso, 0.75, "negro", tags=("decoracion",))
            gatitos.gatoSentado(c, ancho - margen - 60, piso, 0.75, "crema", "felices", tags=("decoracion",))
        c.tag_lower("decoracion")

    def cargarImagenes(self):
        # Fondo de puntos y gatitos en PNG (si la carpeta esta vacia se dibujan los gatitos de gatitos.py)
        ruta = IMAGENES / "fondo_puntos.png"
        self.mosaico = tk.PhotoImage(file=str(ruta)) if ruta.exists() else None
        self.imagenesGatitos = []
        for archivo in sorted((IMAGENES / "gatitos").glob("*.png")):
            try:
                imagen = tk.PhotoImage(file=str(archivo))
            except tk.TclError:
                continue
            reduccion = -(-imagen.height() // ALTO_GATITO)  # division hacia arriba
            if reduccion > 1:
                imagen = imagen.subsample(reduccion, reduccion)
            self.imagenesGatitos.append(imagen)
        # Dos imagenes del gato tecleando (Imagenes/tamborilero/1.png y 2.png); si no estan se usa el dibujado
        self.cuadrosTeclado = []
        for nombre in ("1.png", "2.png"):
            ruta = IMAGENES / "tamborilero" / nombre
            if ruta.exists():
                self.cuadrosTeclado.append(tk.PhotoImage(file=str(ruta)))
        if len(self.cuadrosTeclado) < 2:
            self.cuadrosTeclado = []

    def ubicarGato(self, evento):
        x, y = evento.width // 2, 42
        if self.gato is None and self.cuadrosTeclado:
            self.gato = gatitos.GatoTecladoImagenes(self.lienzoGato, x, 40, self.cuadrosTeclado)
        elif self.gato is None:
            self.gato = gatitos.GatoTamborilero(self.lienzoGato, x, y, 0.8, "crema")
        else:
            self.gato.x = x
            self.gato.dibujar("felices" if not self.errores else "preocupados")

    # Acciones de los botones
    def abrirArchivo(self):
        ruta = filedialog.askopenfilename(initialdir=EJEMPLOS, filetypes=[("Código Rust", "*.rs"), ("Todos", "*.*")])
        if ruta:
            self.cargar(Path(ruta))

    def mostrarEjemplos(self):
        menu = tk.Menu(self, tearoff=0, font=self.fuentes["normal"])
        for archivo in sorted(EJEMPLOS.glob("*.rs")):
            menu.add_command(label=archivo.name, command=lambda a=archivo: self.cargar(a))
        x = self.botonEjemplos.winfo_rootx()
        y = self.botonEjemplos.winfo_rooty() + self.botonEjemplos.winfo_height()
        menu.tk_popup(x, y)

    def mostrarModos(self):
        # Desplegable del boton de analisis: solo cambia el modo, el analisis se ejecuta con el boton
        menu = tk.Menu(self, tearoff=0, font=self.fuentes["normal"])
        for clave, nombre in MODOS.items():
            menu.add_radiobutton(label=nombre, variable=self.varModo, value=clave,
                                 command=self.actualizarBotonAnalizar)
        x = self.botonAnalizar.winfo_rootx()
        y = self.botonAnalizar.winfo_rooty() + self.botonAnalizar.winfo_height()
        menu.tk_popup(x, y)

    def actualizarBotonAnalizar(self):
        self.botonAnalizar.configure(text=f"▶ {MODOS[self.varModo.get()]}")

    def cargar(self, ruta):
        # Solo muestra el codigo en el editor; el analisis lo decide el usuario con el boton de analisis
        self.reiniciarResultados()
        self.editor.poner(ruta.read_text(encoding="utf-8"))
        self.archivo = ruta.name
        self.tarjetaEditor.titulo.configure(text=f"1. Editor de código · {self.archivo}")

    def crearTabla(self, padre, nombre, columnas, anchos):
        marco = tk.Frame(padre, bg=TARJETA)
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", selectmode="browse")
        for columna, ancho in zip(columnas, anchos):
            tabla.heading(columna, text=columna, anchor="w")
            tabla.column(columna, width=ancho, anchor="w")
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=6)
        barra.pack(side="right", fill="y")
        self.vistas[nombre] = marco
        return tabla

    def corrio(self, categoria):
        # True si el ultimo analisis incluyo esa categoria (antes de analizar nada se considera que si)
        return not self.analizado or categoria in ANALIZA[self.modoAnalizado]

    def cambiarVista(self, nombre):
        self.vista = nombre
        for clave, marco in self.vistas.items():
            if clave == nombre:
                marco.pack(fill="both", expand=True)
            else:
                marco.pack_forget()
        # Si el modo no genera esa vista se muestra "—" en lugar de 0 para no dar a entender que no hay nada
        cantidades = {
            "Símbolos": len(self.tabla.get_children()) if self.corrio("Semántico") else "—",
            "Tokens": len(self.tablaTokens.get_children()) if self.corrio("Léxico") else "—",
        }
        for clave, boton in self.botonesVista.items():
            activo = clave == nombre
            boton.configure(text=f"{clave} · {cantidades[clave]}", bg=ACENTO if activo else TARJETA,
                            fg=ACENTO_TEXTO if activo else TEXTO, activebackground=ACENTO,
                            highlightbackground=ACENTO if activo else BORDE)

    def reiniciarResultados(self):
        # Borra los resultados del analisis anterior (errores, tablas, marcas) sin tocar el texto del editor
        self.errores = []
        self.analizado = False
        self.modoAnalizado = "completo"
        self.filtro = "Todos"
        self.editor.limpiarMarcas()
        self.tabla.delete(*self.tabla.get_children())
        self.tablaTokens.delete(*self.tablaTokens.get_children())
        self.avisoLogs.configure(text="")
        self.cambiarVista(self.vista)
        self.mostrarDiagnostico()
        if self.gato is not None:
            self.gato.dibujar("abiertos")

    def limpiar(self):
        self.editor.poner("")
        self.archivo = "programa.rs"
        self.tarjetaEditor.titulo.configure(text="1. Editor de código · programa.rs")
        self.reiniciarResultados()

    def analizarCodigo(self):
        codigo = self.editor.obtener()
        if not codigo.strip():
            self.limpiar()
            return
        modo = self.varModo.get()
        self.analizado = True
        self.modoAnalizado = modo
        if self.filtro != "Todos" and self.filtro not in ANALIZA[modo]:
            self.filtro = "Todos"
        try:
            self.errores, simbolos, textoLogs, filasTokens = analizar(codigo, modo)
            self.avisoLogs.configure(text=textoLogs)
        except Exception as error:
            self.errores, simbolos, filasTokens = [{"categoria": "Sintáctico", "linea": None, "columna": None,
                                                    "mensaje": f"no se pudo completar el análisis ({error})",
                                                    "fragmento": ""}], [], []
        self.editor.marcarErrores(self.errores)
        self.tabla.delete(*self.tabla.get_children())
        for fila in simbolos:
            self.tabla.insert("", "end", values=fila)
        self.tablaTokens.delete(*self.tablaTokens.get_children())
        for fila in filasTokens:
            self.tablaTokens.insert("", "end", values=fila)
        self.cambiarVista(self.vista)
        self.mostrarDiagnostico()
        if self.gato is not None:
            self.gato.golpear(alTerminar=lambda: self.gato.reaccionar(bool(self.errores)))

    # Panel de diagnostico
    def mostrarDiagnostico(self):
        total = len(self.errores)
        if not self.analizado:
            self.contador.configure(text="sin analizar", bg=CODIGO_FONDO, fg=TEXTO_SUAVE)
        elif total:
            self.contador.configure(text=f"{total} error" + ("es" if total != 1 else ""), bg=ROJO_SUAVE, fg=ROJO)
        else:
            self.contador.configure(text="sin errores", bg=ACENTO, fg=ACENTO_TEXTO)

        for hijo in self.filtros.winfo_children():
            hijo.destroy()
        for nombre in ("Todos", "Léxico", "Sintáctico", "Semántico"):
            # Una categoria que el modo no ejecuto se muestra con "—" y deshabilitada, no con 0
            omitido = nombre != "Todos" and not self.corrio(nombre)
            cantidad = total if nombre == "Todos" else sum(1 for e in self.errores if e["categoria"] == nombre)
            activo = nombre == self.filtro
            tk.Button(self.filtros, text=f"{nombre} · {'—' if omitido else cantidad}",
                      command=lambda n=nombre: self.cambiarFiltro(n),
                      state="disabled" if omitido else "normal", disabledforeground=TEXTO_SUAVE,
                      bg=ACENTO if activo else TARJETA, fg=ACENTO_TEXTO if activo else TEXTO,
                      activebackground=ACENTO, relief="flat", font=self.fuentes["normal"], padx=10, pady=4,
                      cursor="arrow" if omitido else "hand2", highlightthickness=1,
                      highlightbackground=ACENTO if activo else BORDE, borderwidth=0).pack(side="left", padx=(0, 6))

        self.lista.vaciar()
        visibles = [e for e in self.errores if self.filtro == "Todos" or e["categoria"] == self.filtro]
        if not visibles:
            dibujo = tk.Canvas(self.lista.interior, width=260, height=130, bg=TARJETA, highlightthickness=0)
            dibujo.pack(pady=(24, 4))
            gatitos.gatoSentado(dibujo, 130, 122, 0.95, "crema", "felices" if self.analizado else "abiertos")
            if not self.analizado:
                texto = "Escribe tu código o abre uno desde Algoritmos,\ny luego presiona el botón de análisis."
            elif total:
                texto = "No hay errores en esta categoría."
            elif self.modoAnalizado == "completo":
                texto = "¡Todo en orden! El código no tiene errores."
            else:
                texto = f"Sin errores en el análisis\n({MODOS[self.modoAnalizado].lower()})."
            tk.Label(self.lista.interior, text=texto, justify="center",
                     bg=TARJETA, fg=TEXTO_SUAVE, font=self.fuentes["normal"]).pack(pady=(0, 12))
        for error in visibles:
            self.tarjetaError(error)

    def cambiarFiltro(self, nombre):
        self.filtro = nombre
        self.mostrarDiagnostico()

    def tarjetaError(self, error):
        colores = CATEGORIAS[error["categoria"]]
        tarjeta = tk.Frame(self.lista.interior, bg=TARJETA, highlightbackground=BORDE, highlightthickness=1,
                           cursor="hand2")
        tarjeta.pack(fill="x", pady=(0, 10), padx=(0, 6))

        fila = tk.Frame(tarjeta, bg=TARJETA)
        fila.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(fila, text=error["categoria"].upper(), bg=colores["fondo"], fg=colores["texto"],
                 font=self.fuentes["chip"], padx=8, pady=1).pack(side="left")
        if error["linea"]:
            tk.Label(fila, text=f"LÍNEA {error['linea']}", bg=TARJETA, fg=TEXTO,
                     font=self.fuentes["chip"]).pack(side="right")

        mensaje = tk.Label(tarjeta, text=error["mensaje"], bg=TARJETA, fg=TEXTO, font=self.fuentes["normal"],
                           justify="left", anchor="w")
        mensaje.pack(fill="x", padx=12)
        tarjeta.bind("<Configure>", lambda e, m=mensaje: m.configure(wraplength=max(e.width - 30, 100)))

        piezas = [tarjeta, fila, mensaje]
        if error["fragmento"]:
            codigo = tk.Label(tarjeta, text=error["fragmento"], bg=CODIGO_FONDO, fg=TEXTO,
                              font=self.fuentes["codigo_pequeno"], anchor="w", padx=8, pady=5)
            codigo.pack(fill="x", padx=12, pady=(6, 10))
            piezas.append(codigo)
        else:
            tk.Frame(tarjeta, bg=TARJETA, height=8).pack()

        if error["linea"]:
            for pieza in piezas + fila.winfo_children():
                pieza.bind("<Button-1>", lambda e, l=error["linea"]: self.editor.irALinea(l))

    def alElegirFila(self, tabla, posicionLinea):
        seleccion = tabla.selection()
        if seleccion:
            linea = tabla.item(seleccion[0], "values")[posicionLinea]
            if str(linea).isdigit():
                self.editor.irALinea(int(linea))


if __name__ == "__main__":
    Interfaz().mainloop()