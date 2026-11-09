// algoritmo_Leiner_sintactico.rs

const LIMITE: u32 = 6;
const BASE: u64 = 1;
const PORCENTAJE_TOTAL: f64 = 50.0 * 2.0;

struct Resumen {
    procesados: u32,
    pares: u32,
    impares: u32,
}

enum Estado {
    Calculando,
    Terminado,
}

fn mostrar_titulo() {
    println!("Tabla de factoriales");
}

fn saludar(nombre: &String) {
    println!("Hola, {}", nombre);
}

fn mostrar_fila(numero: u32, resultado: u64) {
    println!("{}! = {}", numero, resultado);
}

fn calcular_factorial(numero: u32) {
    let mut acumulado: u64 = BASE;
    let mut factor: u32 = 1;

    loop {
        if factor > numero {
            break;
        }
        acumulado = acumulado * factor as u64;
        factor = factor + 1;
    }

    mostrar_fila(numero, acumulado);
}

fn mostrar_porcentaje(pares: u32, total: u32) {
    let porcentaje: f64 = pares as f64 * PORCENTAJE_TOTAL / total as f64;
    println!("Numeros pares: {} de {} ({}%)", pares, total, porcentaje);
}

fn main() {
    let mut nombre = String::new();
    let separador = "--------------------";

    println!("Ingrese su nombre:");
    std::io::stdin().read_line(&mut nombre).expect("No se pudo leer el nombre");
    saludar(&nombre);

    println!("{}", separador);
    mostrar_titulo();

    let mut actual: u32 = 1;
    let mut pares: u32 = 0;

    loop {
        if actual > LIMITE {
            break;
        }
        calcular_factorial(actual);
        if actual % 2 == 0 {
            pares = pares + 1;
        }
        actual = actual + 1;
    }

    let impares: u32;
    impares = LIMITE - pares;

    let resumen = Resumen { procesados: LIMITE, pares: pares, impares: impares };
    let r#final = actual - 1;

    println!("{}", separador);
    mostrar_porcentaje(pares, LIMITE);
    println!("Numeros impares: {}", impares);
    println!("Ultimo numero procesado: {}", r#final);
}
