# Garage61Api

Simple Python wrapper around the Garage61 API.

# Install

`pip install garage61api`

# Usage

```
from garage61api.client import Garage61Client

g61 = Garage61Client(token="YOUR_ACCESS_TOKEN")
print(g61.me())
```

# Endpoints
### General information
- **.me** - Information about the currently authenticated user.
- **.me_accounts** - Get linked accounts for the current user.
- **.me_statistics** - Get personal driving statistics.
- **.teams** - Joined teams or information about a specific team and statistics.
### Content
- **.car_groups** - Available car groups.
- **.cars** - Available cars.
- **.platforms** - Available platforms.
- **.tracks** - Available tracks.
### Driving data
- **.laps** - Find laps and lap records and information about a specific lap.
- **.lap_csv** - Export the telemetry for a lap as a CSV file.

# Documentation

[Garage61 API](https://de.garage61.net/developer)

[GitHub](https://github.com/KuzmaLesnoy/garage61api)

Docstrings