# Elemental abundances. Taken from chemcomp/helpers/units/chemistry_const.py
OH_init_abu = 4.9e-4  # O/H abundance, solar value
CH_init_abu = 2.69e-4  # C/H abundance, solar value
SiH_init_abu = 3.24e-5  # Si/H adundance, solar value
FeH_init_abu = 3.16e-5  # Fe/H adundance, solar value
SH_init_abu = 1.32e-5  # S/H adundance, solar value
MgH_init_abu = 3.98e-5  # Mg/H adundance, solar value
HeH_init_abu = 0.085 
AlH_init_abu = 2.82e-6
TiH_init_abu = 8.91e-8
KH_init_abu = 1.07e-7
NaH_init_abu = 1.74e-6
NH_init_abu = 6.76e-5
VH_init_abu = 8.59e-9

# array of species names. Taken from chemcomp/helpers/analysis_helper.py
element_array = ["C_elem", "O", "Fe", "S", "Mg", "Si", "Na", "K", "N", "Al", "Ti", "V", "H", "He"]
molecule_array = [ 
    "rest",
    "CO",
    "N2",
    "CH4",
    "CO2",
    "NH3",
    "trapped_CO_water",
    "trapped_CO2_water",
    "H2S",
    "H2O",
    "Fe3O4",
    "C",
    "FeS",
    "NaAlSi3O8",
    "KAlSi3O8",
    "Mg2SiO4",
    "Fe2O3",
    "VO",
    "MgSiO3",
    "Al2O3",
    "TiO",
]
iceline_names = [
                "CO & N2",
                "CH4",
                "CO2",
                "NH3",
                "H2O &\nH2S",
                "Fe3O4",
                "C grains",
                "FeS",
                "NaAlSi3O8",
                "KAlSi3O8",
                "Mg2SiO4",
                "Fe2O3",
                "VO",
                "MgSiO3",
                "Al2O3",
                "TiO",
            ]

# Used to skip over trapped molecules
iceline_molecules_and_temps = { 
    "CO" : 20,
    "N2" : 20,
    "CH4" : 30,
    "CO2": 70,
    "NH3": 90,
    "H2S" : 150,
    "H2O" : 150,
    "Fe3O4" : 371,
    "C" : 631,
    "FeS" : 704,
    "NaAlSi3O8" : 958,
    "KAlSi3O8" : 1006,
    "Mg2SiO4": 1354,
    "Fe2O3" : 1357,
    "VO" : 1423,
    "MgSiO3" : 1500,
    "Al2O3" : 1653,
    "TiO" : 2000
}

iceline_temperatures = [20, 30, 70, 90, 150, 371, 631, 704, 958, 1006, 1354, 1357, 1423, 1500, 1653, 2000]