import tkinter as tk
from tkinter import filedialog, messagebox
import pyvips
import os
import abc
import shutil
import zipfile
import pathlib

class AbstractDZIConverter(metaclass=abc.ABCMeta):
    def __init__(self, root):
        self.root = root
        self.file_path = None
        self.output_dir = None
        self.select_file_button = tk.Button(
            root, text="Select File", command=self.select_file
        )
        self.select_file_button.pack(pady=10)

        self.select_output_button = tk.Button(
            root, text="Select Output Directory", command=self.select_output_directory
        )
        self.select_output_button.pack(pady=10)

        self.convert_button = tk.Button(
            root, text="Convert", command=self.convert_and_zip, state=tk.DISABLED
        )
        self.convert_button.pack(pady=10)


    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'select_file') and 
                callable(subclass.select_file) and 
                hasattr(subclass, 'convert_and_zip') and 
                callable(subclass.convert_and_zip) or 
                NotImplemented)

    @abc.abstractmethod 
    def select_file(self):
        raise NotImplementedError


    @abc.abstractmethod 
    def convert_and_zip(self):
        raise NotImplementedError

    def select_output_directory(self):
        self.output_dir = filedialog.askdirectory(title="Select Output Directory")
        if self.output_dir:
            messagebox.showinfo("Selected", f"Selected Output Directory: {self.output_dir}")
            self.check_ready()
            

    def check_ready(self):
        if self.file_path and self.output_dir:
            self.output_dir = os.path.abspath(self.output_dir)
            self.convert_button.config(state=tk.NORMAL)


class DZIConverter(AbstractDZIConverter):
    def __init__(self, root):
        super().__init__(root)
        

    def select_file(self):
        self.file_path = filedialog.askopenfilename(
            title="Select SVS/TIFF file",
            filetypes=[("SVS files", "*.svs"), ("TIF files", "*.tif"), ("TIFF files", "*.tiff")]
        )
        if self.file_path:
            messagebox.showinfo("Selected", f"Selected File: {self.file_path}")
            self.check_ready()


    def convert_and_zip(self):
        try:
            # Prepare output directory and file names
            file_path = self.file_path
            _, filename = os.path.split(file_path)
            output_dir = self.output_dir
            dzi_basename = "_".join(os.path.splitext(filename)[0].split(" "))
            dzi_output_dir = os.path.join(output_dir, f"{dzi_basename}_files")
            dzi_file_path = os.path.join(output_dir, f"{dzi_basename}.dzi")
            if not os.path.exists(dzi_output_dir):
                os.makedirs(dzi_output_dir, 0o666)

            # Convert SVS to DZI using pyvips
            image = pyvips.Image.new_from_file(file_path, access='sequential')
            #print(os.path.abspath(os.path.join((output_dir, dzi_basename))))
            image.dzsave(os.path.join(output_dir, dzi_basename))

            # Zip the DZI file and the associated folder
            """
            zip_filename = os.path.join(output_dir, f"{dzi_basename}.zip")
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(dzi_file_path, os.path.basename(dzi_file_path))
                for root, dirs, files in os.walk(dzi_output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=output_dir)
                        zipf.write(file_path, arcname)
            """
            # Cleanup the DZI files if desired
            #os.remove(dzi_file_path)
            #shutil.rmtree(dzi_output_dir)
            messagebox.showinfo("Success", f"Converted to DZI.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


def main():
    root = tk.Tk()
    root.title("Make It DZI Converter")
    app = DZIConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()