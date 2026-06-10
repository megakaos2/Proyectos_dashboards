import os

print("SOCRATA_TOKEN:", os.getenv("SOCRATA_TOKEN") is not None)
print("SOCRATA_USER:", os.getenv("SOCRATA_USER") is not None)
print("SOCRATA_PASSWORD:", os.getenv("SOCRATA_PASSWORD") is not None)
print("GOOGLE_CREDENTIALS_JSON:", os.getenv("GOOGLE_CREDENTIALS_JSON") is not None)
