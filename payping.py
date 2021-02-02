import requests

from psp import PaymentServiceProvider


class Payping(PaymentServiceProvider):
    def __init__(self, request, token):
        super(Payping, self).__init__(request)
        if not token:
            raise Exception('Invalid Token')
        self.headers = {'Authorization': 'Bearer ' + token}

    def send(self):
        data = {
            "amount": 10000,  # Payping currency is Tomans
            "payerIdentity": '09120000000',
            "payerName": '',
            "description": '',
            "returnUrl": 'https://callback',
            "clientRefId": 'order_id as string'
        }
        response = requests.post('https://api.payping.ir/v2/pay', json=data, headers=self.headers)
        if response.status_code == 200:
            response = response.json()
            code = response['code']
            link = 'https://api.payping.ir/v2/pay/gotoipg/%s' % code
            # TODO Redirect user to link
        else:
            pass
            # TODO Send user to failed payment page

    def verify(self):
        code = self.request.POST.get('code')
        ref_id = self.request.POST.get('refid')
        client_ref_id = self.request.POST.get('clientrefid')
        card_number = self.request.POST.get('cardnumber')
        card_hash_pan = self.request.POST.get('cardhashpan')

        # TODO Important: If refid already exists in DB, payment is not valid

        data = {
            "refId": ref_id,
            "amount": 10000,
        }
        response = requests.post('https://api.payping.ir/v2/pay/verify', json=data, headers=self.headers)
        if response.status_code == 200:
            pass
            # TODO Send user to successful payment page
        else:
            pass

        # TODO Send user to failed payment page
