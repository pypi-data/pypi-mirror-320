import pandas as pd
from pathlib import Path
import csv
import os


def extraer_csv(path, remove_head_if_odd=True):
    """Method to create pandas dataframe from CSV file"""

    # para encontrar el tipo de delimitador del archivo .csv
    with open(path, "r") as f:
        header = next(f)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(header).delimiter

    df = pd.read_csv(path, delimiter=delimiter)
    # Obtener un número par de muestras

    if len(df) % 2 != 0:
        if remove_head_if_odd:
            df.drop(2, inplace=True)
        else:
            df.drop(df.tail(1).index, inplace=True)

    return rename_columns(df)


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Private method, renames columns from Dataframe into more
    readable names. i.e. it creates a new name for each column by
    merging the three original named columns returned on CSV from
    ATP

    Parameters
    ----------
    df : pd.DataFrame
        Signals dataframe

    Returns
    -------
    pd.DataFrame
        Signals dataframe with renamed columns
    """
    # Extraer los labels de las filas 1 y 2
    pattern = r"^b'([\w ]*)'"
    node_from = df.iloc[0].str.replace(pattern, r"\1", regex=True).str.strip()
    node_to = df.iloc[1].str.replace(pattern, r"\1", regex=True).str.strip()
    df = df.drop(index=0)
    df = df.drop(index=1)

    df = columns_replace(df)
    # return df

    # Extraer si la medición es V, I o models; borrar si es Model
    labels_list = df.columns.values.tolist()

    # # convertir los labels de cada nodo a una lista
    node_from_list = node_from.values.tolist()
    node_to_list = node_to.values.tolist()

    labels_list = new_labels(node_from_list, node_to_list, labels_list)

    df.columns = labels_list
    labels_list = labels_list[1:]
    # df.set_index("time", inplace=True)
    df = df.reset_index(drop=True)
    return df


def new_labels(list1: list, list2: list, labels: list) -> list:
    """Private method, merges three labels rows from each column into one row

    Parameters
    ----------
    list1 : list
        FROM node list. ROW 2 in CSV
    list2 : list
        TO node list. ROW 3 in CSV
    labels : list
        Signal type list (current, voltage or MODEL). ROW 1 in CSV

    Returns
    -------
    list
        List with correct column labels
    """

    final_list = []
    for x, y, z in zip(list1, list2, labels):
        if z == "time":
            final_list.append(z)
        elif y == "":
            final_list.append(f"{z}: {x}")
        elif z == "Model":
            final_list.append(f"{x}: {y}")
        else:
            final_list.append(f"{z}: {x}-{y}")
    return final_list


def columns_replace(df: pd.DataFrame) -> pd.DataFrame:
    """Private method, standarizes columns names, making it easier to rename them
    according to signal type they represent.

    eg. for different CSV with time column named as: "Time", "TIME" or "time", all will
    be returned as "time"


    Parameters
    ----------
    df : pd.DataFrame
        Signals dataframe

    Returns
    -------
    pd.DataFrame
        Signals dataframe with standarized columns names
    """
    patterns = [
        (" ", ""),
        (r"^(V|I)[.\w-]*", r"\1"),
        (r"^(C)[.\w-]*", r"I"),
        (r"^(?![\s\S])", r"Model"),
        (r"^\d*\.*\d+", r"Model"),
        (r"MODELS\.*[\d]*", r"Model"),
        (r"Time", r"time"),
        (r"b'", r""),
    ]
    # INFORMACIÓN DE Regex en patterns
    # Quitar los espacios blancos
    # Columnas que comienzan con V-xxx, I-xxx [SEM] o Voltage [Manual]
    # Columnas que comienzan con Current [manual]
    # Columnas que estén vacías [Manual]
    # Columnas cuyos nombres sean números [SEM]
    # Columnas que tengan MODELS en mayúscula [Manual]
    # Hacer la T de time minúscula

    # Crear un diccionario e iterar sobre este para reemplazar el str.replace(x,y)
    for pattern in patterns:
        df.columns = df.columns.str.replace(pattern[0], pattern[1], regex=True)
    return df


def delete_columns(
    df: pd.DataFrame,
    remove_types: list = None,
    keep_types: list = None,
    specific_columns: list = None,
    specific_columns_keep: list = None,
) -> pd.DataFrame:
    """
    Deletes or keeps columns in the DataFrame based on signal types, specific column names,
    or combinations of both.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.

    remove_types : list, optional
        List of signal types to remove, e.g., ["V", "I", "MODELS"].

    specific_columns : list, optional
        List of specific column names to remove.

    keep_types : list, optional
        List of signal types to keep, e.g., ["time", "V"].
        If specified, all other columns are removed.

    specific_columns_keep : list, optional
        List of specific column names to keep. If specified, all other columns
        not in this list or matching `keep_types` are removed.

    Returns
    -------
    pd.DataFrame
        DataFrame with the specified columns removed or kept.
    """
    # Handle columns to keep (either by types or specific names)
    if keep_types or specific_columns_keep:
        # Match signal types to keep
        cols_to_keep = []
        if keep_types:
            pattern = r"^(?:" + "|".join(keep_types) + r")[:\s]*"
            cols_to_keep.extend(
                [
                    col
                    for col in df.columns
                    if pd.Series(col).str.contains(pattern, regex=True).any()
                ]
            )
        # Add specific columns to keep
        if specific_columns_keep:
            cols_to_keep.extend(
                [col for col in specific_columns_keep if col in df.columns]
            )
        # Keep only the specified columns
        df = df[cols_to_keep]
        return df

    # Handle columns to remove (either by types or specific names)
    if remove_types:
        # Identify columns matching signal types to remove
        pattern = r"^(?:" + "|".join(remove_types) + r")[:\s]*"
        cols_to_remove = [
            col
            for col in df.columns
            if pd.Series(col).str.contains(pattern, regex=True).any()
        ]
        df = df.drop(columns=cols_to_remove)

    if specific_columns:
        # Drop columns matching the specific column names
        df = df.drop(columns=[col for col in specific_columns if col in df.columns])

    return df


def extract_time_info(df: pd.DataFrame, time_column: str = "time") -> dict:
    """
    Extracts time step (dt), total samples, and total time from a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.

    time_column : str, optional
        The name of the column containing time data. Defaults to "time".

    Returns
    -------
    dict
        A dictionary with keys:
        - "dt": Time step (difference between consecutive time points).
        - "total_samples": Total number of samples in the DataFrame.
        - "total_time": Total time duration (difference between first and last time points).

    Raises
    ------
    KeyError
        If the specified time column is not found in the DataFrame.

    ValueError
        If the time column has fewer than 2 unique values.
    """
    if time_column not in df.columns:
        raise KeyError(f"Time column '{time_column}' not found in the DataFrame.")

    time_values = df[time_column].dropna().astype(float).unique()
    if len(time_values) < 2:
        raise ValueError(
            f"The time column '{time_column}' must have at least two unique values."
        )

    # Sort the time values (just in case they are not in order)
    time_values.sort()

    # Compute time step (dt), total samples, and total time
    dt = time_values[1] - time_values[0]  # Assume uniform time intervals
    total_samples = len(df)
    total_time = time_values[-1] - time_values[0]
    fs = round(1 / dt)

    return {
        "dt": dt,
        "fs": fs,
        "total_samples": total_samples,
        "total_time": total_time,
    }


def cycle_info(
    df: pd.DataFrame, time_column: str = "time", frequency: float = 60
) -> float:
    """
    Calculates the number of cycles given the time frequency and the total time from the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.

    time_column : str, optional
        The name of the column containing time data. Defaults to "time".

    frequency : float, optional
        The frequency of the signal in Hz (cycles per second). Defaults to 1.0 Hz.

    Returns
    -------
    float
        The calculated number of cycles based on the total time and frequency.
    """
    time_info = extract_time_info(df, time_column)

    fs = time_info["fs"]
    total_samples = time_info["total_samples"]

    # Calculate the number of cycles
    cycles = (total_samples / fs) * frequency
    samples_per_cycle = total_samples / cycles

    return {
        "cycles": cycles,
        "samples_per_cycle": int(samples_per_cycle),
    }


def calculate_windows(df: pd.DataFrame, window_size: int, step: int = 1) -> int:
    """Calculates amount of windows on a dataframe for a given window size and step

    Parameters
    ----------
    df : pd.DataFrame
        Electrical System event signals dataframe
    window_size : int
        Samples in window
    step : int, optional
        sampling steps, by default 1

    Returns
    -------
    int
        total windows
    """
    return ((df.shape[0] - window_size) // step) + 1


def remove_cycles(
    df: pd.DataFrame, cycles: int, remove_from_head: bool = True, frequency: int = 60
) -> pd.DataFrame:
    """Removes unwanted cycles from signal

    Parameters
    ----------
    df : pd.DataFrame
        Electrical System event signals dataframe
    cycles : int
        Total cycles to remove
    remove_from_head : bool, optional
        wheter to remove them from the start or end of the signals, by default True

    Returns
    -------
    pd.DataFrame
        dataframe with trimmed cycles
    """
    samples_per_cycle = cycle_info(df, frequency=frequency)["samples_per_cycle"]
    samples_to_remove = samples_per_cycle * cycles
    if remove_from_head:
        return df.iloc[samples_to_remove + 2 :]
    return df.iloc[: len(df) - samples_to_remove]


def save_parquet(df: pd.DataFrame, path: str):
    database_dir = Path(path).parents[1]
    database_dir = os.path.basename(database_dir)
    new_path = path.replace(f"/{database_dir}/", f"/{database_dir}_clean/")
    new_path = new_path.replace(".csv", ".parquet")
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    df = df.apply(pd.to_numeric, errors="coerce", downcast="float")
    df.to_parquet(new_path, engine="pyarrow")


def clean_file(
    path: str,
    downsampling: int = 1,
    keep_types: list[str] = None,
    keep_columns: list = None,
    rmv_cycles_start: int = None,
    rmv_cycles_end: int = None,
    frequency: int = 60,
):
    df = extraer_csv(path)
    df = delete_columns(
        df,
        keep_types=keep_types,
        specific_columns_keep=keep_columns,
    )
    df = df.iloc[::downsampling]

    if rmv_cycles_start:
        df = remove_cycles(df, rmv_cycles_start, frequency=frequency).reset_index(
            drop=True
        )
    if rmv_cycles_end:
        df = remove_cycles(df, rmv_cycles_end, False, frequency=frequency).reset_index(
            drop=True
        )
    save_parquet(df, path)
