// algoritmo_Leiner_sintactico_errores.rs
// Casos con errores sintacticos de la parte de Leiner. Entre cada error hay sentencias validas

// Error 1: struct con un campo sin dos puntos
struct CampoSinDosPuntos { nombre String }
const SEPARADOR_01: i32 = 1;
const SEPARADOR_02: i32 = 2;

// Error 2: struct con un campo sin tipo
struct CampoSinTipo { nombre: }
const SEPARADOR_03: i32 = 3;
const SEPARADOR_04: i32 = 4;

// Error 3: enum con variantes sin coma
enum VariantesSinComa { Norte Sur }
const SEPARADOR_05: i32 = 5;
const SEPARADOR_06: i32 = 6;

// Error 4: enum con una variante numerica
enum VarianteNumerica { 5 }
const SEPARADOR_07: i32 = 7;
const SEPARADOR_08: i32 = 8;

// Error 5: funcion sin parentesis
fn sin_parentesis { let valor = 1; }
const SEPARADOR_09: i32 = 9;
const SEPARADOR_10: i32 = 10;

// Error 6: parametro sin tipo
fn parametro_sin_tipo(a) { let valor = 1; }
const SEPARADOR_11: i32 = 11;
const SEPARADOR_12: i32 = 12;

fn main() {
    let mut contador = 0;
    let mut entrada = String::new();

    // Error 7: let sin valor
    let sin_valor = ;
    contador = contador + 1;
    contador = contador + 1;

    // Error 8: let sin nombre
    let : i32 = 4;
    contador = contador + 1;
    contador = contador + 1;

    // Error 9: const sin tipo
    const SIN_TIPO = 10;
    contador = contador + 1;
    contador = contador + 1;

    // Error 10: const sin valor
    const SIN_VALOR: i32;
    contador = contador + 1;
    contador = contador + 1;

    // Error 11: mut antes de let
    mut let invertido = 1;
    contador = contador + 1;
    contador = contador + 1;

    // Error 12: argumentos sin coma
    mostrar(1 2);
    contador = contador + 1;
    contador = contador + 1;

    // Error 13: loop sin bloque
    loop;
    contador = contador + 1;
    contador = contador + 1;

    // Error 14: instancia de struct con un campo sin dos puntos
    let persona = Persona { edad 20 };
    contador = contador + 1;
    contador = contador + 1;

    // Error 15: println sin el signo de admiracion
    println("Hola");
    contador = contador + 1;
    contador = contador + 1;

    // Error 16: println sin cadena de formato
    println!(contador);
    contador = contador + 1;
    contador = contador + 1;

    // Error 17: println con una coma sin argumentos
    println!("{}",);
    contador = contador + 1;
    contador = contador + 1;

    // Error 18: String con un metodo distinto de new
    let texto = String::nuevo();
    contador = contador + 1;
    contador = contador + 1;

    // Error 19: entrada con un modulo distinto de io
    std::fs::stdin().read_line(&mut entrada).expect("Modulo incorrecto");
    contador = contador + 1;
    contador = contador + 1;

    // Error 20: read_line sin mut
    std::io::stdin().read_line(&entrada).expect("Falta mut");
    contador = contador + 1;
    contador = contador + 1;

    // Error 21: entrada sin expect
    std::io::stdin().read_line(&mut entrada);
    contador = contador + 1;
    contador = contador + 1;

    // Error 22: referencia sin valor
    let referencia = &;
    contador = contador + 1;
    contador = contador + 1;
}

// Error 23: bloque sin llave de cierre
fn sin_llave_de_cierre() {
    let ultimo = 1;
