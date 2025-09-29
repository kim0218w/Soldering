# Soldering
공학용캡스톤 디자인

Traceback (most recent call last):
  File "/home/pi/Desktop/soldering/nema.py", line 85, in <module>
    lgpio.gpio_claim_output(h, dir_pin, 0)
  File "/usr/lib/python3/dist-packages/lgpio.py", line 781, in gpio_claim_output
    return _u2i(_lgpio._gpio_claim_output(handle&0xffff, lFlags, gpio, level))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/lgpio.py", line 458, in _u2i
    raise error(error_text(v))
lgpio.error: 'GPIO busy'
