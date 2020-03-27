import logging.config
import matplotlib.pyplot as plt
import os

from utils.utilities import set_log_level, get_project_path, convert_path_image_64
from wordcloud import WordCloud

logging.config.fileConfig("%s/logging.ini" % get_project_path())
set_log_level()
logger = logging.getLogger()


def words_clouds(counter: dict, file: str) -> str:
    """
        Create wordcloud
        :param counter: dict with the counter of words
        :param file: path to save the wordcloud
        :return: image in base64
        """
    wc = WordCloud(background_color="white", scale=2, max_words=40, relative_scaling=0.5,
                   normalize_plurals=False).generate_from_frequencies(counter)
    plt.figure(figsize=(20, 10))
    plt.imshow(wc)
    plt.axis("off")
    plt.savefig(get_project_path() + file)
    string_base_64 = convert_path_image_64(get_project_path() + file)
    os.remove(get_project_path() + file)
    return string_base_64
