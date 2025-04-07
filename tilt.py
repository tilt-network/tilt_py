from options import Options
from utils import eprint
from connection import Connection


class Tilt:

    def __init__(self, program_id: str, options: Options = None):
        self.__options = options
        self.__program_id = self.validate(program_id)
        self.__conn = Connection(options.data_src, options.api_url)

    def run(self):
        self.__conn.run()

    def validate_program(self, project_name):
        program_id = self.__options.validate_program(project_name)
        if program_id is None:
            eprint(f'No such project: {project_name}')
