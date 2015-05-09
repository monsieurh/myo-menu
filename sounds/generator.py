import os
import hashlib
import GoogleTTS
from multiprocessing.dummy import Pool as ThreadPool
from pydub import AudioSegment


class AudioGenerator(object):
    pass


class GoogleTTSGenerator(AudioGenerator):
    """
    Creates sound for any spoken text in the program
    """

    @staticmethod
    def generate_sound_threaded(param_dict=None):
        """
        Wrapper function to be called in a map for threading
        :type param_dict: dict
        """
        if not param_dict:
            return
        if param_dict["filename"] and param_dict["lang"] and param_dict["text"]:
            GoogleTTSGenerator.generate_sound(param_dict["filename"], param_dict["lang"], param_dict["text"])

    @staticmethod
    def generate_sound(dest, lang, text):
        """
        Creates a mp3 sound to be reused
        :string filename:Name of the file to be created
        :string lang:two letter representation of the language
        :string text:the content to be read in the mp3 file
        """
        language = lang.lower()
        print "Creating {}".format(dest)
        GoogleTTS.audio_extract(text, {"language": language, "output": dest})


class AudioFileConverter(object):
    @staticmethod
    def convert(source_file, dest_file, src_format, dst_format):
        sound_sample = AudioSegment.from_file(source_file, format=src_format)
        sound_sample.export(dest_file, dst_format)


class Hasher(object):
    """
    Hasher object that hashes text to a short format. Used to check if sound file is already generated before calling
    a web service
    """

    def __init__(self, algorithm=hashlib.sha1, output_len=6):
        """
        Ctor
        :param algorithm: The function used to hash the text (default:hashlib.sha1)
        :param output_len: The desired output length of the hash : N first characters (default 6)
        """
        self.output_length = output_len
        self.algorithm = algorithm

    def get_hash(self, text):
        """
        Returns the hash of a given text
        :param text: Text to hash
        :type text: str
        :return: Unique hash
        :rtype: str
        """
        full_hash = self.algorithm(text.encode('UTF-8')).hexdigest()
        return full_hash[:self.output_length]


class AudioFileManager(object):
    """
    Checks if text sound files are missing and builds them if needed.
    Uses thread to create mp3 in parallel
    """
    FALLBACK_SOUND_FORMAT = "wav"
    POOL_NUMBER = 8

    def __init__(self, locale, output_folder, file_ext="mp3"):
        self._locale = locale.lower()
        self._output_folder = os.path.abspath(output_folder)
        self._thread_pool = ThreadPool(self.POOL_NUMBER)
        self._file_ext = file_ext
        self.current_sound_format = file_ext
        self.hasher = Hasher()

    def _is_built(self, text):
        """
        Check if the file is present on the filesystem
        :param text: The text to be synthesized
        :return: True if the file is already present
        """
        return os.path.exists(self._make_filename(text))

    def _make_filename(self, text):
        short_hash = self.hasher.get_hash(text)
        filename = "{}.{}".format(short_hash, self._file_ext)
        return os.path.join(self._output_folder, filename)

    def lazy_build_files(self, text_list):
        """
        Builds a list of text files in a single call if they are not already present
        :param text_list: list of text to be built
        """
        to_build = [text for text in text_list if not self._is_built(text)]
        self.build_audio_files(to_build)

    def get(self, text):
        """
        Returns a playable wx.Sound object containing the text. Reuses existing files, or creates it if needed.
        :param text: Text string to be vocalized
        :type text: str
        :return: A wx.Sound object containing the TTSed text
        :rtype: wx.Sound
        """
        file_path = self._make_filename(text)
        if not os.path.exists(file_path):
            GoogleTTSGenerator.generate_sound(file_path, self._locale, text)

        return AudioSegment.from_file(file_path, format=self._file_ext)

    def build_audio_files(self, text_list):
        """
        Builds audio files even if they are already present
        """
        # if not self._key_list or not self._generator or not self._parser:
        # return
        args_list = []
        print "Found {} audio files to generate...".format(len(text_list))
        for text in text_list:
            args_list.append(
                {"filename": self._make_filename(text), "lang": self._locale, "text": text.encode('utf-8')})

        self._thread_pool.map(GoogleTTSGenerator.generate_sound_threaded, args_list)

    def _get_audio_files(self):
        """
        Returns a list of present audiofiles on the system
        :return:
        """
        return [os.path.join(self._output_folder, filename) for filename in os.listdir(self._output_folder)]

    def convert_audio_files(self, source_format='mp3', dest_format=FALLBACK_SOUND_FORMAT):
        """
        Converts all audio files to a different encoding using pydub/ffmpeg The default destination format is 'wav'
        :param source_format: a 3-4 letters extension representing the source format
        :type source_format: str
        :param dest_format: a 3-4 letters extension representing the target format
        :type dest_format: str
        """
        self.current_sound_format = dest_format
        all_audio_files = self._get_audio_files()
        # List of files without their extension for comparison
        source_files = [os.path.splitext(filename)[0] for filename in all_audio_files if
                        filename.endswith(source_format)]
        dest_files = [os.path.splitext(filename)[0] for filename in all_audio_files if filename.endswith(dest_format)]

        to_convert = [filename for filename in source_files if filename not in dest_files]

        for filename in to_convert:
            abs_src_path = os.path.abspath(os.path.join(self._output_folder, "{}.{}".format(filename, source_format)))
            abs_dst_path = os.path.abspath(os.path.join(self._output_folder, "{}.{}".format(filename, dest_format)))
            AudioFileConverter.convert(abs_src_path, abs_dst_path, source_format, dest_format)
            print "Done converting {} from {} to {}".format(filename, source_format, dest_format)
