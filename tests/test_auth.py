from app.core.security import verify_password

print(verify_password(
    "SecurePass123!",
    "$2b$12$ZCA99HgNL2j/iD3uYOf0teNOeto0EteEqSndYIgZJkGr0Ol0w9JX2"
))