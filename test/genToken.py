from jose import jwt

token = jwt.encode(
    {"sub": "Johny", "role": "user", "tenant": "demoB"},
    "changemeverystrongsecret",
    algorithm="HS256"
)

print(token)
