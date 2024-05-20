from pathlib import Path

import cv2 as cv
import json
import os
import shutil
from enum import Enum

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
            "name": name,
            "element": element,
            "map_name": map_name,
            "height_offset": height_offset
        }

        file = open(json_collection_path, 'w+')
        json.dump(current_mobs_list, file)
    
    @staticmethod
    def delete_mobs(name_list: list[str]) -> None:
        """
        Delete list of mobs from json collection (mobs_list.json)
        """
        json_collection_path = str(Path(__file__).parent / "mobs_list.json")
        current_mobs_list = MobInfo.get_all_mobs()
        new_mobs_list = {}

        # delete images for cv detection from asset folder
        for key in current_mobs_list:
            if key in name_list:
                os.remove(str(Path(__file__).parent / "names" / f"{key}.png"))
            else:
                new_mobs_list[key] = current_mobs_list[key]

        file = open(json_collection_path, 'w+')
        json.dump(new_mobs_list, file)

    @staticmethod
    def get_all_mobs() -> dict[str, dict]:
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
        return mobs_list


class GeneralAssets:
    MOB_LIFE_BAR = cv.imread(mob_life_bar_path, cv.IMREAD_GRAYSCALE)
    USER_TARGET_BAR = cv.imread(user_target_bar_path, cv.IMREAD_GRAYSCALE)
    INVENTORY_PERIN_CONVERTER = cv.imread(inventory_perin_converter_path, cv.IMREAD_GRAYSCALE)
    INVENTORY_ICONS = cv.imread(inventory_icons_path, cv.IMREAD_GRAYSCALE)
