import requests

from django.shortcuts import render, redirect
from django.http import HttpResponse

from theme.models import *
from gtravel import settings

def validate_dataset():
    LICENSE_VALIDATION_URL = "https://li.gandomteam.com/api/validate"
    domain_name = settings.ALLOWED_HOSTS
    if len(domain_name) > 1:
        return HttpResponse("only add on domain to allowed hosts")
    if domain_name == 'localhost' or domain_name == '127.0.0.1':
        return True
    try:
        response = requests.post(
            LICENSE_VALIDATION_URL,
            json={"domain": domain_name},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "not valid":
            return False
        if data.get("status") == "valid":
            return True
    except requests.exceptions.RequestException as e:
        return True