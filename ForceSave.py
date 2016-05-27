import sublime, sublime_plugin, subprocess, os, sys, datetime
from io import StringIO

class EventDump(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        # Extract file extension from currently saved file
        file_split = view.file_name().split("/")
        length = len(file_split)
        file = file_split[length-1]
        lastDot = file.rfind(".")
        file_extension = file[lastDot+1:]
        file_wo_extension = file[:lastDot]

        # Determine if this is a SFDC type
        sfdc_meta_type=""
        if file_extension == "cls":
            sfdc_meta_type = "classes"
        elif file_extension == "page":
            sfdc_meta_type = "pages"
        elif file_extension == "resource":
            sfdc_meta_type = "staticresources"
        elif file_extension == "component":
            sfdc_meta_type = "components"
        elif file_extension == "trigger":
            sfdc_meta_type = "triggers"
        elif file_extension == "apex":
            sfdc_meta_type = "_apex_"

        # If it is an SFDC type proceed to save
        if sfdc_meta_type != "":
            # Get workspace directory
            # assuming the parent dir is 3 directories up from file being saved
            # workspace_dir = file_split[:-1]  <--- CAUSING ISSUES BECAUSE OF DIFF SAVE PLACES
            workspace_dir = file_split[:5]
            workspace_dir = '/'.join(workspace_dir)
            workspace_dir = workspace_dir + '/'
            
            print(workspace_dir)
            #### path issues for files being saved from different locations

            # Generate shell commands
            # Login, cd into workspace dir, execute force cli save
            commands = ["cd " + workspace_dir,
                        "./login",
                        "force push -f src/" + sfdc_meta_type + "/" + file]

                        # "force push -type " + sfdc_meta_type + " -name " + file_wo_extension]
            
            if sfdc_meta_type == "_apex_":
                commands[2] = "force apex ./" + file

            print("Executing: " + workspace_dir)


            command = " && ".join(commands)

            # Show console window and return focus to current view
            sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": True})
            view.window().focus_group(view.window().active_group())

            startTime = datetime.datetime.now()
            print("")
            print(command)
            print("")
            print("SFDC save started: " + file + " @ " + datetime.datetime.strftime(startTime, '%-I:%M:%S %p'))
            print("")

            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            while proc.poll() is None:
                line = proc.stdout.readline()
                lineToString = line.strip().decode("utf-8")
                if lineToString:
                    print("     " + lineToString)


            endTime = datetime.datetime.now()
            print("")
            print("SFDC save ended: " + file + " @ " + datetime.datetime.strftime(endTime, '%-I:%M:%S %p'))
            sublime.active_window().run_command("show_panel", {"panel": "console", "toggle": False})
            view.window().focus_group(view.window().active_group())
