"""Fútbol Control: la computadora muestra la cancha y los teléfonos son los controles.

El servidor solo crea las salas y reenvía los mensajes entre la pantalla
y los controles por WebSocket. Toda la física del juego corre en el
navegador de la pantalla.
"""

import io
import json
import random
import re
from pathlib import Path

import segno
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, RedirectResponse, Response

BASE = Path(__file__).parent / "templates"
LETRAS = "ABCDEFGHJKLMNPQRSTUVWXYZ"  # sin I ni O para no confundirlas con 1 y 0
CODIGO_VALIDO = re.compile(r"^[A-Z]{4}$")
MAX_JUGADORES = 2

app = FastAPI(title="Fútbol Control")

# rooms[codigo] = {"pantallas": set[WebSocket], "jugadores": {1: ws|None, 2: ws|None}}
rooms: dict[str, dict] = {}


def sala(codigo: str) -> dict:
    if codigo not in rooms:
        rooms[codigo] = {"pantallas": set(), "jugadores": {n: None for n in range(1, MAX_JUGADORES + 1)}}
    return rooms[codigo]


def limpiar(codigo: str) -> None:
    r = rooms.get(codigo)
    if r and not r["pantallas"] and not any(r["jugadores"].values()):
        rooms.pop(codigo, None)


def nuevo_codigo() -> str:
    while True:
        codigo = "".join(random.choice(LETRAS) for _ in range(4))
        if codigo not in rooms:
            return codigo


async def enviar(ws: WebSocket, data: dict) -> None:
    try:
        await ws.send_text(json.dumps(data))
    except Exception:
        pass


# ---------- páginas ----------

@app.get("/")
def inicio():
    return FileResponse(BASE / "index.html")


@app.get("/pantalla")
def pantalla_nueva():
    return RedirectResponse(f"/pantalla/{nuevo_codigo()}")


@app.get("/pantalla/{codigo}")
def pantalla(codigo: str):
    codigo = codigo.upper()
    if not CODIGO_VALIDO.match(codigo):
        return RedirectResponse("/pantalla")
    return FileResponse(BASE / "pantalla.html")


@app.get("/c/{codigo}")
def control(codigo: str):
    if not CODIGO_VALIDO.match(codigo.upper()):
        return RedirectResponse("/")
    return FileResponse(BASE / "control.html")


@app.get("/qr")
def qr(data: str = Query(..., max_length=300)):
    buf = io.BytesIO()
    segno.make(data, error="m").save(buf, kind="svg", scale=8, border=2, dark="#0e2a1c", light="#ffffff")
    return Response(buf.getvalue(), media_type="image/svg+xml", headers={"Cache-Control": "no-store"})


@app.get("/salud")
def salud():
    return {"ok": True, "salas": len(rooms)}


# ---------- tiempo real ----------

@app.websocket("/ws/{codigo}/pantalla")
async def ws_pantalla(ws: WebSocket, codigo: str):
    codigo = codigo.upper()
    if not CODIGO_VALIDO.match(codigo):
        await ws.close(code=1008)
        return
    await ws.accept()
    r = sala(codigo)
    r["pantallas"].add(ws)
    ocupados = [n for n, j in r["jugadores"].items() if j]
    await enviar(ws, {"type": "estado", "jugadores": ocupados})
    try:
        while True:
            texto = await ws.receive_text()
            try:
                msg = json.loads(texto)
            except ValueError:
                continue
            # La pantalla avisa a los controles (gol, fin del partido, vibrar)
            destino = msg.get("para")
            for n, j in list(r["jugadores"].items()):
                if j and (destino is None or destino == n):
                    await enviar(j, msg)
    except WebSocketDisconnect:
        pass
    finally:
        r["pantallas"].discard(ws)
        limpiar(codigo)


@app.websocket("/ws/{codigo}/control")
async def ws_control(ws: WebSocket, codigo: str):
    codigo = codigo.upper()
    if not CODIGO_VALIDO.match(codigo):
        await ws.close(code=1008)
        return
    await ws.accept()
    r = sala(codigo)
    libre = next((n for n, j in r["jugadores"].items() if j is None), None)
    if libre is None:
        await enviar(ws, {"type": "lleno"})
        await ws.close()
        limpiar(codigo)
        return
    r["jugadores"][libre] = ws
    await enviar(ws, {"type": "asignado", "jugador": libre, "pantalla": bool(r["pantallas"])})
    for p in list(r["pantallas"]):
        await enviar(p, {"type": "entra", "jugador": libre})
    try:
        while True:
            texto = await ws.receive_text()
            try:
                msg = json.loads(texto)
            except ValueError:
                continue
            if not isinstance(msg, dict):
                continue
            msg["jugador"] = libre
            for p in list(r["pantallas"]):
                await enviar(p, msg)
    except WebSocketDisconnect:
        pass
    finally:
        if r["jugadores"].get(libre) is ws:
            r["jugadores"][libre] = None
        for p in list(r["pantallas"]):
            await enviar(p, {"type": "sale", "jugador": libre})
        limpiar(codigo)
