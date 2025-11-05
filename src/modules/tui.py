from modules.synchronizer import Sync
from modules.data_prep import DfHandler
from modules.ml_model_evaluator import Eval
from utils.enums import ReturnCode
from utils.globals import PLATFORMS


class TUI:
    def __init__(self) -> None:
        self.cur_input = []
        self.running: bool
        self.sync = Sync()
        self.df_handler = DfHandler()

    def start(self):
        self.running = True
        self._welcome()

    def match_user_input(self) -> ReturnCode:
        match self.cur_input[0].lower():
            case "help":
                return self._print_help()
            case "exit":
                return self.exit_program()
            case "sync":
                return self._handel_sync()
            case "data":
                return self._handel_data()
            case "eval":
                return self._handel_eval()
            case "":
                return ReturnCode.NO_INPUT
            case _:
                print(f"command not found: {self.cur_input[0]}")
                return ReturnCode.NO_COMMAND

    def _welcome(self) -> ReturnCode:
        print(
            "Welcome to the Music synchronizer. Type 'help' to see all possible commands or 'exit' to end the program."
        )
        return ReturnCode.SUCCESS

    def take_user_input(self):
        user_input = input(">>>")
        self.cur_input = user_input.split(" ")

    def _print_help(self) -> ReturnCode:
        print(
            """COMMANDS:
    help - print this help text.
                      
    exit - end the program.
                      
    sync <playlist name> <platform 1> <platform 2> - synchronize a playlist across two platforms or all if none are specified.
        args:
            playlist name [str] - name of playlist to synchronize.
            platform 1 [spotify | amazone | youtube] optional - platform name 1.
            platform 2 [spotify | amazone | youtube] optional - platform name 2.
                      
    data <action> - modify datasets.
        actions:
            new <dataset name> - generate an empty dataset (data/raw/<dataset name>.csv).
                args:
                    dataset name [str] - name of new dataset.
                      
            load <dataset name> - load a dataset from data/raw.
                args:
                    dataset name [str] - name of new dataset.
                      
            expand <platform 1> <platform 2> <repeat> - expand loaded dataset by scraping songs from platform 1 and 2.
                args:
                    platform 1 [spotify | amazone | youtube] - platform name 1.
                    platform 2 [spotify | amazone | youtube] - platform name 2.
                    repeat [int] optional - number of songs to add. Defaults to 1.
                      
            guess - add guesses from machine learning model to loaded dataset.
                      
            process - process loaded dataset for machine learning training. (loaded dataset needs to have 'same' column filled).
                      
    eval <dataset name> - evaluate common machine learning models with selected dataset.
        args:
            dataset name [str] - name of dataset to use for evaluation."""
        )
        return ReturnCode.SUCCESS

    def exit_program(self) -> ReturnCode:
        self.running = False
        return ReturnCode.SUCCESS

    def _handel_sync(self):
        if len(self.cur_input) < 2:
            print("Missing required argument <playlist name>")
            return ReturnCode.MISSING_ARGUMENT
        playlist_name = self.cur_input[1]
        if len(self.cur_input) > 3:
            platform1 = self.cur_input[2].lower()
            platform2 = self.cur_input[3].lower()
            if platform1 not in PLATFORMS:
                print(f"platform 1 has to be one of {PLATFORMS}")
                return ReturnCode.NO_VALIDE_INPUT
            if platform2 not in PLATFORMS:
                print(f"platform 2 has to be one of {PLATFORMS}")
                return ReturnCode.NO_VALIDE_INPUT
            if platform1 == platform2:
                print("platform 1 and platform 2 can't be the same")
                return ReturnCode.NO_VALIDE_INPUT
            method = getattr(self.sync, f"sync_{platform1}_{platform2}")
        else:
            method = self.sync.sync_all
        result = method(playlist_name)
        if result == ReturnCode.NO_PLAYLIST_FOUND:
            print(f"Playlist '{playlist_name}' has to exist on all platforms")
            return ReturnCode.NO_VALIDE_INPUT
        return ReturnCode.SUCCESS

    def _handel_data(self):
        if len(self.cur_input) < 2:
            print(
                "Missing action parameter.\ndata <action>\nOptions: 'new' 'load' 'expand' 'guess' 'process'"
            )
            return ReturnCode.MISSING_ARGUMENT
        match self.cur_input[1].lower():
            case "new":
                return self._handel_data_new()
            case "load":
                return self._handel_data_load()
            case "expand":
                return self._handel_data_expand()
            case "guess":
                return self._handel_data_guess()
            case "process":
                return self._handel_data_process()
            case _:
                print(f"command not found: {self.cur_input[1]}")
                return ReturnCode.NO_COMMAND

    def _handel_data_new(self):
        if len(self.cur_input) < 3:
            print("Missing required argument <dataset name>\ndata new <dataset name>")
            return ReturnCode.MISSING_ARGUMENT
        name = self.cur_input[2]
        self.df_handler.create_new_dataset_raw(name)
        return ReturnCode.SUCCESS

    def _handel_data_load(self):
        if len(self.cur_input) < 3:
            print("Missing required argument <dataset name>\ndata load <dataset name>")
            return ReturnCode.MISSING_ARGUMENT
        name = self.cur_input[2]
        result = self.df_handler.load_dataset_from_csv(name)
        if result == ReturnCode.NO_DATASET:
            print(f"No dataset with name '{name}'")
            return ReturnCode.NO_VALIDE_INPUT
        return ReturnCode.SUCCESS

    def _handel_data_expand(self):
        if len(self.cur_input) < 3:
            print(
                "Missing required argument <platform 1>\ndata expand <platform 1> <platform 2> <repeat>"
            )
            return ReturnCode.MISSING_ARGUMENT
        if len(self.cur_input) < 4:
            print(
                "Missing required argument <platform 2>\ndata expand <platform 1> <platform 2> <repeat>"
            )
            return ReturnCode.MISSING_ARGUMENT

        platform1 = self.cur_input[2].lower()
        platform2 = self.cur_input[3].lower()
        if platform1 not in PLATFORMS:
            print(f"platform 1 has to be one of {PLATFORMS}")
            return ReturnCode.NO_VALIDE_INPUT
        if platform2 not in PLATFORMS:
            print(f"platform 2 has to be one of {PLATFORMS}")
            return ReturnCode.NO_VALIDE_INPUT
        if platform1 == platform2:
            print("platform 1 and platform 2 can't be the same")
            return ReturnCode.NO_VALIDE_INPUT

        if len(self.cur_input) > 4:
            try:
                repeat = int(self.cur_input[4])
            except ValueError:
                print("Argument <repeat> has to be a integer")
                return ReturnCode.NO_VALIDE_INPUT
        else:
            repeat = 1

        result = self.df_handler.expand_dataset_with_songs(platform1, platform2, repeat)
        if result == ReturnCode.NO_DATASET:
            print("No dataset loaded. Use: data load <dataset name>")
            return ReturnCode.NOT_LOADED
        return ReturnCode.SUCCESS

    def _handel_data_guess(self):
        result = self.df_handler.add_guess_ml_data()
        if result == ReturnCode.NO_DATASET:
            print("No dataset loaded. Use: data load <dataset name>")
            return ReturnCode.NOT_LOADED
        return ReturnCode.SUCCESS

    def _handel_data_process(self):
        if len(self.cur_input) > 2:
            if self.cur_input[2].lower() == "true":
                override = True
            elif self.cur_input[2].lower() == "false":
                override = False
            else:
                print("Argument <override> takes only true | false")
                return ReturnCode.NO_VALIDE_INPUT
        else:
            override = False
        result = self.df_handler.process_dataset_for_ml(override)
        if result == ReturnCode.NO_DATASET:
            print("No dataset loaded. Use: data load <dataset name>")
            return ReturnCode.NOT_LOADED
        return ReturnCode.SUCCESS

    def _handel_eval(self):
        if len(self.cur_input) < 2:
            print("Missing required argument <dataset name>\neval <dataset name>")
            return ReturnCode.MISSING_ARGUMENT
        name = self.cur_input[1]
        e = Eval()
        result = e.load_dataset_from_csv(name)
        if result == ReturnCode.NO_DATASET:
            print(f"No dataset with name '{name}'")
            return ReturnCode.NO_VALIDE_INPUT
        e.print_results()
        return ReturnCode.SUCCESS
