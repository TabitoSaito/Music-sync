import time
import os
import joblib
import random

from bs4 import BeautifulSoup as bs

from utils.globals import CHAR_STR, CHAR_LIST_TRANS, SPECIAL_CHAR_DICT, CHAR_STR_SPEC


def zoom_and_scrape(driver, url: os.PathLike[str] | str) -> bs:
    """
    navigates to website, zooms out to forceload content and scrapes html
    """
    driver.get(url)
    time.sleep(4)
    driver.execute_script("document.body.style.zoom='5%'")
    time.sleep(1)

    html = driver.execute_script("return document.documentElement.outerHTML;")
    soup = bs(html, "html.parser")
    return soup


def escape_xpath_string(text: str) -> str:
    """
    Escapes quotes in an XPath expression by alternating single and double quotes.
    """
    if '"' in text and "'" in text:
        return "concat('" + text.replace("'", "', \"'\", '") + "')"
    elif '"' in text:
        return f"'{text}'"
    else:
        return f'"{text}"'


def get_random_query(wildcard="*") -> str:
    # A list of all characters that can be chosen
    characters = "abcdefghijklmnopqrstuvwxyz"

    # Generate a random sequence of 1 to 3 characters
    random_character = "".join(
        random.choice(characters) for _ in range(random.randint(1, 3))
    )

    # Randomly decide wildcard placement
    wildcard_case = random.randint(0, 2)

    match wildcard_case:
        case 0:
            return random_character + wildcard
        case 1:
            return wildcard + random_character + wildcard
        case 2:
            return wildcard + random_character
        case _:
            return random_character


def song_name_prep(name1: str, name2: str, same: bool | None = None) -> list:
    """Helper function vor machine learning input. Calculates the difference in length and the difference in letters of both names.

    Args:
        name1 (str): First string
        name2 (str): String to compare against

    Returns:
        list: input list for machine learning model
    """
    name_diff = abs(len(name1) - len(name2))

    name1_count = {char: 0 for char in CHAR_LIST_TRANS}
    name1_count["etc"] = 0
    name2_count = name1_count.copy()

    for char in name1:
        if char in CHAR_STR:
            name1_count[char] += 1
        elif char in CHAR_STR_SPEC:
            char_trans = SPECIAL_CHAR_DICT[char]
            name1_count[char_trans] += 1
        else:
            name1_count["etc"] += 1

    for char in name2:
        if char in CHAR_STR:
            name2_count[char] += 1
        elif char in CHAR_STR_SPEC:
            char_trans = SPECIAL_CHAR_DICT[char]
            name2_count[char_trans] += 1
        else:
            name2_count["etc"] += 1

    diff_dict = {k: abs(name1_count[k] - name2_count[k]) for k in name1_count}

    if same:
        diff_dict["same"] = same

    row_list = [name_diff] + [v for _, v in diff_dict.items()]

    return row_list


def get_song_match_proba(name1: str, name2: str, model=None, scaler=None) -> float:
    """calculates the probability that both names describe the same song

    Args:
        name1 (str): name of first song
        name2 (str): name of song to compare against
        model (_type_, optional): machine learning model to use for matching. If none, loads basis model. Defaults to None.
        scaler (_type_, optional): scaler to preprocess data for model. If none, loads basis scaler. Defaults to None.

    Returns:
        float: probability of match
    """
    if model is None:
        model = joblib.load(os.path.abspath("src/modules/ML_models/model.pkl"))
    if scaler is None:
        scaler = joblib.load(os.path.abspath("src/modules/ML_scalers/scaler.pkl"))
    try:
        proba = float(
            model.predict_proba(
                scaler.transform([song_name_prep(name1.lower(), name2.lower())])
            )[0][1]
        )
    except (AttributeError, ValueError):
        proba = float(
            model.predict(
                scaler.transform([song_name_prep(name1.lower(), name2.lower())])
            )[0]
        )
    return proba
