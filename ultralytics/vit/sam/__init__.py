from ultralytics.yolo.cfg import get_cfg

from .build import build_sam
from .predict import Predictor


class SAM:

    def __init__(self, model='sam_b.pt') -> None:
        if model and not (model.endswith('.pt') or model.endswith('.pth')):
            # Should raise AssertionError instead?
            raise NotImplementedError('Segment anything prediction requires pre-trained checkpoint')
        self.model = build_sam(model)
        self.predictor = None  # reuse predictor

    def predict(self, source, stream=False, **kwargs):
        overrides = dict(conf=0.25, task='segment')
        overrides.update(kwargs)  # prefer kwargs
        if not self.predictor:
            self.predictor = Predictor(overrides=overrides)
            self.predictor.setup_model(model=self.model)
        else:  # only update args if predictor is already setup
            self.predictor.args = get_cfg(self.predictor.args, overrides)
        return self.predictor(source, stream=stream)

    def train(self, **kwargs):
        raise NotImplementedError("SAM models don't support training")

    def val(self, **kwargs):
        raise NotImplementedError("SAM models don't support validation")
