from yta_general_utils.math.graphic.node import Node
from yta_general_utils.math.normalizable_value import NormalizableValue
from yta_general_utils.math.rate_functions import mRateFunction
from yta_general_utils.programming.parameter_validator import NumberValidator
from yta_general_utils.math.progression import Progression


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
    rate_function: mRateFunction = None

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

    def __init__(self, left_node: Node, right_node: Node, rate_function: mRateFunction = mRateFunction.EASE_IN_OUT_SINE):
        if left_node.x > right_node.x:
            raise Exception('The left_node "x" value must be lower than the right_node "x" value.')
        
        rate_function = mRateFunction.to_enum(rate_function)
        
        self.left_node = left_node
        self.right_node = right_node
        self.rate_function = rate_function

    def get_n_xy_values_to_plot(self, n: int = 100, do_normalize: bool = False) -> list[tuple[NormalizableValue, NormalizableValue]]:
        """
        Return 'n' (x, y) values to be plotted. Each of those
        'x' and 'y' values are normalized only if 'do_normalize'
        flag is set as True.
        """
        if not NumberValidator.is_positive_number(n):
            raise Exception('The provided "n" parameter is not a positive number.')
        
        n = int(n)

        xs = [
            NormalizableValue(x, (self.min_x, self.max_x))
            for x in Progression(self.min_x, self.max_x, 100, mRateFunction.LINEAR).values
        ]
        ys = [
            self.get_y_from_not_normalized_x(x.value)
            for x in xs
        ]

        if do_normalize:
            xs = [x.normalized for x in xs]
            ys = [y.normalized for y in ys]
        else:
            xs = [x.value for x in xs]
            ys = [y.value for y in ys]

        return list(zip(xs, ys))

    def get_y_from_not_normalized_x(self, x: float) -> NormalizableValue:
        """
        The 'x' parameter must be a value between the left
        node 'x' and the right node 'x'.
        """
        return self._get_y_from_x(x, is_x_normalized = False)
    
    def get_y_from_normalized_x(self, x: float) -> NormalizableValue:
        """
        The 'x' parameter must be a value between 0 and 1,
        being 0 the left node x and 1 the right node x.
        """
        return self._get_y_from_x(x, is_x_normalized = True)
    
    def _get_y_from_x(self, x: float, is_x_normalized: bool = False) -> NormalizableValue:
        """
        Get the 'y' value for the given 'x', depending on if
        the 'x' value is normalized or not, flagged with the
        'is_x_normalized' parameter.
        
        This method is for internal use only.
        """
        lower_limit = self.min_x if not is_x_normalized else 0
        upper_limit = self.max_x if not is_x_normalized else 1

        if not NumberValidator.is_number_between(x, lower_limit, upper_limit):
            raise Exception(f'The "x" parameter must be between [{lower_limit}, {upper_limit}].')
        
        value = NormalizableValue(self.rate_function.apply(x), (self.min_y, self.max_y), value_is_normalized = is_x_normalized)
        value = NormalizableValue(1 - value.normalized, (self.min_y, self.max_y), value_is_normalized = is_x_normalized) if self.is_descendant else value

        return value