import os

from rnaglib.data_loading import RNADataset
from rnaglib.tasks import ResidueClassificationTask
from rnaglib.transforms import FeaturesComputer
from rnaglib.transforms import ResidueAttributeFilter, ComposeFilters
from rnaglib.transforms import DummyFilter
from rnaglib.transforms import PDBIDNameTransform


class ChemicalModification(ResidueClassificationTask):
    """Residue-level binary classification task to predict whether or not a given
    residue is chemically modified.
    """

    target_var = "is_modified"
    input_var = "nt_code"

    def __init__(self, root, splitter=None, **kwargs):
        super().__init__(root=root, splitter=splitter, **kwargs)

    def get_task_vars(self):
        return FeaturesComputer(nt_targets=self.target_var, nt_features=self.input_var)

    def process(self):
        # Define your transforms
        residue_attribute_filter = ResidueAttributeFilter(attribute=self.target_var, value_checker=lambda val: val == True)
        self.filters_list.append(residue_attribute_filter)
        rna_filter = ComposeFilters(self.filters_list)
        if self.debug:
            rna_filter = DummyFilter()
        add_name = PDBIDNameTransform()

        # Run through database, applying our filters
        dataset = RNADataset(debug=self.debug, in_memory=self.in_memory)
        all_rnas = []
        os.makedirs(self.dataset_path, exist_ok=True)
        for rna in dataset:
            if rna_filter.forward(rna):
                rna = add_name(rna)["rna"]
                self.add_rna_to_building_list(all_rnas=all_rnas,rna=rna)
        dataset = self.create_dataset_from_list(all_rnas)
        return dataset
