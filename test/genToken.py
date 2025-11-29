from jose import jwt

token = jwt.encode(
    {"sub": "Test", "role": "user", "tenant": "demoC"},
    "changemeverystrongsecret",
    algorithm="HS256"
)

print(token)
