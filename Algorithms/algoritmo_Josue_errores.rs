
fn main() {
    
    let bin_invalido: u8 = 0b1012_0101;
    let bin_vacio: u8 = 0b_;
    let oct_invalido: u32 = 0o7789;
    let hex_invalido: u64 = 0x1A_G5_FF;
    let hex_vacio: u32 = 0x;
    let sufijo_entero_mal: i32 = 1_500i99;

    
    let float_exp_vacio: f64 = 3.1416e;
    let float_exp_signo_vacio: f64 = 1.0e-;
    let float_doble_punto: f32 = 12.34.56;
    let float_sufijo_mal: f64 = 2.5f128;

    
    let char_vacio: char = '';
    let char_multiple: char = 'ab';
    let char_escape_mal: char = '\q';
    let char_sin_cerrar: char = 'z;

    
    let byte_no_ascii: u8 = b'ñ';
    let byte_emoji: u8 = b'🚀';
    let byte_vacio: u8 = b'';
    let byte_multiple: u8 = b'XY';
    let byte_hex_incompleto: u8 = b'\x4';

    
    let raw_hash_desigual_1: &str = r#"Texto con cierre extra"##;
    let raw_hash_desigual_2: &str = r###"Texto con cierre menor"##;
    let raw_sin_comilla_apertura: &str = r##Texto sin comillas##;


    let str_escape_invalido: &str = "Ruta invalida: \k\archivo";
    let str_sin_cerrar: &str = "Esta cadena queda abierta sin comilla final;
}