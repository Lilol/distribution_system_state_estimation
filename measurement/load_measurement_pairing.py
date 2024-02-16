import logging
from collections import defaultdict
from math import isnan
from os.path import join
from random import randint, choices

import pandas
from pandas.core.series import Series
from scipy.io import loadmat

import utility.configuration as configuration
from measurement.definitions import BasicScenario, SmartMeterScenario
from utility.collect_load_consumptions import collect_load_consumptions


class TimeSeriesIdentifier:
    def __init__(self, cluster_name, series_idx):
        self.cluster_name = cluster_name
        self.series_idx = series_idx

    def valid(self):
        # return self.cluster_name is not None and self.series_idx is not None
        return self.series_idx is not None and not pandas.isna(self.series_idx)


class LoadMeasurementPairing:
    def __init__(self, time_series_identifier, controlled_time_series_identifier, pv_power_kwp):
        if isinstance(time_series_identifier, list):
            k = 99
        self.residential_time_series_identifier = time_series_identifier
        self.controlled_time_series_identifier = controlled_time_series_identifier
        self.pv_power_kwp = pv_power_kwp


class LoadMeasurementPairingContainer:
    def __init__(self):
        self.pairings = defaultdict(list)

    def __getitem__(self, items):
        for item in items:
            if self.pairings.get(item) is None:
                logging.getLogger("load_measurement_pairing").warning("Load '" + str(item) +
                                                                      "' is missing from the SAP file")
        p = [pairing for item in items if self.pairings.get(item) is not None for pairing in self.pairings.get(item)]
        return p

    def add_pairing(self, load_id, time_series_identifier, controlled_time_series_identifier, pv_power_kwp):
        self.pairings[load_id].append(LoadMeasurementPairing(time_series_identifier,
                                                             controlled_time_series_identifier,
                                                             pv_power_kwp))


class MeasurementClusterContainer:
    class ClusterBoundaries:
        def __init__(self, lower_boundary, upper_boundary):
            self.lower_boundary = lower_boundary
            self.upper_boundary = upper_boundary

    def __init__(self):
        self.__path = configuration.config.get("input", "measurement_clusters")
        self.__cluster_names = self.__set_cluster_names()
        self.__cluster_boundaries = self.__set_cluster_boundaries()
        self.__cluster_sizes = self.__set_cluster_sizes()

    def __set_cluster_names(self):
        data = loadmat(join(self.__path, f"measurements_week_1.mat"), squeeze_me=False, struct_as_record=False,
                       simplify_cells=True)["week"]["residential"]
        return list(data[list(data)[0]].keys())

    def __set_cluster_sizes(self):
        """Returns the number of measurement series each cluster contains for both residential and controlled
        measurement types.
        """
        data = loadmat(join(self.__path, f"measurements_week_1.mat"), squeeze_me=False, struct_as_record=False,
                       simplify_cells=True)["week"]
        controlled_meas = data["controlled"]
        controlled_measurement_size = controlled_meas[list(controlled_meas)[0]].shape[1]
        residential_meas = data["residential"][list(data["residential"])[0]]
        residential_measurement_size = {name: residential_meas[name].shape[1] for name in self.__cluster_names}
        return residential_measurement_size, controlled_measurement_size

    def __set_cluster_boundaries(self):
        """Returns the upper and lower boundaries for each cluster as a dict from cluster names to ClusterBoundaries
        objects.
        """
        mat_input_data_cluster_boundaries = loadmat(join(self.__path,
                                                         "cluster_boundaries.mat"), squeeze_me=False,
                                                    struct_as_record=False, simplify_cells=True)["CLUSTER_BOUNDARIES"]

        return {name: self.ClusterBoundaries(mat_input_data_cluster_boundaries[i][0],
                                             mat_input_data_cluster_boundaries[i][1]) for i, name in
                enumerate(self.__cluster_names)}

    def get_cluster_boundaries(self):
        return self.__cluster_boundaries

    def get_cluster_sizes(self):
        return self.__cluster_sizes


class LoadMeasurementPairer:
    def __init__(self):
        self.clusters = MeasurementClusterContainer()

    def add_load_measurement_pairing_to_network(self, net):
        scenario = configuration.config.get_scenario()
        add_measurement_pairing = (
                type(scenario) in (BasicScenario, SmartMeterScenario) and scenario != BasicScenario.PV)
        if not add_measurement_pairing:
            return net

        cluster_boundaries = self.clusters.get_cluster_boundaries()
        residential_measurement_size, controlled_measurement_size = self.clusters.get_cluster_sizes()
        load_consumptions = collect_load_consumptions()

        # Select random indices for controlled consumptions
        controlled_id_mapping = self.__create_id_mapping(controlled_measurement_size, load_consumptions)

        net.load_measurement_pairing = LoadMeasurementPairingContainer()
        # Use set to filter duplicates (duplicates are handled)
        assert (not load_consumptions.empty)
        for load_id in set(load_consumptions.index):
            residential_ids = self.__get_random_index_from_cluster(load_consumptions.nappali_fogy[load_id],
                                                                   cluster_boundaries, residential_measurement_size)

            controlled_ids = controlled_id_mapping.ids[load_id] if load_id in controlled_id_mapping else pandas.NA
            self.__add_pairings(net.load_measurement_pairing, load_id, controlled_ids, residential_ids,
                                load_consumptions.teljesitmeny[load_id])
        return net

    @staticmethod
    def __create_id_mapping(measurement_size, load_consumptions):
        load_ids = load_consumptions.index
        load_size = len(load_ids)

        mapping = pandas.DataFrame(choices(range(0, measurement_size), k=load_size), columns=['ids'], index=load_ids)
        # For zero and Nan values, the index is set to Nan
        mapping = mapping.drop(labels=mapping[load_consumptions.vezerelt_fogy.isna()].index, axis=0)
        mapping = mapping.drop(labels=mapping[load_consumptions.vezerelt_fogy == 0].index, axis=0)
        return mapping

    @staticmethod
    def __get_random_index_from_cluster(consumption, cluster_boundaries, residential_measurement_size):
        """ Returns the index of a randomly selected measurement from the appropriate cluster. The cluster is selected
        based on the yearly consumption data of the load. """
        if isinstance(consumption, Series):
            consumption_series = [LoadMeasurementPairer.__get_random_index_from_cluster(val, cluster_boundaries,
                                                                                        residential_measurement_size)
                                  for val in
                                  consumption.values]
            return consumption_series
        if isnan(consumption):
            return TimeSeriesIdentifier(None, None)
        for cluster in cluster_boundaries.keys():
            if cluster_boundaries[cluster].lower_boundary <= consumption < cluster_boundaries[cluster].upper_boundary:
                i = randint(0, residential_measurement_size[cluster] - 1)
                logging.getLogger("load_measurement_pairing").debug(f"Randomly generated measurement id '{str(i)}'")
                return TimeSeriesIdentifier(cluster, i)
        raise ValueError(f"No cluster found for consumption '{consumption}'")

    @staticmethod
    def __add_pairings(load_measurement_pairing, load_id, controlled_ids, residential_ids, pv_power):
        # Randomly assign residential and controlled measurements to a load specified by its load_id
        # Recursive function, if a load_id contains two or more measurement points, assigns a random measurement series
        # to all of them
        if isinstance(controlled_ids, Series):
            assert len(controlled_ids) == len(residential_ids)
            for c_id, r_id, pv in zip(controlled_ids, residential_ids, pv_power):
                load_measurement_pairing.add_pairing(load_id, r_id, TimeSeriesIdentifier(None, c_id), pv)
        else:
            load_measurement_pairing.add_pairing(load_id, residential_ids, TimeSeriesIdentifier(None, controlled_ids),
                                                 pv_power)
