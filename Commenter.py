#
# author: Sergio 'shadown' Alvarez
#

import sublime, sublime_plugin

import os					# path and file location

st_version = 2
if sublime.version() == '' or int(sublime.version()) > 3000:
	st_version = 3

if st_version == 2:
	import cPickle as pickle	# metadata storage
else:
	import pickle	# metadata storage

############## 
"""SETTINGS"""
##############
settings = sublime.load_settings('Commenter.sublime-settings').get # (key, None)

if settings('debug'):
	print ("Sublime Text: %lu" % st_version)
	print ("debug:"				, settings("debug"))
	print ("bookmarks_folder:"	, settings("bookmarks_folder"))
	print ("bookmarks_prefix:"	, settings("bookmarks_prefix"))
	print ("bookmarks_postfix:"	, settings("bookmarks_postfix"))
	print ("bookmarks_ext:"		, settings("bookmarks_ext"))
	print ("os_sep", os.sep)

def getDatabaseForRootFolder(rootFolder):
	_folder  = settings("bookmarks_folder")
	_prefix  = settings("bookmarks_prefix")
	_postfix = settings("bookmarks_postfix")
	_ext     = settings("bookmarks_ext")
	_sep     = os.sep

	# if the destination dir doesn't exist create it.
	if not os.path.isdir(_folder):
		os.mkdir(_folder)

	if settings('debug'):
		print ("[+] Using: " + _folder + _sep + _prefix + os.path.basename(rootFolder) + _postfix + '.' + _ext)

	return _folder + _sep + _prefix + os.path.basename(rootFolder) + _postfix + '.' + _ext


# directory where all bookmarks will be stored.
bookmarks_folder = None

##################
"""Add Comments"""
##################
class CommenterAddCommentCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# create self._bookmark
		self._craftBookmark()

		# we don't want to create a database for a single file.
		if not self._bookmark['rootFolder']:
			print ("[!] This plug-in is for SourceCode Trees, not for individual files!")
			return

		_prev_comment = self._getPreviousComment()

		window        = self.view.window()
		window.show_input_panel("Enter Bookmark Comment:", _prev_comment, self._addComment, None, None)

	def _addComment(self, comment):
		# if the comment is empty remove the bookmark is it exists
		if not comment:
			self._delComment()
			return

		# load pre-existing db if any
		if os.path.isfile(self._dbFile):
			# load previous comments
			comments = pickle.load(open(self._dbFile, "rb"))
		else:
			comments = dict()

		filePath = self._bookmark['filePath']
		fileName = self._bookmark['fileName']
		fileLine = self._bookmark['fileLine']
		
		if not filePath in comments:
			comments[filePath] = dict()

		if not fileName in comments[filePath]:
			comments[filePath][fileName] = dict()

		# if there is a pre-existing comment at that line, we overwrite it
		comments[filePath][fileName][fileLine] = comment

		# save to our comments db
		pickle.dump(comments, open(self._dbFile, "wb" ))

	def _delComment(self):
		# load pre-existing db if any
		if os.path.isfile(self._dbFile):
			# load previous comments
			comments = pickle.load(open(self._dbFile, "rb"))
		else:
			# nothing to delete
			return

		filePath = self._bookmark['filePath']
		fileName = self._bookmark['fileName']
		fileLine = self._bookmark['fileLine']
		
		if not filePath in comments:
			# filePath key doesn't exist, no key to delete
			return

		if not fileName in comments[filePath]:
			# fileName key doesn't exist, no key to delete
			return

		if not fileLine in comments[filePath][fileName]:
			# fileLine key doesn't exist, no key to delete
			return
		else:
			comments[filePath][fileName].pop(fileLine)

		if not len(comments[filePath][fileName].keys()):
			# there are no more keys in that fileName, remove it
			comments[filePath].pop(fileName)

		if not len(comments[filePath].keys()):
			# there are no more keys in that filePath, remove it
			comments.pop(filePath)

		# save to our comments db
		pickle.dump(comments, open(self._dbFile, "wb" ))

	def _craftBookmark(self):
		self._bookmark = dict()

		# file location
		_filePath, _fileName = os.path.split(self.view.file_name())

		# cursor location -> line, column, we only care about the line number
		_sel   = self.view.sel()
		_point = _sel[0].begin()
		_line  =  self.view.rowcol(_point)[0]
		_line  += 1 # rowcol() starts at 0, but 'goto_line' starts at 1

		# get active folders
		_folders = self.view.window().folders()

		# find which folder (aka: project) we are working on.
		_actualFolder = None
		for f in _folders:
			if f in _filePath:
				_actualFolder = f
				break

		# build bookmark
		self._bookmark['rootFolder'] = _actualFolder
		self._bookmark['filePath']   = _filePath
		self._bookmark['fileName']   = _fileName
		self._bookmark['fileLine']   = _line

	def _getPreviousComment(self):
		# create path to DB
		self._dbFile = getDatabaseForRootFolder(self._bookmark['rootFolder'])

		if os.path.isfile(self._dbFile):
			# load previous comments
			comments = pickle.load(open(self._dbFile, "rb"))

			filePath = self._bookmark['filePath']
			fileName = self._bookmark['fileName']
			fileLine = self._bookmark['fileLine']
			
			if filePath in comments:
				if fileName in comments[filePath]:
					if fileLine in comments[filePath][fileName]:
						return comments[filePath][fileName][fileLine]

		return ''

class CommenterBrowseCommentsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# file location
		_filePath, _fileName = os.path.split(self.view.file_name())

		# get active folders
		_folders = self.view.window().folders()

		# find which folder (aka: project) we are working on.
		_actualFolder = None
		for f in _folders:
			if f in _filePath:
				_actualFolder = f
				break

		# if not working on a folder return, since it's a single file
		if not _actualFolder: return

		# get path to DB
		self._dbFile = getDatabaseForRootFolder(_actualFolder)

		if os.path.isfile(self._dbFile):
			# load previous comments
			comments = pickle.load(open(self._dbFile, "rb"))
		else:
			return

		if settings('debug'):
			print ("[+] Actual Comments:", comments)

		if not len(comments): return

		self._comments_list = list()
		self._comments_line = list()
		for path in comments.keys():
			for fname in comments[path].keys():
				for line in comments[path][fname].keys():
					cmnt = comments[path][fname][line]
					self._comments_list.append("%s, line: %lu\t %s" % (fname, line, cmnt))

					filePath = path+os.sep+fname
					self._comments_line.append((line, filePath))

		window = self.view.window()

		window.show_quick_panel(self._comments_list, self._gotoBookmark)

	def _gotoBookmark(self, index):
		# if no bookmark was selected, return
		if index == -1:
			return

		window = self.view.window()

		view = window.open_file(os.path.normpath(self._comments_line[index][1]))

		view.run_command("goto_line", {"line": self._comments_line[index][0]})