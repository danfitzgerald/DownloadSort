#  Copyright 2020 Daniel Fitzgerald
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import logging

DOWNLOADS_DIR = '.\\sample_downloads'  # REPLACE WITH PATH TO DOWNLOADS FOLDER
FOLDER_NAMES = ['Images', 'Documents', 'Executables', 'Other Files']


class StagedFile:
    def __init__(self, media_type, src, dst):
        self.media_type = media_type
        self.src = src
        self.dst = dst

    def move_file(self):
        os.rename(self.src, self.dst)

    def __str__(self):
        return self.media_type + ': ' + self.src + ' --> ' + self.dst


def stage_file(src: str) -> StagedFile:
    # Get desired folder given file extension.
    file_ext = src.split('.')
    if len(file_ext) > 1:
        file_ext = file_ext[-1]
    else:
        file_ext = None
    target_folder = ext_to_folder(file_ext)

    dst_l = src.split(os.sep)
    dst_l.insert(-1, target_folder)
    dst = os.path.join(*dst_l)

    # If the filename already exists at the destination find a suggested one that doesnt.
    i = 2
    # path_changed = False
    original_filename = dst_l[-1]
    original_dst = dst
    suggested_filename = None
    while os.path.exists(dst):
        # path_changed = True
        if file_ext:
            # Filename in the format 'name-i.ext'.
            suggested_filename = original_filename[:-len(file_ext) - 1] + '-' + str(i) + '.' + file_ext
        else:
            # Filename in the format 'name-i' i being an integer
            suggested_filename = original_filename + '-' + str(i)

        dst_l[-1] = suggested_filename
        dst = os.path.join(*dst_l)
        i += 1

    # If there is a suggested filename (ie because a file exists at the desired destination) suggest it.
    if suggested_filename:
        print("A file already exists at destination for %s." % original_dst)
        new_filename = input('Please enter a new destination filename [%s]: ' % suggested_filename)
        if not new_filename.strip() == '':
            dst_l[-1] = new_filename
            dst = os.path.join(*dst_l)

    return StagedFile(target_folder, src, dst)


def move_staged(staged_files: []) -> bool:
    success = True
    for staged_file in staged_files:
        try:
            staged_file.move_file()
        except FileExistsError:
            logging.error("Unable to move file. Destination already exists:\n" + str(staged_file))
            success = False
        except IsADirectoryError or NotADirectoryError:
            logging.error("IsADirectoryError or NotADirectoryError: Implementation error")
            success = False
        except FileNotFoundError:
            logging.error('FileNotFoundError: Either destination folder has not been created or source file no longer'
                          ' exists')
            success = False
        except OSError:
            logging.error("OSError: Oops")
            success = False
    return success


def ext_to_folder(ext: str) -> str:
    if ext == 'png' or ext == 'bmp' or ext == 'jpg' or ext == 'gif':  # Image Files
        return FOLDER_NAMES[0]  # Images.
    if ext == 'txt' or ext == 'text' or ext == 'pdf' or ext == 'doc' or ext == 'docx' or ext == 'ppt' or ext == 'pptx' \
            or ext == 'xls':  # Document Files
        return FOLDER_NAMES[1]  # Documents.
    if ext == 'exe' or ext == 'py' or ext == 'pyc':  # Executable files
        return FOLDER_NAMES[2]  # Executables

    # Else:
    return FOLDER_NAMES[3]  # Other Files.


def _main():
    mkdirs = []
    existing_dirs = []
    required_dirs = []
    # Stage files.
    sd = os.scandir(path=DOWNLOADS_DIR)
    staged_files = []  # Sort log is outputted at end of programs execution.
    i = 0  # Counter
    for f in sd:
        # Traverse through folders to find folders we require to make.
        if f.is_dir():
            path = f.path
            dir_name = path.split(os.sep)[-1]
            if not len(existing_dirs) == len(FOLDER_NAMES) and dir_name in FOLDER_NAMES:
                existing_dirs.append(dir_name)

        # Traverse through files sorting them.
        elif f.is_file():
            sf = stage_file(f.path)
            staged_files.append(sf)

            # If the folder required for the staged file does not exist, stage the folder to be created if it hasn't
            # previously been staged.
            if sf.media_type not in existing_dirs or sf.media_type not in required_dirs:
                required_dirs.append(sf.media_type)
            print(str(i) + ': ' + str(sf))
            i += 1

    print()  # Line break.
    lcv = True  # Loop control variable.
    while lcv:
        usrin = input('Are you okay with moving the above files to their destinations (y/n)? ')
        if usrin.lower() == 'y':
            lcv = False  # Continue to move files.
        if usrin.lower() == 'n':
            return None  # Exit.

    # Create staged folders to be filled.
    # Find folders to make:
    for rdir in required_dirs:
        if rdir not in existing_dirs:
            mkdirs.append(rdir)

    for mkdir in mkdirs:
        os.mkdir(DOWNLOADS_DIR + os.sep + mkdir)
    # Move the staged files to their corresponding destinations.
    if move_staged(staged_files):
        print('Completed without errors.')
    else:
        print('Script completed check errors.')


if __name__ == '__main__':
    _main()
