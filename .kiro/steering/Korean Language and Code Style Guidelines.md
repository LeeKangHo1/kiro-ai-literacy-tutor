<!------------------------------------------------------------------------------------
   Add Rules to this file or a short description and have Kiro refine them for you:   
-------------------------------------------------------------------------------------> 

## Korean Response Rules - Language Settings

- All responses must be written in Korean.
- Code comments should be written in Korean whenever possible.
- Technical terms should be written in both English and Korean when necessary (e.g., "컨테이너(container)").
- Error messages or logs must remain in their original language, but explanations should be provided in Korean.

---

## Korean Response Rules - Exception Cases

- The code itself (e.g., variable names, function names) must be written in English.
- Official documentation or command-line instructions should remain in their original language.
- Exceptions can be made only if the user explicitly requests another language.

---

## Terminal Command Execution Rules

- Before executing any command, check if the virtual environment is activated. If not, activate it before running commands.
- All terminal commands must be based on PowerShell.
- Do not include basic development server commands such as `npm run dev` or `python app.py` when testing. These are assumed to be already handled outside the scope of tests.

---

## File Creation and Code Writing Rules

- At the top of each file, add a comment indicating the file path and file name, like: `# path/to/filename.py`
