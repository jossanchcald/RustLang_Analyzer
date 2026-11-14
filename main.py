import sys
from datetime import datetime
from pathlib import Path
from Analyzers.lexical import lexer as lexicalAnalyzer
from Analyzers.lexical import lexicalErrors, checkUnclosedComments, findColumn
from Analyzers.syntactic import parser, syntacticErrors
from Analyzers.semantic import reiniciarSemantica, listaErroresSemanticos

actualRoute = Path(__file__).resolve().parent
logFolder = actualRoute / "Logs"

def readFile(rustFile):
    try:
        with open(rustFile + '.rs', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"\nError: el archivo '{rustFile}.rs' no existe. Intente nuevamente.")
        return None

def createLogFile(userName, content, prefix="lexico", dateFormat='%d-%m-%Y-%Hh%M'):
    now = datetime.now()
    logFolder.mkdir(parents=True, exist_ok=True)

    logfName = f"{prefix}-{userName}-{now.strftime(dateFormat)}.txt"
    with open(logFolder / logfName, 'w', encoding='utf-8') as logFile:
        logFile.write(content)

#TODO en pruebas
def analyzeRustAlgo(rustFile, userName):

    #ANALIZADOR LEXICO 
    lexicalErrors.clear()  # Limpia errores previos por si se hacen varias pruebas
    lexicalAnalyzer.input(rustFile)
    
    tokens_procesados = ["[[[[[ TOKENS RECONOCIDOS ]]]]]"]
    for tok in lexicalAnalyzer:
        column = findColumn(lexicalAnalyzer.lexdata, tok.lexpos)
        tokens_procesados.append(f"[{tok.type}] -> {tok.value} (Línea {tok.lineno}, Columna {column})")
        
    checkUnclosedComments()  # Comentarios de bloque sin cerrar

    if lexicalErrors:
        tokens_procesados.append("\n [[[[[ ERRORES LÉXICOS ]]]]]")
        for err in lexicalErrors:
            tokens_procesados.append(err["mensaje"] if "mensaje" in err else str(err))

    createLogFile(userName, "\n".join(tokens_procesados))

    # ANALIZADOR SINTACTICO
    syntacticErrors.clear()

    reiniciarSemantica()  # el analisis semantico ocurre mientras el parser reconoce las reglas, por lo tanto se limpian la tabla de simbolos y los errores antes de empezar
    lexicalAnalyzer.lineno = 1
    parser.parse(rustFile, lexer=lexicalAnalyzer, tracking=True)

    erroresSintacticos = ["[[[[[ ERRORES SINTÁCTICOS ]]]]]"]
    erroresSintacticos += syntacticErrors if syntacticErrors else ["No se encontraron errores sintácticos."]
    createLogFile(userName, "\n".join(erroresSintacticos), prefix="sintactico")

    erroresSemanticos = ["[[[[[ ERRORES SEMÁNTICOS ]]]]]"]
    erroresSemanticos += listaErroresSemanticos() or ["No se encontraron errores semánticos."]
    createLogFile(userName, "\n".join(erroresSemanticos), prefix="semantico", dateFormat='%d%m%Y-%Hh%M')
    
    print(f"\nAnálisis completado. Revise la carpeta 'Logs'.")

def main():
    print("\nAnalizador léxico de algoritmos de lenguaje en Rust\n\n" \
    "Para poder utilizar el analizador: \n" \
    "\t> Identifiquese con un username o nombre.\n" \
    "\t> Ingrese el nombre del archivo Rust donde se encuentra el algoritmo a evaluar.\n" \
    "\t\tPD: Debe ser de extension '.rs', si el archivo se encuentra en la carpeta Algorithms ingrese 'Algorithms/NombreArchivo'\n")

    userName = input("Ingrese su nombre: ")
    userNameNoBS = "".join(userName.split())

    fileContent = None

    while (fileContent is None):  
        fileName = input("\n\nIngrese el nombre del archivo Rust (.rs): ").strip()
        if (fileName is None):
            continue

        rustfName = fileName.removesuffix('.rs')
        fileContent = readFile(rustfName)

    analyzeRustAlgo(fileContent, userNameNoBS)



if __name__ == '__main__':
    main()