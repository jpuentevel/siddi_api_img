#!/bin/bash
gunicorn -b 0.0.0.0:$PORT -w 4 app:app