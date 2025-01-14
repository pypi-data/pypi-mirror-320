"""
THIS IS VERY IMPORTANT TO UNDERSTAND THE CODE:

- First of all, the distance. Imagine the map
once it's been plotted. If you go from the origin
to the end, there is a distance you are virtually
drawing. That is the global distance. The distance
from the origin, normalized, is d=1.0. The origin
is d=0.0 and the end is d=1.0.

- As you are using pairs of coordinates, there is
also a local distance in between each pair of
coordinates. Imagine, for a second, that each pair
of coordinates is a map by itself. The first 
coordinate is the d=0.0 and the second coordinate
is the d=1.0 (in local distance terms).

- If you have, for example, 5 pairs of coordinates,
as the total global distance is d=1.0, each pair of
coordinates will represent a 1/5 of that total
global distance, so each pair of coordinates 
local distance is a 1/5 = 0.2 of the total global
distance. Knowing that, in order, the pairs of
coordinates represent the global distance as
follows: [0.0, 0.2], (0.2, 0.4], (0.4, 0.6],
(0.6, 0.8] and (0.8, 1.0] (for the same example
with 5 pairs of coordinates).

- Now that you have clear the previous steps, if
you think about a global distance of d=0.3, that
will be in the second pair of coordinates (the
one that represents (0.2, 0.4] range. But that
d=0.3 is in terms of global distance, so we need
to adapt it to that pair of coordinates local
distance. As we skipped 1 (the first) pair of
coordinates, we need to substract its distance
representation from our global distance, so
d=0.3 - 0.2 => d=0.1. Now, as d=0.1 is a global
distance value, we need to turn it into a local
distance value. As each pair of coordinates
represents a 0.2 of the global distance, we do
this: d=0.1 / 0.2 => d=0.5 and we obtain a local
distance of d=0.5. That is the local distance
within the second pair of coordinates (in this
example) we need to look for.

- Once we know the local distance we need to 
look for, as we now the pair of coordinates X
value of each of those coordinates, we can 
calculate the corresponding X value for what
that local distance fits.

As you can see, we go from a global distance to
a local X value to obtain the corresponding Y
of the affected pair of coordinates. This class
has been created with the purpose of following
a movement, so the distance we are talking about
is actually the amount of that movement we have
done previously so we can obtain the next 
position to which we need to move to follow the
movement that this map describes.
"""
from yta_general_utils.coordinate.coordinate import Coordinate, validate_coordinate_position
from yta_general_utils.math.map.pair_of_coordinates import PairOfCoordinates
from yta_general_utils.programming.parameter_validator import NumberValidator
from typing import Union


# TODO: I think this is not actually a Map so the
# class name should change as it is more a Movement
# graphic and the Graphic class is an Animation
# Graphic or something like that
class Map:
    """
    A class to represent an scenario in which we will
    position Coordinates. The order of the coordinates
    will determine the direction of the movement, and
    they can be disordered (the next coordinate can be
    in a lower X and Y position). Also, there can be
    different coordinates in the same position.

    This is useful to simulate the movement within a
    scene.
    """
    coordinates: list[Coordinate] = None

    @property
    def pairs_of_coordinates(self) -> list[PairOfCoordinates]:
        """
        Get pairs of coordinates ordered by the moment in which
        they were added to the map. There is, at least, one pair
        of coordinates that will be, if no more coordinates
        added, the first and the last one.
        """
        return [
            PairOfCoordinates(self.coordinates[index], self.coordinates[index + 1])
            for index, _ in enumerate(self.coordinates[1:])
        ]

    def __init__(self):
        self.coordinates = []

    def add_coordinate(self, position: Union[tuple[float, float], list[float, float]]):
        """
        Add a new coordinate to the map if valid. The
        coordinate added can be in the same position as
        another coordinate.
        
        This method returns the instance so you can chain
        more than one 'add_coordinate' method call.
        """
        validate_coordinate_position(position)

        self.coordinates.append(Coordinate(position))

        return self
    
    def _get_x_from_normalized_d(self, d: float):
        """
        Obtain the not normalized X value for the given
        'd' global distance value, that is a normalized
        value between 0.0 and 1.0. The X value of the first
        coordinate in the graphic would be d=0.0 and
        the X value of the last coordinate the d=1.0.

        In the map, the distance from the first X to the
        last X is d=1.0. The map can contain more than 
        one pair of coordinates, so the provided 'd' will
        refer to a local distance within a pair of
        coordinates.

        If a map contains 5 pairs of coordinates, as the
        global distance is d=1.0, each pair of coordinates
        represents a d=0.2. First pair of coordinates from
        [0.0, 0.2], second pair (0.2, 0.4], etc. So,
        if a global distance d=0.3 is requested, the
        second pair of coordinates (in the example below) 
        will be used to calculate its X and the 
        corresponding Y value.
        """
        if not NumberValidator.is_number_between(d, 0.0, 1.0):
            raise Exception(f'The provided "d" parameter "{str(d)}" must be between 0.0 and 1.0, both inclusive.')
        
        # 'd' is the distance within the whole map
        # representation with a value between [0.0, 1.0]
        num_of_pairs_of_coordinates = len(self.pairs_of_coordinates)
        # This is the distance that each pair of coordinates
        # is representing (also between [0.0, 1.0]). As a
        # reminder, if 5 pairs of coordinates, 1.0 / 5 = 0.2,
        # so each pair of coordinates would be representing
        # a 0.2 portion of the whole map distance.
        pair_of_coordinates_d = 1 / num_of_pairs_of_coordinates
        # Same example as above, 5 pairs of coordinates:
        # d = 0.2 // 0.2 = index 1 which is for the 2nd pair
        # d = 0.3 // 0.2 = index 1 which is for the 2nd pair
        # d = 0.7 // 0.2 = index 3 which is for the 4th pair
        # TODO: Maybe let the last value (exact, so % = 0) for
        # the previous pair instead of for the next one (?)
        pair_of_coordinates_index = int(d // pair_of_coordinates_d) if d != 1.0 else num_of_pairs_of_coordinates - 1
        pair_of_coordinates = self.pairs_of_coordinates[pair_of_coordinates_index]

        # If d=0.3, we will use the 2nd pair of coordinates,
        # but, as we skipped the first pair of coordinates, we
        # need to substract the corresponding amount, so
        # d=0.3 - 0.2 => d=0.1. Now, working locally in the
        # 2nd pair of coordinates, we are looking for the d=0.1,
        # which is a general distance that we need to turn into
        # a local one. As the pair of coordinates is representing
        # a total of 0.2d of the total map distance, that d=0.1
        # represents the 0.5 in the local distance of that pair
        # of coordinates:
        # d=0.2 = d=1.0 locally => 0.1 * 1 / 0.2 = 0.1 / 0.2 = 0.5
        # so the 10% (0.1d) in global terms means a 50% (0.5d) in
        # local pair of coordinates terms.
        # Formula explained with the same example below:
        # X = 0.3 % (1 * 0.2) / 0.2
        # X = 0.3 % 0.2 / 0.2
        # X = 0.1 / 0.2
        # X = 0.5
        d = d % (pair_of_coordinates_index * pair_of_coordinates_d) / pair_of_coordinates_d if pair_of_coordinates_index > 0 else d
        # Now we need to ask the pair of nodes to calculate the Y
        # position of the X that is in the 'd' local distance:
        # y = min_x + d * (max_x - min_x)
        # I give a pair of examples below with coordinates from 
        # left to right and from right to left:
        # c1(300, y), c2(400, y), d=0.6
        # 300 + 0.6 * (400 - 300) = 300 + 0.6 * 100 = 300 + 60 = 360
        # c1(400, y), c2(300, y), d=0.6
        # 400 + 0.6 * (300 - 400) = 400 + 0.6 * (-100) = 400 + (-60) = 340
        x = pair_of_coordinates.first_coordinate.x + d * (pair_of_coordinates.second_coordinate.x - pair_of_coordinates.first_coordinate.x)

        return x