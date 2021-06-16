from diaman.utils import word_dict


def test_merge_word_dicts():
    """[utils][word_dict] Check correct merge of the dictionnaries.

    """
    ref_dict = {"accordeon": ["acordeon"],
                "accoster": ["accostage", "acostage"]}

    new_dict = {"accordeon": ["accordeons"],
                "accostage": ["accostages"],
                "accumulateur": ["acumulateur", "acc"]}

    word_dict.merge_word_dicts(ref_dict, new_dict)

    expected_dict = {"accordeon": ["acordeon", "accordeons"],
                     "accoster": ["accostage", "acostage", "accostages"],
                     "accumulateur": ["acumulateur", "acc"]}

    for correct_word in ref_dict:
        assert sorted(list(set(ref_dict[correct_word]))) == sorted(list(set(expected_dict[correct_word])))
