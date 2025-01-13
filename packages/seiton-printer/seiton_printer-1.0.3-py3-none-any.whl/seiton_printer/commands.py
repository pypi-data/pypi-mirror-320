from enum import Enum

class PrinterCommands(Enum):
    INICIALIZAR_IMPRESORA = b'\x1B\x40'
    AVANCE_DE_LINEA = b'\x0A'
    AVANCE_DE_LINEAS = b'\x1B\x64'
    AVANCE_Y_CORTE_PAPEL = b'\x1D\x56\x42\x00'
    CORTAR_PAPEL = b'\x1D\x56\x00'
    CORTE_PARCIAL = b'\x1B\x6D'
    NEGRITA = b'\x1B\x21\x01'
    DOBLE_ALTURA = b'\x1B\x21\x08'
    DOBLE_ANCHO = b'\x1B\x21\x10'
    DOBLE_ALTO_NEGRITA = b'\x1B\x21\x08\x1D\x21\x01'
    SUBRAYADO = b'\x1B\x21\x20'
    TAMANO_DOBLE_ALTURA = b'\x1D\x21\x01'
    TAMANO_DOBLE_ANCHO = b'\x1D\x21\x10'
    TAMANO_DOBLE_ANCHO_Y_DOBLE_ALTURA = b'\x1D\x21\x11'
    ALINEACION_IZQUIERDA = b'\x1B\x61\x00'
    ALINEACION_CENTRADA = b'\x1B\x61\x01'
    ALINEACION_DERECHA = b'\x1B\x61\x02'
    ALINEACION = b'\x1B\x61'
    POS_BEEP = b'\x1B\x42'
    PRINT_SELF_TEST = b'\x12\x54'
    HABILITAR_NEGRITA = b'\x1B\x45\x01'
    DESHABILITAR_NEGRITA = b'\x1B\x45\x00'
    HABILITAR_SUBRAYADO = b'\x1B\x2D\x01'
    DESHABILITAR_SUBRAYADO = b'\x1B\x2D\x00'
    STATUS_REQUEST = b'\x10\x05\x01'

    # Comandos QR
    QR_INICIO = b'\x1D\x28\x6B'  # Inicio de comando QR
    QR_CONFIG_MODULO = b'\x31\x43'  # Subcomando para configurar el tamaño del módulo
    QR_ALMACENAR_DATOS = b'\x31\x50\x30'  # Subcomando para almacenar datos
    QR_IMPRIMIR = b'\x31\x51\x30'  # Subcomando para imprimir QR
    QR_PARAM_LONGITUD_MODULO = b'\x03\x00'  # indica que la longitud de los datos siguientes es 3 bytes

    # Códigos de barras
    BARCODE_TYPE_CODE39 = b'\x04'  # Tipo Code 39
    BARCODE_TYPE_CODE128 = b'\x49'  # Tipo Code 128
    BARCODE_PRINT = b'\x1D\x6B'  # Comando base para imprimir código de barras
    BARCODE_WIDTH = b'\x1D\x77'  # Ancho (1-6)
    BARCODE_HEIGHT = b'\x1D\x68'  # Altura (1-255)
    BARCODE_FONT = b'\x1D\x66'  # Fuente HRI
    BARCODE_POSITION = b'\x1D\x48'  # Posición HRI

    # Caracteres especiales
    ENE_MAYUSCULA = b'\x1B\x6E\x00'
    U_CON_DIERESIS = b'\x1B\x6F\x00'
    CODIFICACION_CP850 = b'\x1B\x74\x02'  # Admite letra ñ

    # Control de impresión
    HABILITAR_GS1 = b'\x1B\x3D\x01'

    # Fuente
    CARACTERES_NORMALES = b'\x1B\x4D\x00'
    CARACTERES_CONDENSADOS = b'\x1B\x4D\x01'

    # Imagen
    IMAGE_PRINT = b'\x1B\x2A'  # Imprimir imagen en modo gráfico
    IMAGE_INIT = b'\x1D\x76\x30\x00'  # Comando para iniciar la impresión de imagen

    # Cajón de dinero
    OPEN_CASH_DRAWER = b'\x1B\x70\x00\x19\xFA'  # Comando para abrir el cajón de dinero

    
    
