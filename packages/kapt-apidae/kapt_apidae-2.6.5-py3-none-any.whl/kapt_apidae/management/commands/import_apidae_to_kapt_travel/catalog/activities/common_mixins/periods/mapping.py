# Standard Library
import datetime

# Local application / specific library imports
from .utils import datepaques, jourmoins, jourplus, numjoursem
from kapt_apidae.models import (
    CLOSURE_SPECIAL_DATE,
    OPENING_PERIOD_DAY_CHOICES,
    OPENING_PERIOD_MONTHDAY_CHOICES,
)


CORRESPONDENCE_WEEK_DAYS = {
    OPENING_PERIOD_DAY_CHOICES.LUNDI: 0,
    OPENING_PERIOD_DAY_CHOICES.MARDI: 1,
    OPENING_PERIOD_DAY_CHOICES.MERCREDI: 2,
    OPENING_PERIOD_DAY_CHOICES.JEUDI: 3,
    OPENING_PERIOD_DAY_CHOICES.VENDREDI: 4,
    OPENING_PERIOD_DAY_CHOICES.SAMEDI: 5,
    OPENING_PERIOD_DAY_CHOICES.DIMANCHE: 6,
}

CORRESPONDENCE_MONTH_DAYS = {
    OPENING_PERIOD_MONTHDAY_CHOICES.D_1ER_LUNDI: (0, 0),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_2EME_LUNDI: (0, 1),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_3EME_LUNDI: (0, 2),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_4EME_LUNDI: (0, 3),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_DERNIER_LUNDI: (0, None),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_1ER_MARDI: (1, 0),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_2EME_MARDI: (1, 1),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_3EME_MARDI: (1, 2),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_4EME_MARDI: (1, 3),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_DERNIER_MARDI: (1, None),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_1ER_MERCREDI: (2, 0),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_2EME_MERCREDI: (2, 1),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_3EME_MERCREDI: (2, 2),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_4EME_MERCREDI: (2, 3),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_DERNIER_MERCREDI: (2, None),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_1ER_JEUDI: (3, 0),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_2EME_JEUDI: (3, 1),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_3EME_JEUDI: (3, 2),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_4EME_JEUDI: (3, 3),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_DERNIER_JEUDI: (3, None),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_1ER_VENDREDI: (4, 0),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_2EME_VENDREDI: (4, 1),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_3EME_VENDREDI: (4, 2),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_4EME_VENDREDI: (4, 3),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_DERNIER_VENDREDI: (4, None),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_1ER_SAMEDI: (5, 0),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_2EME_SAMEDI: (5, 1),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_3EME_SAMEDI: (5, 2),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_4EME_SAMEDI: (5, 3),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_DERNIER_SAMEDI: (5, None),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_1ER_DIMANCHE: (6, 0),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_2EME_DIMANCHE: (6, 1),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_3EME_DIMANCHE: (6, 2),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_4EME_DIMANCHE: (6, 3),
    OPENING_PERIOD_MONTHDAY_CHOICES.D_DERNIER_DIMANCHE: (6, None),
}

SIMPLE_CORRESPONDENCE_SPECIAL_DATES = {
    CLOSURE_SPECIAL_DATE.PREMIER_JANVIER: (1, 1),
    CLOSURE_SPECIAL_DATE.PREMIER_MAI: (5, 1),
    CLOSURE_SPECIAL_DATE.HUIT_MAI: (5, 8),
    CLOSURE_SPECIAL_DATE.QUATORZE_JUILLET: (7, 14),
    CLOSURE_SPECIAL_DATE.QUINZE_AOUT: (8, 15),
    CLOSURE_SPECIAL_DATE.PREMIER_NOVEMBRE: (11, 1),
    CLOSURE_SPECIAL_DATE.ONZE_NOVEMBRE: (11, 11),
    CLOSURE_SPECIAL_DATE.VINGT_CINQ_DECEMBRE: (12, 25),
    CLOSURE_SPECIAL_DATE.BERCHTOLDSTAG: (1, 2),
    CLOSURE_SPECIAL_DATE.SAINT_JOSEPH: (3, 19),
    CLOSURE_SPECIAL_DATE.IMMACULEE_CONCEPTION: (12, 8),
}


def correspondence_special_dates(closure_special_date_key, year):
    """Liste des jours fériés France et Suisse"""

    # Simple mapping
    if closure_special_date_key in SIMPLE_CORRESPONDENCE_SPECIAL_DATES:
        month, day = SIMPLE_CORRESPONDENCE_SPECIAL_DATES[closure_special_date_key]
        return datetime.date(year, month, day)

    # Special dates
    dp = datepaques(year)

    # Jour de l'an
    d = [1, 1, year]

    # Vendredi saint
    d = jourmoins(dp, -2)
    if closure_special_date_key == CLOSURE_SPECIAL_DATE.VENDREDI_SAINT:
        return datetime.date(d[2], d[1], d[0])

    # Dimanche de Paques
    d = dp

    # Lundi de Paques
    d = jourplus(dp, +1)
    if closure_special_date_key == CLOSURE_SPECIAL_DATE.LUNDI_PAQUES:
        return datetime.date(d[2], d[1], d[0])

    # Fête du travail
    d = [1, 5, year]

    # Victoire des allies 1945
    d = [8, 5, year]

    # Jeudi de l'Ascension
    d = jourplus(dp, +39)
    if closure_special_date_key == CLOSURE_SPECIAL_DATE.ASCENSION:
        return datetime.date(d[2], d[1], d[0])

    # Dimanche de Pentecote
    d = jourplus(dp, +49)

    # Lundi de Pentecote
    d = jourplus(d, +1)
    if closure_special_date_key == CLOSURE_SPECIAL_DATE.LUNDI_PENTECOTE:
        return datetime.date(d[2], d[1], d[0])

    # Fête dieu
    d = jourplus(dp, +60)
    if closure_special_date_key == CLOSURE_SPECIAL_DATE.FETE_DIEU:
        return datetime.date(d[2], d[1], d[0])

    # Fete Nationale
    d = [14, 7, year]

    # Assomption
    d = [15, 8, year]

    # Toussaint
    d = [1, 11, year]

    # Armistice 1918
    d = [11, 11, year]

    # Jour de Noel
    d = [25, 12, year]

    # Saint Etienne (pour l'Alsace-Moselle)
    d = [26, 12, year]

    # Lundi de jeune federal
    d_premier_jour_septembre = [1, 9, year]
    n_premier_jour_septembre = numjoursem(d_premier_jour_septembre)
    premier_dimanche = jourplus(d_premier_jour_septembre, 7 - n_premier_jour_septembre)
    d = jourplus(premier_dimanche, 15)
    if closure_special_date_key == CLOSURE_SPECIAL_DATE.LUNDI_DU_JEUNE_FEDERAL:
        return datetime.date(d[2], d[1], d[0])
