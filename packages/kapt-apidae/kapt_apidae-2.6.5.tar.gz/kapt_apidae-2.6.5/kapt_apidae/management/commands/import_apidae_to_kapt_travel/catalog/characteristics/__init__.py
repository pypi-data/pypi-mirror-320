# Standard Library
from collections import OrderedDict

# Third party
from .generated_characteristics import GENERATED_LABELS, GENERATED_RESTAURANT_RANKING
from .handmade_characteristics import (
    HANDMADE_LABELS_1,
    HANDMADE_LABELS_2,
    HANDMADE_RESTAURANT_RANKING,
)


# Use try/except to handle the first load when GENERATED_something is not yet in generated_characteristics
try:
    GENERATED_LABELS
except NameError:
    LABELS = OrderedDict(
        list(HANDMADE_LABELS_1.items()) + list(HANDMADE_LABELS_2.items())
    )
else:
    LABELS = OrderedDict(
        list(HANDMADE_LABELS_1.items())
        + list(GENERATED_LABELS.items())
        + list(HANDMADE_LABELS_2.items())
    )

try:
    GENERATED_RESTAURANT_RANKING
except NameError:
    RESTAURANT_RANKING = OrderedDict(list(HANDMADE_RESTAURANT_RANKING.items()))
else:
    RESTAURANT_RANKING = OrderedDict(
        list(GENERATED_RESTAURANT_RANKING.items())
        + list(HANDMADE_RESTAURANT_RANKING.items())
    )
