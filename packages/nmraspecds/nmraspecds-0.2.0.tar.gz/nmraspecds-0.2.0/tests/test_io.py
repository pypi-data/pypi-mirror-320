import os
import unittest

import matplotlib.pyplot as plt
import numpy as np

import nmraspecds.dataset
import nmraspecds.processing
from nmraspecds import io
from numpy import testing
import aspecd.exceptions


class TestDatasetImporterFactory(unittest.TestCase):
    def setUp(self):
        self.dataset_importer_factory = io.DatasetImporterFactory()

    def test_instantiate_class(self):
        pass

    def test_returns_bruker_importer(self):
        source = "testdata/Adamantane/1"
        importer_factory = (
            nmraspecds.dataset.DatasetFactory().importer_factory
        )
        importer = importer_factory.get_importer(source=source)
        self.assertIsInstance(importer, io.BrukerImporter)

    def test_returned_importer_has_source_set(self):
        source = "testdata/Adamantane/1"
        importer_factory = (
            nmraspecds.dataset.DatasetFactory().importer_factory
        )
        importer = importer_factory.get_importer(source=source)
        self.assertIn(source, importer.source)

    def test_returns_fitting_importer(self):
        source = "testdata/fitting-data.asc"
        importer_factory = (
            nmraspecds.dataset.DatasetFactory().importer_factory
        )
        importer = importer_factory.get_importer(source=source)
        self.assertIsInstance(importer, io.FittingImporter)

    def test_gets_name_from_sampleno(self):
        source = "testdata/51/1"
        importer_factory = (
            nmraspecds.dataset.DatasetFactory().importer_factory
        )
        importer = importer_factory.get_importer(source=source)
        self.assertTrue(importer.source.endswith("/20240816_sa51/1"))

    def test_source_without_asc_extension_returns_fitting_importer(self):
        source = "testdata/fitting-data"
        importer_factory = (
            nmraspecds.dataset.DatasetFactory().importer_factory
        )
        importer = importer_factory.get_importer(source=source)
        self.assertIsInstance(importer, nmraspecds.io.FittingImporter)

    def test_raises_with_nonexisting_file_name(self):
        source = "testdata/asdf/1"
        importer_factory = (
            nmraspecds.dataset.DatasetFactory().importer_factory
        )
        with self.assertRaises(FileNotFoundError):
            importer_factory.get_importer(source=source)

    def test_raises_with_not_recognized_file_name(self):
        source = "test_io.py"
        importer_factory = (
            nmraspecds.dataset.DatasetFactory().importer_factory
        )
        with self.assertRaises(io.UnsupportedDataFormatError):
            importer_factory.get_importer(source=source)


class TestBrukerImporter(unittest.TestCase):
    def setUp(self):
        self.bruker_importer = io.BrukerImporter()
        self.dataset = nmraspecds.dataset.ExperimentalDataset()

    def is_fid(self, data):
        #  Test if index of global max or min is within the first 15% of the
        #  data -> FID
        index_max = np.argmax(self.dataset.data.data)
        index_min = np.argmin(self.dataset.data.data)
        index = min(index_min, index_max)
        return index < 0.15 * len(self.dataset.data.data)

    def is_processed(self, data):
        #  Test if index  global max or min is between 10 and 90%  of the
        #  data -> processed data
        if abs(np.amax(self.dataset.data.data)) > abs(
            np.amin(self.dataset.data.data)
        ):
            index = np.argmax(self.dataset.data.data)
        else:
            index = np.argmin(self.dataset.data.data)
        len_data = len(self.dataset.data.data)
        return 0.1 * len_data < index < 0.9 * len_data

    def test_instantiate_class(self):
        pass

    def test_import_data_to_dataset(self):
        self.bruker_importer.source = "testdata/Adamantane/1"
        self.bruker_importer.parameters["type"] = "fid"
        self.dataset.import_from(self.bruker_importer)
        self.assertTrue(self.dataset.data.data.any())

    def test_import_with_wrong_filename_raises(self):
        self.bruker_importer.source = "testdata/foo/1"
        with self.assertRaises(FileNotFoundError):
            self.dataset.import_from(self.bruker_importer)

    def test_data_is_fid(self):
        self.bruker_importer.source = "testdata/Adamantane/1"
        self.bruker_importer.parameters["type"] = "fid"
        self.dataset.import_from(self.bruker_importer)
        self.assertTrue(self.is_fid(self.dataset.data.data))

    def test_data_is_not_processed_data(self):
        self.bruker_importer.source = "testdata/Adamantane/1"
        self.bruker_importer.parameters["type"] = "fid"
        self.dataset.import_from(self.bruker_importer)
        self.assertFalse(self.is_processed(self.dataset.data.data))

    @unittest.skip  # Time axis not present yet
    def test_import_time_axis(self):
        self.bruker_importer.source = "testdata/Adamantane/1"
        self.dataset.import_from(self.bruker_importer)
        self.assertLess(self.dataset.data.axes[0].values[-1], 2)

    def test_import_processed_data_to_dataset(self):
        self.bruker_importer.source = "testdata/Adamantane/1/pdata/1"
        self.dataset.import_from(self.bruker_importer)
        self.assertTrue(self.is_processed(self.dataset.data.data))

    def test_processed_data_is_not_fid(self):
        self.bruker_importer.source = "testdata/Adamantane/1/pdata/1"
        self.bruker_importer.parameters["type"] = "fid"
        self.dataset.import_from(self.bruker_importer)
        self.assertFalse(self.is_fid(self.dataset.data.data))

    def test_with_importer_parameter_imports_processed_data(self):
        for type_ in ("processed", "proc"):
            with self.subTest(type_=type_):
                self.bruker_importer.source = "testdata/Adamantane/1"
                self.bruker_importer.parameters["type"] = type_
                self.dataset.import_from(self.bruker_importer)
                self.assertTrue(self.is_processed(self.dataset.data.data))
                self.assertFalse(self.is_fid(self.dataset.data.data))

    def test_default_type_is_proc(self):
        self.assertEqual(self.bruker_importer.parameters["type"], "proc")

    def test_with_type_raw_imports_fid(self):
        for type_ in ("raw", "fid", "horst"):
            with self.subTest(type_=type_):
                self.dataset = nmraspecds.dataset.ExperimentalDataset()
                self.bruker_importer.source = "testdata/Adamantane/1"
                self.bruker_importer.parameters["type"] = type_
                self.dataset.import_from(self.bruker_importer)
                self.assertFalse(self.is_processed(self.dataset.data.data))
                self.assertTrue(self.is_fid(self.dataset.data.data))

    def test_proc_no_can_be_chosen(self):
        self.bruker_importer.source = "testdata/Adamantane/1"
        self.bruker_importer.parameters["processing_number"] = 2
        self.dataset.import_from(self.bruker_importer)
        self.assertTrue("pdata/2" in self.bruker_importer.source)

    def test_1d_dimension_is_set(self):
        self.bruker_importer.source = "testdata/Adamantane/2"
        self.dataset.import_from(self.bruker_importer)
        self.assertEqual(1, self.bruker_importer._dimension)

    def test_get_ppm_axis(self):
        self.bruker_importer.source = "testdata/Adamantane/1/pdata/1"
        self.dataset.import_from(self.bruker_importer)
        self.assertGreater(self.dataset.data.axes[0].values[0], 0)
        self.assertAlmostEqual(
            self.dataset.data.axes[0].values[0], 156.8483, places=4
        )

    def test_set_axis_unit(self):
        self.bruker_importer.source = "testdata/Adamantane/1/pdata/1"
        self.dataset.import_from(self.bruker_importer)
        unit = self.dataset.data.axes[0].unit
        self.assertEqual(unit, "ppm")

    def test_set_axis_quantity(self):
        self.bruker_importer.source = "testdata/Adamantane/1/pdata/1"
        self.dataset.import_from(self.bruker_importer)
        self.assertEqual(
            "^{1}H chemical shift", self.dataset.data.axes[0].quantity
        )
        self.assertEqual("intensity", self.dataset.data.axes[1].quantity)

    @unittest.skip
    def test_set_axis_quantity_1d_with_two_nuclei(self):
        self.bruker_importer.source = "testdata/Adamantane/2"
        self.dataset.import_from(self.bruker_importer)
        self.assertEqual(
            "^{13}C chemical shift", self.dataset.data.axes[0].quantity
        )
        self.assertEqual("intensity", self.dataset.data.axes[1].quantity)

    @unittest.skipIf(
        not os.path.exists("testdata/2D-data/5"), "File too " "large for git"
    )
    def test_set_2d_axis_quantities(self):
        self.bruker_importer.source = "testdata/2D-data/5"
        self.dataset.import_from(self.bruker_importer)
        self.assertEqual(
            "^{31}P chemical shift", self.dataset.data.axes[0].quantity
        )
        self.assertEqual(
            "^{1}H chemical shift", self.dataset.data.axes[1].quantity
        )
        self.assertEqual("intensity", self.dataset.data.axes[2].quantity)

    @unittest.skip
    def test_set_axis_quantity_with_13C(self):
        self.bruker_importer.source = "testdata/Adamantane/2/pdata/1"
        self.dataset.import_from(self.bruker_importer)
        self.assertEqual(
            "^{13}C chemical shift", self.dataset.data.axes[0].quantity
        )
        self.assertEqual("intensity", self.dataset.data.axes[1].quantity)

    def test_nucleus_is_in_metadata(self):
        self.bruker_importer.source = "testdata/Adamantane/1/pdata/1"
        self.dataset.import_from(self.bruker_importer)
        self.assertEqual(
            self.dataset.metadata.experiment.nuclei[0].type, "1H"
        )

    @unittest.skipIf(
        not os.path.exists("testdata/2D-data/5"), "File too " "large for git"
    )
    def test_2d_nucleus_is_in_metadata(self):
        self.bruker_importer.source = "testdata/2D-data/5"
        self.dataset.import_from(self.bruker_importer)
        self.assertEqual(
            self.dataset.metadata.experiment.nuclei[0].type, "31P"
        )
        self.assertEqual(
            self.dataset.metadata.experiment.nuclei[1].type, "1H"
        )

    def test_base_frequency_is_in_metadata(self):
        self.bruker_importer.source = "testdata/Adamantane/1/pdata/1"
        self.dataset.import_from(self.bruker_importer)
        self.assertAlmostEqual(
            self.dataset.metadata.experiment.nuclei[0].base_frequency.value,
            400.491372,
        )

    def test_base_frequency_unit_in_metadata(self):
        self.bruker_importer.source = "testdata/Adamantane/1/pdata/1"
        self.dataset.import_from(self.bruker_importer)
        self.assertEqual(
            self.dataset.metadata.experiment.nuclei[0].base_frequency.unit,
            "MHz",
        )

    def test_offset_hz_value_and_unit_in_metadata(self):
        self.bruker_importer.source = "testdata/Adamantane/1/pdata/1"
        self.dataset.import_from(self.bruker_importer)
        self.assertAlmostEqual(
            self.dataset.metadata.experiment.nuclei[0].offset_hz.value,
            5,
            places=2,
        )
        self.assertEqual(
            self.dataset.metadata.experiment.nuclei[0].offset_hz.unit, "Hz"
        )

    def test_transmitter_freq_is_different_from_base_freq(self):
        # only works because O1 was manually changed from 0 to 5 Hz in
        # acqus-file.
        self.bruker_importer.source = "testdata/Adamantane/1"
        self.dataset.import_from(self.bruker_importer)
        self.assertNotEqual(
            self.dataset.metadata.experiment.nuclei[0].base_frequency.value,
            self.dataset.metadata.experiment.nuclei[
                0
            ].transmitter_frequency.value,
        )

    def test_spectrometer_frequency_is_written(self):
        self.bruker_importer.source = "testdata/Adamantane/1"
        self.dataset.import_from(self.bruker_importer)
        self.assertAlmostEqual(
            self.dataset.metadata.experiment.spectrometer_frequency.value,
            400.4910556,
        )

    def test_nuclei_in_2nucleus_exp_are_written(self):
        self.bruker_importer.source = "testdata/Adamantane/2"
        self.dataset.import_from(self.bruker_importer)
        self.assertEqual(len(self.dataset.metadata.experiment.nuclei), 2)
        self.assertNotEqual(
            self.dataset.metadata.experiment.nuclei[1].base_frequency.value, 0
        )

    def test_scannumber_is_imported(self):
        self.bruker_importer.source = "testdata/Adamantane/2"
        self.dataset.import_from(self.bruker_importer)
        self.assertTrue(self.dataset.metadata.experiment.runs)
        self.assertIsInstance(self.dataset.metadata.experiment.runs, int)

    def test_loops_are_imported(self):
        self.bruker_importer.source = "testdata/Adamantane/2"
        self.dataset.import_from(self.bruker_importer)
        self.assertIsInstance(self.dataset.metadata.experiment.loops, list)

    def test_delays_imported(self):
        self.bruker_importer.source = "testdata/Adamantane/2"
        self.dataset.import_from(self.bruker_importer)
        self.assertIsInstance(self.dataset.metadata.experiment.delays, list)

    @unittest.skipIf(
        not os.path.exists("testdata/2D-data/5"), "File too " "large for git"
    )
    def test_import_2d_data(self):
        self.bruker_importer.source = "testdata/2D-data/5"
        self.dataset.import_from(self.bruker_importer)
        self.assertTrue(self.dataset.data.data.any())

    @unittest.skipIf(
        not os.path.exists("testdata/2D-data/5"), "File too " "large for git"
    )
    def test_2d_data_has_correct_axes(self):
        self.bruker_importer.source = "testdata/2D-data/5"
        self.dataset.import_from(self.bruker_importer)
        self.assertNotEqual(0, self.dataset.data.axes[1].values[0])
        self.assertNotEqual(1, self.dataset.data.axes[1].values[1])
        # self.assertEqual()

    @unittest.skipIf(
        not os.path.exists("testdata/2D-data/5"), "File too " "large for git"
    )
    def test_2d_dimension_is_set(self):
        self.bruker_importer.source = "testdata/2D-data/5"
        self.dataset.import_from(self.bruker_importer)
        self.assertEqual(2, self.bruker_importer._dimension)

    @unittest.skipIf(
        not os.path.exists("testdata/2D-data/5"), "File too " "large for git"
    )
    def test_2d_dataset_has_metadata(self):
        self.bruker_importer.source = "testdata/2D-data/5"
        self.dataset.import_from(self.bruker_importer)
        self.assertAlmostEqual(
            162.1190167,
            self.dataset.metadata.experiment.spectrometer_frequency.value,
            3,
        )


class TestScreamImporter(unittest.TestCase):
    def setUp(self):
        self.scream_importer = io.ScreamImporter()
        self.dataset = nmraspecds.dataset.ExperimentalDataset()

    def test_instantiate_class(self):
        pass

    def test_import_data_to_dataset(self):
        self.scream_importer.source = "testdata/Scream/22"
        self.scream_importer.parameters["number_of_experiments"] = 13
        self.dataset.import_from(self.scream_importer)
        self.assertTrue(self.dataset.data.data.any())

    def test_is_2d(self):
        self.scream_importer.source = "testdata/Scream/22"
        self.scream_importer.parameters["number_of_experiments"] = 13
        self.dataset.import_from(self.scream_importer)
        self.assertEqual(self.scream_importer._tmp_data.ndim, 2)

    def test_dataset_contains_2d_data(self):
        self.scream_importer.source = "testdata/Scream/22"
        self.scream_importer.parameters["number_of_experiments"] = 13
        self.dataset.import_from(self.scream_importer)
        self.assertEqual(self.dataset.data.data.shape, (16384, 13))

    def test_axes_have_correct_size(self):
        self.scream_importer.source = "testdata/Scream/22"
        self.scream_importer.parameters["number_of_experiments"] = 13
        self.dataset.import_from(self.scream_importer)
        self.assertEqual(len(self.dataset.data.axes[1].values), 13)

    def test_buildup_axes_exist(self):
        self.scream_importer.source = "testdata/Scream/22"
        self.scream_importer.parameters["number_of_experiments"] = 13
        self.dataset.import_from(self.scream_importer)
        testing.assert_array_equal(
            self.dataset.data.axes[1].values,
            np.array(
                [0.25, 0.5, 1, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
            ),
        )

    def test_normalisation_to_ns(self):
        source = "testdata/Scream/34/pdata/103"
        test_dataset = nmraspecds.dataset.ExperimentalDataset()
        test_dataset.import_from(nmraspecds.io.BrukerImporter(source))
        normalisation = nmraspecds.processing.Normalisation()
        normalisation.parameters["kind"] = "scan_number"
        test_dataset.process(normalisation)
        self.scream_importer.source = "testdata/Scream/22"
        self.scream_importer.parameters["number_of_experiments"] = 13
        self.dataset.import_from(self.scream_importer)
        self.assertEqual(
            test_dataset.data.data[42], self.dataset.data.data[42, -1]
        )


class TestFittingImporter(unittest.TestCase):
    def setUp(self):
        self.fitting_importer = io.FittingImporter()
        self.dataset = nmraspecds.dataset.ExperimentalDataset()
        self.fitting_importer.source = "testdata/fitting-data.asc"

    def test_instantiate_class(self):
        pass

    def test_import_data_to_dataset(self):
        self.fitting_importer.source = "testdata/fitting-data.asc"
        self.dataset.import_from(self.fitting_importer)
        self.assertTrue(self.dataset.data.data.any())

    def test_import_data_to_dataset_wo_suffix(self):
        self.fitting_importer.source = "testdata/fitting-data"
        self.dataset.import_from(self.fitting_importer)
        self.assertTrue(self.dataset.data.data.any())

    def test_data_has_correct_size(self):
        self.dataset.import_from(self.fitting_importer)
        self.assertEqual(2, self.dataset.data.data.ndim)
        self.assertEqual(4, self.dataset.data.data.shape[1])

    def test_x_axis_is_calculated(self):
        self.dataset.import_from(self.fitting_importer)
        self.assertAlmostEqual(337.30, self.dataset.data.axes[0].values[0], 2)

    def test_x_axis_has_unit(self):
        self.dataset.import_from(self.fitting_importer)
        self.assertEqual("ppm", self.dataset.data.axes[0].unit)

    def test_metadata_contains_frequency(self):
        self.dataset.import_from(self.fitting_importer)
        self.assertEqual(
            283.417,
            self.dataset.metadata.experiment.spectrometer_frequency.value,
        )
