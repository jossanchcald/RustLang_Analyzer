const MAX: u32 = 10;
const PI: f64 = 3.14159;
const SALUDO: &str = "Hola";
const ACTIVO: bool = true;

struct Persona {
    nombre: String,
    edad: u32,
    altura: f64,
    activo: bool,
}

fn saludar() {
    println!("Hola");
}

fn sumar(a: i32, b: i32) -> i32 {
    a + b
}

fn promedio(a: f64, b: f64) -> f64 {
    (a + b) / 2.0
}

fn es_mayor(edad: i32) -> bool {
    edad >= 18
}

fn obtener_saludo() -> String {
    String::from("Hola")
}

fn longitud(texto: &str) -> usize {
    texto.len()
}

fn maximo(a: i32, b: i32) -> i32 {
    if a > b {
        return a;
    } else {
        return b;
    }
}


// ASIGNACION DE TIPO - reglas 1, 2, 3
fn prueba_asignacion_tipo() {
    // Regla 1: el valor coincide con el tipo declarado
    let edad: i32 = 25;
    let precio: f64 = 19.99;
    let letra: char = 'a';
    let activo: bool = true;
    let saludo: &str = "hola";
    let nombre: String = String::from("Ana");
    let inferido = 100;
    let inferido_dec = 2.5;

    // Regla 1: reasignaciones con el mismo tipo (solo con mut)
    let mut contador: i32 = 0;
    contador = 10;
    contador += 5;
    contador -= 2;
    contador *= 3;
    contador /= 2;
    contador %= 4;
    let mut total: f64 = 1.5;
    total = 2.5;
    let mut mensaje: String = String::from("Hola");
    mensaje = String::from("Adios");
    mensaje += " mundo";

    // Regla 2: las constantes solo se leen
    let limite: u32 = MAX;
    let radio: f64 = PI;
    let texto_const: &str = SALUDO;
    let bandera_const: bool = ACTIVO;

    // Regla 3: primera asignacion de una variable declarada sin valor
    let tardia: i32;
    tardia = 42;
    let mut tardia_mut: i32;
    tardia_mut = 1;
    tardia_mut = 2;
    let etiqueta: i32;
    if edad > 18 {
        etiqueta = 1;
    } else {
        etiqueta = 2;
    }

    println!("{}", edad);
    println!("{}", contador);
    println!("{}", etiqueta);
    println!("{}", tardia);
}

// ASIGNACION DE TIPO - regla 5 (retorno de llamada vs variable)
fn prueba_retorno_llamada() {
    let suma: i32 = sumar(2, 3);
    let media: f64 = promedio(4.0, 6.0);
    let adulto: bool = es_mayor(20);
    let saludo_fn: String = obtener_saludo();
    let tam: usize = longitud("hola");
    let mayor: i32 = maximo(3, 7);
    let sin_tipo = sumar(1, 1);
    saludar();
}


// ASIGNACION DE TIPO - regla 6 (campos de struct)
fn prueba_structs() {
    let p1 = Persona { nombre: String::from("Carlos"), edad: 20, altura: 1.75, activo: true };
    let p2 = Persona { nombre: String::from("Lucia"), edad: 31, altura: 1.62, activo: false };
}


// OPERACIONES PERMITIDAS - reglas 1 a 6
fn prueba_operaciones() {
    // Regla 1: aritmetica entre tipos numericos iguales
    let suma_lit = 5 + 3;
    let suma_dec = 5.0 + 2.5;
    let num_a: i32 = 10;
    let num_b: i32 = 4;
    let resta = num_a - num_b;
    let producto = num_a * num_b;
    let division = num_a / num_b;
    let residuo = num_a % num_b;
    let dec_a: f64 = 2.5;
    let dec_b: f64 = 1.5;
    let producto_dec = dec_a * dec_b;
    let con_literal = num_a + 1;
    let compuesta = (num_a + num_b) * 2 - 1;

    // Regla 2: concatenacion String + &str
    let hola = String::from("Hola ") + "mundo";
    let nombre = String::from("Ana");
    let completo = String::from("Hola ") + &nombre;
    let exclamacion = hola + "!";
    let num_texto = num_a.to_string();
    let unido = num_texto + "x";

    // Regla 3: && y || con operandos bool
    let y1 = true && false;
    let y2 = (5 > 3) || (2 > 1);
    let y3 = num_a > 1 && num_b < 100;
    let y4 = !y1;

    // Regla 4: comparaciones entre tipos compatibles
    let nombre_otro = String::from("Luis");
    let c1 = 5 < 10;
    let c2 = num_a == num_b;
    let c3 = "a" == "b";
    let c4 = 'a' < 'b';
    let c5 = 2.5 >= 1.5;
    let c6 = true != false;
    let c7 = nombre == nombre_otro;

    // Regla 5: negacion unaria sobre numericos con signo o flotantes
    let n1 = -5;
    let n2 = -2.5;
    let con_signo: i32 = 15;
    let n3 = -con_signo;
    let con_dec: f64 = 1.5;
    let n4 = -con_dec;
    let n5 = -(3 + 4);

    // Regla 6: indexar arreglos / vectores con entero sin signo
    let numeros = [10, 20, 30];
    let lista = vec![1, 2, 3];
    let idx: usize = 2;
    let i1 = numeros[0];
    let i2 = numeros[idx];
    let i3 = numeros[1 + 1];
    let i4 = lista[0];
    let i5 = numeros[idx - 1];
}

// CONTROL - regla 6 (for ... in sobre rango o coleccion)
fn prueba_control_for() {
    let numeros = [1, 2, 3];
    let lista = vec![4, 5, 6];
    let limite: usize = 3;
    let inicio: i32 = 1;
    let fin: i32 = 4;
    let mut suma_total: i32 = 0;

    for i in 0..5 {
        suma_total += i;
    }
    for i in 1..=3 {
        println!("{}", i);
    }
    for n in numeros {
        println!("{}", n);
    }
    for x in lista {
        println!("{}", x);
    }
    for _ in 0..2 {
        println!("repetir");
    }
    for k in 0..limite {
        println!("{}", k);
    }
    for j in inicio..fin {
        println!("{}", j);
    }
    for c in 'a'..='e' {
        println!("{}", c);
    }
}

fn main() {
    prueba_asignacion_tipo();
    prueba_retorno_llamada();
    prueba_structs();
    prueba_operaciones();
    prueba_control_for();
}