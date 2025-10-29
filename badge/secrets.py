# Update with your 2.4Ghz WiFi details
# Multiple WiFi networks can be defined - the system will attempt each in order
WIFI_NETWORKS = [
    {
        "ssid": "u25-badger-party",
        "password": "h4ck4w4y"
    },
    {
        "ssid": "Seaside inn Guest",
        "password": "Seasidesf1750"
    }
]

# Backward compatibility - use first network as default
WIFI_SSID = WIFI_NETWORKS[0]["ssid"]
WIFI_PASSWORD = WIFI_NETWORKS[0]["password"]

# Update with your GitHub username
GITHUB_USERNAME = "cyberious"