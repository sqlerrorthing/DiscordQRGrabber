# About
It's a python class where you pass a QR code that draws that qr and an instruction to "verify" it

# Preview
<img src="https://github.com/oneqxz/DiscordQRGrabber/blob/4ad09c3c59225d7f6cdfcb2f96aac29905cd53ce/preview.png">

# Uasge
!!! Download `assets` folder !!!
```python
qr = QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=170, border=2)
qr.add_data("lol data sql my sql lorem here >>> :#")
qr.make(fit=True)

drawable = Drawable(qr.make_image(fill='black', back_color="white"))
```
