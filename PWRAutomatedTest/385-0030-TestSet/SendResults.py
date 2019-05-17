# -*- coding: utf-8 -*-
"""
Created on Fri May 17 11:42:38 2019

@author: Erik

https://stackoverflow.com/questions/38362714/pysftp-paramiko-sshexception-bad-host-key-from-server


"""

import pysftp
sftp = pysftp.Connection('erikiverson.exavault.com',
                         username='erikiverson',
                         private_key='C:\\Users\\Erik\\.ssh\\ExaVault_key',
                         password='9]qR4SeMswF{',)
sftp.put('A.PNG', preserve_mtime=True)
sftp.close()