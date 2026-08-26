import os
import re

# Change version # in 3 places and the date.

# Define the new version comment and version string
new_version_comment = \
"""#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
"""
new_version_string = 'FTM_Version    : "3.17",'

# Pull just the version number out of the string above. We substitute that number into each file rather than the whole line so that whatever spacing
# a given file already uses around FTM_Version and the colon is left alone.
new_version_number = re.search(r'"([^"]*)"', new_version_string).group(1)

# Define the regex patterns to match the version comment and FTM_Version line. Both patterns use [ \t] rather than \s so that a run of whitespace can
# never swallow a newline and match across lines. The FTM_Version pattern allows any amount of space -- or none at all -- both before and after the
# colon, because the modules aren't consistent: most have "FTM_Version    : " but some have "FTM_Version: " or "FTM_Version:     ".
version_comment_pattern = re.compile(r'^#[ \t]+Version[ \t]+.*\n#[ \t]*.*\n#', re.MULTILINE)
ftm_version_pattern = re.compile(r'(FTM_Version[ \t]*:[ \t]*")(\d+\.\d+[^"]*)(")')

def update_file(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Check if the file contains the version comment

    if version_comment_pattern.search(content):

        # Add the new version comment above the first occurrence of the existing version comment
        content = version_comment_pattern.sub(lambda match: new_version_comment + match.group(0), content, count=1)

        # Update the FTM_Version line. Keep the text on either side of the version number, so only the number itself changes.
        content = ftm_version_pattern.sub(lambda match: match.group(1) + new_version_number + match.group(3), content)

        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f'Updated: {file_path}')

    else:
        print(f'No matching patterns found in: {file_path}')

def update_files_in_directory(directory):

    for root, _, files in os.walk(directory):

        for file in files:

            if file.endswith('.py'):

                file_path = os.path.join(root, file)
                update_file(file_path)

if __name__ == "__main__":

    # Define the root directory to start the search
    root_directory = r'C:\Users\rlboo\GitHub\FLExTrans\Dev'

    # Update the files in the directory
    update_files_in_directory(root_directory)
