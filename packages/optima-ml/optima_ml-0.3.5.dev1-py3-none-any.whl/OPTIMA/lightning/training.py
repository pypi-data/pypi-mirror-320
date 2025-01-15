# -*- coding: utf-8 -*-
"""Collection of classes and functions specific to the training of Lightning models."""
import os
import logging

import numpy as np
from lightning.pytorch.callbacks import Callback

import OPTIMA.core.training
import OPTIMA.core.model
import OPTIMA.lightning.inputs


class EarlyStopperForLightningTuning(OPTIMA.core.training.EarlyStopperForTuning, Callback):
    """_summary_.

    Returns
    -------
    _type_
        _description_
    """

    def __init__(self, *args, **kwargs):
        """_summary_.

        Parameters
        ----------
        *args : _type_
            _description_
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        # provide the dataloaders to the EarlyStopper
        OPTIMA.core.training.EarlyStopperForTuning.__init__(self, *args, **kwargs)
        Callback.__init__(self)

    def on_validation_end(self, trainer, pl_module):
        """_summary_.

        Parameters
        ----------
        trainer : _type_
            _description_
        pl_module : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        logs = {}
        for metric, value in trainer.callback_metrics.items():
            logs[metric] = value.detach().cpu().numpy()

        super().at_epoch_end(trainer.current_epoch, logs=logs, pl_module=pl_module, trainer=trainer)

    def on_train_end(self, trainer, pl_module) -> None:
        """_summary_.

        Parameters
        ----------
        trainer : _type_
            _description_
        pl_module : _type_
            _description_

        Returns
        -------
        None
            _description_
        """
        super().finalize()

    def get_train_val_metric_names(self, metric, **kwargs: dict):
        """_summary_.

        Parameters
        ----------
        metric : _type_
            _description_
        **kwargs : dict
            _description_

        Returns
        -------
        _type_
            _description_
        """
        return f"train_{metric}", f"val_{metric}"

    def get_weights(self, pl_module, **kwargs) -> list[np.ndarray]:
        """_summary_.

        Parameters
        ----------
        pl_module : _type_
            _description_
        **kwargs : _type_
            _description_

        Returns
        -------
        list[np.ndarray]
            _description_
        """
        return pl_module.state_dict()  # ist ein pytorch befehl
        # return self.trainer.model.state_dict()

    def set_weights(self, weights: list[np.ndarray], pl_module, **kwargs):
        """_summary_.

        Parameters
        ----------
        weights : list[np.ndarray]
            _description_
        pl_module : _type_
            _description_
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        pl_module.load_state_dict(weights)

    def get_abstract_model(self, trainer, pl_module) -> OPTIMA.core.model.AbstractModel:
        """_summary_.

        Parameters
        ----------
        trainer : _type_
            _description_
        pl_module : _type_
            _description_

        Returns
        -------
        OPTIMA.core.model.AbstractModel
            _description_
        """
        return OPTIMA.core.model.AbstractModel(
            run_config=self.run_config,
            model=pl_module,
            model_config=self.model_config,
            input_handler=self.input_handler,
            pl_trainer=trainer,
        )

    def save_model(self, output_dir: str, model_name: str, trainer, **kwargs):
        """_summary_.

        Parameters
        ----------
        output_dir : str
            _description_
        model_name : str
            _description_
        trainer : _type_
            _description_
        **kwargs : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        try:
            trainer.save_checkpoint(filepath=os.path.join(output_dir, f"{model_name}.ckpt"))
        except BlockingIOError:
            logging.warning(
                "BlockingIOError: [Errno 11] Unable to create file (unable to lock file, errno = 11, error message "
                "= 'Resource temporarily unavailable'). Skipping the save of this checkpoint!"
            )
        except OSError:
            logging.warning("OSError detected. Skipping the save of this checkpoint!")

    def stop_training(self, trainer, **kwargs) -> None:
        """Mark the training for termination due to Early Stopping.

        Parameters
        ----------
        trainer : _type_
            _description_
        **kwargs : _type_
            _description_
        """
        trainer.should_stop = True
