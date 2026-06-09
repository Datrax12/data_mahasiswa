# TODO

- [x] Add route `/resend-otp` in app.py to regenerate and resend OTP to registered email, then redirect to `/verify`.
- [x] Update `templates/verify_otp.html` to include button/form for "Kirim ulang kode OTP" that submits to `/resend-otp` and stays on `/verify`.
- [ ] Test flow: register -> verify -> resend -> submit new OTP.


