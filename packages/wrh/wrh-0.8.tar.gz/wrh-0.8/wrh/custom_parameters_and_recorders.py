from pywr.nodes import Link, Storage, Output, Input, AggregatedNode, NodeMeta
from pywr.domains.river import RiverDomainMixin, Catchment
from pywr.parameters.control_curves import ControlCurveInterpolatedParameter,ControlCurveIndexParameter,BaseControlCurveParameter,ControlCurveParameter
from pywr.parameters._thresholds import ParameterThresholdParameter
from pywr.parameters import AggregatedParameter, InterpolatedVolumeParameter, ConstantParameter, Parameter, MonthlyProfileParameter
from pywr.parameters.parameters import load_parameter
from pywr.parameters.parameters import AbstractInterpolatedParameter
from pywr.parameters import pop_kwarg_parameter, DataFrameParameter
from pywr.recorders import HydropowerRecorder, NumpyArrayLevelRecorder, NumpyArrayNodeRecorder, NumpyArrayStorageRecorder, NodeRecorder, NumpyArrayParameterRecorder
from pywr.parameter_property import parameter_property
from pywr.parameters._hydropower import inverse_hydropower_calculation
from pywr.recorders._hydropower import hydropower_calculation
from pywr.recorders._recorders import BaseConstantNodeRecorder, Recorder, Aggregator
from scipy import interpolate

import datetime
import numpy as np
from scipy.interpolate import Rbf
import pandas as pd
import math
import os


from pywr.nodes import (
    NodeMeta,
    Link,
    Input,
    AggregatedNode,
    Storage,
    Output
)

from pywr.parameters import (
    Parameter,
    load_parameter,
    ScenarioWrapperParameter,
    InterpolatedVolumeParameter,
    ConstantParameter,
    HydropowerTargetParameter,
	AggregatedParameter,
	MonthlyProfileParameter
)

from pywr.recorders import (
    HydropowerRecorder,
    NumpyArrayNodeRecorder
)

from pywr.parameters.control_curves import (
    ControlCurveInterpolatedParameter
)


class ProportionalInput(Input, metaclass=NodeMeta):
    min_proportion = 1e-6

    def __init__(self, model, name, node, proportion, **kwargs):
        super().__init__(model, name, **kwargs)

        self.node = model.pre_load_node(node)

        # Create the flow factors for the other node and self
        if proportion < self.__class__.min_proportion:
            self.max_flow = 0.0
        else:
            factors = [1, proportion]
            # Create the aggregated node to apply the factors.
            self.aggregated_node = AggregatedNode(model, f'{name}.aggregated', [self.node, self])
            self.aggregated_node.factors = factors


class LinearStorageReleaseControl(Link, metaclass=NodeMeta):
    """ A specialised node that provides a default max_flow based on a release rule. """

    def __init__(self, model, name, storage_node, release_values, scenario=None, **kwargs):

        if isinstance(release_values, str):
            release_values = load_parameter(model, release_values)
        else:
            release_values = pd.DataFrame.from_dict(release_values)

        storage_node = model.pre_load_node(storage_node)


        if isinstance(release_values, ControlCurveInterpolatedParameter):
            max_flow_param = release_values

        elif scenario is None:
            control_curves = release_values['volume'].astype(float).values[1:-1]
            values =  release_values['value'].astype(float).values

            max_flow_param = ControlCurveInterpolatedParameter(model, storage_node, control_curves, values)
        else:
            # There should be multiple control curves defined.
            if release_values.shape[1] % 2 != 0:
                raise ValueError("An even number of columns (i.e. pairs) is required for the release rules "
                                 "when using a scenario.")

            ncurves = release_values.shape[1] // 2
            if ncurves != scenario.size:
                raise ValueError(f"The number of curves ({ncurves}) should equal the size of the "
                                 f"scenario ({scenario.size}).")

            curves = []
            for i in range(ncurves):
                volume = release_values.iloc[1:-1, i*2]
                values = release_values.iloc[:, i*2+1]
                control_curve = ControlCurveInterpolatedParameter(model, storage_node, volume, values)
                curves.append(control_curve)

            max_flow_param = ScenarioWrapperParameter(model, scenario, curves)

        self.max_flow = max_flow_param
        self.scenario = scenario
        super().__init__(model, name, max_flow=max_flow_param, **kwargs)

    @classmethod
    def pre_load(cls, model, data):
        name = data.pop("name")
        cost = data.pop("cost", 0.0)
        min_flow = data.pop("min_flow", None)

        node = cls(name=name, model=model, **data)

        cost = load_parameter(model, cost)
        min_flow = load_parameter(model, min_flow)
        if cost is None:
            cost = 0.0
        if min_flow is None:
            min_flow = 0.0

        node.cost = cost
        node.min_flow = min_flow

        """
            The Pywr Loadable base class contains a reference to
            `self.__parameters_to_load.items()` which will fail unless
            a pre-mangled name which matches the expected value from
            inside the Loadable class is added here.

            See pywr/nodes.py:80 Loadable.finalise_load()
        """
        setattr(node, "_Loadable__parameters_to_load", {})
        return node

class Reservoir(RiverDomainMixin, Storage):
    """A reservoir node with control curve.

    The Reservoir is a subclass of Storage with additional functionality to provide a
    simple control curve. The Reservoir has above_curve_cost when it is above its curve
    and the user defined cost when it is below. Typically the costs are negative
    to represent a benefit of filling the reservoir when it is below its curve.

    A reservoir can also be used to simplify evaporation and rainfall by creating
    these nodes internally when the evaporation, rainfall, and area properties are set.

    Parameters
    ----------
    model : Model
        Model instance to which this storage node is attached.
    name : str
        The name of the storage node.
    min_volume : float (optional)
        The minimum volume of the storage. Defaults to 0.0.
    max_volume : float, Parameter (optional)
        The maximum volume of the storage. Defaults to 0.0.
    initial_volume, initial_volume_pc : float (optional)
        Specify initial volume in either absolute or proportional terms. Both are required if `max_volume`
        is a parameter because the parameter will not be evaluated at the first time-step. If both are given
        and `max_volume` is not a Parameter, then the absolute value is ignored.
    evaporation :   DataFrame, Parameter (optional)
        Normally a DataFrame with a index and a single column of 12 evaporation rates, representing each month in a year.
    evaporation_cost : float (optional)
        The cost of evaporation. Defaults to -999.
    unit_conversion : float (optional)
        The unit conversion factor for evaporation. Defaults to 1e6 * 1e-3 * 1e-6. This assumes area is Km2, level is m and evaporation is mm/day.
    rainfall : DataFrame, Parameter (optional)
        Normally a DataFrame with a index and a single column of 12 rainfall rates, representing each month in a year.
    area, level : float, Parameter (optional)
        Optional float or Parameter defining the area and level of the storage node. These values are
        accessible through the `get_area` and `get_level` methods respectively.
    """

    def __init__(self, model, *args, **kwargs):
        """

        Keywords:
            control_curve - A Parameter object that can return the control curve position,
                as a percentage of fill, for the given timestep.
        """

        __parameter_attributes__ = ("min_volume", "max_volume", "level", "area")

        control_curve = pop_kwarg_parameter(kwargs, "control_curve", None)
        above_curve_cost = kwargs.pop("above_curve_cost", None)
        cost = kwargs.pop("cost", 0.0)
        if above_curve_cost is not None:
            if control_curve is None:
                # Make a default control curve at 100% capacity
                control_curve = ConstantParameter(model, 1.0)
            elif not isinstance(control_curve, Parameter):
                # Assume parameter is some kind of constant and coerce to ConstantParameter
                control_curve = ConstantParameter(model, control_curve)

            if not isinstance(cost, Parameter):
                # In the case where an above_curve_cost is given and cost is not a Parameter
                # a default cost Parameter is created.
                kwargs["cost"] = ControlCurveParameter(
                    model, self, control_curve, [above_curve_cost, cost]
                )
            else:
                raise ValueError(
                    "If an above_curve_cost is given cost must not be a Parameter."
                )
        else:
            # reinstate the given cost parameter to pass to the parent constructors
            kwargs["cost"] = cost

        # self.level = pop_kwarg_parameter(kwargs, "level", None)
        # self.area = pop_kwarg_parameter(kwargs, "area", None)

        self.evaporation_cost = kwargs.pop('evaporation_cost', -999)
        self.unit_conversion = kwargs.pop('unit_conversion', 1e6 * 1e-3 * 1e-6) #This assume area is Km2, level is m and evaporation is mm/day

        self.evaporation = kwargs.pop("evaporation", None)
        self.rainfall = kwargs.pop("rainfall", None)

        name = kwargs.pop('name')
        super().__init__(model, name, **kwargs)

        self.rainfall_node = None
        self.rainfall_recorder = None
        self.evaporation_node = None
        self.evaporation_recorder = None


    def finalise_load(self):
        super(Reservoir, self).finalise_load()

        #in some cases, this hasn't been converted to a constant parameter, such as in the unit tests, so
        #check for that here.
        if not isinstance(self.unit_conversion, Parameter):
            self.unit_conversion = ConstantParameter(self.model, self.unit_conversion)

        if self.evaporation is not None:
            self._make_evaporation_node(self.evaporation, self.evaporation_cost)

        if self.rainfall is not None:
            self._make_rainfall_node(self.rainfall)

    def _make_evaporation_node(self, evaporation, cost):

        if not isinstance(self.area, Parameter):
            raise ValueError('Evaporation nodes can only be created if an area Parameter is given.')

        if isinstance(evaporation, Parameter):
            evaporation_param = evaporation
        elif isinstance(evaporation, str):
            evaporation_param = load_parameter(self.model, evaporation)
        elif isinstance(evaporation, (int, float)):
            evaporation_param = ConstantParameter(self.model, evaporation)
        else:
            evp = pd.DataFrame.from_dict(evaporation)
            evaporation_param = DataFrameParameter(self.model, evp)

        evaporation_flow_param = AggregatedParameter(self.model, [evaporation_param, self.unit_conversion, self.area],
                                                     agg_func='product')

        evaporation_node = Output(self.model, '{}_evaporation'.format(self.name), parent=self)
        evaporation_node.max_flow = evaporation_flow_param
        evaporation_node.cost = cost

        self.connect(evaporation_node)
        self.evaporation_node = evaporation_node

        self.evaporation_recorder = NumpyArrayNodeRecorder(self.model, evaporation_node,
                                                           name=f'__{evaporation_node.name}__:evaporation')

    def _make_rainfall_node(self, rainfall):
        if isinstance(rainfall, Parameter):
            rainfall_param = rainfall  
        elif isinstance(rainfall, str):
            rainfall_param = load_parameter(self.model, rainfall)
        elif isinstance(rainfall, (int, float)):
            rainfall_param = ConstantParameter(self.model, rainfall)
        else:
            #it's not a paramter or parameter reference, to try float and dataframe
            rain = pd.DataFrame.from_dict(rainfall)
            rainfall_param = DataFrameParameter(self.model, rain)

        # Create the flow parameters multiplying area by rate of rainfall/evap

        rainfall_flow_param = AggregatedParameter(self.model, [rainfall_param, self.unit_conversion, self.area],
                                                  agg_func='product')

        # Create the nodes to provide the flows
        rainfall_node = Catchment(self.model, '{}_rainfall'.format(self.name), parent=self)
        rainfall_node.max_flow = rainfall_flow_param


        rainfall_node.connect(self)
        self.rainfall_node = rainfall_node
        self.rainfall_recorder = NumpyArrayNodeRecorder(self.model, rainfall_node,
                                                        name=f'__{rainfall_node.name}__:rainfall')

class Turbine(Link, metaclass=NodeMeta):
    """ A hydropower turbine node.

    This node represents a hydropower turbine. It is used to model the generation of electricity from water flow.
    Internally, it uses a HydropowerTargetParameter to calculate the flow required to meet a given generation capacity.
    along with a HydropowerRecorder to record the generation and other relevant parameters.

    Parameters
    ----------
    model : Model
        Model instance to which this turbine node is attached.
    name : str
        Name of the node.
    efficiency : float (default=1.0)
        Turbine efficiency.
    density : float (default=1000.0)
        Water density.
    flow_unit_conversion : float (default=1.0)
        A factor used to transform the units of flow to be compatible with the equation here. This
        should convert flow to units of :math:`m^3/day`
    energy_unit_conversion : float (default=1e-6)
        A factor used to transform the units of energy to be compatible with the equation here. This
        should convert energy to units of :math:`MW`
    storage_node : str (default=None)
        Name of the storage node to which this turbine is connected. If not None, the water elevation
        of the storage node is used to calculate the head of the turbine.
    generation_capacity : float, Parameter (default=0.0)
        The maximum generation capacity of the turbine. This is the maximum amount of energy that the
        turbine can generate. This can be a constant value or a parameter, in :math:`MW`.
    turbine_elevation : double
        Elevation of the turbine itself. The difference between the `water_elevation` and this value gives
        the working head of the turbine.
    min_operating_elevation : double
        Minimum operating elevation of the turbine. This is used to calculate the minimum head of the turbine.
    min_flow : float, Parameter (default=0.0)
        The minimum flow required to operate the turbine. This can be a constant value or a parameter, in :math:`m^3/day`.
    """
    def __init__(self, model, name, **kwargs):
        hp_recorder_kwarg_names = ('efficiency', 'density', 'flow_unit_conversion', 'energy_unit_conversion')
        self.hp_kwargs = {}
        for kwd in hp_recorder_kwarg_names:
            try:
                self.hp_kwargs[kwd] = kwargs.pop(kwd)
            except KeyError:
                pass

        self.storage_node = kwargs.pop("storage_node", None)
        self.turbine_elevation = kwargs.pop('turbine_elevation', 0)
        self.generation_capacity = kwargs.pop('generation_capacity', 0)
        self.min_operating_elevation = kwargs.pop('min_operating_elevation', 0)
        self.min_head = self.min_operating_elevation - self.turbine_elevation

        super().__init__(model, name, **kwargs)

        if isinstance(self.generation_capacity, (float, int)):
            self.generation_capacity = ConstantParameter(model, self.generation_capacity)


    @classmethod
    def pre_load(cls, model, data):
        name = data.pop("name")
        cost = data.pop("cost", 0.0)
        min_flow = data.pop("min_flow", None)


        node = cls(name=name, model=model, **data)

        cost = load_parameter(model, cost)
        min_flow = load_parameter(model, min_flow)
        if cost is None:
            cost = ConstantParameter(node.model, 0.0)
        if min_flow is None:
            min_flow = ConstantParameter(node.model, 0.0)

        try:
            float(min_flow)
            min_flow = ConstantParameter(node.model, min_flow)
        except:
            pass

        node.cost = cost
        node.min_flow = min_flow
        setattr(node, "_Loadable__parameters_to_load", {})

        return node
    
    def finalise_load(self):
        super().finalise_load()

        level_parameter = None
        if self.storage_node is not None:
            storage_node = self.model.nodes[self.storage_node]
            #In some cases, the level of the storage node hasn't been assigned to the level parameter of the storage node.
            #we therefore need to find the parameter in the 'loadable' attribute of the node. Is there another way?
            if hasattr(storage_node, 'level') and not isinstance(storage_node.level, Parameter):
                if storage_node._Loadable__parameters_to_load.get('level'):
                    level_parameter = self.model.parameters[storage_node._Loadable__parameters_to_load['level']]
                else:
                    try:
                        float(storage_node.level)
                        level_parameter = ConstantParameter(self.model, storage_node.level)
                    except:
                        raise Exception(f"An unknown value {storage_node.level} was set on the storage node level.")
            else:
                #the level parameter has been assigned to the node so just retrieve it.
                level_parameter = storage_node.level

        hp_target_flow = HydropowerTargetParameter(self.model, self.generation_capacity,
                                                   water_elevation_parameter=level_parameter,
                                                   min_head=self.min_head, min_flow=self.min_flow,
                                                   turbine_elevation=self.turbine_elevation,
                                                   **self.hp_kwargs)

        self.max_flow = hp_target_flow

        hp_recorder = HydropowerRecorder(self.model, self,
                                         name=f"__{self.name}__:hydropower recorder",
                                         water_elevation_parameter=level_parameter,
                                         turbine_elevation=self.turbine_elevation, **self.hp_kwargs)
        self.hydropower_recorder = hp_recorder

class MonthlyOutput(Output, metaclass=NodeMeta):
    def __init__(self, model, name, scenario=None, **kwargs):
        super().__init__(model, name, **kwargs)



class ControlCurveInterpolatedMonthlyProfileParameter(ControlCurveInterpolatedParameter):
    def __init__(self, model, storage_node, control_curves, values,control_curve_da,value_da):
        super(ControlCurveInterpolatedMonthlyProfileParameter, self).__init__(model, storage_node, control_curves, values)
        self._storage_node=storage_node
        self.values = values
        self._control_curves=control_curves
        self._values = np.array(values)
        self.control_curve_da = control_curve_da
        self.value_da = value_da
            

    def value(self, ts, scenario_index):
    
        i = scenario_index.global_id
        
        node = self._storage_node
        # return the interpolated value for the current level.
        current_pc = node._current_pc[i]
        
        #node_us=model.nodes["C10"]

        if current_pc > 1.0:
            return self._values[0]

        if current_pc < 0.0:
            return self._values[-1]
        
        
        self._control_curves= self.control_curve_da[ts.month-1]
        self._values = self.value_da[ts.month-1]

        
        

        cc_prev = 1.0
        for j, cc_param in enumerate(self._control_curves):
            #cc = cc_param.get_value(scenario_index)
            cc = cc_param
            # If level above control curve then return this level's value
            if current_pc >= cc:
                try:
                    weight = (current_pc - cc) / (cc_prev - cc)
                except ZeroDivisionError:
                    # Last two control curves identical; return the next value
                    return self._values[j+1]
        
                return self._values[j]*weight + self._values[j+1]*(1.0 - weight)
            # Update previous value for next iteration
            cc_prev = cc

        # Current storage is above none of the control curves
        # Therefore interpolate between last control curve and bottom
        cc = 0.0
        try:
            weight = (current_pc - cc) / (cc_prev - cc)
        except ZeroDivisionError:
            # cc_prev == cc  i.e. last control curve is close to 0%
            return self._values[-2]
        return self._values[-2]*weight + self._values[-1]*(1.0 - weight)
    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        control_curves=data.pop("control_curves")
        values = data.pop("values")
        storage_node = data.pop("storage_node")
        
        control_curve_da = data.pop("control_curve_da")
        value_da = data.pop("value_da")
        storage_node = model._get_node_from_ref(model, storage_node)
        return cls(model, storage_node, control_curves, values,control_curve_da,value_da, **data)
    
ControlCurveInterpolatedMonthlyProfileParameter.register()




class Uncontrolled_spill(Parameter):
    def __init__(self, model, a, b, c, nodeOfAbs, **kwargs):
        super().__init__(model, **kwargs)
        self.nodeOfAbs = nodeOfAbs 
        self.a = a
        self.b = b
        self.c = c

    def setup(self):
        super().setup()
        self.sc_comb = len(self.model.scenarios.combinations)
        self.n_ts = len(self.model.timestepper)
        self.Q = np.zeros((self.n_ts, self.sc_comb,), np.float64)

    def value(self, ts, scenario_index):

        i = scenario_index.global_id
        UP_Flow=self.nodeOfAbs.prev_flow[i]
        self.Q[ts.index, scenario_index.global_id] = max(self.a.get_value(scenario_index) * UP_Flow**self.b.get_value(scenario_index) + self.c.get_value(scenario_index), 0)

        return self.Q[ts.index, scenario_index.global_id]
            
    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        a = load_parameter(model, data.pop("a_coefficent"))
        b = load_parameter(model, data.pop("b_coefficent"))
        c = load_parameter(model, data.pop("c_coefficent"))
        nodeOfAbs=model._get_node_from_ref(model, data.pop("nodeOfAbs"))

        return cls(model, a, b, c, nodeOfAbs, **data)
Uncontrolled_spill.register()  # register the name so it can be loaded from JSON


class Transmission_loss(Parameter):
    def __init__(self, model, coeff, nodeOfAbs, **kwargs):
        super().__init__(model, **kwargs)
        self.nodeOfAbs = nodeOfAbs 
        self.coeff = coeff

    def setup(self):
        super().setup()
        self.sc_comb = len(self.model.scenarios.combinations)
        self.n_ts = len(self.model.timestepper)
        self.a = self.coeff[0]
        self.b = self.coeff[1]
        self.Q = np.zeros((self.n_ts, self.sc_comb,), np.float64)

    def value(self, ts, scenario_index):

        i = scenario_index.global_id
        UP_Flow=self.nodeOfAbs.prev_flow[i]
        self.Q[ts.index, scenario_index.global_id] = max(self.a * UP_Flow + self.b, 0)

        return self.Q[ts.index, scenario_index.global_id]
            
    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        coeff = data.pop("loss coefficent")
        nodeOfAbs=model._get_node_from_ref(model, data.pop("nodeOfAbs"))

        return cls(model, coeff, nodeOfAbs, **data)
Transmission_loss.register()  # register the name so it can be loaded from JSON



class LakeSpillPolynomial(Parameter):
    def __init__(self, model, a, b, c, d, e, StorageNode, **kwargs):
        super().__init__(model, **kwargs)
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.StorageNode = StorageNode 

    def setup(self):
        super().setup()
        self.sc_comb = len(self.model.scenarios.combinations)
        self.n_ts = len(self.model.timestepper)
        self.spill = np.zeros((self.n_ts, self.sc_comb,), np.float64)

    def value(self, ts, scenario_index):
        storage = self.StorageNode.volume[scenario_index.global_id]
        #outflow in cms
        outflow = max((self.a.get_value(scenario_index) * (storage**4) + self.b.get_value(scenario_index) * (storage**3) + self.c.get_value(scenario_index) * (storage**2) + self.d.get_value(scenario_index) * storage + self.e.get_value(scenario_index)), 0)
        self.spill[ts.index, scenario_index.global_id] = outflow *(24*60*60/1000000)
        return self.spill[ts.index, scenario_index.global_id]
            
    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        a = load_parameter(model, data.pop("a_coefficent"))
        b = load_parameter(model, data.pop("b_coefficent"))
        c = load_parameter(model, data.pop("c_coefficent"))
        d = load_parameter(model, data.pop("d_coefficent"))
        e = load_parameter(model, data.pop("e_coefficent"))
        StorageNode=model._get_node_from_ref(model, data.pop("storage_node"))

        return cls(model, a, b, c, d, e, StorageNode, **data)
LakeSpillPolynomial.register()  # register the name so it can be loaded from JSON


class TransmissionLossPolynomialAverageTimesteps(Parameter):
    def __init__(self, model, a, b, c, d, e, AbstractionNode, number_of_timesteps, **kwargs):
        super().__init__(model, **kwargs)
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.AbstractionNode = AbstractionNode 
        self.number_of_timesteps = number_of_timesteps 

    def setup(self):
        super().setup()
        self.sc_comb = len(self.model.scenarios.combinations)
        self.n_ts = len(self.model.timestepper)
        self.loss = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.previous_flow = np.zeros((self.n_ts, self.sc_comb,), np.float64)

    def reset(self):
        self.previous_flow[...] = 0

    def value(self, ts, scenario_index):
        self.previous_flow[ts.index,scenario_index.global_id] = self.AbstractionNode.prev_flow[scenario_index.global_id]
        if ts.index < self.number_of_timesteps:
            if ts.index == 0:
                avrage_flow = 0
            else:
                avrage_flow = self.previous_flow[1:ts.index+1:1,scenario_index.global_id].mean(axis=0)
        else:
            avrage_flow = self.previous_flow[ts.index-(self.number_of_timesteps-1):ts.index+1:1,scenario_index.global_id].mean(axis=0)

        self.loss[ts.index, scenario_index.global_id] = max((self.a.get_value(scenario_index) * (avrage_flow**4) + self.b.get_value(scenario_index) * (avrage_flow**3) + self.c.get_value(scenario_index) * (avrage_flow**2) + self.d.get_value(scenario_index) * avrage_flow + self.e.get_value(scenario_index)), 0)

        return self.loss[ts.index, scenario_index.global_id]
            
    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        a = load_parameter(model, data.pop("a_coefficent"))
        b = load_parameter(model, data.pop("b_coefficent"))
        c = load_parameter(model, data.pop("c_coefficent"))
        d = load_parameter(model, data.pop("d_coefficent"))
        e = load_parameter(model, data.pop("e_coefficent"))
        AbstractionNode=model._get_node_from_ref(model, data.pop("node"))
        if "number_of_timesteps" in data:
            number_of_timesteps = data.pop("number_of_timesteps")
        else:
            number_of_timesteps = 12

        return cls(model, a, b, c, d, e, AbstractionNode, number_of_timesteps, **data)
TransmissionLossPolynomialAverageTimesteps.register()  # register the name so it can be loaded from JSON


class CurrentYear(Parameter):
    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)

    def setup(self):
        super().setup()
        self.sc_comb = len(self.model.scenarios.combinations)
        self.n_ts = len(self.model.timestepper)
        self.current_year = np.zeros((self.n_ts, self.sc_comb,), np.float64)

    def value(self, ts, scenario_index):
        self.current_year[ts.index,scenario_index.global_id] = ts.year
        return self.current_year[ts.index,scenario_index.global_id]

    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        return cls(model, **data)

CurrentYear.register()  # register the name so it can be loaded from JSON


class Machar_Marshes_spill(Parameter):
    def __init__(self, model, coeff, nodeOfAbs, **kwargs):
        super().__init__(model, **kwargs)
        self.nodeOfAbs=nodeOfAbs 
        self.coeff = coeff


    def value(self, timestep, scenario_index):
        i = scenario_index.global_id
        UP_Flow=self.nodeOfAbs.flow[i]/1000 #take flow in BCM

        Q=(self.coeff[4]*(UP_Flow**4)) + (self.coeff[3]*(UP_Flow**3)) + (self.coeff[2]*(UP_Flow**2)) + (self.coeff[1]*(UP_Flow)) + self.coeff[0]
        
        Y=0
        if UP_Flow>=Q:
            return Q
        else:
            return Y
            
    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        coeff = data.pop("loss coefficent")
        #nodeOfAbs = data.pop("nodeOfAbs")
        nodeOfAbs=model._get_node_from_ref(model, data.pop("nodeOfAbs"))
        return cls(model, coeff, nodeOfAbs, **data)
Machar_Marshes_spill.register()  # register the name so it can be loaded from JSON


class Wetland_spill(Parameter):
    def __init__(self, model, storage_node,spill_elevation=1785, **kwargs):
        super().__init__(model, **kwargs)
        #storage_node=model.nodes[storage_node]
        self.storage_node=storage_node
        self.spill_elevation=1785

    def value(self, timestep, scenario_index):
        #self.storage_node = storage_node = kwargs.pop('storage_node', None)
        #storage_node=model.nodes[storage_node]
        i = scenario_index.global_id
        #node = self.storage_node
        res_elevation = self.storage_node.volume[i]
        R_volume = [344,1640,3369,5407,7696,10200,12894,15760,18784,21954,25260,28696,32253]
        levels = [1773,1775,1776,1777,1778,1779,1780,1781,1782,1784,1785,1786,1787]
        Current_storage=res_elevation

        try:
            for j in range(len(R_volume)):

                    if R_volume[j+1] >= Current_storage and Current_storage >= R_volume[j]:
                        weight = (R_volume[j+1] - R_volume[j]) / (levels[j+1] - levels[j])
                        res_elevation =levels[j+1]-((R_volume[j+1]-Current_storage)/weight)
                        
        except IndexError:
            pass
        
        
        
        #res_elevation = self.storage_node.level
        
        #res_elevation = InterpolatedVolumeParameter(self.model, storage_node.level, R_volume, levels)
        
        if res_elevation>self.spill_elevation:
            H=res_elevation-self.spill_elevation
            Q=((100)*(H**1.5))*0.0864
            return Q
        else:
            Q=0
            return Q

            
    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        #values = data.pop("values")
        storage_node = data.pop("storage_node")
        spill_elevation = data.pop("spill_elevation")
        storage_node = model._get_node_from_ref(model, storage_node)
        return cls(model, storage_node, spill_elevation, **data)
    
Wetland_spill.register()  # register the name so it can be loaded from JSON




from pywr.parameters import Parameter
class BahirElGazel_spill(Parameter):
    def __init__(self,  model, storage_node, volume, discharge, **kwargs):
        super().__init__(model, **kwargs)
        self.storage_node=storage_node
        self.volume = volume
        self.discharge = discharge

    def value(self, timestep, scenario_index):
        #self.storage_node = storage_node = kwargs.pop('storage_node', None)
        #storage_node=model.nodes[storage_node]
        i = scenario_index.global_id
        #node = self.storage_node
        res_volume = self.storage_node.volume[i]
        volume = self.volume
        discharge = self.discharge
        Current_storage=res_volume
        res_elevation=0

        try:
            for j in range(len(volume)):

                    if volume[j+1] >= Current_storage and Current_storage >= volume[j]:
                        weight = (volume[j+1] - volume[j]) / (discharge[j+1] - discharge[j])
                        res_elevation =discharge[j+1]-((volume[j+1]-Current_storage)/weight)
        except IndexError:
            pass
        
        if res_elevation>0:
            
            Q=res_elevation
            return Q
        else:
            Q=0
            return Q
            
    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        #values = data.pop("values")
        storage_node = data.pop("storage_node")
        volume = data.pop("volume")
        discharge = data.pop("discharge")
        storage_node = model._get_node_from_ref(model, storage_node)
        return cls(model, storage_node, volume,discharge, **data)  
BahirElGazel_spill.register()  # register the name so it can be loaded from JSON



class LakeTanaUncontrolledSpill(Parameter):
    def __init__(self, model, storage_node, R_elevation,R_volume,spill_elevation=1785, **kwargs):
        super().__init__(model, **kwargs)
        self.storage_node=storage_node
        self.elevation = R_elevation
        self.R_volume=R_volume
        self.storage=storage_node
        self.spill_elevation=spill_elevation

    def value(self, timestep, scenario_index):
        Current_storage=self.storage_node.volume[scenario_index.global_id]
        
        try:
            
            for j in range(len(self.R_volume)):

                if self.R_volume[j+1] >= Current_storage and Current_storage >= self.R_volume[j]:
                    weight = (self.R_volume[j+1] - self.R_volume[j]) / (self.elevation[j+1] - self.elevation[j])
                    res_elevation =self.elevation[j+1]-((self.R_volume[j+1]-Current_storage)/weight)

                    if res_elevation>self.spill_elevation:
                        H=res_elevation-self.spill_elevation

                        Q=(100*(H**1.5))*0.0864

                        return Q 
                    else:
                        Q=0.4
                        
                        return Q
        except IndexError:

            Q=(100*(2.5**1.5))*0.0864
            return Q
            
    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        R_elevation = data.pop("R_elevation")
        R_volume = data.pop("R_volume")
        spill_elevation = data.pop("spill_elevation")
        storage_node = model._get_node_from_ref(model, data.pop("storage_node"))
        return cls(model, storage_node, R_elevation, R_volume, **data)
    
LakeTanaUncontrolledSpill.register() 


class MinReleaseInitialFillingParameter(Parameter):
    """ A parameter simulates the filling and long-term operation of the GERD.

    This parameter returns the min_volume for the GERD and also modifies other
    parameters that influence downstream dams. The parameter should be linked to
    GERD min_volume. The paramter is simulates a fraction-based filling rule for
    the GERD.

    inputs
    ----------
    type : a string "FlowFractionInitialFillingParameter"
    inflow_node : the node directly upstream of the GERD that provides the dam inflow
    outflow_constant_scenario_parameter : a ConstantScenarioParameter linked to the max_flow of 
                GERD control node. The values of this node are modified by this parameter to control
                GERD outflow during filling and long-term operation.
    Egypt_bypass_parameter : a ConstantScenarioParameter used to make sure that coordinated releases
                Between the GERD and HAD reaches Egypt. In other words, Egypt_bypass_parameter is added
                to water releases from the Roseires, Sennar, and Merowe dams to make sure that Sudan 
                does not use releases from the GERD that are meant for Egypt.
    storage_node : GERD reservoir node.
    annual_release : a number graeter than 0 represnts the minimum GERD release volume per year
    steady_state_storage : reservoir storage at which the steady-state operation starts
    long_term_min_volume : This is the long-term GERD dead storage of GERD once full. During the filling,
                the GERD is not allowed to fall below this level once reached.
    "minimum_daily_release": a minimum daily release value
    long_term_outflow : This is a parameter that provides the long-term GERD outflow. This is used to
                control GERD releases in the long-term after filling.

    Example
    -----------
      "GERD_min":{
         "type":"FlowFractionInitialFillingParameter",
         "inflow_node":"C60",
         "outflow_constant_scenario_parameter": "GERD_outflow_control",
         "Egypt_bypass_parameter": "Egypt_bypass",
         "storage_node":"GERD",
         "steady_state_storage":49750,
         "annual_release":37000,
         "long_term_min_volume":15000,
         "minimum_daily_release":15,
         "long_term_outflow":"GERD_target_power_flow"
      },

    """

    def __init__(self, model, inflow_node, outflow_node, outflow_constant_scenario_parameter, 
    Egypt_bypass_parameter, storage_node, annual_release, steady_state_storage, minimum_daily_release, long_term_min_volume, long_term_outflow, **kwargs):
        super().__init__(model, **kwargs)
        self._inflow_node = inflow_node
        self._outflow_node = outflow_node
        self._outflow_constant_scenario_parameter = outflow_constant_scenario_parameter
        self._Egypt_bypass_parameter = Egypt_bypass_parameter
        self._storage_node = storage_node
        self._annual_release = annual_release
        self._steady_state_storage = steady_state_storage
        self._minimum_daily_release = minimum_daily_release
        self._long_term_min_volume = long_term_min_volume
        self._long_term_outflow = None
        self.long_term_outflow = long_term_outflow
        self.egypt_irrigation_node1 = model._get_node_from_ref(model, "Egypt Irrigation")
        self.egypt_irrigation_node2 = model._get_node_from_ref(model, "Toshka Irrigation")
        self.egypt_municipal_node = model._get_node_from_ref(model, "Egypt Municipal")

    long_term_outflow = parameter_property("_long_term_outflow")

    def setup(self):
        super().setup()
        self.sc_size = 1
        self.sc_comb = len(self.model.scenarios.combinations)
        for m in range(len(self.model.scenarios.scenarios)):
            self.sc_size = self.sc_size * self.model.scenarios.scenarios[m].size
        self.n_ts = len(self.model.timestepper)
        self.nyears = self.model.timestepper.end.year - self.model.timestepper.start.year + 1

        self.volume_pc_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        self.stage1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        for s in range(self.sc_comb):
            self.previous_outflow_recorder[0,s,0] = self._annual_release/365.25

        self.assignment_values = []
        self.assignment_values2 = []
        for s in range(self.sc_size):
            self.assignment_values.append(100)
            self.assignment_values2.append(0)

    def reset(self):
        self.volume_pc_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        self.stage1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        for s in range(self.sc_comb):
            self.previous_outflow_recorder[0,s,0]=self._annual_release/365.25

    def value(self, ts, scenario_index):

        self.volume_pc_recorder[ts.index, scenario_index.global_id] = self._storage_node.volume[scenario_index.global_id]
        self._max_flow_irr1[ts.index, scenario_index.global_id] = self.egypt_irrigation_node1.get_max_flow(scenario_index)
        self._max_flow_irr2[ts.index, scenario_index.global_id] = self.egypt_irrigation_node2.get_max_flow(scenario_index)
        self._max_flow_muni[ts.index, scenario_index.global_id] = self.egypt_municipal_node.get_max_flow(scenario_index)

        self.year_index = ts.year-self.model.timestepper.start.year
        self.month_index = ts.month-1

        if ts.index != 0 and self.iteration_check[ts.index, scenario_index.global_id]==0:
            self.previous_outflow_recorder[self.month_index,scenario_index.global_id,self.year_index] = self._outflow_node.prev_flow[scenario_index.global_id]

            self.egypt_irrigation_deficit = max((self._max_flow_irr1[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node1.prev_flow[scenario_index.global_id]),0)+max((self._max_flow_irr2[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node2.prev_flow[scenario_index.global_id]),0)
            self.egypt_municipal_deficit = max((self._max_flow_muni[ts.index-1, scenario_index.global_id] - self.egypt_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.egypt_total_deficit[ts.index, scenario_index.global_id] = (self.egypt_irrigation_deficit + self.egypt_municipal_deficit)/0.9

            self.iteration_check[ts.index, scenario_index.global_id] = 1

        if ts.index != 0:
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= 4500 and self.stage1[ts.index-1, scenario_index.global_id] != 3:
                self.stage1[ts.index, scenario_index.global_id] = 1
            if ts.month == 6 and self.stage1[ts.index-1, scenario_index.global_id] == 1:
                self.stage1[ts.index, scenario_index.global_id] = 3
            if self.stage1[ts.index-1, scenario_index.global_id] == 3:
                self.stage1[ts.index, scenario_index.global_id] = 3
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self._long_term_min_volume and self.stage2[ts.index-1, scenario_index.global_id] != 3:
                self.stage2[ts.index, scenario_index.global_id] = 1
            if ts.month == 6 and self.stage2[ts.index-1, scenario_index.global_id] == 1:
                self.stage2[ts.index, scenario_index.global_id] = 3
            if self.stage2[ts.index-1, scenario_index.global_id] == 3:
                self.stage2[ts.index, scenario_index.global_id] = 3

        """
        The follwoing equation is used to activate or deactivate coordination of operation between
        the GERD and the HAD. Coordination implies that the GERD makes extra releases to satisfy water
        deficits in Egypt. To activate coordiation hash out the eqation below
        """
        #self.egypt_total_deficit[ts.index, scenario_index.global_id] = 0

        if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) <= 0.99 * self._steady_state_storage:
                
            """
            The part within the condition above models the filling.
            """

            """
            The if statement below is added to simulate the GERD filling stages for stability and
            turbines testing. Once the GERD reaches a stage, it is not allowed to go lower. The
            first stage is 4500 MCM and the second stage is dead storage.
            """
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self._long_term_min_volume and self.stage1[ts.index, scenario_index.global_id] != 1:
                self.min_volume = self._long_term_min_volume     
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= 4500:
                self.min_volume = 4500
            else:
                self.min_volume = 10

            """
            setting outflow.
            """
            if self.stage1[ts.index, scenario_index.global_id] == 1 or self.stage2[ts.index, scenario_index.global_id] == 1:
                if ts.month != 1:
                    self.correction =  max((self._annual_release/365.25 - self.previous_outflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].mean(axis=0)),0)
                else:
                    self.correction = 0

                self.assignment_values[scenario_index.indices[0]] = max(max(self._inflow_node.prev_flow[scenario_index.global_id] + self.egypt_total_deficit[ts.index, scenario_index.global_id] + self.correction * (self.month_index+1), 0), self._minimum_daily_release)
                self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]

                self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
            else:
                if ts.month != 1:
                    self.correction =  self._annual_release/365.25 - self.previous_outflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].mean(axis=0)
                else:
                    self.correction = 0

                self.assignment_values[scenario_index.indices[0]] = max(max((self._annual_release/365.25 + self.egypt_total_deficit[ts.index, scenario_index.global_id] + self.correction * (self.month_index+1)),0), self._minimum_daily_release)
                self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]

                self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
            return self.min_volume
        else:
            """
            The part within simulates long-term operation.
            """
            if ts.month != 1:
                self.correction =  max((self._annual_release/365.25 - self.previous_outflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].mean(axis=0)),0)
            else:
                self.correction = 0

            self.assignment_values[scenario_index.indices[0]] = max(max((self._long_term_outflow.get_value(scenario_index) + self.egypt_total_deficit[ts.index, scenario_index.global_id] + self.correction * (self.month_index+1)), 0), self._minimum_daily_release)
            self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]

            self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
            self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
           
            self.min_volume = self._long_term_min_volume
            return self.min_volume
            
    @classmethod
    def load(cls, model, data):
        inflow_node = model._get_node_from_ref(model, data.pop("inflow_node"))
        outflow_node = model._get_node_from_ref(model, data.pop("outflow_node"))
        outflow_constant_scenario_parameter = load_parameter(model, data.pop("outflow_constant_scenario_parameter"))
        Egypt_bypass_parameter = load_parameter(model, data.pop("Egypt_bypass_parameter"))
        storage_node = model._get_node_from_ref(model, data.pop("storage_node"))
        annual_release = data.pop("annual_release")
        steady_state_storage = data.pop("steady_state_storage")
        minimum_daily_release = data.pop("minimum_daily_release")
        long_term_min_volume = data.pop("long_term_min_volume")
        long_term_outflow = load_parameter(model, data.pop("long_term_outflow"))

        return cls(model, inflow_node, outflow_node, outflow_constant_scenario_parameter, Egypt_bypass_parameter,
        storage_node, annual_release, steady_state_storage, minimum_daily_release, long_term_min_volume, long_term_outflow, **data)
MinReleaseInitialFillingParameter.register()


class InterpolatedFlowParameterTwelveMonth(AbstractInterpolatedParameter):
    """
    Generic interpolation parameter that uses a node's  average flow at the twelve previous time-step for interpolation.

    """
    def __init__(self, model, node, x, y, interp_kwargs=None, **kwargs):
        super().__init__(model, x, y, interp_kwargs, **kwargs)
        self._node = node

    def setup(self):
        super().setup()
        ncomb = len(self.model.scenarios.combinations)
        nts = len(self.model.timestepper)
        self.previous_flow = np.zeros((nts, ncomb,), np.float64)

    def reset(self):
        self.previous_flow[...] = 0

    def _value_to_interpolate(self, ts, scenario_index):
        self.previous_flow[ts.index,scenario_index.global_id] = self._node.prev_flow[scenario_index.global_id]
        if ts.index < 12:
            if ts.index == 0:
                self.value_to_return = 0
            else:
                self.value_to_return = self.previous_flow[1:ts.index+1:1,scenario_index.global_id].mean(axis=0)
        else:
            self.value_to_return = self.previous_flow[ts.index-11:ts.index+1:1,scenario_index.global_id].mean(axis=0)

        return self.value_to_return

    @classmethod
    def load(cls, model, data):
        node = model._get_node_from_ref(model, data.pop("node"))
        volumes = np.array(data.pop("flows"))
        values = np.array(data.pop("values"))
        kind = data.pop("kind", "linear")
        return cls(model, node, volumes, values, interp_kwargs={'kind': kind})
InterpolatedFlowParameterTwelveMonth.register()


class WashingtonProposal(Parameter):
    """ A parameter simulates the filling and long-term operation of the GERD.

    This parameter returns the min_volume for the GERD and also modifies other
    parameters that influence downstream dams. The parameter should be linked to
    GERD min_volume. The paramter is simulates a fraction-based filling rule for
    the GERD.

    inputs
    ----------
    type : a string "FlowFractionInitialFillingParameter"
    inflow_node : the node directly upstream of the GERD that provides the dam inflow
    outflow_constant_scenario_parameter : a ConstantScenarioParameter linked to the max_flow of 
                GERD control node. The values of this node are modified by this parameter to control
                GERD outflow during filling and long-term operation.
    Egypt_bypass_parameter : a ConstantScenarioParameter used to make sure that coordinated releases
                Between the GERD and HAD reaches Egypt. In other words, Egypt_bypass_parameter is added
                to water releases from the Roseires, Sennar, and Merowe dams to make sure that Sudan 
                does not use releases from the GERD that are meant for Egypt.
    storage_node : GERD reservoir node.
    annual_release : a number graeter than 0 represnts the minimum GERD release volume per year
    steady_state_storage : reservoir storage at which the steady-state operation starts
    long_term_min_volume : This is the long-term GERD dead storage of GERD once full. During the filling,
                the GERD is not allowed to fall below this level once reached.
    "minimum_daily_release": a minimum daily release value
    long_term_outflow : This is a parameter that provides the long-term GERD outflow. This is used to
                control GERD releases in the long-term after filling.

    Example
    -----------
      "GERD_min":{
         "type":"WashingtonProposal",
         "inflow_node":"C60",
         "outflow_constant_scenario_parameter": "GERD_outflow_control",
         "Egypt_bypass_parameter": "Egypt_bypass",
         "storage_node":"GERD",
         "steady_state_storage":49750,
         "annual_release":37000,
         "long_term_min_volume":15000,
         "minimum_daily_release":15,
         "long_term_outflow":"GERD_target_power_flow"
      },

    """

    def __init__(self, model, inflow_node, outflow_node, outflow_constant_scenario_parameter, 
    Egypt_bypass_parameter, storage_node, annual_release, four_year_release, five_year_release,
    steady_state_storage, minimum_daily_release, maximum_daily_release, ts_to_ts_max_change_in_outflow,
    long_term_min_volume, long_term_outflow, first_filling_year,offset_years, first_filling_year_actual_volume,
    second_filling_year_actual_volume, release_table_during_filling_csv, release_table_during_operation_csv,
    consider_release_tables_and_drought_meastures, save_intermediate_calculations, **kwargs):
        super().__init__(model, **kwargs)
        self._inflow_node = inflow_node
        self._outflow_node = outflow_node
        self._outflow_constant_scenario_parameter = outflow_constant_scenario_parameter
        self._Egypt_bypass_parameter = Egypt_bypass_parameter
        self._storage_node = storage_node
        self._annual_release = None
        self.annual_release = annual_release
        self._four_year_release = None
        self.four_year_release = four_year_release
        self._five_year_release = None
        self.five_year_release = five_year_release
        self._steady_state_storage = steady_state_storage
        self._minimum_daily_release = minimum_daily_release
        self._long_term_min_volume = long_term_min_volume
        self._long_term_outflow = None
        self.long_term_outflow = long_term_outflow
        self.egypt_irrigation_node1 = model._get_node_from_ref(model, "Egypt Irrigation")
        self.egypt_irrigation_node2 = model._get_node_from_ref(model, "Toshka Irrigation")
        self.egypt_municipal_node = model._get_node_from_ref(model, "Egypt Municipal")
        self._GERD_dummy_bypass_parameter = load_parameter(model, "GERD_dummy_bypass")
        self.first_filling_year = first_filling_year
        self.offset_years =offset_years
        self.first_filling_year_actual_volume = first_filling_year_actual_volume
        self.second_filling_year_actual_volume = second_filling_year_actual_volume

    long_term_outflow = parameter_property("_long_term_outflow")
    annual_release = parameter_property("_annual_release")
    four_year_release = parameter_property("_four_year_release")
    five_year_release = parameter_property("_five_year_release")

    def setup(self):
        super().setup()
        self.sc_size = 1
        self.sc_comb = len(self.model.scenarios.combinations)
        for m in range(len(self.model.scenarios.scenarios)):
            self.sc_size = self.sc_size * self.model.scenarios.scenarios[m].size
        self.n_ts = len(self.model.timestepper)
        self.nyears = self.model.timestepper.end.year - self.model.timestepper.start.year + 1

        self.volume_pc_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)

        if self.model.timestepper.delta == "M":
            self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        elif self.model.timestepper.delta == "D":
            self.previous_outflow_recorder = np.zeros((366, self.sc_comb, self.nyears,), np.float64)

        self.previous_inflow_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        for s in range(self.sc_comb):
            self.previous_outflow_recorder[0,s,0] = 100

        self.assignment_values = []
        self.assignment_values2 = []
        self.assignment_values3 = []
        for s in range(self.sc_size):
            self.assignment_values.append(100)
            self.assignment_values2.append(0)
            self.assignment_values3.append(0)

    def reset(self):
        self.volume_pc_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        if self.model.timestepper.delta == "M":
            self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        elif self.model.timestepper.delta == "D":
            self.previous_outflow_recorder = np.zeros((366, self.sc_comb, self.nyears,), np.float64)

        self.previous_inflow_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        for s in range(self.sc_comb):
            self.previous_outflow_recorder[0,s,0]=100

    def value(self, ts, scenario_index):

        self.year_index = ts.year-self.model.timestepper.start.year
        self.year_fill = ts.year + self.offset_years
        self.month_index = ts.month-1
        self.day_index = ts.dayofyear-1

        if ((ts.month != 1 and self.model.timestepper.delta == "M") or ((ts.month != 1 and ts.day != 1) and self.model.timestepper.delta == "D")) and self.iteration_check[ts.index, scenario_index.global_id]==1:
            self.volume_pc_recorder[ts.index, scenario_index.global_id] = self._storage_node.volume[scenario_index.global_id]
            self._max_flow_irr1[ts.index, scenario_index.global_id] = self.egypt_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_irr2[ts.index, scenario_index.global_id] = self.egypt_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_muni[ts.index, scenario_index.global_id] = self.egypt_municipal_node.get_max_flow(scenario_index)

            if self.model.timestepper.delta == "M":
                self.previous_outflow_recorder[self.month_index-1,scenario_index.global_id,self.year_index] = self._outflow_node.prev_flow[scenario_index.global_id]
            elif self.model.timestepper.delta == "D":
                self.previous_outflow_recorder[self.day_index-1,scenario_index.global_id,self.year_index] = self._outflow_node.prev_flow[scenario_index.global_id]

            self.previous_inflow_recorder[ts.index, scenario_index.global_id] = self._inflow_node.prev_flow[scenario_index.global_id]

            self.egypt_irrigation_deficit = max((self._max_flow_irr1[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node1.prev_flow[scenario_index.global_id]),0)+max((self._max_flow_irr2[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node2.prev_flow[scenario_index.global_id]),0)
            self.egypt_municipal_deficit = max((self._max_flow_muni[ts.index-1, scenario_index.global_id] - self.egypt_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.egypt_total_deficit[ts.index, scenario_index.global_id] = (self.egypt_irrigation_deficit + self.egypt_municipal_deficit)/0.9

        if ts.index != 0 and self.iteration_check[ts.index, scenario_index.global_id]==0:
            self.volume_pc_recorder[ts.index, scenario_index.global_id] = self._storage_node.volume[scenario_index.global_id]
            self._max_flow_irr1[ts.index, scenario_index.global_id] = self.egypt_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_irr2[ts.index, scenario_index.global_id] = self.egypt_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_muni[ts.index, scenario_index.global_id] = self.egypt_municipal_node.get_max_flow(scenario_index)

            if self.model.timestepper.delta == "M":
                self.previous_outflow_recorder[self.month_index-1,scenario_index.global_id,self.year_index] = self._outflow_node.prev_flow[scenario_index.global_id]
            elif self.model.timestepper.delta == "D":
                self.previous_outflow_recorder[self.day_index-1,scenario_index.global_id,self.year_index] = self._outflow_node.prev_flow[scenario_index.global_id]

            self.previous_inflow_recorder[ts.index, scenario_index.global_id] = self._inflow_node.prev_flow[scenario_index.global_id]

            self.egypt_irrigation_deficit = max((self._max_flow_irr1[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node1.prev_flow[scenario_index.global_id]),0)+max((self._max_flow_irr2[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node2.prev_flow[scenario_index.global_id]),0)
            self.egypt_municipal_deficit = max((self._max_flow_muni[ts.index-1, scenario_index.global_id] - self.egypt_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.egypt_total_deficit[ts.index, scenario_index.global_id] = (self.egypt_irrigation_deficit + self.egypt_municipal_deficit)/0.9
            
            self.iteration_check[ts.index, scenario_index.global_id] = 1


        if self.year_fill >= self.first_filling_year and ts.index != 0:
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.first_filling_year_actual_volume and self.stage1[ts.index-1, scenario_index.global_id] != 3:
                self.stage1[ts.index, scenario_index.global_id] = 1
            else:
                self.stage1[ts.index, scenario_index.global_id] = 0
            if ts.month == 7 and self.stage1[ts.index-1, scenario_index.global_id] == 1:
                self.stage1[ts.index, scenario_index.global_id] = 3
            if self.stage1[ts.index-1, scenario_index.global_id] == 3:
                self.stage1[ts.index, scenario_index.global_id] = 3
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.second_filling_year_actual_volume and self.stage2[ts.index-1, scenario_index.global_id] != 3:
                self.stage2[ts.index, scenario_index.global_id] = 1
            else:
                self.stage2[ts.index, scenario_index.global_id] = 0
            if ts.month == 7 and self.stage2[ts.index-1, scenario_index.global_id] == 1:
                self.stage2[ts.index, scenario_index.global_id] = 3
            if self.stage2[ts.index-1, scenario_index.global_id] == 3:
                self.stage2[ts.index, scenario_index.global_id] = 3

        """
        The follwoing equation is used to activate or deactivate coordination of operation between
        the GERD and the HAD. Coordination implies that the GERD makes extra releases to satisfy water
        deficits in Egypt. To activate coordiation hash out the eqation below
        """
        self.egypt_total_deficit[ts.index, scenario_index.global_id] = 0

        if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) <= 0.99 * self._steady_state_storage:

            """
            The part within the condition above models the filling.
            """

            """
            The if statement below is added to simulate the GERD filling stages for stability and
            turbines testing. Once the GERD reaches a stage, it is not allowed to go lower. The
            first stage is 4900 MCM and the second stage is dead storage.
            """
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= 24350:
                self.min_volume = 24350
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self._long_term_min_volume and self.stage1[ts.index, scenario_index.global_id] != 1:
                self.min_volume = self._long_term_min_volume     
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.second_filling_year_actual_volume:
                self.min_volume = self.second_filling_year_actual_volume
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= 4900:
                self.min_volume = 4900
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.first_filling_year_actual_volume:
                self.min_volume = self.first_filling_year_actual_volume
            else:
                self.min_volume = 10

            """
            setting outflow.
            """
            if ts.month == 7 or ts.month == 8:

                if self.stage1[ts.index, scenario_index.global_id] == 1 or self.stage2[ts.index, scenario_index.global_id] == 1:
                    self.assignment_values[scenario_index.indices[0]] = 10000
                    self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                    self.assignment_values3[scenario_index.indices[0]] = 10000

                    self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                    self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                    self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))
                else:
                    self.assignment_values[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id] + self._minimum_daily_release
                    self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                    self.assignment_values3[scenario_index.indices[0]] = 0.1

                    self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                    self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                    self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))
            else:
                
                if self.stage1[ts.index, scenario_index.global_id] == 1 or self.stage2[ts.index, scenario_index.global_id] == 1:
                    self.assignment_values[scenario_index.indices[0]] = 10000
                    self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                    self.assignment_values3[scenario_index.indices[0]] = 10000

                    self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                    self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                    self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))
                else:
                    if ts.month == 3 or ts.month == 4 or ts.month == 5:
                        if self.model.timestepper.delta == "M":

                            if self.year_fill >= (1+self.first_filling_year):
                                self.correction_annual = max((self._annual_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[5:12,scenario_index.global_id,self.year_index-1].mean(axis=0))/2),0) * (7+self.month_index+1)
                            else:
                                self.correction_annual = 0

                            if self.year_fill >= (4+self.first_filling_year):
                                self.correction_four_year = max((self._annual_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-1].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-2].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-3].mean(axis=0) + self.previous_outflow_recorder[5:12,scenario_index.global_id,self.year_index-4].mean(axis=0))/5),0) * (7+self.month_index+1+36)
                            else:
                                self.correction_four_year = 0

                            if self.year_fill >= (5+self.first_filling_year):
                                self.correction_five_year = max((self._five_year_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-1].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-2].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-3].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-4].mean(axis=0) + self.previous_outflow_recorder[5:12,scenario_index.global_id,self.year_index-5].mean(axis=0))/6),0) * (7+self.month_index+1+48)
                            else:
                                self.correction_five_year = 0

                            self.correction =  max(self.correction_annual, self.correction_four_year, self.correction_five_year)

                        elif self.model.timestepper.delta == "D":

                            if self.year_fill >= (1+self.first_filling_year):
                                self.correction_annual = max((self._annual_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.day_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[153:367,scenario_index.global_id,self.year_index-1].mean(axis=0))/2),0) * (214+self.day_index+1)
                            else:
                                self.correction_annual = 0

                            if self.year_fill >= (4+self.first_filling_year):
                                self.correction_four_year = max((self._annual_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.day_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-1].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-2].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-3].mean(axis=0) + self.previous_outflow_recorder[153:367,scenario_index.global_id,self.year_index-4].mean(axis=0))/5),0) * (214+366*3+self.day_index+1)
                            else:
                                self.correction_four_year = 0

                            if self.year_fill >= (5+self.first_filling_year):
                                self.correction_five_year = max((self._five_year_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.day_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-1].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-2].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-3].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-4].mean(axis=0) + self.previous_outflow_recorder[153:367,scenario_index.global_id,self.year_index-5].mean(axis=0))/6),0) * (214+366*4+self.day_index+1)
                            else:
                                self.correction_five_year = 0

                            self.correction =  max(self.correction_annual, self.correction_four_year, self.correction_five_year)

                        self.assignment_values[scenario_index.indices[0]] = min(max(self.egypt_total_deficit[ts.index, scenario_index.global_id] + self.correction, 0),500)
                        self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                        self.assignment_values3[scenario_index.indices[0]] = 10000
                    else:
                        self.correction = 0

                        self.assignment_values[scenario_index.indices[0]] = max(self.egypt_total_deficit[ts.index, scenario_index.global_id] + self.correction, 0)
                    self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                    self.assignment_values3[scenario_index.indices[0]] = 10000

                    self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                    self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                    self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))

            return self.min_volume
        else:
            """
            The part within simulates long-term operation.
            """
            if ts.month == 3 or ts.month == 4 or ts.month == 5:
                if self.model.timestepper.delta == "M":

                    if self.year_fill >= (1+self.first_filling_year):
                        self.correction_annual = max((self._annual_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[5:12,scenario_index.global_id,self.year_index-1].mean(axis=0))/2),0) * (7+self.month_index+1)
                    else:
                        self.correction_annual = 0

                    if self.year_fill >= (4+self.first_filling_year):
                        self.correction_four_year = max((self._four_year_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-1].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-2].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-3].mean(axis=0) + self.previous_outflow_recorder[5:12,scenario_index.global_id,self.year_index-4].mean(axis=0))/5),0) * (7+self.month_index+1+36)
                    else:
                        self.correction_four_year = 0

                    if self.year_fill >= (5+self.first_filling_year):
                        self.correction_five_year = max((self._five_year_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-1].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-2].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-3].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-4].mean(axis=0) + self.previous_outflow_recorder[5:12,scenario_index.global_id,self.year_index-5].mean(axis=0))/6),0) * (7+self.month_index+1+48)
                    else:
                        self.correction_five_year = 0

                    self.correction =  max(self.correction_annual, self.correction_four_year, self.correction_five_year)

                elif self.model.timestepper.delta == "D":

                    if self.year_fill >= (1+self.first_filling_year):
                        self.correction_annual = max((self._annual_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.day_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[153:367,scenario_index.global_id,self.year_index-1].mean(axis=0))/2),0) * (214+self.day_index+1)
                    else:
                        self.correction_annual = 0

                    if self.year_fill >= (4+self.first_filling_year):
                        self.correction_four_year = max((self._four_year_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.day_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-1].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-2].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-3].mean(axis=0) + self.previous_outflow_recorder[153:367,scenario_index.global_id,self.year_index-4].mean(axis=0))/5),0) * (214+366*3+self.day_index+1)
                    else:
                        self.correction_four_year = 0

                    if self.year_fill >= (5+self.first_filling_year):
                        self.correction_five_year = max((self._five_year_release.get_value(scenario_index)/365.25 - (self.previous_outflow_recorder[0:self.day_index,scenario_index.global_id,self.year_index].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-1].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-2].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-3].mean(axis=0) + self.previous_outflow_recorder[:,scenario_index.global_id,self.year_index-4].mean(axis=0) + self.previous_outflow_recorder[153:367,scenario_index.global_id,self.year_index-5].mean(axis=0))/6),0) * (214+366*4+self.day_index+1)
                    else:
                        self.correction_five_year = 0

                    self.correction =  max(self.correction_annual, self.correction_four_year, self.correction_five_year)

                self.assignment_values[scenario_index.indices[0]] = min(max(max((self._long_term_outflow.get_value(scenario_index) + self.egypt_total_deficit[ts.index, scenario_index.global_id] + self.correction), 0), self._minimum_daily_release),500)
                self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                self.assignment_values3[scenario_index.indices[0]] = 0.1
            else:
                self.correction = 0

                self.assignment_values[scenario_index.indices[0]] = max(max((self._long_term_outflow.get_value(scenario_index) + self.egypt_total_deficit[ts.index, scenario_index.global_id] + self.correction), 0), self._minimum_daily_release)
            self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
            self.assignment_values3[scenario_index.indices[0]] = 0.1

            self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
            self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
            self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))
           
            self.min_volume = 24350
            return self.min_volume
            
    @classmethod
    def load(cls, model, data):
        inflow_node = model._get_node_from_ref(model, data.pop("inflow_node"))
        outflow_node = model._get_node_from_ref(model, data.pop("outflow_node"))
        outflow_constant_scenario_parameter = load_parameter(model, data.pop("outflow_constant_scenario_parameter"))
        Egypt_bypass_parameter = load_parameter(model, data.pop("Egypt_bypass_parameter"))
        storage_node = model._get_node_from_ref(model, data.pop("storage_node"))
        annual_release = load_parameter(model, data.pop("annual_release"))
        four_year_release = load_parameter(model, data.pop("four_year_release"))
        five_year_release = load_parameter(model, data.pop("five_year_release"))
        steady_state_storage = data.pop("steady_state_storage")
        minimum_daily_release = data.pop("minimum_daily_release")
        maximum_daily_release = data.pop("maximum_daily_release")
        ts_to_ts_max_change_in_outflow = data.pop("ts_to_ts_max_change_in_outflow")
        long_term_min_volume = data.pop("long_term_min_volume")
        first_filling_year_actual_volume = data.pop("first_filling_year_actual_volume")
        second_filling_year_actual_volume = data.pop("second_filling_year_actual_volume")
        long_term_outflow = load_parameter(model, data.pop("long_term_outflow"))
        if "first_filling_year" in data:
            first_filling_year = data.pop("first_filling_year")
        else:
            first_filling_year = 2020
        if "offset_years" in data:
            offset_years = data.pop("offset_years")
        else:
            offset_years = 0

        if "release_table_during_filling_csv" in data:
            release_table_during_filling_csv = data.pop("release_table_during_filling_csv")
        else:
            release_table_during_filling_csv = "data/Washington_filling_table.csv"

        if "release_table_during_operation_csv" in data:
            release_table_during_operation_csv = data.pop("release_table_during_operation_csv")
        else:
            release_table_during_operation_csv = "data/Washington_operation_table.csv"
        if "consider_release_tables_and_drought_meastures" in data:
            consider_release_tables_and_drought_meastures = data.pop("consider_release_tables_and_drought_meastures")
        else:
            consider_release_tables_and_drought_meastures = True
        if "save_intermediate_calculations" in data:
            save_intermediate_calculations = data.pop("save_intermediate_calculations")
        else:
            save_intermediate_calculations = True

        return cls(model, inflow_node, outflow_node, outflow_constant_scenario_parameter, Egypt_bypass_parameter,
        storage_node, annual_release, four_year_release, five_year_release, steady_state_storage, minimum_daily_release, maximum_daily_release,
        ts_to_ts_max_change_in_outflow, long_term_min_volume, long_term_outflow, first_filling_year, offset_years, first_filling_year_actual_volume,
        second_filling_year_actual_volume, release_table_during_filling_csv, release_table_during_operation_csv, consider_release_tables_and_drought_meastures,
        save_intermediate_calculations, **data)
WashingtonProposal.register()



class WashingtonProposalDetailed(Parameter):
    """ A parameter simulates the filling and long-term operation of the GERD.

    This parameter returns the min_volume for the GERD and also modifies other
    parameters that influence downstream dams. The parameter should be linked to
    GERD min_volume. The paramter is simulates a fraction-based filling rule for
    the GERD.

    inputs
    ----------
    type : a string "FlowFractionInitialFillingParameter"
    inflow_node : the node directly upstream of the GERD that provides the dam inflow
    outflow_constant_scenario_parameter : a ConstantScenarioParameter linked to the max_flow of 
                GERD control node. The values of this node are modified by this parameter to control
                GERD outflow during filling and long-term operation.
    Egypt_bypass_parameter : a ConstantScenarioParameter used to make sure that coordinated releases
                Between the GERD and HAD reaches Egypt. In other words, Egypt_bypass_parameter is added
                to water releases from the Roseires, Sennar, and Merowe dams to make sure that Sudan 
                does not use releases from the GERD that are meant for Egypt.
    storage_node : GERD reservoir node.
    annual_release : a number graeter than 0 represnts the minimum GERD release volume per year
    steady_state_storage : reservoir storage at which the steady-state operation starts
    long_term_min_volume : This is the long-term GERD dead storage of GERD once full. During the filling,
                the GERD is not allowed to fall below this level once reached.
    "minimum_daily_release": a minimum daily release value
    long_term_outflow : This is a parameter that provides the long-term GERD outflow. This is used to
                control GERD releases in the long-term after filling.

    Example
    -----------
      "GERD_min":{
         "type":"WashingtonProposal",
         "inflow_node":"C60",
         "outflow_constant_scenario_parameter": "GERD_outflow_control",
         "Egypt_bypass_parameter": "Egypt_bypass",
         "storage_node":"GERD",
         "steady_state_storage":49750,
         "annual_release":37000,
         "long_term_min_volume":15000,
         "minimum_daily_release":15,
         "long_term_outflow":"GERD_target_power_flow"
      },

    """

    def __init__(self, model, inflow_node, outflow_node, outflow_constant_scenario_parameter, 
    Egypt_bypass_parameter, storage_node, annual_release, four_year_release, five_year_release,
    steady_state_storage, minimum_daily_release, maximum_daily_release, ts_to_ts_max_change_in_outflow,
    long_term_min_volume, long_term_outflow, additional_flow_filling, first_filling_year,offset_years, first_filling_year_actual_volume,
    second_filling_year_actual_volume, release_table_during_filling_csv, release_table_during_operation_csv,
    consider_release_tables_and_drought_meastures, dynamically_updated_drought_thresholds, save_intermediate_calculations, **kwargs):
        super().__init__(model, **kwargs)
        self._inflow_node = inflow_node
        self._outflow_node = outflow_node
        self._outflow_constant_scenario_parameter = outflow_constant_scenario_parameter
        self._Egypt_bypass_parameter = Egypt_bypass_parameter
        self._storage_node = storage_node
        self._annual_release = None
        self.annual_release = annual_release
        self._four_year_release = None
        self.four_year_release = four_year_release
        self._five_year_release = None
        self.five_year_release = five_year_release
        self._steady_state_storage = steady_state_storage
        self._minimum_daily_release = minimum_daily_release
        self._maximum_daily_release = maximum_daily_release
        self._ts_to_ts_max_change_in_outflow = ts_to_ts_max_change_in_outflow
        self._long_term_min_volume = long_term_min_volume
        self._long_term_outflow = None
        self.long_term_outflow = long_term_outflow
        self._additional_flow_filling = None
        self.additional_flow_filling = additional_flow_filling
        self.egypt_irrigation_node1 = model._get_node_from_ref(model, "Egypt Irrigation")
        self.egypt_irrigation_node2 = model._get_node_from_ref(model, "Toshka Irrigation")
        self.egypt_municipal_node = model._get_node_from_ref(model, "Egypt Municipal")
        self._GERD_dummy_bypass_parameter = load_parameter(model, "GERD_dummy_bypass")
        self.first_filling_year = first_filling_year
        self.offset_years =offset_years
        self.first_filling_year_actual_volume = first_filling_year_actual_volume
        self.second_filling_year_actual_volume = second_filling_year_actual_volume
        self.release_table_during_filling_csv = release_table_during_filling_csv
        self.release_table_during_operation_csv = release_table_during_operation_csv
        self.consider_release_tables_and_drought_meastures = consider_release_tables_and_drought_meastures
        self.dynamically_updated_drought_thresholds = dynamically_updated_drought_thresholds
        self.save_intermediate_calculations = save_intermediate_calculations

    long_term_outflow = parameter_property("_long_term_outflow")
    additional_flow_filling = parameter_property("_additional_flow_filling")
    annual_release = parameter_property("_annual_release")
    four_year_release = parameter_property("_four_year_release")
    five_year_release = parameter_property("_five_year_release")

    def setup(self):
        super().setup()
        self.sc_size = 1
        self.sc_comb = len(self.model.scenarios.combinations)
        for m in range(len(self.model.scenarios.scenarios)):
            self.sc_size = self.sc_size * self.model.scenarios.scenarios[m].size
        self.n_ts = len(self.model.timestepper)
        self.nyears = self.model.timestepper.end.year - self.model.timestepper.start.year + 1

        self.volume_pc_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        #self.GERD_controlled_outflow = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        if self.model.timestepper.delta == "M":
            self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
            self.previous_inflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        elif self.model.timestepper.delta == "D":
            self.previous_outflow_recorder = np.zeros((366, self.sc_comb, self.nyears,), np.float64)
            self.previous_inflow_recorder = np.zeros((366, self.sc_comb, self.nyears,), np.float64)

        self.start_of_year_storage = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.past_four_year_release = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.past_five_year_release = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.past_year_inflow = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.additional_prolonged_drought_release = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.additional_prolonged_period_of_dry_years_release = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.drought_mechanisms_final_annual_release = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.drought_triggered = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.prolonged_drought_triggered = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.prolonged_of_dry_years_triggered = np.zeros((self.nyears, self.sc_comb,), np.float64)

        self.stage1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        for s in range(self.sc_comb):
            self.previous_outflow_recorder[0,s,0] = 100

        self.assignment_values = []
        self.assignment_values2 = []
        self.assignment_values3 = []
        for s in range(self.sc_size):
            self.assignment_values.append(100)
            self.assignment_values2.append(0)
            self.assignment_values3.append(0)

        self.filling_table = pd.read_csv(str(self.release_table_during_filling_csv)).set_index("GERD storage").to_numpy()
        self.operation_table = pd.read_csv(str(self.release_table_during_operation_csv)).set_index("GERD storage").to_numpy()

        self.inflow_1901_2001 = pd.read_csv("data/GERD_inflow_1901_2001.csv").set_index("Year")
        self.historical_inflow = np.zeros((self.nyears-1+len(self.inflow_1901_2001.index.to_list()), self.sc_comb,), np.float64)
        for y in range(len(self.inflow_1901_2001.index.to_list())):
            for s in range(self.sc_comb):
                self.historical_inflow[y,s] = self.inflow_1901_2001.at[y+1901,"GERD_inflow"]

        self.storage_axis2 = [49.3,46.2,43.1,40.1,37,33.9,
                              30.8,27.7,24.7,21.5,18.25]

        self.inflows_axis1 = [70,69,68,67,66,65,64,63,62,61,60,59,58,
                              57,56,55,54,53,52,51,50,49,48,47,46,45,
                              44,43,42,41,40,39,38,37,36,35,34,33,32,
                              31,30,29,28,27,26,25,24,23,22,21,20]

        self.q91 = np.zeros((self.sc_comb,), np.float64)
        self.q88 = np.zeros((self.sc_comb,), np.float64)
        self.q85 = np.zeros((self.sc_comb,), np.float64)
        for s in range(self.sc_comb):
            self.q91[s]=37000
            self.q88[s]=39000
            self.q85[s]=40000

        self.q91_values = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.q88_values = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.q85_values = np.zeros((self.nyears, self.sc_comb,), np.float64)

    def reset(self):
        self.volume_pc_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        #self.GERD_controlled_outflow = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        
        if self.model.timestepper.delta == "M":
            self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
            self.previous_inflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        elif self.model.timestepper.delta == "D":
            self.previous_outflow_recorder = np.zeros((366, self.sc_comb, self.nyears,), np.float64)
            self.previous_inflow_recorder = np.zeros((366, self.sc_comb, self.nyears,), np.float64)

        self.start_of_year_storage = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.past_four_year_release = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.past_five_year_release = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.past_year_inflow = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.additional_prolonged_drought_release = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.additional_prolonged_period_of_dry_years_release = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.drought_mechanisms_final_annual_release = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.drought_triggered = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.prolonged_drought_triggered = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.prolonged_of_dry_years_triggered = np.zeros((self.nyears, self.sc_comb,), np.float64)

        self.stage1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        for s in range(self.sc_comb):
            self.previous_outflow_recorder[0,s,0]=100

        self.inflow_1901_2001 = pd.read_csv("data/GERD_inflow_1901_2001.csv").set_index("Year")
        self.historical_inflow = np.zeros((self.nyears-1+len(self.inflow_1901_2001.index.to_list()), self.sc_comb,), np.float64)
        for y in range(len(self.inflow_1901_2001.index.to_list())):
            for s in range(self.sc_comb):
                self.historical_inflow[y,s] = self.inflow_1901_2001.at[y+1901,"GERD_inflow"]

        self.q91 = np.zeros((self.sc_comb,), np.float64)
        self.q88 = np.zeros((self.sc_comb,), np.float64)
        self.q85 = np.zeros((self.sc_comb,), np.float64)
        for s in range(self.sc_comb):
            self.q91[s]=37000
            self.q88[s]=39000
            self.q85[s]=40000

        self.q91_values = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.q88_values = np.zeros((self.nyears, self.sc_comb,), np.float64)
        self.q85_values = np.zeros((self.nyears, self.sc_comb,), np.float64)

    def interpolate_2D_release_table(self, inflow_values, storage_values, release_values, inflow, storage):
        f = interpolate.interp2d(inflow_values, storage_values, release_values, kind='linear')
        release = f(inflow, storage)
        return release

    def update_inflow_and_outflow(self, timestep, sc_index, iteration):
        #This method updates the previous inflow and outflow arrays, which are key to simulating the Washington Proposal
        if ((timestep.month != 1 and self.model.timestepper.delta == "M") or ((timestep.month + timestep.day > 2) and self.model.timestepper.delta == "D")) and iteration == 1:
            if self.model.timestepper.delta == "M":
                self.previous_outflow_recorder[self.month_index-1,sc_index.global_id,self.year_index] = self._outflow_node.prev_flow[sc_index.global_id]
                self.previous_inflow_recorder[self.month_index-1,sc_index.global_id,self.year_index] = self._inflow_node.prev_flow[sc_index.global_id]
            elif self.model.timestepper.delta == "D":
                self.previous_outflow_recorder[self.day_index-1,sc_index.global_id,self.year_index] = self._outflow_node.prev_flow[sc_index.global_id]
                self.previous_inflow_recorder[self.day_index-1,sc_index.global_id,self.year_index] = self._inflow_node.prev_flow[sc_index.global_id]
        elif timestep.index != 0 and iteration == 0:
            if self.model.timestepper.delta == "M":
                if timestep.month != 1:
                    self.previous_outflow_recorder[self.month_index-1,sc_index.global_id,self.year_index] = self._outflow_node.prev_flow[sc_index.global_id]
                    self.previous_inflow_recorder[self.month_index-1,sc_index.global_id,self.year_index] = self._inflow_node.prev_flow[sc_index.global_id]
                else:
                    self.previous_outflow_recorder[11,sc_index.global_id,self.year_index-1] = self._outflow_node.prev_flow[sc_index.global_id]
                    self.previous_inflow_recorder[11,sc_index.global_id,self.year_index-1] = self._inflow_node.prev_flow[sc_index.global_id]                    
            elif self.model.timestepper.delta == "D":
                if (timestep.month + timestep.day > 2):
                    self.previous_outflow_recorder[self.day_index-1,sc_index.global_id,self.year_index] = self._outflow_node.prev_flow[sc_index.global_id]
                    self.previous_inflow_recorder[self.day_index-1,sc_index.global_id,self.year_index] = self._inflow_node.prev_flow[sc_index.global_id]
                else:
                    self.previous_outflow_recorder[self.leap_year(timestep.year-1)[1]-1,sc_index.global_id,self.year_index-1] = self._outflow_node.prev_flow[sc_index.global_id]
                    self.previous_inflow_recorder[self.leap_year(timestep.year-1)[1]-1,sc_index.global_id,self.year_index-1] = self._inflow_node.prev_flow[sc_index.global_id]

    def update_drought_flows(self, timestep, sc_index):
        #This method calculates the four- and five-year average annual release. Here we also calculate the annual inflow. All these calculations are
        #based on the water year from July to June, according to the Washington Proposal
        if timestep.month == 7:
            if self.model.timestepper.delta == "M":
                if self.year_fill >= (4+self.first_filling_year):
                    self.past_four_year_release[self.year_index-1, sc_index.global_id] = ((self.previous_outflow_recorder[0:self.month_index,sc_index.global_id,self.year_index].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-1].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-2].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-3].sum(axis=0) + self.previous_outflow_recorder[6:12,sc_index.global_id,self.year_index-4].sum(axis=0)) * 30.5)/4
                if self.year_fill >= (5+self.first_filling_year):
                    self.past_five_year_release[self.year_index-1, sc_index.global_id] = ((self.previous_outflow_recorder[0:self.month_index,sc_index.global_id,self.year_index].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-1].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-2].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-3].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-4].sum(axis=0) + self.previous_outflow_recorder[6:12,sc_index.global_id,self.year_index-5].sum(axis=0)) * 30.5)/5
                if self.year_fill >= (1+self.first_filling_year):
                    self.past_year_inflow[self.year_index-1, sc_index.global_id] = (self.previous_inflow_recorder[0:self.month_index,sc_index.global_id,self.year_index].sum(axis=0) + self.previous_inflow_recorder[6:12,sc_index.global_id,self.year_index-1].sum(axis=0)) * 30.5
            elif self.model.timestepper.delta == "D" and timestep.day ==1:
                if self.year_fill >= (4+self.first_filling_year):
                    self.past_four_year_release[self.year_index-1, sc_index.global_id] = (self.previous_outflow_recorder[0:self.day_index,sc_index.global_id,self.year_index].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-1].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-2].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-3].sum(axis=0) + self.previous_outflow_recorder[self.leap_year(timestep.year-4)[0]:367,sc_index.global_id,self.year_index-4].sum(axis=0))/4
                if self.year_fill >= (5+self.first_filling_year):
                    self.past_five_year_release[self.year_index-1, sc_index.global_id] = (self.previous_outflow_recorder[0:self.day_index,sc_index.global_id,self.year_index].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-1].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-2].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-3].sum(axis=0) + self.previous_outflow_recorder[:,sc_index.global_id,self.year_index-4].sum(axis=0) + self.previous_outflow_recorder[self.leap_year(timestep.year-5)[0]:367,sc_index.global_id,self.year_index-5].sum(axis=0))/5
                if self.year_fill >= (1+self.first_filling_year):
                    self.past_year_inflow[self.year_index-1, sc_index.global_id] = self.previous_inflow_recorder[0:self.day_index,sc_index.global_id,self.year_index].sum(axis=0) + self.previous_inflow_recorder[self.leap_year(timestep.year-1)[0]:367,sc_index.global_id,self.year_index-1].sum(axis=0)

    def previous_ts_outlfow_calculator(self, timestep, sc_index):
        #This method calculates the four- and five-year average annual release. Here we also calculate the annual inflow. All these calculations are
        #based on the water year from July to June, according to the Washington Proposal
        if self.model.timestepper.delta == "M":
            if self.month_index == 0:
                if timestep.index != 0:
                    pre_ts_outflow = self.previous_outflow_recorder[11,sc_index.global_id,self.year_index-1]
                else:
                    pre_ts_outflow = 0
            else:
                pre_ts_outflow = self.previous_outflow_recorder[self.month_index-1,sc_index.global_id,self.year_index]
        elif self.model.timestepper.delta == "D":
            if self.day_index == 0:
                if timestep.index != 0:
                    pre_ts_outflow = self.previous_outflow_recorder[(self.leap_year(timestep.year-1)[1]-1),sc_index.global_id,self.year_index-1]
                else:
                    pre_ts_outflow = 0
            else:
                pre_ts_outflow = self.previous_outflow_recorder[self.day_index-1,sc_index.global_id,self.year_index]

        return pre_ts_outflow

    def leap_year(self, year):
        #This method is to determine whether a years leap or not
        #Then passes back the index of 1st July and the number of days in the year
        if (year % 4) == 0:
            if (year % 100) == 0:
                if (year % 400) == 0:
                    return 182, 366 #leap
                else:
                    return 181, 365 #not leap
            else:
                return 182, 366 #leap
        else:
            return 181, 365 # not leap

    #this method updates the drough mitigation thresholds of the Washington proposal based on unfolding hydrology
    def drought_values_update(self, timestep, sc_index):
        #Append past year infow to the historical inflows
        if self.model.timestepper.delta == "M":
            if timestep.month == 7 and self.year_index>0:
                self.historical_inflow[self.year_index+len(self.inflow_1901_2001.index.to_list())-1,sc_index.global_id] = (self.previous_inflow_recorder[0:self.month_index,sc_index.global_id,self.year_index].sum(axis=0)+self.previous_inflow_recorder[6:12,sc_index.global_id,self.year_index-1].sum(axis=0))* 30.5/1000
        elif self.model.timestepper.delta == "D":
            if timestep.month == 7 and timestep.day == 1 and self.year_index>0:
                self.historical_inflow[self.year_index+len(self.inflow_1901_2001.index.to_list())-1,sc_index.global_id] = (self.previous_inflow_recorder[0:self.day_index,sc_index.global_id,self.year_index].sum(axis=0) + self.previous_inflow_recorder[self.leap_year(timestep.year-1)[0]:367,sc_index.global_id,self.year_index-1].sum(axis=0))/1000

        # if True means dynamic drought threshold are in use
        if self.dynamically_updated_drought_thresholds:
            if timestep.month == 7 and self.year_index>0:
                #If less than 10 years, use the values in the Washingtom proposal
                if self.year_index<9:
                    self.q91[sc_index.global_id] = self._annual_release.get_value(sc_index)
                    self.q88[sc_index.global_id] = self._four_year_release.get_value(sc_index)
                    self.q85[sc_index.global_id] = self._five_year_release.get_value(sc_index)
                elif self.year_index==9 or self.year_index==19 or self.year_index==29 or self.year_index==39 or self.year_index==49 or self.year_index==59 or self.year_index==69 or self.year_index==79 or self.year_index==89 or self.year_index==99:
                    #update the drought thresholds using every ten years
                    inflow_historical_numpy_one_scenario = self.historical_inflow[0:self.year_index+1+len(self.inflow_1901_2001.index.to_list())-1,sc_index.global_id]
                    self.q91[sc_index.global_id] = np.ceil(np.quantile(inflow_historical_numpy_one_scenario, 0.09))*1000
                    self.q88[sc_index.global_id] = np.ceil(np.quantile(inflow_historical_numpy_one_scenario, 0.12))*1000
                    self.q85[sc_index.global_id] = np.ceil(np.quantile(inflow_historical_numpy_one_scenario, 0.15))*1000
        else:
            self.q91[sc_index.global_id] = self._annual_release.get_value(sc_index)
            self.q88[sc_index.global_id] = self._four_year_release.get_value(sc_index)
            self.q85[sc_index.global_id] = self._five_year_release.get_value(sc_index)

        #record the values to save is intermidate file saving is flagged as true
        self.q91_values[self.year_index, sc_index.global_id] = self.q91[sc_index.global_id]
        self.q88_values[self.year_index, sc_index.global_id] = self.q88[sc_index.global_id]
        self.q85_values[self.year_index, sc_index.global_id] = self.q85[sc_index.global_id]

    def value(self, ts, scenario_index):

        self.year_index = ts.year-self.model.timestepper.start.year
        self.year_fill = ts.year + self.offset_years
        self.month_index = ts.month-1
        self.day_index = ts.dayofyear-1
        self.correction = 0

        if ((ts.month != 1 and self.model.timestepper.delta == "M") or ((ts.month + ts.day > 2) and self.model.timestepper.delta == "D")) and self.iteration_check[ts.index, scenario_index.global_id]==1:
            
            self.volume_pc_recorder[ts.index, scenario_index.global_id] = self._storage_node.volume[scenario_index.global_id]

            #Here we store the storage in the last time step of June. This is used to determine planned releases according to the tables of the Washington Proposal
            if (ts.month == 7 and self.model.timestepper.delta == "M") or ((ts.month == 7 and ts.day == 1) and self.model.timestepper.delta == "D"):
                self.start_of_year_storage[self.year_index, scenario_index.global_id] = self._storage_node.volume[scenario_index.global_id]

            self._max_flow_irr1[ts.index, scenario_index.global_id] = self.egypt_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_irr2[ts.index, scenario_index.global_id] = self.egypt_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_muni[ts.index, scenario_index.global_id] = self.egypt_municipal_node.get_max_flow(scenario_index)

            self.update_inflow_and_outflow(timestep = ts, sc_index = scenario_index, iteration = self.iteration_check[ts.index, scenario_index.global_id])

            self.egypt_irrigation_deficit = max((self._max_flow_irr1[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node1.prev_flow[scenario_index.global_id]),0)+max((self._max_flow_irr2[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node2.prev_flow[scenario_index.global_id]),0)
            self.egypt_municipal_deficit = max((self._max_flow_muni[ts.index-1, scenario_index.global_id] - self.egypt_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.egypt_total_deficit[ts.index, scenario_index.global_id] = (self.egypt_irrigation_deficit + self.egypt_municipal_deficit)/0.9

        if ts.index != 0 and self.iteration_check[ts.index, scenario_index.global_id]==0:

            self.volume_pc_recorder[ts.index, scenario_index.global_id] = self._storage_node.volume[scenario_index.global_id]

            #Here we store the storage in the last time step of June. This is used to determine planned releases according to the tables of the Washington Proposal
            if (ts.month == 7 and self.model.timestepper.delta == "M") or ((ts.month == 7 and ts.day == 1) and self.model.timestepper.delta == "D"):
                self.start_of_year_storage[self.year_index, scenario_index.global_id] = self._storage_node.volume[scenario_index.global_id]

            self._max_flow_irr1[ts.index, scenario_index.global_id] = self.egypt_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_irr2[ts.index, scenario_index.global_id] = self.egypt_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_muni[ts.index, scenario_index.global_id] = self.egypt_municipal_node.get_max_flow(scenario_index)

            self.update_inflow_and_outflow(timestep = ts, sc_index = scenario_index, iteration = self.iteration_check[ts.index, scenario_index.global_id])

            self.egypt_irrigation_deficit = max((self._max_flow_irr1[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node1.prev_flow[scenario_index.global_id]),0)+max((self._max_flow_irr2[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node2.prev_flow[scenario_index.global_id]),0)
            self.egypt_municipal_deficit = max((self._max_flow_muni[ts.index-1, scenario_index.global_id] - self.egypt_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.egypt_total_deficit[ts.index, scenario_index.global_id] = (self.egypt_irrigation_deficit + self.egypt_municipal_deficit)/0.9
            
            self.iteration_check[ts.index, scenario_index.global_id] = 1


        if self.year_fill >= self.first_filling_year and ts.index != 0:
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.first_filling_year_actual_volume and self.stage1[ts.index-1, scenario_index.global_id] != 3:
                self.stage1[ts.index, scenario_index.global_id] = 1
            else:
                self.stage1[ts.index, scenario_index.global_id] = 0
            if ts.month == 7 and self.stage1[ts.index-1, scenario_index.global_id] == 1:
                self.stage1[ts.index, scenario_index.global_id] = 3
            if self.stage1[ts.index-1, scenario_index.global_id] == 3:
                self.stage1[ts.index, scenario_index.global_id] = 3
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.second_filling_year_actual_volume and self.stage2[ts.index-1, scenario_index.global_id] != 3:
                self.stage2[ts.index, scenario_index.global_id] = 1
            else:
                self.stage2[ts.index, scenario_index.global_id] = 0
            if ts.month == 7 and self.stage2[ts.index-1, scenario_index.global_id] == 1:
                self.stage2[ts.index, scenario_index.global_id] = 3
            if self.stage2[ts.index-1, scenario_index.global_id] == 3:
                self.stage2[ts.index, scenario_index.global_id] = 3

        self.drought_values_update(timestep = ts, sc_index = scenario_index)

        """
        The follwoing equation is used to activate or deactivate coordination of operation between
        the GERD and the HAD. Coordination implies that the GERD makes extra releases to satisfy water
        deficits in Egypt. To activate coordiation hash out the eqation below
        """
        self.egypt_total_deficit[ts.index, scenario_index.global_id] = 0

        if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) <= 0.99 * self._steady_state_storage:

            """
            The part within the "if" statement is for the intial filling.
            """

            """
            The "if" statement below is added to simulate the GERD filling stages for stability and
            turbines testing. Once the GERD reaches a stage, it is not allowed to go lower.
            """
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= 24350:
                self.min_volume = 24350
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self._long_term_min_volume and self.stage1[ts.index, scenario_index.global_id] != 1:
                self.min_volume = self._long_term_min_volume     
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.second_filling_year_actual_volume:
                self.min_volume = self.second_filling_year_actual_volume
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= 4900:
                self.min_volume = 4900
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.first_filling_year_actual_volume:
                self.min_volume = self.first_filling_year_actual_volume
            else:
                self.min_volume = 10


            # Under the following "if" statement we caculate the additional releases needed to mitigate droughts according to four-year past average annual releases
            if ts.month == 7:
                self.update_drought_flows(timestep = ts, sc_index = scenario_index)
                if self.year_fill >= (4+self.first_filling_year):
                    self.prolonged_drought_triggered[self.year_index-1, scenario_index.global_id] = 0
                    if self.past_four_year_release[self.year_index-1, scenario_index.global_id] < self._annual_release.get_value(scenario_index):
                        self.prolonged_drought_triggered[self.year_index-1, scenario_index.global_id] = 1
                        storage_after_considering_committed_releases = self.start_of_year_storage[self.year_index, scenario_index.global_id] - self.drought_mechanisms_final_annual_release[self.year_index+1:self.nyears+1, scenario_index.global_id].sum(axis=0)
                        self.additional_prolonged_drought_release[self.year_index, scenario_index.global_id] = max((storage_after_considering_committed_releases - 24350) * 0.625,0)
                        for year in [self.year_index + 1, self.year_index + 2, self.year_index + 3, self.year_index + 4]:
                            if year <= self.nyears-1:
                                self.drought_mechanisms_final_annual_release[year, scenario_index.global_id] = max (self.drought_mechanisms_final_annual_release[year, scenario_index.global_id], self.additional_prolonged_drought_release[self.year_index, scenario_index.global_id]/4)

                if self.year_fill >= (4+self.first_filling_year):
                    self.prolonged_drought_triggered[self.year_index-1, scenario_index.global_id] = 0
                    if self.past_four_year_release[self.year_index-1, scenario_index.global_id] < self._five_year_release.get_value(scenario_index):
                        self.prolonged_of_dry_years_triggered[self.year_index-1, scenario_index.global_id] = 1
                        storage_after_considering_committed_releases = self.start_of_year_storage[self.year_index, scenario_index.global_id] - self.drought_mechanisms_final_annual_release[self.year_index+1:self.nyears+1, scenario_index.global_id].sum(axis=0)
                        self.additional_prolonged_period_of_dry_years_release[self.year_index, scenario_index.global_id] = max((storage_after_considering_committed_releases - 24350) * 0.5,0)
                        for year in [self.year_index + 1, self.year_index + 2, self.year_index + 3, self.year_index + 4]:
                            if year <= self.nyears-1:
                                self.drought_mechanisms_final_annual_release[year, scenario_index.global_id] = max (self.drought_mechanisms_final_annual_release[year, scenario_index.global_id], self.additional_prolonged_period_of_dry_years_release[self.year_index, scenario_index.global_id]/4)

            # Under this "if" statement, we perfrom water retention which is limitted to the months of Jule and August
            if ts.month == 7 or ts.month == 8:

                if self.stage1[ts.index, scenario_index.global_id] == 1 or self.stage2[ts.index, scenario_index.global_id] == 1:
                    self.assignment_values[scenario_index.indices[0]] = 10000
                    self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                    self.assignment_values3[scenario_index.indices[0]] = 10000

                    self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                    self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                    self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))
                else:
                    self.assignment_values[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id] + self._minimum_daily_release
                    self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                    self.assignment_values3[scenario_index.indices[0]] = 0.1

                    self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                    self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                    self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))
            else:
                if self.stage1[ts.index, scenario_index.global_id] == 1 or self.stage2[ts.index, scenario_index.global_id] == 1:
                    self.assignment_values[scenario_index.indices[0]] = 10000
                    self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                    self.assignment_values3[scenario_index.indices[0]] = 10000

                    self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                    self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                    self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))
                else:
                    # Under this "if" statement, we perform water release correction in certain months to make sure that teh release conforms with
                    # the release tables of the proposal in addition to drought mitigation releases, taking into account planned environmetal releases
                    if ts.month == 3 or ts.month == 4 or ts.month == 5 or ts.month == 6:
                        if self.year_fill >= (1+self.first_filling_year):
                            if self.model.timestepper.delta == "M":
                                planned_drought_mitigation_flow = self.drought_mechanisms_final_annual_release[self.year_index, scenario_index.global_id]
                                this_year_inflow_so_far = (self.previous_inflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].sum(axis=0) + self.previous_inflow_recorder[6:12,scenario_index.global_id,self.year_index-1].sum(axis=0)) * 30.5

                                self.drought_triggered[self.year_index-1, scenario_index.global_id] = 0
                                if this_year_inflow_so_far < self._annual_release.get_value(scenario_index):
                                    self.drought_triggered[self.year_index-1, scenario_index.global_id] = 1
                                    this_year_storage = self.start_of_year_storage[self.year_index-1, scenario_index.global_id] - self.drought_mechanisms_final_annual_release[self.year_index:self.nyears+1, scenario_index.global_id].sum(axis=0)
                                else:
                                    this_year_storage = self.start_of_year_storage[self.year_index-1, scenario_index.global_id]

                                this_year_outflow_so_far = (self.previous_outflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].sum(axis=0) + self.previous_outflow_recorder[6:12,scenario_index.global_id,self.year_index-1].sum(axis=0)) * 30.5
                                previous_ts_outflow = self.previous_ts_outlfow_calculator(timestep = ts, sc_index = scenario_index)
                                this_year_planned_outflow = self.interpolate_2D_release_table(storage_values = self.storage_axis2, inflow_values = self.inflows_axis1,
                                                            release_values = self.filling_table, inflow = this_year_inflow_so_far/1000, storage = this_year_storage/1000)[0]*1000
                                self.correction = (this_year_planned_outflow - this_year_outflow_so_far + planned_drought_mitigation_flow)/30.5
                            elif self.model.timestepper.delta == "D":
                                planned_drought_mitigation_flow = self.drought_mechanisms_final_annual_release[self.year_index, scenario_index.global_id]
                                this_year_inflow_so_far = (self.previous_inflow_recorder[0:self.day_index,scenario_index.global_id,self.year_index].sum(axis=0) + self.previous_inflow_recorder[self.leap_year(ts.year-1)[0]:367,scenario_index.global_id,self.year_index-1].sum(axis=0))

                                self.drought_triggered[self.year_index-1, scenario_index.global_id] = 0
                                if this_year_inflow_so_far < self._annual_release.get_value(scenario_index):
                                    self.drought_triggered[self.year_index-1, scenario_index.global_id] = 1
                                    this_year_storage = self.start_of_year_storage[self.year_index-1, scenario_index.global_id] - self.drought_mechanisms_final_annual_release[self.year_index:self.nyears+1, scenario_index.global_id].sum(axis=0)
                                else:
                                    this_year_storage = self.start_of_year_storage[self.year_index-1, scenario_index.global_id]

                                this_year_outflow_so_far = (self.previous_outflow_recorder[0:self.day_index,scenario_index.global_id,self.year_index].sum(axis=0) + self.previous_outflow_recorder[self.leap_year(ts.year-1)[0]:367,scenario_index.global_id,self.year_index-1].sum(axis=0))
                                previous_ts_outflow = self.previous_ts_outlfow_calculator(timestep = ts, sc_index = scenario_index)
                                this_year_planned_outflow = self.interpolate_2D_release_table(storage_values = self.storage_axis2, inflow_values = self.inflows_axis1,
                                                            release_values = self.filling_table, inflow = this_year_inflow_so_far/1000, storage = this_year_storage/1000)[0]*1000
                                self.correction = this_year_planned_outflow - this_year_outflow_so_far + planned_drought_mitigation_flow

                        else:
                            self.correction = 0
                            
                        previous_ts_outflow = self.previous_ts_outlfow_calculator(timestep = ts, sc_index = scenario_index)

                        if self.consider_release_tables_and_drought_meastures:
                            pass
                        else:
                            self.correction = 0
                            
                        self.assignment_values[scenario_index.indices[0]] = min(max(min(self.correction,(previous_ts_outflow+self._ts_to_ts_max_change_in_outflow)), (previous_ts_outflow-self._ts_to_ts_max_change_in_outflow), 0), self._maximum_daily_release) + self._additional_flow_filling.get_value(scenario_index)
                        self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                        self.assignment_values3[scenario_index.indices[0]] = 10000
                    else:
                        self.correction = 0
                        previous_ts_outflow = self.previous_ts_outlfow_calculator(timestep = ts, sc_index = scenario_index)
                        
                        self.assignment_values[scenario_index.indices[0]] = max(self.correction, 0)
                        self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                        self.assignment_values3[scenario_index.indices[0]] = 10000

                    self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                    self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                    self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))

            #self.GERD_controlled_outflow[ts.index, scenario_index.global_id] = self.assignment_values[scenario_index.indices[0]]
            return self.min_volume
        else:
            """
            The part within this "else" simulates long-term operation.
            """
            # Under the following "if" statement we caculate the additional releases needed to mitigate droughts according to the five- and four- year past average annual releases
            if ts.month == 7:
                self.update_drought_flows(timestep = ts, sc_index = scenario_index)
                if self.year_fill >= (4+self.first_filling_year):
                    self.prolonged_drought_triggered[self.year_index-1, scenario_index.global_id] = 0
                    if self.past_four_year_release[self.year_index-1, scenario_index.global_id] < self.q88[scenario_index.global_id]:
                        self.prolonged_drought_triggered[self.year_index-1, scenario_index.global_id] = 1
                        storage_after_considering_committed_releases = self.start_of_year_storage[self.year_index, scenario_index.global_id] - self.drought_mechanisms_final_annual_release[self.year_index+1:self.nyears+1, scenario_index.global_id].sum(axis=0)
                        self.additional_prolonged_drought_release[self.year_index, scenario_index.global_id] = max((storage_after_considering_committed_releases - 24350) * 1,0)
                        for year in [self.year_index + 1, self.year_index + 2, self.year_index + 3, self.year_index + 4]:
                            if year <= self.nyears-1:
                                self.drought_mechanisms_final_annual_release[year, scenario_index.global_id] = max (self.drought_mechanisms_final_annual_release[year, scenario_index.global_id], self.additional_prolonged_drought_release[self.year_index, scenario_index.global_id]/4)

                if self.year_fill >= (5+self.first_filling_year):
                    self.prolonged_of_dry_years_triggered[self.year_index-1, scenario_index.global_id] = 0
                    if self.past_five_year_release[self.year_index-1, scenario_index.global_id] < self.q85[scenario_index.global_id]:
                        self.prolonged_of_dry_years_triggered[self.year_index-1, scenario_index.global_id] = 1
                        storage_after_considering_committed_releases = self.start_of_year_storage[self.year_index, scenario_index.global_id] - self.drought_mechanisms_final_annual_release[self.year_index+1:self.nyears+1, scenario_index.global_id].sum(axis=0)
                        self.additional_prolonged_period_of_dry_years_release[self.year_index, scenario_index.global_id] = max((storage_after_considering_committed_releases - 24350) * 1,0)
                        for year in [self.year_index + 1, self.year_index + 2, self.year_index + 3, self.year_index + 4, self.year_index + 5]:
                            if year <= self.nyears-1:
                                self.drought_mechanisms_final_annual_release[year, scenario_index.global_id] = max (self.drought_mechanisms_final_annual_release[year, scenario_index.global_id], self.additional_prolonged_period_of_dry_years_release[self.year_index, scenario_index.global_id]/5)
            
            # Under this "if" statement, we perform water release correction in certain months to make sure that teh release conforms with
            # the release tables of the proposal in addition to drought mitigation releases, taking into account planned environmetal releases
            if ts.month == 3 or ts.month == 4 or ts.month == 5 or ts.month == 6:
                if self.year_fill >= (1+self.first_filling_year):
                    if self.model.timestepper.delta == "M":
                        planned_minimum_flow = max((self._minimum_daily_release*(6-self.month_index)*30.5),0)
                        planned_drought_mitigation_flow = self.drought_mechanisms_final_annual_release[self.year_index, scenario_index.global_id]
                        this_year_inflow_so_far = (self.previous_inflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].sum(axis=0) + self.previous_inflow_recorder[6:12,scenario_index.global_id,self.year_index-1].sum(axis=0)) * 30.5
                        # Here storage is corrected and reduced in calculating drought releases for inflows below 37 bcm. See Exhibit B, Annex A, part IV of the Washington Porposal
                        self.drought_triggered[self.year_index-1, scenario_index.global_id] = 0
                        if this_year_inflow_so_far < self.q91[scenario_index.global_id]:
                            self.drought_triggered[self.year_index-1, scenario_index.global_id] = 1
                            this_year_storage = self.start_of_year_storage[self.year_index-1, scenario_index.global_id] - self.drought_mechanisms_final_annual_release[self.year_index:self.nyears+1, scenario_index.global_id].sum(axis=0)
                        else:
                            this_year_storage = self.start_of_year_storage[self.year_index-1, scenario_index.global_id]
                        this_year_outflow_so_far = (self.previous_outflow_recorder[0:self.month_index,scenario_index.global_id,self.year_index].sum(axis=0) + self.previous_outflow_recorder[6:12,scenario_index.global_id,self.year_index-1].sum(axis=0)) * 30.5
                        this_year_planned_outflow = self.interpolate_2D_release_table(storage_values = self.storage_axis2, inflow_values = self.inflows_axis1,
                                                    release_values = self.operation_table, inflow = this_year_inflow_so_far/1000, storage = this_year_storage/1000)[0]*1000
                        self.correction = (this_year_planned_outflow - this_year_outflow_so_far - planned_minimum_flow + planned_drought_mitigation_flow)/30.5
                    elif self.model.timestepper.delta == "D":
                        planned_minimum_flow = max((self._minimum_daily_release*(self.leap_year(ts.year)[0]-self.day_index)),0)
                        planned_drought_mitigation_flow = self.drought_mechanisms_final_annual_release[self.year_index, scenario_index.global_id]
                        this_year_inflow_so_far = (self.previous_inflow_recorder[0:self.day_index,scenario_index.global_id,self.year_index].sum(axis=0) + self.previous_inflow_recorder[self.leap_year(ts.year-1)[0]:367,scenario_index.global_id,self.year_index-1].sum(axis=0))
                        # Here storage is corrected and reduced in calculating drought releases for inflows below 37 bcm. See Exhibit B, Annex A, part IV of the Washington Porposal
                        self.drought_triggered[self.year_index-1, scenario_index.global_id] = 0
                        if this_year_inflow_so_far < self.q91[scenario_index.global_id]:
                            self.drought_triggered[self.year_index-1, scenario_index.global_id] = 1
                            this_year_storage = self.start_of_year_storage[self.year_index-1, scenario_index.global_id] - self.drought_mechanisms_final_annual_release[self.year_index:self.nyears+1, scenario_index.global_id].sum(axis=0)
                        else:
                            this_year_storage = self.start_of_year_storage[self.year_index-1, scenario_index.global_id]
                        this_year_outflow_so_far = (self.previous_outflow_recorder[0:self.day_index,scenario_index.global_id,self.year_index].sum(axis=0) + self.previous_outflow_recorder[self.leap_year(ts.year-1)[0]:367,scenario_index.global_id,self.year_index-1].sum(axis=0))
                        this_year_planned_outflow = self.interpolate_2D_release_table(storage_values = self.storage_axis2, inflow_values = self.inflows_axis1,
                                                    release_values = self.operation_table, inflow = this_year_inflow_so_far/1000, storage = this_year_storage/1000)[0]*1000 
                        self.correction = this_year_planned_outflow - this_year_outflow_so_far - planned_minimum_flow + planned_drought_mitigation_flow
                else:
                    self.correction = 0

                previous_ts_outflow = self.previous_ts_outlfow_calculator(timestep = ts, sc_index = scenario_index)
                
                if self.consider_release_tables_and_drought_meastures:
                    pass
                else:
                    self.correction = 0
                    
                self.assignment_values[scenario_index.indices[0]] = min(max(min((self._long_term_outflow.get_value(scenario_index) + self.correction),(previous_ts_outflow+self._ts_to_ts_max_change_in_outflow)), self._minimum_daily_release, (previous_ts_outflow-self._ts_to_ts_max_change_in_outflow), 0), self._maximum_daily_release)
                self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                self.assignment_values3[scenario_index.indices[0]] = 0.1
            else:
                previous_ts_outflow = self.previous_ts_outlfow_calculator(timestep = ts, sc_index = scenario_index)
                self.correction = 0

                self.assignment_values[scenario_index.indices[0]] = min(max(min((self._long_term_outflow.get_value(scenario_index) + self.correction),(previous_ts_outflow+self._ts_to_ts_max_change_in_outflow)), self._minimum_daily_release, (previous_ts_outflow-self._ts_to_ts_max_change_in_outflow), 0), self._maximum_daily_release)
                self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id]
                self.assignment_values3[scenario_index.indices[0]] = 0.1

            self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
            self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
            self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))

            # Here we save some outputs at the end of the simulation
            #self.GERD_controlled_outflow[ts.index, scenario_index.global_id] = self.assignment_values[scenario_index.indices[0]]
            if scenario_index.global_id == (self.sc_comb-1) and ts.year == self.model.timestepper.end.year and ts.month == self.model.timestepper.end.month and ts.day == self.model.timestepper.end.day and self.save_intermediate_calculations:
                path = os.path.join(os.getcwd(),"outputs")
                os.makedirs(path, exist_ok=True)
                df_out = pd.DataFrame(data = self.drought_mechanisms_final_annual_release, dtype = float)
                df_out.to_csv(str(path+"/"+str('drought_mechanisms_final_annual_release.csv')))
                df_out = pd.DataFrame(data = self.start_of_year_storage, dtype = float)
                df_out.to_csv(str(path+"/"+str('start_of_year_storage.csv')))
                df_out = pd.DataFrame(data = self.past_four_year_release, dtype = float)
                df_out.to_csv(str(path+"/"+str('past_four_year_release.csv')))
                df_out = pd.DataFrame(data = self.past_five_year_release, dtype = float)
                df_out.to_csv(str(path+"/"+str('past_five_year_release.csv')))
                df_out = pd.DataFrame(data = self.past_year_inflow, dtype = float)
                df_out.to_csv(str(path+"/"+str('past_year_inflow.csv')))
                df_out = pd.DataFrame(data = self.drought_triggered, dtype = float)
                df_out.to_csv(str(path+"/"+str('drought_triggered.csv')))
                df_out = pd.DataFrame(data = self.prolonged_drought_triggered, dtype = float)
                df_out.to_csv(str(path+"/"+str('prolonged_drought_triggered.csv')))
                df_out = pd.DataFrame(data = self.prolonged_of_dry_years_triggered, dtype = float)
                df_out.to_csv(str(path+"/"+str('prolonged_of_dry_years_triggered.csv')))
                df_out = pd.DataFrame(data = self.q91_values, dtype = float)
                df_out.to_csv(str(path+"/"+str('q91_values.csv')))
                df_out = pd.DataFrame(data = self.q88_values, dtype = float)
                df_out.to_csv(str(path+"/"+str('q88_values.csv')))
                df_out = pd.DataFrame(data = self.q85_values, dtype = float)
                df_out.to_csv(str(path+"/"+str('q85_values.csv')))
                #df_out = pd.DataFrame(data = self.GERD_controlled_outflow, dtype = float)
                #df_out.to_csv(str(path+"/"+str('GERD_controlled_outflow.csv')))

            self.min_volume = 24350
            return self.min_volume
            
    @classmethod
    def load(cls, model, data):
        inflow_node = model._get_node_from_ref(model, data.pop("inflow_node"))
        outflow_node = model._get_node_from_ref(model, data.pop("outflow_node"))
        outflow_constant_scenario_parameter = load_parameter(model, data.pop("outflow_constant_scenario_parameter"))
        Egypt_bypass_parameter = load_parameter(model, data.pop("Egypt_bypass_parameter"))
        storage_node = model._get_node_from_ref(model, data.pop("storage_node"))
        annual_release = load_parameter(model, data.pop("annual_release"))
        four_year_release = load_parameter(model, data.pop("four_year_release"))
        five_year_release = load_parameter(model, data.pop("five_year_release"))
        steady_state_storage = data.pop("steady_state_storage")
        minimum_daily_release = data.pop("minimum_daily_release")
        maximum_daily_release = data.pop("maximum_daily_release")
        ts_to_ts_max_change_in_outflow = data.pop("ts_to_ts_max_change_in_outflow")
        long_term_min_volume = data.pop("long_term_min_volume")
        first_filling_year_actual_volume = data.pop("first_filling_year_actual_volume")
        second_filling_year_actual_volume = data.pop("second_filling_year_actual_volume")
        long_term_outflow = load_parameter(model, data.pop("long_term_outflow"))

        if "additional_flow_filling" in data:
            additional_flow_filling = load_parameter(model, data.pop("additional_flow_filling"))
        else:
            additional_flow_filling = None

        if "first_filling_year" in data:
            first_filling_year = data.pop("first_filling_year")
        else:
            first_filling_year = 2020
        if "offset_years" in data:
            offset_years = data.pop("offset_years")
        else:
            offset_years = 0

        if "release_table_during_filling_csv" in data:
            release_table_during_filling_csv = data.pop("release_table_during_filling_csv")
        else:
            release_table_during_filling_csv = "data/Washington_filling_table.csv"

        if "release_table_during_operation_csv" in data:
            release_table_during_operation_csv = data.pop("release_table_during_operation_csv")
        else:
            release_table_during_operation_csv = "data/Washington_operation_table.csv"
        if "consider_release_tables_and_drought_meastures" in data:
            consider_release_tables_and_drought_meastures = data.pop("consider_release_tables_and_drought_meastures")
        else:
            consider_release_tables_and_drought_meastures = True
        if "dynamically_updated_drought_thresholds" in data:
            dynamically_updated_drought_thresholds = data.pop("dynamically_updated_drought_thresholds")
        else:
            dynamically_updated_drought_thresholds = False
        if "save_intermediate_calculations" in data:
            save_intermediate_calculations = data.pop("save_intermediate_calculations")
        else:
            save_intermediate_calculations = True

        return cls(model, inflow_node, outflow_node, outflow_constant_scenario_parameter, Egypt_bypass_parameter,
        storage_node, annual_release, four_year_release, five_year_release, steady_state_storage, minimum_daily_release, maximum_daily_release,
        ts_to_ts_max_change_in_outflow, long_term_min_volume, long_term_outflow, additional_flow_filling, first_filling_year, offset_years, first_filling_year_actual_volume,
        second_filling_year_actual_volume, release_table_during_filling_csv, release_table_during_operation_csv, consider_release_tables_and_drought_meastures, dynamically_updated_drought_thresholds,
        save_intermediate_calculations, **data)
WashingtonProposalDetailed.register()


class OpportunisticFilling(Parameter):
    """ A parameter simulates the filling and long-term operation of the GERD.

    This parameter returns the min_volume for the GERD and also modifies other
    parameters that influence downstream dams. The parameter should be linked to
    GERD min_volume. The paramter is simulates a fraction-based filling rule for
    the GERD.

    inputs
    ----------
    type : a string "FlowFractionInitialFillingParameter"
    inflow_node : the node directly upstream of the GERD that provides the dam inflow
    outflow_constant_scenario_parameter : a ConstantScenarioParameter linked to the max_flow of 
                GERD control node. The values of this node are modified by this parameter to control
                GERD outflow during filling and long-term operation.
    Egypt_bypass_parameter : a ConstantScenarioParameter used to make sure that coordinated releases
                Between the GERD and HAD reaches Egypt. In other words, Egypt_bypass_parameter is added
                to water releases from the Roseires, Sennar, and Merowe dams to make sure that Sudan 
                does not use releases from the GERD that are meant for Egypt.
    storage_node : GERD reservoir node.
    annual_release : a number graeter than 0 represnts the minimum GERD release volume per year
    steady_state_storage : reservoir storage at which the steady-state operation starts
    long_term_min_volume : This is the long-term GERD dead storage of GERD once full. During the filling,
                the GERD is not allowed to fall below this level once reached.
    "minimum_daily_release": a minimum daily release value
    long_term_outflow : This is a parameter that provides the long-term GERD outflow. This is used to
                control GERD releases in the long-term after filling.

    Example
    -----------
      "GERD_min":{
         "type":"FlowFractionInitialFillingParameter",
         "inflow_node":"C60",
         "outflow_constant_scenario_parameter": "GERD_outflow_control",
         "Egypt_bypass_parameter": "Egypt_bypass",
         "storage_node":"GERD",
         "steady_state_storage":49750,
         "annual_release":37000,
         "long_term_min_volume":15000,
         "minimum_daily_release":15,
         "long_term_outflow":"GERD_target_power_flow"
      },

    """

    def __init__(self, model, inflow_node, outflow_node, outflow_constant_scenario_parameter, 
    Egypt_bypass_parameter, storage_node, annual_release, four_year_release, five_year_release,
    steady_state_storage, minimum_daily_release, maximum_daily_release, ts_to_ts_max_change_in_outflow,
    long_term_min_volume, long_term_outflow, first_filling_year,offset_years, first_filling_year_actual_volume,
    second_filling_year_actual_volume, release_table_during_filling_csv, release_table_during_operation_csv,
    consider_release_tables_and_drought_meastures, save_intermediate_calculations, **kwargs):
        super().__init__(model, **kwargs)
        self._inflow_node = inflow_node
        self._outflow_node = outflow_node
        self._outflow_constant_scenario_parameter = outflow_constant_scenario_parameter
        self._Egypt_bypass_parameter = Egypt_bypass_parameter
        self._storage_node = storage_node
        self._annual_release = None
        self.annual_release = annual_release
        self._four_year_release = None
        self.four_year_release = four_year_release
        self._five_year_release = None
        self.five_year_release = five_year_release
        self._steady_state_storage = steady_state_storage
        self._minimum_daily_release = minimum_daily_release
        self._long_term_min_volume = long_term_min_volume
        self._long_term_outflow = None
        self.long_term_outflow = long_term_outflow
        self.egypt_irrigation_node1 = model._get_node_from_ref(model, "Egypt Irrigation")
        self.egypt_irrigation_node2 = model._get_node_from_ref(model, "Toshka Irrigation")
        self.egypt_municipal_node = model._get_node_from_ref(model, "Egypt Municipal")
        self.sudan_irrigation_node1 = model._get_node_from_ref(model, "Rahad Irrigation")
        self.sudan_irrigation_node2 = model._get_node_from_ref(model, "Suki_and_NW_Sennar Irrigation")
        self.sudan_irrigation_node3 = model._get_node_from_ref(model, "Gezira Managil Irrigation")
        self.sudan_irrigation_node4 = model._get_node_from_ref(model, "Gunied Irrigation")
        self.sudan_municipal_node = model._get_node_from_ref(model, "Khartoum Municipal")
        self._GERD_dummy_bypass_parameter = load_parameter(model, "GERD_dummy_bypass")
        self.High_Aswan_Dam = model._get_node_from_ref(model, "HAD")
        self.first_filling_year = first_filling_year
        self.offset_years =offset_years
        self.first_filling_year_actual_volume = first_filling_year_actual_volume
        self.second_filling_year_actual_volume = second_filling_year_actual_volume

        #This is the percentage support of GERD to HAD from water deficits and demands
        self.support_factor = 0.45

    long_term_outflow = parameter_property("_long_term_outflow")
    annual_release = parameter_property("_annual_release")
    four_year_release = parameter_property("_four_year_release")
    five_year_release = parameter_property("_five_year_release")

    def setup(self):
        super().setup()
        self.sc_size = 1
        self.sc_comb = len(self.model.scenarios.combinations)
        for m in range(len(self.model.scenarios.scenarios)):
            self.sc_size = self.sc_size * self.model.scenarios.scenarios[m].size
        self.n_ts = len(self.model.timestepper)
        self.nyears = self.model.timestepper.end.year - self.model.timestepper.start.year + 1

        self.volume_pc_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr3 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr4 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_demand = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.sudan_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.sudan_total_demand = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        self.previous_inflow_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.HAD_storage = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        for s in range(self.sc_comb):
            self.previous_outflow_recorder[0,s,0] = 100
            self.HAD_storage[0,s] = 149500

        self.assignment_values = []
        self.assignment_values2 = []
        self.assignment_values3 = []
        for s in range(self.sc_size):
            self.assignment_values.append(100)
            self.assignment_values2.append(0)
            self.assignment_values3.append(0)

    def reset(self):
        self.volume_pc_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr3 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr4 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_demand = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.sudan_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.sudan_total_demand = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        self.previous_inflow_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.HAD_storage = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        
        for s in range(self.sc_comb):
            self.previous_outflow_recorder[0,s,0]=100
            self.HAD_storage[0,s] = 149500

    def value(self, ts, scenario_index):

        self.year_index = ts.year-self.model.timestepper.start.year
        self.year_fill = ts.year + self.offset_years
        self.month_index = ts.month-1

        if ((ts.month != 1 and self.model.timestepper.delta == "M") or ((ts.month != 1 and ts.day != 1) and self.model.timestepper.delta == "D")) and self.iteration_check[ts.index, scenario_index.global_id]==1:
            self.volume_pc_recorder[ts.index, scenario_index.global_id] = self._storage_node.volume[scenario_index.global_id]

            self._max_flow_eg_irr1[ts.index, scenario_index.global_id] = self.egypt_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_eg_irr2[ts.index, scenario_index.global_id] = self.egypt_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_eg_muni[ts.index, scenario_index.global_id] = self.egypt_municipal_node.get_max_flow(scenario_index)

            self._max_flow_sd_irr1[ts.index, scenario_index.global_id] = self.sudan_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_sd_irr2[ts.index, scenario_index.global_id] = self.sudan_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_sd_irr3[ts.index, scenario_index.global_id] = self.sudan_irrigation_node3.get_max_flow(scenario_index)
            self._max_flow_sd_irr4[ts.index, scenario_index.global_id] = self.sudan_irrigation_node4.get_max_flow(scenario_index)
            self._max_flow_sd_muni[ts.index, scenario_index.global_id] = self.sudan_municipal_node.get_max_flow(scenario_index)

            self.previous_outflow_recorder[self.month_index-1,scenario_index.global_id,self.year_index] = self._outflow_node.prev_flow[scenario_index.global_id]
            self.previous_inflow_recorder[ts.index, scenario_index.global_id] = self._inflow_node.prev_flow[scenario_index.global_id]

            self.egypt_irrigation_deficit = max((self._max_flow_eg_irr1[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node1.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_eg_irr2[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node2.prev_flow[scenario_index.global_id]),0)
            self.egypt_municipal_deficit = max((self._max_flow_eg_muni[ts.index-1, scenario_index.global_id] - self.egypt_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.egypt_total_deficit[ts.index, scenario_index.global_id] = (self.egypt_irrigation_deficit + self.egypt_municipal_deficit)*self.support_factor
            self.egypt_total_demand[ts.index, scenario_index.global_id] = (self._max_flow_eg_irr1[ts.index, scenario_index.global_id] + self._max_flow_eg_irr2[ts.index, scenario_index.global_id] + self._max_flow_eg_muni[ts.index, scenario_index.global_id])*self.support_factor
            self.HAD_storage[ts.index, scenario_index.global_id] = self.High_Aswan_Dam.volume[scenario_index.global_id]

            self.sudan_irrigation_deficit = max((self._max_flow_sd_irr1[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node1.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr2[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node2.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr3[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node3.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr4[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node4.prev_flow[scenario_index.global_id]),0)
            self.sudan_municipal_deficit = max((self._max_flow_sd_muni[ts.index-1, scenario_index.global_id] - self.sudan_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.sudan_total_deficit[ts.index, scenario_index.global_id] = self.sudan_irrigation_deficit + self.sudan_municipal_deficit
            self.sudan_total_demand[ts.index, scenario_index.global_id] = self._max_flow_sd_irr1[ts.index, scenario_index.global_id] + self._max_flow_sd_irr2[ts.index, scenario_index.global_id] + self._max_flow_sd_irr3[ts.index, scenario_index.global_id] + self._max_flow_sd_irr4[ts.index, scenario_index.global_id] + self._max_flow_sd_muni[ts.index, scenario_index.global_id]     

        if ts.index != 0 and self.iteration_check[ts.index, scenario_index.global_id]==0:
            self.volume_pc_recorder[ts.index, scenario_index.global_id] = self._storage_node.volume[scenario_index.global_id]

            self._max_flow_eg_irr1[ts.index, scenario_index.global_id] = self.egypt_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_eg_irr2[ts.index, scenario_index.global_id] = self.egypt_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_eg_muni[ts.index, scenario_index.global_id] = self.egypt_municipal_node.get_max_flow(scenario_index)

            self._max_flow_sd_irr1[ts.index, scenario_index.global_id] = self.sudan_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_sd_irr2[ts.index, scenario_index.global_id] = self.sudan_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_sd_irr3[ts.index, scenario_index.global_id] = self.sudan_irrigation_node3.get_max_flow(scenario_index)
            self._max_flow_sd_irr4[ts.index, scenario_index.global_id] = self.sudan_irrigation_node4.get_max_flow(scenario_index)
            self._max_flow_sd_muni[ts.index, scenario_index.global_id] = self.sudan_municipal_node.get_max_flow(scenario_index)

            self.previous_outflow_recorder[self.month_index-1,scenario_index.global_id,self.year_index] = self._outflow_node.prev_flow[scenario_index.global_id]
            self.previous_inflow_recorder[ts.index, scenario_index.global_id] = self._inflow_node.prev_flow[scenario_index.global_id]

            self.egypt_irrigation_deficit = max((self._max_flow_eg_irr1[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node1.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_eg_irr2[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node2.prev_flow[scenario_index.global_id]),0)
            self.egypt_municipal_deficit = max((self._max_flow_eg_muni[ts.index-1, scenario_index.global_id] - self.egypt_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.egypt_total_deficit[ts.index, scenario_index.global_id] = (self.egypt_irrigation_deficit + self.egypt_municipal_deficit)*self.support_factor
            self.egypt_total_demand[ts.index, scenario_index.global_id] = (self._max_flow_eg_irr1[ts.index, scenario_index.global_id] + self._max_flow_eg_irr2[ts.index, scenario_index.global_id] + self._max_flow_eg_muni[ts.index, scenario_index.global_id])*self.support_factor
            self.HAD_storage[ts.index, scenario_index.global_id] = self.High_Aswan_Dam.volume[scenario_index.global_id]

            self.sudan_irrigation_deficit = max((self._max_flow_sd_irr1[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node1.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr2[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node2.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr3[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node3.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr4[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node4.prev_flow[scenario_index.global_id]),0)
            self.sudan_municipal_deficit = max((self._max_flow_sd_muni[ts.index-1, scenario_index.global_id] - self.sudan_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.sudan_total_deficit[ts.index, scenario_index.global_id] = self.sudan_irrigation_deficit + self.sudan_municipal_deficit
            self.sudan_total_demand[ts.index, scenario_index.global_id] = self._max_flow_sd_irr1[ts.index, scenario_index.global_id] + self._max_flow_sd_irr2[ts.index, scenario_index.global_id] + self._max_flow_sd_irr3[ts.index, scenario_index.global_id] + self._max_flow_sd_irr4[ts.index, scenario_index.global_id] + self._max_flow_sd_muni[ts.index, scenario_index.global_id]     

            self.iteration_check[ts.index, scenario_index.global_id] = 1


        if self.year_fill >= self.first_filling_year and ts.index != 0:
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.first_filling_year_actual_volume and self.stage1[ts.index-1, scenario_index.global_id] != 3:
                self.stage1[ts.index, scenario_index.global_id] = 1
            else:
                self.stage1[ts.index, scenario_index.global_id] = 0
            if ts.month == 7 and self.stage1[ts.index-1, scenario_index.global_id] == 1:
                self.stage1[ts.index, scenario_index.global_id] = 3
            if self.stage1[ts.index-1, scenario_index.global_id] == 3:
                self.stage1[ts.index, scenario_index.global_id] = 3
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.second_filling_year_actual_volume and self.stage2[ts.index-1, scenario_index.global_id] != 3:
                self.stage2[ts.index, scenario_index.global_id] = 1
            else:
                self.stage2[ts.index, scenario_index.global_id] = 0
            if ts.month == 7 and self.stage2[ts.index-1, scenario_index.global_id] == 1:
                self.stage2[ts.index, scenario_index.global_id] = 3
            if self.stage2[ts.index-1, scenario_index.global_id] == 3:
                self.stage2[ts.index, scenario_index.global_id] = 3

        if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) <= 0.99 * self._steady_state_storage:

            """
            The part within the condition above models the filling.
            """

            """
            The if statement below is added to simulate the GERD filling stages for stability and
            turbines testing. Once the GERD reaches a stage, it is not allowed to go lower. The
            first stage is 4900 MCM and the second stage is dead storage.
            """
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= 24350:
                self.min_volume = 24350
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self._long_term_min_volume and self.stage1[ts.index, scenario_index.global_id] != 1:
                self.min_volume = self._long_term_min_volume     
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.second_filling_year_actual_volume:
                self.min_volume = self.second_filling_year_actual_volume
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= 4900:
                self.min_volume = 4900
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self.first_filling_year_actual_volume:
                self.min_volume = self.first_filling_year_actual_volume
            else:
                self.min_volume = 10

            """
            setting outflow.
            """
            if self.stage1[ts.index, scenario_index.global_id] == 1 or self.stage2[ts.index, scenario_index.global_id] == 1:
                self.assignment_values[scenario_index.indices[0]] = 10000
                if self.egypt_total_deficit[ts.index, scenario_index.global_id]>0:
                    self.assignment_values2[scenario_index.indices[0]] = 0
                else:
                    self.assignment_values2[scenario_index.indices[0]] = 0
                    
                self.assignment_values3[scenario_index.indices[0]] = 10000

                self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))
            else:
                if self.egypt_total_deficit[ts.index, scenario_index.global_id] > 0 and self.HAD_storage[ts.index, scenario_index.global_id]< 50000: 
                    self.assignment_values[scenario_index.indices[0]] = max((self.egypt_total_deficit[ts.index, scenario_index.global_id] + self.egypt_total_demand[ts.index, scenario_index.global_id] + self.sudan_total_demand[ts.index, scenario_index.global_id]), self._minimum_daily_release)
                    self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id] + self.egypt_total_demand[ts.index, scenario_index.global_id]
                else:
                    self.assignment_values[scenario_index.indices[0]] = max((self.sudan_total_demand[ts.index, scenario_index.global_id]), self._minimum_daily_release)
                    self.assignment_values2[scenario_index.indices[0]] = 0

                self.assignment_values3[scenario_index.indices[0]] = 0.1

                self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))

            return self.min_volume
        else:
            """
            The part within simulates long-term operation.
            """
            if self.egypt_total_deficit[ts.index, scenario_index.global_id] > 0 and self.HAD_storage[ts.index, scenario_index.global_id] < 50000:
                self.assignment_values[scenario_index.indices[0]] = max(self._long_term_outflow.get_value(scenario_index), (self.egypt_total_deficit[ts.index, scenario_index.global_id] + self.egypt_total_demand[ts.index, scenario_index.global_id] + self.sudan_total_demand[ts.index, scenario_index.global_id]), 0, self._minimum_daily_release)
                self.assignment_values2[scenario_index.indices[0]] = self.egypt_total_deficit[ts.index, scenario_index.global_id] + self.egypt_total_demand[ts.index, scenario_index.global_id]
            else:
                self.assignment_values[scenario_index.indices[0]] = max(self._long_term_outflow.get_value(scenario_index), (self.sudan_total_demand[ts.index, scenario_index.global_id]), 0, self._minimum_daily_release)
                self.assignment_values2[scenario_index.indices[0]] = 0

            self.assignment_values3[scenario_index.indices[0]] = 0.1

            self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
            self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
            self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))
           
            self.min_volume = 24350
            return self.min_volume
            
    @classmethod
    def load(cls, model, data):
        inflow_node = model._get_node_from_ref(model, data.pop("inflow_node"))
        outflow_node = model._get_node_from_ref(model, data.pop("outflow_node"))
        outflow_constant_scenario_parameter = load_parameter(model, data.pop("outflow_constant_scenario_parameter"))
        Egypt_bypass_parameter = load_parameter(model, data.pop("Egypt_bypass_parameter"))
        storage_node = model._get_node_from_ref(model, data.pop("storage_node"))
        annual_release = load_parameter(model, data.pop("annual_release"))
        four_year_release = load_parameter(model, data.pop("four_year_release"))
        five_year_release = load_parameter(model, data.pop("five_year_release"))
        steady_state_storage = data.pop("steady_state_storage")
        minimum_daily_release = data.pop("minimum_daily_release")
        maximum_daily_release = data.pop("maximum_daily_release")
        ts_to_ts_max_change_in_outflow = data.pop("ts_to_ts_max_change_in_outflow")
        long_term_min_volume = data.pop("long_term_min_volume")
        first_filling_year_actual_volume = data.pop("first_filling_year_actual_volume")
        second_filling_year_actual_volume = data.pop("second_filling_year_actual_volume")
        long_term_outflow = load_parameter(model, data.pop("long_term_outflow"))
        if "first_filling_year" in data:
            first_filling_year = data.pop("first_filling_year")
        else:
            first_filling_year = 2020
        if "offset_years" in data:
            offset_years = data.pop("offset_years")
        else:
            offset_years = 0

        if "release_table_during_filling_csv" in data:
            release_table_during_filling_csv = data.pop("release_table_during_filling_csv")
        else:
            release_table_during_filling_csv = "data/Washington_filling_table.csv"

        if "release_table_during_operation_csv" in data:
            release_table_during_operation_csv = data.pop("release_table_during_operation_csv")
        else:
            release_table_during_operation_csv = "data/Washington_operation_table.csv"
        if "consider_release_tables_and_drought_meastures" in data:
            consider_release_tables_and_drought_meastures = data.pop("consider_release_tables_and_drought_meastures")
        else:
            consider_release_tables_and_drought_meastures = True
        if "save_intermediate_calculations" in data:
            save_intermediate_calculations = data.pop("save_intermediate_calculations")
        else:
            save_intermediate_calculations = True

        return cls(model, inflow_node, outflow_node, outflow_constant_scenario_parameter, Egypt_bypass_parameter,
        storage_node, annual_release, four_year_release, five_year_release, steady_state_storage, minimum_daily_release, maximum_daily_release,
        ts_to_ts_max_change_in_outflow, long_term_min_volume, long_term_outflow, first_filling_year, offset_years, first_filling_year_actual_volume,
        second_filling_year_actual_volume, release_table_during_filling_csv, release_table_during_operation_csv, consider_release_tables_and_drought_meastures,
        save_intermediate_calculations, **data)
OpportunisticFilling.register()


class Prioratize_GERD_electricity(Parameter):
    """ A parameter simulates the filling and long-term operation of the GERD.

    This parameter returns the min_volume for the GERD and also modifies other
    parameters that influence downstream dams. The parameter should be linked to
    GERD min_volume. The paramter is simulates a fraction-based filling rule for
    the GERD.

    inputs
    ----------
    type : a string "FlowFractionInitialFillingParameter"
    inflow_node : the node directly upstream of the GERD that provides the dam inflow
    outflow_constant_scenario_parameter : a ConstantScenarioParameter linked to the max_flow of 
                GERD control node. The values of this node are modified by this parameter to control
                GERD outflow during filling and long-term operation.
    Egypt_bypass_parameter : a ConstantScenarioParameter used to make sure that coordinated releases
                Between the GERD and HAD reaches Egypt. In other words, Egypt_bypass_parameter is added
                to water releases from the Roseires, Sennar, and Merowe dams to make sure that Sudan 
                does not use releases from the GERD that are meant for Egypt.
    storage_node : GERD reservoir node.
    annual_release : a number graeter than 0 represnts the minimum GERD release volume per year
    steady_state_storage : reservoir storage at which the steady-state operation starts
    long_term_min_volume : This is the long-term GERD dead storage of GERD once full. During the filling,
                the GERD is not allowed to fall below this level once reached.
    "minimum_daily_release": a minimum daily release value
    long_term_outflow : This is a parameter that provides the long-term GERD outflow. This is used to
                control GERD releases in the long-term after filling.

    Example
    -----------
      "GERD_min":{
         "type":"FlowFractionInitialFillingParameter",
         "inflow_node":"C60",
         "outflow_constant_scenario_parameter": "GERD_outflow_control",
         "Egypt_bypass_parameter": "Egypt_bypass",
         "storage_node":"GERD",
         "steady_state_storage":49750,
         "annual_release":37000,
         "long_term_min_volume":15000,
         "minimum_daily_release":15,
         "long_term_outflow":"GERD_target_power_flow"
      },

    """

    def __init__(self, model, inflow_node, outflow_node, outflow_constant_scenario_parameter, 
    Egypt_bypass_parameter, storage_node, annual_release, four_year_release, five_year_release,
    steady_state_storage, minimum_daily_release, maximum_daily_release, ts_to_ts_max_change_in_outflow,
    long_term_min_volume, long_term_outflow, first_filling_year,offset_years, first_filling_year_actual_volume,
    second_filling_year_actual_volume, release_table_during_filling_csv, release_table_during_operation_csv,
    consider_release_tables_and_drought_meastures, save_intermediate_calculations, **kwargs):
        super().__init__(model, **kwargs)
        self._inflow_node = inflow_node
        self._outflow_node = outflow_node
        self._outflow_constant_scenario_parameter = outflow_constant_scenario_parameter
        self._Egypt_bypass_parameter = Egypt_bypass_parameter
        self._storage_node = storage_node
        self._annual_release = None
        self.annual_release = annual_release
        self._four_year_release = None
        self.four_year_release = four_year_release
        self._five_year_release = None
        self.five_year_release = five_year_release
        self._steady_state_storage = steady_state_storage
        self._minimum_daily_release = minimum_daily_release
        self._long_term_min_volume = long_term_min_volume
        self._long_term_outflow = None
        self.long_term_outflow = long_term_outflow
        self.egypt_irrigation_node1 = model._get_node_from_ref(model, "Egypt Irrigation")
        self.egypt_irrigation_node2 = model._get_node_from_ref(model, "Toshka Irrigation")
        self.egypt_municipal_node = model._get_node_from_ref(model, "Egypt Municipal")
        self.sudan_irrigation_node1 = model._get_node_from_ref(model, "Rahad Irrigation")
        self.sudan_irrigation_node2 = model._get_node_from_ref(model, "Suki_and_NW_Sennar Irrigation")
        self.sudan_irrigation_node3 = model._get_node_from_ref(model, "Gezira Managil Irrigation")
        self.sudan_irrigation_node4 = model._get_node_from_ref(model, "Gunied Irrigation")
        self.sudan_municipal_node = model._get_node_from_ref(model, "Khartoum Municipal")
        self._GERD_dummy_bypass_parameter = load_parameter(model, "GERD_dummy_bypass")
        self.High_Aswan_Dam = model._get_node_from_ref(model, "HAD")
        self.first_filling_year = first_filling_year
        self.offset_years =offset_years

    long_term_outflow = parameter_property("_long_term_outflow")
    annual_release = parameter_property("_annual_release")
    four_year_release = parameter_property("_four_year_release")
    five_year_release = parameter_property("_five_year_release")

    def setup(self):
        super().setup()
        self.sc_size = 1
        self.sc_comb = len(self.model.scenarios.combinations)
        for m in range(len(self.model.scenarios.scenarios)):
            self.sc_size = self.sc_size * self.model.scenarios.scenarios[m].size
        self.n_ts = len(self.model.timestepper)
        self.nyears = self.model.timestepper.end.year - self.model.timestepper.start.year + 1

        self.volume_pc_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr3 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr4 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_demand = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.sudan_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.sudan_total_demand = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        self.previous_inflow_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.HAD_storage = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        for s in range(self.sc_comb):
            self.previous_outflow_recorder[0,s,0] = 100
            self.HAD_storage[0,s] = 149500

        self.assignment_values = []
        self.assignment_values2 = []
        self.assignment_values3 = []
        for s in range(self.sc_size):
            self.assignment_values.append(100)
            self.assignment_values2.append(0)
            self.assignment_values3.append(0)

    def reset(self):
        self.volume_pc_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_eg_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr3 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_irr4 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._max_flow_sd_muni = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.egypt_total_demand = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.sudan_total_deficit = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.sudan_total_demand = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.previous_outflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        self.previous_inflow_recorder = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage1 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.stage2 = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self.HAD_storage = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        
        for s in range(self.sc_comb):
            self.previous_outflow_recorder[0,s,0]=100
            self.HAD_storage[0,s] = 149500

    def value(self, ts, scenario_index):

        self.year_index = ts.year-self.model.timestepper.start.year
        self.year_fill = ts.year + self.offset_years
        self.month_index = ts.month-1

        if ((ts.month != 1 and self.model.timestepper.delta == "M") or ((ts.month != 1 and ts.day != 1) and self.model.timestepper.delta == "D")) and self.iteration_check[ts.index, scenario_index.global_id]==1:
            self.volume_pc_recorder[ts.index, scenario_index.global_id] = self._storage_node.volume[scenario_index.global_id]

            self._max_flow_eg_irr1[ts.index, scenario_index.global_id] = self.egypt_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_eg_irr2[ts.index, scenario_index.global_id] = self.egypt_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_eg_muni[ts.index, scenario_index.global_id] = self.egypt_municipal_node.get_max_flow(scenario_index)

            self._max_flow_sd_irr1[ts.index, scenario_index.global_id] = self.sudan_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_sd_irr2[ts.index, scenario_index.global_id] = self.sudan_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_sd_irr3[ts.index, scenario_index.global_id] = self.sudan_irrigation_node3.get_max_flow(scenario_index)
            self._max_flow_sd_irr4[ts.index, scenario_index.global_id] = self.sudan_irrigation_node4.get_max_flow(scenario_index)
            self._max_flow_sd_muni[ts.index, scenario_index.global_id] = self.sudan_municipal_node.get_max_flow(scenario_index)

            self.previous_outflow_recorder[self.month_index-1,scenario_index.global_id,self.year_index] = self._outflow_node.prev_flow[scenario_index.global_id]
            self.previous_inflow_recorder[ts.index, scenario_index.global_id] = self._inflow_node.prev_flow[scenario_index.global_id]

            self.egypt_irrigation_deficit = max((self._max_flow_eg_irr1[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node1.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_eg_irr2[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node2.prev_flow[scenario_index.global_id]),0)
            self.egypt_municipal_deficit = max((self._max_flow_eg_muni[ts.index-1, scenario_index.global_id] - self.egypt_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.egypt_total_deficit[ts.index, scenario_index.global_id] = (self.egypt_irrigation_deficit + self.egypt_municipal_deficit)/0.9
            self.egypt_total_demand[ts.index, scenario_index.global_id] = (self._max_flow_eg_irr1[ts.index, scenario_index.global_id] + self._max_flow_eg_irr2[ts.index, scenario_index.global_id] + self._max_flow_eg_muni[ts.index, scenario_index.global_id])/0.9
            self.HAD_storage[ts.index, scenario_index.global_id] = self.High_Aswan_Dam.volume[scenario_index.global_id]

            self.sudan_irrigation_deficit = max((self._max_flow_sd_irr1[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node1.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr2[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node2.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr3[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node3.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr4[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node4.prev_flow[scenario_index.global_id]),0)
            self.sudan_municipal_deficit = max((self._max_flow_sd_muni[ts.index-1, scenario_index.global_id] - self.sudan_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.sudan_total_deficit[ts.index, scenario_index.global_id] = self.sudan_irrigation_deficit + self.sudan_municipal_deficit
            self.sudan_total_demand[ts.index, scenario_index.global_id] = self._max_flow_sd_irr1[ts.index, scenario_index.global_id] + self._max_flow_sd_irr2[ts.index, scenario_index.global_id] + self._max_flow_sd_irr3[ts.index, scenario_index.global_id] + self._max_flow_sd_irr4[ts.index, scenario_index.global_id] + self._max_flow_sd_muni[ts.index, scenario_index.global_id]     

        if ts.index != 0 and self.iteration_check[ts.index, scenario_index.global_id]==0:
            self.volume_pc_recorder[ts.index, scenario_index.global_id] = self._storage_node.volume[scenario_index.global_id]

            self._max_flow_eg_irr1[ts.index, scenario_index.global_id] = self.egypt_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_eg_irr2[ts.index, scenario_index.global_id] = self.egypt_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_eg_muni[ts.index, scenario_index.global_id] = self.egypt_municipal_node.get_max_flow(scenario_index)

            self._max_flow_sd_irr1[ts.index, scenario_index.global_id] = self.sudan_irrigation_node1.get_max_flow(scenario_index)
            self._max_flow_sd_irr2[ts.index, scenario_index.global_id] = self.sudan_irrigation_node2.get_max_flow(scenario_index)
            self._max_flow_sd_irr3[ts.index, scenario_index.global_id] = self.sudan_irrigation_node3.get_max_flow(scenario_index)
            self._max_flow_sd_irr4[ts.index, scenario_index.global_id] = self.sudan_irrigation_node4.get_max_flow(scenario_index)
            self._max_flow_sd_muni[ts.index, scenario_index.global_id] = self.sudan_municipal_node.get_max_flow(scenario_index)

            self.previous_outflow_recorder[self.month_index-1,scenario_index.global_id,self.year_index] = self._outflow_node.prev_flow[scenario_index.global_id]
            self.previous_inflow_recorder[ts.index, scenario_index.global_id] = self._inflow_node.prev_flow[scenario_index.global_id]

            self.egypt_irrigation_deficit = max((self._max_flow_eg_irr1[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node1.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_eg_irr2[ts.index-1, scenario_index.global_id] - self.egypt_irrigation_node2.prev_flow[scenario_index.global_id]),0)
            self.egypt_municipal_deficit = max((self._max_flow_eg_muni[ts.index-1, scenario_index.global_id] - self.egypt_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.egypt_total_deficit[ts.index, scenario_index.global_id] = (self.egypt_irrigation_deficit + self.egypt_municipal_deficit)/0.9
            self.egypt_total_demand[ts.index, scenario_index.global_id] = (self._max_flow_eg_irr1[ts.index, scenario_index.global_id] + self._max_flow_eg_irr2[ts.index, scenario_index.global_id] + self._max_flow_eg_muni[ts.index, scenario_index.global_id])/0.9
            self.HAD_storage[ts.index, scenario_index.global_id] = self.High_Aswan_Dam.volume[scenario_index.global_id]

            self.sudan_irrigation_deficit = max((self._max_flow_sd_irr1[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node1.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr2[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node2.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr3[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node3.prev_flow[scenario_index.global_id]),0) + max((self._max_flow_sd_irr4[ts.index-1, scenario_index.global_id] - self.sudan_irrigation_node4.prev_flow[scenario_index.global_id]),0)
            self.sudan_municipal_deficit = max((self._max_flow_sd_muni[ts.index-1, scenario_index.global_id] - self.sudan_municipal_node.prev_flow[scenario_index.global_id]),0)
            self.sudan_total_deficit[ts.index, scenario_index.global_id] = self.sudan_irrigation_deficit + self.sudan_municipal_deficit
            self.sudan_total_demand[ts.index, scenario_index.global_id] = self._max_flow_sd_irr1[ts.index, scenario_index.global_id] + self._max_flow_sd_irr2[ts.index, scenario_index.global_id] + self._max_flow_sd_irr3[ts.index, scenario_index.global_id] + self._max_flow_sd_irr4[ts.index, scenario_index.global_id] + self._max_flow_sd_muni[ts.index, scenario_index.global_id]     

            self.iteration_check[ts.index, scenario_index.global_id] = 1


        if self.year_fill >= self.first_filling_year and ts.index != 0:
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= 4900 and self.stage1[ts.index-1, scenario_index.global_id] != 3:
                self.stage1[ts.index, scenario_index.global_id] = 1
            else:
                self.stage1[ts.index, scenario_index.global_id] = 0
            if ts.month == 7 and self.stage1[ts.index-1, scenario_index.global_id] == 1:
                self.stage1[ts.index, scenario_index.global_id] = 3
            if self.stage1[ts.index-1, scenario_index.global_id] == 3:
                self.stage1[ts.index, scenario_index.global_id] = 3
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self._long_term_min_volume and self.stage2[ts.index-1, scenario_index.global_id] != 3:
                self.stage2[ts.index, scenario_index.global_id] = 1
            else:
                self.stage2[ts.index, scenario_index.global_id] = 0
            if ts.month == 7 and self.stage2[ts.index-1, scenario_index.global_id] == 1:
                self.stage2[ts.index, scenario_index.global_id] = 3
            if self.stage2[ts.index-1, scenario_index.global_id] == 3:
                self.stage2[ts.index, scenario_index.global_id] = 3

        if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) <= 0.99 * self._steady_state_storage:

            """
            The part within the condition above models the filling.
            """

            """
            The if statement below is added to simulate the GERD filling stages for stability and
            turbines testing. Once the GERD reaches a stage, it is not allowed to go lower. The
            first stage is 4900 MCM and the second stage is dead storage.
            """
            if np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= 24350:
                self.min_volume = 24350
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= self._long_term_min_volume and self.stage1[ts.index, scenario_index.global_id] != 1:
                self.min_volume = self._long_term_min_volume     
            elif np.amax(self.volume_pc_recorder[0:ts.index+1,scenario_index.global_id], axis=0) >= 4900:
                self.min_volume = 4900
            else:
                self.min_volume = 10

            """
            setting outflow.
            """
            if self.stage1[ts.index, scenario_index.global_id] == 1 or self.stage2[ts.index, scenario_index.global_id] == 1:
                self.assignment_values[scenario_index.indices[0]] = 10000
                if self.egypt_total_deficit[ts.index, scenario_index.global_id]>0:
                    self.assignment_values2[scenario_index.indices[0]] = 0
                else:
                    self.assignment_values2[scenario_index.indices[0]] = 0
                    
                self.assignment_values3[scenario_index.indices[0]] = 10000

                self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))
            else:
                if self.egypt_total_deficit[ts.index, scenario_index.global_id] > 0 and self.HAD_storage[ts.index, scenario_index.global_id]< 50000: 
                    self.assignment_values[scenario_index.indices[0]] = max((self.sudan_total_demand[ts.index, scenario_index.global_id]), self._minimum_daily_release)
                    self.assignment_values2[scenario_index.indices[0]] = 0
                else:
                    self.assignment_values[scenario_index.indices[0]] = max((self.sudan_total_demand[ts.index, scenario_index.global_id]), self._minimum_daily_release)
                    self.assignment_values2[scenario_index.indices[0]] = 0

                self.assignment_values3[scenario_index.indices[0]] = 0.1

                self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
                self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
                self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))

            return self.min_volume
        else:
            """
            The part within simulates long-term operation.
            """
            if self.egypt_total_deficit[ts.index, scenario_index.global_id] > 0 and self.HAD_storage[ts.index, scenario_index.global_id] < 50000:
                self.assignment_values[scenario_index.indices[0]] = max(self._long_term_outflow.get_value(scenario_index), (self.sudan_total_demand[ts.index, scenario_index.global_id]), 0, self._minimum_daily_release)
                self.assignment_values2[scenario_index.indices[0]] = 0
            else:
                self.assignment_values[scenario_index.indices[0]] = max(self._long_term_outflow.get_value(scenario_index), (self.sudan_total_demand[ts.index, scenario_index.global_id]), 0, self._minimum_daily_release)
                self.assignment_values2[scenario_index.indices[0]] = 0

            self.assignment_values3[scenario_index.indices[0]] = 0.1

            self._outflow_constant_scenario_parameter.set_double_variables(np.array(self.assignment_values,dtype = np.float64))
            self._Egypt_bypass_parameter.set_double_variables(np.array(self.assignment_values2,dtype = np.float64))
            self._GERD_dummy_bypass_parameter.set_double_variables(np.array(self.assignment_values3,dtype = np.float64))
           
            self.min_volume = 24350
            return self.min_volume
            
    @classmethod
    def load(cls, model, data):
        inflow_node = model._get_node_from_ref(model, data.pop("inflow_node"))
        outflow_node = model._get_node_from_ref(model, data.pop("outflow_node"))
        outflow_constant_scenario_parameter = load_parameter(model, data.pop("outflow_constant_scenario_parameter"))
        Egypt_bypass_parameter = load_parameter(model, data.pop("Egypt_bypass_parameter"))
        storage_node = model._get_node_from_ref(model, data.pop("storage_node"))
        annual_release = load_parameter(model, data.pop("annual_release"))
        four_year_release = load_parameter(model, data.pop("four_year_release"))
        five_year_release = load_parameter(model, data.pop("five_year_release"))
        steady_state_storage = data.pop("steady_state_storage")
        minimum_daily_release = data.pop("minimum_daily_release")
        maximum_daily_release = data.pop("maximum_daily_release")
        ts_to_ts_max_change_in_outflow = data.pop("ts_to_ts_max_change_in_outflow")
        long_term_min_volume = data.pop("long_term_min_volume")
        first_filling_year_actual_volume = data.pop("first_filling_year_actual_volume")
        second_filling_year_actual_volume = data.pop("second_filling_year_actual_volume")
        long_term_outflow = load_parameter(model, data.pop("long_term_outflow"))
        if "first_filling_year" in data:
            first_filling_year = data.pop("first_filling_year")
        else:
            first_filling_year = 2020
        if "offset_years" in data:
            offset_years = data.pop("offset_years")
        else:
            offset_years = 0

        if "release_table_during_filling_csv" in data:
            release_table_during_filling_csv = data.pop("release_table_during_filling_csv")
        else:
            release_table_during_filling_csv = "data/Washington_filling_table.csv"

        if "release_table_during_operation_csv" in data:
            release_table_during_operation_csv = data.pop("release_table_during_operation_csv")
        else:
            release_table_during_operation_csv = "data/Washington_operation_table.csv"
        if "consider_release_tables_and_drought_meastures" in data:
            consider_release_tables_and_drought_meastures = data.pop("consider_release_tables_and_drought_meastures")
        else:
            consider_release_tables_and_drought_meastures = True
        if "save_intermediate_calculations" in data:
            save_intermediate_calculations = data.pop("save_intermediate_calculations")
        else:
            save_intermediate_calculations = True

        return cls(model, inflow_node, outflow_node, outflow_constant_scenario_parameter, Egypt_bypass_parameter,
        storage_node, annual_release, four_year_release, five_year_release, steady_state_storage, minimum_daily_release, maximum_daily_release,
        ts_to_ts_max_change_in_outflow, long_term_min_volume, long_term_outflow, first_filling_year, offset_years, first_filling_year_actual_volume,
        second_filling_year_actual_volume, release_table_during_filling_csv, release_table_during_operation_csv, consider_release_tables_and_drought_meastures,
        save_intermediate_calculations, **data)
Prioratize_GERD_electricity.register()



class Filling_stages(Parameter):
    """ A parameter simulates GERD filling stages be setting the max volume attribute of the GERD reservoir node.

    inputs
    ----------
    type : a string "Filling_stages"
    Year1_target_volume : max storage volume for year1
    Year2_target_volume : max storage volume for year2
    Year3_target_volume : max storage volume for year3
    Year4_target_volume : max storage volume for year4
    Year5_target_volume : max storage volume for year5
    Year6_target_volume : max storage volume for year6

    Example
    -----------
      "GERD_max":{
         "type":"Filling_stages",
         "Year1_target_volume" : 4000,
         "Year2_target_volume" : 7000,
         "Year3_target_volume" : 18250,
         "Year4_target_volume" : 28900,
         "Year5_target_volume" : 39300,
         "Year6_target_volume" : 49750,
         "Max_storage_capacity" : 74000
      }

    """

    def __init__(self, model, Year1_target_volume, Year2_target_volume, Year3_target_volume, Year4_target_volume,
    Year5_target_volume, Year6_target_volume, Max_storage_capacity, first_filling_year, offset_years, **kwargs):
        super().__init__(model, **kwargs)

        self.Year1_target_volume = Year1_target_volume
        self.Year2_target_volume = Year2_target_volume
        self.Year3_target_volume = Year3_target_volume
        self.Year4_target_volume = Year4_target_volume
        self.Year5_target_volume = Year5_target_volume
        self.Year6_target_volume = Year6_target_volume
        self.Max_storage_capacity = Max_storage_capacity
        self.first_filling_year = first_filling_year
        self.offset_years = offset_years

    def setup(self):
        super().setup()
        self.sc_comb = len(self.model.scenarios.combinations)
        self.n_ts = len(self.model.timestepper)

        self.max_storage = np.zeros((self.n_ts, self.sc_comb,), np.float64)

    def reset(self):
        self.max_storage = np.zeros((self.n_ts, self.sc_comb,), np.float64)

    def value(self, ts, scenario_index):

        self.year_index = ts.year-self.model.timestepper.start.year
        self.year_fill = ts.year + self.offset_years
        self.month_index = ts.month-1
        self.day_index = ts.dayofyear-1

        if self.year_fill < self.first_filling_year:
            self.max_storage[ts.index, scenario_index.global_id] = 12
        elif self.year_fill == self.first_filling_year:
            self.max_storage[ts.index, scenario_index.global_id] = self.Year1_target_volume
        elif self.year_fill == (self.first_filling_year + 1):
            self.max_storage[ts.index, scenario_index.global_id] = self.Year2_target_volume
        elif self.year_fill == (self.first_filling_year + 2):
            self.max_storage[ts.index, scenario_index.global_id] = self.Year3_target_volume
        elif self.year_fill == (self.first_filling_year + 3):
            self.max_storage[ts.index, scenario_index.global_id] = self.Year4_target_volume
        elif self.year_fill == (self.first_filling_year + 4):
            self.max_storage[ts.index, scenario_index.global_id] = self.Year5_target_volume
        elif self.year_fill == (self.first_filling_year + 5):
            self.max_storage[ts.index, scenario_index.global_id] = self.Year6_target_volume
        else:
            self.max_storage[ts.index, scenario_index.global_id] = self.Max_storage_capacity

        return self.max_storage[ts.index, scenario_index.global_id]
            
    @classmethod
    def load(cls, model, data):
        Year1_target_volume = data.pop("Year1_target_volume")
        Year2_target_volume = data.pop("Year2_target_volume")
        Year3_target_volume = data.pop("Year3_target_volume")
        Year4_target_volume = data.pop("Year4_target_volume")
        Year5_target_volume = data.pop("Year5_target_volume")
        Year6_target_volume = data.pop("Year6_target_volume")
        Max_storage_capacity = data.pop("Max_storage_capacity")
        if "first_filling_year" in data:
            first_filling_year = data.pop("first_filling_year")
        else:
            first_filling_year = 2020
        if "offset_years" in data:
            offset_years = data.pop("offset_years")
        else:
            offset_years = 0

        return cls(model, Year1_target_volume, Year2_target_volume, Year3_target_volume, Year4_target_volume, Year5_target_volume,
        Year6_target_volume, Max_storage_capacity, first_filling_year, offset_years, **data)
Filling_stages.register()

class AbstractComparisonNodeRecorder(NumpyArrayNodeRecorder):
    """ Base class for all Recorders performing timeseries comparison of `Node` flows
    """
    def __init__(self, model, node, data_column, data_observed, **kwargs):
        super(AbstractComparisonNodeRecorder, self).__init__(model, node, **kwargs)
        self.flow_node = node
        self.data_column = data_column
        self.observed = data_observed
        self._aligned_observed = None

    def setup(self):
        super(AbstractComparisonNodeRecorder, self).setup()
        # Align the observed data to the model
        from pywr.parameters import align_and_resample_dataframe
        self._aligned_observed = align_and_resample_dataframe(self.observed, self.model.timestepper.datetime_index)

    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        node = model._get_node_from_ref(model, data.pop("node"))
        data_column = data.pop("data_column")

        index_column = data.pop("index_column")
        csv_url = data.pop("csv_url")

        data_observed = pd.read_csv(csv_url).set_index(str(index_column))
        data_observed.index = pd.to_datetime(data_observed.index)

        return cls(model, node, data_column=data_column, data_observed=data_observed, **data)

class AbstractComparisonStorageRecorder(NumpyArrayStorageRecorder):
    """ Base class for all Recorders performing timeseries comparison of `Node` storage
    """
    def __init__(self, model, node, data_column, data_observed, **kwargs):
        super(AbstractComparisonStorageRecorder, self).__init__(model, node, **kwargs)
        self.flow_node = node
        self.data_column = data_column
        self.observed = data_observed
        self._aligned_observed = None

    def setup(self):
        super(AbstractComparisonStorageRecorder, self).setup()
        # Align the observed data to the model
        from pywr.parameters import align_and_resample_dataframe
        self._aligned_observed = align_and_resample_dataframe(self.observed, self.model.timestepper.datetime_index)

    @classmethod
    def load(cls, model, data):
        # called when the parameter is loaded from a JSON document
        node = model._get_node_from_ref(model, data.pop("node"))
        data_column = data.pop("data_column")

        index_column = data.pop("index_column")
        csv_url = data.pop("csv_url")

        data_observed = pd.read_csv(csv_url).set_index(str(index_column))
        data_observed.index = pd.to_datetime(data_observed.index)

        return cls(model, node, data_column=data_column, data_observed=data_observed, **data)

class RootMeanSquaredErrorNodeRecorder(AbstractComparisonNodeRecorder):
    """ Recorder evaluates the RMSE between model and observed """
    def values(self):
        mod = self.data
        obs = self._aligned_observed.to_numpy()
        return np.sqrt(np.mean((obs-mod)**2, axis=0))
RootMeanSquaredErrorNodeRecorder.register()

class MeanBiasErrorNodeRecorder(AbstractComparisonNodeRecorder):
    """ Recorder evaluates the RMSE between model and observed """
    def values(self):
        mod = self.data
        obs = self._aligned_observed.to_numpy()
        return np.absolute(np.mean((mod-obs), axis=0))
        #absolute value is calculate so that this can be a minimisation objective
MeanBiasErrorNodeRecorder.register()

class CoefficientOfDeterminationNodeRecorder(AbstractComparisonNodeRecorder):
    """ Recorder evaluates the Coefficient of Determination of model and observed """
    def values(self):
        mod = self.data
        obs = self._aligned_observed.to_numpy()
        n_items = len(mod)    
        Numerator=n_items*np.sum(mod*obs, axis=0)-np.sum(mod, axis=0)*np.sum(obs, axis=0)
        Denominator=np.sqrt((n_items*np.sum(mod**2, axis=0)-(np.sum(mod, axis=0))**2)*(n_items*np.sum(obs**2, axis=0)-(np.sum(obs, axis=0))**2))
        return (Numerator/Denominator)**2
CoefficientOfDeterminationNodeRecorder.register()

class NashSutcliffeEfficiencyNodeRecorder(AbstractComparisonNodeRecorder):
    """ Recorder evaluates the Nash-Sutcliffe efficiency model and observed """
    def values(self):
        mod = self.data
        obs = self._aligned_observed.to_numpy()
        obs_mean = np.mean(obs, axis=0)
        return 1.0 - np.sum((obs-mod)**2, axis=0)/np.sum((obs-obs_mean)**2, axis=0)
NashSutcliffeEfficiencyNodeRecorder.register()


class RootMeanSquaredErrorStorageRecorder(AbstractComparisonStorageRecorder):
    """ Recorder evaluates the RMSE between model and observed """
    def values(self):
        mod = self.data
        obs = self._aligned_observed.to_numpy()
        return np.sqrt(np.mean((obs-mod)**2, axis=0))
RootMeanSquaredErrorStorageRecorder.register()

class MeanBiasErrorStorageRecorder(AbstractComparisonStorageRecorder):
    """ Recorder evaluates the RMSE between model and observed """
    def values(self):
        mod = self.data
        obs = self._aligned_observed.to_numpy()
        #absolute value is calculate so that this can be a minimisation objective
        return np.absolute(np.mean((mod-obs), axis=0))
MeanBiasErrorStorageRecorder.register()

class CoefficientOfDeterminationStorageRecorder(AbstractComparisonStorageRecorder):
    """ Recorder evaluates the Coefficient of Determination of model and observed """
    def values(self):
        mod = self.data        
        obs = self._aligned_observed.to_numpy()
        n_items = len(mod)
        Numerator=n_items*np.sum(mod*obs, axis=0)-np.sum(mod, axis=0)*np.sum(obs, axis=0)
        Denominator=np.sqrt((n_items*np.sum(mod**2, axis=0)-(np.sum(mod, axis=0))**2)*(n_items*np.sum(obs**2, axis=0)-(np.sum(obs, axis=0))**2))    
        return (Numerator/Denominator)**2
CoefficientOfDeterminationStorageRecorder.register()

class NashSutcliffeEfficiencyStorageRecorder(AbstractComparisonStorageRecorder):
    """ Recorder evaluates the Nash-Sutcliffe efficiency model and observed """
    def values(self):
        mod = self.data
        obs = self._aligned_observed.to_numpy()
        obs_mean = np.mean(obs, axis=0)
        return 1.0 - np.sum((obs-mod)**2, axis=0)/np.sum((obs-obs_mean)**2, axis=0)
NashSutcliffeEfficiencyStorageRecorder.register()


class RbfData:
    """Container for Rbf interpolation data.
    This object is intended to be used with `RbfParameter` where one set of data
    is required for each item to be used as an exogenous variable. This object
    contains the interpolation values and data specifying whether this particular
    item is to be considered a variable.
    """
    def __init__(self, values, is_variable=False, upper_bounds=None, lower_bounds=None):
        self.values = values
        self.is_variable = is_variable
        self.upper_bounds = upper_bounds
        self.lower_bounds = lower_bounds

    def __len__(self):
        return len(self.values)

    def get_upper_bounds(self):
        if self.upper_bounds is None:
            return None
        return [self.upper_bounds]*len(self.values)

    def get_lower_bounds(self):
        if self.lower_bounds is None:
            return None
        return [self.lower_bounds]*len(self.values)


class RbfParameter(Parameter):
    """ A general Rbf parameter.
    This parameter is designed to perform general multi-dimensional interpolation using
    radial basis functions. It utilises the `scipy.interpolate.Rbf` functionality for evaluation
    of the radial basis function, and is mostly a wrapper around that class.
    Parameters
    ==========
    """
    def __init__(self, model, y, nodes=None, parameters=None, days_of_year=None, rbf_kwargs=None, **kwargs):
        super(RbfParameter, self).__init__(model, **kwargs)

        # Initialise defaults of no data
        if nodes is None:
            nodes = {}

        if parameters is None:
            parameters = {}

        for parameter in parameters.keys():
            # Make these parameter's children.
            self.children.add(parameter)

        # Attributes
        self.nodes = nodes
        self.parameters = parameters
        self.days_of_year = days_of_year
        self.y = y
        self.rbf_kwargs = rbf_kwargs if rbf_kwargs is not None else {}
        self._rbf_func = None
        self._node_order = None
        self._parameter_order = None

    def setup(self):
        super().setup()
        double_size = 0

        for node, x in self.nodes.items():
            if x.is_variable:
                double_size += len(x)

        for parameter, x in self.parameters.items():
            if x.is_variable:
                double_size += len(x)

        if self.days_of_year is not None:
            if self.days_of_year.is_variable:
                double_size += len(self.days_of_year)

        if self.y.is_variable:
            double_size += len(self.y)

        self.double_size = double_size
        if self.double_size > 0:
            self.is_variable = True
        else:
            self.is_variable = False

    def reset(self):
        # Create the Rbf object here.
        # This is done in `reset` rather than `setup` because
        # we wish to have support for optimising some of the Rbf parameters.
        # Therefore it needs recreating each time.
        nodes = self.nodes
        parameters = self.parameters
        days_of_year = self.days_of_year
        y = self.y

        if len(nodes) == 0 and len(parameters) == 0 and days_of_year is None:
            raise ValueError('There must be at least one exogenous variable defined.')

        # Create the arguments for the Rbf function.
        # also cache the order of the nodes, so that when the are evaluated later we know
        # the correct order
        args = []
        node_order = []
        for node, x in nodes.items():
            if len(x) != len(y):
                raise ValueError('The length of the exogenous variables for node "{}"'
                                 ' must be the same as length of "y".'.format(node.name))
            args.append(x.values)
            node_order.append(node)

        parameter_order = []
        for parameter, x in parameters.items():
            if len(x) != len(y):
                raise ValueError('The length of the exogenous variables for parameter "{}"'
                                 ' must be the same as the length of "y".'.format(parameter.name))
            args.append(x.values)
            parameter_order.append(parameter)

        if days_of_year is not None:
            # Normalise DoY using cosine & sine harmonics
            x = [2 * np.pi * (doy - 1) / 365 for doy in self.days_of_year.values]
            args.append(np.sin(x))
            args.append(np.cos(x))

        # Finally append the known y values
        args.append(y.values)

        # Convention here is that DoY is the first independent variable.
        self._rbf_func = Rbf(*args, **self.rbf_kwargs)

        # Save the node and parameter order caches
        self._node_order = node_order
        self._parameter_order = parameter_order

    def set_double_variables(self, values):
        """Assign an array of variables to the interpolation data."""
        N = len(self.y)

        values = np.reshape(values, (-1, N))
        item = 0
        for node, x in self.nodes.items():
            if x.is_variable:
                x.values = values[item, :]
                item += 1

        for parameter, x in self.parameters.items():
            if x.is_variable:
                x.values = values[item, :]
                item += 1

        if self.days_of_year is not None:
            if self.days_of_year.is_variable:
                self.days_of_year.values = values[item, :]
                item += 1

        if self.y.is_variable:
            self.y.values = values[item, :]
            item += 1

        # Make sure all variables have been used.
        assert item == values.shape[0]

    def get_double_variables(self):
        """Get the current values of variable interpolation data."""
        values = []

        for node, x in self.nodes.items():
            if x.is_variable:
                values.extend(x.values)

        for parameter, x in self.parameters.items():
            if x.is_variable:
                values.extend(x.values)

        if self.days_of_year is not None:
            if self.days_of_year.is_variable:
                values.extend(self.days_of_year.values)

        if self.y.is_variable:
            values.extend(self.y.values)

        return np.array(values)

    def get_double_upper_bounds(self):
        """Returns an array of the upper bounds of the variables."""
        values = []

        for node, x in self.nodes.items():
            if x.is_variable:
                values.extend(x.get_upper_bounds())

        for parameter, x in self.parameters.items():
            if x.is_variable:
                values.extend(x.get_upper_bounds())

        if self.days_of_year is not None:
            if self.days_of_year.is_variable:
                values.extend(self.days_of_year.get_upper_bounds())

        if self.y.is_variable:
            values.extend(self.y.get_upper_bounds())

        return np.array(values)
    
    def get_double_lower_bounds(self):
        """Returns an array of the lower bounds of the variables."""
        values = []

        for node, x in self.nodes.items():
            if x.is_variable:
                values.extend(x.get_lower_bounds())

        for parameter, x in self.parameters.items():
            if x.is_variable:
                values.extend(x.get_lower_bounds())

        if self.days_of_year is not None:
            if self.days_of_year.is_variable:
                values.extend(self.days_of_year.get_lower_bounds())

        if self.y.is_variable:
            values.extend(self.y.get_lower_bounds())

        return np.array(values)

    def value(self, ts, scenario_index):
        """Calculate the interpolate Rbf value from the current state."""
        # Use the cached node and parameter orders so that the exogenous inputs
        # are in the correct order.
        nodes = self._node_order
        parameters = self._parameter_order
        days_of_year = self.days_of_year

        # Create the arguments for the Rbf function.
        args = []
        for node in nodes:
            if isinstance(node, Storage):
                # Storage nodes use the current volume
                x = node.current_pc[scenario_index.global_id]
            else:
                # Other nodes are based on the flow
                x = node.flow[scenario_index.global_id]
            args.append(x)

        for parameter in parameters:
            x = parameter.get_value(scenario_index)
            args.append(x)

        if days_of_year is not None:
            # Normalise DoY to be between 0 and 1.
            x = 2 * np.pi * (ts.dayofyear - 1) / 365
            args.append(np.sin(x))
            args.append(np.cos(x))

        # Perform interpolation.
        return max(self._rbf_func(*args), 0)

    @classmethod
    def load(cls, model, data):
        y = RbfData(**data.pop('y'))
        days_of_year = data.pop('days_of_year', None)
        if days_of_year is not None:
            days_of_year = RbfData(**days_of_year)

        nodes = {}
        for node_name, node_data in data.pop('nodes', {}).items():
            node = model._get_node_from_ref(model, node_name)
            nodes[node] = RbfData(**node_data)

        parameters = {}
        for param_name, param_data in data.pop('parameters', {}).items():
            parameter = load_parameter(model, param_name)
            parameters[parameter] = RbfData(**param_data)

        if 'is_variable' in data:
            raise ValueError('The RbfParameter does not support specifying the `is_variable` key '
                             'at the root level of its definition. Instead specify individual items '
                             '(e.g. nodes or parameters) to be variables instead.')

        return cls(model, y, nodes=nodes, parameters=parameters, days_of_year=days_of_year, **data)

RbfParameter.register()


# TODO write a test for this. Perhaps abstract common elements from this with above class
class RbfVolumeParameter(Parameter):
    """ A simple Rbf parameter that uses day of year and volume for interpolation.
    """
    def __init__(self, model, node, days_of_year, volume_proportions, y, rbf_kwargs=None, **kwargs):
        super(RbfVolumeParameter, self).__init__(model, **kwargs)

        self.node = node
        self.days_of_year = days_of_year
        self.volume_proportions = volume_proportions
        self.y = y
        self.rbf_kwargs = rbf_kwargs
        self._rbf_func = None
        # TODO expose variables (e.g. epsilon, the y vector).

    def reset(self):
        # Create the Rbf object here.
        # This is done in `reset` rather than `setup` because
        # we wish to have support for optimising some of the Rbf parameters.
        # Therefore it needs recreating each time.

        # Normalise DoY to be between 0 and 1.
        norm_doy = self.days_of_year / 366
        # Convention here is that DoY is the first independent variable.
        self._rbf_func = Rbf(norm_doy, self.volume_proportions, self.y)

    def value(self, ts, scenario_index):

        norm_day = ts.dayofyear / 366
        volume_pc = self.node.current_pc
        # Perform interpolation.
        return self._rbf_func(norm_day, volume_pc)



class PeroidicFlowChange(Parameter):
    def __init__(self, model, node, calculation_interval, return_no_change, **kwargs):
        super().__init__(model, **kwargs)
        self._node = node
        self._calculation_interval = calculation_interval
        self._return_no_change = return_no_change

    def setup(self):
        super().setup()
        self.sc_comb = len(self.model.scenarios.combinations)
        self.nyears = self.model.timestepper.end.year - self.model.timestepper.start.year + 1
        self.n_ts = len(self.model.timestepper)

        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        if self.model.timestepper.delta == "M":
            self.previous_inflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        elif self.model.timestepper.delta == "D":
            self.previous_inflow_recorder = np.zeros((366, self.sc_comb, self.nyears,), np.float64)

        self.inflow_1901_2001 = pd.read_csv("data/GERD_inflow_1901_2001.csv").set_index("Year")
        self.historical_inflow = np.zeros((self.nyears-1+len(self.inflow_1901_2001.index.to_list()), self.sc_comb,), np.float64)
        for y in range(len(self.inflow_1901_2001.index.to_list())):
            for s in range(self.sc_comb):
                self.historical_inflow[y,s] = self.inflow_1901_2001.at[y+1901,"GERD_inflow"]

        self.change_in_mean = np.zeros((self.sc_comb,), np.float64)
        for s in range(self.sc_comb):
            self.change_in_mean[s]=1

        self.change_in_mean_values = np.zeros((self.nyears, self.sc_comb,), np.float64)

    def reset(self):

        self.iteration_check = np.zeros((self.n_ts, self.sc_comb,), np.float64)

        if self.model.timestepper.delta == "M":
            self.previous_inflow_recorder = np.zeros((12, self.sc_comb, self.nyears,), np.float64)
        elif self.model.timestepper.delta == "D":
            self.previous_inflow_recorder = np.zeros((366, self.sc_comb, self.nyears,), np.float64)

        self.inflow_1901_2001 = pd.read_csv("data/GERD_inflow_1901_2001.csv").set_index("Year")
        self.historical_inflow = np.zeros((self.nyears-1+len(self.inflow_1901_2001.index.to_list()), self.sc_comb,), np.float64)
        for y in range(len(self.inflow_1901_2001.index.to_list())):
            for s in range(self.sc_comb):
                self.historical_inflow[y,s] = self.inflow_1901_2001.at[y+1901,"GERD_inflow"]

        self.change_in_mean = np.zeros((self.sc_comb,), np.float64)
        for s in range(self.sc_comb):
            self.change_in_mean[s]=1

        self.change_in_mean_values = np.zeros((self.nyears, self.sc_comb,), np.float64)


    def update_inflow(self, timestep, sc_index, iteration):
        #This method updates the previous inflow and outflow arrays, which are key to simulating the Washington Proposal
        if ((timestep.month != 1 and self.model.timestepper.delta == "M") or ((timestep.month + timestep.day > 2) and self.model.timestepper.delta == "D")) and iteration == 1:
            if self.model.timestepper.delta == "M":
                self.previous_inflow_recorder[self.month_index-1,sc_index.global_id,self.year_index] = self._node.prev_flow[sc_index.global_id]
            elif self.model.timestepper.delta == "D":
                self.previous_inflow_recorder[self.day_index-1,sc_index.global_id,self.year_index] = self._node.prev_flow[sc_index.global_id]
        elif timestep.index != 0 and iteration == 0:
            if self.model.timestepper.delta == "M":
                if timestep.month != 1:
                    self.previous_inflow_recorder[self.month_index-1,sc_index.global_id,self.year_index] = self._node.prev_flow[sc_index.global_id]
                else:
                    self.previous_inflow_recorder[11,sc_index.global_id,self.year_index-1] = self._node.prev_flow[sc_index.global_id]                    
            elif self.model.timestepper.delta == "D":
                if (timestep.month + timestep.day > 2):
                    self.previous_inflow_recorder[self.day_index-1,sc_index.global_id,self.year_index] = self._node.prev_flow[sc_index.global_id]
                else:
                    self.previous_inflow_recorder[self.leap_year(timestep.year-1)[1]-1,sc_index.global_id,self.year_index-1] = self._node.prev_flow[sc_index.global_id]

    def leap_year(self, year):
        #This method is to determine whether a years leap or not
        #Then passes back the index of 1st July and the number of days in the year
        if (year % 4) == 0:
            if (year % 100) == 0:
                if (year % 400) == 0:
                    return 182, 366 #leap
                else:
                    return 181, 365 #not leap
            else:
                return 182, 366 #leap
        else:
            return 181, 365 # not leap

    def change_in_decadal_average_flow(self, timestep, sc_index):
        #Append past year infow to the historical inflows
        if self.model.timestepper.delta == "M":
            if timestep.month == 7 and self.year_index>0:
                self.historical_inflow[self.year_index+len(self.inflow_1901_2001.index.to_list())-1,sc_index.global_id] = (self.previous_inflow_recorder[0:self.month_index,sc_index.global_id,self.year_index].sum(axis=0)+self.previous_inflow_recorder[6:12,sc_index.global_id,self.year_index-1].sum(axis=0))* 30.5/1000
        elif self.model.timestepper.delta == "D":
            if timestep.month == 7 and timestep.day == 1 and self.year_index>0:
                self.historical_inflow[self.year_index+len(self.inflow_1901_2001.index.to_list())-1,sc_index.global_id] = (self.previous_inflow_recorder[0:self.day_index,sc_index.global_id,self.year_index].sum(axis=0) + self.previous_inflow_recorder[self.leap_year(timestep.year-1)[0]:367,sc_index.global_id,self.year_index-1].sum(axis=0))/1000

        if timestep.month == 7 and self.year_index>0:
            if self.year_index<self._calculation_interval-1 or self._return_no_change:
                self.change_in_mean[sc_index.global_id] = 1
            elif self.year_index==self._calculation_interval-1 or self.year_index==self._calculation_interval*2-1 or self.year_index==self._calculation_interval*3-1 or self.year_index==self._calculation_interval*4-1 or self.year_index==self._calculation_interval*5-1 or self.year_index==self._calculation_interval*6-1 or self.year_index==self._calculation_interval*7-1 or self.year_index==self._calculation_interval*8-1 or self.year_index==self._calculation_interval*9-1 or self.year_index==self._calculation_interval*10-1 or self.year_index==self._calculation_interval*11-1 or self.year_index==self._calculation_interval*12-1 or self.year_index==self._calculation_interval*13-1:
                index_from = self.year_index+len(self.inflow_1901_2001.index.to_list())-self._calculation_interval
                index_to = self.year_index+len(self.inflow_1901_2001.index.to_list())
                decadal_flow = self.historical_inflow[index_from:index_to,sc_index.global_id]
                historical_flow_values = self.historical_inflow[0:1+len(self.inflow_1901_2001.index.to_list()),sc_index.global_id]
                self.change_in_mean[sc_index.global_id] = np.mean(decadal_flow, axis = 0)/np.mean(historical_flow_values, axis = 0)

        self.change_in_mean_values[self.year_index, sc_index.global_id] = self.change_in_mean[sc_index.global_id]

    def value(self, ts, scenario_index):

        self.year_index = ts.year-self.model.timestepper.start.year
        self.month_index = ts.month-1
        self.day_index = ts.dayofyear-1

        if ((ts.month != 1 and self.model.timestepper.delta == "M") or ((ts.month + ts.day > 2) and self.model.timestepper.delta == "D")) and self.iteration_check[ts.index, scenario_index.global_id]==1:
            self.update_inflow(timestep = ts, sc_index = scenario_index, iteration = self.iteration_check[ts.index, scenario_index.global_id])

        if ts.index != 0 and self.iteration_check[ts.index, scenario_index.global_id]==0:
            self.update_inflow(timestep = ts, sc_index = scenario_index, iteration = self.iteration_check[ts.index, scenario_index.global_id])
            self.iteration_check[ts.index, scenario_index.global_id] = 1

        self.change_in_decadal_average_flow(timestep = ts, sc_index = scenario_index)

        if False and scenario_index.global_id == (self.sc_comb-1) and ts.year == self.model.timestepper.end.year and ts.month == self.model.timestepper.end.month and ts.day == self.model.timestepper.end.day:
            path = os.path.join(os.getcwd(),"outputs")
            os.makedirs(path, exist_ok=True)
            df_out = pd.DataFrame(data = self.change_in_mean_values, dtype = float)
            df_out.to_csv(str(path+"/"+str('change_in_mean_values.csv')))

        return self.change_in_mean[scenario_index.global_id]
            
    @classmethod
    def load(cls, model, data):
        node = model._get_node_from_ref(model, data.pop("node"))
        calculation_interval = data.pop("calculation_interval")
        return_no_change = data.pop("return_no_change")
        return cls(model, node, calculation_interval, return_no_change, **data)
PeroidicFlowChange.register()


class TriggerTrend(Parameter):
    def __init__(self, model, parameter, trend_parameter, max_value, min_value, **kwargs):
        super().__init__(model, **kwargs)
        self._parameter = None
        self.parameter = parameter
        self._trend_parameter = None
        self.trend_parameter = trend_parameter
        self._max_value = max_value
        self._min_value = min_value

    parameter = parameter_property("_parameter")
    trend_parameter = parameter_property("_trend_parameter")

    def value(self, ts, scenario_index):
        value1 = self._parameter.get_value(scenario_index) * self._trend_parameter.get_value(scenario_index)
        value2 = max(value1, self._min_value)
        value3 = min(value2, self._max_value)
        return value3

    @classmethod
    def load(cls, model, data):
        parameter = load_parameter(model, data.pop("parameter"))
        trend_parameter = load_parameter(model, data.pop("trend_parameter"))
        max_value = data.pop("max_value")
        min_value = data.pop("min_value")
        return cls(model, parameter, trend_parameter, max_value, min_value, **data)
TriggerTrend.register()

class IrrigationWaterRequirement(Parameter):
    def __init__(self, model, eff_rainfall_parameter, et_parameter, crop_factor_parameter, crop_area,
                 application_efficiency, conveyance_efficiency, crop_name, conversion_factor = 1, **kwargs):
        super().__init__(model, **kwargs)

        self.eff_rainfall_parameter = eff_rainfall_parameter
        self.et_parameter = et_parameter
        self.crop_factor_parameter = crop_factor_parameter
        self.crop_area = crop_area
        self.application_efficiency = application_efficiency
        self.conveyance_efficiency = conveyance_efficiency
        self.crop_name = crop_name
        self.conversion_factor = conversion_factor

    def value(self, timestep, scenario_index):

        effective_rainfall = self.eff_rainfall_parameter.get_value(scenario_index)
        et = self.et_parameter.get_value(scenario_index)
        crop_water_factor = self.crop_factor_parameter.get_value(scenario_index)
      
        # Calculate crop water requirement
        if effective_rainfall > crop_water_factor * et:
            # No crop water requirement if there is enough rainfall
            crop_water_requirement = 0.0
        else:
            # Irrigation required to meet shortfall in rainfall
            crop_water_requirement = (crop_water_factor * et - effective_rainfall) * self.crop_area

        # Calculate overall efficiency
        efficiency = self.application_efficiency * self.conveyance_efficiency

        # TODO error checking on division by zero
        irrigation_water_requirement = crop_water_requirement / efficiency * self.conversion_factor
        return irrigation_water_requirement

    @classmethod
    def load(cls, model, data):
        eff_rainfall_parameter = load_parameter(model, data.pop('eff_rainfall_parameter'))
        et_parameter = load_parameter(model, data.pop('et_parameter'))
        crop_factor_parameter = load_parameter(model, data.pop('crop_water_factor_parameter'))
        crop_area = data.pop("crop_area")
        application_efficiency = data.pop("application_efficiency")
        conveyance_efficiency = data.pop("conveyance_efficiency")
        crop_name = data.pop("crop_name")
        if "conversion_factor" in data:
            conversion_factor = data.pop("conversion_factor")
        return cls(model, eff_rainfall_parameter, et_parameter, crop_factor_parameter, crop_area,
                    application_efficiency, conveyance_efficiency, crop_name, conversion_factor, **data)

IrrigationWaterRequirement.register()


class FlowChangeTimestepToTimestep(NumpyArrayNodeRecorder):
    def setup(self):
        super().setup()
        self.sc_comb = len(self.model.scenarios.combinations)
        self.n_ts = len(self.model.timestepper)
        self.flow_values = np.zeros((self.n_ts, self.sc_comb,), np.float64)
        self._data = np.zeros((self.n_ts, self.sc_comb))

    def reset(self):
        self._data[:, :] = 0.0

    def after(self):
        ts = self.model.timestepper.current
        for scenario_index in self.model.scenarios.combinations:
            self.flow_values[ts.index,scenario_index.global_id] = self.node.flow[scenario_index.global_id]
            if ts.index < 1:
                self._data[ts.index,scenario_index.global_id] = 0
            else:
                self._data[ts.index,scenario_index.global_id] = self.flow_values[ts.index,scenario_index.global_id] - self.flow_values[ts.index-1,scenario_index.global_id]
        return 0

    def to_dataframe(self):
        """ Return a `pandas.DataFrame` of the recorder data

        This DataFrame contains a MultiIndex for the columns with the recorder name
        as the first level and scenario combination names as the second level. This
        allows for easy combination with multiple recorder's DataFrames
        """
        index = self.model.timestepper.datetime_index
        sc_index = self.model.scenarios.multiindex

        return pd.DataFrame(data=np.array(self._data), index=index, columns=sc_index)

FlowChangeTimestepToTimestep.register()




class HydropowerTargetParameterWithVaribaleTailwater(Parameter):
    """ A parameter that returns flow from a hydropower generation target.

    This parameter calculates the flow required to generate a particular hydropower production target. It
    is intended to be used on a node representing a turbine where a particular production target is required
    each time-step.

    Parameters
    ----------

    target : Parameter instance
        Hydropower production target. Units should be in units of energy per day.
    water_elevation_parameter : Parameter instance (default=None)
        Elevation of water entering the turbine. The difference of this value with the `turbine_elevation` gives
        the working head of the turbine.
    max_flow : Parameter instance (default=None)
        Upper bounds on the calculated flow. If set the flow returned by this parameter is at most the value
        of the max_flow parameter.
    min_flow : Parameter instance (default=None)
        Lower bounds on the calculated flow. If set the flow returned by this parameter is at least the value
        of the min_flow parameter.
    min_head : double (default=0.0)
        Minimum head for flow to occur. If actual head is less than this value zero flow is returned.
    turbine_elevation_parameter : Parameter instance (default=None)
        Elevation of the turbine itself. The difference between the `water_elevation` and this value gives
        the working head of the turbine. It is recommended to use 'InterpolatedLevelParameter'.
    efficiency : float (default=1.0)
        The efficiency of the turbine.
    density : float (default=1000.0)
        The density of water.
    flow_unit_conversion : float (default=1.0)
        A factor used to transform the units of flow to be compatible with the equation here. This
        should convert flow to units of :math:`m^3/second`
    energy_unit_conversion : float (default=1e-6)
        A factor used to transform the units of total energy. Defaults to 1e-6 to return :math:`MW`.

    Notes
    -----
    The inverse hydropower calculation uses the following equation.

    .. math:: q = \\frac{P}{\\rho * g * \\delta H}

    The energy rate in should be converted to units of MW. The returned flow rate in should is
    converted from units of :math:`m^3` per second to those used by the model using the `flow_unit_conversion` parameter.

    Head is calculated from the given `water_elevation_parameter` and `turbine_elevation_parameter` value. If water elevation
    is given then head is the difference in elevation between the water and the turbine. If water elevation parameter
    is `None` then the head is simply the turbine elevation.

    See Also
    --------
    pywr.recorders.TotalHydroEnergyRecorder
    pywr.recorders.HydropowerRecorder

    """
    def __init__(self, model, target, water_elevation_parameter=None, max_flow=None, min_flow=None,
                 turbine_elevation_parameter=None, efficiency=1.0, density=1000, min_head=0.0,
                 flow_unit_conversion=1.0, energy_unit_conversion=1e-6, **kwargs):
        super(HydropowerTargetParameterWithVaribaleTailwater, self).__init__(model, **kwargs)

        self.target = target
        self.water_elevation_parameter = water_elevation_parameter
        self.max_flow = max_flow
        self.min_flow = min_flow
        self.min_head = min_head
        self.turbine_elevation_parameter = turbine_elevation_parameter
        self.efficiency = efficiency
        self.density = density
        self.flow_unit_conversion = flow_unit_conversion
        self.energy_unit_conversion = energy_unit_conversion

    def value(self, ts, scenario_index):
        
        power = self.target.get_value(scenario_index)

        if self.water_elevation_parameter is not None:
            head = self.water_elevation_parameter.get_value(scenario_index)
            if self.turbine_elevation_parameter is not None:
                head -= self.turbine_elevation_parameter.get_value(scenario_index)
        elif self.turbine_elevation is not None:
            head = self.turbine_elevation_parameter.get_value(scenario_index)
        else:
            raise ValueError('One or both of storage_node or level must be set.')

        # -ve head is not valid

        head = max(head, 0.0)



        # Apply minimum head threshold.
        if head < self.min_head:
            return 0.0

        # Get the flow from the current node
        q = inverse_hydropower_calculation(power, head, 0.0, self.efficiency, density=self.density,
                                           flow_unit_conversion=self.flow_unit_conversion,
                                           energy_unit_conversion=self.energy_unit_conversion)

        if math.isinf(q):
            q = 0.01

        # Bound the flow if required
        if self.max_flow is not None:
            q = min(self.max_flow.get_value(scenario_index), q)
        if self.min_flow is not None:
            q = max(self.min_flow.get_value(scenario_index), q)

        try:
            assert q >= 0.0
        except:
            q=0

        return q

    @classmethod
    def load(cls, model, data):

        target = load_parameter(model, data.pop("target"))
        if "water_elevation_parameter" in data:
            water_elevation_parameter = load_parameter(model, data.pop("water_elevation_parameter"))
        else:
            water_elevation_parameter = None

        if "turbine_elevation_parameter" in data:
            turbine_elevation_parameter = load_parameter(model, data.pop("turbine_elevation_parameter"))
        else:
            turbine_elevation_parameter = None

        if "max_flow" in data:
            max_flow = load_parameter(model, data.pop("max_flow"))
        else:
            max_flow = None

        if "min_flow" in data:
            min_flow = load_parameter(model, data.pop("min_flow"))
        else:
            min_flow = None

        return cls(model, target, water_elevation_parameter=water_elevation_parameter, turbine_elevation_parameter=turbine_elevation_parameter,
                   max_flow=max_flow, min_flow=min_flow, **data)
HydropowerTargetParameterWithVaribaleTailwater.register()


class HydropowerRecorderWithVaribaleTailwater(NumpyArrayNodeRecorder):
    """ Calculates the power production using the hydropower equation

    This recorder saves an array of the hydrpower production in each timestep. It can be converted to a dataframe
    after a model run has completed. It does not calculate total energy production.

    Parameters
    ----------

    water_elevation_parameter : Parameter instance (default=None)
        Elevation of water entering the turbine. The difference of this value with the `turbine_elevation` gives
        the working head of the turbine.
    turbine_elevation_parameter : Parameter instance (default=None)
        Elevation of the turbine itself. The difference between the `water_elevation` and this value gives
        the working head of the turbine. It is recommended to use 'InterpolatedLevelParameter'.
    efficiency : float (default=1.0)
        The efficiency of the turbine.
    density : float (default=1000.0)
        The density of water.
    flow_unit_conversion : float (default=1.0)
        A factor used to transform the units of flow to be compatible with the equation here. This
        should convert flow to units of :math:`m^3/second`
    energy_unit_conversion : float (default=1e-6)
        A factor used to transform the units of total energy. Defaults to 1e-6 to return :math:`MW`.

    Notes
    -----
    The hydropower calculation uses the following equation.

    .. math:: P = \\rho * g * \\delta H * q

    The flow rate in should be converted to units of :math:`m^3` per second using the `flow_unit_conversion` parameter.

    Head is calculated from the given `water_elevation_parameter` and `turbine_elevation` value. If water elevation
    is given then head is the difference in elevation between the water and the turbine. If water elevation parameter
    is `None` then the head is simply the turbine elevation.


    See Also
    --------
    TotalHydroEnergyRecorder
    pywr.parameters.HydropowerTargetParameter

    """
    def __init__(self, model, node, water_elevation_parameter=None, turbine_elevation_parameter=None, efficiency=1.0, density=1000,
                 flow_unit_conversion=1.0, energy_unit_conversion=1e-6, **kwargs):
        super(HydropowerRecorderWithVaribaleTailwater, self).__init__(model, node, **kwargs)

        self.water_elevation_parameter = water_elevation_parameter
        self.turbine_elevation_parameter = turbine_elevation_parameter
        self.efficiency = efficiency
        self.density = density
        self.flow_unit_conversion = flow_unit_conversion
        self.energy_unit_conversion = energy_unit_conversion

    def setup(self):
        super().setup()
        self.sc_comb = len(self.model.scenarios.combinations)
        self.n_ts = len(self.model.timestepper)
        self._data = np.zeros((self.n_ts, self.sc_comb))

    def reset(self):
        self._data[:, :] = 0.0

    def after(self):
        ts = self.model.timestepper.current

        for scenario_index in self.model.scenarios.combinations:

            if self.water_elevation_parameter is not None:
                head = self.water_elevation_parameter.get_value(scenario_index)
                if self.turbine_elevation_parameter is not None:                    
                    head -= self.turbine_elevation_parameter.get_value(scenario_index)
            elif self.turbine_elevation_parameter is not None:
                head = self.turbine_elevation_parameter.get_value(scenario_index)
            else:
                raise ValueError('One or both of storage_node or level must be set.')

            # -ve head is not valid
            head = max(head, 0.0)
            # Get the flow from the current node
            q = self.node.flow[scenario_index.global_id]
            power = hydropower_calculation(q, head, 0.0, self.efficiency, density=self.density,
                                             flow_unit_conversion=self.flow_unit_conversion,
                                             energy_unit_conversion=self.energy_unit_conversion)

            self._data[ts.index, scenario_index.global_id] = power

    def to_dataframe(self):
        """ Return a `pandas.DataFrame` of the recorder data

        This DataFrame contains a MultiIndex for the columns with the recorder name
        as the first level and scenario combination names as the second level. This
        allows for easy combination with multiple recorder's DataFrames
        """
        index = self.model.timestepper.datetime_index
        sc_index = self.model.scenarios.multiindex

        return pd.DataFrame(data=np.array(self._data), index=index, columns=sc_index)


    @classmethod
    def load(cls, model, data):
        from pywr.parameters import load_parameter
        node = model._get_node_from_ref(model, data.pop("node"))
        if "water_elevation_parameter" in data:
            water_elevation_parameter = load_parameter(model, data.pop("water_elevation_parameter"))
        else:
            water_elevation_parameter = None

        if "turbine_elevation_parameter" in data:
            turbine_elevation_parameter = load_parameter(model, data.pop("turbine_elevation_parameter"))
        else:
            turbine_elevation_parameter = None

        return cls(model, node, water_elevation_parameter=water_elevation_parameter,turbine_elevation_parameter=turbine_elevation_parameter, **data)
HydropowerRecorderWithVaribaleTailwater.register()


class AnnualHydroEnergyRecorder(Recorder):
    """Abstract class for recording cumulative annual differences between actual flow and max_flow.

    This abstract class can be subclassed to calculate statistics of differences between cumulative
    annual actual flow and max_flow on multiple nodes. The abstract class records the cumulative
    actual flow and max_flow from multiple nodes and provides an internal data attribute on which
    to store a derived statistic. A reset day and month control the day on which the cumulative
    data is reset to zero.

    Parameters
    ----------
    model : `pywr.core.Model`
    nodes : iterable of `pywr.core.Node`
        Iterable of Node instances to record.
    reset_month, reset_day : int
        The month and day in which the cumulative actual and max_flow are reset to zero.

    Notes
    -----
    If the first time-step of a simulation does not align with `reset_day` and `reset_month` then
    the first period of the model will be less than one year in length.
    """

    def __init__(self, model, nodes, water_elevation_parameter=None, turbine_elevation_parameter=None, efficiency=1.0, density=1000,
                 flow_unit_conversion=1.0, energy_unit_conversion=1e-6, reset_day=1, reset_month=1, **kwargs):
        temporal_agg_func = kwargs.pop('temporal_agg_func', 'mean')
        super().__init__(model, **kwargs)
        self.nodes = [n for n in nodes]

        #self.water_elevation_parameter = water_elevation_parameter
        self.water_elevation_parameter = list(water_elevation_parameter)
        self.turbine_elevation_parameter = list(turbine_elevation_parameter)
        self.efficiency = efficiency
        self.density = density
        self.flow_unit_conversion = flow_unit_conversion
        self.energy_unit_conversion = energy_unit_conversion
        self._temporal_aggregator = Aggregator(temporal_agg_func)
        # Validate the reset day and month
        # date will raise a ValueError if invalid. We use a non-leap year to ensure
        # 29th February is an invalid reset day.
        datetime.date(1999, reset_month, reset_day)

        self.reset_day = reset_day
        self.reset_month = reset_month

        for p in self.water_elevation_parameter:
            p.parents.add(self)

        for p in self.turbine_elevation_parameter:
            p.parents.add(self)


    def setup(self):
        ncomb = len(self.model.scenarios.combinations)
        nts = len(self.model.timestepper)

        start = self.model.timestepper.start
        end_year = self.model.timestepper.end.year
        self.extra_year = 0
        nyears = end_year - start.year + 1
        if start.day != self.reset_day or start.month != self.reset_month:
            nyears += 1
            self.extra_year = 1

        self._data = np.zeros((nyears, ncomb,), np.float64)

        if self.model.timestepper.delta == "D":
            self.energy_ts_level = np.zeros((nyears, 366, ncomb,), np.float64)
        else:
            self.energy_ts_level = np.zeros((nyears, 12, ncomb,), np.float64)

        self._annual_energy = np.zeros_like(self._data)
        self._current_year_index = 0

    def reset(self):
        self._data[...] = 0
        self._annual_energy[...] = 0
        self.energy_ts_level [...] = 0

        self._current_year_index = -1
        self._last_reset_year = -1

    def before(self):

        ts = self.model.timestepper.current
        if ts.year != self._last_reset_year:
            # I.e. we're in a new year and ...
            # ... we're at or past the reset month/day
            if ts.month > self.reset_month or \
                    (ts.month == self.reset_month and ts.day >= self.reset_day):
                self._current_year_index += 1
                self._last_reset_year = ts.year

            if self._current_year_index < 0:
                # reset date doesn't align with the start of the model
                self._current_year_index = 0

    def after(self):
        ts = self.model.timestepper.current
        days = ts.days
        i = self._current_year_index
        nodes_length = range(0,len(self.nodes),1)

        for scenario_index in self.model.scenarios.combinations:
            j = scenario_index.global_id

            energy_temp = 0
            for node_index in nodes_length:
                head = self.water_elevation_parameter[node_index].get_value(scenario_index)
                head -= self.turbine_elevation_parameter[node_index].get_value(scenario_index)
                head = max(head, 0.0)
                # Get the flow from the current node
                q = self.nodes[node_index].flow[scenario_index.global_id]
                power = hydropower_calculation(q, head, 0.0, self.efficiency, density=self.density,
                                                flow_unit_conversion=self.flow_unit_conversion,
                                                energy_unit_conversion=self.energy_unit_conversion)

                energy_temp += power * days * 24

            if self.model.timestepper.delta == "D":
                self.energy_ts_level[i,ts.dayofyear-1,j] = energy_temp
            elif self.model.timestepper.delta == "M":
                self.energy_ts_level[i,ts.month-1,j] = energy_temp

            self._annual_energy[i, j] = sum(self.energy_ts_level[i,:,j])


            self._data[i, j] = self._annual_energy[i, j]   
        
        return 0

    def values(self):
        """Compute a value for each scenario using `temporal_agg_func`.
        """
        return self._temporal_aggregator.aggregate_2d(self._data, axis=0, ignore_nan=self.ignore_nan)

    def to_dataframe_annual(self):
        """ Return a `pandas.DataFrame` of the recorder data

        This DataFrame contains a MultiIndex for the columns with the recorder name
        as the first level and scenario combination names as the second level. This
        allows for easy combination with multiple recorder's DataFrames
        """
        index = np.asarray(range(self.model.timestepper.start.year,self.model.timestepper.end.year+1+self.extra_year,1),dtype=np.float64)
        sc_index = self.model.scenarios.multiindex

        df = pd.DataFrame(data=np.array(self._data), index=index, columns=sc_index)
        try:
            df.to_csv("outputs/"+str(self.name)+".csv")
        except:
            pass

        return pd.DataFrame(data=np.array(self._data), index=index, columns=sc_index)

    def finish(self):
        self.to_dataframe_annual()


    @classmethod
    def load(cls, model, data):
        from pywr.parameters import load_parameter
        nodes = [model._get_node_from_ref(model, node_name) for node_name in data.pop('nodes')]
        if "water_elevation_parameter" in data:
            water_elevation_parameter = [load_parameter(model, p) for p in data.pop("water_elevation_parameter")]
        else:
            water_elevation_parameter = None

        if "turbine_elevation_parameter" in data:
            turbine_elevation_parameter = [load_parameter(model, p) for p in data.pop("turbine_elevation_parameter")]
        else:
            turbine_elevation_parameter = None    

        return cls(model, nodes, water_elevation_parameter = water_elevation_parameter, turbine_elevation_parameter = turbine_elevation_parameter, **data)

AnnualHydroEnergyRecorder.register()






class AbstractAnnualRecorder(Recorder):
    """Abstract class for recording cumulative annual differences between actual flow and max_flow.

    This abstract class can be subclassed to calculate statistics of differences between cumulative
    annual actual flow and max_flow on multiple nodes. The abstract class records the cumulative
    actual flow and max_flow from multiple nodes and provides an internal data attribute on which
    to store a derived statistic. A reset day and month control the day on which the cumulative
    data is reset to zero.

    Parameters
    ----------
    model : `pywr.core.Model`
    nodes : iterable of `pywr.core.Node`
        Iterable of Node instances to record.
    reset_month, reset_day : int
        The month and day in which the cumulative actual and max_flow are reset to zero.
    temporal_agg_func : str or callable (default="mean")
        Aggregation function used over time when computing a value per scenario. This can be used
        to return, for example, the median flow over a simulation. For aggregation over scenarios
        see the `agg_func` keyword argument.
    Notes
    -----
    If the first time-step of a simulation does not align with `reset_day` and `reset_month` then
    the first period of the model will be less than one year in length.
    """
    def __init__(self, model, nodes, reset_day=1, reset_month=1, **kwargs):
        temporal_agg_func = kwargs.pop('temporal_agg_func', 'mean')
        super().__init__(model, **kwargs)
        self._temporal_aggregator = Aggregator(temporal_agg_func)
        self.nodes = [n for n in nodes]

        # Validate the reset day and month
        # date will raise a ValueError if invalid. We use a non-leap year to ensure
        # 29th February is an invalid reset day.
        datetime.date(1999, reset_month, reset_day)

        self.reset_day = reset_day
        self.reset_month = reset_month


    @classmethod
    def load(cls, model, data):
        nodes = [model._get_node_from_ref(model, node_name) for node_name in data.pop('nodes')]
        return cls(model, nodes, **data)

    def setup(self):
        ncomb = len(self.model.scenarios.combinations)
        nts = len(self.model.timestepper)

        start = self.model.timestepper.start
        end_year = self.model.timestepper.end.year
        self.extra_year = 0
        nyears = end_year - start.year + 1
        if start.day != self.reset_day or start.month != self.reset_month:
            nyears += 1
            self.extra_year = 1

        self._data = np.zeros((nyears, ncomb,), np.float64)

        if self.model.timestepper.delta == "D":
            self.max_flow_ts_level = np.zeros((nyears, 366, ncomb,), np.float64)
            self.actual_flow_ts_level = np.zeros((nyears, 366, ncomb,), np.float64)
        elif self.model.timestepper.delta == "M":
            self.max_flow_ts_level = np.zeros((nyears, 12, ncomb,), np.float64)
            self.actual_flow_ts_level = np.zeros((nyears, 12, ncomb,), np.float64)

        self._max_flow = np.zeros_like(self._data)
        self._actual_flow = np.zeros_like(self._data)
        self._current_year_index = 0

    def reset(self):
        self._data[...] = 0
        self._max_flow[...] = 0
        self._actual_flow[...] = 0
        self.max_flow_ts_level[...] = 0
        self.actual_flow_ts_level[...] = 0

        self._current_year_index = -1
        self._last_reset_year = -1

    def before(self):

        ts = self.model.timestepper.current
        if ts.year != self._last_reset_year:
            # I.e. we're in a new year and ...
            # ... we're at or past the reset month/day
            if ts.month > self.reset_month or \
                    (ts.month == self.reset_month and ts.day >= self.reset_day):
                self._current_year_index += 1
                self._last_reset_year = ts.year

            if self._current_year_index < 0:
                # reset date doesn't align with the start of the model
                self._current_year_index = 0

    def after(self):
        ts = self.model.timestepper.current
        i = self._current_year_index

        for scenario_index in self.model.scenarios.combinations:
            j = scenario_index.global_id

            max_flow = 0
            actual_flow = 0
            for node in self.nodes:
                max_flow += node.get_max_flow(scenario_index)
                actual_flow += node.flow[scenario_index.global_id]

            if self.model.timestepper.delta == "D":
                self.max_flow_ts_level[i, ts.dayofyear-1, j] = max_flow * ts.days
                self.actual_flow_ts_level[i, ts.dayofyear-1, j] = actual_flow * ts.days
            elif self.model.timestepper.delta == "M":
                self.max_flow_ts_level[i, ts.month-1, j] = max_flow * ts.days
                self.actual_flow_ts_level[i, ts.month-1, j] = actual_flow * ts.days            

            self._max_flow[i, j] = sum(self.max_flow_ts_level[i,:,j])
            self._actual_flow[i, j] = sum(self.actual_flow_ts_level[i,:,j])

        return 0

    def values(self):
        """Compute a value for each scenario using `temporal_agg_func`.
        """
        return self._temporal_aggregator.aggregate_2d(self._data, axis=0, ignore_nan=self.ignore_nan)

    def to_dataframe_annual(self):
        """ Return a `pandas.DataFrame` of the recorder data

        This DataFrame contains a MultiIndex for the columns with the recorder name
        as the first level and scenario combination names as the second level. This
        allows for easy combination with multiple recorder's DataFrames
        """
        index = np.asarray(range(self.model.timestepper.start.year,self.model.timestepper.end.year+1+self.extra_year,1),dtype=np.float64)
        sc_index = self.model.scenarios.multiindex

        df = pd.DataFrame(data=np.array(self._data), index=index, columns=sc_index)
        try:
            df.to_csv("outputs/"+str(self.name)+".csv")
        except:
            pass

        return pd.DataFrame(data=np.array(self._data), index=index, columns=sc_index)



class AnnualFlowRecorder(AbstractAnnualRecorder):
    """Recorder for the cumulative annual deficit across multiple nodes.

    This recorder calculates the cumulative annual absolute flow from multiple nodes.

    Parameters
    ----------
    model : `pywr.core.Model`
    nodes : iterable of `pywr.core.Node`
        Iterable of Node instances to record.
    reset_month, reset_day : int
        The month and day in which the cumulative actual and max_flow are reset to zero.

    Notes
    -----
    If the first time-step of a simulation does not align with `reset_day` and `reset_month` then
    the first period of the model will be less than one year in length.
    """
    def after(self):
        super(AnnualFlowRecorder, self).after()

        i = self._current_year_index

        for scenario_index in self.model.scenarios.combinations:
            j = scenario_index.global_id
            self._data[i, j] = self._actual_flow[i, j]
        return 0

    def finish(self):
        self.to_dataframe_annual()

AnnualFlowRecorder.register()



class AnnualSuppliedRatioRecorder(AbstractAnnualRecorder):
    """Recorder for cumulative annual ratio of supplied flow from multiples nodes.

    This recorder calculates the cumulative annual ratio of supplied flow to max_flow
    from multiple nodes.

    Parameters
    ----------
    model : `pywr.core.Model`
    nodes : iterable of `pywr.core.Node`
        Iterable of Node instances to record.
    reset_month, reset_day : int
        The month and day in which the cumulative actual and max_flow are reset to zero.

    Notes
    -----
    If the first time-step of a simulation does not align with `reset_day` and `reset_month` then
    the first period of the model will be less than one year in length.
    """
    def after(self):
        super(AnnualSuppliedRatioRecorder, self).after()

        i = self._current_year_index

        for scenario_index in self.model.scenarios.combinations:
            j = scenario_index.global_id
            try:
                self._data[i, j] = self._actual_flow[i, j] / self._max_flow[i, j]
            except ZeroDivisionError:
                self._data[i, j] = 1.0
        return 0

    def finish(self):
        self.to_dataframe_annual()
        
AnnualSuppliedRatioRecorder.register()
