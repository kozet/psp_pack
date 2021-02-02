class PaymentServiceProvider:
    def __init__(self, request):
        self.request = request

    def send(self):
        """
            send user to bank
        """
        raise NotImplementedError("Couldn't find send method.")

    def verify(self):
        """
            verify payment
        """
        raise NotImplementedError("Couldn't find verify method.")
