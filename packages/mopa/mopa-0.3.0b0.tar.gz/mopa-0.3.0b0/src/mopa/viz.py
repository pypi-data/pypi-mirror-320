"""Visualization tools"""

import hiplot as hip
import pandas as pd


def parallel(df, custom_col_names=None, invert_cols=None):
    """
    Create parallel plot using Hiplot

    Parameters
    ----------
    df: DataFrame
        DataFrame to plot
    custom_col_names: dict
        Dictionary to rename columns
    invert_cols: list
        Columns to flip, must be custom column names if given

    Returns
    -------
    exp: hiplot.experiment.Experiment
        Hiplot parallel figure
    """
    # Rename Columns
    if custom_col_names is None:
        custom_col_names = {}
    df = df.rename(custom_col_names, axis=1)

    # Plotting

    # Old Method
    # exp = hip.Experiment.from_dataframe(df)

    manual_datapoints = []
    parameters = {}

    # Populate experiment with datapoints
    for index, row in df.iterrows():
        values = {col: float(row[col]) if pd.api.types.is_numeric_dtype(df[col]) else row[col] for col in df.columns}
        manual_datapoints.append(hip.Datapoint(uid=str(index), values=values))

    for col_name in df.columns:
        print(col_name)
        parameters[col_name] = hip.ValueDef(value_type = hip.ValueType.NUMERIC)

    # Create HiPlot Experiment
    exp = hip.Experiment(datapoints=manual_datapoints, parameters_definition=parameters)

    exp.display_data(hip.Displays.PARALLEL_PLOT).update(
        {
            'hide': ['uid'],
            'invert': invert_cols
        }
    )
    exp.display_data(hip.Displays.TABLE).update({'hide': ['uid', 'from_uid']})
    print(f'Success: Created parallel plot of columns {df.columns.to_list()}')
    return exp
