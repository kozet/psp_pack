import base64
import datetime

import requests
from pyDes import triple_des, PAD_PKCS5

from psp import PaymentServiceProvider


class Sadad(PaymentServiceProvider):
    def __init__(self, request, merchant_id, terminal_id, terminal_key):
        super(Sadad, self).__init__(request)
        self.merchant_id = merchant_id
        self.terminal_id = terminal_id
        self.terminal_key = terminal_key

    def send(self):
        order_id = 999999
        amount = 100000
        sign_data_text = self.terminal_id + ';' + str(order_id) + ';' + str(amount)
        sign_data = self._encrypte(sign_data_text).decode('utf-8')  # encrypt with TripleDes(ECB,PKCS7)

        data = {
            'MerchantId': self.merchant_id,
            'TerminalId': self.terminal_id,
            'Amount': amount,  # Sadad currency is Rials
            'OrderId': order_id,
            'LocalDateTime': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'ReturnUrl': 'https://callback',
            'SignData': sign_data,
        }
        response = requests.post('https://sadad.shaparak.ir/VPG/api/v0/Request/PaymentRequest', json=data)

        try:
            response = response.json()
        except Exception:
            context = {'form_action': 'https://sadad.shaparak.ir/VPG/api/v0/Request/PaymentRequest', 'form_data': data}
            # TODO Post a form created with the above context in order to redirect user to back

        status = response.get('ResCode')
        if str(status) == '0':
            token = response['Token']
            link = 'https://sadad.shaparak.ir/VPG/Purchase?Token=' + token
            # TODO Redirect user to link
        else:
            error_message = response.get('Description')
            # TODO Send user to failed payment page

    def verify(self):
        payment_id = self.request.POST.get('OrderId')
        res_code = self.request.POST.get('ResCode')

        if str(res_code) == '0':
            token = self.request.POST.get('token')
            sign_data = self._encrypte(token)  # encrypt with TripleDes(ECB,PKCS7)
            data = {
                'Token': token,
                'SignData': sign_data
            }
            response = requests.post('https://sadad.shaparak.ir/vpg/api/v0/Advice/Verify', data)

            try:
                response = response.json()
            except Exception:
                context = {'form_action': 'https://sadad.shaparak.ir/vpg/api/v0/Advice/Verify', 'form_data': data}
                # TODO Post a form created with the above context in order to redirect user to bank

            res_code = response.get('ResCode')
            if str(res_code) == '0':
                payment_id = self.request.POST.get('OrderId')
                amount = response.get('Amount')
                trans_num = response.get('RetrivalRefNo')
                trace_id = response.get('SystemTraceNo')

                # TODO Important: If RetrivalRefNo already exists in DB, payment is not valid

                # TODO Send user to successful payment page
            else:
                error_message = response.get('errorMessage')
        else:
            error_message = self.request.POST.get('Description')

        # TODO Send user to failed payment page

    def _encrypte(self, text):
        singer = triple_des(key=base64.b64decode(self.terminal_key), padmode=PAD_PKCS5)
        sign_data = singer.encrypt(text)
        return base64.b64encode(sign_data)
