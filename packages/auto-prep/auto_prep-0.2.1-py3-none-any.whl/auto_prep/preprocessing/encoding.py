import pandas as pd
from sklearn.preprocessing import OneHotEncoder

from ..utils.abstract import Categorical, RequiredStep
from ..utils.logging_config import setup_logger
from .utils import TolerantLabelEncoder

logger = setup_logger(__name__)


class ColumnEncoder(RequiredStep, Categorical):
    """
    Encoder for categorical features. This class applies different encoding techniques
    (OneHotEncoding or LabelEncoding) based on the number of unique values in each column.

    For columns with less than 5 unique values, OneHotEncoder is used. For columns with
    5 or more unique values, TolerantLabelEncoder is applied.

    Attributes:
        encoders (dict): A dictionary of fitted encoders for each column.
        columns (list): A list of columns that have been encoded.
    """

    def __init__(self):
        """
        Initializes the encoder with empty dictionaries for encoders and columns.
        """
        self.encoders = {}  # Dictionary to store encoder for each column
        self.columns = []  # List to store columns that are encoded

    def fit(self, X: pd.DataFrame, y: pd.Series = None) -> "ColumnEncoder":
        """
        Fits the encoder to the categorical features in the data.

        Args:
            X (pd.DataFrame): The feature data to fit the encoder to.
            y (pd.Series, optional): The target variable (to fit the encoder).

        Returns:
            ColumnEncoder: The fitted encoder instance.

        The encoder will choose between OneHotEncoder and LabelEncoder based on the
        number of unique values in each column. OneHotEncoder is used for columns
        with fewer than 5 unique values, and TolerantLabelEncoder is used for columns with
        5 or more unique values.
        """
        logger.start_operation(
            f"Fitting ColumnEncoder to data with {X.shape[0]} rows and {X.shape[1]} columns."
        )
        try:
            categorical_columns = X.select_dtypes(exclude="number").columns.tolist()
            for column in categorical_columns:
                unique_vals = len(X[column].unique())
                if unique_vals < 5:
                    # OneHotEncoder for columns with less than 5 unique values
                    logger.debug(
                        f"Column {column} has {unique_vals} unique values, using OneHotEncoder."
                    )
                    self.encoders[column] = OneHotEncoder(sparse_output=False)
                    self.encoders[column].fit(X[[column]])
                else:
                    # TolerantLabelEncoder for columns with 5 or more unique values
                    logger.debug(
                        f"Column {column} has {unique_vals} unique values, using TolerantLabelEncoder."
                    )
                    self.encoders[column] = TolerantLabelEncoder()
                    self.encoders[column].fit(X[column])
                self.columns.append(column)
        except Exception as e:
            logger.error(f"Error in ColumnEncoder fit: {e}")
            raise e
        finally:
            logger.end_operation()
        return self

    def transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        """
        Transforms the feature data using the fitted encoders.

        Args:
            X (pd.DataFrame): The feature data to transform.
            y (pd.Series, optional): The target variable (to append to the result).

        Returns:
            pd.DataFrame: The transformed feature data, with encoded columns.
        """
        logger.start_operation(
            f"Transforming data with {X.shape[0]} rows and {X.shape[1]} columns."
        )

        try:
            for column in self.columns:
                try:
                    if isinstance(self.encoders[column], OneHotEncoder):
                        logger.debug(f"Applying OneHotEncoder to column {column}.")
                        encoded_data = self.encoders[column].transform(X[[column]])
                        ohe_columns = [
                            f"{column}_{cat}"
                            for cat in self.encoders[column].categories_[0]
                        ]
                        encoded_df = pd.DataFrame(
                            encoded_data, columns=ohe_columns, index=X.index
                        )
                        X = pd.concat([X.drop(column, axis=1), encoded_df], axis=1)
                    else:
                        logger.debug(
                            f"Applying TolerantLabelEncoder to column {column}."
                        )
                        X[column] = self.encoders[column].transform(
                            X[column], column=column
                        )
                except Exception as e:
                    raise Exception(f"Error in transforming column {column}") from e

        except Exception as e:
            logger.error(f"Error in ColumnEncoder transform: {e}")
            raise e
        finally:
            logger.end_operation()
        return X

    def fit_transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        """
        Fits and transforms the feature data using the encoder.

        Args:
            X (pd.DataFrame): The feature data to transform.
            y (pd.Series, optional): The target variable (to append to the result).

        Returns:
            pd.DataFrame: The transformed feature data, with encoded columns.

        This method combines the fit and transform steps in one operation.
        """
        logger.start_operation("Fitting and transforming data.")
        result = self.fit(X).transform(X)
        logger.end_operation()
        return result

    def to_tex(self) -> dict:
        return {
            "desc": "Encodes categorical columns using OneHotEncoder (for columns with <5 unique values) or TolerantLabelEncoder (for columns with >=5 unique values). Encodes target variable using LabelEncoder if provided.",
        }
