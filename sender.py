import socket
import des

RECEIVER_IP = "0.tcp.eu.ngrok.io"
RECEIVER_PORT = 27571
ENCRYPTION_KEY = "12345678"  #  exactly 8 characters, must match receiver

def send_message(message):
    try:
        encrypted_hex = des.encrypt_message(message, ENCRYPTION_KEY)

        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_socket.connect((RECEIVER_IP, RECEIVER_PORT))
        sender_socket.sendall(encrypted_hex.encode())
        sender_socket.close()

        print(f" Message sent successfully!")
        print(f"   Original:  {message}")
        print(f"   Encrypted: {encrypted_hex[:60]}..." if len(encrypted_hex) > 60 else f"   Encrypted: {encrypted_hex}")

    except ConnectionRefusedError:
        print(f" Cannot connect to {RECEIVER_IP}:{RECEIVER_PORT}")
    except Exception as e:
        print(f" Error: {e}")

def interactive_mode():
    print("=" * 50)
    print(" DES SENDER MODE")
    print("=" * 50)
    print(f"Sending to: {RECEIVER_IP}:{RECEIVER_PORT}")
    print(f"Encryption Key: {ENCRYPTION_KEY}")
    print("=" * 50)
    print("Type messages to send ('quit' to exit)\n")

    while True:
        message = input(" Enter message: ")

        if message.lower() == 'quit':
            print("Goodbye!")
            break

        if message.strip():
            send_message(message)
        else:
            print("  Message cannot be empty")

if __name__ == "__main__":
    interactive_mode()