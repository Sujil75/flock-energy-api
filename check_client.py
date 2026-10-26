from app.clients.legacy_client import LegacyPortalClient

client = LegacyPortalClient()

print("Client created:", isinstance(client, LegacyPortalClient))
print("Base URL configured:", bool(client.base_url))
print("Session initialized:", client.session is not None)