import base64
import datetime

import pytz
import requests
import xmltodict
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from psp import PaymentServiceProvider


class Pasargad(PaymentServiceProvider):
    def __init__(self, request, merchant_id, terminal_id, private_key):
        super(Pasargad, self).__init__(request)
        self.merchant_id = merchant_id
        self.terminal_id = terminal_id
        self.private_key = private_key

    def send(self):
        order_id = 999999  # order_id from DB
        amount = 100000  # order amount in Rials
        payment_date = "order creation date from DB with strftime('%Y/%m/%d %H:%M:%S')"
        timestamp = datetime.datetime.now().astimezone(pytz.timezone("Asia/Tehran")).strftime('%Y/%m/%d %H:%M:%S')
        redirect_address = 'https://callback'
        action = '1003'
        sign_data_string = '#%s#%s#%s#%s#%s#%s#%s#%s#' % (self.merchant_id, self.terminal_id, order_id, payment_date,
                                                          amount, redirect_address, action, timestamp)
        sign_data = self._encrypte(sign_data_string)  # encrypt with TripleDes(ECB,PKCS7)

        context = {'form_action': 'https://pep.shaparak.ir/gateway.aspx', 'form_data': {
            'merchantCode': self.merchant_id,
            'terminalCode': self.terminal_id,
            'invoiceNumber': order_id,
            'invoiceDate': payment_date,
            'amount': amount,  # Pasargad currency is Rials
            'timeStamp': timestamp,
            'redirectAddress': redirect_address,
            'action': action,
            'sign': sign_data,
        }}
        # TODO Post a form created with the above context in order to redirect user to bank

    def verify(self):
        order_id = self.request.GET.get('iN')
        amount = 100000  # order amount in Rials
        transaction_ref = self.request.GET.get('tref')
        response = requests.post('https://pep.shaparak.ir/CheckTransactionResult.aspx',
                                 data={'invoiceUID': transaction_ref}).text
        response = xmltodict.parse(response.strip()).get('resultObj')

        result = response.get('result')
        if result == 'True':
            payment_date = "order creation date from DB with strftime('%Y/%m/%d %H:%M:%S')"
            timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            sign_data_string = '#%s#%s#%s#%s#%s#%s#' % (
                self.merchant_id, self.terminal_id, order_id, payment_date, amount, timestamp)
            sign_data = self._encrypte(sign_data_string)  # encrypt with TripleDes(ECB,PKCS7)

            data = {
                'MerchantCode': self.merchant_id,
                'TerminalCode': self.terminal_id,
                'InvoiceNumber': order_id,
                'InvoiceDate': payment_date,
                'amount': amount,
                'TimeStamp': timestamp,
                'sign': sign_data,
            }
            verify_response = requests.post('https://pep.shaparak.ir/VerifyPayment.aspx', data=data).text
            verify_response = xmltodict.parse(verify_response.strip()).get('actionResult')
            verify_result = verify_response.get('result')
            if verify_result == 'True':
                payment_id = response.get('invoiceNumber')
                amount = response.get('amount')
                trans_id = response.get('transactionReferenceID')
                referenceNumber = response.get('referenceNumber')

                # TODO Important: If transactionReferenceID already exists in DB, payment is not valid

                # TODO If transactionReferenceID does not exist in DB, payment has been verfoed successfully

                # TODO Send user to successful payment page
            else:
                error_message = verify_response.get('resultMessage')
        else:
            pass
        # TODO Send user to failed payment page

    def _encrypte(self, text: str):
        digest = SHA1.new(text.encode())
        key = self.private_key.strip()
        rsakey = RSA.importKey(key)
        sign = PKCS1_v1_5.new(rsakey).sign(digest)
        return base64.b64encode(sign).decode()
