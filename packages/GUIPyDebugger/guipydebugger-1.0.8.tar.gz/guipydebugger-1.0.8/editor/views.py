import io
import json
import sys
import traceback

from . import utils
from diagrammer import views as project_info
from diagrammer import venv_path

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

if project_info.entry_point_path:
    debug_shell = utils.Debugger(project_info.entry_point_path)
    # Create a programmatically controllable debugger instance
    if len(venv_path) > 0:
        sys.path.append(venv_path[0])
    # if it was assigned in start.py, this allows skipping recreating the entire virtual environment (SLOWWWW)


# Create your views here.
@csrf_exempt
def editor(request):
    if request.method == "POST":

        output = ""
        # set output to empty string

        data = json.loads(request.body)
        # deserialize json object 

        if data.get("handler") == "Code Executor":
            output_buffer = io.StringIO()
            # Redirect standard output to the in-memory buffer
            sys.stdout = output_buffer
            sys.stderr = output_buffer

            code = data.get('code')
            # get the value under "code" key

            try:
                exec(code)
            except Exception as e:
                # Capture the exception and its traceback
                print(f"\nError: {str(e)}\n")
                print(traceback.format_exc())


            output = output_buffer.getvalue()
            output = output.replace("\n", "<br>")  
            # Replace newlines with HTML break tags

            sys.stdout = sys.__stdout__ 
            sys.stderr = sys.__stderr__
            # Restore stdout and stderr

            return JsonResponse({"output": output})
        
        if data.get("handler") == "PDB Command":
            command = data.get("pdb_command")
            # isolate the desired command
            try:
                output= debug_shell.execute_debug_cmd(command)
            except NameError as e:
                print("\n[ERROR] No entry point was placed in a python file")
                print("Please place #ENTRY on line one of the file you would like to debug\n")
                
                print("[WARNING] Take a look at the console output in setup, sometimes file permissions cause files to skip duplication hence this error")
                print("Try running the gui_pdb command again from inside the directory you would like to debug.\n(gui_pdb defaults to the cwd when no argument is passed)")
                output = "Please specify an entry point for the debug shell.\n\nIf you have, ensure file permissions are not causing issues"

            return JsonResponse({"output": output})
            # return a JSON object storing the string results of the execution

    return render(request, 'editor/editor.html')