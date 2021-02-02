import re

import requests
from zeep import Client
from zeep.transports import Transport

from psp import PaymentServiceProvider


class Saman(PaymentServiceProvider):
    def __init__(self, request, merchant_id, password):
        super(Saman, self).__init__(request)
        self.merchant_id = merchant_id
        self.password = password
        if not self.merchant_id or not self.password:
            raise Exception('Invalid Credentials')
        self.verify_code_mapper = {
            '-1': 'خطای در پردازش اطلاعات ارسالی.',
            '-3': 'ورودیها حاوی کارکترهای غیرمجاز میباشند.',
            '-4': '.کلمه عبور یا کد فروشنده اشتباه است',
            '-6': 'سند قبلا برگشت کامل یافته است. یا خارج از زمان  30دقیقه ارسال شده است.',
            '-7': 'رسید دیجیتالی تهی است.',
            '-8': 'طول ورودیها بیشتر از حد مجاز است.',
            '-9': 'وجود کارکترهای غیرمجاز در مبلغ برگشتی.',
            '-10': 'رسید دیجیتالی حاوی کاراکترهای غیرمجاز است.',
            '-11': 'طول ورودیها کمتر از حد مجاز است.',
            '-12': 'مبلغ برگشتی منفی است.',
            '-13': 'مبلغ برگشتی برای برگشت جزئی بیش از مبلغ برگشت نخورده ی رسید دیجیتالی است.',
            '-14': 'چنین تراکنشی تعریف نشده است.',
            '-15': 'مبلغ برگشتی به صورت اعشاری داده شده است.',
            '-16': 'خطای داخلی سیستم درگاه',
            '-17': 'برگشت زدن جزیی تراکنش مجاز نیست.',
            '-18': 'آی پی فروشنده نا معتبر است و یا رمز اشتباه است.',
        }
        self.status_code_mapper = {
            '-1': ('Canceled By User', 'تراکنش توسط خریدار کنسل شده است.'),
            '5': ('Honour Not Do', ' از انجام تراکنش صرف نظر شد.'),
            '12': ('Invalid Transaction', 'درخواست برگشت یک تراکنش رسیده است، در حالی که تراکنش اصلی پیدا نمی شود.'),
            '14': ('Invalid Card Number', 'شماره کارت نامعتبر است.'),
            '15': ('No Such Issuer', 'چنین صادر کننده کارتی وجود ندارد.'),
            '33': ('Expired Card Pick Up', 'از تاریخ انقضای کارت گذشته است و کارت دیگر معتبر نیست.'),
            '34': ('Suspected Fraud Pick Up', 'خریدار یا فیلد CVV2 و یا فیلد ExpDate را اشتباه وارد کرده است.'),
            '38': ('Allowable PIN Tries Exceeded Pick Up',
                   'رمز کارت 3 مرتبه اشتباه وارد شده است در نتیجه کارت غیر فعال خواهد شد.'),
            '51': ('No Sufficient Funds', 'موجودی حساب خریدار، کافی نیست.'),
            '54': ('Expired Account', 'تاریخ انقضای کارت سپری شده است.'),
            '55': ('Incorrect PIN', 'خریدار رمز کارت را اشتباه وارد کرده است.'),
            '56': ('No Card Record', 'کارت نامعتبر است.'),
            '57': ('Transaction Not Permitted', 'انجام تراکنش مربوطه توسط دارنده کارت مجاز نمی باشد.'),
            '61': ('Exceeds Withdrawal Amount Limit', 'مبلغ بیش از سقف برداشت می باشد.'),
            '65': ('Exceeds Withdrawal Frequency Limit', 'تعداد درخواست تراکنش بیش از حد مجاز است.'),
            '68': ('Response Received Too Late', 'تراکنش در شبکه بانکی Timeout خورده است.'),
            '75': ('PIN Reties Exceeds-Slm', 'تعداد دفعات ورود رمز غلط بیش از حد مجاز است.'),
            '79': ('Invalid Amount', 'مبلغ سند برگشتی، از مبلغ تراکنش اصلی بیشتر است.'),
            '80': ('PIN Reties Exceeds-Slm', 'تعداد دفعات ورود رمز غلط بیش از حد مجاز است.'),
            '84': ('Issuer Down Slm', 'سیستم بانک صادر کننده کارت خریدار، در وضعیت عملیاتی نیست.'),
            '93': ('Transaction Cannot Be Completed', 'امکان سند خوردن وجود ندارد.'),
            '96': ('TME Error', 'خطای نامشخص در شبکه بانکی.'),
        }
        self.transport = Transport()
        self.transport.session.headers.pop('User-Agent')
        requests.packages.urllib3.disable_warnings()
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        try:
            requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        except AttributeError:
            pass

    def send(self):
        token = self.get_token()
        if not token:
            pass
            # TODO Send user to failed payment page

        data = {
            'Token': token,
            'RedirectURL': 'https://callback',
        }
        context = {'form_action': 'https://sep.shaparak.ir/payment.aspx', 'form_data': data}
        # TODO Post a form created with the above context in order to redirect user to bank

    def get_token(self):
        order_id = 999999
        amount = 100000  # Saman currency is Rials
        client = Client('https://sep.shaparak.ir/payments/initpayment.asmx?WSDL', transport=self.transport)
        res = client.service.RequestToken(self.merchant_id, order_id, amount, 0, 0, 0, 0, 0, 0, 0, "", 0, "")
        error_code = self.get_error_code(res)
        if error_code:
            return None
        return res

    def verify(self):
        state = self.request.POST['State']
        state_code = self.request.POST['StateCode']
        refnum = self.request.POST['RefNum']
        cid = self.request.POST['CID']
        traceno = self.request.POST['TRACENO']
        securepan = self.request.POST['SecurePan']
        resnum = self.request.POST['ResNum']
        mid = self.request.POST['MID']

        amount = 100000  # TODO Fetch amount form DB

        # TODO Important: If TRACENO already exists in DB, payment is not valid

        if state_code == '0':
            try:
                client = Client('https://sep.shaparak.ir/payments/referencepayment.asmx?WSDL',
                                transport=self.transport)
                verify = client.service.verifyTransaction(refnum, str(self.merchant_id))
                if verify > 0:
                    if int(verify) == amount:
                        pass
                        # TODO Send user to successful payment page
                    else:
                        client.service.reverseTransaction(refnum, mid, mid, str(self.password))
                else:
                    error_message = self.verify_code_mapper[str(int(verify))]
            except:
                pass

        # TODO Send user to failed payment page

    def get_error_code(self, response):
        has_error = re.match(r'^-\d+\.?\d*$', response)
        if has_error:
            return response.split('.')[0]
        return None
