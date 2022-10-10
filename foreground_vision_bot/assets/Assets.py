from pathlib import Path
import cv2 as cv

mob_rosposa_water_path = str(Path(__file__).parent / "names" / "rosposa_water.png")
mob_kingyo_water_path = str(Path(__file__).parent / "names" / "kingyo_water.png")
mob_dlakav_water_path = str(Path(__file__).parent / "names" / "dlakav_water.png")
mob_batto_wind_path = str(Path(__file__).parent / "names" / "batto_wind.png")
mob_castor_soil_path = str(Path(__file__).parent / "names" / "castor_soil.png")
mob_kretan_soil_path = str(Path(__file__).parent / "names" / "kretan_soil.png")
mob_worun_soil_path = str(Path(__file__).parent / "names" / "worun_soil.png")
mob_cetiri_electricity_path = str(Path(__file__).parent / "names" / "cetiri_electricity.png")
mob_oseti_electricity_path = str(Path(__file__).parent / "names" / "oseti_electricity.png")
mob_carvi_fire_path = str(Path(__file__).parent / "names" / "carvi_fire.png")
mob_nyamuli_fire_path = str(Path(__file__).parent / "names" / "nyamuli_fire.png")

mob_type_wind_path = str(Path(__file__).parent / "mob_types" / "wind.png")
mob_type_fire_path = str(Path(__file__).parent / "mob_types" / "fire.png")
mob_type_soil_path = str(Path(__file__).parent / "mob_types" / "soil.png")
mob_type_water_path = str(Path(__file__).parent / "mob_types" / "water.png")
mob_type_electricity_path = str(Path(__file__).parent / "mob_types" / "electricity.png")

mob_life_bar_path = str(Path(__file__).parent / "general" / "mob_life_bar.png")
user_target_bar_path = str(Path(__file__).parent / "general" / "user_target_bar.png")
inventory_perin_converter_path = str(Path(__file__).parent / "general" / "inventory_perin_converter.png")
inventory_icons_path = str(Path(__file__).parent / "general" / "inventory_icons.png")


class MobType:
    WIND = cv.imread(mob_type_wind_path, cv.IMREAD_GRAYSCALE)
    FIRE = cv.imread(mob_type_fire_path, cv.IMREAD_GRAYSCALE)
    SOIL = cv.imread(mob_type_soil_path, cv.IMREAD_GRAYSCALE)
    WATER = cv.imread(mob_type_water_path, cv.IMREAD_GRAYSCALE)
    ELECTRICITY = cv.imread(mob_type_electricity_path, cv.IMREAD_GRAYSCALE)


class MobInfo:
    ROSPOSA = {
        "name": "rosposa",
        "element": MobType.WATER,
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "image": cv.imread(mob_rosposa_water_path, cv.IMREAD_GRAYSCALE),
    }
    KINGYO = {
        "name": "kingyo",
        "element": MobType.WATER,
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "image": cv.imread(mob_kingyo_water_path, cv.IMREAD_GRAYSCALE),
    }
    DLAKAV = {
        "name": "dlakav",
        "element": MobType.WATER,
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "image": cv.imread(mob_dlakav_water_path, cv.IMREAD_GRAYSCALE),
    }
    BATTO = {
        "name": "batto",
        "element": MobType.WIND,
        "map_name": "Neo Cascada",
        "height_offset": 125,
        "image": cv.imread(mob_batto_wind_path, cv.IMREAD_GRAYSCALE),
    }
    CASTOR = {
        "name": "castor",
        "element": MobType.SOIL,
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "image": cv.imread(mob_castor_soil_path, cv.IMREAD_GRAYSCALE),
    }
    KRETAN = {
        "name": "kretan",
        "element": MobType.SOIL,
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "image": cv.imread(mob_kretan_soil_path, cv.IMREAD_GRAYSCALE),
    }
    WORUN = {
        "name": "worun",
        "element": MobType.SOIL,
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "image": cv.imread(mob_worun_soil_path, cv.IMREAD_GRAYSCALE),
    }
    OSETI = {
        "name": "oseti",
        "element": MobType.ELECTRICITY,
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "image": cv.imread(mob_oseti_electricity_path, cv.IMREAD_GRAYSCALE),
    }
    CARVI = {
        "name": "carvi",
        "element": MobType.FIRE,
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "image": cv.imread(mob_carvi_fire_path, cv.IMREAD_GRAYSCALE),
    }
    NYAMULI =  {
        "name": "nyamuli",
        "element": MobType.FIRE,
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "image": cv.imread(mob_nyamuli_fire_path, cv.IMREAD_GRAYSCALE),
    }

    @staticmethod
    def get_all_mobs():
        return [getattr(MobInfo, attr) for attr in dir(MobInfo) if not attr.startswith("__")]


class GeneralAssets:
    MOB_LIFE_BAR = cv.imread(mob_life_bar_path, cv.IMREAD_GRAYSCALE)
    USER_TARGET_BAR = cv.imread(user_target_bar_path, cv.IMREAD_GRAYSCALE)
    INVENTORY_PERIN_CONVERTER = cv.imread(inventory_perin_converter_path, cv.IMREAD_GRAYSCALE)
    INVENTORY_ICONS = cv.imread(inventory_icons_path, cv.IMREAD_GRAYSCALE)
