### <a id="onepw"></a>The `onepw` Python module for 1Password integration

Documentation on how [to install and use the module](https://pypi.org/project/onepw/#install) is available at [PyPi](https://pypi.org/project/onepw/).

[1Password](https://1password.com) is a popular password manager used by individuals and organisations. It has a [desktop app](https://1password.com/downloads) for many platforms and a [support community](https://1password.community) where ideas are shared and questions are asked and answered.

For developers, it also provides [SDKs, tools and support](https://developer.1password.com). The `onepw` module uses [1Password CLI](https://developer.1password.com/docs/cli) command line tool to implement its features. For more advanced 1Password integration the [SDKs from 1Password](https://developer.1password.com/docs/sdks/) should be considered.

**Table of contents**

 - <a href="#install">To install and use the module</a>

     - <a href="#class-OnePW">Class `OnePW`</a>

     - <a href="#get">Method `OnePW.get`</a>

     - <a href="#list">Method `OnePW.list`</a>

     - <a href="#add">Method `OnePW.add`</a>

     - <a href="#delete">Method `OnePW.delete`</a>

 - <a href="#cli">To use the module as a console script</a>

     - <a href="#cli-onepw">Command `onepw`</a>

     - <a href="#cli-onepw-get">Command `onepw get`</a>

     - <a href="#cli-onepw-list">Command `onepw list`</a>

     - <a href="#cli-onepw-add">Command `onepw add`</a>

     - <a href="#cli-onepw-delete">Command `onepw delete`</a>

### <a id="install"></a>To install and use the module

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
when integrating *1Password* with Python:

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

#### Class <a id="class-OnePW"></a>`OnePW`

OnePW(account: str | None = None, pw: str | None = None)

*A Python class for 1Password sessions*

When an instance of this class is created, a *1Password* session
is started.  With this session you can perform *1Password CLI*
commands. The following methods for such commands are available:

 - `get`: get a field from a 1Password entry

 - `list`: list all entries from 1Password

 - `add`: add an entry to 1Password

 - `delete`: delete an entry from 1Password

In the following example, a *1Password* session is created and the
password from the `"Google"` entry in 1Password is fetched:

```python
op = OnePW()
pw = op.get("Google", field="password")
```

When a *1Password* session is instantiated you are signed in
to *1Password*. If the *1Password CLI* tool is integrated with
the *1Password* desktop app, the desktop app is used to sign
in to *1Password*. Otherwise, the password has to be provided,
either as the argument `pw` (usually not recommended) or
prompted for.

**Arguments:**

 - `account`: The account to sign in to (usually, not needed;
default `None`)

 - `pw`: The password used to sign in (usually, not needed;
default `None`)

#### Method <a id="get"></a>`OnePW.get`

```python
get(title: str, field: str = 'password', return_format: str | None = None) -> str | dict
```

*Get a field from a 1Password entry*

Get the value of a field from the 1Password entry with the
title `title`. The default field is `"password"`, but any
other fields like `"username"` or `"email"` are possible.
`"all"` will return a dictionary with all fields.  The method
raises a `OnePWError` exception if an entry with the given
title and/or field is not found.

The argument `return_format` can be used to change what is
returned. If it is not set, it will return the value of the
field as a text string. One exception is when `field` is
`"all"`. Then a dictionary containing all fields will be
returned (se below for an example).  If it is set, the
`return_format` argument can have two different values:
`"reference"` or `"raw-dict"`. If `return_format` is
`"reference"`, a reference to the field is returned (and not
the value of the field). `"raw-dict"` is applicable only when
the `field` argument *is* `"all"`. If the `field` argument is
`"all"` and the `return_format`argument is `"raw-dict"`, the
raw dictionary conatining all the details about the entry is
returned (and not only all the fields and some other details).

If `field` is `"all"`, and `format` *is not* `"raw-dict"`, the
returned dictionary will have a format like this (numbers of
items under `"fields"` and `"urls"` will vary):

```python
{
  "id": "auniqu4idfrom1p4ssw0rdapp1",
  "title": "An example",
  "vault": "Personal",
  "category": "LOGIN",
  "fields": {
    "username": "an@email.address",
    "password": "a s3cret p4ssw0rd"
  },
  "urls": {
    "website": "https://a.web.page/"
  }
}
```

**Arguments/return value:**

 - `title`: The title of the entry (can also be the id of the
entry)

 - `field`: The field to get from the entry, where `"all"` will
return all fields as a dictionary (default `"password"`)

 - `return_format`: Specifies an alternative format to return
the field/data in the entry (default `None`)

 - `return`: The value of the field in the entry

#### Method <a id="list"></a>`OnePW.list`

```python
list(categories: str | None = None, favorite: bool = False, tags: str | None = None, vault: str | None = None, return_format: str = 'title') -> list | dict
```

*List all entries in 1Password*

 List all the entries in 1Password with their titles, ids or as
 a dictionary representation.  By default, the method returns a
 list of all entry titles. If `return_format` is set to `"id"`,
 it returns a list of all entry ids. If `return_format` is set
 to `"dict"` or `"id-dict"`, it returns a dictionary of all
 entries and some data, where the key for each entry is the
 title (if `return_format` is `"dict"`) or the id (if
 `return_format` is `"id-dict"`) of the entry.  If
 `return_format` is set to `"raw-dict"` or `"id-raw-dict"`, it
 returns a dictionary of all entries and all the details about
 each entry, where the key for each entry is the title (if
 `return_format` is `"raw-dict"`) or the id (if `return_format`
 is `"id-raw-dict"`) of the entry.

 Arguments/return value:

 - `categories`: only list items in these comma-separated
 categories (default `None`, meaning all entries)

 -  `favorite`: only list favorite items (default `False`,
 meaning all entries)

 -  `tags`: only list items with these comma-separated tags
 (default `None`, meaning all entries)

 -  `vault`: only list items in this vault (default `None`,
 meaning all vaults)

 -  `return_format`: the return format of the returned list or
 dictionary (default `"title"`, meaning a list of entry titles)

 -  `return`: returns a list or a dictionary with all the
 entries

#### Method <a id="add"></a>`OnePW.add`

```python
add(title: str, username: str, password: str, email: str | None = None, url: str | None = None)
```

*Add a new entry to 1Password*

Add a new entry to 1Password with the provided values. A
title, username and password are required. The method raises a
`OnePWError` exception if adding the entry fails.

**Arguments:**

 - `title`: The title of the entry

 - `username`: The username added to the entry

 - `password`: The password added to the entry

 - `email`: The email address added to the entry (default `None`)

 - `url`: The URL added to the entry (default `None`)

#### Method <a id="delete"></a>`OnePW.delete`

```python
delete(title: str, no_archive: bool = False)
```

*Delete an entry from 1Password*

Delete an entry from 1Password with the given title. 

**Arguments:**

 - `title`: The title of the entry to delete

 - `no_archive`: Do not archive entry when deleted (default
`False`)

### <a id="cli"></a>To use the module as a console script

#### Command <a id="cli-onepw"></a>`onepw`

*Perform 1Password CLI commands*

**Usage:**

```bash
onepw [-h] [-V] [--doc [{get,list,add,delete}]] [--account ACCOUNT] [--pw PASSWORD] {get,list,add,delete} ...
```

**Positional arguments:**

Name | Description
---- | -----------
`{get,list,add,delete}` | the command to perform

**Options:**

Name | Description
---- | -----------
`-h, --help` | show this help message and exit
`-V, --version` | show program's version number and exit
`--doc [{get,list,add,delete}]` | print documentation of module or specific method
`--account ACCOUNT` | the 1Password account (usually, not necessary)
`--pw PASSWORD` | the 1Password secret password (be careful using this)

Use `onepw {get,list,add,delete} -h` to show help message for a specific
Command

#### Command <a id="cli-onepw-get"></a>`onepw get`

*Get the value of a field from an entry in 1Password*

**Usage:**

```bash
onepw get [-h] --title TITLE [--field FIELD] [--reference]
```

**Options:**

Name | Description
---- | -----------
`-h, --help` | show this help message and exit
`--title TITLE` | the title of the entry to get the value from
`--field FIELD` | the field of the entry to get the value from, or if `all`, return all fields in a JSON string (default `password`)
`--reference` | get reference to field, not value

#### Command <a id="cli-onepw-list"></a>`onepw list`

*List all entries in 1Password*

**Usage:**

```bash
onepw list [-h] [--categories CATEGORIES] [--favorite] [--tags TAGS] [--vault VAULT]
```

**Options:**

Name | Description
---- | -----------
`-h, --help` | show this help message and exit
`--categories CATEGORIES` | only list items in these categories (comma-separated)
`--favorite` | only list favorite items
`--tags TAGS` | only list items with these tags (comma-separated)
`--vault VAULT` | only list items in this vault

#### Command <a id="cli-onepw-add"></a>`onepw add`

*Add an entry to 1Password*

**Usage:**

```bash
onepw add [-h] --title TITLE --username USERNAME [--password PASSWORD] [--email EMAIL] [--url URL]
```

**Options:**

Name | Description
---- | -----------
`-h, --help` | show this help message and exit
`--title TITLE` | the title of the new entry
`--username USERNAME` | the user name in the new entry
`--password PASSWORD` | the password in the new entry (`onepw add` will ask for the password if it is not provided)
`--email EMAIL` | the email address in the new entry (optional)
`--url URL` | the URL in the new entry (optional)

#### Command <a id="cli-onepw-delete"></a>`onepw delete`

*Delete an entry from 1Password*

**Usage:**

```bash
onepw delete [-h] --title TITLE [--no-confirm] [--no-archive]
```

**Options:**

Name | Description
---- | -----------
`-h, --help` | show this help message and exit
`--title TITLE` | the title of the entry to delete
`--no-confirm` | do not confirm before deleting entry (default `False`)
`--no-archive` | do not archive deleted entry (default `False`)

