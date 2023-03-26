from pathlib import Path

import cv2 as cv
import json
import os
import shutil

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
        "element": "water",
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "name_img": cv.imread(mob_rosposa_water_path, cv.IMREAD_GRAYSCALE),
        "element_img": MobType.WATER,
    }
    KINGYO = {
        "name": "kingyo",
        "element": "water",
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "name_img": cv.imread(mob_kingyo_water_path, cv.IMREAD_GRAYSCALE),
        "element_img": MobType.WATER,
    }
    DLAKAV = {
        "name": "dlakav",
        "element": "water",
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "name_img": cv.imread(mob_dlakav_water_path, cv.IMREAD_GRAYSCALE),
        "element_img": MobType.WATER,
    }
    BATTO = {
        "name": "batto",
        "element": "wind",
        "map_name": "Neo Cascada",
        "height_offset": 125,
        "name_img": cv.imread(mob_batto_wind_path, cv.IMREAD_GRAYSCALE),
        "element_img": MobType.WIND,
    }
    CASTOR = {
        "name": "castor",
        "element": "soil",
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "name_img": cv.imread(mob_castor_soil_path, cv.IMREAD_GRAYSCALE),
        "element_img": MobType.SOIL,
    }
    KRETAN = {
        "name": "kretan",
        "element": "soil",
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "name_img": cv.imread(mob_kretan_soil_path, cv.IMREAD_GRAYSCALE),
        "element_img": MobType.SOIL,
    }
    WORUN = {
        "name": "worun",
        "element": "soil",
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "name_img": cv.imread(mob_worun_soil_path, cv.IMREAD_GRAYSCALE),
        "element_img": MobType.SOIL,
    }
    OSETI = {
        "name": "oseti",
        "element": "electricity",
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "name_img": cv.imread(mob_oseti_electricity_path, cv.IMREAD_GRAYSCALE),
        "element_img": MobType.ELECTRICITY,
    }
    CARVI = {
        "name": "carvi",
        "element": "fire",
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "name_img": cv.imread(mob_carvi_fire_path, cv.IMREAD_GRAYSCALE),
        "element_img": MobType.FIRE,
    }
    NYAMULI = {
        "name": "nyamuli",
        "element": "fire",
        "map_name": "Neo Cascada",
        "height_offset": 80,
        "name_img": cv.imread(mob_nyamuli_fire_path, cv.IMREAD_GRAYSCALE),
        "element_img": MobType.FIRE,
    }

    @staticmethod
    def add_new_mob(name: str, map_name: str, image_path: str, height_offset: int, element: str) -> None:
        """
        Add new mob to json collection (mobs_list.json)
        """
        json_collection_path = str(Path(__file__).parent / "mobs_list.json")

        # copy image for cv detection in asset folder
        shutil.copyfile(image_path, str(Path(__file__).parent / "names" / f"{name}.png"))

        current_mobs_list = MobInfo.get_all_mobs()
        current_mobs_list[name] = {
            "element": element,
            "map_name": map_name,
            "height_offset": height_offset
        }

        file = open(json_collection_path, 'w+')
        json.dump(current_mobs_list, file)


    @staticmethod
    def get_all_mobs() -> dict:
        """
        Get a list of all mobs registered. Using a dump of mobs_list.json file

        :return: list of all mobs as dict (key: 'mob_name', val: params_dict)
        """
        json_collection_path = str(Path(__file__).parent / "mobs_list.json")

        # Check mobs_list.json
        if not os.path.isfile(json_collection_path):
            file = open(json_collection_path, 'w+')
            json.dump({}, file)
            file.close()

        mobs_list = json.load(open(json_collection_path, 'r'))
        print('------>',mobs_list)
        return mobs_list
        #return [
        #    getattr(MobInfo, attr)
        #    for attr in dir(MobInfo)
        #    if not attr.startswith("__") and not callable(getattr(MobInfo, attr))
        #]


class GeneralAssets:
    MOB_LIFE_BAR = cv.imread(mob_life_bar_path, cv.IMREAD_GRAYSCALE)
    USER_TARGET_BAR = cv.imread(user_target_bar_path, cv.IMREAD_GRAYSCALE)
    INVENTORY_PERIN_CONVERTER = cv.imread(inventory_perin_converter_path, cv.IMREAD_GRAYSCALE)
    INVENTORY_ICONS = cv.imread(inventory_icons_path, cv.IMREAD_GRAYSCALE)
