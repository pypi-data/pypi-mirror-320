
""" --------------------------------------------------------------------------
Titre : ye3sld
Auteur : palw3ey
Mainteneur : palw3ey
Licence : MIT
Pays : France
Email : palw3ey@gmail.com
Site : https://github.com/palw3ey/ye3sld

Description :

Créer un fichier HTML
  qui affiche la structure de la liste des dossiers d'un bucket S3.

Create an html file
  that show the directory listing structure of an s3 bucket.

Première : 2024-12-30
Révision : 2025-01-12
Version : 1.0.4
-------------------------------------------------------------------------- """

# Import libraries
import os
import sys
import argparse
import re
from datetime import datetime
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# hide any traceback information when an exception occurs
sys.tracebacklimit = 0

# Optional, set your defaults here :
DEFAULT_SERVICE_NAME = 's3'
DEFAULT_ENDPOINT_URL = ''
DEFAULT_AWS_ACCESS_KEY_ID = ''
DEFAULT_AWS_SECRET_ACCESS_KEY = ''
DEFAULT_REGION_NAME = ''
DEFAULT_BUCKET_NAME = ''
DEFAULT_PREFIX = ''
DEFAULT_OUTPUT_HTML_LOCAL = 'index-sld.html'
DEFAULT_OUTPUT_HTML_S3 = 'index-sld.html'
DEFAULT_HREF_BASE_URL = ''
DEFAULT_REGEX_EXCLUDE = ''
DEFAULT_OVERWRITE = False
DEFAULT_UPLOAD = False
DEFAULT_CLI = False


def check_s3_file_exists(s3, bucket_name, output_html_s3):
    """ Check if s3 file exists """

    try:
        s3.head_object(Bucket=bucket_name, Key=output_html_s3)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise


def list_files(s3, bucket_name, prefix, regex_exclude):
    """ List files in the S3 bucket """

    all_files = []
    continuation_token = None

    # split by commas, and strip whitespace
    patterns_spit = regex_exclude.split(',')
    patterns = [
        pattern.strip()
        for pattern in patterns_spit
        if pattern.strip()
    ]

    while True:
        if continuation_token:
            response = s3.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                ContinuationToken=continuation_token
            )
        else:
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                size = obj['Size']
                last_modified = obj['LastModified']
                # Check if the key matches any of the exclude patterns
                if not any(re.search(pattern, key) for pattern in patterns):
                    all_files.append(f"{key}?{size}?{last_modified}")

        # Check if there are more files to retrieve
        if response.get('IsTruncated'):
            continuation_token = response.get('NextContinuationToken')
        else:
            break

    return all_files


def get_full_path(output_html_local):
    """ Get full path of local file """

    if os.path.isabs(output_html_local):
        full_path = output_html_local
    else:
        full_path = os.path.join(os.getcwd(), output_html_local)

    return full_path


def finalization(s3, params):
    """ Upload and show final message """

    if params["upload"]:
        if not params["overwrite"] and check_s3_file_exists(
            s3,
            params["bucket_name"],
            params["output_html_s3"]
        ):

            message_exist_s3 = (
                f"Upload canceled : {params['output_html_s3']} "
                "already exists in bucket."
            )
            if not params["cli"]:
                response = messagebox.askyesno(
                    "File Exists", f"{params['output_html_s3']} "
                    "already exists in the bucket. "
                    "Do you want to overwrite it?"
                )
                if not response:
                    return message_exist_s3
            else:
                return (
                    message_exist_s3 +
                    "\nHint ? Add this option to overwrite : --overwrite"
                )

        s3.upload_file(
            params["output_html_local"],
            params["bucket_name"],
            params["output_html_s3"]
        )
        message_upload = f" and uploaded: {params['output_html_s3']}"
    else:
        message_upload = ""

    return (
        f"Success : HTML file created: "
        f"{params['output_html_local']}{message_upload}"
    )


def generate_html(params):
    """ Generate HTML """

    required_args = {
        'Service name': params["service_name"],
        'Endpoint URL': params["endpoint_url"],
        'Access key ID': params["aws_access_key_id"],
        'Secret access key': params["aws_secret_access_key"],
        'Bucket name': params["bucket_name"],
        'Local output HTML file': params["output_html_local"]
    }

    missing_args = []

    for arg_name, arg_value in required_args.items():
        if arg_value is None or arg_value == '':
            missing_args.append(arg_name)

    if missing_args:
        return f'Missing required arguments : {", ".join(missing_args)}'

    params["output_html_local"] = get_full_path(params["output_html_local"])

    # Check if the local file already exists
    if os.path.exists(params["output_html_local"]) and not params["overwrite"]:
        message_exist_local = (
            f"Operation canceled : {params['output_html_local']} "
            "already exists locally."
        )
        if not params["cli"]:
            response = messagebox.askyesno(
                "File Exists",
                f"{params['output_html_local']} already exists locally. "
                "Do you want to overwrite it?"
            )
            if not response:
                return message_exist_local
        else:
            return (
                message_exist_local +
                "\nHint ? Add this option to overwrite : --overwrite"
            )

    try:

        current_date = datetime.now().isoformat()

        # Start building the HTML file
        with open(params["output_html_local"], 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="generator" content="ye3sld">
        <meta name='generation-date' content='""" + current_date + """'>
        <title>SLD : S3</title>
        <style>

            body {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                transition: background-color 0.3s, color 0.3s;
                word-wrap: break-word;
            }

            h1 {
                margin: 0;
            }

            #caption {
                display: block;
                font-size: 0.7em;
                color: gray;
                margin-top: 0.2em;
            }

            #s3output {
                display: none;
            }

            .info {
                display: none;
                margin-left: 10px;
                font-size: 0.9em;
                color: #789;
            }

            a {
                color: #ecf0f1;
                text-decoration: none;
                border-radius: 5px;
                transition: background-color 0.3s, color 0.3s;
                padding: 2px 5px 2px 5px;
            }

            a:hover {
                background-color: #204e8a;
                color: #fff;
            }

            ul {
                list-style-type: none;
                padding-left: 0px;
            }

            ul ul {
                padding-left: 1em;
            }

            li {
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 2px 5px 2px 5px;
                margin: 5px 0;
                transition: box-shadow 0.3s;
            }

            li:hover {
                box-shadow: 0 2px 8px 2px rgba(0, 0, 0, 0.7);
            }

        </style>
    </head>
    <body>
        <h1 id="title" title="">SLD : S3</h1>
        <span id="caption">
            Structure de la liste des dossiers S3
            <span id="filescount"></span>
        </span>

        <pre id="s3output">
""")

            # Initialize a session using Boto3
            s3 = boto3.client(
                service_name=params["service_name"],
                endpoint_url=params["endpoint_url"],
                aws_access_key_id=params["aws_access_key_id"],
                aws_secret_access_key=params["aws_secret_access_key"],
                region_name=params["region_name"]
            )

            # List files in the bucket
            for file in list_files(
                s3,
                params["bucket_name"],
                params["prefix"],
                params["regex_exclude"]
            ):
                # Remove the bucket name prefix
                relative_path = file.replace(
                    f"{params['bucket_name']}/",
                    "",
                    1
                )
                # write to the HTML file
                f.write(relative_path + "\n")

            f.write("""        </pre>
        <div id="folder-structure"></div>
        <script>

            // Get the content of the hidden <pre>, and split into an array
            const preContent = document.getElementById('s3output').textContent;
            const paths = preContent.trim().split('\\n');

            // Build the structure
            function buildFolderStructure(paths) {

                const root = {};

                paths.forEach(path => {
                    const parts = path.split('/')
                        .filter(part => part && !part.startsWith('?'));
                    let current = root;

                    parts.forEach(part => {
                        if (!current[part]) {
                            current[part] = {};
                        }
                        current = current[part];
                    });
                });

                return root;
            }

            // Create the list
            function createList(structure, basePath = '') {

                const ul = document.createElement('ul');

                for (const key in structure) {

                    const parts = key.split('?');

                    const a = document.createElement('a');
                    const fullPath = `${basePath}/${parts[0]}`;
                    a.textContent = parts[0];
                    a.href = encodeURIComponent(fullPath);
                    a.target = "_blank";

                    const li = document.createElement('li');
                    li.appendChild(a);

                    if (parts[1] !== undefined && parts[2] !== undefined) {
                        const span = document.createElement('span');
                        span.className = 'info';
                        span.textContent = `Size: ${formatBytes(parts[1])} |
                            Last Modified: ${parts[2]}`;
                        li.appendChild(span);
                    }

                    // If the current key has children, create a nested list
                    if (Object.keys(structure[key]).length > 0) {
                        li.appendChild(createList(structure[key], fullPath));
                    }

                    ul.appendChild(li);

                }

                return ul;
            }

            const folderStructure = buildFolderStructure(paths);
            const folderList = createList(folderStructure);

            result = document.getElementById('folder-structure')
            result.appendChild(folderList);

            // The url base to prepend to all href
            const href_base_url = '""" + params['href_base_url'] + """';

            // Prepend the base to each link's href
            document.querySelectorAll('ul a').forEach(link => {
                link.href = href_base_url + link.getAttribute('href');
            });

            // Show files count
            filescount=document.querySelectorAll('li').length - (
                document.querySelectorAll('ul').length-1
            );
            document.getElementById('filescount').innerHTML =
                ` | Fichiers : ${filescount}`
            document.getElementById('title').setAttribute(
                'title',
                `S3 Directory Listing Structure | Files : ${filescount}`
            );

            // Converts a size in bytes to a human-readable format
            function formatBytes(bytes) {
                if (bytes === 0) return '0 Bytes';
                const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
                const i = Math.floor(Math.log(bytes) / Math.log(1024));
                const formattedSize = (bytes / Math.pow(1024, i)).toFixed(2);
                return `${formattedSize} ${sizes[i]}`;
            }

            // Show size and last modified info when click on title
            document.getElementById('title').onclick = function() {
                // Find the first <li> element on the page
                const firstLi = document.querySelector('li');
                const span = firstLi ? firstLi.querySelector('.info') : null;

                // Determine the current visibility state
                const shouldShow = span && (span.style.display === 'none' ||
                    span.style.display === '');

                // Set the display style based on the determined state
                document.querySelectorAll('li').forEach(li => {
                    const span = li.querySelector('.info');
                    if (span) {
                        span.style.display = shouldShow ? 'inline' : 'none';
                    }
                });
            };

            // Show size and last modified info when click on li
            result.onclick = function(event) {
                const li = event.target.closest('li');
                if (li &&
                    event.target.tagName !== 'UL' &&
                    event.target.tagName !== 'A' &&
                    event.target.tagName !== 'SPAN') {

                    const span = li.querySelector('.info');

                    span.style.display =
                        (span.style.display === 'none' ||
                        span.style.display === '') ?
                        'inline' : 'none';
                }
            };

        </script>
    </body>
</html>
""")

        return finalization(s3, params)

    except (IOError, ValueError, BotoCoreError, ClientError) as e:
        return f"An error occurred: {str(e)}"


def cli_mode():
    """ CLI mode """

    parser = argparse.ArgumentParser(
        description='Create an HTML file that shows the directory listing '
        'structure of an S3 bucket.'
    )

    parser.add_argument(
        '--service_name',
        default=DEFAULT_SERVICE_NAME,
        help='Service name (default: s3)'
    )
    parser.add_argument(
        '--endpoint_url',
        default=DEFAULT_ENDPOINT_URL,
        help='S3 endpoint URL'
    )
    parser.add_argument(
        '--aws_access_key_id',
        default=DEFAULT_AWS_ACCESS_KEY_ID,
        help='AWS Access Key ID'
    )
    parser.add_argument(
        '--aws_secret_access_key',
        default=DEFAULT_AWS_SECRET_ACCESS_KEY,
        help='AWS Secret Access Key'
    )
    parser.add_argument(
        '--region_name',
        default=DEFAULT_REGION_NAME,
        help='AWS Region'
    )
    parser.add_argument(
        '--bucket_name',
        default=DEFAULT_BUCKET_NAME,
        help='S3 Bucket Name'
    )
    parser.add_argument(
        '--prefix',
        default=DEFAULT_PREFIX,
        help='S3 prefix'
    )
    parser.add_argument(
        '--output_html_local',
        default=DEFAULT_OUTPUT_HTML_LOCAL,
        help='Local Output HTML file name'
    )
    parser.add_argument(
        '--output_html_s3',
        default=DEFAULT_OUTPUT_HTML_S3,
        help='S3 Output HTML file name'
    )
    parser.add_argument(
        '--href_base_url',
        default=DEFAULT_HREF_BASE_URL,
        help='URL to prepend to links'
    )
    parser.add_argument(
        '--exclude',
        default=DEFAULT_REGEX_EXCLUDE,
        help='Regex exclude patterns'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        default=DEFAULT_OVERWRITE,
        help='Overwrite if file exist'
    )
    parser.add_argument(
        '--upload',
        action='store_true',
        default=DEFAULT_UPLOAD,
        help='Upload HTML file to bucket'
    )
    parser.add_argument(
        '--cli',
        action='store_true',
        default=DEFAULT_CLI,
        help='Use cli mode'
    )

    args = parser.parse_args()

    input_data = {
        "service_name": args.service_name,
        "endpoint_url": args.endpoint_url,
        "aws_access_key_id": args.aws_access_key_id,
        "aws_secret_access_key": args.aws_secret_access_key,
        "region_name": args.region_name,
        "bucket_name": args.bucket_name,
        "prefix": args.prefix,
        "output_html_local": args.output_html_local,
        "output_html_s3": args.output_html_s3,
        "href_base_url": args.href_base_url,
        "regex_exclude": args.exclude,
        "overwrite": args.overwrite,
        "upload": args.upload,
        "cli": True
    }

    print(generate_html(input_data))


def create_label_entry(root, text, row, default_value):
    """ Create a label and an entry field """

    ttk.Label(root, text=text).grid(row=row, column=0)
    entry = ttk.Entry(root, width=50)
    entry.grid(row=row, column=1)
    entry.insert(0, default_value)
    return entry


def gui_mode():
    """ GUI mode """

    def on_start():
        """ When user click on start button """

        # Collect all input values into a dictionary
        input_data = {
            "service_name": entries["service_name"].get(),
            "endpoint_url": entries["endpoint_url"].get(),
            "aws_access_key_id": entries["aws_access_key_id"].get(),
            "aws_secret_access_key": entries["aws_secret_access_key"].get(),
            "region_name": entries["region_name"].get(),
            "bucket_name": entries["bucket_name"].get(),
            "prefix": entries["prefix"].get(),
            "output_html_local": entries["output_html_local"].get(),
            "output_html_s3": entries["output_html_s3"].get(),
            "href_base_url": entries["href_base_url"].get(),
            "regex_exclude": entries["regex_exclude"].get(),
            "overwrite": checkbox_overwrite_var.get(),
            "upload": checkbox_upload_var.get(),
            "cli": False
        }

        messagebox.showinfo("Info", generate_html(input_data))

    def toggle_upload():
        """ Toggle entry output_html_s3 when user click on upload checkbox """

        if checkbox_upload_var.get():
            entries["output_html_s3"].config(state=tk.NORMAL)
        else:
            entries["output_html_s3"].config(state=tk.DISABLED)

    def select_output_file():
        """ Open the save file dialog """

        file_path = filedialog.asksaveasfilename(
            title="Output file",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )

        if file_path:
            # Clear the entry box and update it with the selected file path
            entries["output_html_local"].delete(0, tk.END)
            entries["output_html_local"].insert(0, file_path)

    # Main window
    root = tk.Tk()
    root.configure(padx=10, pady=10)
    root.title("SLD : S3")

    # Create a style object
    # style = ttk.Style()
    # style.theme_use('default')

    # Entries
    entry_fields = [
        (
            "service_name",
            "Service name :",
            0,
            DEFAULT_SERVICE_NAME
        ),
        (
            "endpoint_url",
            "Endpoint URL :",
            1,
            DEFAULT_ENDPOINT_URL
        ),
        (
            "aws_access_key_id",
            "Access key ID :",
            2,
            DEFAULT_AWS_ACCESS_KEY_ID
        ),
        (
            "aws_secret_access_key",
            "Secret access key :",
            3,
            DEFAULT_AWS_SECRET_ACCESS_KEY
        ),
        (
            "region_name",
            "Region (opt) :",
            4,
            DEFAULT_REGION_NAME
        ),
        (
            "bucket_name",
            "Bucket name :",
            5,
            DEFAULT_BUCKET_NAME
        ),
        (
            "prefix",
            "Prefix (opt) :",
            6,
            DEFAULT_PREFIX
        ),
        (
            "output_html_local",
            "Local Output HTML file :",
            7,
            DEFAULT_OUTPUT_HTML_LOCAL
        ),
        (
            "output_html_s3",
            "S3 Output HTML file :",
            9,
            DEFAULT_OUTPUT_HTML_S3
        ),
        (
            "href_base_url",
            "Href base URL (opt) :",
            10,
            DEFAULT_HREF_BASE_URL
        ),
        (
            "regex_exclude",
            "Regex exclude patterns (opt) :\nExample: .tmp, .old, backup_.*",
            11,
            DEFAULT_REGEX_EXCLUDE
        )
    ]

    entries = {}

    for entry_name, label_text, position, default_value in entry_fields:
        entry = create_label_entry(root, label_text, position, default_value)
        entries[entry_name] = entry

    # Browse button
    ttk.Button(
        root,
        text="browse...",
        command=select_output_file
    ).grid(row=8, column=1, sticky="w")

    # Overwrite checkbox
    checkbox_overwrite_var = tk.BooleanVar(value=DEFAULT_OVERWRITE)
    ttk.Checkbutton(
        root,
        text="Overwrite",
        variable=checkbox_overwrite_var
    ).grid(row=8, column=1)

    # Upload checkbox
    checkbox_upload_var = tk.BooleanVar(value=DEFAULT_UPLOAD)
    ttk.Checkbutton(
        root,
        text="Upload to S3",
        variable=checkbox_upload_var,
        command=toggle_upload
    ).grid(row=8, column=1, sticky="e")

    toggle_upload()

    # Start button
    ttk.Button(
        root,
        text=" Start ! ",
        command=on_start
    ).grid(row=12, column=1, sticky="e")

    # Start the GUI event loop
    root.mainloop()


def boto3_availability(cli):
    """ Show error message and quit if boto3 is missing """

    message = (
        "boto3 is not installed."
        "\nHint ? You can install it with : pip install boto3"
    )

    if not BOTO3_AVAILABLE:
        if cli:
            print(message)
        else:
            messagebox.showerror("Error", message)
        sys.exit(1)


def main():
    """ Main entry point """

    if DEFAULT_CLI or len(sys.argv) > 1 or '--cli' in sys.argv:
        boto3_availability(True)
        cli_mode()
    else:
        if TKINTER_AVAILABLE:
            boto3_availability(False)
            gui_mode()
        else:
            print(
                "GUI mode is not available, because tkinter is missing."
                "\nHint ? Use CLI options: ye3sld --help"
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
