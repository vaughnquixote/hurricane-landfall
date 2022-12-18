class Cyclone:

    def __init__(self, name, basin, cyclone_num, year, num_observations):
        self.name = name
        self.basin = basin
        self.cyclone_num = cyclone_num
        self.year = year
        self.locations = []
        self.landfall = False
        self.num_observations = num_observations
        self.observations = []

    def add_observation(self, observation_data):
        self.observations.append(observation_data)

    def get_max_wind_speed(self):
        max_wind_speed = 0
        for obs in self.observations:
            if obs.max_wind > max_wind_speed:
                max_wind_speed = obs.max_wind
        return max_wind_speed

class CycloneObservationData:

    def __init__(self, location, datetime, record_identifier, max_wind):
        self.location = location
        self.datetime = datetime
        self.record_identifier = record_identifier
        self.max_wind = max_wind