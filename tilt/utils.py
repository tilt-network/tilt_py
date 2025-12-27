import warnings


def _is_jupyter():
    try:
        from IPython.core.getipython import get_ipython

        ipy = get_ipython()
        return ipy is not None and "IPKernelApp" in ipy.config
    except (ImportError, NameError, AttributeError):
        return False


if _is_jupyter():
    try:
        import nest_asyncio

        nest_asyncio.apply()
    except ImportError:
        pass

warnings.filterwarnings(
    "ignore",
    message='install "ipywidgets" for Jupyter support',
    category=UserWarning,
    module="rich.live",
)
