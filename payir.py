import requests

from psp import PaymentServiceProvider


class PayIR(PaymentServiceProvider):
    def __init__(self, request, api_key):
        super(PayIR, self).__init__(request)
        self.api_key = api_key
        self.status_message_mapper = {
            '0': 'درحال حاضر درگاه بانکی قطع شده و مشکل بزودی برطرف می شود',
            '-1': 'API Key ارسال نمی شود',
            '-2': 'Token ارسال نمی شود',
            '-3': 'API Key ارسال شده اشتباه است',
            '-4': 'امکان انجام تراکنش برای این پذیرنده وجود ندارد',
            '-5': 'تراکنش با خطا مواجه شده است',
            '-6': 'تراکنش تکراریست یا قبلا انجام شده',
            '-7': 'مقدار Token ارسالی اشتباه است',
            '-8': 'شماره تراکنش ارسالی اشتباه است',
            '-9': 'زمان مجاز برای انجام تراکنش تمام شده',
            '-10': 'مبلغ تراکنش ارسال نمی شود',
            '-11': 'مبلغ تراکنش باید به صورت عددی و با کاراکترهای لاتین باشد',
            '-12': 'مبلغ تراکنش می بایست عددی بین 10,000 و 500,000,000 ریال باشد',
            '-13': 'مقدار آدرس بازگشتی ارسال نمی شود',
            '-14': 'آدرس بازگشتی ارسالی با آدرس درگاه ثبت شده در شبکه پرداخت پی یکسان نیست',
            '-15': 'امکان وریفای وجود ندارد. این تراکنش پرداخت نشده است',
            '-16': 'یک یا چند شماره موبایل از اطلاعات پذیرندگان ارسال شده اشتباه است',
            '-17': 'میزان سهم ارسالی باید بصورت عددی و بین 1 تا 100 باشد',
            '-18': 'فرمت پذیرندگان صحیح نمی باشد',
            '-19': 'هر پذیرنده فقط یک سهم میتواند داشته باشد',
            '-20': 'مجموع سهم پذیرنده ها باید 100 درصد باشد',
            '-21': 'Reseller ID ارسالی اشتباه است',
            '-22': 'فرمت یا طول مقادیر ارسالی به درگاه اشتباه است',
            '-23': 'سوییچ PSP ( درگاه بانک ) قادر به پردازش درخواست نیست. لطفا لحظاتی بعد مجددا تلاش کنید',
            '-24': 'شماره کارت باید بصورت 16 رقمی، لاتین و چسبیده بهم باشد',
            '-25': 'امکان استفاده از سرویس در کشور مبدا شما وجود نداره',
            '-26': 'امکان انجام تراکنش برای این درگاه وجود ندارد',
        }

    def send(self):
        data = {
            'api': self.api_key,
            'amount': 'amount as string',  # PayIR currency is Rials
            'redirect': 'https://callback',
            'mobile': '09120000000',
            'factorNumber': 'order_id as string'
        }

        response = requests.post('https://pay.ir/pg/send', data)
        response = response.json()
        status = response.get('status')
        if str(status) == '1':
            token = response.get('token')
            link = 'https://pay.ir/pg/' + token
            # TODO Redirect user to link
        else:
            # Failed Payment
            error_message = self.status_message_mapper[str(status)]
            # TODO Send user to failed payment page

    def verify(self):
        status = self.request.GET.get('status')
        token = self.request.GET.get('token')

        if str(status) == '1':
            data = {
                'api': self.api_key, 'token': token,
            }
            response = requests.post('https://pay.ir/pg/verify', data)
            response = response.json()
            status = response.get('status')
            transId = response.get('transId')
            factorNumber = response.get('factorNumber')
            cardNumber = response.get('cardNumber')

            # TODO Important: If transId already exists in DB, payment is not valid

            if str(status) == '1':
                pass
                # TODO Send user to successful payment page
            else:
                error_message = self.status_message_mapper[str(status)]
        else:
            pass
        # TODO Send user to failed payment page
