import unittest

from ..db_engine import db_engine
from ..user_management import check_user_exists, add_new_user, remove_user, update_user
from ..calculation_management import (
    get_all_available_basis_sets,
    get_all_available_calculations,
    get_all_available_methods,
    get_all_available_solvent_effects
)
from ..db_tables import User
from ...models import UserModel


class TestDB(unittest.TestCase):
    def test_db_engine(self):
        db_engine.validate_connection()

    def test_check_user_does_not_exists(self):
        self.assertFalse(check_user_exists("this_user_does_not_exist"))

    def test_add_and_remove_user(self):
        username_for_test = "test_user@test_domain.com"
        if check_user_exists(username_for_test):
            self.assertTrue(remove_user(username_for_test))

        self.assertTrue(add_new_user(username_for_test))
        self.assertTrue(remove_user(username_for_test))

    def test_patch_user(self):
        user_model_for_test = UserModel(email="testuser@testdomain.com")
        user_for_test = "testuser@testdomain.com"

        if check_user_exists(user_for_test):
            self.assertTrue(remove_user(user_for_test))

        self.assertFalse(update_user(user_model_for_test))
        self.assertTrue(add_new_user(user_for_test))
        self.assertTrue(update_user(user_model_for_test))

    def test_get_available_calculations(self):
        available_calculations = [
            {"id": 1, "name": "Single-Point-Calculation"},
            {"id": 2, "name": "Geometry-Optimization"},
            {"id": 3, "name": "Vibrational-Frequencies"},
        ]

        available_calculations_response = get_all_available_calculations()

        available_calculations_as_dict = [
            {"id": item.id, "name": item.name}
            for item in available_calculations_response
        ]

        self.assertEqual(available_calculations_as_dict, available_calculations)

    def test_get_available_basis_sets(self):
        available_basis_sets = [
            {"id": 1, "name": "Minimal: STO-3G"},
            {"id": 2, "name": "Basic: 3-21G"},
            {"id": 3, "name": "Routine: 6-31G(d)"},
            {"id": 4, "name": "Accurate: 6-311+G(2d,p)"},
            {"id": 5, "name": "cc-pVDZ"},
            {"id": 6, "name": "cc-pVTZ"},
        ]

        available_basis_sets_response = get_all_available_basis_sets()

        available_basis_sets_as_dict = [
            {"id": item.id, "name": item.name} for item in available_basis_sets_response
        ]

        self.assertEqual(available_basis_sets_as_dict, available_basis_sets)

    def test_get_available_methods(self):
        available_methods = [
            {"id": 1, "name": "Hartree-Fock"},
            {"id": 2, "name": "Moller-Plesset (MP2)"},
            {"id": 3, "name": "Density Functional Theory (DFT)"},
        ]

        available_methods_response = get_all_available_methods()

        available_methods_as_dict = [
            {"id": item.id, "name": item.name} for item in available_methods_response
        ]

        self.assertEqual(available_methods_as_dict, available_methods)
        
    def test_get_available_solvent_effects(self):
        available_solvent_effects = [
            {"id": 1, "name": "Water"},
            {"id": 2, "name": "Acetonitrile"},
            {"id": 3, "name": "Cyclohexane"},
            {"id": 4, "name": "Acetone"},
            {"id": 5, "name": "Methanol"},
            {"id": 6, "name": "MethylCyclohexane"},
            {"id": 7, "name": "DiEthylEther"},
            {"id": 8, "name": "Tetrahydrofuran"},
            {"id": 9, "name": "0-Dichlorobenzene"},
            {"id": 10, "name": "Benzene"},
            {"id": 11, "name": "DiButylether"},
        ]

        available_solvent_effects_response = get_all_available_solvent_effects()

        available_solvent_effects_as_dict = [
            {"id": item.id, "name": item.name} for item in available_solvent_effects_response
        ]

        self.assertEqual(available_solvent_effects_as_dict, available_solvent_effects)


if __name__ == "__main__":
    unittest.main()
