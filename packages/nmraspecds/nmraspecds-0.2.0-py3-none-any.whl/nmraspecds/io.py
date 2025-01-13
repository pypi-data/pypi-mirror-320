"""
io module of the nmraspecds package.
"""
import glob
import os.path
import re

import aspecd.io
import linecache

import matplotlib.pyplot as plt
import nmrglue
import numpy as np

import nmraspecds.metadata
import nmraspecds.dataset
import nmraspecds.processing


class UnsupportedDataFormatError(Exception):
    """Exception raised when data format is not supported.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=""):
        super().__init__(message)
        self.message = message


class DatasetImporterFactory(aspecd.io.DatasetImporterFactory):
    """
    Factory to return the appropriate importer for the dataset.

    The format is currently determined from the type of data. Abbreviations
    for the sample names can be used, i.e. ``42`` instead of ``20240816_sa42``.

    Raises
    ------
    UnsupportedDataFormatError
        Raised if a format is set but does not match any of the supported
        formats

    """

    def _get_importer(self):
        # Check characteristic for fitted data.
        if self.source.endswith(".asc") or os.path.isfile(
            self.source + ".asc"
        ):
            return FittingImporter(source=self.source)
        # TODO: Maybe improve process of detecting abbreviated sample names.
        # Source path is completed if the sample name was abbreviated (path
        # does not exist).
        if not os.path.exists(self.source):
            try:
                path, expno = os.path.split(self.source)
                basepath, sample = os.path.split(path)
                name = glob.glob(f"{basepath}/*{str(sample)}*")[0]
                self.source = os.path.join(name, expno)
            except IndexError:
                raise FileNotFoundError
        # Standard behaviour for Bruker data.
        if os.path.isdir(self.source):
            return BrukerImporter(source=self.source)
        else:
            raise UnsupportedDataFormatError


class BrukerImporter(aspecd.io.DatasetImporter):
    """
    Import data from Bruker format.

    Data acquired with Bruker spectrometers are mostly processed in TopSpin
    Software. If nothing else is given, processed data (processing no. 1) is
    imported together with metadata. The import of data and metadata is done
    using nmrglue and then mapped to the dataset.


    Attributes
    ----------
    parameters : :class:`dict`
        Parameters controlling the import

        type : : class:`str`
            type of data, raw or processed.

            Default: pdata

        processing_number : :class:`str`
            Processing number of the desired dataset.

            Default: 1

    Raises
    ------
    FileNotFound
        Raised if source file was not found.

    Examples
    --------
    It is always nice to give some examples how to use the class. Best to do
    that with code examples:

    .. code-block::

        datasets:
          - source: dataset
            id: data
            label: My Data


    .. versionchanged:: 0.2
        Type of nucleus is added to axis quantity
    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self.parameters["type"] = "proc"
        self.parameters["processing_number"] = 1
        self._parameters = None
        self._raw_parameters = None
        self._data = None
        self._dimension = None

    def _import(self):
        self._check_for_type()
        if not os.path.exists(self.source):
            raise FileNotFoundError
        self._read_data()
        self._create_axes()
        self._get_spectrometer_frequency()
        self._add_nuclei()
        self._add_axis_metadata()
        self._import_metadata()

    def _import_metadata(self):
        self.dataset.metadata.experiment.runs = self._parameters["acqus"][
            "NS"
        ]
        self.dataset.metadata.experiment.delays = self._parameters["acqus"][
            "D"
        ]
        self.dataset.metadata.experiment.loops = self._parameters["acqus"][
            "L"
        ]

    def _add_nuclei(self):
        nuclei = dict()
        for key, value in self._parameters["acqus"].items():
            if key.startswith("NUC") and value != "off" and value != 0:
                nuclei[key] = value
        for key in reversed(sorted(nuclei.keys())):
            self._add_nucleus(key)

    def _get_spectrometer_frequency(self):
        self.dataset.metadata.experiment.spectrometer_frequency.value = (
            self._parameters
        )["procs"]["SF"]

    def _create_axes(self):
        unified_dict = nmrglue.bruker.guess_udic(
            self._parameters, self._data, strip_fake=False
        )
        for dim in np.arange(0, unified_dict["ndim"]):
            # unified_dict = self._do_referencing_manually(unified_dict, dim)
            uc = nmrglue.convert.fileiobase.uc_from_udic(unified_dict, dim)
            ppmsc = uc.ppm_scale()
            self.dataset.data.axes[dim].values = ppmsc

    def _do_referencing_manually(self, unified_dict, dim):
        # TODO: Diese Referenzierung ist noch sehr komisch und funktioniert
        #  nicht richtig. Eigentlich müsste man an die Daten aus proc2s ran,
        #  aber die werden nicht eingelesen?
        # nmrglue appears to stumble with referencing for data produced using newer versions of TopSpin
        # These two lines set the referencing manually by referring to the processed data dictionary
        print(
            "Carrier",
            unified_dict[0]["car"],
            unified_dict[1]["car"],
        )
        # unified_dict[dim]["obs"] = self._parameters['procs']['SF']
        unified_dict[dim]["car"] = (
            self._raw_parameters["acqus"]["SFO1"] - unified_dict[dim]["obs"]
        ) * 1e6
        print(
            "Carrier2",
            unified_dict[dim]["car"],
            unified_dict[dim]["car"] / unified_dict[dim]["obs"],
        )
        return unified_dict

    def _add_axis_metadata(self):
        for nr, nucleus in enumerate(self.dataset.metadata.experiment.nuclei):
            if nr > self._dimension:
                pass
            match = re.match(r"(\d+)([A-Za-z]+)", nucleus.type)
            number = match.group(1)
            letters = match.group(2)
            nucleus = f"{{{number}}}{letters}"
            self.dataset.data.axes[nr].unit = "ppm"
            self.dataset.data.axes[nr].quantity = f"^{nucleus} chemical shift"
        self.dataset.data.axes[-1].quantity = "intensity"

    def _read_data(self):
        if "pdata" in self.source:
            self._parameters, self._data = nmrglue.bruker.read_pdata(
                self.source
            )
            self._raw_parameters, _ = nmrglue.bruker.read_pdata(self.source)
        else:
            self._parameters, self._data = nmrglue.bruker.read(self.source)
        self._dimension = self._data.ndim
        if self._dimension == 2:
            self._data = self._data
        self.dataset.data.data = self._data

    def _check_for_type(self):
        if (
            "type" in self.parameters
            and self.parameters["type"].startswith("proc")
            and "pdata" not in self.source
        ):
            self.source = os.path.join(
                self.source,
                "pdata",
                str(self.parameters["processing_number"]),
            )

    def _add_nucleus(self, nuc=""):
        nr = nuc[-1]
        nucleus = nmraspecds.metadata.Nucleus()
        nucleus.type = self._parameters["acqus"][nuc]
        nucleus.base_frequency.value = self._parameters["acqus"][f"BF{nr}"]
        nucleus.base_frequency.unit = "MHz"
        nucleus.offset_hz.value = float(self._parameters["acqus"][f"O{nr}"])
        nucleus.offset_hz.unit = "Hz"
        self.dataset.metadata.experiment.add_nucleus(nucleus)


class ScreamImporter(aspecd.io.DatasetImporter):
    """
    Import scream data from a pseudo-2D dataset after processing.

    .. note::
        Importer not finished yet.

    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self.parameters["number_of_experiments"] = 1
        self._tmp_data = None
        self._tmp_t_buildup = None
        self._datasets = []

    def _import(self):
        base_path, last_element = os.path.split(self.source)
        for count, variable_element in enumerate(
            np.arange(
                int(last_element),
                int(last_element) + self.parameters["number_of_experiments"],
            )
        ):
            self.source = os.path.join(
                base_path, str(variable_element), "pdata", "103"
            )
            tmp_dataset = nmraspecds.dataset.ExperimentalDataset()
            tmp_dataset.import_from(BrukerImporter(self.source))
            self._datasets.append(tmp_dataset)

        for count, single_dataset in enumerate(self._datasets):
            if self._tmp_data is None:
                self._tmp_data = np.ndarray(
                    (
                        len(self._datasets[0].data.data),
                        len(self._datasets),
                    )
                )
            normalisation = nmraspecds.processing.Normalisation()
            normalisation.parameters["kind"] = "scan_number"
            single_dataset.process(normalisation)
            self._tmp_data[:, count] = single_dataset.data.data
            if self._tmp_t_buildup is None:
                self._tmp_t_buildup = np.ndarray((len(self._datasets),))
            self._tmp_t_buildup[count] = (
                single_dataset.metadata.experiment.loops[20]
                * single_dataset.metadata.experiment.delays[20]
            )

        self.dataset.data.data = self._tmp_data
        self._create_axes()

    def _create_axes(self):
        self.dataset.data.axes[1].values = self._tmp_t_buildup
        self.dataset.data.axes[1].unit = "s"
        self.dataset.data.axes[1].quantity = "buildup time"
        self.dataset.data.axes[2].quantity = "intensity"


class FittingImporter(aspecd.io.DatasetImporter):
    """
    Import data from DMFit with experimental and simulated data.

    Data needs to be exported to ascii-format using the "Export spec,
    model with all lines" command.

    The file is composed with three comment lines:
      * title of the dataset
      * frequency
      * description of the columns.

    .. code-block::

        31P-spectrum MAS 12 kHz
        ##freq 283.417
        ##col_ Hz	Spectrum	Model	Line#1	Line#2

    The data then follows in the columns. As only the frequency is available as
    metadata, most NMR specific processing steps cannot be performed. The
    data can then be plotted with the special plotter
    :class:`nmraspecds.plotting.FittingPlotter2D` which provides a color
    scheme that explains the single peaks.


    Attributes
    ----------
    attr : :class:`None`
        Short description


    Examples
    --------
    The import of the dataset is performed as usual. Together with a plot in
    the simplest case, the recipe looks as follows:

    .. code-block:: yaml

        datasets:
          - source: fitting-data
            id: fit-data
            label: My Fitted Data
        tasks:
          - kind: singleplot
            type: FittingPlotter2D
            properties:
              filename: output.pdf

    """

    def __init__(self, source=None):
        super().__init__(source=source)

    def _import(self):
        if self.source:
            if not self.source.endswith(".asc"):
                self.source += ".asc"

        data = np.loadtxt(self.source, skiprows=3)
        # data = self._sort_data_maximum(data)
        self.dataset.data.data = data[:, 1:]
        frequency = float(linecache.getline(self.source, 2).strip("##freq "))
        self.dataset.data.axes[0].values = data[:, 0] / frequency
        self.dataset.data.axes[0].unit = "ppm"
        self.dataset.data.axes[0].quantity = "chemical shift"
        self.dataset.data.axes[1].quantity = "spectrum No"
        self.dataset.data.axes[2].quantity = "intensity"
        self.dataset.metadata.experiment.spectrometer_frequency.value = (
            frequency
        )
        self.dataset.metadata.experiment.spectrometer_frequency.unit = "MHz"

    def _sort_data_maximum(self, data):
        axis = data[:, 0]
        print(data.shape)
        data_small = data[:, 2:]
        max_ = np.argmax(data_small, axis=1).astype(int)
        sorted_max = np.argsort(max_)[::-1]
        print(sorted_max)
        data[:, 2:] = data_small[sorted_max]
        print(data.shape)
        return data
