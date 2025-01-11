"""Utility functions for classical MD subpackage."""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np

from pymatgen.analysis.graphs import MoleculeGraph
from pymatgen.analysis.local_env import OpenBabelNN, metal_edge_extender
from pymatgen.core import Element, Molecule

try:
    import openff.toolkit as tk
    from openff.units import Quantity, unit
except ImportError:
    tk = None
    Quantity = None
    unit = None
    warnings.warn(
        "To use the pymatgen.io.openff module install openff-toolkit and openff-units"
        "with `conda install -c conda-forge openff-toolkit openff-units`.",
        stacklevel=2,
    )


def mol_graph_to_openff_mol(mol_graph: MoleculeGraph) -> tk.Molecule:
    """
    Convert a Pymatgen MoleculeGraph to an OpenFF Molecule.

    Args:
        mol_graph (MoleculeGraph): The Pymatgen MoleculeGraph to be converted.

    Returns:
        tk.Molecule: The converted OpenFF Molecule.
    """
    # create empty openff_mol and prepare a periodic table
    p_table = {str(el): el.Z for el in Element}
    openff_mol = tk.Molecule()

    # set atom properties
    partial_charges = []
    # TODO: should assert that there is only one molecule
    for i_node in range(len(mol_graph.graph.nodes)):
        node = mol_graph.graph.nodes[i_node]
        atomic_number = node.get("atomic_number") or p_table[mol_graph.molecule[i_node].species_string]

        # put formal charge on first atom if there is none present
        formal_charge = node.get("formal_charge")
        if formal_charge is None:
            formal_charge = (i_node == 0) * round(mol_graph.molecule.charge) * unit.elementary_charge

        # assume not aromatic if no info present
        is_aromatic = node.get("is_aromatic") or False

        openff_mol.add_atom(atomic_number, formal_charge, is_aromatic=is_aromatic)

        # add to partial charge array
        partial_charge = node.get("partial_charge")
        if isinstance(partial_charge, Quantity):
            partial_charge = partial_charge.magnitude
        partial_charges.append(partial_charge)

    charge_array = np.array(partial_charges)
    if np.not_equal(charge_array, None).all():
        openff_mol.partial_charges = charge_array * unit.elementary_charge

    # set edge properties, default to single bond and assume not aromatic
    for i_node, j, bond_data in mol_graph.graph.edges(data=True):
        bond_order = bond_data.get("bond_order") or 1
        is_aromatic = bond_data.get("is_aromatic") or False
        openff_mol.add_bond(i_node, j, bond_order, is_aromatic=is_aromatic)

    openff_mol.add_conformer(mol_graph.molecule.cart_coords * unit.angstrom)
    return openff_mol


def mol_graph_from_openff_mol(molecule: tk.Molecule) -> MoleculeGraph:
    """
    This is designed to closely mirror the graph structure generated by tk.Molecule.to_networkx.

    Args:
        molecule (tk.Molecule): The OpenFF Molecule to convert.

    Returns:
        MoleculeGraph: The converted MoleculeGraph.
    """
    mol_graph = MoleculeGraph.from_empty_graph(Molecule([], []), name="none")
    p_table = {el.Z: str(el) for el in Element}
    total_charge = cum_atoms = 0

    coords = molecule.conformers[0].magnitude if molecule.conformers is not None else np.zeros((molecule.n_atoms, 3))
    for idx, atom in enumerate(molecule.atoms):
        mol_graph.insert_node(
            cum_atoms + idx,
            p_table[atom.atomic_number],
            coords[idx, :],
        )
        mol_graph.graph.nodes[cum_atoms + idx]["atomic_number"] = atom.atomic_number
        mol_graph.graph.nodes[cum_atoms + idx]["is_aromatic"] = atom.is_aromatic
        mol_graph.graph.nodes[cum_atoms + idx]["stereochemistry"] = atom.stereochemistry
        # set partial charge as a pure float
        partial_charge = None if atom.partial_charge is None else atom.partial_charge.magnitude
        mol_graph.graph.nodes[cum_atoms + idx]["partial_charge"] = partial_charge
        # set formal charge as a pure float
        formal_charge = atom.formal_charge.magnitude
        mol_graph.graph.nodes[cum_atoms + idx]["formal_charge"] = formal_charge
        total_charge += formal_charge
    for bond in molecule.bonds:
        mol_graph.graph.add_edge(
            cum_atoms + bond.atom1_index,
            cum_atoms + bond.atom2_index,
            bond_order=bond.bond_order,
            is_aromatic=bond.is_aromatic,
            stereochemistry=bond.stereochemistry,
        )
    # formal_charge += molecule.total_charge
    cum_atoms += molecule.n_atoms
    mol_graph.molecule.set_charge_and_spin(charge=total_charge)
    return mol_graph


def get_atom_map(inferred_mol: tk.Molecule, openff_mol: tk.Molecule) -> tuple[bool, dict[int, int]]:
    """
    Compute an atom mapping between two OpenFF Molecules.

    Attempts to find an isomorphism between the molecules, considering various matching
    criteria such as formal charges, stereochemistry, and bond orders. Returns the atom
    mapping if an isomorphism is found, otherwise returns an empty mapping.

    Args:
        inferred_mol (tk.Molecule): The first OpenFF Molecule.
        openff_mol (tk.Molecule): The second OpenFF Molecule.

    Returns:
        Tuple[bool, Dict[int, int]]: A tuple containing a boolean indicating if an
            isomorphism was found and a dictionary representing the atom mapping.
    """
    # do not apply formal charge restrictions
    kwargs = {
        "return_atom_map": True,
        "formal_charge_matching": False,
    }
    isomorphic, atom_map = tk.topology.Molecule.are_isomorphic(openff_mol, inferred_mol, **kwargs)
    if isomorphic:
        return True, atom_map
    # relax stereochemistry restrictions
    kwargs["atom_stereochemistry_matching"] = False
    kwargs["bond_stereochemistry_matching"] = False
    isomorphic, atom_map = tk.topology.Molecule.are_isomorphic(openff_mol, inferred_mol, **kwargs)
    if isomorphic:
        return True, atom_map
    # relax bond order restrictions
    kwargs["bond_order_matching"] = False
    isomorphic, atom_map = tk.topology.Molecule.are_isomorphic(openff_mol, inferred_mol, **kwargs)
    if isomorphic:
        return True, atom_map
    return False, {}


def infer_openff_mol(
    mol_geometry: Molecule,
) -> tk.Molecule:
    """Infer an OpenFF Molecule from a Pymatgen Molecule.

    Constructs a MoleculeGraph from the Pymatgen Molecule using the OpenBabelNN local
    environment strategy and extends metal edges. Converts the resulting MoleculeGraph
    to an OpenFF Molecule using mol_graph_to_openff_mol.

    Args:
        mol_geometry (pymatgen.core.Molecule): The Pymatgen Molecule to infer from.

    Returns:
        tk.Molecule: The inferred OpenFF Molecule.
    """
    mol_graph = MoleculeGraph.from_local_env_strategy(mol_geometry, OpenBabelNN())
    mol_graph = metal_edge_extender(mol_graph)
    return mol_graph_to_openff_mol(mol_graph)


def add_conformer(openff_mol: tk.Molecule, geometry: Molecule | None) -> tuple[tk.Molecule, dict[int, int]]:
    """
    Add conformers to an OpenFF Molecule based on the provided geometry.

    If a geometry is provided, infers an OpenFF Molecule from it,
    finds an atom mapping between the inferred molecule and the
    input molecule, and adds the conformer coordinates to the input
    molecule. If no geometry is provided, generates a single conformer.

    Args:
        openff_mol (tk.Molecule): The OpenFF Molecule to add conformers to.
        geometry (Union[pymatgen.core.Molecule, None]): The geometry to use for adding
            conformers.

    Returns:
        Tuple[tk.Molecule, Dict[int, int]]: A tuple containing the updated OpenFF
            Molecule with added conformers and a dictionary representing the atom
            mapping.
    """
    # TODO: test this
    if geometry:
        # for geometry in geometries:
        inferred_mol = infer_openff_mol(geometry)
        is_isomorphic, atom_map = get_atom_map(inferred_mol, openff_mol)
        if not is_isomorphic:
            raise ValueError(
                f"An isomorphism cannot be found between smile {openff_mol.to_smiles()}"
                f"and the provided molecule {geometry}."
            )
        new_mol = Molecule.from_sites([geometry.sites[i] for i in atom_map.values()])
        openff_mol.add_conformer(new_mol.cart_coords * unit.angstrom)
    else:
        atom_map = {i: i for i in range(openff_mol.n_atoms)}
        openff_mol.generate_conformers(n_conformers=1)
    return openff_mol, atom_map


def assign_partial_charges(
    openff_mol: tk.Molecule,
    atom_map: dict[int, int],
    charge_method: str,
    partial_charges: None | list[float],
) -> tk.Molecule:
    """
    Assign partial charges to an OpenFF Molecule.

    If partial charges are provided, assigns them to the molecule
    based on the atom mapping. If the molecule has only one atom,
    assigns the total charge as the partial charge. Otherwise,
    assigns partial charges using the specified charge method.

    Args:
        openff_mol (tk.Molecule): The OpenFF Molecule to assign partial charges to.
        atom_map (Dict[int, int]): A dictionary representing the atom mapping.
        charge_method (str): The charge method to use if partial charges are
            not provided.
        partial_charges (Union[None, List[float]]): A list of partial charges to
            assign or None to use the charge method.

    Returns:
        tk.Molecule: The OpenFF Molecule with assigned partial charges.
    """
    # TODO: test this
    # assign partial charges
    if partial_charges is not None:
        partial_charges = np.array(partial_charges)
        chargs = partial_charges[list(atom_map.values())]  # type: ignore[index, call-overload]
        openff_mol.partial_charges = chargs * unit.elementary_charge
    elif openff_mol.n_atoms == 1:
        openff_mol.partial_charges = np.array([openff_mol.total_charge.magnitude]) * unit.elementary_charge
    else:
        openff_mol.assign_partial_charges(charge_method)
    return openff_mol


def create_openff_mol(
    smile: str,
    geometry: Molecule | str | Path | None = None,
    charge_scaling: float = 1,
    partial_charges: list[float] | None = None,
    backup_charge_method: str = "am1bcc",
) -> tk.Molecule:
    """Create an OpenFF Molecule from a SMILES string and optional geometry.

    Constructs an OpenFF Molecule from the provided SMILES
    string, adds conformers based on the provided geometry (if
    any), assigns partial charges using the specified method
    or provided partial charges, and applies charge scaling.

    Args:
        smile (str): The SMILES string of the molecule.
        geometry (Union[pymatgen.core.Molecule, str, Path, None], optional): The
            geometry to use for adding conformers. Can be a Pymatgen Molecule,
            file path, or None.
        charge_scaling (float, optional): The scaling factor for partial charges.
            Default is 1.
        partial_charges (Union[List[float], None], optional): A list of partial
            charges to assign, or None to use the charge method.
        backup_charge_method (str, optional): The backup charge method to use if
            partial charges are not provided. Default is "am1bcc".

    Returns:
        tk.Molecule: The created OpenFF Molecule.
    """
    if isinstance(geometry, str | Path):
        geometry = Molecule.from_file(str(geometry))

    if partial_charges is not None:
        if geometry is None:
            raise ValueError("geometries must be set if partial_charges is set")
        if len(partial_charges) != len(geometry):
            raise ValueError("partial charges must have same length & order as geometry")

    openff_mol = tk.Molecule.from_smiles(smile, allow_undefined_stereo=True)

    # add conformer
    openff_mol, atom_map = add_conformer(openff_mol, geometry)
    # assign partial charges
    openff_mol = assign_partial_charges(
        openff_mol,
        atom_map,
        backup_charge_method,
        partial_charges,
    )
    openff_mol.partial_charges *= charge_scaling

    return openff_mol
