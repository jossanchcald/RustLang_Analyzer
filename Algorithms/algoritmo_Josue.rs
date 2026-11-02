
struct SensorConfig {
    id: u32,
    nombre: String,
    activo: bool,
}

enum EstadoSensor {
    Operativo,
    EnMantenimiento,
    Critico,
}

fn main() {
    
    let temp_min: i8 = -10i8;
    let temp_ambiente: i16 = 25_i16;
    let presion_base: i32 = 101_325i32;
    let delta_tiempo: i64 = -5_000_000_i64;
    let acumulado_energia: i128 = 9_000_000_000_000i128;
    let offset_memoria: isize = -64_isize;

    
    let registro_estado: u8 = 0b1010_1100u8;
    let mascara_red: u16 = 0xFF_00_u16;
    let permisos_unix: u32 = 0o755_u32;
    let direccion_mac: u64 = 0x00_1A_2B_3C_4D_5Eu64;
    let contador_ciclos: u128 = 1_844_674_407_370_955u128;
    let indice_buffer: usize = 0b1111_0000_usize;

    
    let dec_simple = 42;
    let dec_sep = 1_000_000;
    let hex_simple = 0xdead_beef;
    let oct_simple = 0o77_44;
    let bin_simple = 0b1100_0011;

    
    let pi_aprox: f32 = 3.14159_f32;
    let constante_planck: f64 = 6.626e-34;
    let velocidad_luz: f64 = 2.998E+8_f64;
    let factor_calibracion: f64 = 1_234.567_89;
    let tolerancia = 0.000_1f32;

    
    let sistema_encendido: bool = true;
    let alerta_sobrecalentamiento: bool = false;

    
    let unidad_temp: char = 'C';
    let caracter_enie: char = 'ñ';
    let salto_linea: char = '\n';
    let tabulador: char = '\t';
    let icono_estado: char = '🚀';

    
    let byte_inicio: u8 = b'A';
    let byte_fin: u8 = b'Z';
    let byte_salto: u8 = b'\n';
    let byte_hex: u8 = b'\x7F';

    
    let mensaje_inicio: &str = "Iniciando sistema de telemetria...";
    let ruta_logs: &str = r"C:\sensores\logs\telemetria_2026.log";
    let consulta_json: &str = r#"{"sensor": "Temp_01", "unidad": "Celsius"}"#;
    let plantilla_xml: &str = r###"<config version="1.0">Valor "#1" activado</config>"###;
    let etiqueta_nodo: String = String::from("Nodo-Guayaquil-01");
    let respaldo_txt: String = "Respaldo automatico completado".to_string();

    
    let lecturas_recientes: [i32; 4] = [10, 20, 30, 40];
    let resumen_nodo: (&str, i32, f64, bool) = ("Sensor_A", 100, 99.5, true);
    let historial_alertas: Vec<i32> = vec![1, 2, 3];
    let valor_opcional: Option<i32> = Some(42);
    let valor_vacio: Option<i32> = None;
    let resultado_op: Result<i32, &str> = Ok(200);
    let error_op: Result<i32, &str> = Err("Timeout");

    
    let mut promedio_lecturas: i32 = (lecturas_recientes[0] + lecturas_recientes[1] + lecturas_recientes[2] + lecturas_recientes[3]) / 4;
    promedio_lecturas += 5;

    if sistema_encendido && !alerta_sobrecalentamiento && (promedio_lecturas >= 15 || registro_estado == 0b1010_1100u8) {
        println!("Estado {}: {} [{}]", unidad_temp, mensaje_inicio, ruta_logs);
        println!("Lectura calibrada: {}", promedio_lecturas);
    }
}