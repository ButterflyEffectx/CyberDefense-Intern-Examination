from jose import jwt

token = jwt.encode(
    {"sub": "Joey", "role": "admin", "tenant": "demoA"},
    "changemeverystrongsecret",
    algorithm="HS256"
)

print(token)
