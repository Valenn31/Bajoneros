import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No necesita estar disponible, solo para obtener la IP local
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    ip = get_local_ip()
    print(f"\nTu servidor estará disponible en: http://{ip}:8000\n")
    print("Ejecuta el servidor con:")
    print("  python manage.py runserver 0.0.0.0:8000")
    print("o para daphne:")
    print("  daphne -b 0.0.0.0 -p 8000 sistema.asgi:application\n")