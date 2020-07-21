#!/bin/bash
pip freeze > requirements.txt
virtualenv .env && source .env/bin/activate && pip install -r requirements.txt
