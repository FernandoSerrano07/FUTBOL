# Fútbol Control

Juego de fútbol donde **la computadora es la cancha y el teléfono es el control**.
Se juega desde el navegador, sin instalar nada: la pantalla muestra un código QR,
lo escaneás con el teléfono y queda como mando con joystick y botón de **PATEAR**.

- 1 teléfono: jugás contra la computadora.
- 2 teléfonos: jugador 1 (azul) contra jugador 2 (rojo).
- También funciona con teclado: J1 con W A S D + Espacio, J2 con flechas + Enter.
- Partidos de 3 minutos, con marcador, "¡GOL!" en pantalla y vibración en el teléfono.

Hecho en Python con FastAPI. El servidor crea las salas (código de 4 letras) y pasa
los movimientos del teléfono a la pantalla por WebSocket.

## Estructura

```
app.py              servidor (páginas, código QR y conexión en tiempo real)
templates/
  index.html        página de inicio
  pantalla.html     la cancha (se abre en la computadora)
  control.html      el control (se abre en el teléfono)
requirements.txt    librerías de Python
render.yaml         configuración para Render
```

## Probarlo en tu computadora (opcional)

Necesitás Python 3.10 o más reciente.

```
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Abrí `http://localhost:8000` en la computadora. Para usar el teléfono como control,
el teléfono debe estar en la misma red Wi-Fi y abrir `http://IP-DE-TU-COMPU:8000`.

## Subirlo a GitHub

1. Entrá a github.com, iniciá sesión y tocá **New repository**.
2. Ponele un nombre (por ejemplo `futbol-control`), dejalo **Public** y tocá **Create repository**.
3. En la página del repositorio nuevo, tocá **uploading an existing file**.
4. Arrastrá **todo el contenido** de esta carpeta (los archivos y la carpeta `templates`, no la carpeta de afuera).
5. Abajo tocá **Commit changes**.

## Publicarlo en Render

1. Entrá a render.com y creá una cuenta con tu usuario de GitHub.
2. Tocá **New +** → **Blueprint**.
3. Elegí el repositorio `futbol-control` y tocá **Connect**. Render lee el archivo `render.yaml` solo.
4. Tocá **Apply** y esperá unos minutos a que diga **Live**.
5. Render te da un enlace como `https://futbol-control.onrender.com`. Ese es tu juego.

Si preferís hacerlo a mano: **New +** → **Web Service**, elegí el repositorio y usá:
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips="*"`
- Plan: Free

## Cómo jugar

1. En la computadora abrí tu enlace de Render y tocá **Abrir la cancha en esta pantalla**.
2. Escaneá el QR con la cámara del teléfono (o entrá al enlace y escribí el código).
3. Presioná **PATEAR** en el teléfono o **Empezar partido** en la computadora.
4. Mové el joystick para correr y tocá **PATEAR** cerca del balón para disparar.

## Detalle del plan gratis de Render

En el plan gratis, el servicio se "duerme" después de un rato sin uso. La primera vez
que lo abrás después de eso puede tardar cerca de un minuto en cargar. Es normal.
