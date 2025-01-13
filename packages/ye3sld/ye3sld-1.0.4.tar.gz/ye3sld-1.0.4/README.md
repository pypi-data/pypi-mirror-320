# ye3sld

Créer un fichier HTML qui affiche la structure de la liste des dossiers d'un bucket S3.  

Create an html file that show the directory listing structure of an s3 bucket.

# Features

- Works with all S3 compatible storage API implementations ([Amazon](https://aws.amazon.com/s3/), [Garage](https://garagehq.deuxfleurs.fr/), [MinIO](https://min.io/), etc.)
- GUI (Graphical User Interface) mode and CLI (Command Line Interface) mode
- Enter the Endpoint URL, Access key ID, Secret access key, Region, Bucket name
- Filter on a specific folder in S3 bucket (Prefix)
- Filter with regex to exclude certain patterns (eg: .tmp, .old, backup_.*)
- Can list all files, even if there are more than 1000 files in the bucket (S3 pagination)
- Select the output HTML file location: in local and S3 bucket (optional)
- Output HTML : Nice tree structure with a smooth effect when moving the mouse over the list items
- Output HTML : List items are clickable, with customizable href base url

The main goal is to display the entire folder structure on a single page. Really light and simple, without any action button or entry box on the output html page.

# Prerequisite

Python and boto3  
tkinter if you want a Graphical User Interface

# Simple usage

### 1) Install

Open the command prompt and type :

```bash
pip install ye3sld
```

### 2) Run

From the command prompt, 

For GUI mode, type :
```bash
ye3sld
```

Fill in the fields in the GUI
  
![Example Image](https://raw.githubusercontent.com/palw3ey/ye3sld/master/doc/demo-gui.png)

For CLI mode, type :  
```bash
ye3sld --cli --endpoint_url="http://MYWEBSITE" --aws_access_key_id="MYID" --aws_secret_access_key="MYSECRET" --bucket_name="MYBUCKET" --upload --overwrite --exclude=".tmp, .old"
```
To show all CLI options : `ye3sld --help`
  
### 3) Verify

Open the HTML output file in your local folder or in your s3 bucket

![Example Image](https://raw.githubusercontent.com/palw3ey/ye3sld/master/doc/demo-output.png)
  
To view the HTML code [Click here](https://raw.githubusercontent.com/palw3ey/ye3sld/master/doc/demo-output.html)

# Version

| name | version |
| :- |:- |
|ye3sld | 1.0.4 |

# Changelog

## [1.0.4] - 2025-01-12
### Added
- Show size and last modification when clicking on a line or on the page title
- Add generation date in the html meta
- ttk style

### Changed
- Refactoring code to conform to PEP 8, improve readability, maintainability, and consistency. Passed conformity checks with Flake8 and Pylint (rated at 10.00/10).
- Changed some exception handling 
- All DEFAULT can now be use for GUI and CLI

## [1.0.3] - 2025-01-07
### Added
- Hide the traceback, to avoid overwhelming the user with technical details

### Fixed
- args.cli replaced with True in cli_mode() function when calling generate_html() function

## [1.0.2] - 2025-01-06
### Changed
- Success and error message
- Help message in cli mode
- Missing tkinter message displayed in main()

### Added
- New function "check_s3_file_exists" to detect if s3 output file already exists
- New function "get_full_path" to get fullpath of the local output file
- Hint in cli mode

## [1.0.1] - 2025-01-02
### Fixed
- messagebox was not showing because tkinter was not imported in the generate_html function. Now, tkinter is imported at the top of the script, inside a try except.
  
## [1.0.0] - 2024-12-30
### Added
- première : first release

# ToDo

Feel free to contribute or share your ideas for new features, you can contact me here on github or by email. I speak French, you can write to me in other languages ​​I will find ways to translate.

# License

MIT  
author: palw3ey  
maintainer: palw3ey  
email: palw3ey@gmail.com  
website: https://github.com/palw3ey/ye3sld
