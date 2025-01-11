# Standard Library
from collections import OrderedDict


# See here for more info on characteristics: https://base.apidae-tourisme.com/diffuser/dev-tools/referentiel/elements-reference/

SPOKEN_LANGUAGES = {
    1189: "de",
    1192: "en",
    1194: "es",
    1197: "fr",
    1200: "it",
    1202: "nl",
    1205: "ru",
    1206: "zh-cn",
    4306: "pt",
    4602: "ja",
    4603: "ko",
    4604: "pl",
    4604: "pl",  # Polonais
    4605: "ar",
    4873: "oc",
    5118: "da",
    5421: "el",  # Grec
    5467: "cs",  # Tchèque
    5468: "sv",  # Suédois
    5469: "lsf",  # Langue des signes française
    5690: "co",  # Corse
    5989: "hy",  # Arménien
    5990: "bg",  # Bulgare
    5991: "ca",  # Catalan
    5992: "af",  # Egyptien ~
    5993: "he",  # Hébreu
    5994: "hu",  # Hongrois
    5995: "no",  # Norvégien
    5996: "fr",  # Provencal ~
    5997: "ro",  # Roumain
    5999: "th",  # Thaï
    6000: "vi",  # Vietnamien
    6434: "sk",  # Slovaque
}

CARACTERISTIQUES = {
    756: "internet-access",
    797: "cable-satellite-tv",
    824: "heating",
    838: "baby",
    842: "wifi-internet_connection",
    847: "140-cm",
    848: "shared-toilets",
    850: "private-lavatory",
    876: "kitchen",
    877: "fireplace",
    880: "90-cm-bunk-beds",
    882: "internet-access",
    893: "air-conditioning",
    895: "freezer",
    898: "kitchen",
    902: "shower",
    796: "bath",
    904: "bed-linen-provided",
    907: "oven",
    917: "common-washing-machine",
    919: "private-washing-machine",
    922: "dishwasher",
    939: "socket-tv",
    941: "wired-internet-connection",
    943: "fridge",
    949: "dryer",
    950: "dryer",
    960: "phone",
    963: "color-tv",
    973: "separate-toilet",
    974: "private-bathroom",
    977: "private-bathroom",
    986: "central-heating",
    987: "electricity",
    999: "microwave",
    101: "90-cm",
    101: "160-cm",
    101: "baby-bed",
    101: "baby-changing-table",
    369: "private-bathroom",
    382: "private-bathroom",
    606: "two-wheeled-garage",
    672: "garden-furniture",
    710: "ground-closed",
    723: "terrace",
    741: "lavatory",
    776: "car-port",
    803: "barbecue",
    804: "air-conditioning",
    972: "garage-parking",
    105: "garage-parking",
    105: "independant",
    105: "garden",
    108: "attached",
    108: "attached",
    109: "pool",
    110: "plain-pied-house",
    131: "garage-parking",
    131: "garage-parking",
    132: "garage-parking",
    132: "garage-parking",
    132: "garage-parking",
    137: "dry-toilets",
    1376: "wind-powered",
    1378: "biomass",
    1381: "solar",
    1384: "geothermics",
    1388: "constructed-wetland",
    1418: "garage-parking",
    1421: "garage-parking",
    1477: "garden",
    1479: "garden",
    1504: "private-pool",
    1505: "shared-pool",
    1506: "private-pool",
    1507: "private-pool",
    1508: "private-pool",
    1115: "wifi-internet_connection",
    1116: "internet-access",
    687: "pets-welcome",
    916: "room-hire",
    934: "loan-of-bike",
    1025: "pets-supplement",
}

REFERENT_LABEL = ["2765", "3631", "2638", "2677", "2635", "2737"]

# Comes before generated labels
HANDMADE_LABELS_1 = OrderedDict(
    [
        # Handle duplicate labels
        (
            2615,
            {
                "identifier": "2638",
                "name_fr": "Bienvenue à la ferme",
                "name_en": "Bienvenue à la Ferme",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2616,
            {
                "identifier": "3631",
                "name_fr": "Camping Qualité France",
                "name_en": "Camping Qualité France",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2719,
            {
                "identifier": "2737",
                "name_fr": "Gîtes de France",
                "name_en": "Gîtes de France",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2617,
            {
                "identifier": "2737",
                "name_fr": "Gîtes de France / Pré Vert",
                "name_en": "Gîtes de France",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2634,
            {
                "identifier": "2737",
                "name_fr": "Gîtes de France",
                "name_en": "Gîtes de France",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2636,
            {
                "identifier": "3788",
                "name_fr": "Accueil paysan",
                "name_en": "Accueil paysan",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            4179,
            {
                "identifier": "3788",
                "name_fr": "Accueil paysan",
                "name_en": "Accueil paysan",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2639,
            {
                "identifier": "2702",
                "name_fr": "Fleurs de soleil",
                "name_en": "Fleurs de soleil",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2718,
            {
                "identifier": "2677",
                "name_fr": "Loisirs de France",
                "name_en": "Loisirs de France",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3578,
            {
                "identifier": "3593",
                "name_fr": "Gîtes et cheval",
                "name_en": "Gîtes et Cheval",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3579,
            {
                "identifier": "3594",
                "name_fr": "Gîtes de neige",
                "name_en": "Winter holidays Gîtes",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3580,
            {
                "identifier": "3595",
                "name_fr": "Gîtes panda",
                "name_en": "Gîtes Panda",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3581,
            {
                "identifier": "3597",
                "name_fr": "Gîtes de pêche",
                "name_en": "Fishing stay",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3582,
            {
                "identifier": "3599",
                "name_fr": "Gîtes de charme",
                "name_en": "Charming Gîtes",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3583,
            {
                "identifier": "3600",
                "name_fr": "Vignoble",
                "name_en": "Gîtes in the vineyard",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3589,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3603,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3608,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2655,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            4828,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2632,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3617,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2753,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2553,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3644,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3178,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3627,
            {
                "identifier": "3617",
                "name_fr": "En cours de classement",
                "name_en": "Undergoing classification",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3590,
            {
                "identifier": "3609",
                "name_fr": "Ecogîte®",
                "name_en": "Ecogîte®",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3591,
            {
                "identifier": "3610",
                "name_fr": "City break",
                "name_en": "City break",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3592,
            {
                "identifier": "3611",
                "name_fr": "Bébé câlin",
                "name_en": "Welcome baby",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            4634,
            {
                "identifier": "3633",
                "name_fr": "Bien-être / Thermalisme",
                "name_en": "Wellbeing/thermalism",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            4635,
            {
                "identifier": "3633",
                "name_fr": "Bien-être / Thermalisme",
                "name_en": "Wellbeing/thermalism",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            4822,
            {
                "identifier": "2635",
                "name_fr": "Clévacances",
                "name_en": "Clévacances",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            3120,
            {
                "identifier": "2635",
                "name_fr": "Clévacances",
                "name_en": "Clévacances",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            5529,
            {
                "identifier": "2635",
                "name_fr": "Clévacances",
                "name_en": "Clévacances",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            5212,
            {
                "identifier": "2635",
                "name_fr": "Clévacances",
                "name_en": "Clévacances",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            5199,
            {
                "identifier": "2635",
                "name_fr": "Clévacances",
                "name_en": "Clévacances",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            5395,
            {
                "identifier": "2765",
                "name_fr": "Logis",
                "name_en": "Logis",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2840,
            {
                "identifier": "2765",
                "name_fr": "Logis",
                "name_en": "Logis",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            2787,
            {
                "identifier": "4531",
                "name_fr": "Accor",
                "name_en": "Accor",
                "content-type": "AccommodationActivity",
            },
        ),
        (
            0,
            {
                "identifier": "classement-prefectoral",
                "name_fr": "Classement préfectoral",
                "name_en": "prefectoral-classement",
                "content-type": "AccommodationActivity",
            },
        ),
    ]
)

# Comes after generated labels
HANDMADE_LABELS_2 = OrderedDict(
    [
        (2541, {"identifier": "classement-prefectoral", "value": 1}),
        (2543, {"identifier": "classement-prefectoral", "value": 2}),
        (2546, {"identifier": "classement-prefectoral", "value": 3}),
        (2548, {"identifier": "classement-prefectoral", "value": 4}),
        (2550, {"identifier": "classement-prefectoral", "value": 0}),
        (2553, {"identifier": "classement-prefectoral", "value": 0}),
        (2556, {"identifier": "classement-prefectoral", "value": 0}),
        (2561, {"identifier": "classement-prefectoral", "value": 5}),
        (2627, {"identifier": "classement-prefectoral", "value": 1}),
        (2628, {"identifier": "classement-prefectoral", "value": 2}),
        (2629, {"identifier": "classement-prefectoral", "value": 3}),
        (2630, {"identifier": "classement-prefectoral", "value": 4}),
        (2631, {"identifier": "classement-prefectoral", "value": 5}),
        (2632, {"identifier": "classement-prefectoral", "value": 0}),
        (2633, {"identifier": "classement-prefectoral", "value": 0}),
        # TODO: Comfort et very comfortable type_id 53
        (2654, {"identifier": "classement-prefectoral", "value": 0}),
        (2656, {"identifier": "classement-prefectoral", "value": 0}),
        (2655, {"identifier": "classement-prefectoral", "value": 0}),
        (2657, {"identifier": "classement-prefectoral", "value": 0}),
        (2658, {"identifier": "classement-prefectoral", "value": 1}),
        (2659, {"identifier": "classement-prefectoral", "value": 2}),
        (2660, {"identifier": "classement-prefectoral", "value": 3}),
        (2661, {"identifier": "classement-prefectoral", "value": 4}),
        (2662, {"identifier": "classement-prefectoral", "value": 5}),
        (2748, {"identifier": "classement-prefectoral", "value": 1}),
        (2749, {"identifier": "classement-prefectoral", "value": 2}),
        (2750, {"identifier": "classement-prefectoral", "value": 3}),
        (2751, {"identifier": "classement-prefectoral", "value": 4}),
        (2752, {"identifier": "classement-prefectoral", "value": 4}),
        (2753, {"identifier": "classement-prefectoral", "value": 0}),
        (2755, {"identifier": "classement-prefectoral", "value": 0}),
        (2756, {"identifier": "classement-prefectoral", "value": 0}),
        (2758, {"identifier": "classement-prefectoral", "value": 5}),
        # Fleurs de soleil
        (5422, {"identifier": "2702", "value": 3}),
        (5423, {"identifier": "2702", "value": 4}),
        (5424, {"identifier": "2702", "value": 5}),
        # Gîtes de france
        (3584, {"identifier": "2737", "value": 1}),
        (3585, {"identifier": "2737", "value": 2}),
        (3586, {"identifier": "2737", "value": 3}),
        (3587, {"identifier": "2737", "value": 4}),
        (3588, {"identifier": "2737", "value": 5}),
        (3602, {"identifier": "2737", "value": 1}),
        (3604, {"identifier": "2737", "value": 2}),
        (3605, {"identifier": "2737", "value": 3}),
        (3606, {"identifier": "2737", "value": 4}),
        (3607, {"identifier": "2737", "value": 5}),
        (3640, {"identifier": "2737", "value": 1}),
        (3641, {"identifier": "2737", "value": 2}),
        (3642, {"identifier": "2737", "value": 3}),
        (3643, {"identifier": "2737", "value": 4}),
        (3644, {"identifier": "2737", "value": 0}),
        (4105, {"identifier": "2737", "value": 0}),
        # Cle vacances
        (3612, {"identifier": "2635", "value": 1}),
        (3613, {"identifier": "2635", "value": 2}),
        (3614, {"identifier": "2635", "value": 3}),
        (3615, {"identifier": "2635", "value": 4}),
        (3616, {"identifier": "2635", "value": 5}),
        # Loisirs de france
        (3623, {"identifier": "2677", "value": 1}),
        (3626, {"identifier": "2677", "value": 2}),
        (3629, {"identifier": "2677", "value": 3}),
        (3632, {"identifier": "2677", "value": 1}),
        (3634, {"identifier": "2677", "value": 2}),
        (3635, {"identifier": "2677", "value": 3}),
        (3636, {"identifier": "2677", "value": 1}),
        (3637, {"identifier": "2677", "value": 2}),
        (3638, {"identifier": "2677", "value": 3}),
        # Bienvenue à la ferme
        (3596, {"identifier": "2638", "value": 1}),
        (3598, {"identifier": "2638", "value": 2}),
        (3601, {"identifier": "2638", "value": 3}),
        # Camping qualité france
        (3620, {"identifier": "3631", "value": 1}),
        (3621, {"identifier": "3631", "value": 2}),
        (3625, {"identifier": "3631", "value": 3}),
        (3627, {"identifier": "3631", "value": 0}),
    ]
)


HANDMADE_RESTAURANT_RANKING = OrderedDict(
    [
        (2971, {"identifier": "2964", "value": 1}),  # 1 étoile Michelin
        (2972, {"identifier": "2964", "value": 2}),  # 2 étoiles Michelin
        (2973, {"identifier": "2964", "value": 3}),  # 3 étoiles Michelin
        (2974, {"identifier": "2964"}),  # Bib gourmand ...
        (
            2917,
            {
                "identifier": "2967",
                "name_fr": "Restaurateurs de France",
                "name_en": "Restaurateurs de France",
                "content-type": "MealActivity",
            },
        ),
        (
            2919,
            {
                "identifier": "2766",
                "name_fr": "Tables et auberges de France",
                "name_en": "Tables et auberges de France",
                "content-type": "MealActivity",
            },
        ),
        (
            2944,
            {
                "identifier": "2944",
                "name_fr": "Logis (repas)",
                "name_en": "Logis (meal)",
                "content-type": "MealActivity",
            },
        ),
        (2954, {"identifier": "2944", "value": 1}),  # Cocotte
        (2956, {"identifier": "2944", "value": 2}),
        (2958, {"identifier": "2944", "value": 3}),
        (5172, {"identifier": "2953", "value": 1}),  # 1 toque Gault & Millau
        (5173, {"identifier": "2953", "value": 2}),  # 2 toques Gault & Millau
        (5174, {"identifier": "2953", "value": 3}),  # 3 toques Gault & Millau
        (5175, {"identifier": "2953", "value": 4}),  # 4 toques Gault & Millau
        (5176, {"identifier": "2953", "value": 5}),  # 5 toques Gault & Millau
    ]
)

RESTAURANT_TYPE = OrderedDict(
    [
        (
            "category",
            {
                "identifier": "meal-activity-type",
                "name_fr": "Type de restauration",
                "name_en": "Restauration type",
                "parent": "meal-activity",
                "is_category": True,
            },
        ),
        (
            2859,
            {
                "identifier": "country-inn-activity-type",
                "name_fr": "Auberge de campagne",
                "name_en": "Country inn",
                "name_nl": "Landelijke herberg",
                "name_es": "Posada",
                "name_it": "Albergo di campagna",
                "name_de": "Landherberge",
                "parent": "meal-activity-type",
                "is_category": False,
            },
        ),
        (
            2861,
            {
                "identifier": "farmhouse-inn-activity-type",
                "name_fr": "Ferme auberge",
                "name_en": "Farmhouse inn",
                "name_nl": "Ferme auberge",
                "name_es": "Casa rural",
                "name_it": "Fattoria-ostello",
                "name_de": "Bauernherberge",
                "parent": "meal-activity-type",
                "is_category": False,
            },
        ),
        (
            2865,
            {
                "identifier": "hotel-restaurant-activity-type",
                "name_fr": "Hôtel - Restaurant",
                "name_en": "Hotel-Restaurant",
                "name_nl": "Hotel-restaurant",
                "name_es": "Hotel - restaurante",
                "name_it": "Hotel ristorante",
                "name_de": "Hotel-Restaurant",
                "parent": "meal-activity-type",
                "is_category": False,
            },
        ),
        (
            2866,
            {
                "identifier": "restaurant-activity-type",
                "name_fr": "Restaurant",
                "name_en": "Restaurant",
                "name_nl": "Restaurants",
                "name_es": "Restaurante",
                "name_it": "Ristorante",
                "name_de": "Restaurant",
                "parent": "meal-activity-type",
                "is_category": False,
            },
        ),
        (
            4528,
            {
                "identifier": "food-truck-activity-type",
                "name_fr": "Food truck",
                "name_en": "Food truck",
                "name_nl": "Food truck",
                "name_es": "Food truck",
                "name_it": "Food truck",
                "name_de": "Food truck",
                "parent": "meal-activity-type",
                "is_category": False,
            },
        ),
        (
            "TABLE",
            {
                "identifier": "meal-type-table-dhotes",
                "name_fr": "Table d'hôtes",
                "name_en": "Table d'hôtes",
                "parent": "meal-activity-type",
                "is_category": False,
            },
        ),
    ]
)


STRUCTURE_TYPE = OrderedDict(
    [
        (
            "category",
            {
                "identifier": "structure-activity-type",
                "name_fr": "Type de structure",
                "name_en": "Structure type",
                "parent": "structure-activity",
                "is_category": True,
            },
        ),
        (
            3166,
            {
                "identifier": "tourist-information-office-structure-activity-type",
                "name_fr": "Office de Tourisme ou Syndicat d'Initiative",
                "name_en": "Tourist Information Office",
                "parent": "structure-activity-type",
                "is_category": False,
            },
        ),
        (
            3196,
            {
                "identifier": "cultural-associations-structure-activity-type",
                "name_fr": "Associations culturelles",
                "name_en": "Cultural associations",
                "parent": "structure-activity-type",
                "is_category": False,
            },
        ),
        (
            3840,
            {
                "identifier": "ski-school-structure-activity-type",
                "name_fr": "Ecole de ski",
                "name_en": "Ski school",
                "parent": "structure-activity-type",
                "is_category": False,
            },
        ),
        (
            3988,
            {
                "identifier": "service-provider-structure-activity-type",
                "name_fr": "Prestataire de service",
                "name_en": "Service provider",
                "parent": "structure-activity-type",
                "is_category": False,
            },
        ),
        (
            4011,
            {
                "identifier": "activity-provider-structure-activity-type",
                "name_fr": "Prestataires d'activités",
                "name_en": "Activity provider",
                "parent": "structure-activity-type",
                "is_category": False,
            },
        ),
    ]
)


RESTAURANT_CATEGORY = OrderedDict(
    [
        (
            "category",
            {
                "identifier": "meal-activity-category",
                "name_fr": "Catégorie de restauration",
                "name_en": "Restauration category",
                "parent": "meal-activity",
                "is_category": True,
            },
        ),
        (
            2880,
            {
                "identifier": "brasserie-meal-activity-category",
                "name_fr": "Brasserie",
                "name_en": "Brasserie",
                "name_nl": "Brasserie",
                "name_es": "Cervecería",
                "name_it": "Brasserie",
                "name_de": "Brasserie/Brauerei",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            2881,
            {
                "identifier": "cafeteria-meal-activity-category",
                "name_fr": "Cafétéria",
                "name_en": "Cafeteria",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            2882,
            {
                "identifier": "creperie-meal-activity-category",
                "name_fr": "Crêperie",
                "name_en": "Crêperie",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            2883,
            {
                "identifier": "traditional-cooking-meal-activity-category",
                "name_fr": "Restaurant traditionnel",
                "name_en": "Traditional cooking",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            2884,
            {
                "identifier": "grill-meal-activity-category",
                "name_fr": "Grill",
                "name_en": "Grill",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            2886,
            {
                "identifier": "pizzeria-meal-activity-category",
                "name_fr": "Pizzeria",
                "name_en": "Pizzeria",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            2887,
            {
                "identifier": "fast-food-meal-activity-category",
                "name_fr": "Restauration rapide",
                "name_en": "Fast food",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            2893,
            {
                "identifier": "foreign-specialities-meal-activity-category",
                "name_fr": "Restaurant de spécialités étrangères",
                "name_en": "Foreign specialities",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            2894,
            {
                "identifier": "bouchon-meal-activity-category",
                "name_fr": "Bouchon",
                "name_en": "Bouchon",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            2895,
            {
                "identifier": "mountain-restaurant-meal-activity-category",
                "name_fr": "Restaurant d'altitude / Restaurant d'alpage",
                "name_en": "Restaurant on the ski slopes / Mountain restaurant",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            3821,
            {
                "identifier": "training-restaurant-meal-activity-category",
                "name_fr": "Restaurant d'application",
                "name_en": "Training restaurant",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            3823,
            {
                "identifier": "entertainment-restaurant-meal-activity-category",
                "name_fr": "Restaurant spectacle",
                "name_en": "Entertainment restaurant",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            3824,
            {
                "identifier": "dancing-restaurant-meal-activity-category",
                "name_fr": "Restaurant dansant",
                "name_en": "Dancing restaurant",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            3825,
            {
                "identifier": "gastronomic-restaurant-meal-activity-category",
                "name_fr": "Restaurant gastronomique",
                "name_en": "Brasserie",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            5351,
            {
                "identifier": "bistro-restaurant-meal-activity-category",
                "name_fr": "Restaurant bistronomique",
                "name_en": "Bistro restaurant",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            5315,
            {
                "identifier": "beach-restaurant-meal-activity-category",
                "name_fr": "Restaurant de plage",
                "name_en": "Beach restaurant",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            6539,
            {
                "identifier": "guinguette-meal-activity-category",
                "name_fr": "Guinguette",
                "name_en": "Guinguette",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            6137,
            {
                "identifier": "foudcourt-activity-category",
                "name_fr": "Food court",
                "name_en": "FoodCourt",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            5923,
            {
                "identifier": "family-meal-activity-category",
                "name_fr": "Repas en tribu",
                "name_en": "Family meal",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
        (
            6174,
            {
                "identifier": "mountain-restaurant-activity-category",
                "name_fr": "Restaurant d'alpage",
                "name_en": "Mountain restaurant",
                "parent": "meal-activity-category",
                "is_category": False,
            },
        ),
    ]
)

RENTAL_ACCOMMODATION_TYPE = OrderedDict(
    [
        (
            "category",
            {
                "identifier": "accommodation-activity-type",
                "name_fr": "Type d'hébergement",
                "name_en": "Accommodation type",
                "parent": "accommodation-activity",
                "is_category": True,
            },
        ),
        (
            9990,
            {
                "identifier": "room-activity-type",
                "name_fr": "Chambre",
                "name_en": "Room",
                "parent": "accommodation-activity-type",
                "is_category": True,
            },
        ),
        (
            99991,
            {
                "identifier": "rental-activity-type",
                "name_fr": "Location",
                "name_en": "Rental",
                "parent": "accommodation-activity-type",
                "is_category": True,
            },
        ),
        (
            99992,
            {
                "identifier": "group-activity-type",
                "name_fr": "Groupes",
                "name_en": "Groups",
                "parent": "accommodation-activity-type",
                "is_category": True,
            },
        ),
        (
            2410,
            {
                "identifier": "campsite-activity-type",
                "name_fr": "Camping",
                "name_en": "Campsite",
                "name_nl": "Camping",
                "name_es": "Camping",
                "name_it": "Campeggio",
                "name_de": "Campingplatz",
                "parent": "accommodation-activity-type",
                "is_category": True,
            },
        ),
        (
            2619,
            {
                "identifier": "bnb-activity-type",
                "name_fr": "Chambre d'hôtes",
                "name_en": "Bed & breakfast",
                "name_nl": "Bed&breakfast",
                "name_es": "Habitación de huéspedes",
                "name_it": "Camere per turisti",
                "name_de": "Fremdenzimmer",
                "parent": "room-activity-type",
                "is_category": False,
            },
        ),
        (2626, {"identifier": "bnb-activity-type"}),
        (
            2734,
            {
                "identifier": "hotel-activity-type",
                "name_fr": "Hôtel",
                "name_en": "Hotel",
                "name_nl": "Hotel",
                "name_es": "Hotel",
                "name_it": "Hotel",
                "name_de": "Hotel",
                "parent": "room-activity-type",
                "is_category": False,
            },
        ),
        (
            2736,
            {
                "identifier": "hotel-restaurant-accommodation-activity-type",
                "name_fr": "Hôtel-Restaurant",
                "name_en": "Hotel-restaurant",
                "name_nl": "Hotel - Restaurant",
                "name_es": "Hotel - Restaurante",
                "name_it": "Hotel - Ristorante",
                "name_de": "Hotel - Restaurant",
                "parent": "room-activity-type",
                "is_category": False,
            },
        ),
        (
            2620,
            {
                "identifier": "lodge-activity-type",
                "name_fr": "Meublés et Gîtes",
                "name_en": "Furnished accommodation and Gîtes",
                "name_nl": "Gemeubileerde kamers en Gîtes",
                "name_es": "Amueblados y Casas Rurales",
                "name_it": "Alloggi ammobiliati e rurali",
                "name_de": "Möblierte Unterkünfte und Ferienwohnungen",
                "parent": "rental-activity-type",
                "is_category": False,
            },
        ),
        (2625, {"identifier": "lodge-activity-type"}),
        (
            2643,
            {
                "identifier": "family-holiday-accommodation-activity-type",
                "name_fr": "Maison familiale de vacances",
                "name_en": "Family Holiday Accommodation",
                "name_nl": "Maison familiale de vacances",
                "name_es": "Casa rural familiar de vacaciones",
                "name_it": "Casa vacanza famiglia",
                "name_de": "Ferienhaus",
                "parent": "rental-activity-type",
                "is_category": False,
            },
        ),
        (
            2649,
            {
                "identifier": "tourist-residence-activity-type",
                "name_fr": "Résidence de tourisme",
                "name_en": "Tourist residence",
                "name_nl": "Vakantiedorp",
                "name_es": "Residencia de turismo",
                "name_it": "Residence turistico",
                "name_de": "Touristenresidenz",
                "parent": "rental-activity-type",
                "is_category": False,
            },
        ),
        (
            2650,
            {
                "identifier": "hotel-residence-activity-type",
                "name_fr": "Résidence",
                "name_en": "Hotel residence",
                "name_nl": "Hotel Residence",
                "name_es": "Residencia hotelera",
                "name_it": "Residence alberghiero",
                "name_de": "Hotelresidenz",
                "parent": "rental-activity-type",
                "is_category": False,
            },
        ),
        (
            2651,
            {
                "identifier": "village-of-gites-activity-type",
                "name_fr": "Village de gîtes",
                "name_en": "Village of gîtes",
                "name_nl": "Gîtedorp",
                "name_es": "Pueblo de casas rurales y de campo",
                "name_it": "Villaggio turistico",
                "name_de": "Feriendorf",
                "parent": "rental-activity-type",
                "is_category": False,
            },
        ),
        (
            2644,
            {
                "identifier": "holiday-villages-activity-type",
                "name_fr": "Village de vacances",
                "name_en": "Holiday villages",
                "name_nl": "Vakantiedorp",
                "name_es": "Pueblo de vacaciones",
                "name_it": "Villaggio vacanza",
                "name_de": "Feriendorf",
                "parent": "rental-activity-type",
                "is_category": False,
            },
        ),
        (
            2409,
            {
                "identifier": "camping-on-farm-sites-activity-type",
                "name_fr": "Camping à la ferme",
                "name_en": "Camping on farm sites",
                "name_nl": "Kamperen bij de boer",
                "name_es": "Camping en la granja",
                "name_it": "Campeggio in fattoria",
                "name_de": "Camping auf dem Bauernhof",
                "parent": "campsite-activity-type",
                "is_category": False,
            },
        ),
        (
            2413,
            {
                "identifier": "residential-leisure-park-activity-type",
                "name_fr": "Parc résidentiel de loisirs",
                "name_en": "Residential leisure park",
                "name_nl": "Vakantiepark",
                "name_es": "Parque residencial de ocio",
                "name_it": "Complesso di villeggiatura",
                "name_de": "Parc résidentiel de loisirs (Urlaubsresidenz)",
                "parent": "campsite-activity-type",
                "is_category": False,
            },
        ),
        (
            2416,
            {
                "identifier": "natural-area-activity-type",
                "name_fr": "Aire naturelle",
                "name_en": "Tourism campsite - natural site",
                "name_nl": "Natuurterrein",
                "name_es": "Área natural",
                "name_it": "Area naturale",
                "name_de": "Naturcampingplatz",
                "parent": "campsite-activity-type",
                "is_category": False,
            },
        ),
        (
            3722,
            {
                "identifier": "bivouac-shelter-activity-type",
                "name_fr": "Zone de bivouac",
                "name_en": "Bivouac shelter",
                "name_nl": "Bivak",
                "name_es": "Vivac",
                "name_it": "Bivacco",
                "name_de": "Biwak als Feldlager",
                "parent": "campsite-activity-type",
                "is_category": False,
            },
        ),
        (
            2418,
            {
                "identifier": "campervan-activity-type",
                "name_fr": "Aire de service/accueil camping-cars",
                "name_en": "Camper van service/reception area",
                "name_nl": "Parkeerplaats met voorzieningen/Receptie campers",
                "name_es": "Área de servicio/admisión camping-cars",
                "name_it": "Area servizio/accoglienza camper",
                "name_de": "Servicestation/Wohnmobilrastplatz",
                "parent": "campsite-activity-type",
                "is_category": False,
            },
        ),
        (
            2640,
            {
                "identifier": "youth-hostels-activity-type",
                "name_fr": "Auberge de jeunesse",
                "name_en": "Youth hostels",
                "name_nl": "Jeugdherberg",
                "name_es": "Albergue juvenil",
                "name_it": "Ostello",
                "name_de": "Jugendherberge",
                "parent": "group-activity-type",
                "is_category": False,
            },
        ),
        (
            2641,
            {
                "identifier": "youth-centres-activity-type",
                "name_fr": "Centre de jeunes",
                "name_en": "Youth centres",
                "name_nl": "Jongerencentrum",
                "name_es": "Centro de juventud",
                "name_it": "Centro per giovani",
                "name_de": "Jugendgästehaus",
                "parent": "group-activity-type",
                "is_category": False,
            },
        ),
        (
            2642,
            {
                "identifier": "holiday-centres-activity-type",
                "name_fr": "Centre de vacances",
                "name_en": "Holiday centres",
                "name_nl": "Vakantiecentrum",
                "name_es": "Centro de vacaciones",
                "name_it": "Centro vacanze",
                "name_de": "Urlaubszentrum",
                "parent": "group-activity-type",
                "is_category": False,
            },
        ),
        (
            2652,
            {
                "identifier": "centre-international-de-sejour-accommodation-for-young-people-activity-type",
                "name_fr": "Centre international de séjour",
                "name_en": "Centre international de séjour (accommodation for young people)",
                "name_nl": "Internationaal centrum",
                "name_es": "Centro internacional de estancia",
                "name_it": "Centro internazionale di soggiorno",
                "name_de": "Internationale Jugendherberge",
                "parent": "group-activity-type",
                "is_category": False,
            },
        ),
        (
            2653,
            {
                "identifier": "gite-denfants-family-run-gites-for-children-activity-type",
                "name_fr": "Gîte d'enfants",
                "name_en": "Gîte d'enfants (family-run gîtes for children)",
                "name_nl": "Kindergîte",
                "name_es": "Albergue infantil",
                "name_it": "Alloggio rurale per bambini",
                "name_de": "Kinderbeherbergung",
                "parent": "group-activity-type",
                "is_category": False,
            },
        ),
        (
            2647,
            {
                "identifier": "gite-sejour-activity-type",
                "name_fr": "Gîte d'étape/séjour",
                "name_en": "Group gîte",
                "name_nl": "Gîte d’étape/séjour",
                "name_es": "Albergue de etapa/estancia",
                "name_it": "Alloggio rurale per pernottamento",
                "name_de": "Ferienwohnung/Übernachtung",
                "parent": "group-activity-type",
                "is_category": False,
            },
        ),
        (
            2648,
            {
                "identifier": "refuge-activity-type",
                "name_fr": "Refuge",
                "name_en": "Refuge",
                "name_nl": "Berghut",
                "name_es": "Refugio",
                "name_it": "Rifugio",
                "name_de": "Hütte",
                "parent": "group-activity-type",
                "is_category": False,
            },
        ),
        (
            2646,
            {
                "identifier": "other-accommodation-activity-type",
                "name_fr": "Autres hébergements",
                "name_en": "Other accommodation",
                "name_nl": "Andere accommodatie",
                "name_es": "Otros alojamientos",
                "name_it": "Altri alloggi",
                "name_de": "Andere Unterkünfte",
                "parent": "accommodation-activity-type",
                "is_category": False,
            },
        ),
        (
            6142,
            {
                "identifier": "collective-hostel-activity-type",
                "name_fr": "Auberge collective",
                "name_en": "Collective hostel",
                "name_nl": "Collectief hostel",
                "name_es": "Hostal colectivo",
                "name_it": "Hostel collettivo",
                "name_de": "Kollektives Hostel",
                "parent": "accommodation-activity-type",
                "is_category": False,
            },
        ),
        (
            5902,
            {
                "identifier": "homestay-activity-type",
                "name_fr": "Chambre chez un particulier",
                "name_en": "Room in a private home",
                "name_nl": "Kamer in een privéwoning",
                "name_es": "Habitación en una casa particular",
                "name_it": "Camera in una casa privata",
                "name_de": "Zimmer bei einer Privatperson",
                "parent": "accommodation-activity-type",
                "is_category": False,
            },
        ),
    ]
)

# 3283 = Itinéraire cyclo
# 3313 = Itinéraire de randonnée équestre
# 3333 = Itinéraire de randonnée pédestre
# 3302 = Itinéraire raquettes
# 3284 = Itinéraire VTT
# 4201 = Itinéraire de trail
# 5324 = Parcours de marche nordique
# 5447 = Itinéraire de Vélo à Assistance Electrique
ITINERARY_EQUIPMENT_ACTIVITY = [3283, 3313, 3333, 3302, 3284, 4201, 5324, 5447]
