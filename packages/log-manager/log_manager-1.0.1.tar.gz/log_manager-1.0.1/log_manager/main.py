from datetime import datetime
import getpass
import os
import traceback
from stop_watch import StopWatch


class SetupError(ValueError):
    err_dict = {'permission': {'name': 'Permission Error',
                             'description': 'You do not have the appropriate permission to perform the action {}. The account in use is {}.'},
                'no_log_file': {'name': 'File Logging Error',
                             'description': '{} {}'},
                'sp_log': {'name': 'SharePoint Logging Error',
                             'description': '{} {}'}}

    def __init__(self, err_vars):
        """
Raise this when there's an application error
        :param err_vars:
        """
        e = self.err_dict.get(err_vars[0])
        if e:
            self.error = e['name']
            self.description = e['description'].format(err_vars[1], err_vars[2])

    def __str__(self):
        return '\n'.join(['MM Processing Manager Application', self.error, self.description])



class LogManager:  # v3.3.0
    file_logging = False
    screen_logging = False
    log_screen = None
    log_file = None
    add_log_files = {}
    message_body = ''

    def __init__(self, display=True, time_stamp=True, user=None, application_error_log=None):
        """
        Logging object to display messages on screen or write to text file
        :param display: Set as False to suppress print commands
        :param time_stamp: Set as False to suppress timestamp from first entry
        :param user: Recommended - import psutil -> user = psutil.Process().username()
        :param application_error_log: URL for fallback text file, to log LogManager errors

        """
        self.__display = display
        self.time_stamp = time_stamp
        self.timer = StopWatch()
        self.user = user
        self.application_error_log = r'C:\Temp\ApplicationError.txt' if not application_error_log else application_error_log

    def __repr__(self):
        out_str = '\n====================================\n'
        out_str = out_str + 'Log Manager\n'
        if self.user:
            out_str = out_str + '------------------------------------\n'
            out_str = out_str + 'Current user: ' + self.user + '\n'
        out_str = out_str + '------------------------------------\n'
        out_str = out_str + 'Screen logging: ' + str(self.screen_logging) + '\n'
        out_str = out_str + 'File logging: ' + str(self.file_logging) + '\n'
        if self.file_logging:
            out_str = out_str + 'Log file: ' + self.log_file + '\n'
        out_str = out_str + '====================================\n'

        return out_str

    def start_screen_logging(self, logging_object):
        self.screen_logging = True
        self.log_screen = logging_object

    def start_text_logging(self, log_file_url, reset_log=False):
        self.file_logging = True
        self.log_file = log_file_url
        if reset_log:
            backup_url = self.log_file.replace('.', '_bu.')
            if os.path.exists(backup_url):
                os.remove(backup_url)
            os.popen(' '.join(['copy', self.log_file, backup_url]))
            open(self.log_file, 'w').close()

    def start_sp_logging(self, context, log_name):
        raise SetupError(['sp_log', 'SharePoint logging has not been implemented yet.', 'Please call back later.'])

    def supplemental_text_log(self, log_name, log_file_url, reset_log=False):
        self.add_log_files[log_name] = log_file_url
        if reset_log:
            open(log_file_url, 'w').close()

    def write_log(self, log_message, log_file_name=None):
        if not self.log_file and not log_file_name:
            raise SetupError(
                ['no_log_file', 'No log file has been specified.',
                 'Please add LogManager.start_text_logging(log_file_url).'])

        if log_file_name:
            log_file = self.add_log_files[log_file_name]
        else:
            log_file = self.log_file

        if len(log_message) > 0:
            try:
                with open(log_file, 'a') as file:
                    file.write(log_message + '\n')
            except (PermissionError, FileNotFoundError) as e:
                try:
                    with open(self.application_error_log, 'w') as file:
                        file.write(f'An application failed whilst trying to write to the file: "{log_file}"\n')
                        file.write(f'The error message being written was: "{log_message}"\n')
                        file.write(f'Current user (os): {os.getlogin()}|{getpass.getuser()}')
                        file.write(e)
                except PermissionError:
                    raise SetupError(
                        ['permission', 'application_error_log',
                         f'Current user (os): {os.getlogin()}|{getpass.getuser()}'])
                except FileNotFoundError:
                    raise SetupError(
                        ['no_log_file', 'The default application_error_log cannot be accessed',
                         f'This needs to be available at : {self.application_error_log}'])
        elif log_message == 'crlf':
            try:
                with open(log_file, 'a') as file:
                    file.write('\n')
            except:
                msg = 'The application failed whilst trying to write a blank line to the file: "' + \
                      log_file + '"\n'
                print(msg)
                with open(self.application_error_log, 'w') as file:
                    file.write(msg)

    def separator(self, sep_char='-', log_file_name=None):
        if not self.file_logging:
            return
        if log_file_name is not None:
            log_file = self.add_log_files[log_file_name]
        else:
            log_file = self.log_file

        try:
            with open(log_file, 'a') as file:
                file.write((sep_char * 20) + '\n')
        except:
            with open(self.application_error_log, 'w') as file:
                file.write('The application failed whilst writing a separator to the file: "' + log_file + '"\n')
                file.write('The character being written was: "' + sep_char + '"\n')

    def create_entry(self, entries: list, new_lines=False, add_to_email=False, add_script_loc=False):
        file_logging = self.file_logging
        log_file_name = None
        if isinstance(entries, str):
            entries = [entries]
        elif isinstance(entries[0], str) and entries[0] == 'ext_log':  # use supplemental log
            log_file_name = entries[1]
            entries = entries[2:]
            file_logging = True
        out_list = [self.timer.now()] if self.time_stamp else []
        if add_script_loc:
            out_list.append(self.script_loc())
        if self.user:
            out_list.append(self.user)
        for entry in entries:  # Convert all log elements to strings
            try:
                e = str(entry)
            except TypeError:
                e = 'Blank entry'
            out_list.append(e)
        message_display = '\n'.join(out_list) if new_lines else ' : '.join(out_list)
        file_message = message_display if new_lines else '|'.join(out_list)

        if self.screen_logging:
            try:
                self.log_screen.insert("end", message_display + "\n")
                self.log_screen.see("end")
            except:
                message_display += '\n\nScreen logging disabled'

        if file_logging:
            self.write_log(file_message, log_file_name)

        if add_to_email:
            html_string = '|'.join(out_list)
            self.compose(html_string)

        if self.__display:
            print(message_display)

    def check_sum(self, df, name, check_val):
        if len(check_val) > 0:
            if len(df) > 0:
                count = len(df[df['ADDRESS KEY'] == check_val])
            else:
                count = 'No data'
            self.create_entry([name + ' CheckSum', check_val, count])

    def compose(self, in_str):
        self.message_body += (in_str + '<br>\n')

    def send(self, email):
        email.add_html(self.message_body, append=True, finalise=True)
        return email.send()

    def script_loc(self):
        def get_call_id(stack_line):
            fs = stack_line.split(',')
            url = fs[0].split('\\')[-1]
            ss = fs[1].strip().split(' ')
            line = ss[1]
            func = ss[-1][:-1]
            return url, line, func

        out_str = traceback.extract_stack(None, 3)[0]
        return ' > '.join(get_call_id(str(out_str)))


