import pandas as pd
import numpy as np
from ..utils.utils import getlogger
from ..utils.cost_utils import calculate_costs_with_df, populate_margin_functions

# Constants for margin calculations
# TODO: get rid of these magic numbers
PRE_COLLAR_MARGIN_RATE = 0.2  # 20% margin for pre-collar section
CENTRALISER_COST_FACTOR_LOW = 2/3
CENTRALISER_COST_FACTOR_HIGH = 4/3
CENTRALISER_DEPTH_OFFSET_LOW = -20
CENTRALISER_DEPTH_OFFSET_HIGH = 20


class CostStageCalculator:
    """
    Stores calculation methods required for the cost calculation pipeline.

    This class manages the calculations for various cost components associated with wellbore construction. 
    It uses provided cost rates and wellbore parameters to calculate drilling, time, material, and other costs. 
    Margin functions are applied to these costs to account for uncertainties and contingencies.

    Attributes
    ----------
    logger : Logger
        Logger instance for logging errors and information.
    cost_rates : dict
        Dictionary containing cost rates for different stages and components.
    wellbore_params : dict
        Dictionary containing wellbore parameters required for cost calculations.
    margin_functions : pd.DataFrame
        DataFrame containing margin functions used for cost calculations.
    stage_labels : list
        List of labels indicating the different stages of cost calculation.
    stage_calculators : dict
        Dictionary mapping stage labels to their corresponding cost calculation methods.

    Methods
    -------
    drilling_rate_params() -> dict
        Returns parameters required for calculating drilling rates.

    time_rate_params() -> dict
        Returns parameters required for calculating time rates.

    material_params() -> dict
        Returns parameters required for calculating material costs.

    other_params() -> dict
        Returns parameters required for calculating other costs.

    drilling_cost_rates() -> dict
        Returns cost rates specific to drilling.

    time_cost_rates() -> dict
        Returns cost rates specific to time-related expenses.

    material_cost_rates() -> dict
        Returns cost rates specific to materials.

    other_cost_rates() -> dict
        Returns cost rates specific to other miscellaneous costs.

    _initialise_margin_functions(margins_dict: dict) -> pd.DataFrame
        Initialises margin functions based on provided margin rates.

    calculate_drilling_components_cost() -> pd.DataFrame
        Calculates the costs associated with drilling components.

    calculate_drilling_rates_total_cost(base_sum: float) -> pd.Series
        Calculates the total cost for drilling rates including margins.

    calculate_time_components_cost() -> pd.DataFrame
        Calculates the costs associated with time-based components.

    calculate_material_components_cost() -> pd.DataFrame
        Calculates the costs associated with material components.

    calculate_other_components_cost() -> pd.DataFrame
        Calculates the costs associated with other miscellaneous components.
    """

    def __init__(self,
                 cost_rates,
                 wellbore_params,
                 margin_rates,
                 stage_labels):
        self.logger = getlogger()
        self.cost_rates = cost_rates
        self.wellbore_params = wellbore_params
        self.stage_labels = stage_labels
        self.margin_functions = self._initialise_margin_functions(margin_rates)

        self.stage_calculators = {
            'drilling_rates': self.calculate_drilling_components_cost,
            'time_rates': self.calculate_time_components_cost,
            'materials': self.calculate_material_components_cost,
            'others': self.calculate_other_components_cost
        }

    @property
    def drilling_rate_params(self):
        return self.wellbore_params['drilling_rates']

    @property
    def time_rate_params(self):
        return self.wellbore_params['time_rates']

    @property
    def material_params(self):
        return self.wellbore_params['materials']

    @property
    def other_params(self):
        return self.wellbore_params['others']

    @property
    def drilling_cost_rates(self):
        return self.cost_rates['drilling_rates']

    @property
    def time_cost_rates(self):
        return self.cost_rates['time_rates']

    @property
    def material_cost_rates(self):
        return self.cost_rates['materials']

    @property
    def other_cost_rates(self):
        return self.cost_rates['others']

    def _initialise_margin_functions(self, margins_dict) -> pd.DataFrame:
        return populate_margin_functions(margins_dict)

    def calculate_drilling_components_cost(self) -> pd.DataFrame:
        """
        Calculates the costs associated with drilling components.

        This method computes the drilling costs based on total well depth, section lengths, and diameters. 
        It includes costs for pilot holes and casing stages, incorporating different diameter rates and offsets.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the base, low, and high cost estimates for each drilling component.

        Raises
        ------
        KeyError
            If any required parameter is missing from `drilling_rate_params` or `drilling_cost_rates`.
        """
        try:
            #TODO: section drilling cost scaling factor - 1.5727 currently hardcoded
            cost_scaling_factor = 1.5727

            total_well_depth = self.drilling_rate_params["total_well_depth"]
            drilling_section_length_diameter = pd.concat([self.drilling_rate_params['section_lengths'],
                                                          self.drilling_rate_params['section_diameters']], axis=1)
            drilling_section_length_diameter.columns = ['length', 'diameter']

            pilot_hole_cost = total_well_depth * \
                self.drilling_cost_rates['pilot_hole_rate_per_meter']

            drilling_section_result = pd.DataFrame({
                'base': [pilot_hole_cost]
            }, index=['pilot_hole'])

            casing_stages_result = drilling_section_length_diameter.apply(
                lambda row: max(row['length'] * (
                    cost_scaling_factor * row['diameter'] - self.drilling_cost_rates['diameter_based_offset']), 0), axis=1)

            casing_stages_result = pd.DataFrame({
                'base': casing_stages_result
            })
            drilling_section_result = pd.concat(
                [drilling_section_result, casing_stages_result], axis=0)

            drilling_section_result[['low', 'high']] = np.nan
            drilling_section_result = drilling_section_result[[
                'low', 'base', 'high']]
            
            # print('\ndrilling_section_result')
            # print(drilling_section_result)

            return drilling_section_result
        except KeyError as e:
            self.logger.error(
                f"Error in calculating drilling rates: {e} at line {e.__traceback__.tb_lineno}")
            raise

    def calculate_drilling_rates_total_cost(self,
                                            base_sum) -> pd.Series:
        """
        Calculates the total cost for drilling rates, including margins.

        This method computes the low, base, and high cost estimates for drilling rates based on the 
        total well depth and error margins provided in `drilling_cost_rates`.

        Parameters
        ----------
        base_sum : float
            The base sum of drilling costs.

        Returns
        -------
        pd.Series
            A Series containing the low, base, and high cost estimates for drilling rates.
        """
        cost_margin = self.drilling_rate_params["total_well_depth"] * \
            self.drilling_cost_rates['drilling_rate_error_margin_per_meter']
        cost_low = base_sum - cost_margin
        cost_high = base_sum + cost_margin
        return pd.Series([cost_low, base_sum, cost_high], index=['low', 'base', 'high'])

    def calculate_time_components_cost(self) -> pd.DataFrame:
        """
        Calculates the costs associated with time-based components.

        This method computes the time-related costs for wellbore construction, including rig standby, 
        development, accommodation, telehandler, and generator fuel costs. It uses the required flow rate 
        and drilling time parameters for calculations.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the base, low, and high cost estimates for each time-related component.

        Raises
        ------
        ValueError
            If any calculation error occurs.
        KeyError
            If any required parameter is missing from `time_rate_params` or `time_cost_rates`.
        """
        try:
            flow_rate = self.time_rate_params["required_flow_rate"]
            drilling_time = self.time_rate_params["drilling_time"]
            base_costs = {
                'rig_standby_cost': self.time_cost_rates["rig_standby_rate"],
                'development_bail_surge_jet': flow_rate * self.time_cost_rates['development_bail_surge_jet_rate_per_hour'],
                'accommodation_cost': drilling_time * self.time_cost_rates['accommodation_meals_rate_per_day'],
                'site_telehandler_cost': drilling_time * self.time_cost_rates["site_telehandler_rate_per_day"],
                'site_generator_fuel_cost': drilling_time * self.time_cost_rates["site_generator_fuel_rate_per_day"]
            }

            time_rates_df = calculate_costs_with_df(
                base_values=base_costs,
                margin_functions=self.margin_functions.loc['time_rates'],
                index_labels=base_costs.keys()
            )

            # print('\ntime rates:')
            # print(time_rates_df)

            return time_rates_df

        except (ValueError, KeyError) as e:
            self.logger.error(
                f"Error in calculating time rates: {e} at line {e.__traceback__.tb_lineno}")
            raise

    def calculate_material_components_cost(self) -> pd.DataFrame:
        """
        Calculates the costs associated with material components.

        This method computes the material costs required for wellbore construction, including cement, 
        gravel, bentonite, drilling fluids, and other materials. It also calculates the costs for different 
        bore sections and centraliser.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the base, low, and high cost estimates for each material component.

        Raises
        ------
        KeyError
            If any required parameter is missing from `material_params` or `material_cost_rates`.
        """
        try:
            total_well_depth = self.material_params["total_well_depth"]
            individual_section_lengths = self.material_params["individual_section_lengths"]
            section_excavation_volumes = self.material_params["section_excavation_volumes"]
            #print(f'section excatvation volumes')
            #print(section_excavation_volumes)
            total_excavation_volume = section_excavation_volumes.sum()
            #print(f"total exc volume: {total_excavation_volume}")
            total_gravel_volume = self.material_params["total_gravel_volume"]
            total_cement_volume = self.material_params["total_cement_volume"]
            operational_section_count = self.material_params["operational_section_count"]
            #print(f"total gravel volume: {total_gravel_volume}")
            #print(f"total cement volume: {total_cement_volume}")
            base_costs = {
                'cement': total_cement_volume * self.material_cost_rates['cement_rate_per_cubic_meter'],
                'gravel': total_gravel_volume * self.material_cost_rates['gravel_rate_per_cubic_meter'],
                'bentonite': total_excavation_volume * self.material_cost_rates['bentonite_rate_per_cubic_meter'],
                'drilling_fluid_and_lubricants': total_excavation_volume * self.material_cost_rates['drilling_fluid_and_lubricant_rate_per_cubic_meter'],
                'drilling_mud': total_excavation_volume * self.material_cost_rates['drilling_mud_rate_per_cubic_meter'],
                'bore_flange_and_valve_spec': self.material_cost_rates['bore_table_flange_gate_valve_rate'],
                'cement_shoe': self.material_cost_rates['cement_shoe_rate'],
                'packer_lowering_assembly': self.material_cost_rates['packer_lowering_assembly_rate'] * operational_section_count
            }

            material_costs_df = calculate_costs_with_df(
                base_values=base_costs,
                margin_functions=self.margin_functions.loc['materials'],
                index_labels=base_costs.keys()
            )

            #centraliser cost calculation
            total_well_depth_without_screen = individual_section_lengths.iloc[:-2].sum()
            centraliser_row = {
                'low': max(self.material_cost_rates['centraliser_rate_per_meter'] * CENTRALISER_COST_FACTOR_LOW * (total_well_depth_without_screen + CENTRALISER_DEPTH_OFFSET_LOW), 0),
                'base': self.material_cost_rates['centraliser_rate_per_meter'] * total_well_depth,
                'high': self.material_cost_rates['centraliser_rate_per_meter'] * CENTRALISER_COST_FACTOR_HIGH * (total_well_depth_without_screen + CENTRALISER_DEPTH_OFFSET_HIGH)
            }
            material_costs_df = pd.concat(
                [material_costs_df, pd.DataFrame(centraliser_row, index=['centraliser'])])
            
            # print('\nmaterial_costs without bore sections')
            # print(material_costs_df)

            # bore section cost calculation using the private method
            bore_section_costs = self._calculate_bore_section_material_costs()
            
            material_costs_df = pd.concat(
                [material_costs_df, bore_section_costs])

            #print('\nmaterial: bore section costs')
            #print(bore_section_costs)
            #print(f'centraliser:{centraliser_row}')
            # print('\nmaterial_cost: ')
            # print(material_costs_df)
            return material_costs_df
        except KeyError as e:
            self.logger.error(
                f"Error in calculating material costs: {e} at line {e.__traceback__.tb_lineno}")
            raise

    def _calculate_bore_section_material_costs(self) -> pd.DataFrame:
        """
        Private method to calculate the bore section material costs.
        """
        try:
            #section_lengths = self.material_params["individual_section_lengths"]
            #section_diameters = self.material_params["section_diameters"]
            
            bore_section_params = pd.DataFrame({
                'lengths': self.material_params["individual_section_lengths"],
                'diameters': self.material_params["section_diameters"] * 1E3
                })

            # bore_section_params = pd.DataFrame(
            #     section_lengths.multiply(section_diameters) * 1E3)
            bore_section_costs = pd.DataFrame(
                index=bore_section_params.index, columns=['low', 'base', 'high'])
            
            #print(f'\nbore section params: {bore_section_params}')
            bore_section_costs['base'] = bore_section_params.apply(
                lambda row: (
                    row['lengths'] * row['diameters'] * self.material_cost_rates['pre_collar']['coefficient'] /
                    self.material_cost_rates['pre_collar']['divisor']
                    if row.name == 'pre_collar'
                    else (
                        row['lengths'] * (row['diameters'] * self.material_cost_rates['screen']['coefficient'] +
                        self.material_cost_rates['screen']['offset'])
                        if row.name == 'screen'
                        else row['lengths'] * \
                            ( row['diameters'] * self.material_cost_rates['other_section']['coefficient'] + \
                             self.material_cost_rates['other_section']['offset'])
                    )
                ), axis=1
            )
            bore_section_costs['low'] = bore_section_costs.apply(
                lambda row: max(row['base'] - bore_section_params.at[row.name, 'lengths']
                                * self.material_cost_rates['bore_section_margin_rate'], 0)
                if row.name != 'pre_collar' 
                else row['base'] * (1 - PRE_COLLAR_MARGIN_RATE), 
                axis=1
            )
            bore_section_costs['high'] = bore_section_costs.apply(
                lambda row: row['base'] + bore_section_params.at[row.name, 'lengths']
                * self.material_cost_rates['bore_section_margin_rate']
                if row.name != 'pre_collar' 
                else row['base'] * (1 + PRE_COLLAR_MARGIN_RATE), 
                axis=1
            )

            return bore_section_costs
        
        except KeyError as e:
            self.logger.error(f"Error in calculating bore section costs: {e}")
            raise

    def calculate_other_components_cost(self) -> pd.DataFrame:
        """
        Calculates the costs associated with other miscellaneous components.

        This method computes the costs for various additional components such as disinfection, mobilisation, 
        grouting, logging, fabrication, cement casing, gravel packing, and subcontract welders. It uses 
        parameters like total well depth, section lengths, and drilling time for calculations.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the base, low, and high cost estimates for each miscellaneous component.

        Raises
        ------
        KeyError
            If any required parameter is missing from `other_params` or `other_cost_rates`.
        Exception
            If any other error occurs during cost calculation.
        """
        try:
            total_well_depth = self.other_params["total_well_depth"]
            section_lengths = self.other_params["section_lengths"]
            drilling_time = self.other_params["drilling_time"]
            pre_collar_length = section_lengths['pre_collar']
            screen_length = section_lengths['screen']

            total_casing_length = self.other_params['total_casing_length']

            base_costs = {
                'disinfection_drilling_plant': self.other_cost_rates['disinfection_drilling_plant_rate'],
                'mobilisation_demobilization': self.other_cost_rates['mobilisation_demobilization_rate_per_day'] * drilling_time,
                'installation_grouting_pre_collar': self.other_cost_rates['installation_grouting_pre_collar_rate_per_meter'] * pre_collar_length,
                'wireline_logging': self.other_cost_rates['wireline_logging_rate_per_meter'] * total_well_depth,
                'fabrication_installation': self.other_cost_rates['fabrication_installation_rate_per_meter'] * (total_casing_length),
                #d
                'cement_casing': self.other_cost_rates['cement_casing_rate_per_meter'] * (total_well_depth - screen_length),
                'pack_gravel': self.other_cost_rates['gravel_pack_rate_per_meter'] * screen_length,
                'subcontract_welders': self.other_cost_rates['subcontract_welders_rate_per_day'] * drilling_time
            }

            other_costs_df = calculate_costs_with_df(
                base_values=base_costs,
                margin_functions=self.margin_functions.loc['others'],
                index_labels=base_costs.keys()
            )

            # print('other_costs')
            # print(other_costs_df)

            return other_costs_df
        except KeyError as e:
            self.logger.error(
                f"Error in calculating other costs: {e} at line {e.__traceback__.tb_lineno}")
            raise
        except Exception as e:
            self.logger.error(
                f"Error in calculating other costs: {e} at line {e.__traceback__.tb_lineno}")
            raise
