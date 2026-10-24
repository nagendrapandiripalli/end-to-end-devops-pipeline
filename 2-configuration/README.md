# Application configuration role

The role supplies configurable values in roles/app_deploy/defaults/main.yml.
Override these using inventory group_vars or host_vars. Do not reintroduce a
vars_files reference to the defaults: play-level variables would take precedence
over inventory values. Use extra variables only for deliberate run-specific
overrides.

Example group_vars/app_servers.yml next to your inventory:

    app_env: staging
    app_install_dir: /opt/myapp-staging
    app_service_name: myapp-staging
    app_port: 8081
    db_host: staging-db.internal

The default values are unchanged. Previously inventory variables could be
shadowed by both role vars and the playbook vars_files entry; both sources of
that precedence conflict have been removed.

## Validate before applying

From 2-configuration, with Ansible installed:

    ansible-playbook -i your-inventory playbook.yml --syntax-check
    ansible-playbook -i your-inventory playbook.yml --check --diff

Review the rendered configuration for the expected environment before applying.
Check mode may still require access to the target hosts. Keep secrets in Ansible
Vault or an approved secret store; do not commit them in inventory examples.

This role configures an existing application service; it does not install the
application binary or create a service unit. Provision those before using it.
Package installation currently targets Debian-family hosts.

## Automated syntax validation

GitHub Actions installs the version in requirements-ci.txt and runs:

    ansible-playbook -i inventory-ci.ini playbook.yml --syntax-check

The isolated inventory avoids dependence on private server addresses or SSH
credentials. Syntax checking parses the playbook and role without executing
tasks, installing packages or restarting services. Never use this inventory
for an actual deployment: it points at the local machine.

This catches Ansible syntax and module-resolution errors, but does not verify
service availability, template output or runtime idempotency. Those still
require a disposable target environment. Upgrade the pinned checker version
deliberately and verify syntax again when upgrading deployment Ansible.
