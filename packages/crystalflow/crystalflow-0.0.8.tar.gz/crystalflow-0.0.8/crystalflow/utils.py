import numpy as np
from ase.db import connect
from ase.spacegroup import get_spacegroup
from ase import Atoms
import spglib
from pymatgen.core.structure import Structure, Lattice
from pymatgen.analysis.diffraction import xrd
from scipy.special import wofz

def prim2conv(prim_atom):
    """
    Convert a primitive cell to a conventional cell.

    Parameters:
    -----------
    prim_atom : Atoms
        The primitive atom defined in the atomic simulation unit.

    Returns:
    --------
    tuple
        Lattice constants, conventional lattice cell matrix in Cartesian coordinates, Atoms attribute.
    """
    lattice = prim_atom.get_cell()
    positions = prim_atom.get_scaled_positions()
    numbers = prim_atom.get_atomic_numbers()
    cell = (lattice, positions, numbers)

    # Standardize cell using spglib
    conventional_cell = spglib.standardize_cell(cell, to_primitive=False, no_idealize=True)
    conv_lattice, conv_positions, conv_numbers = conventional_cell

    # Create Atoms object for conventional cell
    conventional_atoms = Atoms(cell=conv_lattice, scaled_positions=conv_positions, numbers=conv_numbers, pbc=True)
    lc = conventional_atoms.cell.cellpar()
    lmtx = conventional_atoms.get_cell()[:]
    return lc, lmtx, conventional_atoms


def matgen_xrdsim(atom, avi_size, step):
    """
    Simulate XRD pattern for the given atomic structure.

    Parameters:
    -----------
    atom : Atoms
        Atomic structure for which XRD is simulated.
    avi_size : float
        Average lattice size for broadening peaks.
    step : float
        Resolution for XRD simulation.
    
    Returns:
    --------
    ndarray
        Simulated XRD intensity profile.
    """
    wavelength = 1.54184  # Cu Kα radiation
    two_theta_range = (10, 100, step)

    # Get diffraction data
    mu_array, Ints = get_diff(atom)

    # Apply Lorentz correction
    Ints = Ints * np.sin(np.radians(mu_array/2)) ** 2 * np.cos(np.radians(mu_array/2))

    # Calculate peak broadening
    Γ = 0.888 * wavelength / (avi_size * np.cos(np.radians(mu_array) / 2))
    gamma_list = Γ / 2 + 1e-10
    sigma2_list = Γ ** 2 / (8 * np.sqrt(2)) + 1e-10

    # Simulate XRD pattern
    x_sim = np.arange(two_theta_range[0], two_theta_range[1], two_theta_range[2])
    y_sim = np.zeros_like(x_sim)
    for num in range(len(Ints)):
        y_sim += draw_peak_density(x_sim, Ints[num], mu_array[num], gamma_list[num], sigma2_list[num])

    # Normalize the intensity profile
    nor_y = y_sim / theta_intensity_area(x_sim, y_sim)
    return nor_y, list(zip(mu_array, Ints/Ints.max() * 100))


def get_diff(atom):
    """
    Get XRD pattern using Pymatgen for the given atomic structure.

    Parameters:
    -----------
    atom : Atoms
        Atomic structure for which the diffraction pattern is calculated.
    
    Returns:
    --------
    tuple
        Two theta angles (x) and intensities (y).
    """
    calculator = xrd.XRDCalculator()
    struc = _atom2str(atom)

    pattern = calculator.get_pattern(struc, two_theta_range=(10, 80))
    return pattern.x, pattern.y


def _atom2str(atoms, ):
    """
    Convert ASE Atoms object to Pymatgen Structure object.

    Parameters:
    -----------
    atoms : Atoms
        ASE Atoms object.

    Returns:
    --------
    Structure
        Pymatgen Structure object.
    """
    _, _, c_atom = prim2conv(atoms)
    cell = c_atom.get_cell()
    symbols = c_atom.get_chemical_symbols()
    positions = c_atom.get_scaled_positions()
    lattice = Lattice(cell)
    return Structure(lattice, symbols, positions)


def draw_peak_density(x, Weight, mu, gamma, sigma2):
    """
    Generate Voigt peak shape based on input parameters.

    Parameters:
    -----------
    x : ndarray
        X-axis values (e.g., two theta angles).
    Weight : float
        Peak intensity.
    mu : float
        Peak position (mean value).
    gamma : float
        Lorentzian width.
    sigma2 : float
        Gaussian variance.

    Returns:
    --------
    ndarray
        Simulated peak density.
    """
    z = ((x - mu) + 1j * gamma) / (np.sqrt(sigma2) * np.sqrt(2))
    Voigt = np.real(wofz(z) / (np.sqrt(sigma2) * np.sqrt(2 * np.pi)))
    peak_density = Weight * Voigt
    return peak_density


def theta_intensity_area(theta_data, intensity):
    """
    Calculate the area under the intensity curve.

    Parameters:
    -----------
    theta_data : ndarray
        X-axis values (e.g., two theta angles).
    intensity : ndarray
        Corresponding intensity values.

    Returns:
    --------
    float
        Area under the curve.
    """
    return np.trapz(intensity, theta_data)

def space_group_to_crystal_system(space_group):
    if space_group < 1 or space_group > 230:
        return "Invalid space group number"
    elif space_group <= 2:
        return 7  
    elif space_group <= 15:
        return 6  
    elif space_group <= 74:
        return 4  
    elif space_group <= 142:
        return 3 
    elif space_group <= 167:
        return 5  
    elif space_group <= 194:
        return 2 
    else:
        return 1 
    
def symbol_to_atomic_number(symbol_list):
    # Mapping of element symbols to atomic numbers
    atomic_numbers = {
        'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5,
        'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10,
        'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,
        'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20,
        'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25,
        'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29, 'Zn': 30,
        'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35,
        'Kr': 36, 'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40,
        'Nb': 41, 'Mo': 42, 'Tc': 43, 'Ru': 44, 'Rh': 45,
        'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50,
        'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55,
        'Ba': 56, 'La': 57, 'Ce': 58, 'Pr': 59, 'Nd': 60,
        'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64, 'Tb': 65,
        'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70,
        'Lu': 71, 'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75,
        'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79, 'Hg': 80,
        'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85,
        'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90,
        'Pa': 91, 'U': 92, 'Np': 93, 'Pu': 94, 'Am': 95,
        'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99, 'Fm': 100,
        'Md': 101, 'No': 102, 'Lr': 103, 'Rf': 104, 'Db': 105,
        'Sg': 106, 'Bh': 107, 'Hs': 108, 'Mt': 109, 'Ds': 110,
        'Rg': 111, 'Cn': 112, 'Nh': 113, 'Fl': 114, 'Mc': 115,
        'Lv': 116, 'Ts': 117, 'Og': 118
    }
    
    atomic_number_list = []
    for symbol in symbol_list:
        if symbol in atomic_numbers:
            atomic_number_list.append(atomic_numbers[symbol])
        else:
            atomic_number_list.append(0)  # Append None if symbol not in the dictionary
    
    return atomic_number_list


