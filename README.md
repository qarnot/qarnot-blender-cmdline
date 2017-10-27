# Qarnot Blender Cmdline

Launch Blender renders on Qarnot [Render](https://render.qarnot.com) as if you were rendering locally!

# Requirements

You need a Qarnot [Render](https://render.qarnot.com) account and Qarnot Python SDK available on [Github](https://github.com/qarnot/qarnot-sdk-python) or [Pypi](https://pypi.python.org/pypi/qarnot/).

Rename `qarnot.conf.sample` to `qarnot.conf` and input your private token that you can find in your [account](https://account.qarnot.com)

# Usage

Use the `qarnot-blender.py` script with Blender usual arguments

```bash
./qarnot-blender.py --factory-startup -b files/qarnot.blend -a --frame-start 10 --frame-end 20
```

# Coming soon

* Windows version
* Automatic range / frame detection
* More Blender options support
