from typing import (
    Callable,
    Optional,
    Union,
    List,
    Dict,
    Tuple,
)
import logging
import warnings

import numpy as np
from numpy.typing import ArrayLike

from optuna.distributions import (
    IntDistribution,
    FloatDistribution,
    CategoricalDistribution
)
from optuna.trial import Trial
from optuna.exceptions import TrialPruned

import pandas as pd
from sklearn.model_selection import (
    cross_val_score,
    BaseCrossValidator
)
from sklearn.utils.class_weight import compute_sample_weight

from catboost import (
    Pool,
    CatBoostClassifier,
    CatBoostRegressor,
    CatBoostRanker,
)

from .utils import (
    stopit_after_timeout,
    CrossValidator
)

logger = logging.getLogger('optuna.OptunaTuneCV')

CatboostModel = Union[CatBoostRegressor, CatBoostClassifier, CatBoostRanker]
DataSet = Union[np.ndarray, List, pd.DataFrame, pd.Series]


class OptunaTuneCV:
    """
    Class for optimizing model hyperparameters using Optuna with cross-validation.

    This class acts as a callable objective function for Optuna studies. It automates
    hyperparameter tuning for machine learning models via Optuna, integrating with
    cross-validation to evaluate performance. It supports parameter space definitions,
    scoring customization, and optional multi-GPU parallelism.

    Attributes
    ----------
        model : CatboostModel
            The model whose hyperparameters are being tuned.
        param_distributions : Union[Dict, Callable[[Trial], Dict]]
            Hyperparameter search space, either as a dictionary or callable returning
            parameters per trial.
        direction : str
            Optimization direction, either 'maximize' or 'minimize'.
        x : DataSet
            The feature data for training.
        y : DataSet
            The target variable corresponding to the training data.
        group_id : Optional[List[int]]
            Optional group identifiers for the data.
        cv : Union[int, BaseCrossValidator]
            Cross-validation splitting strategy, e.g., number of folds or custom validator.
        scoring : Optional[str]
            Scoring metric to evaluate model performance.
        params_post_processing : Optional[Callable[[Trial, Dict], Dict]]
            Callable for post-processing hyperparameters after they are sampled.
        _best_score : float
            Internal tracking of the best score seen so far.
        best_score : Optional[float]
            External tracking for the best score, if provided at initialization.
        weight_column : Optional[ArrayLike]
            Optional sample weight for training data.
        n_folds_start_prune : int
            Minimum number of completed folds before pruning can activate. Default is infinity.
        has_pruner : bool
            Whether pruning logic is enabled for optimization.
        parallel : bool
            Whether to enable parallel cross-validation runs.
        parallel_available_gpus : Optional[List[int]]
            List of available GPU IDs for parallel computation, if applicable.
        trial_timeout : Optional[int]
            Maximum duration (in seconds) per trial before pruning. Ignored if `parallel` is True.
        error_handling : str
            Strategy for handling exceptions during trials. Options are 'raise' or 'prune'.
    Examples
    --------
    >>> from catboost import CatBoostClassifier
    >>> from catboost_extensions import OptunaTuneCV, CatboostParamSpace
    >>> from sklearn.datasets import make_classification
    >>> from sklearn.model_selection import StratifiedKFold
    >>> from sklearn.metrics import roc_auc_score
    >>> import optuna

    >>> X, y = make_classification(n_samples=1000, n_features=20, n_informative=10, random_state=0)
    >>> model = CatBoostClassifier(task_type='CPU', verbose=0)
    >>> param_space_getter = CatboostParamSpace(params_preset='general', task_type='GPU')
    >>> objective = OptunaTuneCV(model, param_space_getter, X, y, cv=5, scoring='roc_auc', direction='maximize')
    >>> study = optuna.create_study(direction='maximize')
    >>> study.optimize(objective, n_trials=100)

    """

    def __init__(
            self,
            model: CatboostModel,
            param_space: Union[Dict, Callable[[Trial], Dict]],
            x: DataSet,
            y: DataSet,
            group_id: Optional[List[int]] = None,
            last_best_score: Optional[float] = None,
            trial_timeout: Optional[int] = None,
            params_post_processing: Optional[Callable[[Trial, Dict], Dict]] = None,
            cv: Union[int, BaseCrossValidator] = 5,
            scoring: Optional[str] = None,
            direction: str = 'maximize',
            weight_column: Optional[ArrayLike] = None,
            has_pruner: bool = False,
            n_folds_start_prune: int = np.inf,
            parallel: bool = False,
            parallel_available_gpus: Optional[List[int]] = None,
            error_handling: str = 'raise',
    ):
        self.model = model
        self.param_distributions = param_space
        self.direction = direction
        self.x = x
        self.y = y
        self.group_id = group_id
        self.cv = cv
        self.scoring = scoring
        self.params_post_processing = params_post_processing
        self._best_score = -np.inf if direction == 'maximize' else np.inf
        self.best_score = last_best_score
        self.weight_column = weight_column
        self.n_folds_start_prune = n_folds_start_prune
        self.has_pruner = has_pruner
        self.parallel = parallel
        self.parallel_available_gpus = parallel_available_gpus
        if self.has_pruner:
            warnings.warn(
                "The 'has_pruner' argument is deprecated and will be removed in a future version. ",
                DeprecationWarning,
                stacklevel=2
            )
        self.trial_timeout = trial_timeout
        if self.trial_timeout is not None:
            if self.parallel:
                warnings.warn('Trial timeout is not supported when parallel mode is enabled. Ignoring this parameter.')
        self.error_handling = error_handling

    @property
    def best_score(self):
        return self._best_score

    @best_score.setter
    def best_score(self, value):
        if value is not None:
            if self.direction == 'maximize':
                self._best_score = max(self._best_score, value)
            else:
                self._best_score = min(self._best_score, value)

    def _get_params(self, trial):
        params = {
            name: trial._suggest(name, distribution)
            for name, distribution in self.param_distributions.items()
        }
        return params

    @staticmethod
    def get_model_iterations(cb_model):
        iterations = cb_model.get_param('iterations')
        if iterations is None:
            iterations = 1000
        return iterations

    def eval_model(self, cb_model, val_pool, metric):
        score = cb_model.eval_metrics(val_pool, metrics=metric, ntree_start=self.get_model_iterations(cb_model) - 1)
        return score[metric][0]

    def _cross_val_score(self, model, trial):
        validator = CrossValidator(model, self.x, scoring=self.scoring, y=self.y, cv=self.cv, optuna_trial=trial,
                                   n_folds_start_prune=self.n_folds_start_prune, weight_column=self.weight_column)
        if self.parallel:
            return np.mean(
                validator.parallel_fit(available_gpus=self.parallel_available_gpus)[self.scoring])
        else:
            return np.mean(
                stopit_after_timeout(self.trial_timeout, raise_exception=True)(validator.fit)()[self.scoring])

    def __call__(self, trial):
        if callable(self.param_distributions):
            params = self.param_distributions(trial)
        else:
            params = self._get_params(trial)
        if callable(self.params_post_processing):
            params = self.params_post_processing(params, trial)
        model = self.model.copy()
        try:
            result = self._cross_val_score(model.set_params(**params), trial)
        except TimeoutError:
            raise TrialPruned('Trial was pruned due to timeout')
        except Exception as e:
            if self.error_handling == 'raise':
                raise
            raise TrialPruned(f'Trial was pruned due to error: {e}')
        self.best_score = max(self.best_score, result) if self.direction == 'maximize' else min(self.best_score, result)
        return result


def update_params(fn):
    """Decorator for updating _param dict in CatboostParamSpace class"""

    def wrapper(self, value):
        result = fn(self, value)
        param_name = fn.__name__
        self._params[param_name] = getattr(self, param_name)
        return result

    return wrapper


class CatboostParamSpace:
    """
    Class for defining Catboost hyperparameters space for Optuna

    Parameters
    ----------
    task_type : str
        Task type. 'CPU' or 'GPU'.
    cook_params : Optional[List[str]]
        List of parameters for cooking. Example ['iterations', 'learning_rate', 'depth'].
    params_preset : str
        Preset for parameters. 'small', 'general', 'extended', 'ctr'.
    """

    def __init__(self, task_type: str = 'CPU', cook_params: Optional[List[str]] = None, params_preset: str = 'general'):
        self.cook_params = cook_params
        self.params_preset = params_preset
        self._task_type = task_type
        self._iterations = IntDistribution(100, 5000)
        self._learning_rate = FloatDistribution(1e-3, 1e-1, log=True)
        self._depth = IntDistribution(2, 15)
        self._grow_policy = CategoricalDistribution(['SymmetricTree', 'Depthwise', 'Lossguide'])
        self._l2_leaf_reg = FloatDistribution(1e-2, 1000.0, log=True)
        self._random_strength = FloatDistribution(1e-2, 10.0, log=True)
        if self._task_type == 'CPU':
            self._bootstrap_type = CategoricalDistribution(['Bayesian', 'MVS', 'Bernoulli', 'No'])
            self._score_function = CategoricalDistribution(['Cosine', 'L2'])
            self._rsm = FloatDistribution(0.01, 1.0)
            self.simple_ctr_type = CategoricalDistribution(
                ['Borders', 'Buckets', 'BinarizedTargetMeanValue', 'Counter'])
            self.combinations_ctr_type = CategoricalDistribution(
                ['Borders', 'Buckets', 'BinarizedTargetMeanValue', 'Counter'])
            self.simple_ctr_border_type = 'Uniform'
            self.combinations_ctr_border_type = 'Uniform'
            self.target_border_type = CategoricalDistribution(
                ['Median', 'Uniform', 'UniformAndQuantiles', 'MaxLogSum', 'MinEntropy', 'GreedyLogSum']
            )
        else:
            self._bootstrap_type = CategoricalDistribution(['Bayesian', 'Poisson', 'Bernoulli', 'MVS', 'No'])
            self._score_function = CategoricalDistribution(['Cosine', 'L2', 'NewtonCosine', 'NewtonL2'])
            self.simple_ctr_type = CategoricalDistribution(
                ['Borders', 'Buckets', 'FeatureFreq', 'FloatTargetMeanValue'])
            self.combinations_ctr_type = CategoricalDistribution(
                ['Borders', 'Buckets', 'FeatureFreq', 'FloatTargetMeanValue'])
            self.simple_ctr_border_type = CategoricalDistribution(
                ['Median', 'Uniform', 'UniformAndQuantiles', 'MaxLogSum', 'MinEntropy', 'GreedyLogSum'])
            self.combinations_ctr_border_type = CategoricalDistribution(['Median', 'Uniform'])
        self._max_ctr_complexity = IntDistribution(1, 10)
        self._max_bin = IntDistribution(8, 512)
        self._min_data_in_leaf = IntDistribution(1, 32)
        self._one_hot_max_size = IntDistribution(2, 255)
        self._bagging_temperature = FloatDistribution(0, 10)
        self._subsample = FloatDistribution(0.1, 1, log=True)
        self.simple_ctr_border_count = IntDistribution(1, 255)
        self.combinations_ctr_border_count = IntDistribution(1, 255)
        self._leaf_estimation_method = CategoricalDistribution(['Newton', 'Gradient', 'Exact'])
        self.boost_from_average = CategoricalDistribution([True, False])
        self._model_size_reg = FloatDistribution(0, 1)
        self.langevin = CategoricalDistribution([True, False])
        self.boosting_type = CategoricalDistribution(['Ordered', 'Plain'])
        self._fold_len_multiplier = FloatDistribution(1.1, 2)
        self._params = self._get_params_presets()

    @property
    def fold_len_multiplier(self):
        return self._fold_len_multiplier

    @fold_len_multiplier.setter
    @update_params
    def fold_len_multiplier(self, value: Tuple[float, float]):
        self._fold_len_multiplier = FloatDistribution(*value)

    @property
    def model_size_reg(self):
        return self._model_size_reg

    @model_size_reg.setter
    @update_params
    def model_size_reg(self, value: Tuple[float, float]):
        self._model_size_reg = FloatDistribution(*value)

    @property
    def task_type(self):
        return self._task_type

    @task_type.setter
    @update_params
    def task_type(self, value):
        if value not in ['CPU', 'GPU']:
            raise ValueError('task_type must be "CPU" or "GPU"')
        self._task_type = value

    @property
    def leaf_estimation_method(self):
        return self._leaf_estimation_method

    @leaf_estimation_method.setter
    @update_params
    def leaf_estimation_method(self, value: List[str]):
        for val in value:
            if val not in ['Newton', 'Gradient', 'Exact']:
                raise ValueError('leaf_estimation_method must be "Newton", "Gradient" or "Exact"')
        self._leaf_estimation_method = CategoricalDistribution(value)

    @property
    def bagging_temperature(self):
        return self._bagging_temperature

    @bagging_temperature.setter
    @update_params
    def bagging_temperature(self, value: Tuple[float, float]):
        self._bagging_temperature = FloatDistribution(*value)

    @property
    def subsample(self):
        return self._subsample

    @subsample.setter
    @update_params
    def subsample(self, value: Tuple[float, float]):
        self._subsample = FloatDistribution(*value)

    @property
    def one_hot_max_size(self):
        return self._one_hot_max_size

    @one_hot_max_size.setter
    @update_params
    def one_hot_max_size(self, value: Tuple[int, int]):
        self._one_hot_max_size = IntDistribution(*value)

    @property
    def min_data_in_leaf(self):
        return self._min_data_in_leaf

    @min_data_in_leaf.setter
    @update_params
    def min_data_in_leaf(self, value: Tuple[int, int]):
        self._min_data_in_leaf = IntDistribution(*value)

    @property
    def max_bin(self):
        return self._max_bin

    @max_bin.setter
    @update_params
    def max_bin(self, value: Tuple[int, int]):
        self._max_bin = IntDistribution(*value)

    @property
    def rsm(self):
        return self._rsm

    @rsm.setter
    @update_params
    def rsm(self, value: Tuple[float, float]):
        self._rsm = FloatDistribution(*value)

    @property
    def l2_leaf_reg(self):
        return self._l2_leaf_reg

    @l2_leaf_reg.setter
    @update_params
    def l2_leaf_reg(self, value: Tuple[float, float]):
        self._l2_leaf_reg = FloatDistribution(*value)

    @property
    def max_ctr_complexity(self):
        return self._max_ctr_complexity

    @max_ctr_complexity.setter
    @update_params
    def max_ctr_complexity(self, value: Tuple[int, int]):
        self._max_ctr_complexity = IntDistribution(*value)

    @property
    def score_function(self):
        return self._score_function

    @score_function.setter
    @update_params
    def score_function(self, value: List[str]):
        if self.task_type == 'CPU':
            for val in value:
                if val not in ['Cosine', 'L2']:
                    raise ValueError('score_function must be "Cosine" or "L2"')
        else:
            for val in value:
                if val not in ['Cosine', 'L2', 'NewtonCosine', 'NewtonL2']:
                    raise ValueError('score_function must be "Cosine", "L2", "NewtonCosine" or "NewtonL2"')
        self._score_function = CategoricalDistribution(value)

    @property
    def random_strength(self):
        return self._random_strength

    @random_strength.setter
    @update_params
    def random_strength(self, value: Tuple[float, float]):
        self._random_strength = FloatDistribution(*value)

    @property
    def learning_rate(self):
        return self._learning_rate

    @learning_rate.setter
    @update_params
    def learning_rate(self, value: Tuple[float, float]):
        self._learning_rate = FloatDistribution(*value)

    @property
    def iterations(self):
        return self._iterations

    @iterations.setter
    @update_params
    def iterations(self, value: Tuple[int, int]):
        self._iterations = IntDistribution(*value)

    @property
    def depth(self):
        return self._depth

    @depth.setter
    @update_params
    def depth(self, value: Tuple[int, int]):
        self._depth = IntDistribution(*value)

    @property
    def grow_policy(self):
        return self._grow_policy

    @grow_policy.setter
    @update_params
    def grow_policy(self, value: List[str]):
        for val in value:
            if val not in ['SymmetricTree', 'Depthwise', 'Lossguide']:
                raise ValueError('grow_policy must be "SymmetricTree" "Lossquide" or "Depthwise"')
        self._grow_policy = CategoricalDistribution(value)

    @property
    def bootstrap_type(self):
        return self._bootstrap_type

    @bootstrap_type.setter
    @update_params
    def bootstrap_type(self, value: List[str]):
        if self._task_type == 'CPU':
            for val in value:
                if val not in ['Bayesian', 'MVS', 'Bernoulli', 'No']:
                    raise ValueError('bootstrap_type must be "Bayesian", "MVS", "No" or "Bernoulli" for CPU task_type')
            self._bootstrap_type = CategoricalDistribution(value)
        else:
            for val in value:
                if val not in ['Bayesian', 'Poisson', 'Bernoulli', 'MVS', 'No']:
                    raise ValueError(
                        'bootstrap_type must be "Bayesian", "Poisson", "Bernoulli", "No" or "MVS" for GPU task_type')
            self._bootstrap_type = CategoricalDistribution(value)

    def _get_params_presets(self):
        """ Get parameters presets"""

        if self.cook_params is not None:
            params = {
                name: getattr(self, name)
                for name in self.cook_params
            }
        elif self.params_preset == 'small':
            params = {
                'iterations': self.iterations,
                'learning_rate': self.learning_rate,
                'depth': self.depth,
                'grow_policy': self.grow_policy,
                'l2_leaf_reg': self.l2_leaf_reg,
                'random_strength': self.random_strength,
                'bootstrap_type': self.bootstrap_type,
            }

        elif self.params_preset == 'general':
            params = {
                'iterations': self.iterations,
                'learning_rate': self.learning_rate,
                'depth': self.depth,
                'grow_policy': self.grow_policy,
                'l2_leaf_reg': self.l2_leaf_reg,
                'random_strength': self.random_strength,
                'bootstrap_type': self.bootstrap_type,
                'max_bin': self.max_bin,
                'score_function': self.score_function,
            }
            if self.task_type == 'CPU':
                params['rsm'] = self.rsm
        elif self.params_preset == 'extended':
            params = {
                'iterations': self.iterations,
                'learning_rate': self.learning_rate,
                'depth': self.depth,
                'grow_policy': self.grow_policy,
                'l2_leaf_reg': self.l2_leaf_reg,
                'random_strength': self.random_strength,
                'bootstrap_type': self.bootstrap_type,
                'max_bin': self.max_bin,
                'min_data_in_leaf': self.min_data_in_leaf,
                'score_function': self.score_function,
                'leaf_estimation_method': self.leaf_estimation_method,
                'boost_from_average': self.boost_from_average,
            }
            if self.task_type == 'CPU':
                params['rsm'] = self.rsm
        elif self.params_preset == 'ctr':
            params = {
                'one_hot_max_size': self.one_hot_max_size,
                'max_ctr_complexity': self.max_ctr_complexity,
                'model_size_reg': self.model_size_reg,
                'simple_ctr': f'{self.simple_ctr_type}:CtrBorderCount={self.simple_ctr_border_count}:' \
                              f'CtrBorderType={self.simple_ctr_border_type}',
                'combinations_ctr': f'{self.combinations_ctr_type}:CtrBorderCount={self.combinations_ctr_border_count}:' \
                                    f'CtrBorderType={self.combinations_ctr_border_type}'
            }
        else:
            raise ValueError('params_type must be "extended", "general", "ctr" or "small"')

        return params

    def add_params(self, params: List[str]):
        """ Add parameters to the parameter space
        Parameters
        ----------
        params : List[str]
            List of parameters to add
        """
        for param in params:
            self._params[param] = getattr(self, param)

    def del_params(self, params: List[str]):
        """ Delete parameters from the parameter space
        Parameters
        ----------
        params : List[str]
            List of parameters to delete
        """
        for param in params:
            self._params.pop(param)

    def get_params_space(self):
        """ Show parameters space"""
        return self._params

    @staticmethod
    def get_ctr_params(
            ctr_type='Borders',
            ctr_border_count=15,
            ctr_border_type='Uniform',
            target_border_count=1,
            target_border_type='MinEntropy',
    ):
        """ Get CTR parameters"""
        return f'{ctr_type}:CtrBorderCount={ctr_border_count}:CtrBorderType={ctr_border_type}'

    def __call__(self, trial):

        if self.params_preset in ['small', 'general', 'extended'] or self.cook_params is not None:
            params = {
                name: trial._suggest(name, distribution)
                for name, distribution in self._params.items()
            }
            if self.params_preset in ['small', 'general', 'extended']:
                if params['bootstrap_type'] != 'No':
                    if params["bootstrap_type"] == "Bayesian":
                        params["bagging_temperature"] = trial._suggest("bagging_temperature", self.bagging_temperature)
                    else:
                        params["subsample"] = trial._suggest("subsample", self.subsample)
        elif self.params_preset == 'ctr':
            params = {
                'one_hot_max_size': trial._suggest('one_hot_max_size', self.one_hot_max_size),
                'max_ctr_complexity': trial._suggest('max_ctr_complexity', self.max_ctr_complexity),
                'model_size_reg': trial._suggest('model_size_reg', self.model_size_reg),
            }
            simple_ctr_type = trial._suggest('simple_ctr_type', self.simple_ctr_type)
            combinations_ctr_type = trial._suggest('combinations_ctr_type', self.combinations_ctr_type)
            simple_ctr_border_count = trial._suggest('simple_ctr_border_count', self.simple_ctr_border_count)
            combinations_ctr_border_count = trial._suggest('combinations_ctr_border_count',
                                                           self.combinations_ctr_border_count)
            if simple_ctr_type != 'FeatureFreq':
                if self.task_type == 'GPU':
                    simple_ctr_border_type = trial._suggest('simple_ctr_border_type',
                                                            self.simple_ctr_border_type)
                else:
                    simple_ctr_border_type = 'Uniform'

            else:
                simple_ctr_border_type = 'MinEntropy'

            if combinations_ctr_type != 'FeatureFreq':
                if self.task_type == 'GPU':
                    combinations_ctr_border_type = trial._suggest('combinations_ctr_border_type',
                                                                  self.combinations_ctr_border_type)
                else:
                    combinations_ctr_border_type = 'Uniform'
            else:
                combinations_ctr_border_type = 'Median'
            params['simple_ctr'] = self.get_ctr_params(
                ctr_type=simple_ctr_type,
                ctr_border_count=simple_ctr_border_count,
                ctr_border_type=simple_ctr_border_type
            )
            params['combinations_ctr'] = self.get_ctr_params(
                ctr_type=combinations_ctr_type,
                ctr_border_count=combinations_ctr_border_count,
                ctr_border_type=combinations_ctr_border_type
            )
        else:
            raise ValueError('params_preset must be "extended", "general", "ctr" or "small"')
        return params
