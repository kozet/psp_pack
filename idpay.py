import requests

from psp import PaymentServiceProvider


class IDPay(PaymentServiceProvider):
    def __init__(self, request, api_key):
        super(IDPay, self).__init__(request)

        if not api_key:
            raise Exception('Invalid Api Key')
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': api_key,
        }
        self.status_message_mapper = {
            '1': 'پرداخت انجام نشده است',
            '2': 'پرداخت ناموفق بوده است',
            '3': 'خطا رخ داده است',
            '4': 'بلوکه شده',
            '5': 'برگشت به پرداخت کننده',
            '6': 'برگشت خورده سیستمی',
            '7': 'انصراف از پرداخت',
            '8': 'به درگاه پرداخت منتقل شد',
            '10': 'در انتظار تایید پرداخت',
            '100': 'پرداخت تایید شده است',
            '101': 'پرداخت قبلا تایید شده است',
            '200': 'به دریافت کننده واریز شد',
        }

    def send(self):
        data = {
            'order_id': 'order_id as string',
            'amount': 100000,  # IDPay currency is Rials
            'phone': '09120000000',
            'callback': 'https://callback',
        }

        response = requests.post("https://api.idpay.ir/v1.1/payment", json=data, headers=self.headers)
        if response.status_code == 201:
            response = response.json()
            link = response.get('link')
            # TODO Redirect user to link
        else:
            # Failed Payment
            error_message = response.json()['error_message']
            # TODO Send user to failed payment page

    def verify(self):
        status = self.request.POST.get('status')
        token = self.request.POST.get('id')
        order_id = self.request.POST.get('order_id')
        # TODO Check if order_id exists in DB
        data = {
            'order_id': order_id,
            'id': token,
        }

        if str(status) == '100' or str(status) == '101':
            # Already Verified
            # TODO Send user to successful payment page
            pass
        elif str(status) == '10':
            response = requests.post("https://api.idpay.ir/v1.1/payment/verify", json=data, headers=self.headers)
            response = response.json()
            amount = response.get('amount')
            card_number = response.get('payment', {}).get('card_no')
            order_id = response.get('order_id')
            track_id = response.get('track_id')  # Transaction Number

            # TODO Important: If track_id already exists in DB, payment is not valid

            # TODO If track_id does not exist in DB, payment has been verified successfully

            # TODO Send user to successful payment page
        else:
            error_message = self.status_message_mapper[status]

        # TODO Send user to failed payment page
