const MAX_INTENTOS: u32 = 3;
const _LIMITE_2: i32 = 10;

fn calcular_total(valor_a: i32, valor_b: i32, _ignorado: i32) -> i32 {
    let suma = valor_a + valor_b;
    let producto = (valor_a * valor_b) - suma;
    producto
}

fn main() {
    let mut contador = 0;
    let edad_1: i32 = 20;
    let _privada = 5;
    let r#match = 10;
    let r#loop = r#match + 1;
    let r#for = [1, 2, 3];
    let tupla = (edad_1, r#loop);
    let _ = calcular_total(edad_1, r#loop, 0);
}
