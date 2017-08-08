class AppDevSteps:
    def register_app(self, cert, sig):
        self.go_to_app_register()
        self.by_id('id_certificate').send_keys(cert)
        self.by_id('id_signature').send_keys(sig)
        self.by_id('id_signature').submit()
