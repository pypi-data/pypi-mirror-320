import copy
import unittest

import aspecd.processing
import numpy as np
import scipy
from numpy import testing

import nmraspecds.dataset
import nmraspecds.metadata
import nmraspecds.analysis
from nmraspecds import processing


class TestExternalReferencing(unittest.TestCase):
    def setUp(self):
        self.referencing = processing.ExternalReferencing()
        self.dataset = nmraspecds.dataset.ExperimentalDataset()
        self.data = scipy.signal.windows.gaussian(2048, std=2)
        self.axis = np.linspace(0, 30, num=2048)

    def _import_dataset(self):
        importer = nmraspecds.io.BrukerImporter()
        importer.source = "testdata/Adamantane/1"
        self.dataset.import_from(importer)

    def test_instantiate_class(self):
        pass

    def test_axis_gets_changed(self):
        self.dataset.data.data = self.data
        self.dataset.data.axes[0].values = self.axis
        self.dataset.data.axes[0].unit = "ppm"
        self.referencing.parameters["offset"] = 520
        nucleus = nmraspecds.metadata.Nucleus()
        nucleus.base_frequency.from_string("400 MHz")
        self.dataset.metadata.experiment.add_nucleus(nucleus)
        self.dataset.metadata.experiment.spectrometer_frequency.from_string(
            "400.0000 MHz"
        )
        axis_before = copy.deepcopy(self.dataset.data.axes[0].values)
        self.dataset.process(self.referencing)
        axis_after = self.dataset.data.axes[0].values
        testing.assert_allclose(
            axis_before - 520 / 400, axis_after, rtol=1e-4
        )

    def test_new_frequency_is_written(self):
        self.dataset.data.data = self.data
        self.dataset.data.axes[0].values = self.axis
        self.dataset.data.axes[0].unit = "ppm"
        self.dataset.metadata.experiment.spectrometer_frequency.from_string(
            "400.00000 MHz"
        )
        nucleus = nmraspecds.metadata.Nucleus()
        nucleus.base_frequency.from_string("400 MHz")
        self.dataset.metadata.experiment.add_nucleus(nucleus)
        self.referencing.parameters["offset"] = 500
        spectrometer_frequency_before = copy.deepcopy(
            self.dataset.metadata.experiment.spectrometer_frequency.value
        )
        self.dataset.process(self.referencing)
        spectrometer_frequency_after = (
            self.dataset.metadata.experiment.spectrometer_frequency.value
        )
        self.assertNotEqual(
            spectrometer_frequency_before, spectrometer_frequency_after
        )
        self.assertGreater(
            spectrometer_frequency_after, spectrometer_frequency_before
        )

    def test_without_offset_raises(self):
        self.dataset.data.data = self.data
        self.dataset.data.axes[0].values = self.axis
        self.dataset.data.axes[0].unit = "ppm"
        with self.assertRaises(ValueError):
            self.dataset.process(self.referencing)

    def test_with_dict_from_analysis_is_ok(self):
        self._import_dataset()
        analysis = nmraspecds.analysis.ChemicalShiftCalibration()
        analysis.parameters["return_type"] = "dict"
        analysis.parameters["standard"] = "adamantane"
        analysis_result = self.dataset.analyse(analysis)
        axis_before = copy.deepcopy(self.dataset.data.axes[0].values)
        self.referencing.parameters["offset"] = analysis_result.result
        self.dataset.process(self.referencing)
        axis_after = self.dataset.data.axes[0].values
        self.assertNotEqual(axis_before[0], axis_after[0])

    def test_different_offset_nucleus_is_recalculated(self):
        self._import_dataset()
        analysis_data = nmraspecds.dataset.ExperimentalDataset()
        importer = nmraspecds.io.BrukerImporter()
        importer.source = "testdata/Adamantane/2"
        analysis_data.import_from(importer)
        analysis = nmraspecds.analysis.ChemicalShiftCalibration()
        analysis.parameters["return_type"] = "dict"
        analysis.parameters["standard"] = "adamantane"
        analysis_result = analysis_data.analyse(analysis)
        axis_before = copy.deepcopy(self.dataset.data.axes[0].values)
        self.referencing.parameters["offset"] = analysis_result.result
        self.dataset.process(self.referencing)
        axis_after = self.dataset.data.axes[0].values
        self.assertNotEqual(axis_before[0], axis_after[0])

    def test_no_nucleus_in_dataset_issues_warning(self):
        self.dataset.data.data = self.data
        self.dataset.data.axes[0].values = self.axis
        self.dataset.data.axes[0].unit = "ppm"
        nucleus = nmraspecds.metadata.Nucleus()
        nucleus.base_frequency.from_string("400 MHz")
        self.dataset.metadata.experiment.add_nucleus(nucleus)
        self.referencing.parameters["offset"] = 3
        with self.assertLogs(__package__, level="WARNING"):
            self.dataset.process(self.referencing)

    def test_correct_delta_with_different_value_pairs(self):
        target_offsets = (-800, 400, 400)
        current_offsets = (200, 400, -200)
        deltas = (-1000, 0, 600)
        self.dataset.data.data = self.data
        self.dataset.data.axes[0].values = self.axis
        self.dataset.data.axes[0].unit = "ppm"
        nucleus = nmraspecds.metadata.Nucleus()
        nucleus.base_frequency.from_string("400 MHz")
        nucleus.offset_hz.from_string("-20000 Hz")
        self.dataset.metadata.experiment.add_nucleus(nucleus)
        for nr, delta in enumerate(deltas):
            with self.subTest(delta=delta):
                self.referencing.parameters["offset"] = target_offsets[nr]
                self.dataset.metadata.experiment.spectrometer_frequency.value = (
                    self.dataset.metadata.experiment.nuclei[
                        0
                    ].base_frequency.value
                    + current_offsets[nr] * 1e-6
                )
                referencing = self.dataset.process(self.referencing)
                self.assertAlmostEqual(delta, referencing._delta, 7)

    def test_with_real_parameters_offset_zero(self):
        """Original data: 230821/Adamantane_Ref_4mm and
        230821_sa105/2/pdata/1"""
        self.dataset.data.data = self.data
        self.dataset.data.axes[0].values = np.linspace(-387.3, 383.7, num=65)
        self.dataset.data.axes[0].unit = "ppm"
        nucleus = nmraspecds.metadata.Nucleus()
        nucleus.base_frequency.from_string("162.1226880 MHz")
        nucleus.type = "31P"
        self.dataset.metadata.experiment.add_nucleus(nucleus)
        self.dataset.metadata.experiment.spectrometer_frequency.from_string(
            "162.1146880 MHz"
        )  # offset: -8000 Hz
        self.referencing.parameters["offset"] = {
            "offset": -182.5,
            "nucleus": "13C",
        }
        referencing = self.dataset.process(self.referencing)
        self.assertAlmostEqual(-294, referencing._offset, -1)
        self.assertAlmostEqual(7706, referencing._delta, 0)

    def test_with_real_parameters_offset_nonzero(self):
        """Original data: 221028_AlCl3/2"""
        self.dataset.data.data = self.data
        self.dataset.data.axes[0].values = np.linspace(
            -302.215, 196.82411, num=2048
        )
        self.dataset.data.axes[0].unit = "ppm"
        nucleus = nmraspecds.metadata.Nucleus()
        nucleus.base_frequency.from_string("104.3585990 MHz")
        nucleus.offset_hz.from_string("1500.00 Hz")
        nucleus.type = "27Al"
        self.dataset.metadata.experiment.add_nucleus(nucleus)
        self.dataset.metadata.experiment.spectrometer_frequency.from_string(
            "104.3655990 MHz"
        )
        self.referencing.parameters["offset"] = {
            "offset": -48.38,
            "nucleus": "27Al",
        }
        referencing = self.dataset.process(self.referencing)
        self.assertAlmostEqual(-48.38, referencing._offset, -1)
        self.assertAlmostEqual(-7048.38, referencing._delta, -1)
        self.assertAlmostEqual(
            104.3585504,
            self.dataset.metadata.experiment.spectrometer_frequency.value,
            2,
        )
        self.assertAlmostEqual(
            264.32587, max(self.dataset.data.axes[0].values), -2
        )


class TestNormalisation(unittest.TestCase):
    def setUp(self):
        self.normalisation = processing.Normalisation()

    def test_instantiate_class(self):
        pass

    def test_normalises_to_number_of_scans(self):
        dataset = nmraspecds.dataset.ExperimentalDataset()
        dataset.data.data = np.asarray([12.0])
        dataset.metadata.experiment.runs = 8
        self.normalisation.parameters["kind"] = "scan_number"
        dataset.process(self.normalisation)
        self.assertEqual(1.5, dataset.data.data[0])

    def test_with_kind_maximum_processes_with_aspecd(self):
        dataset = nmraspecds.dataset.ExperimentalDataset()
        dataset.data.data = np.asarray([12.0])
        dataset.metadata.experiment.runs = 15
        self.normalisation.parameters["kind"] = "maximum"
        dataset.process(self.normalisation)
        self.assertEqual(1, max(dataset.data.data))
