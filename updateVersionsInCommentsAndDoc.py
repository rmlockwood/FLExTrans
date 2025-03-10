import os
import re

# Define the new version comment and version string
new_version_comment = """
#   Version 3.13 - 3/10/25 - Ron Lockwood
#   Bumped to 3.13.
#
"""
new_version_string = 'FTM_Version    : "3.13",'

# Define the regex patterns to match the version comment and FTM_Version line
version_comment_pattern = re.compile(r'#\s+Version\s+\d+\.\d+\.\d+\s+-\s+\d+/\d+/\d+\s+-\s+.+\s+.+\n#\s+.*\n#')
ftm_version_pattern = re.compile(r'FTM_Version\s+:\s+"(\d+\.\d+\.\d+)",')

def update_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Check if the file contains the version comment and FTM_Version line
    if version_comment_pattern.search(content) and ftm_version_pattern.search(content):
        # Add the new version comment after the existing version comment
        content = version_comment_pattern.sub(lambda match: match.group(0) + '\n' + new_version_comment + '\n', content)
        
        # Update the FTM_Version line
        content = ftm_version_pattern.sub(new_version_string, content)

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
    root_directory = 'C:\\Users\\rlboo\\GitHub\\FLExTrans\\Dev'

    # Update the files in the directory
    update_files_in_directory(root_directory)