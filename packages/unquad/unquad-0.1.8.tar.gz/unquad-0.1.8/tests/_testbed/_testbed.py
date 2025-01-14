import functools
import multiprocessing
import random
from pathlib import Path

import numpy as np
import pandas as pd

from sys import float_info
from statistics import mean
from dataclasses import dataclass

from pyod.models.base import BaseDetector
from pyod.models.iforest import IForest
from sklearn.model_selection import train_test_split
from tqdm import tqdm

from unquad.data.loader import DataLoader
from unquad.estimator.configuration import DetectorConfig
from unquad.estimator.detector import ConformalDetector
from unquad.strategy.base import BaseStrategy
from unquad.strategy.jackknife import Jackknife
from unquad.strategy.split import Split
from unquad.utils.enums import Dataset
from unquad.utils.metrics import false_discovery_rate, statistical_power


@dataclass
class Setup:

    L: int

    detector: BaseDetector
    strategy: BaseStrategy
    config: DetectorConfig

    n: int
    normal: pd.DataFrame
    outlier: pd.DataFrame
    n_test_normal: int
    n_train_calib: int
    n_test_outlier: int


class Experiment:

    def __init__(self, _setup: Setup):
        self._setup = setup

    def run(self, _j: int) -> (float, float):

        _detector = self._setup.detector
        _strategy = self._setup.strategy
        _config = self._setup.config
        _config.seed = _j

        train, test = train_test_split(
            self._setup.normal,
            train_size=self._setup.n_train_calib,
            random_state=self._setup.L,
        )

        train.drop(["Class"], axis=1, inplace=True)

        ce = ConformalDetector(detector=_detector, strategy=_strategy, config=_config)
        ce.detector.set_params(
            **{
                "n_jobs": 1,
            }
        )
        ce.fit(train)

        _fdr_list, _power_list = [], []
        for l in range(self._setup.L):

            test_set = pd.concat(
                [
                    test.sample(n=self._setup.n_test_normal, random_state=l),
                    self._setup.outlier.sample(
                        n=self._setup.n_test_outlier, random_state=l
                    ),
                ],
                ignore_index=True,
            )

            x_test = test_set.drop(["Class"], axis=1)
            y_test = test_set["Class"]

            est = ce.predict(x_test)

            _fdr = false_discovery_rate(y_test, est, dec=3)
            _fdr_list.append(_fdr)
            _power = statistical_power(y_test, est, dec=3)
            _power_list.append(_power)

        return mean(_fdr_list), mean(_power_list)


if __name__ == "__main__":

    random.seed(1)
    np.random.seed(1)

    FDR_FILE_PATH = Path("fdr.csv")
    POWER_FILE_PATH = Path("power.csv")

    datasets = [
        Dataset.WBC,
        Dataset.SHUTTLE,
        Dataset.BREAST,
        Dataset.MUSK,
        Dataset.IONOSPHERE,
        Dataset.THYROID,
        Dataset.MAMMOGRAPHY,
        Dataset.FRAUD,
    ]

    strategies = [
        Split(),
        # CrossValidation(k=10),
        # CrossValidation(k=10, plus=True),
        # Jackknife(),
        # Jackknife(plus=True),
    ]

    models = [
        IForest(behaviour="new", contamination=float_info.min),
        # LOF(contamination=float_info.min),
        # PCA(n_components=3, contamination=float_info.min),
    ]

    fdr, power = [], []
    L, J = 100, 100

    for dataset in datasets:
        dl = DataLoader(dataset=dataset)
        df = dl.df

        for strategy in strategies:
            if strategy in [Jackknife(), Jackknife(plus=True)] and dl.rows > 1_000:
                continue

            normal = df.loc[df.Class == 0]
            outlier = df.loc[df.Class == 1]

            n_normal = len(normal)
            n_train_calib = n_normal // 2
            n_cal = min(2000, n_train_calib // 2)
            n_test = min(1000, n_train_calib // 3)
            n_test_outlier = n_test // 10
            n_test_normal = n_test - n_test_outlier

            for model in models:

                config = DetectorConfig()

                setup = Setup(
                    L=L,
                    detector=model,
                    strategy=strategy,
                    config=config,
                    n=dl.rows,
                    normal=normal,
                    outlier=outlier,
                    n_test_normal=n_test_normal,
                    n_train_calib=n_train_calib,
                    n_test_outlier=n_test_outlier,
                )

                j = range(J)
                experiment = Experiment(_setup=setup)
                func = functools.partial(experiment.run)
                with multiprocessing.Pool(10) as pool:
                    result = list(tqdm(pool.imap_unordered(func, j), total=J))

                fdr = [_tuple[0] for _tuple in result]
                power = [_tuple[1] for _tuple in result]

                # False Discovery Rate
                fdr_df = {
                    "dataset": [dataset.value],
                    "strategy": [strategy.__str__()],
                    "model": [model.__class__.__name__],
                    "mean": [np.round(np.mean(fdr), 3)],
                    "q90": [np.round(np.quantile(fdr, 0.9), 3)],
                    "std": [np.round(np.std(fdr), 3)],
                    "raw": [fdr],
                }
                fdr_df = pd.DataFrame(data=fdr_df)

                if FDR_FILE_PATH.is_file():
                    existing_df = pd.read_csv(FDR_FILE_PATH)
                    fdr_df = pd.concat([existing_df, fdr_df], axis=0)
                fdr_df.to_csv(FDR_FILE_PATH, index=False)

                # Statistical Power
                power_df = {
                    "dataset": [dataset.value],
                    "strategy": [strategy.__str__()],
                    "model": [model.__class__.__name__],
                    "mean": [np.round(np.mean(power), 3)],
                    "q90": [np.round(np.quantile(power, 0.9), 3)],
                    "std": [np.round(np.std(power), 3)],
                    "raw": [power],
                }
                power_df = pd.DataFrame(data=power_df)

                if POWER_FILE_PATH.is_file():
                    existing_df = pd.read_csv(POWER_FILE_PATH)
                    power_df = pd.concat([existing_df, power_df], axis=0)
                power_df.to_csv(POWER_FILE_PATH, index=False)
