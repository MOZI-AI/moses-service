__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import subprocess
import logging
import re
import tempfile
import fileinput

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
        if not "W1" in moses_opts: moses_opts += ' -W1'
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

        cmd = ["moses", "-i", self.input, "-o", self.output]

        for opt in self.moses_options.split():
            cmd.append(opt)

        self.logger.info("Started Moses with options: " + self.moses_options)

        process = subprocess.Popen(args=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        return process.returncode, stdout, stderr

    def format_combo(self, combo_file):
        """
        Format the raw combo output returned by moses into a file that has only the model and the combo complexity score
        :param combo_file: The path to the raw combo output
        :return:
        """

        with fileinput.input(combo_file, inplace=True) as fp:
            for line in fp:
                match = self.output_regex.match(line.strip())
                if match is not None:
                    model = match.group(2).strip()
                    if model == "true" or model == "false":
                        continue
                    complexity = match.group(3).split(",")[2].split("=")[1]
                    formatted_line = "%s,%s" % (model, complexity.strip())
                    print(formatted_line)

        with open(combo_file, "r+") as fp:
            content = fp.read()
            fp.seek(0, 0)
            fp.write("%s,%s\n%s" % ("model", "complexity", content))