# uk_police

## Overview
uk_police is a Python wrapper for the UK Police API, providing an easy-to-use interface to access and interact with police data such as street-level crimes, outcomes, neighbourhoods, and stop-and-search activities. This readme.md is generated through ChatGPT for now, please forgive errors.

## Features
- Retrieve street-level crimes at specific locations or within custom areas.
- Fetch crime outcomes by coordinates, location, or area.
- Access information about neighbourhoods, including teams, events, and boundaries.
- Perform stop-and-search queries by area, force, or location.
- List and get details of police forces.
- Obtain metadata, such as available crime categories and the last updated date for the data.

## Requirements
- Python 3.7 or later
- `requests`

## Usage

uk_police is split between 4 sections
- Street level crimes
- Neighbourhood
- Stop and search
- Police force

this is an example to find specific info:

```python
import uk_police

# Step 1: Locate the neighbourhood for specific coordinates
neighbourhood_info = uk_police.neighbourhoods.locate_neighbourhood(latitude=52.629729, longitude=-1.131592)
force_id = neighbourhood_info['force']
neighbourhood_id = neighbourhood_info['neighbourhood']

# Step 2: Get detailed information about the neighbourhood
neighbourhood_details = uk_police.neighbourhoods.get_neighbourhood_details(force_id=force_id, neighbourhood_id=neighbourhood_id)
print("Neighbourhood Details:", neighbourhood_details)

# Step 3: Fetch street-level crimes in the neighbourhood area
polygon = "52.268,0.543:52.794,0.238:52.130,0.478"  # Replace with actual boundary data if available
crimes = uk_police.street_level.get_street_crimes_in_area(poly=polygon, date="2023-12")
print("Crimes in Area:", crimes)

# Step 4: Retrieve outcomes for crimes near the specified coordinates
outcomes = uk_police.street_level.get_outcomes_by_coordinates(lat=52.629729, lng=-1.131592, date="2023-12")
print("Crime Outcomes:", outcomes)
```

## Methods

Below are all methods in the api

### Street Level Crimes

Methods relating to Street Level Crime:

#### Fetching Crimes at a Specific Location
```python
import uk_police

crimes = uk_police.street_level.get_street_crimes_at_location(lat=52.629729, lng=-1.131592)
print(crimes)
```

#### Fetching Crimes in a Custom Area
```python
import uk_police

polygon = "52.268,0.543:52.794,0.238:52.130,0.478"
crimes = uk_police.street_level.get_street_crimes_in_area(poly=polygon)
print(crimes)
```

#### Fetching Outcomes at a Specific Location
```python
import uk_police

outcomes = uk_police.street_level.get_outcomes_at_location(location_id="12345", date="2023-12")
print(outcomes)
```

#### Fetching Outcomes by Coordinates
```python
import uk_police

outcomes = uk_police.street_level.get_outcomes_by_coordinates(lat=52.629729, lng=-1.131592, date="2023-12")
print(outcomes)
```

#### Fetching Outcomes in a Custom Area
```python
import uk_police

polygon = "52.268,0.543:52.794,0.238:52.130,0.478"
outcomes = uk_police.street_level.get_outcomes_in_area(poly=polygon)
print(outcomes)
```

#### Fetching Crimes at a Specific Location by ID or Coordinates
```python
import uk_police

# Fetch by location ID
crimes = uk_police.street_level.get_crimes_at_specific_location(location_id="12345")
print(crimes)

# Fetch by coordinates
crimes = uk_police.street_level.get_crimes_at_specific_location(lat=52.629729, lng=-1.131592)
print(crimes)
```

#### Fetching Crimes with No Location
```python
import uk_police

crimes = uk_police.street_level.get_crimes_no_location(category="all-crime", force="leicestershire", date="2023-12")
print(crimes)
```

#### Fetching Crime Categories
```python
import uk_police

categories = uk_police.street_level.get_crime_categories(date="2023-12")
print(categories)
```

#### Fetching Last Updated Date
```python
import uk_police

last_updated = uk_police.street_level.get_last_updated()
print(last_updated)
```

#### Fetching Outcomes for a Specific Crime
```python
import uk_police

crime_id = "e11dade0a92a912d12329b9b2abb856ac9520434ad6845c30f503e9901d140f1"
outcomes = uk_police.street_level.get_outcomes_for_crime(crime_id=crime_id)
print(outcomes)
```
### Fetching Neighbourhood Details

Methods relating to neighbourhoods:

#### Listing Neighbourhoods for a Force
```python
import uk_police

neighbourhoods = uk_police.neighbourhoods.list_neighbourhoods(force_id="leicestershire")
print(neighbourhoods)
```

#### Fetching Neighbourhood Details
```python
import uk_police

details = uk_police.neighbourhoods.get_neighbourhood_details(force_id="leicestershire", neighbourhood_id="12345")
print(details)
```

#### Fetching Neighbourhood Boundary
```python
import uk_police

boundary = uk_police.neighbourhoods.get_neighbourhood_boundary(force_id="leicestershire", neighbourhood_id="12345")
print(boundary)
```

#### Fetching Neighbourhood Team Members
```python
import uk_police

team = uk_police.neighbourhoods.get_neighbourhood_team(force_id="leicestershire", neighbourhood_id="12345")
print(team)
```

#### Fetching Neighbourhood Events
```python
import uk_police

events = uk_police.neighbourhoods.get_neighbourhood_events(force_id="leicestershire", neighbourhood_id="12345")
print(events)
```

#### Fetching Neighbourhood Priorities
```python
import uk_police

priorities = uk_police.neighbourhoods.get_neighbourhood_priorities(force_id="leicestershire", neighbourhood_id="12345")
print(priorities)
```

#### Locating Neighbourhood by Coordinates
```python
import uk_police

location = uk_police.neighbourhoods.locate_neighbourhood(latitude=52.629729, longitude=-1.131592)
print(location)
```

### Stop and Search

Methods relating to stop and search: 

#### Stop and Search by Area
```python
import uk_police

# By latitude and longitude
stops = uk_police.stop_search.stop_and_search_by_area(lat=52.629729, lng=-1.131592, date="2023-12")
print(stops)

# By polygon
polygon = "52.268,0.543:52.794,0.238:52.130,0.478"
stops = uk_police.stop_search.stop_and_search_by_area(poly=polygon, date="2023-12")
print(stops)
```

#### Stop and Search by Location
```python
import uk_police

stops = uk_police.stop_search.stop_and_search_by_location(location_id="12345", date="2023-12")
print(stops)
```

#### Stop and Search with No Location
```python
import uk_police

stops = uk_police.stop_search.stop_and_search_no_location(force="leicestershire", date="2023-12")
print(stops)
```

#### Stop and Search by Force
```python
import uk_police

stops = uk_police.stop_search.stop_and_search_by_force(force="leicestershire", date="2023-12")
print(stops)
```

### Fetching Police Force Details

Methods relating to Forces:

#### Listing All Police Forces
```python
import uk_police

forces = uk_police.forces.list_forces()
print(forces)
```

#### Fetching Details of a Specific Police Force
```python
import uk_police

details = uk_police.forces.get_force_details(force_id="leicestershire")
print(details)
```

#### Fetching Senior Officers of a Specific Police Force
```python
import uk_police

officers = uk_police.forces.get_senior_officers(force_id="leicestershire")
print(officers)
```

## Validation
uk_police provides built-in validation for inputs:
- Latitude and longitude are validated to ensure they fall within valid ranges.
- Polygon strings for custom areas are checked for proper formatting.

## Rate Limiting

The UK Police API enforces a rate limit of 15 requests per second, with a burst of 30 requests allowed. If the rate limit is exceeded, the API responds with a `429 Too Many Requests` error.

`uk-police` handles this automatically by:
1. Raising a `RateLimitError` when the limit is exceeded.
2. Including the `Retry-After` value (if provided) in the exception.
3. Retrying the request up to 3 times before failing.

You can configure the retry behavior by using the `max_retries` parameter.

## Acknowledgements
This project relies on the [UK Police API](https://data.police.uk/docs/) for data access and services.