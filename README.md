# QR Generator App

Aplicacion de escritorio para crear codigos QR desde uno o varios enlaces, con interfaz moderna y flujo rapido para usuario final.

## Funcionalidades

- Generacion de QR desde un enlace individual.
- Generacion en lote pegando multiples enlaces (uno por linea).
- Carga de enlaces desde archivo de texto.
- Seleccion de carpeta de salida desde explorador.
- Nombres automaticos amigables basados en dominio.
    - Ejemplo: `https://www.google.com` -> `google-qr.png`
- Evita colisiones de nombre con numeracion automatica.
    - Ejemplo: `google-qr.png`, `google-qr-2.png`, `google-qr-3.png`
- Mensajes y notificaciones visuales integradas al estilo de la app.
- Soporte de icono personalizado para ventana principal y dialogos.
- Configuracion del tamano y margen de los codigos QR.
- Selector de idioma entre espanol e ingles.

## Tecnologias implementadas

- Python 3
- PyQt6 (interfaz grafica)
- qrcode + Pillow (generacion y exportacion de imagen)

## Privacidad

La aplicacion no envia enlaces a internet ni guarda informacion personal fuera de los archivos QR que tu decidas exportar.
