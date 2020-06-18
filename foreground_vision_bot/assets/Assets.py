from pathlib import Path
from enum import Enum  

import cv2 as cv

mob_rosposa_water_path = str(Path(__file__).parent / 'names' / 'rosposa_water.png')
mob_kingyo_water_path = str(Path(__file__).parent / 'names' / 'kingyo_water.png')
mob_dlakav_water_path = str(Path(__file__).parent / 'names' / 'dlakav_water.png')
mob_batto_wind_path = str(Path(__file__).parent / 'names' / 'batto_wind.png')
mob_castor_soil_path = str(Path(__file__).parent / 'names' / 'castor_soil.png')
mob_kretan_soil_path = str(Path(__file__).parent / 'names' / 'kretan_soil.png')
mob_worun_soil_path = str(Path(__file__).parent / 'names' / 'worun_soil.png')
mob_cetiri_electricity_path = str(Path(__file__).parent / 'names' / 'cetiri_electricity.png')
mob_oseti_electricity_path = str(Path(__file__).parent / 'names' / 'oseti_electricity.png')
mob_carvi_fire_path = str(Path(__file__).parent / 'names' / 'carvi_fire.png')
mob_nyamuli_fire_path = str(Path(__file__).parent / 'names' / 'nyamuli_fire.png')

mob_type_wind_path = str(Path(__file__).parent / 'mob_types' / 'wind.png')
mob_type_fire_path = str(Path(__file__).parent / 'mob_types' / 'fire.png')
mob_type_soil_path = str(Path(__file__).parent / 'mob_types' / 'soil.png')
mob_type_water_path = str(Path(__file__).parent / 'mob_types' / 'water.png')
mob_type_electricity_path = str(Path(__file__).parent / 'mob_types' / 'electricity.png')

mob_life_bar_path = str(Path(__file__).parent / 'mob_life_bar.png')
user_target_bar_path = str(Path(__file__).parent / 'user_target_bar.png')


class MobName():
	ROSPOSA = cv.imread(mob_rosposa_water_path, cv.IMREAD_GRAYSCALE)
	KINGYO = cv.imread(mob_kingyo_water_path, cv.IMREAD_GRAYSCALE)
	DLAKAV = cv.imread(mob_dlakav_water_path, cv.IMREAD_GRAYSCALE)
	BATTO = cv.imread(mob_batto_wind_path, cv.IMREAD_GRAYSCALE)
	CASTOR = cv.imread(mob_castor_soil_path, cv.IMREAD_GRAYSCALE)
	KRETAN = cv.imread(mob_kretan_soil_path, cv.IMREAD_GRAYSCALE)
	WORUN = cv.imread(mob_worun_soil_path, cv.IMREAD_GRAYSCALE)
	OSETI = cv.imread(mob_oseti_electricity_path, cv.IMREAD_GRAYSCALE)
	CARVI = cv.imread(mob_carvi_fire_path, cv.IMREAD_GRAYSCALE)
	NYAMULI = cv.imread(mob_nyamuli_fire_path, cv.IMREAD_GRAYSCALE)


class MobType():
	WIND = cv.imread(mob_type_wind_path, cv.IMREAD_GRAYSCALE)
	FIRE = cv.imread(mob_type_fire_path, cv.IMREAD_GRAYSCALE)
	SOIL = cv.imread(mob_type_soil_path, cv.IMREAD_GRAYSCALE)
	WATER = cv.imread(mob_type_water_path, cv.IMREAD_GRAYSCALE)
	ELECTRICITY = cv.imread(mob_type_electricity_path, cv.IMREAD_GRAYSCALE)


class MobInfo():
	"""
	MOB_NAME = (MOB NAME CV IMAGE, MOB TYPE CV IMAGE, HEIGHT_OFFSET)
	"""
	ROSPOSA = (MobName.ROSPOSA, MobType.WATER, 80)
	KINGYO = (MobName.KINGYO, MobType.WATER, 80)
	DLAKAV = (MobName.DLAKAV, MobType.WATER, 80)
	BATTO = (MobName.BATTO, MobType.WIND, 125)
	CASTOR = (MobName.CASTOR, MobType.SOIL, 80)
	KRETAN = (MobName.KRETAN, MobType.SOIL, 80)
	WORUN = (MobName.WORUN, MobType.SOIL, 80)
	OSETI = (MobName.OSETI, MobType.ELECTRICITY, 80)
	CARVI = (MobName.CARVI, MobType.FIRE, 80)
	NYAMULI = (MobName.NYAMULI, MobType.FIRE, 80)

	def __init__(self):
		pass

	@staticmethod
	def get_all_mobs():
		return [getattr(MobInfo, attr) for attr in dir(MobInfo) if not attr.startswith("__")]


class GeneralAssets():
	MOB_LIFE_BAR = cv.imread(mob_life_bar_path, cv.IMREAD_GRAYSCALE)
	USER_TARGET_BAR = cv.imread(user_target_bar_path, cv.IMREAD_GRAYSCALE)
