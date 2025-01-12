import uuid
import gzip
import os
import datetime
import pandas as pd
import numpy as np
import platypus
from platypus import Hypervolume
#from hydra_pywr import *

from pywr.optimisation.platypus import PlatypusWrapper
from .custom_parameters_and_recorders import *


import logging
logger = logging.getLogger(__name__)

class SaveNondominatedSolutionsArchive(PlatypusWrapper):

    def __init__(self, *args, **kwargs):
        self.output_directory = kwargs.pop('output_directory', 'outputs')
        self.search_data = kwargs.pop('search_data', {})
        self.model_name = kwargs.pop('model_name')
        super().__init__(*args, **kwargs)

        # To determine the number of variables, etc
        m = self.model
        self.hv_calculated = []

    @property
    def output_subdirectory(self):
        path = os.path.join(self.output_directory, self.model_name[0:-4], f'{self.uid}_seed{self.search_data["seed"]}')
        os.makedirs(path, exist_ok=True)
        return path

    def save_nondominant(self, algorithm):

        uid = uuid.uuid4().hex

        va = []
        va_ = []
        nva_ = []

        platypus_variables = platypus.nondominated(algorithm.result)
        for v in platypus_variables:
            for ivar, var in enumerate(self.model_variables):
                j = slice(self.model_variable_map[ivar], self.model_variable_map[ivar+1])
                tem_va = np.array(v.variables[j])
                tem_nme = [f'{var.name}[d{i}]' for i in range(len(tem_va))]

                va_.append(tem_va)
                nva_.append(tem_nme)

            va_flatt = [val for sublist in va_ for val in sublist]
            nva_flatt = [val for sublist in nva_ for val in sublist]
            va.append(va_flatt)
            va_ = []
            nva_ = []

        variables = pd.DataFrame(data=va, columns=nva_flatt)
        variables = variables.add_prefix('VAR_')

        platypus_objectives = platypus.nondominated(algorithm.result)

        objectives = pd.DataFrame(data=np.array([o.objectives for o in platypus_objectives]),
                                  columns=[f'{o.name}' for o in self.model_objectives])

        objectives = objectives.add_prefix('OBJ_')

        platypus_constraints = platypus.nondominated(algorithm.result)

#        TODO allow to pass double bounded constraints
        constraints = pd.DataFrame(data=np.array([c.constraints for c in platypus_constraints]),
                                   columns=[f'{c.name}' for c in self.model_constraints])

        constraints = constraints.add_prefix('CONS_')

        metrics = pd.concat([objectives, constraints, variables], axis=1)
        metrics['NFE'] = algorithm.nfe
        metrics.to_csv(os.path.join(self.output_subdirectory, f'nfe{algorithm.nfe}.csv.gz'), compression='infer')


        # Compute hypervolume
        num_objectives = len(self.model_objectives)
        min_ref = []
        max_ref = []
        for i in range(num_objectives):
                min_ref.append(-20000000)
                max_ref.append(20000000)

        hyp = Hypervolume(minimum=min_ref, maximum=max_ref)
        hv = hyp.calculate(algorithm.result)
        
        self.hv_calculated.append([algorithm.nfe, hv])
        hv_pd = pd.DataFrame(data=self.hv_calculated, columns=['nfe','hypervolume']).set_index('nfe')
        hv_pd.to_csv(os.path.join(self.output_subdirectory, f'hypervolume_seed_{self.search_data["seed"]}.csv'))
        print("Hypervolume:", hv)
