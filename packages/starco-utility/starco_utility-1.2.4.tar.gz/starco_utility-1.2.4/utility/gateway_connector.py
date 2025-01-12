from utility.requesting import SyncRetryClient


class GatewayHandler:
    def __init__(self, merchant_id, base_url: str):
        self.merchant_id = merchant_id
        self.base_url = base_url.rstrip('/')
        self.request = SyncRetryClient()

    def paylink(self, amount, callback_url: str, mobile: str, email: str, description=None):
        url = f'{self.base_url}/create/'
        headers = {
            'Authorization': f'Token {self.merchant_id}'
        }
        data = {
            'amount': amount,
            'callback_url': callback_url,
            'phone': mobile,
            'email': email,
            'description': description
        }
        return self.request.post(url, data, headers=headers)

    def verify(self, amount: int, token: str):
        url = f'{self.base_url}/verify/'
        headers = {
            'Authorization': f'Token {self.merchant_id}'
        }

        data = {
            'amount': amount,
            'token': token,
        }
        return self.request.post(url, data, headers=headers)
