import os
import shutil
import subprocess

def build_pdf(export_dir):
    """
    Checks for latexmk and compiles the main.tex file in the given export_dir.
    Returns (success_boolean, output_message)
    """
    main_tex_path = os.path.join(export_dir, 'main.tex')
    
    if not os.path.exists(main_tex_path):
        return False, "main.tex not found in export directory."
    
    latexmk_path = shutil.which("latexmk")
    if not latexmk_path:
        return False, "latexmk is not installed or not in PATH. Please install a LaTeX distribution (like TeX Live or MiKTeX) containing latexmk."
    
    # Run latexmk
    # -pdf: generate PDF using pdflatex
    # -interaction=nonstopmode: don't stop on errors
    # -cd: change to the directory of the main file before running
    # -f: force compilation even if there are errors
    command = [
        latexmk_path,
        "-pdf",
        "-interaction=nonstopmode",
        "-f",
        "-cd",  
        main_tex_path
    ]
    
    try:
        # We run it with cwd=export_dir just to be safe, though -cd does this
        process = subprocess.run(
            command,
            cwd=export_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False  # Don't raise exception on non-zero exit code
        )
        
        pdf_path = os.path.join(export_dir, 'main.pdf')
        
        if os.path.exists(pdf_path):
            return True, "PDF compiled successfully."
        else:
            return False, f"latexmk ran but PDF was not generated.\n\nLog:\n{process.stdout}"
            
    except Exception as e:
        return False, f"Error executing latexmk: {str(e)}"
