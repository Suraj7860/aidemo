import collections
import jsonlines
import copy
import re


def doccano_file_to_word_dict(filepath):
    """Extract the word dictionnary after doccano labelling.

    Parameters
    ----------
    filepath : str
        path to the doccano output file.

    """
    word_dict = {}
    with jsonlines.open(filepath, 'r') as reader:
        for item in reader:
            try:
                correct_word = [item['text'][label[0]:label[1]].lstrip().rstrip()
                                for label in item['labels'] if label[2] == 'CORRECT'][0]
                incorrect_words = [item['text'][label[0]:label[1]].lstrip().rstrip()
                                   for label in item['labels'] if label[2] == 'INCORRECT']
                word_dict[correct_word] = incorrect_words
            except:
                pass

    return word_dict


def pandas_to_doccano_file(df, col_text, col_id, path, meta_cols="all",
                           pre_annotate_dict={}):
    """Generate a jsonl file to give as input to doccano.

    Parameters
    ----------
    df : pd.DataFrame
        dataframe containing a column with textual information.
    col_text : str
        name of the column containing the textual information.
    col_id : str
        name of the column containing the ids.
    path : str
        filepath where to save the jsonl file.
    meta_cols : str, list, None.
        metadata columns.
    pre_annotate_dict : dict
        dict containing the default regex.

    """
    def check_input(df, meta_cols):
        df_cols = df.columns
        if col_text not in df_cols:
            raise TypeError(f"'{col_text}' not in columns")
        if col_id not in df_cols:
            raise TypeError(f"'{col_id}' not in columns")
        if meta_cols == "all":
            meta_cols = df_cols[~df_cols.isin([col_id, col_text, "json_to_doccano"])]
        elif isinstance(meta_cols, str):
            meta_cols = [meta_cols]
        if not isinstance(meta_cols, collections.Iterable):
            raise TypeError("meta_cols must be str or iterable")
        if len(intersection(meta_cols, df_cols)) != len(meta_cols):
            raise TypeError(f"in {str(meta_cols)} there are unknown columns")
        else:
            meta_cols = list(meta_cols)
        return meta_cols

    df_copy = copy.deepcopy(df)
    meta_cols = check_input(df_copy, meta_cols)
    rules = [f"(?P<{cat}>{regex})" for cat, regex in pre_annotate_dict.items()]
    regex_groups = "|".join(rules)
    df_copy.loc[:, f"cleaned_{col_text}"] = df_copy[col_text].apply(clean_for_doccano)
    df_copy.loc[:, "json_to_doccano"] = df_copy.apply(
        lambda row: {
            "id": row[col_id],
            "text": row[f"cleaned_{col_text}"],
            "meta": {other: str(row[other]) for other in meta_cols},
            "labels": [
                [match.start(), match.end(), match.lastgroup]
                for match in re.finditer(regex_groups, row[f"cleaned_{col_text}"])
            ],
        },
        axis=1,
    )

    list_of_json = list(df_copy.loc[:, "json_to_doccano"])
    with jsonlines.open(path, "w") as writer:
        writer.write_all(list_of_json)


def clean_for_doccano(text):
    return re.sub(r"\n|\t|\r", " ", text).lstrip().rstrip()


def intersection(lst1, lst2):
    """Get intersection between two ensembles.

    Parameters
    ----------
    lst1 : list
        first list.
    lst2 : list
        second list.

    Returns
    -------
    list
        list of elements that were on both lists.

    """
    lst3 = [value for value in lst1 if value in lst2]
    return lst3
