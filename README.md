# Analizador de Rust

Proyecto de Lenguajes de Programación: analizador **léxico**, **sintáctico** y **semántico** para un subconjunto del lenguaje Rust, con interfaz gráfica.

**Integrantes:** Josue Sanchez Calderon · Jared Selim Beltran Martinez · Leiner David Saltos Peñafiel

## Requisitos

- **Python 3.9 o superior** (probado con Python 3.14)
- **tkinter**, para la interfaz gráfica. Viene incluido con Python. En Linux, si falta: `sudo apt install python3-tk`
- Bibliotecas externas (están en `requirements.txt`):

| Biblioteca | Versión | Uso |
|---|---|---|
| `ply` | 3.11 | Generación del analizador léxico (`lex`) y sintáctico (`yacc`) |
| `regex` | 2026.9.29 | Expresiones regulares del analizador léxico |

## Instalación

**1. Python.** Verifica que se lo tiene con `python3 --version` (en Windows: `python --version`). Si no, descárguelo de [python.org](https://www.python.org/downloads/) (en Windows, marca la opción *Add Python to PATH* al instalar).

**2. Entorno virtual y bibliotecas.** Desde la carpeta del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Si no tienes el `requirements.txt`**, instale las bibliotecas a mano (con el entorno virtual activado):

```bash
pip install ply==3.11 regex==2026.9.29
```

**3. Comprobar la instalación:**

```bash
python3 -c "import ply, regex, tkinter; print('Todo listo')"
```

Si dice `No module named 'tkinter'`, instálelo según su sistema:

| Sistema | Comando |
|---|---|
| Linux (Debian/Ubuntu) | `sudo apt install python3-tk` |
| macOS con Homebrew | `brew install python-tk` |
| Windows / macOS con python.org | Ya viene incluido. Si falta, reinstale Python y deje marcada la opción *tcl/tk* |

## Ejecución

**Interfaz gráfica** (recomendado):

```bash
python3 interfaz.py
```

1. Escribe o pega código Rust en el editor, o abre uno con **Abrir archivo** / **Algoritmos**.
2. Presiona **▶ Analizar código**.
3. Los errores léxicos, sintácticos y semánticos aparecen en el panel *Diagnóstico* con su número de línea. Al hacer clic en uno, el editor salta a esa línea.
4. La tabla inferior muestra la **tabla de símbolos** y la lista de **tokens** reconocidos.

**Versión por consola:**

```bash
python3 main.py
```

Pide un nombre de usuario y el archivo `.rs` a analizar (por ejemplo `Algorithms/NombreArchivo`, sin la extensión).

## Estructura

```
Analyzers/
    lexical.py       Analizador léxico
    syntactic.py     Analizador sintáctico
    semantic.py      Tabla de símbolos y reglas semánticas
interfaz.py          Interfaz gráfica
gatitos.py           Dibujos de la interfaz
main.py              Versión por consola
Algorithms/          Algoritmos de prueba (.rs) de cada integrante
Imagenes/            Imágenes de la interfaz
Logs/                Logs generados por los analizadores
requirements.txt     Bibliotecas necesarias
```

## Logs

Cada análisis guarda un log por analizador en la carpeta `Logs/`, con el prefijo `lexico-`, `sintactico-` o `semantico-`, seguido del nombre de usuario y la fecha y hora.