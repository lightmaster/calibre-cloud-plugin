#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2017, Kerim Ölçer <kerimlcr@gmail.com>, Ali Güven Odabaşıoğlu <agaodabasioglu@gmail.com>'
__docformat__ = 'restructuredtext en'
__version__   = "0.0.3"

if False:
    get_icons = get_resources = None

#Another import
import os, re, sys, getpass
from PyQt5.Qt import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel, QLineEdit
from PyQt5.QtWidgets import QWidget, QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import webdav.client as wc

#Calibre config files import
from calibre_plugins.cloud_sync.config import prefs
from calibre.utils.config import config_dir
#Gui import
from calibre_plugins.cloud_sync.gui.MainWindow import Ui_Form as MainWindow
from calibre_plugins.cloud_sync.gui.yandex import Ui_Dialog as YandexMainWindow
from calibre_plugins.cloud_sync.gui.dropbox import Ui_Dialog as DropboxMainWindow
from calibre_plugins.cloud_sync.gui.google import Ui_Dialog as GoogleMainWindow
from calibre_plugins.cloud_sync.gui.error import Ui_Dialog as ErrorMainWindow
from calibre_plugins.cloud_sync.gui.about import Ui_Dialog as AboutMainWindow

try:
    load_translations()
except NameError:
    pass # load_translations() added in calibre 1.9

class DemoDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config
        self.db = gui.current_db


class YandexMainWindowForm(QDialog,YandexMainWindow):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window)
        if (prefs['yy'] == '1'):
            self.getUsername.hide()
            self.getPassword.hide()
            self.label_2.hide()
            self.logout_button.clicked.connect(self.logout)
            self.label.setText("Now Session : " + prefs['username'])
        if (prefs['yy'] == '0'):
            self.logout_button.hide()
            self.getUsername.show()
            self.getPassword.show()
            self.label_2.show()
            self.getUsername.setText(prefs['username'])
            self.getPassword.setEchoMode(QLineEdit.Password)
            self.getPassword.setText(prefs['password'])
        self.downloadButton.clicked.connect(self.download)
        self.uploadButton.clicked.connect(self.upload)
        self.pushButton.clicked.connect(self.push)
        self.pullButton.clicked.connect(self.pull)

    def logout(self):
        prefs['username'] = 'username'
        prefs['password'] = 'password'
        prefs['yy'] = '0'
        QMessageBox.information(self, "Info", _("Logout successful"))
        return  1

    def save(self):
        prefs['password'] = self.getPassword.text()
        prefs['username'] = self.getUsername.text()
        prefs['yy'] = '1'
        return 1

    def yandexDisk(self, choice):

        yandexUrl = 'https://webdav.yandex.com.tr'
        options = {
         'webdav_hostname': yandexUrl,
         'webdav_login'   : prefs['username'],
         'webdav_password': prefs['password']
        }
        client = wc.Client(options)

        if (client.check() == False):
            QMessageBox.information(self, "Info", _("Login information is incorrect!"))
            return 1

        if(choice == "download"):
            if (client.check('Calibre') == False):
                client.mkdir('Calibre')
                QMessageBox.information(self, "Info", _("It was created because there is no Calibre file in Drive, download could not be done."))
            else:
                client.download_sync(remote_path="Calibre", local_path=prefs['librarypath'])
                QMessageBox.information(self, "Info", _("Download complete."))
        elif(choice == "upload"):
            if (client.check('Calibre') == False):
                client.mkdir('Calibre')
            client.upload_sync(remote_path="Calibre", local_path=prefs['librarypath'])
            QMessageBox.information(self, "Info", _("Upload complete."))
        elif(choice == "pull"):
            if (client.check('Calibre') == False):
                client.mkdir('Calibre')
                QMessageBox.information(self, "Info", _("It was created because there is no Calibre file in Drive, pull could not be done."))
            else:
                client.pull(remote_directory="Calibre", local_directory=prefs['librarypath'])
                QMessageBox.information(self, "Info", _("Pull complete."))
        elif(choice == "push"):
            if (client.check('Calibre') == False):
                client.mkdir('Calibre')
            client.push(remote_directory="Calibre", local_directory=prefs['librarypath'])
            QMessageBox.information(self, "Info", _("Push complete."))
        else:
            return 1

    def download(self):
        self.save()
        self.yandexDisk("download")
        return 1

    def upload(self):
        self.save()
        self.yandexDisk("upload")
        return 1

    def pull(self):
        self.save()
        self.yandexDisk("pull")
        return 1
        
    def push(self):
        self.save()
        self.yandexDisk("push")
        return 1
    
class DropboxMainWindowForm(QDialog, DropboxMainWindow):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window)

        if (prefs['dd'] == '1'):
            self.getUsername.hide()
            self.getPassword.hide()
            self.label_2.hide()
            self.logout_button.clicked.connect(self.logout)

        if (prefs['dd'] == '0'):
            self.logout_button.hide()
            self.getUsername.show()
            self.getPassword.show()
            self.label_2.show()
            self.getUsername.setText(prefs['d_username'])
            self.getPassword.setEchoMode(QLineEdit.Password)
            self.getPassword.setText(prefs['d_password'])

        self.downloadButton.clicked.connect(self.download)
        self.uploadButton.clicked.connect(self.upload)
        self.pushButton.clicked.connect(self.push)
        self.pullButton.clicked.connect(self.pull)

    def logout(self):
        prefs['d_username'] = 'username'
        prefs['d_password'] = 'password'
        prefs['dd'] = '0'
        QMessageBox.information(self, "Info", _("Logout successful"))
        return 1

    def save(self):
        prefs['d_password'] = self.getPassword.text()
        prefs['d_username'] = self.getUsername.text()
        prefs['dd'] = '1'
        return 1

    def dropbox(self, choice):
        options = {
            'webdav_hostname': 'https://dav.dropdav.com',
            'webdav_login'   : prefs['d_username'],
            'webdav_password': prefs['d_password']
        }
        client = wc.Client(options)

        if (client.check() == False):
            QMessageBox.information(self, "Info", _("Login information is incorrect!"))
            return 1

        if (choice == "download"):
            if (client.check('Calibre') == False):
                client.mkdir('Calibre')
                QMessageBox.information(self, "Info", _(
                        "It was created because there is no Calibre file in Drive, download could not be done."))
            else:
                client.download_sync(remote_path="Calibre", local_path=prefs['librarypath'])
                QMessageBox.information(self, "Info", _("Download complete."))
        elif (choice == "upload"):
            if (client.check('Calibre') == False):
                client.mkdir('Calibre')
            client.upload_sync(remote_path="Calibre", local_path=prefs['librarypath'])
            QMessageBox.information(self, "Info", _("Upload complete."))
        elif (choice == "pull"):
            if (client.check('Calibre') == False):
                client.mkdir('Calibre')
                QMessageBox.information(self, "Info", _(
                        "It was created because there is no Calibre file in Drive, pull could not be done."))
            else:
                client.pull(remote_directory="Calibre", local_directory=prefs['librarypath'])
                QMessageBox.information(self, "Info", _("Pull complete."))
        elif (choice == "push"):
            if (client.check('Calibre') == False):
                client.mkdir('Calibre')
            client.push(remote_directory="Calibre", local_directory=prefs['librarypath'])
            QMessageBox.information(self, "Info", _("Push complete."))
        else:
            return 1

    def download(self):
        self.save()
        self.dropbox("download")
        return 1

    def upload(self):
        self.save()
        self.dropbox("upload")
        return 1

    def pull(self):
        self.save()
        self.dropbox("pull")
        return 1

    def push(self):
         self.save()
         self.dropbox("push")
         return 1


class GoogleMainWindowForm(QDialog,GoogleMainWindow):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.googleDeauthButton.clicked.connect(self.googleDeAuth)
        self.uploadButton.clicked.connect(self.doGoogleUpload)
        self.downloadButton.clicked.connect(self.doGoogleDownload)
        username = getpass.getuser()
        if_exits = os.path.exists('/home/%s/.credentials/drive-calibre.json'%(username))
        if (if_exits == False):
            self.googleAuthButton.clicked.connect(self.googleAuth)
        else:
            self.googleAuthButton.hide()
            self.googleDeauthButton.setGeometry(30, 20, 99, 71)
            self.googleDeauthButton.resize(240,70)

    def credSettings(self):
        
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        credential_json = os.path.join(credential_dir,'client_secrets.json')
        credential_settings = os.path.join(credential_dir,'settings.yaml')
        if not os.path.exists(credential_json):
            file1=open(credential_json,'w')
            file1.write('{"installed":{"client_id":"697679503383-ud6kdb3gb2qhj1j4eop77a01qi3kc1en.apps.googleusercontent.com","project_id":"calibre-sync","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://accounts.google.com/o/oauth2/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"2Q9dbumIaW84NWddk9PmmrQN","redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}')
            file1.close()
        if not os.path.exists(credential_settings):
            file2=open(credential_settings,'w')
            file2.write("client_config_file: '%s/.credentials/client_secrets.json'"%(home_dir))
            file2.close()

    def googleAuth(self):
        self.credSettings()
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        credential_settings = os.path.join(credential_dir,'settings.yaml')
        gauth = GoogleAuth(credential_settings)
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,'drive-calibre.json')
        gauth.LoadCredentialsFile(credential_path)
        if gauth.credentials is None:
            gauth.LocalWebserverAuth()

        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile(credential_path)
        QMessageBox.information(self, "Info", _("Auth successful."))
        return GoogleDrive(gauth)

    def find_folders(self,fldname):
        drive = self.googleAuth()
        file_list = drive.ListFile({'q': "title='{}' and mimeType contains 'application/vnd.google-apps.folder' and trashed=false".format(fldname)}).GetList()
        return file_list

    def is_ExistLocal(self,path,title):
	    for locfname in os.listdir(path):
	    	if (locfname==title):
	    		return 1
	    	elif(os.path.isdir(path+locfname)):
                if(self.is_ExistLocal(path+locfname+"/",title)==1):
                    return 1
    
    def isExist(self,folderid,fname):
        drive = self.googleAuth()
        file_list = drive.ListFile({'q': "'"+str(folderid)+"'"+" in parents and trashed=false"}).GetList()
        for files in file_list:
            if(fname==files['title']):
                return 1
            elif (files['mimeType'] == 'application/vnd.google-apps.folder'):
                if(self.isExist(files['id'],fname) == 1):
				    return 1

    def uploadFolderToFolder(self,path,foldname,up='root'):
        drive = self.googleAuth()
	    foldcheck = self.find_folders(foldname)
	    if not foldcheck:
		    new_folder = drive.CreateFile({'title':'{}'.format(foldname),'mimeType':'application/vnd.google-apps.folder'})
		    if new_folder:
			    new_folder['parents'] = [{u'id': up}]
			    new_folder.Upload()
			    folderid=new_folder['id']
	    else:
		    folderid=foldcheck[0]['id']
		    file_list = drive.ListFile({'q': "'"+str(folderid)+"'"+" in parents and trashed=false"}).GetList()
	    if folderid:
		    for files in os.listdir(path):
		    	if(os.path.isdir(path+files) == True):
		    		newpath=path+files+"/"
		    		self.uploadFolderToFolder(newpath,files,folderid)
		    	if(self.isExist(folderid,files) != 1):
		    		f = drive.CreateFile({'title': files , "parents":[{"id": folderid}]})
		    		f.SetContentFile(path+files)
		    		f.Upload()
		    		print('title: %s, mimeType: %s' % (f['title'], f['mimeType']))
    
    def uploadDelete(self,localpath,foldname):
        drive = self.googleAuth()
	    foldcheck = self.find_folders(foldname)
	    folderid=foldcheck[0]['id']
	    file_list = drive.ListFile({'q': "'"+str(folderid)+"'"+" in parents and trashed=false"}).GetList()
	    for files in file_list:
		    if (files['mimeType'] == 'application/vnd.google-apps.folder'):
		    	self.uploadDelete(localpath,files['title'])
		    if (self.is_ExistLocal(localpath,files['title']) != 1):
		    	print(files['title'])
		    	files.Delete()

    def downloadFolderToFolder(self,localpath,foldname):
        drive = self.googleAuth()
	    foldcheck = self.find_folders(foldname)
	    if not foldcheck:
		    print("Error")
	    else:
		    folderid=foldcheck[0]['id']
		    file_list = drive.ListFile({'q': "'"+str(folderid)+"'"+" in parents and trashed=false"}).GetList()
	    if folderid is not None:
		    for files in file_list:
		    	if (files['mimeType'] == 'application/vnd.google-apps.folder'):
		    		pathway=localpath+files['title']+"/"
		    		if(self.is_ExistLocal(localpath,files['title']) != 1):
		    			os.makedirs(pathway)
		    		self.downloadFolderToFolder(pathway,files['title'])
		    	elif (self.is_ExistLocal(localpath,files['title']) != 1):
		    		fileid=files['id']
		    		file1 = drive.CreateFile({'id': fileid})
		    		file1.GetContentFile(localpath+files['title'])
    def downloadDelete(self,path):
        drive = self.googleAuth()
	    foldcheck = self.find_folders("Calibre")
	    folderid=foldcheck[0]['id']
	    for locfname in os.listdir(path):
		    if (os.path.isdir(path+locfname)):
		    	self.downloadDelete(path+locfname+"/")
		    if(self.isExist(folderid,locfname) != 1):
			    print(path+locfname)
			    os.remove(path+locfname)

    def downloadFolderToFolders(self,localpath):
        drive = self.googleAuth()
        folderid=self.find_folders('Calibre')[0]['id']
        file_list = drive.ListFile({'q': "'"+str(folderid)+"'"+" in parents and trashed=false"}).GetList()
        if folderid is not None:
            for files in file_list:
                if (self.is_ExistLocal(localpath,files['title']) != 1):
                    fileid=files['id']
                    file1 = drive.CreateFile({'id': fileid})
                    file1.GetContentFile(localpath+files['title'])

    def googleDeAuth(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        os.remove(credential_dir+'/drive-calibre.json')
        QMessageBox.information(self, "Info", _("Deauth successful."))
    
    def doGoogleUpload(self):
        path=prefs['librarypath']
        path=path+"/"
        self.uploadFolderToFolder(path,"Calibre")
        self.uploadDelete(path,"Calibre")
        QMessageBox.information(self, "Info", _("Upload complete."))

    def doGoogleDownload(self):
        try:    
            path=prefs['librarypath']
            path=path+"/"
            self.downloadFolderToFolder(path,"Calibre")
            self.downloadDelete(path)
            QMessageBox.information(self, "Info", _("Download complete."))
        except:
            QMessageBox.information(self, "Info", _("Calibre file does not exist on your Drive!"))


class AboutMainWindowForm(QDialog,AboutMainWindow):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.label_appname.setText("Cloud Sync")
        self.label_version.setText(__version__)
        self.label_expl.setText(_("Local or server files are synchronized with this plugin."))
        self.label_copy.setText('Copyright © 2017 – Kerim Ölçer\n'
    'Copyright © 2017 – Ali Güven Odabaşıoğlu')
        self.label_cs.setText("This program comes with absolutely no warranty.\n"
    "See the GNU General Public License, version 3 or "
    "later for details.")


#MainWindow
class MainWindowForm(QWidget, MainWindow):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.move(QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())
        self.label_version.setText(__version__)
        self.yandex_button.clicked.connect(self.yandex_dialog)
        self.google_button.clicked.connect(self.google_dialog)
        self.dropbox_button.clicked.connect(self.dropbox_dialog)
        self.question_button.clicked.connect(self.about)
        self.license_button.clicked.connect(self.openUrl)
        
    def openUrl(self):
        url = QtCore.QUrl('https://www.gnu.org/licenses/gpl-3.0.html')
        if not QtGui.QDesktopServices.openUrl(url):
            QtGui.QMessageBox.warning(self, 'Open Url', _('Could not open url.'))

    def about(self):
        self.aboutMainWindow = AboutMainWindowForm()
        self.hide()
        self.aboutMainWindow.exec_()
        self.show()

    def yandex_dialog(self):
        self.yandexMainWindow = YandexMainWindowForm()
        self.hide()
        self.yandexMainWindow.exec_()
        self.show()

    def google_dialog(self):
        self.googleMainWindow = GoogleMainWindowForm()
        self.hide()
        self.googleMainWindow.exec_()
        self.show()

    def dropbox_dialog(self):
        self.dropboxMainWindow = DropboxMainWindowForm()
        self.hide()
        self.dropboxMainWindow.exec_()
        self.show()
