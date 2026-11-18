
struct Estudiante {
    nombre: String,
    edad: i32,
    promedio: f64,
}

fn calcular_promedio(nota1: i32, nota2: i32) -> i32 {
    let resultado: i32 = nota1 + nota2;
    return resultado;
}

fn main() {
    // =====================================
    // 1. DECLARACIONES DE VARIABLES
    // =====================================

    let edad: i32 = 20;
    let nombre: String = String::from("Josue");
    let activo: bool = true;
    let mut contador: i32 = 0;

    // ERROR SEMANTICO: tipos incompatibles
    let altura: i32 = 1.75;

    // ERROR SEMANTICO: variable no declarada
    println!("{}", estudiante);

    // ERROR SEMANTICO: modificacion de variable inmutable
    edad = 21;

    // ERROR LEXICO: literal numerico mal formado
    let numero = 0b102;

    // ERROR LEXICO: caracter no reconocido
    @

    // =====================================
    // 2. OPERACIONES Y CONDICIONALES
    // =====================================

    // ERROR SEMANTICO: operacion entre String e i32
    let suma = nombre + edad;

    // ERROR SEMANTICO: condicion debe ser bool
    if contador {
        println!("Contador activo");
    }

    // ERROR SINTACTICO: falta la condicion del if
    if {
        println!("Condicion incorrecta");
    }

    // =====================================
    // 3. CICLOS Y ARREGLOS
    // =====================================

    let numeros = [10, 20, 30, 40];

    // ERROR SEMANTICO: indice negativo
    let valor = numeros[-1];

    // ERROR SEMANTICO: rango decimal no iterable
    for i in 1.5..5.5 {
        println!("{}", i);
    }

    // ERROR SEMANTICO: break fuera de un ciclo
    break;

    // ERROR SEMANTICO: arreglo con tipos diferentes
    let datos = [10, 20, "treinta"];

    // =====================================
    // 4. FUNCIONES Y ASIGNACIONES
    // =====================================

    // ERROR SEMANTICO: argumento no declarado
    let resultado = calcular_promedio(10, calificacion);

    // ERROR SEMANTICO: operacion aritmetica invalida
    let division = activo / edad;

    // ERROR SEMANTICO: variable sin inicializar
    let mut puntos: i32;
    puntos += 10;

    // =====================================
    // 5. ESTRUCTURAS
    // =====================================

    let alumno = Estudiante {
        nombre: String::from("Carlos"),
        edad: 20,
        promedio: 9.5
    };

    // ERROR SEMANTICO: campo con tipo incorrecto
    let otro = Estudiante {
        nombre: String::from("Maria"),
        edad: "veinte",
        promedio: 8.5
    };

    // ERROR SINTACTICO: falta el punto y coma
    let mensaje = "Analisis de Rust"

    println!("Fin del programa");
}