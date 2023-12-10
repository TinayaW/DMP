import time

import holidays
import streamlit as st
import folium
import pickle
import numpy as np
from streamlit.components.v1 import html
from streamlit_folium import folium_static
import pandas as pd
from sodapy import Socrata
from datetime import datetime, timedelta
import plotly.express as px
import sqlite3
import hashlib  # For hashing passwords
from catboost import CatBoostClassifier
from sklearn.preprocessing import StandardScaler

st.set_page_config(
    page_title="Chicago CrimeWiz",
    page_icon=":cop:",
)

# SQLite connection
conn = sqlite3.connect('Crime_whiz.db')
cursor = conn.cursor()

# Create a table to store user credentials if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()
# Create a table to store user feedback if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        feedback_text TEXT
    )
''')
conn.commit()

# Create a table to store predictions if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        prediction_text TEXT,
        prediction TEXT
    )
''')
conn.commit()


# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Function to verify passwords
def verify_password(entered_password, hashed_password):
    return hashlib.sha256(entered_password.encode()).hexdigest() == hashed_password


# Load Catboost model
with open('catboost_model.pkl', 'rb') as model_file:
    catboost_model = pickle.load(model_file)

# Load StandardScaler
with open('scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# Load the forecasting model
with open('forecaster_model.pkl', 'rb') as forecaster_file:
    forecaster_model = pickle.load(forecaster_file)

# Load the Multiclass classifier
with open('multiclass_model_crimetype_test_2.pkl', 'rb') as multiclass_file:
    multiclass_model = pickle.load(multiclass_file)

# Define a list of districts in Chicago
list_of_districts_in_chicago = [
    "Central", "Wentworth", "Grand Crossing", "South Chicago", "Calumet",
    "Gresham", "Englewood", "Chicago Lawn", "Deering", "Ogden",
    "Harrison", "Near West", "Wood", "Shakespeare", "Austin",
    "Jefferson Park", "Albany Park", "Near North", "Town Hall", "Morgan Park",
    "Rogers Park", "Pullman"
]

# Define the coordinates or shapes for each district
district_coordinates = {
    "Central": [41.8781, -87.6298],
    "Wentworth": [41.8525, -87.6315],
    "Grand Crossing": [41.7625, -87.6096],
    "South Chicago": [41.7399, -87.5667],
    "Calumet": [41.7300, -87.5545],
    "Gresham": [41.7500, -87.6528],
    "Englewood": [41.7798, -87.6455],
    "Chicago Lawn": [41.7750, -87.6963],
    "Deering": [41.7143, -87.6900],
    "Ogden": [41.8568, -87.6589],
    "Harrison": [41.8731, -87.7050],
    "Near West": [41.8819, -87.6638],
    "Wood": [41.7769, -87.6646],
    "Shakespeare": [41.9182, -87.6525],
    "Austin": [41.8947, -87.7654],
    "Jefferson Park": [41.9702, -87.7649],
    "Albany Park": [41.9681, -87.7234],
    "Near North": [41.9000, -87.6345],
    "Town Hall": [41.9434, -87.6703],
    "Morgan Park": [41.6908, -87.6668],
    "Rogers Park": [42.0095, -87.6768],
    "Pullman": [41.7076, -87.6096]
    # Add coordinates for other districts as needed
}

beat_coordinates = {2222: {'latitude': 41.73008335, 'longitude': -87.65789521},
                    2432: {'latitude': 42.00245638, 'longitude': -87.67452513},
                    424: {'latitude': 41.72974619, 'longitude': -87.54707029},
                    2534: {'latitude': 41.91035839, 'longitude': -87.72742459},
                    1812: {'latitude': 41.92285719, 'longitude': -87.64493045},
                    1833: {'latitude': 41.90004901, 'longitude': -87.62805088},
                    1622: {'latitude': 41.97191129, 'longitude': -87.77393392},
                    2311: {'latitude': 41.96557945, 'longitude': -87.66260565},
                    631: {'latitude': 41.74571729, 'longitude': -87.60395969},
                    1211: {'latitude': 41.87745183, 'longitude': -87.685141},
                    933: {'latitude': 41.79855213, 'longitude': -87.66091383},
                    823: {'latitude': 41.78050758, 'longitude': -87.71805263},
                    2522: {'latitude': 41.92305905, 'longitude': -87.74276698},
                    1824: {'latitude': 41.90190408, 'longitude': -87.62849331},
                    334: {'latitude': 41.76033729, 'longitude': -87.55965726},
                    1031: {'latitude': 41.83983142, 'longitude': -87.7181856},
                    1533: {'latitude': 41.87497665, 'longitude': -87.75342847},
                    834: {'latitude': 41.74144905, 'longitude': -87.70357837},
                    523: {'latitude': 41.67242675, 'longitude': -87.62624777},
                    1333: {'latitude': 41.88489718, 'longitude': -87.67600602},
                    1223: {'latitude': 41.85423319, 'longitude': -87.67605214},
                    2023: {'latitude': 41.98142489, 'longitude': -87.65986484},
                    1423: {'latitude': 41.90770923, 'longitude': -87.6943388},
                    1033: {'latitude': 41.85169421, 'longitude': -87.7023807},
                    932: {'latitude': 41.80062466, 'longitude': -87.668561},
                    2221: {'latitude': 41.72131147, 'longitude': -87.66334244},
                    331: {'latitude': 41.77328043, 'longitude': -87.57297055},
                    2024: {'latitude': 41.97345976, 'longitude': -87.65217463},
                    2523: {'latitude': 41.93611145, 'longitude': -87.72247649},
                    2433: {'latitude': 41.99373375, 'longitude': -87.66052967},
                    312: {'latitude': 41.77874438, 'longitude': -87.61213537},
                    621: {'latitude': 41.75412598, 'longitude': -87.64398778},
                    1414: {'latitude': 41.92569268, 'longitude': -87.70387163},
                    2112: {'latitude': 41.84187918, 'longitude': -87.6231485},
                    2333: {'latitude': 41.93291556, 'longitude': -87.64460547},
                    1323: {'latitude': 41.89962585, 'longitude': -87.66559939},
                    1831: {'latitude': 41.89074162, 'longitude': -87.62867113},
                    2233: {'latitude': 41.68867654, 'longitude': -87.63848857},
                    434: {'latitude': 41.70557895, 'longitude': -87.56070596},
                    2423: {'latitude': 42.01403891, 'longitude': -87.66397341},
                    1313: {'latitude': 41.88915276, 'longitude': -87.70129239},
                    524: {'latitude': 41.67762464, 'longitude': -87.6475502},
                    232: {'latitude': 41.79623446, 'longitude': -87.63040781},
                    124: {'latitude': 41.88799819, 'longitude': -87.62256814},
                    833: {'latitude': 41.75465809, 'longitude': -87.74138501},
                    1331: {'latitude': 41.88119493, 'longitude': -87.69492986},
                    412: {'latitude': 41.73702926, 'longitude': -87.56981134},
                    1412: {'latitude': 41.93081233, 'longitude': -87.7158018},
                    314: {'latitude': 41.78396041, 'longitude': -87.59643156},
                    612: {'latitude': 41.75238256, 'longitude': -87.65678193},
                    2234: {'latitude': 41.68517743, 'longitude': -87.64302923},
                    912: {'latitude': 41.8082678, 'longitude': -87.70168827},
                    324: {'latitude': 41.76199126, 'longitude': -87.58860091},
                    413: {'latitude': 41.72938593, 'longitude': -87.56809575},
                    322: {'latitude': 41.76847723, 'longitude': -87.61904294},
                    1011: {'latitude': 41.86127727, 'longitude': -87.71756894},
                    221: {'latitude': 41.81438055, 'longitude': -87.62921531},
                    715: {'latitude': 41.79103816, 'longitude': -87.6646557},
                    533: {'latitude': 41.65817937, 'longitude': -87.59673282},
                    1422: {'latitude': 41.90650779, 'longitude': -87.71396784},
                    132: {'latitude': 41.87525976, 'longitude': -87.62439833},
                    2011: {'latitude': 41.97593227, 'longitude': -87.69812186},
                    934: {'latitude': 41.79799154, 'longitude': -87.65240032},
                    825: {'latitude': 41.78229233, 'longitude': -87.68479869},
                    411: {'latitude': 41.74635074, 'longitude': -87.5940072},
                    1722: {'latitude': 41.95920112, 'longitude': -87.73075272},
                    835: {'latitude': 41.74853532, 'longitude': -87.6927389},
                    1434: {'latitude': 41.91079699, 'longitude': -87.68221369},
                    1631: {'latitude': 41.9450995, 'longitude': -87.81711306},
                    1813: {'latitude': 41.91131705, 'longitude': -87.64987092},
                    924: {'latitude': 41.83511556, 'longitude': -87.65092444},
                    714: {'latitude': 41.78538062, 'longitude': -87.67149418},
                    1421: {'latitude': 41.91455181, 'longitude': -87.69603778},
                    332: {'latitude': 41.76627248, 'longitude': -87.58397675},
                    1924: {'latitude': 41.940001, 'longitude': -87.65425834},
                    1933: {'latitude': 41.926824, 'longitude': -87.64470774},
                    1523: {'latitude': 41.88601084, 'longitude': -87.75880062},
                    522: {'latitude': 41.68111244, 'longitude': -87.62890557},
                    421: {'latitude': 41.75499732, 'longitude': -87.55444022},
                    423: {'latitude': 41.73661698, 'longitude': -87.55986874},
                    1111: {'latitude': 41.89933429, 'longitude': -87.73098162},
                    1923: {'latitude': 41.95261114, 'longitude': -87.66651346},
                    431: {'latitude': 41.71488314, 'longitude': -87.55962393},
                    1524: {'latitude': 41.89289762, 'longitude': -87.75690249},
                    911: {'latitude': 41.79718478, 'longitude': -87.69741829},
                    915: {'latitude': 41.79401301, 'longitude': -87.67415942},
                    2513: {'latitude': 41.90916786, 'longitude': -87.79236227},
                    311: {'latitude': 41.78024012, 'longitude': -87.62183452},
                    713: {'latitude': 41.784047, 'longitude': -87.65597616},
                    813: {'latitude': 41.79076454, 'longitude': -87.73181578},
                    723: {'latitude': 41.77835911, 'longitude': -87.64460823},
                    1614: {'latitude': 41.97589398, 'longitude': -87.8367713},
                    2514: {'latitude': 41.92975906, 'longitude': -87.77091038},
                    913: {'latitude': 41.83094756, 'longitude': -87.68464536},
                    313: {'latitude': 41.78395819, 'longitude': -87.60512141},
                    1913: {'latitude': 41.94327418, 'longitude': -87.68257439},
                    1311: {'latitude': 41.90211667, 'longitude': -87.69536066},
                    212: {'latitude': 41.82398187, 'longitude': -87.61401269},
                    821: {'latitude': 41.80139471, 'longitude': -87.70393066},
                    1731: {'latitude': 41.94127917, 'longitude': -87.72720178},
                    734: {'latitude': 41.76609088, 'longitude': -87.66248819},
                    1522: {'latitude': 41.88141335, 'longitude': -87.75862515},
                    2515: {'latitude': 41.92415094, 'longitude': -87.7611337},
                    2411: {'latitude': 42.00514091, 'longitude': -87.69013435},
                    222: {'latitude': 41.81150969, 'longitude': -87.60972844},
                    2431: {'latitude': 42.00859887, 'longitude': -87.66803739},
                    2323: {'latitude': 41.94868359, 'longitude': -87.64365277},
                    1132: {'latitude': 41.87304378, 'longitude': -87.72565123},
                    432: {'latitude': 41.71842814, 'longitude': -87.53663726},
                    1624: {'latitude': 41.95785019, 'longitude': -87.749185},
                    513: {'latitude': 41.69807889, 'longitude': -87.62996177},
                    2312: {'latitude': 41.96799444, 'longitude': -87.65747278},
                    2122: {'latitude': 41.82802325, 'longitude': -87.60819227},
                    2521: {'latitude': 41.92836863, 'longitude': -87.75616067},
                    2213: {'latitude': 41.71543767, 'longitude': -87.67840953},
                    1611: {'latitude': 42.00901629, 'longitude': -87.81016115},
                    711: {'latitude': 41.79243939, 'longitude': -87.63766609},
                    1123: {'latitude': 41.88369767, 'longitude': -87.70890375},
                    722: {'latitude': 41.77821494, 'longitude': -87.63346798},
                    1834: {'latitude': 41.88941477, 'longitude': -87.61867782},
                    1424: {'latitude': 41.90339556, 'longitude': -87.67113637},
                    1634: {'latitude': 41.94057799, 'longitude': -87.76115593},
                    512: {'latitude': 41.70621529, 'longitude': -87.61919786},
                    2413: {'latitude': 41.99666603, 'longitude': -87.68510986},
                    211: {'latitude': 41.82853347, 'longitude': -87.62664961},
                    2412: {'latitude': 41.99840711, 'longitude': -87.68000797},
                    1014: {'latitude': 41.85489051, 'longitude': -87.72409423},
                    2533: {'latitude': 41.90513366, 'longitude': -87.75081561},
                    2531: {'latitude': 41.90293936, 'longitude': -87.7658304},
                    1131: {'latitude': 41.87687008, 'longitude': -87.73416319},
                    2532: {'latitude': 41.91401274, 'longitude': -87.76424432},
                    1513: {'latitude': 41.88206122, 'longitude': -87.76974614},
                    1532: {'latitude': 41.88191158, 'longitude': -87.74644734},
                    323: {'latitude': 41.76420907, 'longitude': -87.61145511},
                    712: {'latitude': 41.78935149, 'longitude': -87.64761111},
                    231: {'latitude': 41.80456263, 'longitude': -87.62448503},
                    2535: {'latitude': 41.90359791, 'longitude': -87.72404283},
                    1732: {'latitude': 41.94583163, 'longitude': -87.72508915},
                    1822: {'latitude': 41.90650501, 'longitude': -87.6445845},
                    2332: {'latitude': 41.94103942, 'longitude': -87.643397},
                    2124: {'latitude': 41.80893309, 'longitude': -87.60154108},
                    1431: {'latitude': 41.92273324, 'longitude': -87.69570283},
                    1723: {'latitude': 41.96568561, 'longitude': -87.7219146},
                    824: {'latitude': 41.79001897, 'longitude': -87.70180878},
                    1122: {'latitude': 41.88207222, 'longitude': -87.72097543},
                    1713: {'latitude': 41.96754265, 'longitude': -87.71104201},
                    1931: {'latitude': 41.9379326, 'longitude': -87.67225302},
                    623: {'latitude': 41.74890631, 'longitude': -87.6308474},
                    2022: {'latitude': 41.98547874, 'longitude': -87.65998028},
                    814: {'latitude': 41.81132494, 'longitude': -87.74778907},
                    1433: {'latitude': 41.91742662, 'longitude': -87.66730608},
                    1322: {'latitude': 41.89800936, 'longitude': -87.67604053},
                    634: {'latitude': 41.72589231, 'longitude': -87.61923642},
                    815: {'latitude': 41.80959023, 'longitude': -87.72501884},
                    234: {'latitude': 41.79307232, 'longitude': -87.61828587},
                    2313: {'latitude': 41.96365003, 'longitude': -87.65462498},
                    2212: {'latitude': 41.67737088, 'longitude': -87.68321755},
                    2033: {'latitude': 41.97048265, 'longitude': -87.65780685},
                    1724: {'latitude': 41.96443454, 'longitude': -87.70972282},
                    1832: {'latitude': 41.89581034, 'longitude': -87.6313775},
                    511: {'latitude': 41.71951842, 'longitude': -87.62876101},
                    1231: {'latitude': 41.86520013, 'longitude': -87.66574112},
                    1413: {'latitude': 41.92291438, 'longitude': -87.71426116},
                    112: {'latitude': 41.8780481, 'longitude': -87.62978367},
                    2211: {'latitude': 41.69142914, 'longitude': -87.70274108},
                    1212: {'latitude': 41.88691062, 'longitude': -87.64586737},
                    414: {'latitude': 41.75783754, 'longitude': -87.57993698},
                    2512: {'latitude': 41.92012383, 'longitude': -87.78275306},
                    812: {'latitude': 41.78140808, 'longitude': -87.7644504},
                    2113: {'latitude': 41.84743565, 'longitude': -87.62704721},
                    921: {'latitude': 41.80349896, 'longitude': -87.64634897},
                    1712: {'latitude': 41.9698827, 'longitude': -87.72059479},
                    1213: {'latitude': 41.87305895, 'longitude': -87.66091553},
                    1135: {'latitude': 41.86669414, 'longitude': -87.68851349},
                    2123: {'latitude': 41.81126172, 'longitude': -87.60523041},
                    931: {'latitude': 41.80621782, 'longitude': -87.66719376},
                    2232: {'latitude': 41.7067781, 'longitude': -87.64578291},
                    131: {'latitude': 41.87351512, 'longitude': -87.63346103},
                    1032: {'latitude': 41.84117414, 'longitude': -87.709677},
                    1511: {'latitude': 41.89539565, 'longitude': -87.76921388},
                    1324: {'latitude': 41.89128765, 'longitude': -87.67107781},
                    914: {'latitude': 41.81011896, 'longitude': -87.6861834},
                    1024: {'latitude': 41.85416093, 'longitude': -87.7113678},
                    611: {'latitude': 41.74903676, 'longitude': -87.67082687},
                    735: {'latitude': 41.76740985, 'longitude': -87.67464077},
                    2131: {'latitude': 41.80042579, 'longitude': -87.59681141},
                    2111: {'latitude': 41.85277715, 'longitude': -87.62723804},
                    1232: {'latitude': 41.86692303, 'longitude': -87.65442283},
                    922: {'latitude': 41.83646674, 'longitude': -87.66557012},
                    2524: {'latitude': 41.92624927, 'longitude': -87.72361421},
                    613: {'latitude': 41.74358532, 'longitude': -87.65369734},
                    1023: {'latitude': 41.8580504, 'longitude': -87.6955125},
                    1633: {'latitude': 41.94051529, 'longitude': -87.76621774},
                    1711: {'latitude': 41.99526743, 'longitude': -87.72904414},
                    123: {'latitude': 41.88199496, 'longitude': -87.62765089},
                    2422: {'latitude': 42.02202929, 'longitude': -87.6666866},
                    321: {'latitude': 41.77515164, 'longitude': -87.59777888},
                    632: {'latitude': 41.73473959, 'longitude': -87.60735201},
                    1133: {'latitude': 41.87277206, 'longitude': -87.71535843},
                    1021: {'latitude': 41.85733379, 'longitude': -87.71501886},
                    2424: {'latitude': 42.01933713, 'longitude': -87.68051138},
                    1613: {'latitude': 41.97163707, 'longitude': -87.80466796},
                    1623: {'latitude': 41.97260258, 'longitude': -87.75614393},
                    2132: {'latitude': 41.7879531, 'longitude': -87.59255401},
                    122: {'latitude': 41.88525302, 'longitude': -87.62463674},
                    214: {'latitude': 41.8195043, 'longitude': -87.61858254},
                    1112: {'latitude': 41.90263228, 'longitude': -87.71793215},
                    832: {'latitude': 41.76227244, 'longitude': -87.68670471},
                    1411: {'latitude': 41.93043712, 'longitude': -87.68799318},
                    1823: {'latitude': 41.89986033, 'longitude': -87.63987705},
                    1124: {'latitude': 41.88065088, 'longitude': -87.70626011},
                    531: {'latitude': 41.68555647, 'longitude': -87.61093283},
                    614: {'latitude': 41.73616404, 'longitude': -87.66292796},
                    822: {'latitude': 41.78952401, 'longitude': -87.71934518},
                    1651: {'latitude': 41.97620017, 'longitude': -87.90531241},
                    1134: {'latitude': 41.87358022, 'longitude': -87.7054884},
                    1733: {'latitude': 41.93996043, 'longitude': -87.69799015},
                    733: {'latitude': 41.76647881, 'longitude': -87.64823962},
                    1531: {'latitude': 41.89644844, 'longitude': -87.75304326},
                    422: {'latitude': 41.75168856, 'longitude': -87.56516664},
                    725: {'latitude': 41.7712692, 'longitude': -87.66292914},
                    724: {'latitude': 41.77311179, 'longitude': -87.64962444},
                    233: {'latitude': 41.79256831, 'longitude': -87.61931826},
                    1811: {'latitude': 41.92084027, 'longitude': -87.66303397},
                    1821: {'latitude': 41.91098315, 'longitude': -87.63995139},
                    2324: {'latitude': 41.95261447, 'longitude': -87.65119817},
                    433: {'latitude': 41.6818337, 'longitude': -87.5399662},
                    2525: {'latitude': 41.92437629, 'longitude': -87.72645416},
                    1113: {'latitude': 41.88198358, 'longitude': -87.74016354},
                    2322: {'latitude': 41.96032758, 'longitude': -87.65615298},
                    1034: {'latitude': 41.85207859, 'longitude': -87.67503178},
                    2331: {'latitude': 41.94549641, 'longitude': -87.65497563},
                    1013: {'latitude': 41.84784046, 'longitude': -87.72357021},
                    1114: {'latitude': 41.88450666, 'longitude': -87.73088956},
                    1012: {'latitude': 41.85442853, 'longitude': -87.73120127},
                    133: {'latitude': 41.8578329, 'longitude': -87.62248012},
                    333: {'latitude': 41.76598878, 'longitude': -87.57378977},
                    1932: {'latitude': 41.93365513, 'longitude': -87.64575151},
                    1911: {'latitude': 41.96832671, 'longitude': -87.69638827},
                    1632: {'latitude': 41.93986796, 'longitude': -87.79712363},
                    111: {'latitude': 41.88065102, 'longitude': -87.6431253},
                    213: {'latitude': 41.82254954, 'longitude': -87.61579708},
                    732: {'latitude': 41.76867121, 'longitude': -87.63859377},
                    1121: {'latitude': 41.89711491, 'longitude': -87.71256367},
                    811: {'latitude': 41.79675055, 'longitude': -87.7549337},
                    1312: {'latitude': 41.90014265, 'longitude': -87.69076672},
                    622: {'latitude': 41.74698295, 'longitude': -87.63677186},
                    1512: {'latitude': 41.88627173, 'longitude': -87.77328243},
                    2223: {'latitude': 41.7289573, 'longitude': -87.63841736},
                    1233: {'latitude': 41.85572742, 'longitude': -87.64673368},
                    2032: {'latitude': 41.9688122, 'longitude': -87.68264547},
                    624: {'latitude': 41.75529087, 'longitude': -87.59815962},
                    731: {'latitude': 41.76539607, 'longitude': -87.62669777},
                    935: {'latitude': 41.81092987, 'longitude': -87.63849313},
                    923: {'latitude': 41.8407216, 'longitude': -87.66014223},
                    1621: {'latitude': 41.98064511, 'longitude': -87.75219116},
                    1432: {'latitude': 41.91800922, 'longitude': -87.66650271},
                    1912: {'latitude': 41.95501797, 'longitude': -87.69109077},
                    1332: {'latitude': 41.88275314, 'longitude': -87.67682855},
                    2013: {'latitude': 41.98904963, 'longitude': -87.66526521},
                    224: {'latitude': 41.80536464, 'longitude': -87.6166344},
                    633: {'latitude': 41.72406643, 'longitude': -87.60466617},
                    831: {'latitude': 41.7748488, 'longitude': -87.69343031},
                    1115: {'latitude': 41.88053567, 'longitude': -87.73244712},
                    223: {'latitude': 41.80253687, 'longitude': -87.61512917},
                    1814: {'latitude': 41.92411295, 'longitude': -87.63791682},
                    1125: {'latitude': 41.88022455, 'longitude': -87.68824895},
                    1022: {'latitude': 41.8644747, 'longitude': -87.70697989},
                    1222: {'latitude': 41.85878575, 'longitude': -87.66792226},
                    726: {'latitude': 41.77214508, 'longitude': -87.67678821},
                    2031: {'latitude': 41.96868205, 'longitude': -87.69366729},
                    2133: {'latitude': 41.78872186, 'longitude': -87.5981628},
                    113: {'latitude': 41.88331975, 'longitude': -87.62977725},
                    1224: {'latitude': 41.86223134, 'longitude': -87.66771767},
                    1922: {'latitude': 41.96322198, 'longitude': -87.67489638},
                    1612: {'latitude': 41.98969526, 'longitude': -87.81762836},
                    2511: {'latitude': 41.93757573, 'longitude': -87.78132026},
                    215: {'latitude': 41.81566955, 'longitude': -87.6264022},
                    134: {'latitude': 41.84834997, 'longitude': -87.62712524},
                    1925: {'latitude': 41.94704847, 'longitude': -87.64693094},
                    1221: {'latitude': 41.89271997, 'longitude': -87.70523856},
                    225: {'latitude': 41.80088105, 'longitude': -87.62780807},
                    1934: {'latitude': 41.93679949, 'longitude': -87.6442917},
                    1225: {'latitude': 41.87823235, 'longitude': -87.68388831},
                    1914: {'latitude': 41.96545517, 'longitude': -87.65314238},
                    1921: {'latitude': 41.94044475, 'longitude': -87.68158135},
                    1215: {'latitude': 41.89446667, 'longitude': -87.66136317},
                    1653: {'latitude': 41.97702072, 'longitude': -87.89657613},
                    121: {'latitude': 41.88349097, 'longitude': -87.64124391},
                    235: {'latitude': 41.79325404, 'longitude': -87.5975206},
                    1655: {'latitude': 41.97389263, 'longitude': -87.88667196},
                    1650: {'latitude': 41.97618213, 'longitude': -87.87642115}}

# Sidebar - EDA and Login
st.sidebar.title(":blue[Chicago] :red[CrimeWiz] 👮")
# st.sidebar.subheader("Exploratory Data Analysis")

# Login and Registration Section in the Sidebar
login_option = st.sidebar.radio("Select Option", ["Login", "Register"])

if login_option == "Login":
    # Login
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')

    if st.sidebar.button("Login"):
        select_query = "SELECT password FROM users WHERE username = ?"
        cursor.execute(select_query, (username,))
        result = cursor.fetchone()

        if result:
            hashed_password_from_db = result[0]

            if verify_password(password, hashed_password_from_db):
                st.sidebar.success("Logged in as {}".format(username))
                st.session_state.logged_in = True
            else:
                st.sidebar.error("Invalid password. Please try again.")
        else:
            st.sidebar.error("Username not found. Please register.")

elif login_option == "Register":
    # Registration
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type='password')

    if st.sidebar.button("Register"):
        hashed_password = hash_password(new_password)

        insert_query = "INSERT INTO users (username, password) VALUES (?, ?)"
        values = (new_username, hashed_password)

        cursor.execute(insert_query, values)
        conn.commit()

        st.sidebar.success("Registration successful. You can now log in.")
# Selector for Navigation
navigation_option = st.sidebar.selectbox("Select Option", ["Make Predictions", "Data Analysis"])

# Main Section - Predictions and Map
st.title(":blue[Chicago] :red[CrimeWiz] 👮")

# Check if the user is logged in before allowing access to predictions and map
if getattr(st.session_state, 'logged_in', False):

    if navigation_option == "Make Predictions":
        st.subheader("Crime Forecaster")
        st.divider()


        def generate_forecast(future_dates):
            # Create a DataFrame for future dates
            future_df = pd.DataFrame({'Date': future_dates})

            fh_values = len(future_dates)

            # Initialize an empty list to store predictions
            future_predictions = []

            for i in range(0, fh_values):
                prediction = forecaster_model.predict(fh=i)

                # Extract numerical value from DataFrame
                if isinstance(prediction, pd.DataFrame):
                    # Assuming your DataFrame has a numerical column, adjust 'your_column_name' accordingly
                    prediction = prediction['y'].iloc[0]

                # Flatten nested arrays or sequences
                if isinstance(prediction, (list, np.ndarray)):
                    prediction = np.mean(prediction)  # Take the mean value for simplicity
                else:
                    prediction = float(prediction)

                future_predictions.append(prediction)

            # Assign the list of predictions to the 'predicted_crime_rate' column
            future_df['Predicted Crime Rate'] = future_predictions

            return future_df


        st.subheader(":blue[Crime Rates Forecaster] ")
        # Date Selection
        selected_date = st.date_input('Select a future date:', datetime.now().date() + timedelta(days=30))

        # Generate future dates
        future_dates = pd.date_range(start=datetime.now().date(), end=selected_date, freq='30D')[1:]

        # Generate and display forecast
        forecast_df = generate_forecast(future_dates)



        # Plotting with Plotly
        fig = px.line(forecast_df, x='Date', y='Predicted Crime Rate')
        fig.update_layout(xaxis_title='Month', yaxis_title='Predicted Crime Rates')
        st.plotly_chart(fig)

        st.write("###### Forecasted Crime Rates ")
        st.write(forecast_df)
        st.divider()

        st.subheader(":red[Crime Forecaster based on map]")
        # User Inputs
        selected_date = st.date_input("Select Date", key= '1')
        selected_location = st.selectbox("Select Location", list_of_districts_in_chicago)

        # Retrieve latitude and longitude for the selected location
        selected_latitude, selected_longitude = district_coordinates[selected_location]

        # Create a NumPy array with the selected features
        selected_features = np.array([selected_date.year, selected_date.month, selected_date.day,
                                      selected_date.weekday(), selected_latitude, selected_longitude])

        # Standardize the input using the loaded scaler
        preprocessed_input = scaler.transform(selected_features.reshape(1, -1))

        # Map Section
        st.text("Chicago Districts Map")

        # Create a unique ID for the map div
        map_div_id = f"map-{selected_location}"

        # Display the map div
        html(f'<div id="{map_div_id}"></div>')

        # Create a Folium map
        m = folium.Map(location=[selected_latitude, selected_longitude], zoom_start=12)

        # Add a marker to the map
        folium.Marker([selected_latitude, selected_longitude], popup=selected_location).add_to(m)

        # Display the map
        folium_static(m)

        st.write("Can a Violent Crime happen in {} on {}?".format(selected_location, selected_date))

        # Predictions Button
        predictions = []
        if st.button("See Predictions", key='3'):
            # Add a loading spinner
            with st.spinner('Making Predictions...'):
                # Simulate a delay (you can replace this with the actual prediction logic)
                time.sleep(1.2)
                # Make predictions
                predictions = catboost_model.predict(preprocessed_input)
                if predictions[0] == 1:
                    # Display the predictions
                    st.write(
                        "Predictions for {} in {}: A Violent Crime can happen".format(selected_date, selected_location))
                else:
                    st.write("Predictions for {} in {}: A Violent Crime may not happen".format(selected_date,
                                                                                               selected_location))

            # Save predictions to the database ****CHECK THIS PART****
            insert_prediction_query = "INSERT INTO predictions (username, prediction_text, prediction) VALUES (?, ?,?)"
            prediction_values = (username, f" {selected_date} in {selected_location}", f"{predictions[0]}")

            cursor.execute(insert_prediction_query, prediction_values)
            conn.commit()

            # Display recent predictions
            st.subheader("Recent Predictions")

            prediction_query = "SELECT * FROM predictions WHERE username = ?"
            cursor.execute(prediction_query, (username,))
            prediction_results = cursor.fetchall()

            # for prediction in prediction_results:
            #     st.write(f"Username: {prediction[1]}")
            #     st.write(f"Prediction: {prediction[2]}")
            #     st.write(f"   {prediction[3]}")
            #     st.write("------")

            # Display predictions in a table
            prediction_table = [["Username", "Date And Location", "Prediction"]]
            for prediction in prediction_results:
                prediction_table.append([prediction[1], prediction[2], prediction[3]])

            st.table(prediction_table)
        st.divider()

        st.subheader(":blue[Crime Forecaster Based on Beat]")

        # User Inputs
        selected_date_1 = st.date_input("Select Date", key= '2')
        selected_time = st.time_input("Select a time")
        # Display the selected time
        # st.write("Selected time:", selected_time)
        # selected_beat = st.number_input("Enter Your Beat", step=1, value=0, format="%d")

        # Assuming Beat is a categorical variable, so using a selectbox
        beat_options = sorted(list(beat_coordinates.keys()))
        selected_beat = st.selectbox("Beat", beat_options)

        # Fetch latitude and longitude based on the selected beat
        latitude = beat_coordinates[selected_beat]['latitude']
        longitude = beat_coordinates[selected_beat]['longitude']

        # Create a dictionary with user inputs
        user_data = {
            "Date": selected_date_1,
            "Beat": selected_beat,
            "Time": selected_time,
            "Latitude": latitude,
            "Longitude": longitude,
            # Add other features
        }

        # Convert user inputs to a DataFrame
        input_df = pd.DataFrame([user_data])
        input_df['Date'] = pd.to_datetime(input_df['Date'])

        # Extract relevant features from the 'Date' column
        input_df['Year'] = input_df['Date'].dt.year
        input_df['Month'] = input_df['Date'].dt.month
        input_df['WeekOfYear'] = input_df['Date'].dt.isocalendar().week
        input_df['Quarter'] = input_df['Date'].dt.quarter
        input_df['Day'] = input_df['Date'].dt.day
        input_df['DayOfWeek'] = input_df['Date'].dt.dayofweek
        input_df['IsWeekend'] = input_df['Date'].dt.dayofweek.isin([5, 6]).astype(int)
        input_df['IsWeekday'] = 1 - input_df['IsWeekend']
        input_df['MonthBegin'] = input_df['Date'].dt.is_month_start.astype(int)
        input_df['MonthEnd'] = input_df['Date'].dt.is_month_end.astype(int)
        input_df['Hour'] = selected_time.hour
        input_df['Minute'] = selected_time.minute
        input_df['Second'] = selected_time.second
        input_df['Date'] = input_df['Date'].dt.date
        check_date = input_df['Date'].iloc[0]
        check_holiday = check_date in holidays.US()
        input_df['Holiday'] = check_holiday

        # Display user inputs
        st.write(":green[User Input:]")
        st.write(input_df)
        columns_to_rem = ['Date', 'Time']
        input_df_final = input_df.drop(columns_to_rem, axis=1)
        print(input_df_final.info())

        if st.button("See Predictions", key= '4'):
            # Add a loading spinner
            with st.spinner('Making Predictions...'):
                # Simulate a delay (you can replace this with the actual prediction logic)
                time.sleep(1.2)
                # Make predictions
                predictions_multiclass = multiclass_model.predict(input_df_final)
                st.write(predictions_multiclass)
                # if predictions[0] == 1:
                #     # Display the predictions
                #     st.write(
                #         "Predictions for {} in {}: A Violent Crime can happen".format(selected_date, selected_location))
                # else:
                #     st.write("Predictions for {} in {}: A Violent Crime may not happen".format(selected_date,
                #                                                                                selected_location))



        # # Retrieve latitude and longitude for the selected location
        # selected_latitude, selected_longitude = district_coordinates[selected_location]
        #
        # # Create a NumPy array with the selected features
        # selected_features_1 = np.array([selected_date.year, selected_date.month, selected_date.day,
        #                                 selected_date.weekday(), selected_latitude, selected_longitude,
        #                                 selected_time.hour, selected_time.minute, selected_time.second, selected_beat])




    elif navigation_option == "Data Analysis":
        # Data Analysis logic goes here
        st.subheader("Data Analysis Section")
        # st.write("This is the Data Analysis section.")

        # Socrata API endpoint for Chicago crime data
        socrata_domain = "data.cityofchicago.org"
        socrata_dataset_identifier = "ijzp-q8t2"

        # Create a Socrata client
        client = Socrata(socrata_domain, None)

        # Add date and time input options
        start_date = st.date_input("Start Date", datetime(2022, 1, 1))
        end_date = st.date_input("End Date", datetime.today())

        # Convert the selected dates to strings
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S')

        # Build the query for the Socrata API
        query = f"date between '{start_date_str}' and '{end_date_str}'"

        # Create a spinner for loading animation
        with st.spinner("Loading data..."):
            # Fetch the data from the Socrata API
            results = client.get(socrata_dataset_identifier, where=query, limit=100000)

        # Convert the data to a DataFrame
        df = pd.DataFrame.from_records(results)

        # Convert the 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'])

        # Convert the 'latitude' and 'longitude' columns to numeric, filtering out non-numeric values
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

        # Extract the day of the week and create a new column
        df['day_of_week'] = df['date'].dt.day_name()

        # Filter out non-numeric values before calculating the mean
        filtered_df = df[['latitude', 'longitude']].apply(pd.to_numeric, errors='coerce')

        # Display a map of crime locations for the selected time frame
        st.subheader("Crime Map for Selected Time Frame")
        st.map(filtered_df[['latitude', 'longitude']].dropna())

        # Display the raw data for the selected time frame
        st.subheader("Raw Data for Selected Time Frame")
        st.write(df)

        # Display the raw data for the selected time frame
        st.subheader("Crime data for Selected Time Frame")
        st.write(df['primary_type'].value_counts())

        # # Display some basic statistics for the selected time frame
        # st.subheader("Basic Statistics for Selected Time Frame")
        # df_new = df[['primary_type', 'location_description', 'arrest', 'domestic', 'day_of_week', 'latitude', 'longitude', 'date']]
        # st.write(df_new.describe())

        # Display a bar chart of crime types for the selected time frame
        st.subheader("Crime Types for Selected Time Frame")
        crime_counts = df['primary_type'].value_counts()
        st.bar_chart(crime_counts)

        # Display the top 10 crime locations for the selected time frame
        st.subheader("Top 10 Crime Locations for Selected Time Frame")
        top_locations = df['location_description'].value_counts().head(10)
        # st.write(top_locations)

        # Create a Plotly pie chart for the top 10 crime locations
        fig_top_locations = px.pie(top_locations, names=top_locations.index, values=top_locations.values,
                                   title="Top 10 Crime Locations for Selected Time Frame")

        # Display the Plotly pie chart using st.plotly_chart
        st.plotly_chart(fig_top_locations)

        # Display a bar chart of crime counts per day of the week for the selected time frame
        st.subheader("Crime Counts per Day of the Week for Selected Time Frame")
        day_of_week_counts = df['day_of_week'].value_counts()
        st.bar_chart(day_of_week_counts, color='#ffaa00')

        # Extract the time of the day and create a new column
        df['time_of_day'] = pd.cut(df['date'].dt.hour,
                                   bins=[0, 6, 12, 18, 24],
                                   labels=['Night', 'Morning', 'Afternoon', 'Evening'],
                                   right=False)

        # Display the crime counts per time of the day with corresponding hours
        st.subheader("Crime Counts per Time of the Day for Selected Time Frame")
        time_of_day_counts = df['time_of_day'].value_counts()
        st.bar_chart(time_of_day_counts, color='#00ffaa')

        # Display the corresponding hours for each time of day
        time_of_day_hours = {
            'Night': '0:00 - 5:59',
            'Morning': '6:00 - 11:59',
            'Afternoon': '12:00 - 17:59',
            'Evening': '18:00 - 23:59'
        }

        for time_of_day, hours in time_of_day_hours.items():
            st.write(f"{time_of_day}: {hours}")

        # Extract the time of the day and create a new column
        df['hour_of_day'] = df['date'].dt.hour

        # Display the crime counts per hour of the day
        st.subheader("Crime Counts per Hour of the Day for Selected Time Frame")
        hour_of_day_counts = df['hour_of_day'].value_counts().sort_index()

        # Create a line chart using Plotly
        fig_line_chart = px.line(x=hour_of_day_counts.index, y=hour_of_day_counts.values,
                                 labels={'x': 'Hour of the Day', 'y': 'Crime Count'},
                                 title="Crime Counts per Hour of the Day")

        # Display the Plotly line chart using st.plotly_chart
        st.plotly_chart(fig_line_chart)

        # Create a space before the dropdown
        st.markdown("&nbsp;")  # Add a non-breaking space using Markdown

        # Create a dropdown to select a day of the week
        selected_day = st.selectbox("Select a Day of the Week", df['day_of_week'].unique())

        # Filter data for the selected day of the week
        selected_day_data = df[df['day_of_week'] == selected_day]

        # Display the count for the top 5 crimes for the selected day
        st.subheader(f"Top 5 Crimes on {selected_day}")
        top_crimes = selected_day_data['primary_type'].value_counts().head(5)
        # st.write(top_crimes)

        # Create a Plotly bar chart
        fig = px.bar(top_crimes, x=top_crimes.index, y=top_crimes.values,
                     labels={'x': 'Crime Type', 'y': 'Crime Count'},
                     title=f"Top 5 Crimes on {selected_day}")

        # Display the Plotly bar chart using st.plotly_chart
        st.plotly_chart(fig)

else:
    st.warning("Please log in to access Predictions and the Data Analysis.")

# Close the SQLite connection when done
conn.close()
