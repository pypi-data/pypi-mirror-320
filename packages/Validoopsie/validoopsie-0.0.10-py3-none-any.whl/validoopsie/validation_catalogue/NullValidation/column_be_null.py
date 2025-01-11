from __future__ import annotations

import narwhals as nw
from narwhals.typing import FrameT

from validoopsie.base import BaseValidationParameters, base_validation_wrapper


@base_validation_wrapper
class ColumnBeNull(BaseValidationParameters):
    """Check if the values in a column are null.

    Args:
        column (str): Column to validate.
        threshold (float, optional): The threshold for the validation. Defaults to 0.0.
        impact (str, optional): The impact level of the validation. Defaults to "low".
        kwargs (dict): Additional keyword arguments.

    """

    @property
    def fail_message(self) -> str:
        """Return the fail message, that will be used in the report."""
        return f"The column '{self.column}' doesn't have values that are null."

    def __call__(self, frame: FrameT) -> FrameT:
        """Check if the unique values are in the list.

        Return will be used in the `__execute_check__` method in `column_check`
        decorator.
        """
        return (
            frame.select(self.column)
            .filter(
                nw.col(self.column).is_null() == False,
            )
            .group_by(self.column)
            .agg(nw.col(self.column).count().alias(f"{self.column}-count"))
        )
