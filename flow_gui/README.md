# modes of logiclance


## 1. --gui

    🖥️ Launches the graphical interface for flow execution.

    Example:

    `logiclance --gui`

## 2. --cli <username> <password> <flow>

    🧑‍💻 Runs the flow in CLI mode using credentials from employee_details.csv.

    Example:

    `logiclance --cli sanjay admin123 synthesis`

## 3. --cli <username> <password> <flow> <custom_script_path>

    🔧 Same as CLI mode above, but overrides the default script with a user-provided one.

    Example:

    `logiclance --cli sanjay admin123 synthesis /path/to/custom_script.tcl`

## 4. --cli <username> <password> <flow> --interactive

    🧠 Interactive CLI mode – shows selectable stages the user is authorized to run.

    Example:

    `logiclance --cli sanjay admin123 synthesis --interactive`

## 5. --help

    📘 Shows usage instructions and examples.

    Example:

    `logiclance --help`


# IMPORTANT:
Don't change the format 
`logiclance --cli <username> <password> <flow> [optional script path] [--interactive]`