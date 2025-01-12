"""This module contains a model pipeline that recommends items using the Elliot framework.

Classes:

    RecommendationPipelineElliot: can batch recommendations from multiple elliot models.

Deprecated:

from elliot.run import run_experiment

class RecommendationPipelineElliot(RecommendationPipeline):
    ...
    def train_and_test_model(
            self,
            model: ElliotRecommender,
            model_dir: str,
            is_running: Callable[[], bool],
            **kwargs) -> str:
        ...
        create_yml(yml_path, data, self.event_dispatcher)

        run_experiment(yml_path)

        delete_dir(temp_dir, self.event_dispatcher)
        ...
    ...

This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)
"""

import os
from typing import Callable

import numpy as np
import pandas as pd

from ...core.core_constants import MODEL_RATINGS_FILE
from ...core.io.io_create import create_dir, create_yml
from ...core.io.io_delete import delete_dir, delete_file
from ..algorithms.elliot.elliot_recommender import ElliotRecommender
from .recommendation_pipeline import RecommendationPipeline


class RecommendationPipelineElliot(RecommendationPipeline):
    """Recommendation Pipeline implementation for the Elliot framework."""

    def train_and_test_model(
            self,
            model: ElliotRecommender,
            model_dir: str,
            is_running: Callable[[], bool],
            **kwargs) -> None:
        """Train and test the specified model.

        Convert the model configuration into a yml file that is accepted by the framework.
        Feed it to the framework to obtain results, clear unwanted artifacts and modify the
        ratings file so that it conforms to the standard convention.

        Args:
            model: the model that needs to be trained.
            model_dir: the path of the directory where the computed ratings can be stored.
            is_running: function that returns whether the pipeline
                is still running. Stops early when False is returned.

        Keyword Args:
            num_items(int): the number of item recommendations to produce.

        Raises:
            ArithmeticError: possibly raised by a model on training or testing.
            MemoryError: possibly raised by a model on training or testing.
            RuntimeError: possibly raised by a model on training or testing.
        """
        params = model.get_params()
        params['meta'] = {'verbose': False, 'save_recs': True, 'save_weights': False}

        top_k = kwargs['num_items']

        temp_dir = create_dir(os.path.join(model_dir, 'temp'), self.event_dispatcher)
        yml_path = os.path.join(temp_dir, 'config.yml')

        data = {
            'experiment': {
                'dataset': 'df',
                'data_config': {
                    'strategy': 'fixed',
                    'train_path': os.path.join('..', '..', 'train_set.tsv'),
                    'test_path': os.path.join('..', '..', 'test_set.tsv'),
                },
                'top_k': top_k,
                'models': {
                    model.get_name(): params
                },
                'evaluation': {
                    'simple_metrics': ['Precision']
                },
                'path_output_rec_result': model_dir,
                'path_output_rec_weight': temp_dir,
                'path_output_rec_performance': temp_dir
            }
        }

        create_yml(yml_path, data, self.event_dispatcher)

        # run_experiment(yml_path)

        delete_dir(temp_dir, self.event_dispatcher)
        if params.get('epochs'):
            # remove everything so that only the final epochs file remains
            self.clear_unused_epochs(params['epochs'], model_dir)

        self.reconstruct_rank_column(model_dir, top_k)

    def clear_unused_epochs(self, num_epochs: int, model_dir: str) -> None:
        """Clear unused epochs from the model output directory.

        Recommenders with an 'epochs' parameter will generate computed ratings
        for each epoch. Only the final epoch is needed.

        Args:
            num_epochs: the number of epochs that was run by the algorithm.
            model_dir: the directory where the computed ratings are stored.
        """
        used_epoch = 'it=' + str(num_epochs)
        for file in os.listdir(model_dir):
            file_name = os.fsdecode(file)
            # skip model settings json
            if 'settings.json' in file_name:
                continue

            file_path = os.path.join(model_dir, file_name)

            if used_epoch not in file_name:
                delete_file(file_path, self.event_dispatcher)

    def reconstruct_rank_column(self, model_dir: str, top_k: int) -> None:
        """Reconstruct the rank column in the result file that the framework generated.

        Args:
            model_dir: the directory where the computed ratings are stored.
            top_k: the topK that was used to compute the ratings.
        """
        result_file_path = self.rename_result(model_dir)
        result = pd.read_csv(
            result_file_path,
            sep='\t',
            header=None,
            names=['user', 'item', 'score']
        )

        # create topK ranking array
        row_count = len(result)
        ranks = np.zeros(row_count)
        for i in range(row_count):
            ranks[i] = i % top_k + 1

        # add rank column
        result['rank'] = ranks
        result['rank'] = result['rank'].astype(int)

        # overwrite result
        result[['rank', 'user', 'item', 'score']].to_csv(
            result_file_path,
            sep='\t',
            header=True,
            index=False
        )

    @staticmethod
    def rename_result(model_dir: str) -> str:
        """Rename the computed ratings file to be consistent with other pipelines.

        Args:
            model_dir: the directory where the computed ratings are stored.

        Returns:
            the file path of the result after renaming.
        """
        for file in os.listdir(model_dir):
            file_name = os.fsdecode(file)
            # skip the model settings json
            if '.tsv' not in file_name:
                continue

            src_path = os.path.join(model_dir, file_name)
            dst_path = os.path.join(model_dir, MODEL_RATINGS_FILE)

            os.rename(src_path, dst_path)

            return dst_path
