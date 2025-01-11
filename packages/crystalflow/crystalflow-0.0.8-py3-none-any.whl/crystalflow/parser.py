import numpy as np
from ase.db import connect
from ase.spacegroup import get_spacegroup
from ase import Atoms
import spglib
from pymatgen.core.structure import Structure, Lattice
from pymatgen.analysis.diffraction import xrd
from scipy.special import wofz
import warnings
from . import atom_emb
from .utils import *

def get(dataloc, entry_id, max_atom_num=500, property_list=['formation_energy', 'band_gap','bulk_modulus'], avi_size=10, step=0.01):
    """
    Main Function

    Parameters
    ----------
    dataloc : str
        Path to the database file (e.g., 'MP.db').
    entry_id : int
        The ID of the data entry to be processed. Index starts from 1 in the database file.
    max_atom_num : int, optional
        Maximum number of atoms allowed in a lattice cell. Default is 500. If the number of atoms exceeds this limit, the structure is removed.
    property_list : list, optional
        List of properties to be extracted from the database. Default is ['formation_energy'].
    step : float, optional
        Resolution of the XRD simulation. Default is 0.01.
    avi_size : int, optional
        Assigned value for the average grain size. Default is 10.

    Returns
    -------
    tuple or None
        Returns a tuple containing the following components if successful, otherwise `None`:
        
        - pxrd : ndarray
            Simulated powder XRD pattern with fixed peak broadening over a diffraction range of 10-100° under Cu-Kα target diffraction.  
            The dimension of this pattern is determined by `step`, with length proportional to the range and resolution.  
        
        - peak_pair : list of tuple
            List of diffraction angle-intensity pairs, where each element is a tuple `(diffraction angle, diffraction intensity)`.

        - _cryst : list
            Contains information about the crystal in the conventional lattice cell:
            - `G_latt_consts` : Lattice constants.
            - `cell` : Lattice vectors.
            - `G_spacegroup` : Space group.
            - `crystal_system` : Crystal system.
            - `sites` : Fractional coordinates of all atoms.
            - `N_symbols` : Atomic elements in the lattice.

        - _graph : list
            Graph embedding details:
            - `node_emb` : 92-dimensional node embedding for atoms, generated using CGCNN.
            - `cart_sites` : Cartesian coordinate of all atoms in the cell, reflecting their relative locations.
            - `distance_matrix` : Spatial distance matrix for each atomic pair in Cartesian coordinates.

        - _obj : any
            Target(s) for downstream tasks.

    Notes
    -----
    - The Lorentz effect is accounted for in the XRD simulation.
    """
    database = connect(dataloc)

    warnings.filterwarnings("ignore")
    # _loc = pkg_resources.resource_filename('crystalflow', '')
   
    cgcnn_emb = atom_emb.data

    try:
        # Retrieve atoms from database
        atoms = database.get_atoms(id=entry_id)

        # Convert primitive cell to conventional cell
        G_latt_consts, _, c_atom = prim2conv(atoms)
        N_symbols = c_atom.get_chemical_symbols() 
        G_spacegroup = get_spacegroup(c_atom).no  
        crystal_system = space_group_to_crystal_system(G_spacegroup)  
        sites = c_atom.get_scaled_positions()
        cell = c_atom.get_cell()

        # Collect structure information
        _cryst = [G_latt_consts, cell, G_spacegroup, crystal_system, sites, N_symbols, ]

        positions = c_atom.get_scaled_positions()
        if len(positions) > max_atom_num:
            return None  # Too many atoms, return nothing

        pxrd, peak_pair = matgen_xrdsim(atoms, avi_size, step)

        # Retrieve specified properties from the database
        _obj = [database.get(id=entry_id)[prop] for prop in property_list]

        # Convert the cryst to graph
        element_encode = symbol_to_atomic_number(N_symbols)

        node_emd = []
        for _code in element_encode:
            value = cgcnn_emb[str(_code)] # 92-d
            node_emd.append(np.array(value))

        distance_matrix = c_atom.get_all_distances()
        cart_sites = c_atom.get_positions()
        _graph = [node_emd,cart_sites ,distance_matrix]
        return pxrd, peak_pair,_cryst,_graph, _obj

    except Exception as e:
        print(f"An error occurred: crystal id = {entry_id}", e)
        return None

