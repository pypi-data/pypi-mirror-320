#!/usr/bin/env python3

###############################################################################
#
# Copyright (c) 2022-2025, Anders Andersen, UiT The Arctic University
# of Norway. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# - Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###############################################################################


R"""The `onepw` Python module for 1Password integration

The `onepw` Python module implements a limited *1Password* integration
using *1Password CLI*:

 - https://developer.1password.com/docs/cli

To use the module, install the *1Password CLI* tool `op`:

 - https://1password.com/downloads/command-line/

(or install it with a package tool, e.g., *HomeBrew* on a Mac).

The `onepw` module is available from my software repository and from
PyPi:

 - https://www.pg12.org/software

 - https://pypi.org/project/onepw/

It is best to install the module and the companion console script
`onepw` with `pip`:

```bash
pip install onepw
```

It is recommended to integrated the *1Password CLI* tool with the
*1Password* desktop app (to use the desktop app to sign in to
*1Password*).  See Step 2 here for details:

 - https://developer.1password.com/docs/cli/get-started/

Other similar Python modules, with more or different functionality,
are available. The obvious first choice is the SDKs from *1Password*:

 - https://developer.1password.com/docs/sdks/

Their Python SDK is in active development and should be considered
when integratiing *1Password* with Python:

 - https://github.com/1Password/onepassword-sdk-python

Another option is to use the `keyring` module with the third-party
backend *OnePassword Keyring*:

 - https://pypi.org/project/keyring/

 - https://pypi.org/project/onepassword-keyring/

One downside of this approach is that when *OnePassword Keyring* is
installed, it replaces the default backend of the `keyring` module.  I
prefer that the default behavior of `keyring` is unchanged (using the
system keychain/keyring) and use a specific module (like `onepw`) for
*1Password* integration in Python.

"""


# Use subprocess to perform the command line operations
import subprocess


# The 1Password command line program `op` uses JSON
import json


# Use `shutil.which()` to verify that the 1Password CLI is installed
import shutil


# When adding entries to 1Password, store it in a temporary file first
import tempfile


# Current version of module
version = "1.17"


# On a Mac, the 1Password `op` tool is installed in "/usr/local/bin/"
# or "/opt/homebrew/bin/" (with HomeBrew)
op_path = ""	# We guess full path is not necessary (test: `shutil.which()`)
op_cmd = op_path + "op"


def _fetch_fields_op(field_list: list) -> dict:
    """Fetch all fields of given type

    Fetch all fields from the field list in a dictionary where either
    `"id"` or `"label"` is the key for each field and either `"value"`
    or `"href"` is the value of each field.

    `field_list` -- a list of information for each field

    `return` -- a dictionary with field key-value pairs

    """
    fields = {}
    for v in field_list:
        for k in ["id", "label"]:
            if k in v and v[k]:
                if not v[k] in fields:
                    if "value" in v:
                        fields[v[k]] = v["value"]
                    elif "href" in v:
                        fields[v[k]] = v["href"]
                break
    return fields


class OnePWError(Exception):
    """Any error in the 1Password session"""
    def __init__(self, errmsg: str):
        self.errmsg = errmsg


class OnePW:
    """A Python class for 1Password sessions

    When an instance of this class is created, a *1Password* session
    is started.  With this session you can perform *1Password CLI*
    commands. The following methods for such commands are available:

     - `get`: get a field from a 1Password entry

     - `add`: add an entry to 1Password
    
     - `delete`: delete an entry from 1Password
    
    In the following example, a *1Password* session is created and the
    password from the `"Google"` entry in 1Password is fetched:

    ```python
    op = OnePW()
    pw = op.get("Google", field="password")
    ```

    """


    def __init__(self, account: str | None = None, pw: str | None = None):
        """Instantiate a 1Password session

        When a *1Password* session is instantiated you are signed in
        to *1Password*. If the *1Password CLI* tool is integrated with
        the *1Password* desktop app, the desktop app is used to sign
        in to *1Password*. Otherwise, the password has to be provided,
        either as the argument `pw` (usually not recommended) or
        prompted for.

        Arguments:

        `account` -- The account to sign in to (usually, not needed;
        default `None`)

        `pw` -- The password used to sign in (usually, not needed;
        default `None`)

        """

        # Save for error messages
        self._last = "__init__"

        # Verify that the 1Password command `op` is installed
        if not shutil.which(op_cmd):
            errmsg = "\nInstall (and initialize) the 'op' command from " + \
                "1Password:\n" + \
                "  https://1password.com/downloads/command-line\n"
            raise OnePWError(errmsg)
        
        # Login (new session)
        if account:
            cmd =  [op_cmd, "signin", "--account", account, "--raw"]
        else:
            cmd =  [op_cmd, "signin", "--raw"]
        if pw:
            res = subprocess.run(
                cmd, input=pw, text=True, capture_output=True)
        else:
            res = subprocess.run(
                cmd, text=True, capture_output=True)
        if res.returncode != 0:
            errmsg = "1Password signin failed (error-code: " + \
                f"{res.returncode})\n  {res.stderr.strip()}"
            raise OnePWError(errmsg)

        # Save session token (empty if 1Password 8 CLI integration enabled)
        self.session_token = res.stdout.rstrip()


    def get(self,
            title: str,
            field: str = "password",
            return_format: str = "json") -> str | dict:
        """Get a field from a 1Password entry

        Get the value of a field from the 1Password entry with the
        title `title`. The default field is `"password"`, but any
        other fields like `"username"`, `"email"` or `"url"` are
        possible.  `"all"` will return a JSON string with all fields.
        The method raises a `OnePWError` exception if an entry with
        the given title and/or field is not found.

        The argument `return_format` is only relevant if the value of
        argument `field` is `"all"`.  It can have four different
        values: `"json"` (default), `"dict"`, `"raw-json"`,
        `"raw-dict"`. `"json"` returns a JSON string with all fields
        and their values, `"dict"` returns a dictionary with all
        fields and their values, `"raw-json"` returns the raw JSON
        string returned by the 1Password CLI command, and `"raw-dict"`
        returns a dictionary based on the raw JSON string.

        Arguments/return value:

        `title` -- The title of the entry

        `field` -- The field to get from the entry, where `"all"` will
        return all fields as a JSON string (default `"password"`)

        `return_format` -- If field is `"all"`, this argument
        specifies the format to return the fields/data in the entry
        (default `"json"`)

        `return` -- The value of the field in the entry

        """

        # Save for error messages
        self._last = "get"

        # Build command
        cmd = [op_cmd, "--session", self.session_token, "item",
               "get", title, "--reveal"]
        if field == "all":
            cmd += ["--format", "json"]
        else:
            cmd += ["--fields", field]
        
        # Get entry for item from 1Password
        res = subprocess.run(cmd, text=True, capture_output=True)
        if res.returncode != 0:
            errmsg = f"Fetching '{field}' for '{title}' from 1Password " + \
                f"failed:\n  {res.stderr.strip()}"
            raise OnePWError(errmsg)
        
        # Decode the entry

        # Fetch return string
        value = res.stdout.rstrip()

        # Return all fields?
        if field == "all":

            # Check format string
            if not return_format in ["json", "dict", "raw-json", "raw-dict"]:
                errmsg = f"Unknown return format: {return_format}"
                raise OnePWError(errmsg)

            # If "raw-json", no further decoding needed
            if return_format != "raw-json":

                # Convert to Python dictionary
                value = json.loads(value)

                # If "raw-json", no further decoding needed
                if return_format != "raw-dict":

                    # Create a new return value fetching the values we want
                    new = {}
                    new["title"] = value["title"]
                    new["vault"] = value["vault"]["name"]

                    # Try to find all real fields of interest
                    for k in ["fields", "urls"]:
                        if k in value:
                            new[k] = _fetch_fields_op(value[k])
                        else:
                            new[k] = {}

                    # The result (convert to JSON, if requested)
                    value = new
                    if return_format == "json":
                        value = json.dumps(value)

        # Return specific field?
        else:
            if not value:
                errmsg = f"No '{field}' in 1Password for '{title}'"
                raise OnePWError(errmsg)

        # Return the value
        return value


    def add(
            self, title: str, username: str, password: str,
            email: str | None = None, url: str | None = None):
        """Add a new entry to 1Password

        Add a new entry to 1Password with the provided values. A
        title, username and password are required. The method raises a
        `OnePWError` exception if adding the entry fails.

        Arguments:

        `title` -- The title of the entry

        `username` -- The username added to the entry

        `password` -- The password added to the entry

        `email` -- The email address added to the entry (default `None`)
        
        `url` -- The URL added to the entry (default `None`)

        """

        # Save for error messages
        self._last = "add"
        
        # Get template for new entry
        res = subprocess.run(
            [op_cmd, "--session", self.session_token,
             "item", "template", "get", "Login"],
            text=True, capture_output=True)
        if res.returncode != 0:
            errmsg = "Fetching template for 'Login' from 1Password " + \
                f"failed:\n  {res.stderr.strip()}"
            raise OnePWError(errmsg)

        # Fill in the form with username and password
        try:
            template = json.loads(res.stdout.rstrip())
            for field in template["fields"]:
                if field["id"] == "username":
                    field["value"] = username
                elif field["id"] == "password":
                    field["value"] = password
        except KeyError:
            errmsg = "Error in 1Password template?"
            raise OnePWError(errmsg)
        except:
            errmsg = "Unable to parse template output from 1Password"
            raise OnePWError(errmsg)

        # Add email if provided
        if email:
            template["fields"].append(
                {"id": "email", "label": "email", "purpose": "EMAIL",
                 "value": email, "type": "STRING"})

        # Add entry to 1Password via a temp json file
        with tempfile.NamedTemporaryFile(mode="w") as tmp:

            # Dump the json to a temp file
            json.dump(template, tmp)
            tmp.seek(0) # Go back to beginning of file

            # Create the `op` command
            cmd = [op_cmd, "--session", self.session_token,
                   "item", "create", "--template", tmp.name,
                   "--title", f"{title}"]
            if url:
                cmd.append("--url")        
                cmd.append(f"{url}")        

            # Actually add entry to 1Password
            res = subprocess.run(cmd, text=True, capture_output=True)

        # Did it go OK?
        if res.returncode != 0:
            errmsg = f"Adding entry in 1Password for '{title}' " + \
                f"failed:\n  {res.stderr.strip()}"
            raise OnePWError(errmsg)


    def delete(self, title: str, no_archive: bool = False):
        """Delete an entry from 1Password

        Delete an entry from 1Password with the given title. 

        Arguments:

        `title` -- The title of the entry to delete

        `no_archive` -- Do not archive entry when deleted (default
        `False`)

        """

        # Save for error messages
        self._last = "delete"

        # Build command
        cmd = [op_cmd, "--session", self.session_token,
               "item", "delete", title]
        if not no_archive:
            cmd.append("--archive")

        # Delete entry
        res = subprocess.run(cmd, text=True, capture_output=True)
        if res.returncode != 0:
            errmsg = f"Deleting entry '{title}' from 1Password failed:\n" + \
                f"  {res.stderr.strip()}"
            raise OnePWError(errmsg)


def d2na(kw: dict, sep: str = " ", pre: str = "--", asg: str = " ") -> str:
    """Convert dictionary to string representation of named arguments

    A simple help function converting a dictionary to a string
    representation of arguments.  It is possible to modify the
    separator `sep`, the pre-string before the name `pre`, and the
    asignment string `asg`.  The default values are matching command
    line arguments.

    Arguments/return value:

    `sep` -- Separator between each name/value pair (`sep`, default
    " ", but ", " is an alternative for named arguments to Python
    functions)

    `pre` -- A string added before the name of each argument (default
    "--", but '"' is an alternative for named arguments to Python
    functions)

    `asg` -- The string for assignment of the value to the named
    argument (default " ", but "=" is an alternative for named
    arguments to Python functions)

    `return` -- The string representation

    """
    na_str_list = []
    for k in kw:
        na_str_list.append(f"{pre}{k}{asg}{repr(kw[k])}")
    return sep.join(na_str_list)


def _print_sig(cmd: str, name: str | None = None):
    """Print the method signature

    Print the method signature of the method named `cmd` in the
    `OnePW` class.

    Arguments:

    `cmd` -- Name of the method to print the signature of

    """
    from inspect import signature
    method = getattr(OnePW, cmd)
    if not name: name = method.__name__
    sig = str(signature(method))
    if ", " in sig:
        sig = sig.replace("self, ", "", 1)
    else:
         sig = sig.replace("self", "", 1)
    print(f"{name}{sig}")


def _print_doc(method: str | list | None = None, prog: str = "onepw"):
    """Print the documentation of a single method or a list of methods

    Print the method documentation of the method named `method` in the
    `OnePW` class. If `method` is a list of method names, print the
    documention of the module, the `OnePW` class, and all the
    methods. If `method` is `None`, only print the documention of the
    module and the `OnePW` class.

    Arguments:

    `method` -- Name of a method, a list of method names, or `None` for
    no specific method

    """

    # Print documention for a single method
    if type(method) is str:
        m = getattr(OnePW, method)
        print(f"\n\033[1mMethod '{method}'\033[0m:\n")
        _print_sig(method)
        print("\n" + m.__doc__.strip() + "\n")

    # Print documention for the module
    else:

        # Print the module documention
        print(f"\n\033[1mModule 'onepw'\033[0m:\n")
        print(__doc__.strip() + "\n")

        # Print the class `OnePW` documention
        print(f"\033[1mClass 'OnePW'\033[0m:\n")
        _print_sig("__init__", "OnePW")
        print("\n" + OnePW.__doc__.strip() + "\n")
        init_doc_lines = OnePW.__init__.__doc__.strip().splitlines()[2:]
        print("\n".join(init_doc_lines) + "\n")

        # Print information about the list of methods
        if type(method) is list:
            print(f"\033[1mClass 'OnePW' methods\033[0m:\n")
            for m in method:
                print(f"\033[1m{m}\033[0m: {prog} --doc {m}\n")

    
def main():
    """Run module as a program

    Run the module as a program with these possible commands:

    - `get`: get the value of a field in an entry in 1Password (default
      field is password)

    - `add`: add an entry in 1Password

    - `delete`: delete an entry from 1Password

    """

    # Need `argv`, `stderr` and `exit`
    import sys

    # The commands implemented
    cmds = ["get", "add", "delete"]
    methods = cmds
    cmdchoices = "{" + ",".join(cmds) + "}"
    
    # A trick for a late binding of args.func (after the creation of
    # the 1Password session)
    method_dict = {}  # Will be populated with a method for each command
    get_func = lambda **kw: method_dict["get"](**kw)
    add_func = lambda **kw: method_dict["add"](**kw)
    delete_func = lambda **kw: method_dict["delete"](**kw)
    
    # Create overall argument parser
    import argparse
    parser = argparse.ArgumentParser(
        description="perform 1Password CLI commands",
        epilog=f"use '%(prog)s {cmdchoices} -h' " + \
          "to show help message for a specific command")
    parser.add_argument(
        "-V", "--version", action="version",
        version=f"%(prog)s " + version)
    parser.add_argument(
        "--doc", nargs='?', const=True, choices=methods,
        default=argparse.SUPPRESS, 
        help="print documentation of module or specific method")
    parser.add_argument(
        "-D", action="store_true", default=argparse.SUPPRESS, 
        help=argparse.SUPPRESS)
    parser.add_argument(
        "-L", action="store_true", default=argparse.SUPPRESS, 
        help=argparse.SUPPRESS)
    parser.add_argument(
        "-M", nargs='?', const=True, choices=methods + ["OnePW"],
        default=argparse.SUPPRESS,
        help=argparse.SUPPRESS)
    parser.add_argument(
        "--account", default=None,
        help="the 1Password account (usually, not necessary)")
    parser.add_argument(
        "--pw", metavar="PASSWORD", default=None,
        help="the 1Password secret password (be careful using this)")
    subparsers = parser.add_subparsers(
        help="the command to perform")

    # Create argument parser for the `get` command
    parser_get = subparsers.add_parser(
        "get",
        description="get the value of a field from an entry in 1Password")
    parser_get.add_argument(
        "--title", required=True,
        help="the title of the entry to get the value from")
    parser_get.add_argument(
        "--field", default="password",
        help="the field of the entry to get the value from " + \
          "(default 'password')")
    parser_get.set_defaults(func=get_func)

    # Create argument parser for the `add` command
    parser_add = subparsers.add_parser(
        "add", description='add an entry to 1Password')
    parser_add.add_argument(
        "--title", required=True,
        help="the title of the new entry")
    parser_add.add_argument(
        "--username", required=True,
        help="the user name in the new entry")
    parser_add.add_argument(
        "--password",
        help="the password in the new entry " + \
          "('%(prog)s' will ask for the password if it is not provided)")
    parser_add.add_argument(
        "--email", default=None,
        help="the email address in the new entry (optional)")
    parser_add.add_argument(
        "--url", default=None,
        help="the URL in the new entry (optional)")
    parser_add.set_defaults(func=add_func)

    # Create argument parser for the `delete` command
    parser_delete = subparsers.add_parser(
        "delete",
        description="delete an entry from 1Password")
    parser_delete.add_argument(
        "--title", required=True,
        help="the title of the entry to delete")
    parser_delete.add_argument(
        "--no-confirm", action="store_true",
        help="do not confirm before deleting entry (default `False`)")
    parser_delete.add_argument(
        "--no-archive", action="store_true",
        help="do not archive deleted entry (default `False`)")
    parser_delete.set_defaults(func=delete_func)
    
    # Parse arguments
    args = parser.parse_args()

    # Print documentation?
    if "doc" in args:
        if args.doc == True:
            _print_doc(cmds, sys.argv[0])
        else:
            _print_doc(args.doc)
        return

    # Print alternative (non-documented) documentation?
    if "D" in args:
        _print_doc()
        return

    # Print the available methods
    if "L" in args:
        print("\n".join(cmds))
        return
    
    # Print list of commands (non-documented)?
    if "M" in args:
        if args.M == True:
            print("\n".join(methods))
        elif args.M == "OnePW":
            _print_sig("__init__", args.M)
        else:
            _print_sig(args.M)
        return

    # If we have a password without a value in arguments, we ask for it
    if "password" in args:
        if not args.password:
            from getpass import getpass
            args.password = getpass()

    # Arguments are passed on to the methods; make them a dictionary
    kw = vars(args)

    # Confirm?
    if "no_confirm" in args:
        no_confirm = kw.pop("no_confirm")
        if not no_confirm:
            response = input(
                f"Are you sure you want to delete entry '{args.title}' " + \
                "from 1Password? (yes/no) ")
            if response != "yes":
                return

    # Starte the 1Password session
    account = kw.pop("account")
    pw = kw.pop("pw")
    try:
        op = OnePW(account = account, pw = pw)
    except OnePWError as e:
        print(
            f">>> {sys.argv[0]}: Unable to sign in to 1Password:\n" + \
            f"--> {e.errmsg}", file = sys.stderr)
        sys.exit(1)

    # Bind methods to the commands
    for m in cmds:
        method_dict[m] = getattr(op, m)

    # Fetch command
    try:
        func = kw.pop("func")
    except KeyError:
        parser.print_usage(file = sys.stderr)
        print(
            f"{sys.argv[0]}: error: no command given: {','.join(cmds)}",
            file = sys.stderr)
        sys.exit(1)
        
    # Perform command
    try:
        res = func(**kw)
    except OnePWError as e:
        print(
            f">>> {sys.argv[0]}: Unable to do '{op._last}' command:\n" + \
            f"  {op._last} {d2na(kw)}\n" + \
            f"--> {e.errmsg}", file = sys.stderr)
        sys.exit(1)

    # Print result, if any
    if res: print(res)


# Execute this module as a program
if __name__ == '__main__':
    main()
