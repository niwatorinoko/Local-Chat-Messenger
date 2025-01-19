import socket
import threading
import os

# 設定
SERVER_ADDRESS = '/tmp/udp_chat_server'
CLIENT_ADDRESS = '/tmp/udp_chat_client'
BUFFER_SIZE = 4096

# サーバからのメッセージ受信スレッド
def receive_messages(sock):
    while True:
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            print(data.decode('utf-8'))
        except Exception as e:
            print(f"受信エラー: {e}")
            break

def client_main():
    # ソケット作成
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    # 既存のクライアントソケットファイルを削除
    try:
        os.unlink(CLIENT_ADDRESS)
    except FileNotFoundError:
        pass

    # ソケットをクライアントアドレスにバインド
    sock.bind(CLIENT_ADDRESS)

    # ユーザー名を取得
    username = input("ユーザー名を入力してください: ")
    if len(username.encode('utf-8')) > 255:
        print("ユーザー名が長すぎます (最大255バイト)。")
        return

    # サーバからのメッセージ受信スレッドを開始
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    print("チャットを開始します (終了するには 'exit' と入力):")
    try:
        while True:
            # ユーザーの入力を取得
            message = input()
            if message.lower() == 'exit':
                print("チャットを終了します。")
                break

            # メッセージを送信
            username_length = len(username.encode('utf-8'))
            data = bytes([username_length]) + username.encode('utf-8') + message.encode('utf-8')
            sock.sendto(data, SERVER_ADDRESS)

    finally:
        # ソケットを閉じる
        sock.close()
        os.unlink(CLIENT_ADDRESS)

if __name__ == "__main__":
    client_main()
