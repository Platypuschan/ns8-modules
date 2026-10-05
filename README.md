# My NethServer 8 modules

I built these modules for my own NethServer 8 setup. They took some work, so I'm sharing them in case they save you some time too. This is a test repository, and I can't promise the modules will work in every setup. Please try them on a test system first and make a backup. Feedback and bug reports are very welcome.

## Modules

- **[Gitea Reworked](https://github.com/Platypuschan/ns8-gitea-reworked)** — A private Git service with Git over SSH, optional Active Directory login with group-based access, and a recovery administrator whose password you can view or regenerate in the NS8 settings.
- **[ntfy Reworked](https://github.com/Platypuschan/ns8-ntfy-reworked)** — Self-hosted notifications with an editor for ntfy's `server.yml`, settings for NS8's reverse proxy, and outgoing mail through the NS8 smarthost.
- **[Organizr Reworked](https://github.com/Platypuschan/ns8-organizr-reworked)** — A dashboard for services and bookmarks, packaged with NS8 HTTPS routing, persistent data, and backup/restore support. Choose at first setup: a managed setup that creates a recovery administrator and can let accounts of an NS8 Active Directory domain sign in, or Organizr's own setup wizard.
- **[Samba Reworked](https://github.com/Platypuschan/ns8-samba-reworked)** — A wizard to join a domain controller on a separate NS8 installation to an existing AD domain, plus optional ntfy alerts after repeated replication failures. It does not replicate SYSVOL; read the module's network and installation notes before using it.
- **[Fail2ban Reworked](https://github.com/Platypuschan/ns8-fail2ban-reworked)** — Watches failed logins from SSH, the NS8 admin UI, Gitea, Organizr, and Samba. It applies permanent host-wide bans, shares bans and a whitelist across NS8 installations through a coordinator, and can send ntfy alerts. Read its firewall and rootful-module notes before installing it.
- **[Obsidian LiveSync](https://github.com/Platypuschan/ns8-obsidian-livesync)** — A CouchDB server for the [Self-hosted LiveSync](https://github.com/vrtmrz/obsidian-livesync) plugin of Obsidian, with the plugin's server settings, HTTPS routing, and backup/restore support. Sync accounts each get a database of their own and can be added by hand or created automatically for the members of an NS8 Active Directory group; users who leave the group are locked out, their database is kept. The settings page shows the values to enter in the plugin and can reset a database.

## Add the repository

In the NS8 admin UI, open **Settings → Software repositories → Add repository**. Use `platypuschan` as the name and paste this URL:

```text
https://platypuschan.github.io/ns8-modules/ns8/updates/
```

Enable the repository, then select **Reload repositories** in the Software Center. The links above have setup details for each module. If you find a bug or have an idea, please open an issue in that module's repository and tell me what you tried.
