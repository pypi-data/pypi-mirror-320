from yta_general_utils.math.value_normalizer import ValueNormalizer
from yta_general_utils.math.rate_functions import RateFunction
from yta_general_utils.programming.parameter_validator import NumberValidator

import numpy as np


class Progression:
    """
    Class to represent a progression, which is a list of
    values between two limits and a number of steps, with
    also an associated rate function to calculate those
    steps in between.

    This class is useful to obtain each individual value
    that must be applied in different use cases.
    """
    _start: float = None
    _end: float = None
    _n_between_limits: float = None
    _values: list[float] = None
    """
    The amount of values that will exist in between the
    lower and the upper limit. A progression with 0 steps
    will be as simple as [lower_limit, upper_limit].
    """
    _rate_function: callable = None
    """
    The function to calculate the steps in between the
    lower and upper limit.
    """

    @property
    def values(self):
        """
        The list of 'start', 'n' and 'end' values according to
        the provided 'rate_function' provided.
        """
        if self._values is None:
            values = [
                ValueNormalizer(self.start, self.end).denormalize(normalized_value)
                for normalized_value in Progression.get_n_normalized_values(self.n, self.rate_function)
            ]

            # If limits are switched, we need to adjust it
            values = [self.end - value for value in values] if self.start > self.end else values

            self._values = values

        return self._values

    @property
    def start(self):
        """
        The first value of the progression, that acts as a limit.
        """
        return self._start
    
    @start.setter
    def start(self, value: float):
        if not NumberValidator.is_number(value):
            raise Exception('The provided "start" value is not a number.')

        self._values = None
        self._start = value

    @property
    def end(self):
        """
        The last value of the progression, that acts as a limit.
        """
        return self._end
    
    @end.setter
    def end(self, value: float):
        if not NumberValidator.is_number(value):
            raise Exception('The provided "end" value is not a number.')
        
        self._values = None
        self._end = value

    @property
    def n(self):
        """
        The amount of expected values between 'start' and 'end'.
        """
        return self._n
    
    @n.setter
    def n(self, value: int):
        """
        The amount of expected values between 'start' and 'end'.
        """
        if not NumberValidator.is_positive_number(value) or not NumberValidator.is_int(value):
            raise Exception('The provided "n" value must be a positive and int value.')
        
        self._values = None
        self._n = value

    @property
    def rate_function(self):
        """
        The rate function that will be applied to calculate
        the 'n' values between 'start' and 'end'.
        """
        return self._rate_function
    
    @rate_function.setter
    def rate_function(self, value: RateFunction):
        # TODO: Validate rate function

        self._values = None
        self._rate_function = value

    def __init__(self, start: float, end: float, n: int, rate_function: callable = RateFunction.linear):
        # TODO: Validate, please

        self._start = start
        self._end = end
        self._n = n
        self._rate_function = rate_function
        self._values = None

    # def get_n_values(self):
    #     """
    #     Get 'n' values between the provided 'lower_limit' and
    #     'upper_limit' resulting in a list of n+2 values. This
    #     method will use the provided 'rate_function' to 
    #     calculate those values.

    #     I will give one example with [10, 20] range and n = 4
    #     values:
    #     - Ease_in_quad r.f. normalized: [0.0, 0.04, 0.16, 0.36, 0.64, 1.0]
    #     - Ease_in_quad r.f. denormalized values: [10, 10.4, 11.6, 13.6, 16.4, 20]
    #     """
    #     # Apply the rate function to those values
    #     # TODO: Apply the provided 'rate_function'
    #     # TODO: Validate that 'rate_function' is a method of 
    #     # RateFunction class (?)
    #     self._rate_function = RateFunction.linear

    #     # Denormalize values to the range defined by limits
    #     denormalized_values = [
    #         ValueNormalizer(self.start, self.end).denormalize(normalized_value)
    #         for normalized_value in Progression.get_n_normalized_values(self.steps, rate_function)
    #     ]

    #     return denormalized_values
    
    @staticmethod
    def get_n_equally_distributed_normalized_values(n: int):
        """
        Get a list containing 0.0 and 1.0 limits and 'n'
        equally distributed (and normalized) values in 
        between those limits.

        If n = 4:
        - [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        """
        if not NumberValidator.is_positive_number(n):
            raise Exception('The provided "n" parameter is not a positive number.')

        return [0.0] + (np.linspace(0.0, 1.0, n).tolist() if n > 0 else []) + [1.0]

    @staticmethod
    def get_n_normalized_values(n: int, rate_function: callable = RateFunction.linear):
        """
        Get a list containing 0.0 and 1.0 limits and 'n'
        values in between those limits according to the
        provided 'rate_function'.

        If n = 4 and rate_function = ease_in_quad:
        - [0.0, 0.04, 0.16, 0.36, 0.64, 1.0]
        """
        if not NumberValidator.is_positive_number(n):
            raise Exception('The provided "n" parameter is not a positive number.')
        
        # TODO: Apply the provided 'rate_function'
        # TODO: Validate that 'rate_function' is a method of 
        # RateFunction class (?)
        rate_function = RateFunction.linear

        return [
            rate_function(normalized_value)
            for normalized_value in Progression.get_n_equally_distributed_normalized_values(n)
        ]
    
# TODO: I think I can improve the RateFunction class to include
# some of this functionality, or maybe mix it, to be able to
# obtain a list of 'n' equally distributed normalized values or
# similar, and also improve the GraphicInterpolation that is
# using a normalizer function that is not actually the new
# ValueNormalizer class which includes the limits to work
# properly...