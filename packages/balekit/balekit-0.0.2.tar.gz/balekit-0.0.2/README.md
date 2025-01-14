## BaleKit
A tool for developing bots in Bale messenger!
## Quick Example
```python
from balekit import Bot
app = Bot("TOKEN")
msg = app.send_message("Hello World!")
c = msg["result"]["message_id"]
app.edit_message_text(1234567890,c, "Hello World!")
```
## Contact Us
- [Bale](https://ble.ir/mpmms)
- [Telegram](https://t.me/mpm_ms)
- [GitHub Issues](https://github.com/mpmms/balekit/issues)

## Installing

```bash
pip install balekit==
```