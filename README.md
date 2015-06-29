ansible-django-stack
====================

Ansible Playbook designed for environments running a Django app.  It can install and configure these applications that are commonly used in production Django deployments:

- Nginx
- Gunicorn
- PostgreSQL
- Supervisor
- Virtualenv
- Memcached
- Celery
- RabbitMQ

Default settings are stored in ```roles/role_name/vars/main.yml```.  Environment-specific settings are in the ```env_vars``` directory.

**Tested with OS:** Ubuntu 14.04 LTS x64

## Getting Started

A quick way to get started is with Vagrant and VirtualBox.

### Requirements

- [Ansible](http://docs.ansible.com/intro_installation.html)
- [Vagrant](http://www.vagrantup.com/downloads.html)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

The main settings to change here is in the **env_vars/base** file, where you can configure the location of your Git project, the project name, and application name which will be used throughout the Ansible configuration.

Note that the default values in the playbooks assume that your project structure looks something like this:

```
myproject
├── manage.py
├── myproject
│   ├── apps
│   │   └── __init__.py
│   ├── templates
│   │   ├── 403.html
│   │   ├── 404.html
│   │   ├── 500.html
│   │   └── base.html
│   ├── __init__.py
│   ├── celery.py
├── config
│   ├── settings
│   │   ├── base.py
│   │   ├── __init__.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── README.md
└── requirements.txt
```

The main things to note are the locations of the `manage.py`, `wsgi.py` and `celery.py` files.  If your project's structure is a little different, you may need to change the values in these 2 files:

- `roles/web/tasks/setup_django_app.yml`
- `roles/web/templates/gunicorn_start.j2`
- `roles/celery/templates/celery_start.j2`

Also, if your app needs additional system packages installed, you can add them in `roles/web/tasks/install_additional_packages.yml`.

If you setup your django project with the [cookiecutter template](https://github.com/RayCrafter/cookiecutter-django), just replace the repository link in `env_vars/base.yml` to your repository.

I set some default values in the `env_vars` based on a test project, [Djangotest](https://github.com/RayCrafter/djangotest), so all you really have to do is type in this one command in the project root:

```
vagrant up
```

Wait a few minutes for the magic to happen.  Access the app by going to this URL: http://192.168.33.15

Yup, exactly, you just provisioned a completely new server and deployed an entire Django stack in 5 minutes with _two words_ :).

### Additional vagrant commands

**SSH to the box**

```
vagrant ssh
```

**Re-provision the box to apply the changes you made to the Ansible configuration**

```
vagrant provision
```

**Reboot the box**

```
vagrant reload
```

**Shutdown the box**

```
vagrant halt
```

## Running the Ansible Playbook to provision servers

First, create an inventory file for the environment, for example:

```
# development

[all:vars]
env=dev

[webservers]
webserver1.example.com
webserver2.example.com

[dbservers]
dbserver1.example.com
```

Next, create a playbook for the server type. See [webservers.yml](webservers.yml) for an example.

Run the playbook:

```
ansible-playbook -i development webservers.yml
```

You can also provision an entire site by combining multiple playbooks.  For example, I created a playbook called `site.yml` that includes both the `webservers.yml` and `dbservers.yml` playbook.

A few notes here:

- The `dbservers.yml` playbook will only provision servers in the `[dbservers]` section of the inventory file.
- The `webservers.yml` playbook will only provision servers in the `[webservers]` section of the inventory file.
- An inventory var called `env` is also set which applies to `all` hosts in the inventory.  This is used in the playbook to determine which `env_var` file to use.

You can then provision the entire site with this command:

```
ansible-playbook -i development site.yml
```

If you're testing with vagrant, you can use this command:

```
ansible-playbook -i vagrant_ansible_inventory_default --private-key=~/.vagrant.d/insecure_private_key vagrant.yml
```

## Advanced Options

### Creating a swap file

By default, the playbook won't create a swap file.  To create/enable swap, simply change the values in `roles/base/vars/main.yml`. 

You can also override these values in the main playbook, for example:


```
---

...

  roles:
    - { role: base, create_swap_file: yes, swap_file_size_kb: 1024 }
    - db
    - rabbitmq
    - web
    - celery
```

This will create and mount a 1GB swap.  Note that block size is 1024, so the size of the swap file will be 1024 x `swap_file_size_kb`.

## Useful Links

- [Ansible - Getting Started](http://docs.ansible.com/intro_getting_started.html)
- [Ansible - Best Practices](http://docs.ansible.com/playbooks_best_practices.html)
- [Setting up Django with Nginx, Gunicorn, virtualenv, supervisor and PostgreSQL](http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/)
- [How to deploy encrypted copies of your SSL keys and other files with Ansible and OpenSSL](http://www.calazan.com/how-to-deploy-encrypted-copies-of-your-ssl-keys-and-other-files-with-ansible-and-openssl/)
