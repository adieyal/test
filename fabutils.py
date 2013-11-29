from fabric.operations import local, run, sudo
from fabric.context_managers import settings

def new_user(username):   
    
    with settings(warn_only=True):
        sudo("useradd --no-create-home {username}".format(username=username))

def remote_mkdir(path):
    sudo("mkdir -p {path}".format(**locals()))

def remote_copy_file(from_file, dest_file):
    sudo("cp {from_file} {dest_file}".format(**locals()))

def remote_soft_link(from_file, dest_file):
    sudo("ln -fs {from_file} {dest_file}".format(**locals()))

def ask_number(query):
    while True:
        try:
            result = raw_input(query)
            return int(result)
        except ValueError:
            print ""
            print "Expected an integer. Please try again."
            print ""

def ask_not_empty(query):
    while True:
        result = raw_input(query)
        if result.strip() == "":
            print ""
            print "Expected a non-empty value. Please try again."
            print ""
            continue
        return result
            


