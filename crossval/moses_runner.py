__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import subprocess
import logging
import re
import in_place


class MosesRunner:
    """
    A class that handles running of the MOSES binary program
    """

    def __init__(self, input_file, output_file, moses_opts):
        """
        :param input_file: The input file to run MOSES on
        :param output_file: The file to write MOSES program outputs to
        :param moses_opts: MOSES parameters
        """
        self.input = input_file
        self.output = output_file
        self.moses_options = moses_opts
        self.output_regex = re.compile(r"(-?\d+) (.+) \[(.+)\]")
        self.logger = logging.getLogger("mozi_snet")

    def run_moses(self):
        """
        Runs moses binary with the given options and input file.
        :return:
        :returns returncode: the return code of the process
        :returns stdout: the standard output of the process
        :returns stdin: the error output of the process, if any
        """
        cmd = "moses -i {0} -o {1} {2}".format(self.input, self.output, self.moses_options)
        self.logger.info("Started Moses with options: " + cmd)

        process = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        return process.returncode, stdout, stderr

    def format_combo(self, combo_file):
        """
        Format the raw combo output returned by moses into a file that has only the model and the combo complexity score
        :param combo_file: The path to the raw combo outout
        :return:
        """

        with in_place.InPlace(combo_file) as fp:
            for line in fp:
                match = self.output_regex.match(line.strip())
                if match is not None:
                    model = match.group(2)
                    complexity = match.group(3).split(",")[2].split("=")[1]
                    formatted_line = "%s,%s" % (model, complexity)
                    fp.write(formatted_line)

        # Add the model,complexity header

        with open(combo_file, "r+") as fp:
            content = fp.read()
            fp.seek(0, 0)
            fp.write("%s,%s\n%s" % ("model", "complexity", content))

