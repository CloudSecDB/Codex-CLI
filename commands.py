import os
import time

from pathlib import Path
from prompt_file import *

def get_command_result(input, prompt_file):
    """
    Checks if the input is a command and if so, executes it
    Currently supported commands:
    - unlearn
    - unlearn all
    - start context
    - stop context
    - show context <n>
    - edit context
    - save context
    - clear context
    - load context <filename>
    - set engine <engine>
    - set temperature <temperature>
    - set max_tokens <max_tokens>
    - set shell <shell>

    Returns: command result or "" if no command matched
    """
    if prompt_file == None:
        return "", None
    
    config = prompt_file.config
    # configuration setting commands
    if input.__contains__("set"):
        # set temperature <temperature>
        if input.__contains__("temperature"):
            input = input.split()
            if len(input) == 4:
                config['temperature'] = float(input[3])
                prompt_file.set_headers(config)
                print("# Temperature set to " + str(config['temperature']))
                return "config set", prompt_file
            else:
                return "", prompt_file
        # set max_tokens <max_tokens>
        elif input.__contains__("max_tokens"):
            input = input.split()
            if len(input) == 4:
                config['max_tokens'] = int(input[3])
                prompt_file.set_headers(config)
                print("# Max tokens set to " + str(config['max_tokens']))
                return "config set", prompt_file
            else:
                return "", prompt_file
        elif input.__contains__("shell"):
            input = input.split()
            if len(input) == 4:
                config['shell'] = input[3]
                prompt_file.set_headers(config)
                print("# Shell set to " + str(config['shell']))
                return "config set", prompt_file
            else:
                return "", prompt_file
        elif input.__contains__("engine"):
            input = input.split()
            if len(input) == 4:
                config['engine'] = input[3]
                prompt_file.set_headers(config)
                print("# Engine set to " + str(config['engine']))
                return "config set", prompt_file
            else:
                return "", prompt_file

    if input.__contains__("show config"):
        print('\n')
        config = prompt_file.read_headers()
        # read the dictionary into a list of # lines
        lines = []
        for key, value in config.items():
            lines.append('\n# {}: {}'.format(key, value))
        print(''.join(lines))
        return "config shown", prompt_file

    # interaction deletion commands
    if input.__contains__("unlearn"):
        # if input is "unlearn all", then delete all the lines of the prompt file
        if input.__contains__("all"):
            # TODO maybe add a confirmation prompt or temporary file save before deleting file
            prompt_file.clear()
            return "unlearned interaction", prompt_file
        else:
        # otherwise remove the last two lines assuming single line prompt and responses
        # TODO Codex sometimes responds with multiple lines, so some kind of metadata tagging is needed
            prompt_file.clear_last_interaction()
        return "unlearned interaction", prompt_file

    # context commands
    if input.__contains__("context"):
        # start context
        if input.__contains__("start"):
            if config['context'] == 'off':
                config['context'] = 'on'
                
                # we need to have prompt_file now track openai_completion_input.txt
                prompt_file.turn_on_context()
                return "started context", prompt_file
            
            return "started context", prompt_file
        
        # stop context
        if input.__contains__("stop"):
            config['context'] = 'off'
            prompt_file.turn_off_context()
            return "stopped context", prompt_file
        
        if input.__contains__("default"):
            prompt_file.default_context()
            return "stopped context", prompt_file
        
        # show context <n>
        if input.__contains__("show"):
            print('\n')
            with open(prompt_file.file_name, 'r') as f:
                lines = f.readlines()
                lines = lines[5:] # skip headers
            
            line_numbers = 0
            if len(input.split()) > 3:
                line_numbers = int(input.split()[3])
            
            if line_numbers != 0:
                for line in lines[-line_numbers:]:
                    print('\n# '+line, end='')
            else:
                print('\n# '.join(lines))
            return "context shown", prompt_file
        
        # edit context
        if input.__contains__("edit"):
            # open the prompt file in text editor
            if config['shell'] != 'powershell':
                os.system('open {}'.format(prompt_file.file_name))
            else:
                os.system('start {}'.format(prompt_file.file_name))
            return "context shown", prompt_file

        # save context <filename>
        if input.__contains__("save"):
            # save the current prompt file to a new file
            # if filename not specified use the current time (to avoid name conflicts)

            filename = time.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
            if len(input.split()) == 4:
                filename = input.split()[3]
            
            prompt_file.save_to(filename)
            
            print('\n#\tContext saved to {}'.format(filename))
            return "context saved", prompt_file
        
        # clear context
        if input.__contains__("clear"):
            # temporary saving deleted prompt file
            prompt_file.clear()
            return "unlearned interaction", prompt_file
        
        # load context <filename>
        if input.__contains__("load"):
            # the input looks like # load context <filename>
            # write everything from the file to the prompt file
            input = input.split()
            if len(input) == 4:
                filename = input[3]
                prompt_file.load_context(filename)
                return "context loaded", prompt_file
            print('\n#\tInvalid command format, did you specify which file to load?')
            return "context loaded", prompt_file
    
    return "", prompt_file
