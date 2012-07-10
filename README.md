# Description

Commenter is a [Sublime Text 2](http://www.sublimetext.com/) package that allows you to create bookmarks with comments, which is useful when auditing source code.

It handles bookmarks per working directory. - It is NOT meant to be used with single files -

## The workflow goes like

* You open a folder in ST2, which contains the source code you are about to audit
* Open files within that folder and press (Cmd + Ctrl + m) to create bookmarks

A separete bookmark database will be created for each "Folder" you have open via "File"->"Open...", when you create your first bookmark, in the directory specified in Commenter.sublime-settings

# Install

## Manual Install

Go to your Packages subdirectory under ST2's data directory:

* Windows: %APPDATA%\Sublime Text 2
* OS X: ~/Library/Application Support/Sublime Text 2
* Linux: ~/.config/sublime-text-2
* Portable Installation: Sublime Text 2/Data

And clone the repo:

git clone git://github.com/shadown/Commenter.git

## Configuration

Open Commenter.sublime-settings and customize the setting as you want.

```
{
    "debug"             : false,
    "bookmarks_folder"  : "/Users/shadown/.subl_commenter",
    "bookmarks_prefix"  : "",
    "bookmarks_postfix" : "_comments",
    "bookmarks_ext"     : "db"
}
```

Be sure to set "bookmarks_folder" to the directory you want to store the bookmark-database files.

### The settings are self-explanatories, but anyway here it goes:

```
"debug": set it to "true" if you want to see some debug messages in the console embedded in ST2.
"bookmarks_folder": complete path to the folder where you want to create the bookmarks-database files.
"bookmarks_prefix": prefix you want to add to the bookmark-database filename.
"bookmarks_postfix": postfix you want to add to the bookmark-database filename.
"bookmarks_ext": extension you want your database to use.
```

# Shortcuts

## Create a bookmark 
	(Cmd + Ctrl + m) and enter your comment.
## Access a bookmark 
	(Cmd + Ctrl + b) select the bookmart you want to jump to.
## Modify a bookmark's comment
	(Cmd + Ctrl + m) in the line of the bookmark and modify it.
## Remore a bookmark
	(Cmd + Ctrl + m) empty the bookmark's comment, press (enter), and the bookmark will be removed as well.

That's all!
