"""
This is an adaption of the rate functions found in manim
library for the moviepy library. I have to use lambda t
functions with the current frame time to be able to resize
or reposition a video, so I have adapted the manim rate
functions to be able to return a factor that, with specific
moviepy functions, will make a change with the factor that
has been calculated with the corresponding rate function.

You can see 'manim/utils/rate_functions.py'.

This is the way I have found to make it work and to be able
to build smoother animations. As manim docummentation says,
the rate functions have been inspired by the ones listed in
this web page: https://easings.net/

Thanks to:
- https://github.com/semitable/easing-functions/blob/master/easing_functions/easing.py
"""
from yta_general_utils.programming.enum import YTAEnum as Enum
from yta_general_utils.programming.parameter_validator import NumberValidator, PythonValidator
from yta_general_utils.math.value_normalizer import ValueNormalizer
from yta_general_utils.math import Math
from math import pow, sqrt
from typing import Callable, Iterable

import numpy as np


def linear(n: float) -> float:
    return n

def slow_into(n: float) -> float:
    return np.sqrt(1 - (1 - n) * (1 - n))

def smooth(n: float, inflection: float = 10.0) -> float:
    error = Math.sigmoid(-inflection / 2)

    return min(
        max((Math.sigmoid(inflection * (n - 0.5)) - error) / (1 - 2 * error), 0),
        1,
    )

def smooth_step(n: float) -> float:
    """
    Implementation of the 1st order SmoothStep sigmoid function.
    The 1st derivative (speed) is zero at the endpoints.
    https://en.wikipedia.org/wiki/Smoothstep
    """
    return 0 if n <= 0 else 3 * n**2 - 2 * n**3 if n < 1 else 1

def smoother_step(n: float) -> float:
    """
    Implementation of the 2nd order SmoothStep sigmoid function.
    The 1st and 2nd derivatives (speed and acceleration) are zero at the endpoints.
    https://en.wikipedia.org/wiki/Smoothstep
    """
    return 0 if n <= 0 else 6 * n**5 - 15 * n**4 + 10 * n**3 if n < 1 else 1

def smootherer_step(n: float) -> float:
    """
    Implementation of the 3rd order SmoothStep sigmoid function.
    The 1st, 2nd and 3rd derivatives (speed, acceleration and jerk) are zero at the endpoints.
    https://en.wikipedia.org/wiki/Smoothstep
    """
    alpha = 0
    if 0 < n < 1:
        alpha = 35 * n**4 - 84 * n**5 + 70 * n**6 - 20 * n**7
    elif n >= 1:
        alpha = 1

    return alpha

def rush_into(n: float, inflection: float = 10.0) -> float:
    return 2 * smooth(n / 2.0, inflection)

def rush_from(n: float, inflection: float = 10.0) -> float:
    return 2 * smooth(n / 2.0 + 0.5, inflection) - 1

def double_smooth(n: float) -> float:
    if n < 0.5:
        return 0.5 * smooth(2 * n)
    else:
        return 0.5 * (1 + smooth(2 * n - 1))
    
def there_and_back(n: float, inflection: float = 10.0) -> float:
    if n < 0.5:
        n = 2 * n
    else:
        n = 2 * (1 - n)

    return smooth(n, inflection)

def there_and_back_with_pause(n: float, pause_ratio: float = 1.0 / 3) -> float:
    a = 1.0 / pause_ratio
    if n < 0.5 - pause_ratio / 2:
        return smooth(a * n)
    elif n < 0.5 + pause_ratio / 2:
        return 1
    else:
        return smooth(a - a * n)
    
def running_start(n: float, pull_factor: float = -0.5) -> float:
    # TODO: This is being taken from manim, maybe copy (?)
    from manim.utils.bezier import bezier

    return bezier([0, 0, pull_factor, pull_factor, 1, 1, 1])(n)

def wiggle(n: float, wiggles: float = 2) -> float:
    # TODO: Manim says 'not_quite_there' function is not working
    return there_and_back(n) * np.sin(wiggles * np.pi * n)

def ease_in_cubic(n: float) -> float:
    return n * n * n

def ease_out_cubic(n: float) -> float:
    return 1 - pow(1 - n, 3)

# TODO: What is this (?)
def squish_rate_func(func: Callable[[float], float], a: float = 0.4, b: float = 0.6) -> Callable[[float], float]:
    def result(n: float):
        if a == b:
            return a

        if n < a:
            return func(0)
        elif n > b:
            return func(1)
        else:
            return func((n - a) / (b - a))

    return result

def lingering(n: float) -> float:
    return squish_rate_func(lambda n: n, 0, 0.8)(n)

def exponential_decay(n: float, half_life: float = 0.1) -> float:
    # The half-life should be rather small to minimize
    # the cut-off error at the end
    return 1 - np.exp(-n / half_life)

def ease_in_sine(n: float) -> float:
    return 1 - np.cos((n * np.pi) / 2)

def ease_out_sine(n: float) -> float:
    return np.sin((n * np.pi) / 2)

def ease_in_out_sine(n: float) -> float:
    return -(np.cos(np.pi * n) - 1) / 2

def ease_in_quad(n: float) -> float:
    return n * n

def ease_out_quad(n: float) -> float:
    return 1 - (1 - n) * (1 - n)

def ease_in_out_quad(n: float) -> float:
    return 2 * n * n if n < 0.5 else 1 - pow(-2 * n + 2, 2) / 2

def ease_in_out_cubic(n: float) -> float:
    return 4 * n * n * n if n < 0.5 else 1 - pow(-2 * n + 2, 3) / 2

def ease_in_quart(n: float) -> float:
    return n * n * n * n

def ease_out_quart(n: float) -> float:
    return 1 - pow(1 - n, 4)

def ease_in_out_quart(n: float) -> float:
    return 8 * n * n * n * n if n < 0.5 else 1 - pow(-2 * n + 2, 4) / 2

def ease_in_quint(n: float) -> float:
    return n * n * n * n * n

def ease_out_quint(n: float) -> float:
    return 1 - pow(1 - n, 5)

def ease_in_out_quint(n: float) -> float:
    return 16 * n * n * n * n * n if n < 0.5 else 1 - pow(-2 * n + 2, 5) / 2

def ease_in_expo(n: float) -> float:
    return 0 if n == 0 else pow(2, 10 * n - 10)

def ease_out_expo(n: float) -> float:
    return 1 if n == 1 else 1 - pow(2, -10 * n)

def ease_in_out_expo(n: float) -> float:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    elif n < 0.5:
        return pow(2, 20 * n - 10) / 2
    else:
        return (2 - pow(2, -20 * n + 10)) / 2
    
def ease_in_circ(n: float) -> float:
    return 1 - sqrt(1 - pow(n, 2))

def ease_out_circ(n: float) -> float:
    return sqrt(1 - pow(n - 1, 2))

def ease_in_out_circ(n: float) -> float:
    return (
        (1 - sqrt(1 - pow(2 * n, 2))) / 2
        if n < 0.5
        else (sqrt(1 - pow(-2 * n + 2, 2)) + 1) / 2
    )

def ease_in_back(n: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1

    return c3 * n * n * n - c1 * n * n

def ease_out_back(n: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1

    return 1 + c3 * pow(n - 1, 3) + c1 * pow(n - 1, 2)

def ease_in_out_back(n: float) -> float:
    c1 = 1.70158
    c2 = c1 * 1.525

    return (
        (pow(2 * n, 2) * ((c2 + 1) * 2 * n - c2)) / 2
        if n < 0.5
        else (pow(2 * n - 2, 2) * ((c2 + 1) * (n * 2 - 2) + c2) + 2) / 2
    )

def ease_in_elastic(n: float) -> float:
    c4 = (2 * np.pi) / 3
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return -pow(2, 10 * n - 10) * np.sin((n * 10 - 10.75) * c4)

def ease_out_elastic(n: float) -> float:
    c4 = (2 * np.pi) / 3
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return pow(2, -10 * n) * np.sin((n * 10 - 0.75) * c4) + 1
    
def ease_in_out_elastic(n: float) -> float:
    c5 = (2 * np.pi) / 4.5
    if n == 0:
        return 0
    elif n == 1:
        return 1
    elif n < 0.5:
        return -(pow(2, 20 * n - 10) * np.sin((20 * n - 11.125) * c5)) / 2
    else:
        return (pow(2, -20 * n + 10) * np.sin((20 * n - 11.125) * c5)) / 2 + 1
        
def ease_in_bounce(n: float) -> float:
    return 1 - ease_out_bounce(1 - n)

def ease_out_bounce(n: float) -> float:
    n1 = 7.5625
    d1 = 2.75

    if n < 1 / d1:
        return n1 * n * n
    elif n < 2 / d1:
        return n1 * (n - 1.5 / d1) * (n - 1.5 / d1) + 0.75
    elif n < 2.5 / d1:
        return n1 * (n - 2.25 / d1) * (n - 2.25 / d1) + 0.9375
    else:
        return n1 * (n - 2.625 / d1) * (n - 2.625 / d1) + 0.984375

def ease_in_out_bounce(n: float) -> float:
    if n < 0.5:
        return (1 - ease_out_bounce(1 - 2 * n)) / 2
    else:
        return (1 + ease_out_bounce(2 * n - 1)) / 2
    
# TODO: Check if any interesting function in
# https://github.com/semitable/easing-functions/blob/master/easing_functions/easing.py

# TODO: Rename to RateFunction when the other one
# is removed
class mRateFunction(Enum):
    """
    Rate functions to be used with an 'n' value
    that is between 0.0 and 1.0. This 'n' means
    the x distance within the graphic function
    and will return the y value for that point.
    """
    LINEAR = 'linear'
    SLOW_INTO = 'slow_into'
    SMOOTH = 'smooth'
    SMOOTH_STEP = 'smooth_step'
    SMOOTHER_STEP = 'smoother_step'
    SMOOTHERER_STEP = 'smootherer_step'
    RUSH_INTO = 'rush_into'
    RUSH_FROM = 'rush_from'
    DOUBLE_SMOOTH = 'double_smooth'
    THERE_AND_BACK = 'there_and_back'
    THERE_AND_BACK_WITH_PAUSE = 'there_and_back_with_pause'
    RUNNING_START = 'running_start'
    WIGGLE = 'wiggle'
    EASE_IN_CUBIC = 'ease_in_cubic'
    EASE_OUT_CUBIC = 'ease_out_cubic'
    #SQUISH_RATE_FUNC = 'squish_rate_func'
    LINGERING = 'lingering'
    EXPONENTIAL_DECAY = 'exponential_decay'
    EASE_IN_SINE = 'ease_in_sine'
    EASE_OUT_SINE = 'ease_out_sine'
    EASE_IN_OUT_SINE = 'ease_in_out_sine'
    EASE_IN_QUAD = 'ease_in_quad'
    EASE_OUT_QUAD = 'ease_out_quad'
    EASE_IN_OUT_QUAD = 'ease_in_out_quad'
    EASE_IN_OUT_CUBIC = 'ease_in_out_cubic'
    EASE_IN_QUART = 'ease_in_quart'
    EASE_OUT_QUART = 'ease_out_quart'
    EASE_IN_OUT_QUART = 'ease_in_out_quart'
    EASE_IN_QUINT = 'ease_in_quint'
    EASE_OUT_QUINT = 'ease_out_quint'
    EASE_IN_OUT_QUINT = 'ease_in_out_quint'
    EASE_IN_EXPO = 'ease_in_expo'
    EASE_OUT_EXPO = 'ease_out_expo'
    EASE_IN_OUT_EXPO = 'ease_in_out_expo'
    EASE_IN_CIRC = 'ease_in_circ'
    EASE_OUT_CIRC = 'ease_out_circ'
    EASE_IN_OUT_CIRC = 'ease_in_out_circ'
    EASE_IN_BACK = 'ease_in_back'
    EASE_OUT_BACK = 'ease_out_back'
    EASE_IN_OUT_BACK = 'ease_in_out_back'
    EASE_IN_ELASTIC = 'ease_in_elastic'
    EASE_OUT_ELASTIC = 'ease_out_elastic'
    EASE_IN_OUT_ELASTIC = 'ease_in_out_elastic'
    EASE_IN_BOUNCE = 'ease_in_bounce'
    EASE_OUT_BOUNCE = 'ease_out_bounce'
    EASE_IN_OUT_BOUNCE = 'ease_in_out_bounce'

    def get_function(self):
        """
        Obtain the function to calculate the value of
        the given 'n'. This function can be called by
        providing the 'n' value and any other needed
        key parameter.
        """
        functions = {
            mRateFunction.LINEAR: linear,
            mRateFunction.SLOW_INTO: slow_into,
            mRateFunction.SMOOTH: smooth,
            mRateFunction.SMOOTH_STEP: smooth_step,
            mRateFunction.SMOOTHER_STEP: smoother_step,
            mRateFunction.SMOOTHERER_STEP: smootherer_step,
            mRateFunction.RUSH_INTO: rush_into,
            mRateFunction.RUSH_FROM: rush_from,
            mRateFunction.DOUBLE_SMOOTH: double_smooth,
            mRateFunction.THERE_AND_BACK: there_and_back,
            mRateFunction.THERE_AND_BACK_WITH_PAUSE: there_and_back_with_pause,
            mRateFunction.RUNNING_START: running_start,
            mRateFunction.WIGGLE: wiggle,
            mRateFunction.EASE_IN_CUBIC: ease_in_cubic,
            mRateFunction.EASE_OUT_CUBIC: ease_out_cubic,
            #mRateFunction.SQUISH_RATE_FUNC: squish_rate_func,
            mRateFunction.LINGERING: lingering,
            mRateFunction.EXPONENTIAL_DECAY: exponential_decay,
            mRateFunction.EASE_IN_SINE: ease_in_sine,
            mRateFunction.EASE_OUT_SINE: ease_out_sine,
            mRateFunction.EASE_IN_OUT_SINE: ease_in_out_sine,
            mRateFunction.EASE_IN_QUAD: ease_in_quad,
            mRateFunction.EASE_OUT_QUAD: ease_out_quad,
            mRateFunction.EASE_IN_OUT_QUAD: ease_in_out_quad,
            mRateFunction.EASE_IN_OUT_CUBIC: ease_in_cubic,
            mRateFunction.EASE_IN_QUART: ease_in_quart,
            mRateFunction.EASE_IN_OUT_QUART: ease_in_out_quart,
            mRateFunction.EASE_IN_QUINT: ease_in_quint,
            mRateFunction.EASE_OUT_QUINT: ease_out_quint,
            mRateFunction.EASE_IN_OUT_QUINT: ease_in_out_quint,
            mRateFunction.EASE_IN_EXPO: ease_in_expo,
            mRateFunction.EASE_OUT_EXPO: ease_out_expo,
            mRateFunction.EASE_IN_OUT_EXPO: ease_in_out_expo,
            mRateFunction.EASE_IN_CIRC: ease_in_circ,
            mRateFunction.EASE_OUT_CIRC: ease_out_circ,
            mRateFunction.EASE_IN_OUT_CIRC: ease_in_out_circ,
            mRateFunction.EASE_IN_BACK: ease_in_back,
            mRateFunction.EASE_OUT_BACK: ease_out_back,
            mRateFunction.EASE_IN_OUT_BACK: ease_in_out_back,
            mRateFunction.EASE_IN_ELASTIC: ease_in_elastic,
            mRateFunction.EASE_OUT_ELASTIC: ease_out_elastic,
            mRateFunction.EASE_IN_OUT_ELASTIC: ease_in_out_elastic,
            mRateFunction.EASE_IN_BOUNCE: ease_in_bounce,
            mRateFunction.EASE_OUT_BOUNCE: ease_out_bounce,
            mRateFunction.EASE_IN_OUT_BOUNCE: ease_in_out_bounce,
        }

        return functions[self]

    def apply(self, n: float, **kwargs):
        """
        Apply the rate function to the given 'n' and
        kwargs.

        The 'n' parameter must be a value between 0
        and 1.
        """
        if not NumberValidator.is_number_between(n, 0, 1):
            raise Exception('The rate function has been built to work with an "n" value between 0 and 1.')

        return self.get_function()(n, **kwargs)
    


# We have a range that defines the x and one range that defines the y
# We have nodes that are defined within that range
class Node:
    """
    Class that represent a Node in a Graphic, which
    has to be inside the limits.
    """
    position: tuple[float, float]

    @property
    def x(self):
        return self.position[0]

    @property
    def y(self):
        return self.position[1]

    def __init__(self, x: float, y: float):
        self.position = (x, y)

class GraphicAxis:
    """
    Class that represent a Graphic axis with its min
    and max range.
    """
    range: tuple[float, float] = None
    """
    The range of the axis, a (min, max) tuple.
    """

    def __init__(self, min: float, max: float):
        if not NumberValidator.is_number(min) or not NumberValidator.is_number(max):
            raise Exception('The parameters "min" and "max" must be numbers.')
        
        if min >= max:
            raise Exception('The "min" parameter cannot be greater or equal than the "max" parameter.')

        self.range = (min, max)

    @property
    def min(self):
        """
        The minimum value.
        """
        return self.range[0]
    
    @property
    def max(self):
        """
        The maximum value.
        """
        return self.range[1]
    
class NormalizableValue:
    """
    Class to represent a value within a range, useful
    to normalize or denormalize it without doubt if the
    value is yet normalized or not.

    We store any value as not normalized but you are
    able to normalize it in any case as we know the 
    range.
    """
    value: float = None
    """
    The value not normalized.
    """
    range: tuple[float, float] = None

    @property
    def normalized(self) -> float:
        """
        The 'value' but normalized according to the 'range' in
        which the lower limit will by represented by the 0 and
        the upper limit by the 1.
        """
        return ValueNormalizer(self.range[0], self.range[1]).normalize(self.value)

    def __init__(self, value: float, range: tuple[float, float], value_is_normalized: bool = False):
        """
        Initialize the 'value' within the 'range' provided. If
        the 'value' provided is already normalized, set the 
        'value_is_normalized' flag as True to be correctly
        recognized.
        """
        if not PythonValidator.is_tuple(range) or len(range) != 2:
            raise Exception('The provided "range" is not a tuple of 2 values.')
        
        if range[0] >= range[1]:
            raise Exception('The provided "range" first value is greater or equal to the second one.')
        
        if not NumberValidator.is_number_between(value, range[0], range[1]):
            raise Exception('The provided "value" is out of the given "range".')
        
        # Denormalize the value if the one provided is normalized
        value = ValueNormalizer(range[0], range[1]).denormalize(value) if value_is_normalized else value
        
        self.value = value
        self.range = range
    
class PairOfNodes:
    """
    Class to represent a pair of consecutive Nodes
    within a Graphic, that are connected and able
    to calculate any 'd' value between them. The
    left node must be positioned in a lower 'x' 
    than the right one to be consecutive and valid.

    This pair of nodes will be represented by the 0
    to 1 x and y axis values locally so they can be
    turned into the general Graphic value applying
    the general Graphic limits.
    """
    left_node: Node = None
    right_node: Node = None

    @property
    def max_x(self):
        return self.right_node.x
    
    @property
    def min_x(self):
        return self.left_node.x
    
    @property
    def max_y(self):
        return max([self.left_node.y, self.right_node.y])
    
    @property
    def min_y(self):
        return min([self.left_node.y, self.right_node.y])
    
    @property
    def is_descendant(self):
        """
        Check if the 'y' value of the left node is greater
        than the 'y' value of the right node.
        """
        return self.left_node.y > self.right_node.y

    def __init__(self, left_node: Node, right_node: Node):
        if left_node.x > right_node.x:
            raise Exception('The left_node "x" value must be lower than the right_node "x" value.')
        
        # TODO: Add a rate function to join them (?)
        self.left_node = left_node
        self.right_node = right_node

    def get_y_from_not_normalized_x(self, x: float) -> NormalizableValue:
        """
        The 'x' parameter must be a value between the left
        node 'x' and the right node 'x'.
        """
        if not NumberValidator.is_number_between(x, self.min_x, self.max_x):
            raise Exception(f'The "x" parameter must be between [{self.min_x}, {self.max_x}].')
        
        x: NormalizableValue = NormalizableValue(x, [self.min_x, self.max_x])

        # TODO: We need to be able to choose the function
        # that calculates the 'y' value, by now is being
        # forced to linear.
        value = NormalizableValue(mRateFunction.LINEAR.apply(x.normalized), [self.min_y, self.max_y], value_is_normalized = True)
        # If the y values are descendant in the graphic we
        # need to invert the linear function to obtain the
        # corresponding value
        if self.is_descendant:
            value = NormalizableValue(1 - value.normalized, [self.min_y, self.max_y], value_is_normalized = True)

        return value
    
    def get_y_from_normalized_x(self, x: float) -> NormalizableValue:
        """
        The 'x' parameter must be a value between 0 and 1,
        being 0 the left node x and 1 the right node x.
        """
        if not NumberValidator.is_number_between(x, 0, 1):
            raise Exception(f'The "x" parameter must be between [0, 1].')
        
        # TODO: We need to be able to choose the function
        # that calculates the 'y' value, by now is being
        # forced to linear.
        value = NormalizableValue(mRateFunction.LINEAR.apply(x), [self.min_y, self.max_y], value_is_normalized = True)

        # If the y values are descendant in the graphic we
        # need to invert the linear function to obtain the
        # corresponding value
        if self.is_descendant:
            value = NormalizableValue(1 - value.normalized, [self.min_y, self.max_y], value_is_normalized = True)

        return value

class Graphic:
    """
    Class that represent a Graphic in which we will
    place Nodes and apply rate functions between
    those nodes to calculate the corresponding y
    values.
    """
    x_axis: GraphicAxis = None
    """
    The x axis which contains the min and max x 
    valid values.
    """
    y_axis: GraphicAxis = None
    """
    The y axis which contains the min and max y
    valid values.
    """
    _nodes: list[Node]
    """
    The list of nodes defined in the graphic to
    build it. These nodes are interconnected with
    a rate function.
    """

    @property
    def nodes(self):
        """
        Get the nodes ordered by the x position.
        """
        return sorted(self._nodes, key = lambda node: node.position[0])
    
    @property
    def min_x(self):
        return min(self.nodes, key = lambda node: node.x)
    
    @property
    def max_x(self):
        return max(self.nodes, key = lambda node: node.x)
    
    @property
    def min_y(self):
        return min(self.nodes, key = lambda node: node.y)
    
    @property
    def max_y(self):
        return max(self.nodes, key = lambda node: node.y)
    
    @property
    def pairs_of_nodes(self) -> list[PairOfNodes]:
        """
        Get pairs of nodes ordered by the x position. There
        is, at least, one pair of nodes that will be, if no
        more nodes added, the first and the last one.
        """
        return [
            PairOfNodes(self.nodes[index], self.nodes[index + 1])
            for _, index in enumerate(self.nodes[1:])
        ]

    def __init__(self, x_axis: GraphicAxis, y_axis: GraphicAxis):
        if not PythonValidator.is_instance(x_axis, GraphicAxis) or not PythonValidator.is_instance(y_axis, GraphicAxis):
            raise Exception('The "x_axis" and "y_axis" parameter must be instances of GraphicAxis class.')

        # TODO: Maybe make it possible to be instiated with a list
        # of nodes
        
        self.x_axis = x_axis
        self.y_axis = y_axis

    def get_node(self, x: float):
        return next((node for node in self.nodes if node.x == x), None)

    def add_node(self, x: tuple[float, float], y: tuple[float, float]):
        """
        Add a new node to the graphic if its position is
        inside the x and y axis ranges and if there is not
        another node in that position.
        """
        if x < self.x_axis.min or x > self.x_axis.max:
            raise Exception(f'The provided "x" is not in the [{self.x_axis.min}, {self.x_axis.max}] range.')
        
        if y < self.y_axis.min or y > self.x_axis.max:
            raise Exception(f'The provided "y" is not in the [{self.y_axis.min}, {self.y_axis.max}] range.')
        
        if self.get_node(x) is not None:
            raise Exception('There is another node in the provided "x" position.')

        self._nodes.append(Node(x, y))

    def _get_pair_of_node_from_x(self, x: float):
        """
        Obtain the pair of nodes in which the provided 'x'
        is contained.
        """
        return next((pair_of_node for pair_of_node in self.pairs_of_nodes if x <= pair_of_node.max_x), None)

    def get_y_from_not_normalized_x(self, x: float):
        """
        Return the 'y' value (not normalized) corresponding
        to the provided not normalized 'x' of the graphic.
        """
        if not NumberValidator.is_number_between(x, self.min_x, self.max_x):
            raise Exception(f'The "x" parameter is out of the graphic bounds, it must be between [{self.min_x}, {self.max_x}].')
        
        return self._get_pair_of_node_from_x(x).get_y_from_not_normalized_x(x).value



# TODO: Remove this below when refactored and no longer used
class RateFunction:
    """
    Class to simplify and encapsulate the functionality related
    to normalized bezier and rate functions.

    For any case the 'n' value must be a normalized value 
    between 0 and 1 to work as expected. You can apply the 
    result to a variation you want to make in some of your
    functions.

    If you want to make a linear zoom of a 20%, you will use
    a progressive zoom by applying the formula '1 + 0.2 * 
    linear(t)' (where t is the normalized time moment of the
    zoom animation).

    This is based on the manim library and this web page 
    https://easings.net/.
    """
    @staticmethod
    def linear(n: float) -> float:
        return n
    
    @staticmethod
    def slow_into(n: float) -> float:
        return np.sqrt(1 - (1 - n) * (1 - n))

    @staticmethod
    def smooth(n: float, inflection: float = 10.0) -> float:
        error = Math.sigmoid(-inflection / 2)

        return min(
            max((Math.sigmoid(inflection * (n - 0.5)) - error) / (1 - 2 * error), 0),
            1,
        )
    
    @staticmethod
    def smoothstep(n: float) -> float:
        """
        Implementation of the 1st order SmoothStep sigmoid function.
        The 1st derivative (speed) is zero at the endpoints.
        https://en.wikipedia.org/wiki/Smoothstep
        """
        return 0 if n <= 0 else 3 * n**2 - 2 * n**3 if n < 1 else 1
    
    @staticmethod
    def smootherstep(n: float) -> float:
        """
        Implementation of the 2nd order SmoothStep sigmoid function.
        The 1st and 2nd derivatives (speed and acceleration) are zero at the endpoints.
        https://en.wikipedia.org/wiki/Smoothstep
        """
        return 0 if n <= 0 else 6 * n**5 - 15 * n**4 + 10 * n**3 if n < 1 else 1
    
    @staticmethod
    def smoothererstep(n: float) -> float:
        """
        Implementation of the 3rd order SmoothStep sigmoid function.
        The 1st, 2nd and 3rd derivatives (speed, acceleration and jerk) are zero at the endpoints.
        https://en.wikipedia.org/wiki/Smoothstep
        """
        alpha = 0
        if 0 < n < 1:
            alpha = 35 * n**4 - 84 * n**5 + 70 * n**6 - 20 * n**7
        elif n >= 1:
            alpha = 1
        return alpha
    
    @staticmethod
    def rush_into(n: float, inflection: float = 10.0) -> float:
        return 2 * RateFunction.smooth(n / 2.0, inflection)

    @staticmethod
    def rush_from(n: float, inflection: float = 10.0) -> float:
        return 2 * RateFunction.smooth(n / 2.0 + 0.5, inflection) - 1
    
    @staticmethod
    def double_smooth(n: float) -> float:
        if n < 0.5:
            return 0.5 * RateFunction.smooth(2 * n)
        else:
            return 0.5 * (1 + RateFunction.smooth(2 * n - 1))
        
    @staticmethod
    def there_and_back(n: float, inflection: float = 10.0) -> float:
        if n < 0.5:
            n = 2 * n
        else:
            n = 2 * (1 - n)

        return RateFunction.smooth(n, inflection)
    
    @staticmethod
    def there_and_back_with_pause(n: float, pause_ratio: float = 1.0 / 3) -> float:
        a = 1.0 / pause_ratio
        if n < 0.5 - pause_ratio / 2:
            return RateFunction.smooth(a * n)
        elif n < 0.5 + pause_ratio / 2:
            return 1
        else:
            return RateFunction.smooth(a - a * n)
        
    @staticmethod
    def running_start(n: float, pull_factor: float = -0.5) -> Iterable: # what is func return type?
        # TODO: This is being taken from manim, maybe copy (?)
        from manim.utils.bezier import bezier

        return bezier([0, 0, pull_factor, pull_factor, 1, 1, 1])(n)
    
    @staticmethod
    def wiggle(n: float, wiggles: float = 2) -> float:
        # TODO: Manim says 'not_quite_there' function is not working
        return RateFunction.there_and_back(n) * np.sin(wiggles * np.pi * n)
    
    @staticmethod
    def ease_in_cubic(n: float) -> float:
        return n * n * n
    
    @staticmethod
    def ease_out_cubic(n: float) -> float:
        return 1 - pow(1 - n, 3)
    
    @staticmethod
    def squish_rate_func(func: Callable[[float], float], a: float = 0.4, b: float = 0.6) -> Callable[[float], float]:
        def result(n: float):
            if a == b:
                return a

            if n < a:
                return func(0)
            elif n > b:
                return func(1)
            else:
                return func((n - a) / (b - a))

        return result
    
    @staticmethod
    def lingering(n: float) -> float:
        return RateFunction.squish_rate_func(lambda n: n, 0, 0.8)(n)
    
    @staticmethod
    def exponential_decay(n: float, half_life: float = 0.1) -> float:
        # The half-life should be rather small to minimize
        # the cut-off error at the end
        return 1 - np.exp(-n / half_life)

    @staticmethod
    def ease_in_sine(n: float) -> float:
        return 1 - np.cos((n * np.pi) / 2)
    
    @staticmethod
    def ease_out_sine(n: float) -> float:
        return np.sin((n * np.pi) / 2)
    
    @staticmethod
    def ease_in_out_sine(n: float) -> float:
        return -(np.cos(np.pi * n) - 1) / 2

    @staticmethod
    def ease_in_quad(n: float) -> float:
        return n * n
    
    @staticmethod
    def ease_out_quad(n: float) -> float:
        return 1 - (1 - n) * (1 - n)

    @staticmethod
    def ease_in_out_quad(n: float) -> float:
        return 2 * n * n if n < 0.5 else 1 - pow(-2 * n + 2, 2) / 2
    
    @staticmethod
    def ease_in_out_cubic(n: float) -> float:
        return 4 * n * n * n if n < 0.5 else 1 - pow(-2 * n + 2, 3) / 2

    @staticmethod
    def ease_in_quart(n: float) -> float:
        return n * n * n * n
    
    @staticmethod
    def ease_out_quart(n: float) -> float:
        return 1 - pow(1 - n, 4)

    @staticmethod
    def ease_in_out_quart(n: float) -> float:
        return 8 * n * n * n * n if n < 0.5 else 1 - pow(-2 * n + 2, 4) / 2
    
    @staticmethod
    def ease_in_quint(n: float) -> float:
        return n * n * n * n * n

    @staticmethod
    def ease_out_quint(n: float) -> float:
        return 1 - pow(1 - n, 5)
    
    @staticmethod
    def ease_in_out_quint(n: float) -> float:
        return 16 * n * n * n * n * n if n < 0.5 else 1 - pow(-2 * n + 2, 5) / 2

    @staticmethod
    def ease_in_expo(n: float) -> float:
        return 0 if n == 0 else pow(2, 10 * n - 10)
    
    @staticmethod
    def ease_out_expo(n: float) -> float:
        return 1 if n == 1 else 1 - pow(2, -10 * n)
    
    @staticmethod
    def ease_in_out_expo(n: float) -> float:
        if n == 0:
            return 0
        elif n == 1:
            return 1
        elif n < 0.5:
            return pow(2, 20 * n - 10) / 2
        else:
            return (2 - pow(2, -20 * n + 10)) / 2
        
    @staticmethod
    def ease_in_circ(n: float) -> float:
        return 1 - sqrt(1 - pow(n, 2))
    
    @staticmethod
    def ease_out_circ(n: float) -> float:
        return sqrt(1 - pow(n - 1, 2))
    
    @staticmethod
    def ease_in_out_circ(n: float) -> float:
        return (
            (1 - sqrt(1 - pow(2 * n, 2))) / 2
            if n < 0.5
            else (sqrt(1 - pow(-2 * n + 2, 2)) + 1) / 2
        )

    @staticmethod
    def ease_in_back(n: float) -> float:
        c1 = 1.70158
        c3 = c1 + 1

        return c3 * n * n * n - c1 * n * n

    @staticmethod
    def ease_out_back(n: float) -> float:
        c1 = 1.70158
        c3 = c1 + 1

        return 1 + c3 * pow(n - 1, 3) + c1 * pow(n - 1, 2)
    
    @staticmethod
    def ease_in_out_back(n: float) -> float:
        c1 = 1.70158
        c2 = c1 * 1.525

        return (
            (pow(2 * n, 2) * ((c2 + 1) * 2 * n - c2)) / 2
            if n < 0.5
            else (pow(2 * n - 2, 2) * ((c2 + 1) * (n * 2 - 2) + c2) + 2) / 2
        )
    
    @staticmethod
    def ease_in_elastic(n: float) -> float:
        c4 = (2 * np.pi) / 3
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return -pow(2, 10 * n - 10) * np.sin((n * 10 - 10.75) * c4)
        
    @staticmethod
    def ease_out_elastic(n: float) -> float:
        c4 = (2 * np.pi) / 3
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return pow(2, -10 * n) * np.sin((n * 10 - 0.75) * c4) + 1

    @staticmethod
    def ease_in_out_elastic(n: float) -> float:
        c5 = (2 * np.pi) / 4.5
        if n == 0:
            return 0
        elif n == 1:
            return 1
        elif n < 0.5:
            return -(pow(2, 20 * n - 10) * np.sin((20 * n - 11.125) * c5)) / 2
        else:
            return (pow(2, -20 * n + 10) * np.sin((20 * n - 11.125) * c5)) / 2 + 1

    @staticmethod
    def ease_in_bounce(n: float) -> float:
        return 1 - RateFunction.ease_out_bounce(1 - n)
    
    @staticmethod
    def ease_out_bounce(n: float) -> float:
        n1 = 7.5625
        d1 = 2.75

        if n < 1 / d1:
            return n1 * n * n
        elif n < 2 / d1:
            return n1 * (n - 1.5 / d1) * (n - 1.5 / d1) + 0.75
        elif n < 2.5 / d1:
            return n1 * (n - 2.25 / d1) * (n - 2.25 / d1) + 0.9375
        else:
            return n1 * (n - 2.625 / d1) * (n - 2.625 / d1) + 0.984375
        
    @staticmethod
    def ease_in_out_bounce(n: float) -> float:
        if n < 0.5:
            return (1 - RateFunction.ease_out_bounce(1 - 2 * n)) / 2
        else:
            return (1 + RateFunction.ease_out_bounce(2 * n - 1)) / 2

# TODO: I can create my own curves by setting nodes with
# different values (as speed curves in a famous video
# editor) to make my own animations