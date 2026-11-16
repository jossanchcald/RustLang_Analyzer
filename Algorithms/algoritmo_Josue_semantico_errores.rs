const MAX: u32 = 10;
const PI: f64 = 3.14159;

struct Persona {
    nombre: String,
    edad: u32,
    altura: f64,
    activo: bool,
}

fn saludar() {
    println!("Hola");
}

fn obtener_numero() -> i32 {
    5
}

fn obtener_texto() -> String {
    String::from("hola")
}

// ASIGNACION DE TIPO - regla 1 (tipo del valor vs tipo de la variable)
fn prueba_asignacion_tipo() {
    //  tipos incompatibles en la declaración de 'edad', tipo esperado 'i32'
    let edad: i32 = "veinte";
    //  ... declaración de 'activo', tipo esperado 'bool'
    let activo: bool = 5;
    //  ... declaración de 'precio', tipo esperado 'f64'
    let precio: f64 = 10;
    //  ... declaración de 'cantidad', tipo esperado 'i32'
    let cantidad: i32 = 2.5;
    //  ... declaración de 'nombre', tipo esperado 'String'
    let nombre: String = "Ana";
    //  ... declaración de 'letra', tipo esperado 'char'
    let letra: char = "a";

    let mut contador: i32 = 0;
    //  tipos incompatibles en la asignación de 'contador', tipo esperado 'i32'
    contador = true;

    let mut total: i32 = 0;
    //  ... asignación de 'total', tipo esperado 'i32'
    total += "5";

    let mut nombre_m: String = String::from("Ana");
    //  ... asignación de 'nombre_m', tipo esperado 'String'
    nombre_m = 5;
}


// ASIGNACION DE TIPO - regla 2 (constantes no se pueden modificar)

fn prueba_constantes() {
    //  no se puede modificar la constante 'MAX'
    MAX = 20;
    //  no se puede modificar la constante 'PI'
    PI = 3.0;
    //  no se puede modificar la constante 'MAX'
    MAX += 1;
}


// ASIGNACION DE TIPO - regla 3 (solo se reasigna con mut)

fn prueba_inmutables() {
    let edad_fija = 20;
    //  no se puede modificar la variable inmutable 'edad_fija'
    edad_fija = 21;

    let saludo_fijo = String::from("Hola");
    //  no se puede modificar la variable inmutable 'saludo_fijo'
    saludo_fijo = String::from("Chao");

    let contador_fijo: i32 = 0;
    //  no se puede modificar la variable inmutable 'contador_fijo'
    contador_fijo += 1;

    let una_vez: i32;
    una_vez = 1;
    //  no se puede modificar la variable inmutable 'una_vez' (segunda asignacion)
    una_vez = 2;
}

// ASIGNACION DE TIPO - regla 5 (retorno de la llamada vs variable)

fn prueba_retorno_llamada() {
    //  la función 'saludar' devuelve el tipo unitario '()' y no puede asignarse a una variable de tipo 'i32'
    let resultado: i32 = saludar();
    //  ... unitario '()' ... de tipo 'String'
    let texto: String = saludar();
    //  ... unitario '()' ... de tipo 'bool'
    let bandera: bool = saludar();
    //  la función 'obtener_numero' devuelve el tipo 'i32' y no puede asignarse a una variable de tipo 'String'
    let palabra: String = obtener_numero();
    //  ... 'obtener_numero' devuelve el tipo 'i32' ... de tipo 'bool'
    let activo_fn: bool = obtener_numero();
    //  la función 'obtener_texto' devuelve el tipo 'String' ... de tipo 'i32'
    let numero_fn: i32 = obtener_texto();
    //  ... 'obtener_numero' devuelve el tipo 'i32' ... de tipo 'f64'
    let ret_dec: f64 = obtener_numero();
}


// ASIGNACION DE TIPO - regla 6 (campos de struct)

fn prueba_structs() {
    //  el campo 'edad' de la estructura 'Persona' espera un valor de tipo 'u32', pero se asignó '&str'
    let p1 = Persona { nombre: String::from("Carlos"), edad: "veinte", altura: 1.75, activo: true };
    //  el campo 'nombre' ... espera 'String', pero se asignó '&str'
    let p2 = Persona { nombre: "Carlos", edad: 20, altura: 1.75, activo: true };
    //  el campo 'altura' ... espera 'f64', pero se asignó '&str'
    let p3 = Persona { nombre: String::from("Ana"), edad: 20, altura: "alta", activo: true };
    //  el campo 'activo' ... espera 'bool', pero se asignó 'i32'
    let p4 = Persona { nombre: String::from("Ana"), edad: 20, altura: 1.75, activo: 5 };
    //  el campo 'edad' ... espera 'u32', pero se asignó 'f64'
    let p5 = Persona { nombre: String::from("Ana"), edad: 2.5, altura: 1.75, activo: true };
}


// OPERACIONES - regla 1 (aritmetica solo entre numericos iguales)

fn prueba_op_aritmeticas() {
    //  operación '+' inválida entre los tipos 'i32' y 'f64'
    let suma_mixta = 5 + 2.5;

    let entero_a: i32 = 4;
    let decimal_a: f64 = 2.5;
    //  operación '*' inválida entre los tipos 'i32' y 'f64'
    let producto_mixto = entero_a * decimal_a;
    //  operación '-' inválida entre los tipos 'i32' y 'f64'
    let resta_mixta = entero_a - 1.5;
    //  operación '-' inválida entre los tipos 'bool' y 'i32'
    let bool_menos = true - 1;

    let entero_i32: i32 = 1;
    let entero_i64: i64 = 2;
    //  operación '+' inválida entre los tipos 'i32' y 'i64'
    let suma_tipos = entero_i32 + entero_i64;
}


// OPERACIONES - regla 2 (concatenacion: String + &str)

fn prueba_op_concatenacion() {
    //  operación '+' inválida entre los tipos 'String' y 'i32'
    let texto = String::from("Hola ") + 32;
    //  operación '+' inválida entre los tipos '&str' y '&str'
    let dos_literales = "Hola " + "mundo";
    //  operación '+' inválida entre los tipos 'i32' y '&str'
    let entero_mas_texto = 5 + "x";
    //  operación '+' inválida entre los tipos 'String' y 'f64'
    let texto_mas_dec = String::from("a") + 2.5;
}


// OPERACIONES - regla 3 (&& y || solo con bool)

fn prueba_op_logicas() {
    //  el operador '&&' requiere operandos bool; se encontró un valor entero
    let r1 = true && 5;
    //  el operador '||' requiere operandos bool; se encontró un valor entero
    let r2 = 1 || false;
    //  el operador '&&' requiere operandos bool; se encontró un valor cadena
    let r3 = "a" && true;
    //  el operador '&&' requiere operandos bool; se encontró un valor cadena
    let r4 = true && "x";
    //  el operador '||' requiere operandos bool; se encontró un valor decimal
    let r5 = 2.5 || true;
}


// OPERACIONES - regla 4 (comparaciones entre tipos compatibles)

fn prueba_op_comparaciones() {
    let edad = 20;
    //  no se puede comparar un entero con una cadena mediante el operador '<'
    let c1 = edad < "18";
    //  no se puede comparar un entero con un booleano mediante el operador '=='
    let c2 = 5 == true;
    //  no se puede comparar una cadena con un entero mediante el operador '>'
    let c3 = "a" > 1;
    //  no se puede comparar un decimal con un carácter mediante el operador '<'
    let c4 = 2.5 < 'c';

    let ent_a: i32 = 1;
    let ent_b: i64 = 2;
    //  no se puede comparar un valor de tipo 'i32' con un valor de tipo 'i64' mediante el operador '<'
    let c5 = ent_a < ent_b;

    let fa: f32 = 1.5;
    let fb: f64 = 2.5;
    //  no se puede comparar un valor de tipo 'f32' con un valor de tipo 'f64' mediante el operador '=='
    let c6 = fa == fb;
}

// OPERACIONES - regla 5 (negacion unaria solo con signo / flotantes)

fn prueba_op_negacion() {
    let cantidad: u32 = 15;
    //  no se puede aplicar el operador unario '-' a un valor sin signo de tipo 'u32'
    let negativo = -cantidad;

    let byte_val: u8 = 5;
    //  ... valor sin signo de tipo 'u8'
    let neg_byte = -byte_val;

    let activo_neg = true;
    //  no se puede aplicar el operador unario '-' a un valor de tipo 'bool'
    let neg_bool = -activo_neg;
    //  ... a un valor de tipo '&str'
    let neg_cad = -"hola";
    //  ... a un valor de tipo 'char'
    let neg_char = -'a';
}


// OPERACIONES - regla 6 (indexacion: base y tipo del indice)

fn prueba_op_indices() {
    let numeros = [10, 20, 30];
    //  los índices de un arreglo deben ser de tipo entero sin signo ('usize'); se encontró '&str'
    let valor = numeros["0"];
    //  ... se encontró 'f64'
    let v_dec = numeros[1.5];
    //  ... se encontró 'bool'
    let v_bool = numeros[true];
    //  ... se encontró un valor negativo
    let v_neg = numeros[-1];

    let idx_i32: i32 = 1;
    //  ... se encontró 'i32'
    let v_i32 = numeros[idx_i32];
    let idx_u32: u32 = 1;
    //  ... se encontró 'u32' (en Rust solo se indexa con usize)
    let v_u32 = numeros[idx_u32];

    let numero_simple = 5;
    //  solo se permite acceder por índice a arreglos o vectores; se encontró un valor de tipo 'i32'
    let x1 = numero_simple[0];
    let cadena = "hola";
    //  ... se encontró un valor de tipo '&str'
    let x2 = cadena[0];
    let verdadero = true;
    //  ... se encontró un valor de tipo 'bool'
    let x3 = verdadero[0];

    let vector = vec![1, 2, 3];
    //  los índices de un arreglo deben ser de tipo entero sin signo ('usize'); se encontró 'f64'
    let x4 = vector[2.0];
}


// CONTROL - regla 6 (for ... in requiere rango o coleccion iterable)
// Mensaje esperado en todos: el 'for' requiere un rango o una estructura iterable

fn prueba_control_for() {
    let n: i32 = 5;
    
    for i in n {
        println!("{}", i);
    }

    let flag_for = true;
    
    for i in flag_for {
        println!("{}", i);
    }

    
    for i in 2.5 {
        println!("{}", i);
    }

    
    for c in "abc" {
        println!("{}", c);
    }

    // ERROR: rango con flotantes
    for i in 0.0..1.0 {
        println!("{}", i);
    }

    // ERROR: extremo del rango bool
    for i in 0..true {
        println!("{}", i);
    }

    let tupla = (1, 2);
    // ERROR: tupla no es iterable
    for t in tupla {
        println!("{}", t);
    }
}

fn main() {
    prueba_asignacion_tipo();
    prueba_constantes();
    prueba_inmutables();
    prueba_retorno_llamada();
    prueba_structs();
    prueba_op_aritmeticas();
    prueba_op_concatenacion();
    prueba_op_logicas();
    prueba_op_comparaciones();
    prueba_op_negacion();
    prueba_op_indices();
    prueba_control_for();
}