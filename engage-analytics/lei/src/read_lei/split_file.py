
import os


class Split:

    @staticmethod
    def split_json(source_filepath: str, dest_folder: str, split_file_prefix: str, records_per_file: int,
                   type_file: str) -> None:
        """
        Flat and Split JSON file
        :param source_filepath: path of the file for split
        :param dest_folder = path of the folder for the output
        :param split_file_prefix: preficx
        :param records_per_file: url for download the file
        :param type_file: url for download the file
        """

        if type_file == "lei2": os.system(
            "jq -c '.records = (.records[] | [.]) ' " + source_filepath + " > " + dest_folder + "temp.json")

        if type_file == "rr": os.system(
            "jq -c '.relations = (.relations[] | [.]) ' " + source_filepath + " > " + dest_folder + "temp.json")

        os.system("split -l " + str(records_per_file) + " -d " + dest_folder + "temp.json " + split_file_prefix)
        os.remove(source_filepath)
        os.remove(dest_folder + "temp.json")