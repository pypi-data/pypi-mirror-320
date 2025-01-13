from PIL import Image
import io
from seiton_printer.commands import PrinterCommands

class Seiton:
    def __init__(self, usb_port_path):
        self.usb_port_path = usb_port_path
        self.buffer = bytearray()
        self.set_default_styles()
    
    def _write_to_printer(self, data):
        with open(self.usb_port_path, 'wb') as printer:
            printer.write(data)
    
    def add_text(self, text):
        """Agrega texto al buffer actual."""
        mapped_text = self.map_special_characters(text)  # Map special characters
        self.buffer.extend(f"{mapped_text}\n".encode('latin-1'))
        return self
    
    def set_default_styles(self):
        """Restablece los estilos a los valores predeterminados."""
        self.buffer.extend(PrinterCommands.INICIALIZAR_IMPRESORA.value)
        return self
    
    def align_to_right(self):
        """Alinea el contenido a la derecha."""
        self.buffer.extend(PrinterCommands.ALINEACION_DERECHA.value)
        return self
    
    def align_to_center(self):
        """Centra el contenido."""
        self.buffer.extend(PrinterCommands.ALINEACION_CENTRADA.value)
        return self
    
    def feed_line(self):
        """Avanza el papel una línea."""
        self.buffer.extend(PrinterCommands.AVANCE_DE_LINEA.value)
        return self
    
    def feed_lines(self, lines):
        """Avanza el papel un número específico de líneas."""
        self.buffer.extend(PrinterCommands.AVANCE_DE_LINEAS.value + bytes([lines]))
        return self
    
    def cut_paper(self):
        """Activa la cuchilla para cortar el papel."""
        self.buffer.extend(PrinterCommands.CORTAR_PAPEL.value)
        return self
    
    def feed_and_cut_paper(self):
        """Avanza el papel una línea y luego lo corta."""
        self.buffer.extend(PrinterCommands.AVANCE_Y_CORTE_PAPEL.value)
        return self
    
    def double_tall_double_wide(self):
        """Aplica formato de texto doble alto y doble ancho."""
        self.buffer.extend(PrinterCommands.TAMANO_DOBLE_ANCHO_Y_DOBLE_ALTURA.value)
        return self
    
    def double_tall(self):
        """Aplica formato de texto doble alto."""
        self.buffer.extend(PrinterCommands.TAMANO_DOBLE_ALTURA.value)
        return self
    
    def double_wide(self):
        """Aplica formato de texto doble ancho."""
        self.buffer.extend(PrinterCommands.TAMANO_DOBLE_ANCHO.value)
        return self
    
    def double_tall_bold(self):
        """Aplica formato de texto doble alto y negrita."""
        self.buffer.extend(PrinterCommands.DOBLE_ALTO_NEGRITA.value)
        return self
    
    def pos_beep(self, beep_count, beep_millis):
        """Activa el buzzer de la impresora."""
        beep_command = bytes([*PrinterCommands.POS_BEEP.value, beep_count, beep_millis])
        self.buffer.extend(beep_command)
        return self
    
    def generate_qr_code(self, content, size):
        """Genera un código QR."""
        if size < 1 or size > 16:
            raise ValueError('El tamaño del código QR debe estar entre 1 y 16.')
        
        # Comando de tamaño
        size_command = bytes([
            *PrinterCommands.QR_INICIO.value,
            *PrinterCommands.QR_PARAM_LONGITUD_MODULO.value,
            *PrinterCommands.QR_CONFIG_MODULO.value,
            size
        ])
        
        # Comando para almacenar datos
        store_command = bytearray()
        store_command.extend(PrinterCommands.QR_INICIO.value)
        content_length = len(content) + 3
        store_command.extend([content_length & 0xff, (content_length >> 8) & 0xff])
        store_command.extend(PrinterCommands.QR_ALMACENAR_DATOS.value)
        store_command.extend(content.encode('utf8'))
        
        # Comando para imprimir
        print_command = bytes([
            *PrinterCommands.QR_INICIO.value,
            *PrinterCommands.QR_PARAM_LONGITUD_MODULO.value,
            *PrinterCommands.QR_IMPRIMIR.value
        ])
        
        self.buffer.extend(size_command)
        self.buffer.extend(store_command)
        self.buffer.extend(print_command)
        return self
    
    def add_barcode(self, barcode_data, width=3, height=100):
        """
        Genera un código de barras CODE39.
        
        Args:
            barcode_data (str): Datos para codificar
            width (int): Ancho del código de barras (1-6)
            height (int): Altura del código de barras (1-255)
        """
        if not barcode_data:
            raise ValueError('El contenido del código de barras no puede estar vacío.')
        
        if width < 1 or width > 6:
            raise ValueError('El ancho del código de barras debe estar entre 1 y 6.')
            
        if height < 1 or height > 255:
            raise ValueError('La altura del código de barras debe estar entre 1 y 255.')
        
        try:
            # Configurar ancho
            self.buffer.extend(PrinterCommands.BARCODE_WIDTH.value + bytes([width]))
            
            # Configurar altura
            self.buffer.extend(PrinterCommands.BARCODE_HEIGHT.value + bytes([height]))
            
            # Configurar posición del texto HRI (debajo del código)
            self.buffer.extend(PrinterCommands.BARCODE_POSITION.value + b'\x02')
            
            # Configurar fuente HRI
            self.buffer.extend(PrinterCommands.BARCODE_FONT.value + b'\x00')
            
            # Intentar primero con CODE39 (más simple y confiable)
            barcode_bytes = barcode_data.encode('ascii')
            self.buffer.extend(PrinterCommands.BARCODE_PRINT.value + 
                             PrinterCommands.BARCODE_TYPE_CODE39.value +
                             barcode_bytes + b'\x00')
            
            return self
            
        except Exception as e:
            print(f"Error al generar código de barras: {str(e)}")
            raise
    
    def print_self_test(self):
        """Imprime la página de autodiagnóstico."""
        self.buffer.extend(PrinterCommands.PRINT_SELF_TEST.value)
        return self
    
    def add_image(self, image_path, width=None, height=None, alignment=1):
        """
        Agrega una imagen al buffer.
        
        Args:
            image_path (str): Ruta a la imagen
            width (int, optional): Ancho deseado de la imagen
            height (int, optional): Alto deseado de la imagen
            alignment (int, optional): Alineación (0=izquierda, 1=centro, 2=derecha)
        """
        try:
            printer_width = 384  # Ancho común en impresoras térmicas
            resize_width = width or printer_width
            resize_height = height

            # Abrir y procesar la imagen
            img = Image.open(image_path)
            
            # Redimensionar manteniendo el aspect ratio si no se especifica height
            if resize_width and not resize_height:
                ratio = resize_width / img.width
                resize_height = int(img.height * ratio)
        
            if resize_width or resize_height:
                img = img.resize((resize_width, resize_height))
        
            # Convertir a escala de grises y luego a binario
            img = img.convert('L')
            img = img.point(lambda x: 0 if x < 128 else 255, '1')
        
            # Obtener dimensiones
            width_pixels = img.width
            height_pixels = img.height
        
            # Calcular bytes por línea (redondeado a múltiplo de 8)
            width_bytes = (width_pixels + 7) // 8
        
            # Inicializar el buffer de imagen
            image_buffer = bytearray()
        
            # Alineación
            image_buffer.extend(b'\x1B\x61' + bytes([alignment]))
        
            # Comando GS v 0
            image_buffer.extend(b'\x1D\x76\x30\x00')
        
            # Ancho y alto en bytes
            image_buffer.extend(bytes([
                width_bytes & 0xFF,
                (width_bytes >> 8) & 0xFF,
                height_pixels & 0xFF,
                (height_pixels >> 8) & 0xFF
            ]))
        
            # Convertir imagen a bytes
            pixels = list(img.getdata())
        
            # Procesar cada línea
            for y in range(height_pixels):
                line = bytearray(width_bytes)
                for x in range(width_pixels):
                    if pixels[y * width_pixels + x] == 0:  # pixel negro
                        line[x // 8] |= (1 << (7 - (x % 8)))
                image_buffer.extend(line)
        
            # Limpiar cualquier comando residual
            image_buffer.extend(b'\x1B\x40')  # Inicializar impresora
            image_buffer.extend(b'\x1B\x4A\x00')  # Avance de línea mínimo
        
            # Agregar el buffer de imagen al buffer principal
            self.buffer.extend(image_buffer)
        
            return self
        
        except Exception as e:
            print(f'Error al procesar la imagen: {str(e)}')
            raise
    
    def map_special_characters(self, text: str) -> str:
        """
        Mapea los caracteres especiales a sus códigos de impresora.

        Args:
            text (str): Texto a mapear

        Returns:
            str: Texto con caracteres especiales mapeados
        """
        special_chars = {
            'á': '\xA0',
            'é': '\x82',
            'í': '\xA1',
            'ó': '\xA2',
            'ú': '\xA3',
            'ñ': '\xA4',
            'Ñ': '\xA5',
        }

        return ''.join(special_chars.get(char, char) for char in text)


    def open_cash_drawer(self):
        """
        Abre el cajón de dinero conectado a la impresora.

        Returns:
            self: La instancia actual de Seiton para continuar armando el ticket
        """
        # Utilizar el comando definido en commands.py
        self.buffer.extend(PrinterCommands.OPEN_CASH_DRAWER.value)
        return self
    
    def enable_bold(self):
        """
        Aplica el formato de texto en negrita.

        Returns:
            self: La instancia actual de Seiton para continuar armando el ticket
        """
        self.buffer.extend(PrinterCommands.HABILITAR_NEGRITA.value)
        return self

    def disable_bold(self):
        """
        Desactiva el formato de texto en negrita.

        Returns:
            self: La instancia actual de Seiton para continuar armando el ticket
        """
        self.buffer.extend(PrinterCommands.DESHABILITAR_NEGRITA.value)
        return self

    def enable_underline(self):
        """
        Aplica el formato de texto subrayado.

        Returns:
            self: La instancia actual de Seiton para continuar armando el ticket
        """
        self.buffer.extend(PrinterCommands.HABILITAR_SUBRAYADO.value)
        return self

    def disable_underline(self):
        """
        Desactiva el formato de texto subrayado.

        Returns:
            self: La instancia actual de Seiton para continuar armando el ticket
        """
        self.buffer.extend(PrinterCommands.DESHABILITAR_SUBRAYADO.value)
        return self
    
    def print(self):
        """Imprime el ticket."""
        try:
            self._write_to_printer(self.buffer)
            self.buffer = bytearray()
        except Exception as e:
            print(f"Error al imprimir: {str(e)}")
            raise

    
    def is_printer_connected(port: str) -> bool:
        """
        Verifica si la impresora está conectada a un puerto USB específico.
        :param port: El puerto USB a verificar.
        :return: Verdadero si la impresora está conectada, falso si no lo está.
        """
        try:
            print('Verificando la conexión de la impresora...')
            status_command = PrinterCommands.STATUS_REQUEST.value
            with open(port, 'wb') as usb_port:
                usb_port.write(status_command)
            print('Comando de estado enviado con éxito.')
            return True
        except Exception as error:
            print(f'Error al verificar la conexión de la impresora: {error}')
            return False