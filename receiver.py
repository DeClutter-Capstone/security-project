import socket
import des

LISTEN_PORT = 5555
ENCRYPTION_KEY = "12345678"  #  exactly 8 characters, must match sender

def receive_messages():
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    receiver_socket.bind(("0.0.0.0", LISTEN_PORT))
    receiver_socket.listen(5)

    print("=" * 50)
    print("DES RECEIVER MODE")
    print("=" * 50)
    print(f"Listening on port: {LISTEN_PORT}")
    print(f"Encryption Key: {ENCRYPTION_KEY}")
    print("=" * 50)
    print("Waiting for incoming messages...\n")

    try:
        while True:
            client_socket, client_address = receiver_socket.accept()
            print(f"\nConnection from: {client_address[0]}")

            chunks = []
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)

            encrypted_hex = b''.join(chunks).decode()

            if encrypted_hex:
                decrypted = des.decrypt_message(encrypted_hex, ENCRYPTION_KEY)
                print(f" Message received and decrypted:")
                print(f"   Encrypted: {encrypted_hex[:60]}..." if len(encrypted_hex) > 60 else f"   Encrypted: {encrypted_hex}")
                print(f"    Decrypted: {decrypted}")
            else:
                print("  Empty message received")

            client_socket.close()

    except KeyboardInterrupt:
        print("\n\nStopped Receiving")
    except Exception as e:
        print(f" Error: {e}")
    finally:
        receiver_socket.close()

if __name__ == "__main__":
    receive_messages()