import os

from rnaglib.data_loading import RNADataset
from rnaglib.tasks import ResidueClassificationTask
from rnaglib.transforms import FeaturesComputer
from rnaglib.transforms import ComposeFilters, RibosomalFilter, DummyFilter, ResidueAttributeFilter
from rnaglib.transforms import PDBIDNameTransform


class ProteinBindingSite(ResidueClassificationTask):
    """Residue-level task where the job is to predict a binary variable
    at each residue representing the probability that a residue belongs to
    a protein-binding interface
    """

    target_var = "protein_binding"
    input_var = "nt_code"

    def __init__(self, root, splitter=None, **kwargs):
        super().__init__(root=root, splitter=splitter, **kwargs)

    def get_task_vars(self):
        return FeaturesComputer(nt_features=self.input_var, nt_targets=self.target_var)

    def process(self):
        # build the filters
        ribo_filter = RibosomalFilter()
        non_bind_filter = ResidueAttributeFilter(attribute=self.target_var, value_checker=lambda val: val)
        self.filters_list += [ribo_filter, non_bind_filter]
        filters = ComposeFilters(self.filters_list)
        if self.debug:
            filters = DummyFilter()

        # Define your transforms
        add_name = PDBIDNameTransform()

        # Run through database, applying our filters
        dataset = RNADataset(debug=self.debug, in_memory=False)
        all_rnas = []
        os.makedirs(self.dataset_path, exist_ok=True)
        for rna in dataset:
            if filters.forward(rna):
                rna = add_name(rna)
                self.add_rna_to_building_list(all_rnas=all_rnas, rna=rna["rna"])
        dataset = self.create_dataset_from_list(rnas=all_rnas)
        return dataset
