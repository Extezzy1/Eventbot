from yoomoney import Quickpay, Client
from random import randrange

import config


class Payment:

    def __init__(self, yoomoney_wallet, yoomoney_token):
        self.yoomoney_wallet = yoomoney_wallet
        self.yoomoney_token = yoomoney_token

    def create_payment(self, amount):
        bill = ''
        for i in range(9):
            bill += '1234567890aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ'[randrange(0, 62)]
        print(bill)
        quickpay = Quickpay(
                receiver=self.yoomoney_wallet,
                quickpay_form='shop',
                targets='Bot',
                paymentType='SB',
                sum=amount,
                label=bill
            )
        try:
            url = quickpay.redirected_url
        except KeyError:
            url = 'Error'
        return url, bill

    def check_payment(self, bill):
        client = Client(self.yoomoney_token)
        history = client.operation_history(label=bill)
        for operation in history.operations:
            if operation.label == bill:
                if operation.status == 'success':
                    return 'Оплачено'
                elif operation.status == 'in_progress':
                    return 'Ожидает оплаты'
                else:
                    return '?'
