from __future__ import annotations

import base64
import json
import os
import platform
import shutil
import subprocess
import typing
import urllib.request
from array import array

from ..enums import StiHtmlMode
from .StiHandler import StiHandler

if typing.TYPE_CHECKING:
    from .StiComponent import StiComponent


class StiNodeJs:

### Fields

    __component: StiComponent = None
    __error: str = None
    __errorStack: list = None
    __handler: StiHandler = None

    @property
    def handler(self) -> StiHandler:
        if self.__component == None and self.__handler == None:
            self.__handler = StiHandler()

        return self.__component.handler if self.__component else self.__handler


### Options

    version = '20.12.2'
    architecture = 'x64'
    system = ''
    binDirectory = ''
    workingDirectory = ''


### Properties

    @property
    def error(self) -> str:
        """Main text of the last error."""

        return self.__error
    
    @property
    def errorStack(self) -> array:
        """Full text of the last error as an array of strings."""

        return self.__errorStack


### Parameters

    def __getSystem(self) -> str:
        systemName = platform.system()
        if systemName == 'Windows': return 'win'
        if systemName == 'Darwin': return 'darwin'
        return 'linux'
            
    def __getArchiveName(self) -> str:
        extension = '.zip' if self.system == 'win' else '.tar.gz'
        return self.__getDirectoryName() + extension
    
    def __getDirectoryName(self) -> str:
        return f'node-v{self.version}-{self.system}-{self.architecture}'
    
    def __getDirectory(self) -> str:
        return os.path.join(os.getcwd(), self.__getDirectoryName())
    
    def __getUrl(self) -> str:
        return f'https://nodejs.org/dist/v{self.version}/' + self.__getArchiveName()
    
    def __getVersion(self) -> str:
        return self.handler.version


### Helpers

    def __isDashboardsProduct(self) -> bool:
        try:
            from stimulsoft_dashboards.report.StiDashboard import StiDashboard
        except Exception as e:
            return False
        return True
    
    def __clearError(self):
        self.__error = None
        self.__errorStack = None

    def __getNodeError(self, returnError: str, returnCode: int) -> str:
        lines = (returnError or '').split('\n')
        npmError = False
        errors = ['npm ERR', 'Error', 'SyntaxError', 'ReferenceError', 'TypeError', 'RequestError']
        for line in lines:
            if len(line or '') > 0:
                for error in errors:
                    if line.startswith(error):
                        if line.startswith('npm') and not npmError:
                            npmError = True
                            continue
                        return line
        
        if returnCode != 0:
            for line in lines:
                if len(line or '') > 0:
                    return line
                
            return f'ExecErrorCode: {returnCode}'
        
        return None
    
    def __getNodeErrorStack(self, returnError: str) -> list:
        return None if len(returnError or '') == 0 else returnError.split('\n')
    
    def __getNodePath(self) -> str:
        if len(self.binDirectory or '') == 0:
            return None
        
        nodePath = os.path.join(self.binDirectory, 'node.exe') if self.system == 'win' else os.path.join(self.binDirectory, 'bin', 'node')
        return nodePath if os.path.isfile(nodePath) else None
    
    def __getNpmPath(self) -> str:
        nodePath = self.__getNodePath()
        if len(nodePath or '') == 0:
            return None
        
        npmPath = nodePath[:-8] + 'npm.cmd' if self.system == 'win' else nodePath[:-4] + 'npm'
        return npmPath if os.path.isfile(npmPath) else None
    
    def __download(self) -> bool:
        url = self.__getUrl()
        archivePath = os.path.join(self.binDirectory, self.__getArchiveName())

        try:
            if not os.path.isdir(self.binDirectory):
                os.mkdir(self.binDirectory)

            urllib.request.urlretrieve(url, archivePath)
        except Exception as e:
            self.__error = str(e)
            return False
        
        return True
    
    def __unpack(self) -> bool:
        archivePath = os.path.join(self.binDirectory, self.__getArchiveName())
        try:
            shutil.unpack_archive(archivePath, self.binDirectory)
        except Exception as e:
            self.__error = str(e)
            return False

        sourcesPath = os.path.join(self.binDirectory, self.__getDirectoryName())
        for sourceFile in os.listdir(sourcesPath):
            shutil.move(os.path.join(sourcesPath, sourceFile), self.binDirectory)
        
        os.rmdir(sourcesPath)
        os.remove(archivePath)
        
        return True
    
    def __getHandlerScript(self) -> str:
        script = self.handler.getHtml(StiHtmlMode.SCRIPTS)
        return script.replace('Stimulsoft.handler.send', 'Stimulsoft.handler.https')


### Methods

    def installNodeJS(self) -> bool:
        """
        Installs the version of Node.js specified in the parameters into the working directory from the official website.
        
        return:
            Boolean execution result.
        """

        self.__clearError()
        if self.__getNodePath() == None:
            if not self.__download(): return False
            if not self.__unpack(): return False
        return True

    def updatePackages(self) -> bool:
        """
        Updates product packages to the current version.
        
        return:
            Boolean execution result.
        """

        self.__clearError()
        npmPath = self.__getNpmPath()
        product = 'dashboards' if self.__isDashboardsProduct() else 'reports'
        version = self.__getVersion()
        result = subprocess.run(f'"{npmPath}" install stimulsoft-{product}-js@{version}', cwd=self.workingDirectory, capture_output=True, text=True)
        self.__error = self.__getNodeError(result.stderr, result.returncode) if len(result.stderr or '') > 0 else self.__getNodeError(result.stdout, result.returncode)
        self.__errorStack = self.__getNodeErrorStack(result.stderr) if len(result.stderr or '') > 0 else self.__getNodeErrorStack(result.stdout)
        return len(self.error or '') == 0

    def run(self, script) -> bytes|str|bool:
        """
        Executes server-side script using Node.js
        
        script:
            JavaScript prepared for execution in Node.js

        return:
            Depending on the script, it returns a byte stream or string data or a bool result.
        """

        self.__clearError()
        nodePath = self.__getNodePath()
        if nodePath == None:
            self.__error = 'The path to the Node.js not found.'
            return False

        product = 'dashboards' if self.__isDashboardsProduct() else 'reports'
        require = f"var Stimulsoft = require('stimulsoft-{product}-js');\n"
        handler = self.__getHandlerScript()
        buffer = str(require+handler+script).encode()
        result = subprocess.run(f'"{nodePath} "', cwd=self.workingDirectory, input=buffer, capture_output=True, shell=False)
        stdout = '' if result.stdout == None else result.stdout.decode()
        stderr = '' if result.stderr == None else result.stderr.decode()
        self.__error = self.__getNodeError(stderr, result.returncode) if len(stderr) > 0 else self.__getNodeError(stdout, result.returncode)
        self.__errorStack = self.__getNodeErrorStack(stderr) if len(stderr) > 0 else self.__getNodeErrorStack(stdout)
        if len(self.error or '') > 0:
            return False

        if len(stdout) > 0:
            try:
                jsonData = json.loads(stdout)
                if jsonData['type'] == 'string': return jsonData['data']
                if jsonData['type'] == 'bytes': return base64.b64decode(jsonData['data'])
            except Exception as e:
                self.__error = 'ParseError: ' + str(e)
                return False
        
        return True


### Constructor

    def __init__(self, component: StiComponent = None):
        self.__component = component
        self.system = self.__getSystem()
        self.binDirectory = self.__getDirectory()
        self.workingDirectory = os.getcwd()