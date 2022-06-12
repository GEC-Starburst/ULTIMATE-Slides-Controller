# ULTIMATE-Slides-Controller

Welcome to ULTIMATE Slides Controller!

We have the following three features that you can become the Presentation Master!

> Before using, run
> ```bash
> python -m pip install -r requirements.txt
> ```
> to install the dependencies!

## Earbuds Slides Control
```bash
python earbuds.py
```

While running, use your wireless earbuds's buttons to control your slides!

## Voice Slides Control

```bash
python voice.py
```

While running, you can say "Next" or "Back" to control your slides!

## Web Slides Control

To use web slides control, go to https://ngrok.com/ to get your AuthToken

```bash
python web.py [Ngrok AuthToken]
```

While running, go to http://localhost:5000, and click "Start Session" and share the link to others
Others can now use the web page to control your slides! 
