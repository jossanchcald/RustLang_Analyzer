import sys
from datetime import datetime
from pathlib import Path
from Analyzers.lexical import lexer as lexicalAnalyzer
from Analyzers.lexical import lexicalErrors

actualRoute = Path(__file__).resolve().parent
logFolder = actualRoute / "Logs"

def readFile(rustFile):
    try:
        with open(rustFile + '.rs', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"\nError: el archivo '{rustFile}.rs' no existe.")
        sys.exit(1)

def createLogFile(userName, content):
    now = datetime.now()
    logFolder.mkdir(parents=True, exist_ok=True)

    logfName = f"lexico-{userName}-{now.strftime('%d-%m-%Y-%Hh%M')}.txt"
    with open(logFolder / logfName, 'w', encoding='utf-8') as logFile:
        logFile.write(content)

#TODO en pruebas
def analyzeRustAlgo(rustFile, userName):
    lexicalErrors.clear()  # Limpia errores previos por si se hacen varias pruebas
    lexicalAnalyzer.input(readFile(rustFile))
    
    tokens_procesados = ["[[[[[ TOKENS RECONOCIDOS ]]]]]"]
    for tok in lexicalAnalyzer:
        tokens_procesados.append(f"[{tok.type}] -> {tok.value} (Línea {tok.lineno})")
        
    if lexicalErrors:
        tokens_procesados.append("\n [[[[[ ERRORES LÉXICOS ]]]]]")
        for err in lexicalErrors:
            tokens_procesados.append(err["mensaje"] if "mensaje" in err else str(err))
            
    createLogFile(userName, "\n".join(tokens_procesados))
    print(f"\nAnálisis completado. Revise la carpeta 'Logs'.")

def main():
    print("\nAnalizador léxico de algoritmos de lenguaje en Rust\n\n" \
    "Para poder utilizar el analizador: \n" \
    "\t> Identifiquese con un username o nombre.\n" \
    "\t> Ingrese el nombre del archivo Rust donde se encuentra el algoritmo a evaluar.\n" \
    "\t\tPD: Debe ser de extension '.rs', si el archivo se encuentra en la carpeta Algorithms ingrese 'Algorithms/NombreArchivo'\n")

    userName = input("Ingrese su nombre: ")
    userNameNoBS = "".join(userName.split())

    fileName = input("\nIngrese el nombre del archivo Rust (.rs): ")
    rustfName = fileName.removesuffix('.rs')

    analyzeRustAlgo(rustfName, userNameNoBS)


if __name__ == '__main__':
    main()