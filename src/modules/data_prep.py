import os
import pandas as pd
import numpy as np
import random
from typing import Any

from utils.globals import CHAR_LIST_TRANS
from utils.enums import ReturnCode
from utils.custom_types import Song, Platform
import utils.helper as helper
from modules.managers import (
    Manager,
    SpotifyManager,
    AmazonMusicManager,
    YoutubeMusicManager,
)


class DfHandler:
    def __init__(self) -> None:
        self.df = None
        self.df_name = ""
        self.manager = Manager()

    def create_new_dataset_raw(self, name: str):
        """creates new csv file for raw song data

        Args:
            name (str): name of new dataset
        """
        if os.path.exists(os.path.abspath(f"data/raw/{name}.csv")):
            return

        columns = [
            "platform1",
            "platform2",
            "name1",
            "artist1",
            "name2",
            "artist2",
            "same",
            "ml guess",
        ]
        df = pd.DataFrame(columns=columns)
        df.to_csv(os.path.abspath(f"data/raw/{name}.csv"))

    def load_dataset_from_csv(self, name: str) -> ReturnCode:
        """loads dataset from raw folder. Needed for various class methods

        Args:
            name (str): name of dataset to load
        """
        if not os.path.exists(os.path.abspath(f"data/raw/{name}.csv")):
            return ReturnCode.NO_DATASET
        self.df = pd.read_csv(
            os.path.abspath(f"data/raw/{name}.csv"), index_col=0
        ).astype(object)
        self.df_name = name
        return ReturnCode.SUCCESS

    def save_dataset_to_csv(self) -> ReturnCode | None:
        """save currently loaded dataset as csv file"""
        if self.df is None:
            return ReturnCode.NO_DATASET

        self.df.to_csv(os.path.abspath(f"data/raw/{self.df_name}.csv"))

    def process_dataset_for_ml(self, override: bool = False) -> ReturnCode | None:
        """process loaded dataset for machine learning training. Processed dataset is saved under "processed" with same name as loaded dataset

        Args:
            override (bool, optional): True if existing datasets should be overriden. False if existing datasets should be updated with processed data. Defaults to False.
        """
        if self.df is None:
            return ReturnCode.NO_DATASET

        if self.df["same"].isna().sum() > 0:
            return ReturnCode.NAN_IN_DATASET

        if os.path.exists(os.path.abspath(f"data/processed/{self.df_name}.csv")):
            df_target = pd.read_csv(
                os.path.abspath(f"data/processed/{self.df_name}.csv"), index_col=0
            ).astype(object)
        else:
            columns = ["name_diff"] + CHAR_LIST_TRANS + ["etc", "same"]
            df_target = pd.DataFrame(columns=columns)
            df_target.to_csv(os.path.abspath(f"data/processed/{self.df_name}.csv"))
        if override:
            df_src = self.df
            df_target.drop(df_target.iloc[:0], axis=1, inplace=True)
        else:
            df_src = self.df.iloc[len(df_target) :, :]

        columns = ["name_diff"] + CHAR_LIST_TRANS + ["etc", "same"]
        df_list = [
            helper.song_name_prep(name1, name2, same)
            for name1, name2, same in zip(
                df_src["name1"], df_src["name2"], df_src["same"]
            )
        ]

        df_temp = pd.DataFrame(df_list, columns=columns)

        df_target = pd.concat([df_target, df_temp], axis=0, ignore_index=True)
        df_target.to_csv(os.path.abspath(f"data/processed/{self.df_name}.csv"))

    def check_if_song_in_dataset(
        self, song: Song, similar_song: Song
    ) -> np.bool | ReturnCode:
        """checks if given song pair is already in loaded dataset. Order of input doesn't matter.

        Args:
            song (Song): first song
            similar_song (Song): second song

        Returns:
            np.bool: True if already in dataset
        """
        if self.df is None:
            return ReturnCode.NO_DATASET

        check = (
            (self.df["name1"] == song[0]) & (self.df["name2"] == similar_song[0])
        ).any()
        reverse_check = (
            (self.df["name1"] == similar_song[0]) & (self.df["name2"] == song[0])
        ).any()
        return check or reverse_check

    def append_row_to_dataset(self, row: list[Any]) -> ReturnCode | None:
        if self.df is None:
            return ReturnCode.NO_DATASET

        self.df.loc[len(self.df)] = row

    def eval_platform(
        self,
        platform1: Platform,
        platform2: Platform,
    ) -> tuple[
        SpotifyManager | AmazonMusicManager | YoutubeMusicManager,
        SpotifyManager | AmazonMusicManager | YoutubeMusicManager,
        str,
    ]:
        """helper function to evaluate witch handler should be used. Platform input order doesn't matter.

        Args:
            platform1 (Literal[&quot;spotify&quot;, &quot;amazon&quot;, &quot;youtube&quot;]): first platform
            platform2 (Literal[&quot;spotify&quot;, &quot;amazon&quot;, &quot;youtube&quot;]): second platform

        Raises:
            ValueError: on wrong input

        Returns:
            tuple[ SpotifyManager | AmazonMusicManager | YoutubeMusicManager, SpotifyManager | AmazonMusicManager | YoutubeMusicManager, ]: handlers for the platforms and wildcard symbol
        """
        if platform1.lower() == platform2.lower():
            raise ValueError("platform1 and platform2 need to be different")

        wildcard = "*"

        match platform1:
            case "spotify":
                handler1 = self.manager.sm
                wildcard = "%"
            case "amazon":
                handler1 = self.manager.amm
                handler1.start_driver()
                handler1.login()
            case "youtube":
                handler1 = self.manager.ytm
            case _:
                raise ValueError(f"no handler for {platform1}")
        match platform2:
            case "spotify":
                handler2 = self.manager.sm
            case "amazon":
                handler2 = self.manager.amm
                handler2.start_driver()
                handler2.login()
            case "youtube":
                handler2 = self.manager.ytm
            case _:
                raise ValueError(f"no handler for {platform2}")
        return handler1, handler2, wildcard

    def expand_dataset_with_songs(
        self,
        platform1: Platform,
        platform2: Platform,
        repeat: int = 1,
        avoid_duplicates: bool = True,
        quicksave_interval: int = 5,
    ) -> ReturnCode | None:
        """expand loaded dataset with song data by scraping from the selected platforms.

        Args:
            platform1 (Literal[&quot;spotify&quot;, &quot;amazone&quot;, &quot;youtube&quot;]): platform to fetch random song from
            platform2 (Literal[&quot;spotify&quot;, &quot;amazone&quot;, &quot;youtube&quot;]): platform to fetch similar song from
            repeat (int, optional): number of songs to add. Defaults to 1.
            avoid_duplicates (bool, optional): if True only adds songs that aren't already in the dataset. Defaults to True.
            quicksave_interval (int, optional): number of songs after witch the dataset gets periodically saved. Defaults to 5.
        """
        if self.df is None:
            return ReturnCode.NO_DATASET

        handler1, handler2, wildcard = self.eval_platform(platform1, platform2)

        for i in range(repeat):
            print(f"adding song {i + 1}/{repeat}")

            done = False
            while not done:
                query = helper.get_random_query(wildcard)

                result = handler1.get_similar_songs_data(query, rand=True)
                if result[0] == ReturnCode.FOUND:
                    song = result[1][0]
                    result2 = handler2.get_similar_songs_data(song[0], song[1])
                else:
                    continue
                if result2[0] == ReturnCode.FOUND:
                    found_songs = result2[1]
                else:
                    continue

                # remove songs that match by string comparison
                if song[0] in [item[0] for item in found_songs]:
                    continue

                if len(found_songs) < 1:
                    continue
                elif len(found_songs) == 1:
                    song_choice = found_songs[0]
                else:
                    # make weighted random choice between the first song and a random other result song
                    i = random.randint(1, 100)
                    if i < 80:
                        song_choice = found_songs[0]
                    else:
                        song_choice = random.choice(found_songs[1:])

                # avoid duplicates if necessary
                if (
                    self.check_if_song_in_dataset(song, song_choice)
                    and avoid_duplicates
                ):
                    continue

                row = [
                    platform1,
                    platform2,
                    song[0],
                    song[1],
                    song_choice[0],
                    song_choice[1],
                    pd.NA,
                    pd.NA,
                ]
                self.append_row_to_dataset(row)
                done = True

            if i % quicksave_interval == 0:
                self.save_dataset_to_csv()

        self.save_dataset_to_csv()
        try:
            handler1.close_driver()
        except AttributeError:
            pass
        try:
            handler2.close_driver()
        except AttributeError:
            pass

    def add_guess_ml_data(
        self, model=None, scaler=None, confidence: float = 0.7
    ) -> ReturnCode | None:
        """populates "ml guess" column in loaded dataset with guess from machine learning model

        Args:
            model (_type_, optional): machine learning model to use. If None, defaults to a base model. Defaults to None.
            scaler (_type_, optional): scaler to use. If None, defaults to a base scaler Defaults to None.
            confidence (float, optional): minimum confidence needed by model to count guess as True. Defaults to 0.7.
        """
        if self.df is None:
            return ReturnCode.NO_DATASET

        self.df["ml guess"] = [
            (
                1
                if helper.get_song_match_proba(name1, name2, model=model, scaler=scaler)
                >= confidence
                else 0
            )
            for name1, name2 in zip(self.df["name1"], self.df["name2"])
        ]
        self.df.to_csv(os.path.abspath(f"data/raw/{self.df_name}.csv"))
