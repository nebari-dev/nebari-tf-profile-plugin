from nebari.hookspecs import hookimpl

from .main import TFProfileStage


@hookimpl
def nebari_stage():
    return [TFProfileStage]
