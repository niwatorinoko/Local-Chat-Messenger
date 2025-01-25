import socket
import threading
import time
from faker import Faker

# サーバ設定
SERVER_ADDRESS = '/tmp/udp_chat_server'
BUFFER_SIZE = 4096
CLIENT_TIMEOUT = 60  # クライアントのタイムアウト (秒)

# クライアント情報を管理する辞書 {address: last_active_time}
clients = {}

# Faker インスタンス
faker = Faker()

# クライアントの監視スレッド
def monitor_clients():
    while True:
        current_time = time.time()
        for client, last_seen in list(clients.items()):
            if current_time - last_seen > CLIENT_TIMEOUT:
                print(f"タイムアウト: {client}")
                del clients[client]
        time.sleep(1)

# サーバのメインスレッド
def server_main():
    # ソケット作成
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    # 既存のソケットファイル削除
    try:
        import os
        os.unlink(SERVER_ADDRESS)
    except FileNotFoundError:
        pass

    # ソケットをサーバアドレスにバインド
    sock.bind(SERVER_ADDRESS)
    print(f"サーバが開始されました: {SERVER_ADDRESS}")

    # クライアント監視スレッドを開始
    threading.Thread(target=monitor_clients, daemon=True).start()

    while True:
        try:
            # クライアントからのメッセージを受信
            data, client_address = sock.recvfrom(BUFFER_SIZE)
            clients[client_address] = time.time()  # 最終アクティブ時間を更新

            # ユーザー名とメッセージを解析
            username_length = data[0]
            username = data[1:1 + username_length].decode('utf-8')
            message = data[1 + username_length:].decode('utf-8')

            print(f"{username} ({client_address}): {message}")

            # クライアント間のリレー用メッセージを作成
            relay_message = f"{username}: {message}".encode('utf-8')
            for client in clients.keys():
                if client != client_address:
                    sock.sendto(relay_message, client)

            # ランダムな応答を生成
            fake_message = faker.text(max_nb_chars=50)
            fake_response = f"[サーバー]: {fake_message}".encode('utf-8')

            # サーバからの応答をすべてのクライアントにリレー
            for client in clients.keys():
                sock.sendto(fake_response, client)

        except Exception as e:
            print(f"エラー: {e}")

if __name__ == "__main__":
    server_main()
