import zeep

from psp import PaymentServiceProvider


class Zarinpal(PaymentServiceProvider):
    def __init__(self, request, merchant_id):
        super(Zarinpal, self).__init__(request)
        self.merchant_id = merchant_id
        self.status_message_mapper = {
            '-1': 'اطلاعات ارسال شده ناقص است.',
            '-2': 'IP و یا مرچنت کد پذیرنده صحیح نیست.',
            '-3': 'با توجه به محدودیت‌های شاپرک امکان پرداخت با رقم درخواست شده میسر نمی‌باشد.',
            '-4': 'سطح تایید پذیرنده پایین‌تر از سطح نقره‌ای است.',
            '-9': 'خطای اعتبار سنجی',
            '-10': 'ای پی و يا مرچنت كد پذيرنده صحيح نيست.',
            '-11': 'درخواست مورد نظر یافت نشد.',
            '-12': 'امکان ویرایش درخواست میسر نمی‌باشد.',
            '-15': 'ترمینال شما به حالت تعلیق در آمده با تیم پشتیبانی تماس بگیرید.',
            '-16': 'سطح تاييد پذيرنده پايين تر از سطح نقره ای است.',
            '-21': 'هیچ نوع عملیات مالی برای این تراکنش یافت نشد.',
            '-22': 'تراکنش ناموفق می‌باشد.',
            '-30': 'اجازه دسترسی به تسویه اشتراکی شناور ندارید.',
            '-31': 'حساب بانکی تسویه را به پنل اضافه کنید مقادیر وارد شده واسه تسهیم درست نیست.',
            '-33': 'رقم تراکنش با رقم پرداخت شده مطابقت ندارد.',
            '-34': 'سقف تقسیم تراکنش ار لحاظ تعداد یا رقم عبور نموده است.',
            '-35': 'تعداد افراد دریافت کننده تسهیم بیش از حد مجاز است.',
            '-40': 'اجازه دسترسی به متد مربوطه وجود ندارد.',
            '-41': 'اطلاعات ارسال شده مربوط به AdditionalData غیر معتبر می‌باشد.',
            '-42': 'مدت‌زمان معتبر طول عمر شناسه پرداخت باید بین ۳۰ دقیقه تا ۴۵ روز باشد.',
            '-50': 'مبلغ پرداخت شده با مقدار مبلغ در وریفای متفاوت است.',
            '-51': 'پرداخت ناموفق.',
            '-52': 'خطای غیر منتظره با پشتیبانی تماس بگیرید.',
            '-53': 'اتوریتی برای این مرچنت کد نیست.',
            '-54': 'درخواست مورد نظر آرشیو شده است.',
            '100': 'عملیات با موفقیت انجام گردیده است.',
            '101': 'عملیات پرداخت موفق بوده و قبلا PaymentVerification تراکنش انجام شده است.',
        }

    def send(self):
        order_id = 999999
        amount = 10000
        try:
            client = zeep.Client(wsdl='https://www.zarinpal.com/pg/services/WebGate/wsdl')
            res = client.service.PaymentRequest(self.merchant_id,
                                                amount,  # Zarinpal currency is Tomans
                                                str(order_id),
                                                'customer@email.com',
                                                '09120000000',
                                                'https://callback')
            if res.Status == 100:
                transaction_number = res.Authority
                link = 'https://www.zarinpal.com/pg/StartPay/' + res.Authority
                # TODO Redirect user to link
            else:
                error_message = self.status_message_mapper[str(res.Status)]
        except:
            pass

        # TODO Send user to failed payment page

    def verify(self):
        status = self.request.GET['Status']
        authority = self.request.GET['Authority']

        amount = 10000  # TODO Fetch from DB

        if status == 'OK':
            try:
                client = zeep.Client(wsdl='https://www.zarinpal.com/pg/services/WebGate/wsdl')
                res = client.service.PaymentVerification(self.merchant_id, authority, amount)
                if res.Status == 100 or res.Status == 101:
                    pass
                    # TODO Send user to successful payment page
                else:
                    error_message = self.status_message_mapper[str(res.Status)]
            except:
                pass
        else:
            pass

        # TODO Send user to failed payment page
