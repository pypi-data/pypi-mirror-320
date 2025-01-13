import pandas as pd

from ..utils.abstract import Numerical, RequiredStep
from ..utils.config import config
from ..utils.logging_config import setup_logger

logger = setup_logger(__name__)


class CorrelationFilter(RequiredStep, Numerical):
    """
    Transformer to detect highly correlated features and drop one of them. Pearsons correlation is used.
    Is a required step in preprocessing.

    Attributes:
        dropped_columns (list): List of columns that were dropped due to high correlation.
    """

    def __init__(self):
        """
        Initializes the filter with a specified correlation threshold.

        Args:
            correlation_threshold (float): Correlation threshold above which features are considered highly correlated.
        """

        self.threshold = config.correlation_threshold
        self.dropped_columns = []

    def fit(self, X: pd.DataFrame, y: pd.Series = None) -> "CorrelationFilter":
        """
        Identifies highly correlated features. Adds the second one from the pair to the list of columns to be dropped.

        Args:
            X (pd.DataFrame): The input feature data.

        Returns:
            CorrelationFilter: The fitted filter instance.
        """
        logger.start_operation(
            f"Fitting CorrelationFilter with threshold {self.threshold}"
        )
        try:
            corr_matrix = X.corr().abs()
            correlated_pairs = set()
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    if corr_matrix.iloc[i, j] > self.threshold:
                        correlated_pairs.add(
                            corr_matrix.columns[j]
                        )  # only the second column of the pair is dropped

            self.dropped_columns = list(correlated_pairs)
            logger.debug(
                f"Successfully fitted CorrelationFilter with threshold: {self.threshold}"
            )
        except Exception as e:
            logger.error(
                f"Failed to fit CorrelationFilter with threshold: {self.threshold}: {e}",
                exc_info=True,
            )
            raise ValueError(f"Failed to fit CorrelationFilter: {e}")
        finally:
            logger.end_operation()
        return self

    def transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        """
        Drops all features identified as highly correlated with another feature.

        Args:
            X (pd.DataFrame): The feature data.

        Returns:
            pd.DataFrame: The transformed data with correlated columns removed.
        """
        logger.start_operation(
            f"Transforming data by dropping {len(self.dropped_columns)} highly correlated columns."
        )
        try:
            X_transformed = X.drop(columns=self.dropped_columns, errors="ignore")
            logger.debug("Successfully transformed CorrelationFilter")
        except Exception as e:
            logger.error(
                f"Failed to transform CorrelationFilter with threshold: {self.threshold}: {e}",
                exc_info=True,
            )
            raise ValueError(f"Failed to transform CorrelationFilter: {e}")
        finally:
            logger.end_operation()
        return X_transformed

    def fit_transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        """
        Fits and transforms the data by removing correlated features. Performs fit and transform in one step.

        Args:
            X (pd.DataFrame): The feature data.

        Returns:
            pd.DataFrame: The transformed data.
        """
        logger.start_operation(
            f"Fitting and transforming data with correlation threshold {self.threshold}"
        )
        try:
            result = self.fit(X).transform(X, y)
            logger.debug("Successfully fit_transformed CorrelationFilter")
        except Exception as e:
            logger.error(
                f"Failed to fit_transform CorrelationFilter with threshold: {self.threshold}: {e}",
                exc_info=True,
            )
            raise ValueError(f"Failed to fit_transform CorrelationFilter: {e}")
        finally:
            logger.end_operation()
        return result

    def to_tex(self) -> dict:
        """
        Returns a short description of the transformer in dictionary format.
        """
        return {
            "desc": f"Removes one column from pairs of columns correlated above correlation threshold: {self.threshold}.",
        }
