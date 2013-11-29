import fnmatch
import os
import re
from fabric.operations import local, run, sudo, put
from fabric.context_managers import lcd
import fabutils

re_templates = re.compile(r"\{\{\s*([^}]+)\s*\}\}")

if os.path.exists("fabdefs.py"):
    from fabdefs import *

def _encode(s):
    return s.encode("utf8")

def _template_engine(context):
    def repl(match):
        s = match.groups()[0].strip()
        return _encode(context[s])
    return repl

def _find_sample_files():
    matches = []
    for root, dirnames, filenames in os.walk('.'):
      for filename in fnmatch.filter(filenames, '*.sample.*'):
            matches.append(os.path.join(root, filename))
    return matches

def _process_files(context):
    template_engine = _template_engine(context)

    for filename in _find_sample_files():
        new_filename = filename.replace("sample.", "")
        content = open(filename).read()

        new_content = re_templates.sub(template_engine, content)
        new_content = _encode(new_content)

        fp = open(new_filename, "w")
        fp.write(new_content)
        fp.close()

def install():
    #context = {
    #    "subdomain" : str(fabutils.ask_not_empty("Please enter in your application subdomain (e.g. mpr): ")),
    #    "gunicorn_host" : "192.168.123.92",
    #    "gunicorn_port" : str(fabutils.ask_number("Please enter in your gunicorn port (e.g. 9002): "))
    #}

    context = {
        "subdomain" : "r2j",
        "gunicorn_host" : "192.168.123.92",
        "gunicorn_port" : "9002",
        "admin_user" : "adi",
        "server_prefix" : "code4sa.org",
        "server_ssh_port" : "2222"
    }

    context["supervisor_name"] = "{subdomain}".format(**context)
    context["username"] = context["subdomain"]
    context["domain"] = "{subdomain}.{server_prefix}".format(**context)
    context["code_dir"] = "/var/www/{domain}".format(**context)
    context["virtualenv_root"] = "/var/www/.virtualenvs".format(**context)
    context["virtualenv_dir"] = "{virtualenv_root}/{subdomain}".format(**context)

    _process_files(context)

    fabutils.new_user(context["username"])
    sudo("virtualenv {virtualenv_dir}".format(**context))
    put("deploy/nginx.conf", "/etc/nginx/sites-available/{domain}".format(**context), use_sudo=True)
    fabutils.remote_soft_link(
        "/etc/nginx/sites-available/{domain}".format(**context), "/etc/nginx/sites-enabled/{domain}".format(**context)
    )
    sudo("/etc/init.d/nginx restart")

    context["repo"] = fabutils.ask_not_empty("Please enter in your git repo url (e.g. git@github.com:Code4SA/test.git): ")

    
    local("rm -rf .git")
    local("git init")
    local("git add .")
    local("git commit -a -m 'Initial Commit'")
    local("git remote add origin {repo}".format(**context))
    local("git push -u origin master")

    run("git clone {repo} /tmp/{domain}".format(**context))
    sudo("mv /tmp/{domain} {code_dir}".format(**context))
    sudo("chown {username}:{username} {code_dir}".format(**context))
    sudo("chmod ug+wxr {code_dir}".format(**context))

    put("deploy/supervisor.conf", "/etc/supervisor/conf.d/{supervisor_name}.conf".format(**context), use_sudo=True)
    sudo("supervisorctl update")
    
