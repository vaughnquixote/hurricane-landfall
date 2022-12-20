class Cyclone:
    """
    A class which represents a cyclone. 

    Attributes
    name (str): the name of the cyclone or UNNAMED 
    basin (str): the basin in which the cyclone was measured
    cyclone_num (str): the number cyclone for the year
    year (str): the year that the cyclone appeared
    landfall (bool): indicator of whether or not the hurricane made landfall
    num_observations (int): the number of observations made of the cyclone
    observations (lis[CycloneObservationData]): a list of observations 
        containing data about the cyclone at a given time such as location
        and maximum wind speed
    """

    def __init__(self, name, basin, cyclone_num, year, num_observations):
        """
        construct the object based on passed in data and with a couple of
        default values
        """
        self.name = name
        self.basin = basin
        self.cyclone_num = cyclone_num
        self.year = year
        self.landfall = False
        self.num_observations = num_observations
        self.observations = []

    def add_observation(self, observation_data):
        """
        Add an observation to the cyclones list of observations. 

        Params:
        observation_data (CycloneObservationData): the observation
        
        Returns:
        none
        """
        self.observations.append(observation_data)

    def get_max_wind_speed(self):
        """
        Get the maximum wind speed of the cyclone based on the observation
        data stored on the object. 

        Params:
        None

        Returns:
        max_wind_speed (int): the maximum wind speed recorded for the cyclone
        """
        max_wind_speed = 0
        for obs in self.observations:
            if obs.max_wind > max_wind_speed:
                max_wind_speed = obs.max_wind
        return max_wind_speed

class CycloneObservationData:
    """
    A class made to store data from the observation of a hurricane.

    Attributes:
    location (shapely.Point): a point representing the geographic location
        of the cyclone
    datetime (datetime.datetime): the date and time that the observation was
       recorded
    record_identifier (str): an identifier which can indicate that a cyclone 
        made landfall among other things
    max_wind (int): the maximum wind speed recorded at this observation
    """
    def __init__(self, location, datetime, record_identifier, max_wind):
        self.location = location
        self.datetime = datetime
        self.record_identifier = record_identifier
        self.max_wind = max_wind