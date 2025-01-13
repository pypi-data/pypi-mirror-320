#!/usr/bin/env python3
from seiton import Seiton
import asyncio

# Inicializar la impresora con la ruta del dispositivo USB
printer = Seiton('/dev/usb/lp0')

def print_image_example():
    """Ejemplo de impresión de una imagen"""
    try:
        image_path = '../assets/seiton.png'
        
        (printer.align_to_center()
         .double_tall_double_wide()
         .add_text('Impresion de Logo')
         .feed_lines(3)
         .align_to_center()
         .add_image(image_path, 200, None, 1)
         .feed_lines(3)
         .align_to_center()
         .add_text('NO valido como ticket')
         .feed_lines(5)
         .cut_paper()
         .print())
        
        print('Imagen impresa correctamente')
    except Exception as e:
        print('Error al imprimir:', str(e))

def print_styles_example():
    """Ejemplo de diferentes estilos de impresión"""
    try:
        (printer
         .set_default_styles()
         .double_tall_double_wide()
         .add_text('Doble alto doble ancho y Ñ, ñ, á, é, í')
         .feed_lines(2)
         .align_to_right()
         .double_tall()
         .feed_lines(2)
         .align_to_center()
         .double_tall()
         .add_text('Solo doble alto')
         .feed_lines(2)
         .align_to_right()
         .double_wide()
         .add_text('Solo doble ancho')
         .feed_lines(2)
         .double_tall_bold()
         .add_text('Doble alto con negrita')
         .feed_lines(2)
         .enable_bold()  # Aplicar negrita
         .add_text('Texto en negrita')
         .disable_bold()  # Desactivar negrita
         .feed_lines(2)
         .enable_underline()  # Aplicar subrayado
         .add_text('Texto subrayado')
         .disable_underline()  # Desactivar subrayado
         .feed_lines(2)
         .set_default_styles()
         .add_text('Aca volvimos a los estilos por defecto')
         .feed_and_cut_paper()
         .print())
        
        print('Estilos impresos correctamente')
    except Exception as e:
        print('Error al imprimir:', str(e))

def print_qr_example():
    """Ejemplo de impresión de código QR"""
    try:
        (printer
         .set_default_styles()
         .align_to_center()
         .add_text('CODIGO QR DE EJEMPLO')
         .feed_lines(2)
         .generate_qr_code('https://seiton.com.ar/', 8)
         .feed_lines(3)
         .add_text('Escanear el QR')
         .feed_and_cut_paper()
         .print())
        
        print('Código QR impreso correctamente')
    except Exception as e:
        print('Error al imprimir:', str(e))

def print_barcode_example():
    """Ejemplo de impresión de código de barras"""
    try:
        (printer
         .set_default_styles()
         .align_to_center()
         .add_text('CODIGO DE BARRAS')
         .feed_lines(2)
         .add_barcode('123456789', 3, 100)
         .feed_lines(3)
         .add_text('12345678')
         .feed_and_cut_paper()
         .print())
        
        print('Código de barras impreso correctamente')
    except Exception as e:
        print('Error al imprimir:', str(e))

def print_self_test():
    """Ejemplo de impresión de auto-diagnóstico"""
    try:
        (printer
         .set_default_styles()
         .print_self_test()
         .feed_and_cut_paper()
         .print())
        
        print('Auto-diagnóstico impreso correctamente')
    except Exception as e:
        print('Error al imprimir:', str(e))

def test_is_printer_connected():
    """
    Caso de prueba para verificar la conexión de la impresora.
    """
    test_port = '/dev/usb/lp0'  # Ajustar según el puerto de prueba
    is_connected = Seiton.is_printer_connected(test_port)
    if is_connected:
        print(f'La impresora está conectada en el puerto {test_port}.')
    else:
        print(f'No se encontró la impresora en el puerto {test_port}.')

if __name__ == '__main__':
    # Ejecutar ejemplo de imagen
    print_image_example()
    
    # Ejecutar ejemplo de estilos
    print_styles_example()
    
    # Ejecutar ejemplo de QR
    print_qr_example()
    
    # Ejecutar ejemplo de código de barras
    print_barcode_example()
    
    # Ejecutar auto-diagnóstico
    print_self_test()
    
    # Ejecutar el caso de prueba
    test_is_printer_connected()
