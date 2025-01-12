import os
import sys
import json
import click
import pandas
import tables
import random
import warnings
import numpy as np

#from hydra_pywr import *
from pywr.model import Model
from .moea import SaveNondominatedSolutionsArchive
from pywr.recorders.progress import ProgressRecorder
from .custom_parameters_and_recorders import *
from .preprocess import *

import logging
logger = logging.getLogger(__name__)

@click.group()
def cli():
    pass

@cli.command(name='run', help="Run a Pywr model from a JSON file.")
@click.option('-f', '--file-name', type=str, help="The JSON file of the Pywr model you would like to run.")
def run(file_name):
    path = os.path.join("outputs")
    os.makedirs(path, exist_ok=True)

    #preprocessjson = JSONPreprocess(json_file=file_name)
    #preprocessjson.reorder()

    """ Run the Pywr model. """
    logger.info('Loading model from file: "{}"'.format(file_name))
    model = Model.load(file_name)

    warnings.filterwarnings('ignore', category=tables.NaturalNameWarning)

    ProgressRecorder(model)

    logger.info('Starting model run.')
    ret = model.run()
    logger.info(ret)

    try:
        df = model.to_dataframe()

        fn = '{}/{}.csv'.format("outputs","water_results_time_step")
        i=1
        while os.path.isfile(os.path.join(os.getcwd(), fn)):
            fn = '{}/{}_{}.csv'.format("outputs","water_results_time_step", str(i))
            i+=1
        df.to_csv(fn)
    except:
        pass


@cli.command(name='search', help="Perform multi-objective optimization for a Pywr JSON file model using an MOEA algorithm.")
@click.option('-f', '--file-name', type=str,help="The JSON file of the pywr model you would like to do the search on.")
@click.option('-s', '--seed', type=int, default=None, help="An integer representing the random starting point for the search.")
@click.option('-p', '--num-cpus', type=int, default=None, help="The number of processing cores to used for the search.")
@click.option('-n', '--max-nfe', type=int, default=1000, help="The number of iterations for the search.")
@click.option('--pop-size', type=int, default=50, help="The population size of the search.")
@click.option('-a', '--algorithm', type=click.Choice(['NSGAII', 'NSGAIII', 'EpsMOEA', 'EpsNSGAII']), default='NSGAII', help="The MOEA algorithm to be used for the search.")
@click.option('-e', '--epsilons', multiple=True, type=float, default=(0.05, ), help="The Epsilon value used with the EpsMOEA and EpsNSGAII algorithms.")
@click.option('--divisions-outer', type=int, default=12, help="The number of outer divisions used with the NSGAIII algorithm.")
@click.option('--divisions-inner', type=int, default=0, help="The number of inner divisions used with the NSGAIII algorithm.")
def search(file_name, seed, num_cpus, max_nfe, pop_size, algorithm, epsilons, divisions_outer, divisions_inner):
    import platypus

    logger.info('Loading model from file: "{}"'.format(file_name))
    directory, model_name = os.path.split(file_name)
    output_directory = os.path.join(directory, 'outputs')

    #preprocessjson = JSONPreprocess(json_file=file_name)
    #preprocessjson.reorder()

    if algorithm == 'NSGAII':
        algorithm_klass = platypus.NSGAII
        algorithm_kwargs = {'population_size': pop_size}
    elif algorithm == 'NSGAIII':
        algorithm_klass = platypus.NSGAIII
        algorithm_kwargs = {'divisions_outer': divisions_outer, 'divisions_inner': divisions_inner}
    elif algorithm == 'EpsMOEA':
        algorithm_klass = platypus.EpsMOEA
        algorithm_kwargs = {'population_size': pop_size, 'epsilons': epsilons}
    elif algorithm == 'EpsNSGAII':
        algorithm_klass = platypus.EpsNSGAII
        algorithm_kwargs = {'population_size': pop_size, 'epsilons': epsilons}
    else:
        raise RuntimeError('Algorithm "{}" not supported.'.format(algorithm))

    if seed is None:
        seed = random.randrange(sys.maxsize)

    search_data = {'algorithm': algorithm, 'seed': seed, 'user_metadata':algorithm_kwargs}
    wrapper = SaveNondominatedSolutionsArchive(file_name, search_data=search_data, output_directory=output_directory,
                                                   model_name=model_name)

    if seed is not None:
        random.seed(seed)

    logger.info('Starting model search.')

    if num_cpus is None:
        evaluator_klass = platypus.MapEvaluator
        evaluator_args = ()
    else:
        evaluator_klass = platypus.ProcessPoolEvaluator
        evaluator_args = (num_cpus,)

    with evaluator_klass(*evaluator_args) as evaluator:
        algorithm = algorithm_klass(wrapper.problem, evaluator=evaluator, **algorithm_kwargs, seed=seed)

        algorithm.run(max_nfe, callback=wrapper.save_nondominant)

def start_cli():
    """ Start the command line interface. """
    from . import logger
    import sys
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(ch)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # Also log pywr messages
    pywr_logger = logging.getLogger('pywr')
    pywr_logger.setLevel(logging.INFO)
    pywr_logger.addHandler(ch)
    cli(obj={})

start_cli()
