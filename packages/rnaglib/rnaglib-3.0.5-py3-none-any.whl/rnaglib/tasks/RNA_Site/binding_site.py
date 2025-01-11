from networkx import (
    set_node_attributes,
)  # check whether needed after rna-fm integration

from rnaglib.data_loading.create_dataset import (
    annotator_add_embeddings,
    nt_filter_split_chains,
)  # check whether needed after rna-fm integration
import os

from rnaglib.data_loading import RNADataset
from rnaglib.transforms import FeaturesComputer
from rnaglib.splitters import SPLITTING_VARS, default_splitter_tr60_tr18, RandomSplitter
from rnaglib.tasks import ResidueClassificationTask
from rnaglib.encoders import BoolEncoder
from rnaglib.transforms import ResidueAttributeFilter
from rnaglib.transforms import PDBIDNameTransform, ChainNameTransform
from rnaglib.transforms import BindingSiteAnnotator
from rnaglib.transforms import ChainFilter, ComposeFilters


class BenchmarkBindingSite(ResidueClassificationTask):
    target_var = "binding_site"
    input_var = "nt_code"

    def __init__(self, root, splitter=None, **kwargs):
        super().__init__(root=root, splitter=splitter, **kwargs)

    @property
    def default_splitter(self):
        if self.debug:
            return RandomSplitter()
        else:
            return default_splitter_tr60_tr18()

    def process(self) -> RNADataset:
        # Define your transforms
        chain_filter = ChainFilter(SPLITTING_VARS["PDB_TO_CHAIN_TR60_TE18"])
        self.filters_list.append(chain_filter)
        
        rna_filter = ComposeFilters(self.filters_list)
        bs_annotator = BindingSiteAnnotator()
        namer = ChainNameTransform()

        dataset = RNADataset(
            debug=self.debug,
            in_memory=self.in_memory,
            redundancy="all",
            rna_id_subset=SPLITTING_VARS["PDB_TO_CHAIN_TR60_TE18"].keys(),
        )

        # Run through database, applying our filters
        all_rnas = []
        os.makedirs(self.dataset_path, exist_ok=True)
        for rna in dataset:
            if rna_filter.forward(rna):
                rna = bs_annotator(rna)
                rna = namer(rna)['rna']
                self.add_rna_to_building_list(all_rnas=all_rnas, rna=rna)
        dataset = self.create_dataset_from_list(all_rnas)
        return dataset

    def get_task_vars(self) -> FeaturesComputer:
        return FeaturesComputer(
            nt_features=self.input_var,
            nt_targets=self.target_var,
            custom_encoders={self.target_var: BoolEncoder()},
        )


class BindingSite(ResidueClassificationTask):
    target_var = "binding_small-molecule"
    input_var = "nt_code"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process(self) -> RNADataset:
        # Define your transforms
        attribute_filter = ResidueAttributeFilter(attribute=self.target_var, value_checker=lambda val: val is not None)
        self.filters_list.append(attribute_filter)

        rna_filter = ComposeFilters(self.filters_list)
        add_name = PDBIDNameTransform()

        # Run through database, applying our filters
        dataset = RNADataset(debug=self.debug, in_memory=self.in_memory)
        all_rnas = []
        os.makedirs(self.dataset_path, exist_ok=True)
        for rna in dataset:
            if rna_filter.forward(rna):
                rna = add_name(rna)["rna"]
                self.add_rna_to_building_list(all_rnas=all_rnas, rna=rna)
        dataset = self.create_dataset_from_list(all_rnas)
        return dataset

    def get_task_vars(self) -> FeaturesComputer:
        return FeaturesComputer(nt_features=self.input_var, nt_targets=self.target_var)
