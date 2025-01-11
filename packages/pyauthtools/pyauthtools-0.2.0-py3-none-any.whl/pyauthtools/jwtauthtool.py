import jwt
from datetime import datetime, timedelta
from flask import request, abort, render_template, Flask, redirect, make_response, session, url_for
import os
from dotenv import load_dotenv


load_dotenv()
JWT_ALG = 'HS256' if not os.getenv('JWT_ALG') else os.getenv('JWT_ALG')
JWT_PUBLIC = os.getenv('JWT_PUBLIC')
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_AUTH_SERVICE = os.getenv('JWT_AUTH_SERVICE')


def encode(payload):
  headers = {
    "alg": JWT_ALG,
    "typ": "JWT"
  }
  payload.update({    # payload
    "exp": datetime.utcnow() + timedelta(days=1)
  })
  try:
    token = jwt.encode(payload, JWT_SECRET, JWT_ALG, headers=headers)
    return token
  except Exception as e:
    return e
  
def decode(token):
  try:
    if JWT_ALG == 'HS256':
      decoded = jwt.decode(token, JWT_SECRET, JWT_ALG)
    elif JWT_ALG == 'RS256':
      decoded = jwt.decode(token, JWT_PUBLIC, algorithms='RS256')
    return decoded
  except:
    return 'err'
  
  
def auth(func):
  def validate_auth(*args, **kwargs):
    try:
      url = request.url
      headers = request.headers
      token = request.args['auth']
      if not token:
        print(f'pyauthtools.auth, url: {url}, headers: {headers}')
        token = headers.get('Authorization').split(' ')[1]
      result = decode(token)
      if result == 'err':
        return redirect(f'http://{JWT_AUTH_SERVICE}/login?url={url}')
      return func(*args, **kwargs)
    except Exception as e:
      return redirect(f'http://{JWT_AUTH_SERVICE}/login?url={url}')
  return validate_auth
  
  
  
# secret = 'a2c4e6f8'
# encoded = encode({"some": "payload"}, secret, algorithm="HS256")
# print(decode(encoded, secret, algorithm="HS256"))

  
# private_key = b"-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAwhvqCC+37A+UXgcvDl+7nbVjDI3QErdZBkI1VypVBMkKKWHM\nNLMdHk0bIKL+1aDYTRRsCKBy9ZmSSX1pwQlO/3+gRs/MWG27gdRNtf57uLk1+lQI\n6hBDozuyBR0YayQDIx6VsmpBn3Y8LS13p4pTBvirlsdX+jXrbOEaQphn0OdQo0WD\noOwwsPCNCKoIMbUOtUCowvjesFXlWkwG1zeMzlD1aDDS478PDZdckPjT96ICzqe4\nO1Ok6fRGnor2UTmuPy0f1tI0F7Ol5DHAD6pZbkhB70aTBuWDGLDR0iLenzyQecmD\n4aU19r1XC9AHsVbQzxHrP8FveZGlV/nJOBJwFwIDAQABAoIBAFCVFBA39yvJv/dV\nFiTqe1HahnckvFe4w/2EKO65xTfKWiyZzBOotBLrQbLH1/FJ5+H/82WVboQlMATQ\nSsH3olMRYbFj/NpNG8WnJGfEcQpb4Vu93UGGZP3z/1B+Jq/78E15Gf5KfFm91PeQ\nY5crJpLDU0CyGwTls4ms3aD98kNXuxhCGVbje5lCARizNKfm/+2qsnTYfKnAzN+n\nnm0WCjcHmvGYO8kGHWbFWMWvIlkoZ5YubSX2raNeg+YdMJUHz2ej1ocfW0A8/tmL\nwtFoBSuBe1Z2ykhX4t6mRHp0airhyc+MO0bIlW61vU/cPGPos16PoS7/V08S7ZED\nX64rkyECgYEA4iqeJZqny/PjOcYRuVOHBU9nEbsr2VJIf34/I9hta/mRq8hPxOdD\n/7ES/ZTZynTMnOdKht19Fi73Sf28NYE83y5WjGJV/JNj5uq2mLR7t2R0ZV8uK8tU\n4RR6b2bHBbhVLXZ9gqWtu9bWtsxWOkG1bs0iONgD3k5oZCXp+IWuklECgYEA27bA\n7UW+iBeB/2z4x1p/0wY+whBOtIUiZy6YCAOv/HtqppsUJM+W9GeaiMpPHlwDUWxr\n4xr6GbJSHrspkMtkX5bL9e7+9zBguqG5SiQVIzuues9Jio3ZHG1N2aNrr87+wMiB\nxX6Cyi0x1asmsmIBO7MdP/tSNB2ebr8qM6/6mecCgYBA82ZJfFm1+8uEuvo6E9/R\nyZTbBbq5BaVmX9Y4MB50hM6t26/050mi87J1err1Jofgg5fmlVMn/MLtz92uK/hU\nS9V1KYRyLc3h8gQQZLym1UWMG0KCNzmgDiZ/Oa/sV5y2mrG+xF/ZcwBkrNgSkO5O\n7MBoPLkXrcLTCARiZ9nTkQKBgQCsaBGnnkzOObQWnIny1L7s9j+UxHseCEJguR0v\nXMVh1+5uYc5CvGp1yj5nDGldJ1KrN+rIwMh0FYt+9dq99fwDTi8qAqoridi9Wl4t\nIXc8uH5HfBT3FivBtLucBjJgOIuK90ttj8JNp30tbynkXCcfk4NmS23L21oRCQyy\nlmqNDQKBgQDRvzEB26isJBr7/fwS0QbuIlgzEZ9T3ZkrGTFQNfUJZWcUllYI0ptv\ny7ShHOqyvjsC3LPrKGyEjeufaM5J8EFrqwtx6UB/tkGJ2bmd1YwOWFHvfHgHCZLP\n34ZNURCvxRV9ZojS1zmDRBJrSo7+/K0t28hXbiaTOjJA18XAyyWmGg==\n-----END RSA PRIVATE KEY-----\n"
# public_key = b"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwhvqCC+37A+UXgcvDl+7\nnbVjDI3QErdZBkI1VypVBMkKKWHMNLMdHk0bIKL+1aDYTRRsCKBy9ZmSSX1pwQlO\n/3+gRs/MWG27gdRNtf57uLk1+lQI6hBDozuyBR0YayQDIx6VsmpBn3Y8LS13p4pT\nBvirlsdX+jXrbOEaQphn0OdQo0WDoOwwsPCNCKoIMbUOtUCowvjesFXlWkwG1zeM\nzlD1aDDS478PDZdckPjT96ICzqe4O1Ok6fRGnor2UTmuPy0f1tI0F7Ol5DHAD6pZ\nbkhB70aTBuWDGLDR0iLenzyQecmD4aU19r1XC9AHsVbQzxHrP8FveZGlV/nJOBJw\nFwIDAQAB\n-----END PUBLIC KEY-----\n"
# encoded = encode({"some": "payload"}, private_key, algorithm="RS256")
# print(decode(encoded, public_key, algorithm="RS256"))

