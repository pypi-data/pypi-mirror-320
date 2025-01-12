from skfolio.optimization._base import BaseOptimization
from sklearn.utils.validation import check_is_fitted

from .data import DataPlaceHolder


class AdaptorPipeMixin:
    """AdaptorPipeMixin class that provides a reverse pipe operator for optimization objects.

    This mixin enables the use of the reverse pipe operator (`|`) with optimization
    results, allowing for seamless integration with adaptor classes that transform
    optimization results.

    Methods:
        __ror__(self, other: BaseOptimization):
            Applies the fit_transform method if the other object is an instance of BaseOptimization.
            Raises a TypeError if the operation is not supported for the given types.
    """

    def __ror__(self, other: BaseOptimization):
        """Reverse pipe operator for BaseOptimization.

        Args:
            other (BaseOptimization): The optimization result to be transformed.

        Returns:
            The result of applying the fit_transform method on the optimization result.

        Raises:
            TypeError: If the operand types are not supported for this operation.
        """
        if isinstance(other, BaseOptimization):
            check_is_fitted(other, "weights_")
            return self.fit_transform(other)  # type: ignore
        else:
            raise TypeError(
                f"unsupported operand type(s) for |: {self.__class__.__name__} and '{type(other)}'"
            )


class TransformerPipeMixin:
    """
    TransformerPipeMixin class that provides pipe operators for transformer classes.

    This mixin enables the use of the pipe operator (`|`) and the reverse pipe operator
    (`|`) with transformer classes, allowing for seamless integration with other
    classes that take a DataPlaceHolder as input.

    Attributes:

    Methods:
        __or__(self, other: BaseOptimization):
            Applies the fit_transform method if the other object is an instance of BaseOptimization.
            Raises a TypeError if the operation is not supported for the given types.
        __ror__(self, other: DataPlaceHolder):
            Applies the fit_transform method if the other object is an instance of DataPlaceHolder.
            Raises a TypeError if the operation is not supported for the given types.
    """

    def __or__(self, other: BaseOptimization):
        """
        Pipe operator for BaseOptimization.

        Args:
            other (BaseOptimization): The optimization result to be transformed.

        Returns:
            The result of applying the fit_transform method on the optimization result.

        Raises:
            TypeError: If the operand types are not supported for this operation.
        """
        if isinstance(other, BaseOptimization):
            return other.fit_transform(self)  # type: ignore
        else:
            raise TypeError(
                f"unsupported operand type(s) for |: {self.__class__.__name__} and '{type(other)}'"
            )

    def __ror__(self, other: DataPlaceHolder):
        """
        Reverse pipe operator for DataPlaceHolder.

        Args:
            other (DataPlaceHolder): The input data to be transformed.

        Returns:
            The result of applying the fit_transform method on the input data.

        Raises:
            TypeError: If the operand types are not supported for this operation.
        """
        if isinstance(other, DataPlaceHolder):
            return self.fit_transform(other)  # type: ignore
        else:
            raise TypeError(
                f"unsupported operand type(s) for |: {self.__class__.__name__} and '{type(other)}'"
            )


class OptimizerPipeMixin:
    """
    OptimizerPipeMixin class that provides a reverse pipe operator for optimization classes.

    This mixin enables the use of the reverse pipe operator (`|`) with optimization
    classes, allowing for seamless integration with other classes that take a
    DataPlaceHolder as input.

    Attributes:

    Methods:
        __ror__(self, other: DataPlaceHolder):
            Applies the fit method if the other object is an instance of DataPlaceHolder.
            Raises a TypeError if the operation is not supported for the given types.
    """

    def __ror__(self, other: DataPlaceHolder):
        """
        Reverse pipe operator for DataPlaceHolder.

        Args:
            other (DataPlaceHolder): The input data to be optimized.

        Returns:
            The result of applying the fit method on the input data.

        Raises:
            TypeError: If the operand types are not supported for this operation.
        """
        if isinstance(other, DataPlaceHolder):
            return self.fit(other)  # type: ignore
        else:
            raise TypeError(
                f"unsupported operand type(s) for |: {self.__class__.__name__} and '{type(other)}'"
            )


class SelectorPipeMixin:
    """SelectorPipeMixin class that provides a reverse pipe operator for selector classes.

    This mixin enables the use of the reverse pipe operator (`|`) with selector
    classes, allowing for seamless integration with other classes that take a
    DataPlaceHolder as input.

    Attributes:

    Methods:
        __ror__(self, other: DataPlaceHolder):
            Applies the fit_transform method if the other object is an instance of DataPlaceHolder.
            Raises a TypeError if the operation is not supported for the given types.
    """

    def __ror__(self, other: DataPlaceHolder):
        """
        Reverse pipe operator for DataPlaceHolder.

        Args:
            other (DataPlaceHolder): The input data to be transformed.

        Returns:
            The result of applying the fit_transform method on the input data.

        Raises:
            TypeError: If the operand types are not supported for this operation.
        """
        if isinstance(other, DataPlaceHolder):
            return self.fit_transform(other)  # type: ignore
        else:
            raise TypeError(
                f"unsupported operand type(s) for |: {self.__class__.__name__} and '{type(other)}'"
            )
