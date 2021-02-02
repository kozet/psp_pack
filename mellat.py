import datetime

import pytz
import zeep

from psp import PaymentServiceProvider


class Mellat(PaymentServiceProvider):
    def __init__(self, request, terminal_id, username, password):
        super(Mellat, self).__init__(request)
        self.terminal_id = terminal_id
        self.username = username
        self.password = password
        self.status_code_mapper = {
            '11': 'شماره کارت نامعتبر است',
            '12': 'موجودی کافی نیست',
            '13': 'رمز نادرست است',
            '14': 'تعداد دفعات وارد کردن رمز بیش از حد مجاز است',
            '15': 'کارت نامعتبر است',
            '16': 'دفعات برداشت وجه بیش از حد مجاز است',
            '17': 'کاربر از انجام تراکنش منصرف شده است',
            '18': 'تاریخ انقضای کارت گذشته است',
            '19': 'مبلغ برداشت وجه بیش از حد مجاز است',
            '111': 'صادر کننده کارت نامعتبر است',
            '112': 'خطای سوییچ صادر کننده کارت',
            '113': 'پاسخی از صادر کننده کارت دریافت نشد',
            '114': 'دارنده این کارت مجاز به انجام این تراکنش نیست',
            '21': 'پذیرنده نامعتبر است',
            '23': 'خطای امنیتی رخ داده است',
            '24': 'اطلاعات کاربری پذیرنده نامعتبر است',
            '25': 'مبلغ نامعتبر است',
            '31': 'پاسخ نامعتبر است',
            '32': 'فرمت اطلاعات وارد شده صحیح نمی‌باشد',
            '33': 'حساب نامعتبر است',
            '34': 'خطای سیستمی',
            '35': 'تاریخ نامعتبر است',
            '41': 'شماره درخواست تکراری است',
            '42': 'تراکنش Sale یافت نشد',
            '43': 'قبلا درخواست Verfiy داده شده است',
            '44': 'درخواست Verfiy یافت نشد',
            '45': 'تراکنش Settle شده است',
            '46': 'تراکنش Settle نشده است',
            '47': 'تراکنش Settle یافت نشد',
            '48': 'تراکنش Reverse شده است',
            '49': 'تراکنش Refund یافت نشد.',
            '412': 'شناسه قبض نادرست است',
            '413': 'شناسه پرداخت نادرست است',
            '414': 'سازمان صادر کننده قبض نامعتبر است',
            '415': 'مدت زمان مجاز برای انجام تراکنش به پایان رسیده است',
            '416': 'خطا در ثبت اطلاعات',
            '417': 'شناسه پرداخت کننده نامعتبر است',
            '418': 'اشکال در تعریف اطلاعات مشتری',
            '419': 'تعداد دفعات ورود اطلاعات از حد مجاز گذشته است',
            '421': 'IP نامعتبر است',
            '51': 'تراکنش تکراری است',
            '54': 'تراکنش مرجع موجود نیست',
            '55': 'تراکنش نامعتبر است',
            '61': 'خطا در واریز'
        }

    def send(self):
        try:
            client = zeep.Client(wsdl='https://bpm.shaparak.ir/pgwchannel/services/pgw?wsdl')
            res = client.service.bpPayRequest(terminalId=int(self.terminal_id),
                                              userName=self.username,
                                              userPassword=self.password,
                                              orderId=999999,  # orderId from DB
                                              amount=100000,  # Mellat currency is Rials
                                              localDate=datetime.datetime.now().astimezone(
                                                  pytz.timezone("Asia/Tehran")).strftime("%Y%m%d"),
                                              localTime=datetime.datetime.now().astimezone(
                                                  pytz.timezone("Asia/Tehran")).strftime("%H%M%S"),
                                              additionalData='',
                                              callBackUrl='https://callback',
                                              payerId=888888)  # payerId from DB
            res_parts = res.split(',')
            res_code = res_parts[0]
            if res_code == '0':
                ref_id = res_parts[1]

                context = {'form_action': 'https://bpm.shaparak.ir/pgwchannel/startpay.mellat',
                           'form_data': {'RefId': ref_id, 'mobileNo': '09120000000'}}

                # TODO Post a form created with the above context in order to redirect user to bank
            else:
                error_message = self.status_code_mapper[res_code]
        except:
            pass

        # TODO Send user to failed payment page

    def verify(self):
        res_code = self.request.POST['ResCode']
        if res_code == '0':
            sale_order_id = self.request.POST['SaleOrderId']
            sale_reference_id = self.request.POST['SaleReferenceId']
            card_number = self.request.POST['CardHolderPan']

            # TODO Important: If SaleOrderId already exists in DB, payment is not valid

            # TODO If SaleOrderId does not exist in DB, continue to verifying the payment
            try:
                client = zeep.Client(wsdl='https://bpm.shaparak.ir/pgwchannel/services/pgw?wsdl')
                res = client.service.bpVerifyRequest(terminalId=int(self.terminal_id),
                                                     userName=self.username,
                                                     userPassword=self.password,
                                                     orderId=999999,  # orderId from DB
                                                     saleOrderId=sale_order_id,
                                                     saleReferenceId=int(sale_reference_id))
                if str(res) == '0':
                    res = client.service.bpSettleRequest(terminalId=int(self.terminal_id),
                                                         userName=self.username,
                                                         userPassword=self.password,
                                                         orderId=999999,  # orderId from DB
                                                         saleOrderId=sale_order_id,
                                                         saleReferenceId=int(sale_reference_id))
                    if str(res) == '0':
                        # Payment has been verified successfully
                        # TODO Send user to successful payment page
                        pass
                    else:
                        error_message = self.status_code_mapper[str(res)]
                else:
                    client.service.bpReversalRequest(terminalId=int(self.terminal_id),
                                                     userName=self.username,
                                                     userPassword=self.password,
                                                     orderId=999999,  # orderId from DB
                                                     saleOrderId=sale_order_id,
                                                     saleReferenceId=int(sale_reference_id))
                    error_message = self.status_code_mapper[str(res)]
                    # Payment verification failed
            except:
                pass
        else:
            pass

        # TODO Send user to failed payment page
