# PyAuthTools

Some auth tools using in python flask.

## Surpported Algorisms
HS256

RS256


## Install
```pip
pip install pyauthtools
```

## Environments
```env
JWT_ALG = 'HS256'   # or 'RS256'
JWT_PUBLIC = b'xxx' # when RS256
JWT_SECRET = b'xxx' # pri_key or secret
```

## Usages
```python
@app.route('/index', methods=['POST', 'GET'])
@auth    # Just above the func
def index():
  return rend_template('index.html')
```
