import logging
import os
import shutil
import warnings
from typing import Union

import numpy as np
from pylatex import NoEscape
from sklearn import set_config
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, roc_auc_score

os.environ["OMP_DISPLAY_ENV"] = "FALSE"
# Suppress UserWarnings and RuntimeWarnings
warnings.simplefilter("ignore", category=UserWarning)
warnings.simplefilter("ignore", category=RuntimeWarning)


set_config(transform_output="pandas")

# ANSI color codes
COLORS: dict = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[41m",  # Red background
    "RESET": "\033[0m",  # Reset color
}

LOG_FORMAT: str = "%(asctime)s %(levelname)s %(name)s: %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL: str = logging.CRITICAL

DEFAULT_TEX_GEOMETRY: dict = {
    "margin": "0.5in",
    "headheight": "10pt",
    "footskip": "0.2in",
    "tmargin": "0.5in",
    "bmargin": "0.5in",
}

DEFAULT_ABSTRACT: str = NoEscape(
    r"""
    \begin{abstract}
    This raport has been generated with AutoPrep.
    \end{abstract}
    """
)

DEFAULT_CHARTS_SETTINGS: dict = {
    "theme": "white",
    "title_fontsize": 18,
    "title_fontweight": "bold",
    "xlabel_fontsize": 15,
    "ylabel_fontsize": 15,
    "tick_label_rotation": 45,
    "palette": "pastel",
    "plot_width": 20,
    "plot_height_per_row": 8,
    "heatmap_cmap": "coolwarm",
    "heatmap_fmt": ".2f",
}

DEFAULT_CORRELATION_SELECTOR_SETTINGS: dict = {
    "threshold": 0.8,
    "k": 10,
}

DEFAULT_OUTLIER_DETECTOR_SETTINGS: dict = {
    "zscore_threshold": 3,
    "isol_forest_n_estimators": 100,
    "cook_threshold": 1,
}

DEFAULT_IMPUTTER_SETTINGS: dict = {
    "categorical_strategy": "most_frequent",
    "numerical_strategy": "mean",
    "n_iter": 10,
}

DEFAULT_TUNING_PARAMS: dict = {
    "cv": 3,
    "verbose": 0,
    "n_jobs": -1,
    "random_state": 42,
    "n_iter": 10,
}


class GlobalConfig:
    """Global config class."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GlobalConfig, cls).__new__(cls, *args, **kwargs)
            cls._instance.set()
        return cls._instance

    def set(
        self,
        raport_name: str = "raport",
        raport_title: str = "ML Raport",
        raport_author: str = "AutoPrep",
        raport_abstract: str = DEFAULT_ABSTRACT,
        root_dir: str = "raport",
        return_tex_: bool = True,
        logger_colors_map: dict = COLORS,
        log_format: str = LOG_FORMAT,
        log_date_format: str = LOG_DATE_FORMAT,
        log_level: str = LOG_LEVEL,
        log_dir: str = None,
        max_log_file_size_in_mb: int = 5,
        tex_geomatry: dict = DEFAULT_TEX_GEOMETRY,
        train_size: float = 0.8,
        test_size: float = 0.1,
        valid_size: float = 0.1,
        random_state: int = 42,
        max_datasets_after_preprocessing: int = 3,
        perform_only_required_: bool = False,
        raport_decimal_precision: int = 4,
        chart_settings: dict = DEFAULT_CHARTS_SETTINGS,
        correlation_selectors_settings: dict = DEFAULT_CORRELATION_SELECTOR_SETTINGS,
        outlier_detector_settings: dict = DEFAULT_OUTLIER_DETECTOR_SETTINGS,
        imputer_settings: dict = DEFAULT_IMPUTTER_SETTINGS,
        umap_components: int = 50,
        correlation_threshold: float = 0.8,
        correlation_percent: float = 0.7,
        n_bins: int = 4,
        outlier_detector_method: str = "zscore",
        max_unique_values_classification: int = 20,
        regression_pipeline_scoring_model: BaseEstimator = RandomForestRegressor(
            n_estimators=100, random_state=42, max_depth=5, n_jobs=-1, warm_start=True
        ),
        classification_pipeline_scoring_model: BaseEstimator = RandomForestClassifier(
            n_estimators=100, random_state=42, max_depth=5, n_jobs=-1, warm_start=True
        ),
        regression_pipeline_scoring_func: Union[callable, str] = (
            mean_squared_error,
            "min",
        ),
        classification_pipeline_scoring_func_bin: Union[callable, str] = (
            roc_auc_score,
            "max",
        ),
        classification_pipeline_scoring_func_multi: Union[callable, str] = (
            accuracy_score,
            "max",
        ),
        max_workers: int = None,
        tuning_params: dict = DEFAULT_TUNING_PARAMS,
        max_models: int = 3,
    ):
        """
        Args:
            raport_name (str) - Raport name. Defaults to "raport.pdf".
            raport_title (str) - Raport title. Defaults to "ML Raport".
            raport_title (str) - Raport author. Defaults to "AutoPrep".
            raport_abstract (str) - Raport abstract section. Can be set to "".
                Defaults to :obj:`DEFAULT_ABSTRACT`.
            root_dir (str) - Root directory. Here raport will be
                stored and all cache. Defaults to "raport".
            return_tex_ (bool) - If true it will create .tex file
                alongsite the pdf. Defaults to True.
            logger_colors_map (dict) - Color map for the loggers.
                Defaults to :obj:`COLORS`.
            log_format (str) - Log format for logging liblary.
                Defaults to :obj:`LOG_FORMAT`.
            log_date_format (str) - Log date format for logging liblary.
                Defaults to :obj:`LOG_DATE_FORMAT`.
            log_level (str) - Log level for logging liblary.
                Defaults to :obj:`LOG_LEVEL`.
            log_dir (str) - Log directory for storing the logs.
                If None provided, will default to "logs" in directory from which program was called.
                -1 means no logging to file.
            max_log_file_size_in_mb (int) - Maximum file size in mb for
                each logger. Defaults to 5.
            tex_geomatry (dict) - Geometry for pylatex.
                Defaults to :obj:`DEFAULT_TEX_GEOMETRY`.
            train_size (float) - % of traing set size. Defaults to 0.8.
            test_size (float) - % of traing set size. Defaults to 0.1.
            valid_size (float) - % of traing set size. Defaults to 0.1.
            random_state (int) - Random state for sklearn.
            max_datasets_after_preprocessing (int) - Maximum number of datasets that will be left
                after preprocessing steps. On them further models will be trained. Strongly
                affects performance.
            perform_only_required_ (bool) - weather or not to perform only required steps.
                Affects entire process.
            raport_decimal_precision (int) - Decimal precision for all float in raport.
                Will use standard python rounding.
            chart_settings (dict): Settings for customizing chart appearance.
                Defaults to None, which initializes default settings.
            correlation_selectors_settings (dict): Settings for correlation selectors.
            outlier_detector_settings (dict): Settings for outlier detectors
            imputer_settings (dict): Settings for imputers
            umap_components (int): Number of components for UMAP.
            max_unique_values_classification (int) - in case of target column being of non numerical dtype,
                it will calculate number of unique values (in task "auto"). If this number will be lower than
                that value, it'll perform classification.
            regression_pipeline_scoring_model (BaseEstimator) - model used for scoring processing pipelines
                in classification regression task.
            classification_pipeline_scoring_model (BaseEstimator) - model used for scoring processing pipelines
                in classification regression task.
            regression_pipeline_scoring_func (callable) - metric for scoring :obj:`regression_pipeline_scoring_model` output.
            classification_pipeline_scoring_func (callable) - metric for scoring :obj:`classification_pipeline_scoring_model` output.
            raport_chart_color_pallete (List[str]) - Color palette for basic eda charts.
            max_unique_values_classification (int) - in case of target column being of non numerical dtype,
                it will calculate number of unique values (in task "auto"). If this number will be lower than
                that value, it'll perform classification.
            regression_pipeline_scoring_model (BaseEstimator) - model used for scoring processing pipelines
                in classification regression task.
            classification_pipeline_scoring_model (BaseEstimator) - model used for scoring processing pipelines
                in classification regression task.
            regression_pipeline_scoring_func Union[callable, str] - pair (metric, direction) for scoring :obj:`regression_pipeline_scoring_model` output. Available directions are ['max', 'min'].
            classification_pipeline_scoring_func_bin Union[callable, str] - pair (metric, direction) for scoring :obj:`classification_pipeline_scoring_model` output. Available directions are ['max', 'min'].
            classification_pipeline_scoring_func_multi Union[callable, str] - pair (metric, direction) for scoring :obj:`classification_pipeline_scoring_model` output. Available directions are ['max', 'min'].
            raport_chart_color_pallete (List[str]) - Color palette for basic eda charts.
            correlation_threshold (float) - threshold used for detecting highly correlated features.Default 0.8.
            correlation_percent (float) - % of selected features based on their correlation with the target. Default 0.5.
            n_bins (int) - number of bins to create while binning numerical features.
            outlier_detector_method (str) - method used for outlier detection. Default "zscore".
            max_workers (int) - maximum number of cores to evaluate on.
            tuning_params (dict) - Tuning params for RandomizedSearchCV.
            max_models (int) - Maximum number of final models to save and raport.
        """
        assert (
            isinstance(raport_name, str) and raport_name != ""
        ), "raport_name should not be empty"
        self.raport_name = raport_name
        self.raport_title = raport_title
        self.raport_author = raport_author
        self.raport_abstract = raport_abstract

        self.root_dir = root_dir
        self.raport_path = os.path.abspath(os.path.join(root_dir, raport_name))
        self.charts_dir = os.path.join(self.raport_path, "charts")
        self.pipelines_dir = os.path.join(self.raport_path, "pipelines")

        self.return_tex_ = return_tex_

        self.logger_colors_map = logger_colors_map
        self.log_format = log_format
        self.log_date_format = log_date_format
        self.log_level = log_level

        assert (
            int(max_log_file_size_in_mb) == max_log_file_size_in_mb
            and max_log_file_size_in_mb >= 1
        ), f"Wrong value for max_log_file_size_in_mb: {max_log_file_size_in_mb}. "
        "Should be int > 1."
        self.max_log_file_size_in_mb = max_log_file_size_in_mb

        if log_dir is None:
            log_dir = os.path.abspath("logs")
        if log_dir != -1:
            os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir

        self.tex_geomatry = tex_geomatry

        self.train_size = train_size
        self.test_size = test_size
        self.valid_size = valid_size

        self.random_state = random_state
        np.random.seed(random_state)

        self.chart_settings = chart_settings

        assert (
            max_datasets_after_preprocessing > 0
        ), "Values smaller than 1 are forbidden."
        self.max_datasets_after_preprocessing = max_datasets_after_preprocessing
        self.perform_only_required_ = perform_only_required_

        self.raport_decimal_precision = raport_decimal_precision

        self.root_project_dir = os.path.abspath(
            os.path.join(__file__, "..", "..", "..")
        )

        assert 0 <= correlation_threshold <= 1, (
            f"Invalid value for correlation_threshold: {correlation_threshold}. "
            "It must be a float between 0 and 1."
        )
        self.correlation_threshold = correlation_threshold

        assert 0 <= correlation_percent <= 1, (
            f"Invalid value for correlation_selector_percent: {correlation_percent}. "
            "It must be a float between 0 and 1."
        )
        self.correlation_percent = correlation_percent

        assert (
            int(n_bins) == n_bins and n_bins >= 1
        ), f"Wrong value for n_bins: {n_bins}. "
        "Should be int >= 1."
        self.n_bins = n_bins

        self.correlation_selectors_settings = correlation_selectors_settings
        self.outlier_detector_settings = outlier_detector_settings
        self.imputer_settings = imputer_settings

        self.umap_components = umap_components

        assert (
            max_unique_values_classification >= 0
        ), "max_unique_values_classification should be positive integer."
        self.max_unique_values_classification = max_unique_values_classification
        self.regression_pipeline_scoring_model = regression_pipeline_scoring_model
        self.classification_pipeline_scoring_model = (
            classification_pipeline_scoring_model
        )

        for func_ in (
            regression_pipeline_scoring_func,
            classification_pipeline_scoring_func_bin,
            classification_pipeline_scoring_func_multi,
        ):
            assert func_[1] in (
                "min",
                "max",
            ), f"Unknown direction choosen for {func_.__name__}"
        self.regression_pipeline_scoring_func = regression_pipeline_scoring_func
        self.classification_pipeline_scoring_func = (
            classification_pipeline_scoring_func_bin
        )
        self.classification_pipeline_scoring_func_multi = (
            classification_pipeline_scoring_func_multi
        )

        assert outlier_detector_method in [
            "zscore",
            "iqr",
            "isolation_forest",
        ], f"Invalid value for outlier_detector_method: {outlier_detector_method}."
        "Should be one of ['zscore', 'iqr', 'isolation_forest', 'cooks_distance']."
        self.outlier_detector_method = outlier_detector_method

        self.max_workers = max_workers
        self.tuning_params = tuning_params

        assert max_models > 0, "Invalid value"
        self.max_models = max_models

    def update(self, **kwargs):
        """Updates config's data with kwargs."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def prepare_dir(self):
        """Clears and creates all neccessary directories."""
        if os.path.exists(self.root_dir):
            shutil.rmtree(self.root_dir)
        os.makedirs(self.root_dir, exist_ok=True)
        os.makedirs(self.charts_dir, exist_ok=True)
        os.makedirs(self.pipelines_dir, exist_ok=True)


config = GlobalConfig()
