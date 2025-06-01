# python_client.py
import requests
import json
import time
import uuid # 予約IDのダミー生成などに使用する可能性

class GpuReservationApiClient:
    """GPU予約システムのFastAPIバックエンド用APIクライアントクラス"""

    def __init__(self, api_url):
        """
        初期化
        
        Args:
            api_url (str): API のベース URL（ngrok URL）
        """
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self):
        """
        ヘルスチェック
        
        Returns:
            dict: ヘルスチェック結果
        """
        response = self.session.get(f"{self.api_url}/health")
        return response.json()

    def _send_request(self, action: str, payload: dict, user_id_for_context: str = "test-user-123"):
        """
        共通のリクエスト送信メソッド

        Args:
            action (str): 実行するアクション名
            payload (dict): アクションに渡すペイロード
            user_id_for_context (str): テスト用のユーザーID (FastAPIがuser_contextを期待する場合)

        Returns:
            dict: APIからのレスポンス
        """
        request_body = {
            "action": action,
            "payload": payload,
            "user_context": { # Lambdaが追加するuser_contextを模倣 (テスト用)
                "sub": user_id_for_context,
                "email": f"{user_id_for_context}@example.com"
                # 他に必要なCognitoクレームがあれば追加
            }
        }
        # FastAPIのエンドポイントが /api であると仮定
        api_endpoint = f"{self.api_url}/api"
        print(f"Sending request to {api_endpoint} with action '{action}' and payload: {json.dumps(payload, indent=2)}")

        start_time = time.time()
        try:
            response = self.session.post(api_endpoint, json=request_body)
            total_time = time.time() - start_time
            response.raise_for_status() # HTTPエラーがあれば例外を発生

            result = response.json()
            result["total_request_time_ms"] = round(total_time * 1000)
            print(f"Response for action '{action}': {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
        except requests.exceptions.HTTPError as e:
            print(f"API HTTP error for action '{action}': {e.response.status_code} - {e.response.text}")
            raise  # またはカスタムエラーを返す
        except requests.exceptions.RequestException as e:
            print(f"API request error for action '{action}': {e}")
            raise

    def reserve_gpu_from_nlp(self, natural_language_request: str, user_id: str = "test-user-nlp"):
        """自然言語でGPU予約をリクエスト"""
        payload = {"natural_language_request": natural_language_request}
        return self._send_request("reserve_gpu_from_nlp", payload, user_id)

    def get_my_reservations(self, user_id: str = "test-user-reservations"):
        """指定したユーザーの予約一覧を取得"""
        # このアクションはpayloadが空かもしれないし、ページネーション情報などを含むかもしれない
        payload = {}
        return self._send_request("get_my_reservations", payload, user_id)

    def cancel_reservation(self, reservation_id: str, user_id: str = "test-user-cancel"):
        """指定した予約IDの予約をキャンセル"""
        payload = {"reservation_id": reservation_id}
        return self._send_request("cancel_reservation", payload, user_id)


# 使用例
if __name__ == "__main__":
    # FastAPIサーバーのURL (ローカル実行時またはngrok URL)
    # CDKでデプロイしたAPI Gatewayのエンドポイントをテストする場合は、そのURLと適切なIDトークンが必要
    NGROK_URL = "https://your-ngrok-url.ngrok.url" # FastAPIをローカルで8001ポートで実行する場合
    # NGROK_URL = "https://your-ngrok-subdomain.ngrok.io" # ngrokを使用する場合
    API_BASE_URL = NGROK_URL # こちらを有効化

    # IDトークン (オプション。API Gateway + Cognito Authorizer経由でテストする場合に必要)
    # id_token = "YOUR_VALID_COGNITO_ID_TOKEN"
    # client = GpuReservationApiClient(API_BASE_URL, id_token=id_token)
    client = GpuReservationApiClient(API_BASE_URL)


    print("--- ヘルスチェック ---")
    try:
        health = client.health_check()
        print(json.dumps(health, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"ヘルスチェック失敗: {e}")
    print("-" * 30)

    print("\n--- 自然言語によるGPU予約リクエスト ---")
    try:
        nlp_request = "明日の午後2時から4時間、トレーニング用にA10Gを1台予約したいです。"
        response = client.reserve_gpu_from_nlp(nlp_request, user_id="user-12345")
        # FastAPIからのレスポンス構造に合わせて表示/処理
    except Exception as e:
        print(f"予約リクエスト失敗: {e}")
    print("-" * 30)

    # ダミーの予約ID（実際の予約リクエスト後に得られたIDを使う）
    dummy_reservation_id = str(uuid.uuid4())

    print(f"\n--- ユーザー (user-abcde) の予約一覧取得 ---")
    try:
        reservations = client.get_my_reservations(user_id="user-abcde")
        # FastAPIからのレスポンス構造に合わせて表示/処理
    except Exception as e:
        print(f"予約一覧取得失敗: {e}")
    print("-" * 30)

    print(f"\n--- 予約キャンセル (予約ID: {dummy_reservation_id}) ---")
    try:
        # まずは予約を作成するステップが必要だが、ここではキャンセル処理のテストのみ示す
        # 実際のテストでは、作成した予約のIDを使用する
        cancel_response = client.cancel_reservation(reservation_id=dummy_reservation_id, user_id="user-who-owns-reservation")
        # FastAPIからのレスポンス構造に合わせて表示/処理
    except Exception as e:
        print(f"予約キャンセル失敗: {e}")
    print("-" * 30)
