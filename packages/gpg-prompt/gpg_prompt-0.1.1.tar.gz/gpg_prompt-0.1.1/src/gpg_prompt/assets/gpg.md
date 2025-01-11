# GNU Privacy Guard (GPG) Documentation
Extracted from the GnuPG manual first
published by the GnuPG Project
This version by David Robert Lewis
aka ubuntupunk

This document accompanies several helper programmes and a database designed to assist and teach users about GPG,
follow this link to access the [GPG official manuals](https://www.gnupgp.org/documentation/manuals.html). 
Disclaimer, this project is not related to the GnuPG Project and the contents below has not been tested and validated by the author. If any divergence from the official manual arises, please open a pull request at the
[gpg-prompt repo](https://github.com/ubuntupunk/gpg-prompt). For bug issues with GPG software please use the official channels.

## Table of Contents

- [GNU Privacy Guard (GPG) Documentation](#gnu-privacy-guard-gpg-documentation)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
    - [What is GPG?](#what-is-gpg)
    - [Basic Concepts](#basic-concepts)
  - [Key Management](#key-management)
    - [Key Generation](#key-generation)
    - [Key Listing](#key-listing)
    - [Key Export](#key-export)
    - [Key Import](#key-import)
    - [Key Verification](#key-verification)
    - [Key Signing](#key-signing)
    - [Key Revocation](#key-revocation)
    - [Key Editing](#key-editing)
    - [Key Trust and Validation](#key-trust-and-validation)
    - [Key Server Operations](#key-server-operations)
  - [Encryption and Decryption](#encryption-and-decryption)
    - [Basic Encryption](#basic-encryption)
    - [Decryption](#decryption)
    - [Advanced Encryption Options](#advanced-encryption-options)
    - [Hidden Recipients](#hidden-recipients)
    - [Output Options](#output-options)
    - [Special Options](#special-options)
  - [Signing and Verification](#signing-and-verification)
    - [Basic Signing](#basic-signing)
    - [Signature Verification](#signature-verification)
    - [Advanced Verification Options](#advanced-verification-options)
    - [Signature Notation Options](#signature-notation-options)
    - [Trust Options](#trust-options)
  - [Web Key Directory (WKD)](#web-key-directory-wkd)
    - [Basic WKD Usage](#basic-wkd-usage)
    - [WKD Server Setup](#wkd-server-setup)
    - [Advanced WKD Options](#advanced-wkd-options)
    - [WKD Configuration](#wkd-configuration)
    - [Security Considerations](#security-considerations)
    - [Best Practices](#best-practices)
  - [Server Configuration](#server-configuration)
    - [Keyserver Configuration](#keyserver-configuration)
    - [Network Settings](#network-settings)
    - [Connection Options](#connection-options)
    - [Security Options](#security-options)
  - [Configuration Files](#configuration-files)
    - [Main Configuration File](#main-configuration-file)
    - [Agent Configuration](#agent-configuration)
    - [Directory Structure](#directory-structure)
    - [Configuration Options](#configuration-options)
      - [Key Management](#key-management-1)
      - [Algorithm Preferences](#algorithm-preferences)
      - [Security Settings](#security-settings)
    - [Environment Variables](#environment-variables)
    - [Best Practices](#best-practices-1)
  - [Command List](#command-list)

## Introduction

### What is GPG?

GNU Privacy Guard (GPG) is a free implementation of the OpenPGP standard. It is a tool for secure communication and data storage.

### Basic Concepts

* **Key Pair**: A pair of keys, one public and one private, used for encryption and decryption.
* **Public Key**: A key that can be shared with others, used for encryption.
* **Private Key**: A key that should be kept secret, used for decryption.
* **Keyring**: A collection of keys, used to manage and store keys.
* **Keyserver**: A server that stores and distributes public keys.

> **Note**: This documentation is a practical guide drawn from the official GPG manual. For complete technical details and all available options, please refer to the [GPG Manual Page](gpg-origin.md).

## Key Management

### Key Generation

To generate a new key pair:
```bash
gpg --gen-key
```

This command starts an interactive dialog that helps you create a key pair. You will be asked to:
1. Select the key type (RSA and RSA is recommended)
2. Choose the key size (2048 or 4096 bits is recommended)
3. Set an expiration date (optional but recommended)
4. Enter your name and email address
5. Set a passphrase

For more control over the key generation process, use the `--full-gen-key` option:
```bash
gpg --full-gen-key
```

### Key Listing

To list all keys in your public keyring:
```bash
gpg --list-keys
# or
gpg -k
```

To list secret keys:
```bash
gpg --list-secret-keys
# or
gpg -K
```

To show fingerprints along with the keys:
```bash
gpg --fingerprint
```

### Key Export

To export a public key in ASCII armor format:
```bash
gpg --armor --export user-id > public.key
```

To export a secret key (be very careful with this!):
```bash
gpg --armor --export-secret-keys user-id > private.key
```

To export a specific subkey:
```bash
gpg --armor --export-secret-subkeys user-id > subkey.key
```

### Key Import

To import a public key:
```bash
gpg --import public.key
```

To import a private key:
```bash
gpg --import private.key
```

### Key Verification

After importing a key, you should verify its fingerprint:
```bash
gpg --fingerprint user-id
```

### Key Signing

To sign someone's public key:
```bash
gpg --sign-key user-id
```

To sign with your own key and export the signature:
```bash
gpg --armor --export user-id > signed.key
```

### Key Revocation

To generate a revocation certificate:
```bash
gpg --gen-revoke user-id > revoke.asc
```

To revoke a key using the certificate:
```bash
gpg --import revoke.asc
```

### Key Editing

To edit a key (change expiration, add/remove email addresses, etc.):
```bash
gpg --edit-key user-id
```

Common commands in the key editing interface:
- `adduid`: Add a new user ID
- `deluid`: Delete a user ID
- `expire`: Change expiration date
- `passwd`: Change the passphrase
- `trust`: Change the trust level
- `save`: Save changes and exit
- `quit`: Exit without saving

### Key Trust and Validation

To mark a key as trusted:
```bash
gpg --edit-key user-id trust
```

Trust levels:
1. Don't know (1)
2. I do NOT trust (2)
3. I trust marginally (3)
4. I trust fully (4)
5. I trust ultimately (5)

### Key Server Operations

To send a key to a keyserver:
```bash
gpg --keyserver keyserver.ubuntu.com --send-keys key-id
```

To receive a key from a keyserver:
```bash
gpg --keyserver keyserver.ubuntu.com --recv-keys key-id
```

To search for a key on a keyserver:
```bash
gpg --keyserver keyserver.ubuntu.com --search-keys search-string
```

To refresh all keys from a keyserver:
```bash
gpg --keyserver keyserver.ubuntu.com --refresh-keys
```

## Encryption and Decryption

### Basic Encryption

To encrypt a file for a specific recipient:
```bash
gpg --encrypt --recipient user-id file
```

To encrypt with ASCII armor output:
```bash
gpg --armor --encrypt --recipient user-id file
```

To encrypt for multiple recipients:
```bash
gpg --encrypt --recipient user1-id --recipient user2-id file
```

To encrypt with a symmetric cipher (password-based):
```bash
gpg --symmetric file
```

### Decryption

To decrypt a file:
```bash
gpg --decrypt file.gpg > decrypted-file
```

To decrypt and verify a signed, encrypted file:
```bash
gpg --decrypt signed-encrypted-file.gpg
```

### Advanced Encryption Options

* `--symmetric`, `-c`
    Encrypt with symmetric cipher only. This command asks for a passphrase.

* `--cipher-algo name`
    Use name as cipher algorithm. Running the program with the command `--version` yields a list of supported algorithms.

* `--digest-algo name`
    Use name as the message digest algorithm. Running the program with the command `--version` yields a list of supported algorithms.

* `--compress-algo name`
    Use compression algorithm name. Supported algorithms are:
    - `zlib`: RFC-1950 ZLIB compression
    - `zip`: PKWare's ZIP compression
    - `bzip2`: Burrows-Wheeler compression
    - `none`: No compression

* `--s2k-mode n`
    Selects how passphrases are mangled. The possible values for n are:
    - `0`: Simple S2K
    - `1`: Salted S2K
    - `3`: Iterated and salted S2K

* `--s2k-count n`
    Specify how many times the passphrase mangling should be repeated. Value must be between 1024 and 65011712.

* `--s2k-cipher-algo name`
    Use name as the cipher algorithm for symmetric encryption with a passphrase.

* `--s2k-digest-algo name`
    Use name as the digest algorithm used to mangle the passphrase.

### Hidden Recipients

* `--hidden-recipient name`
    Encrypt for user ID name, but hide the keyid of this user's key. This option helps prevent traffic analysis.

* `--throw-keyids`
    Don't put keyids in encrypted packets. This option helps to hide the receivers and is a limited countermeasure against traffic analysis.

### Output Options

* `--output file`, `-o file`
    Write output to file instead of stdout.

* `--armor`, `-a`
    Create ASCII armored output.

* `--textmode`, `-t`
    Treat input as text and convert line endings.

### Special Options

* `--force-mdc`
    Force the use of encryption with a modification detection code. This is the default.

* `--disable-mdc`
    Disable the use of the modification detection code. Only use this if you know what you are doing.

* `--require-secmem`
    Refuse to run if GnuPG cannot get secure memory.

* `--no-random-seed-file`
    Don't use the random seed file for starting the internal random number generator.

* `--no-greeting`
    Suppress the initial copyright message.

* `--no-permission-warning`
    Suppress warnings about unsafe file and home directory permissions.

## Signing and Verification

### Basic Signing

To create a cleartext signature:
```bash
gpg --clearsign file
```

To create a detached signature:
```bash
gpg --detach-sign file
```

To create an ASCII armored detached signature:
```bash
gpg --armor --detach-sign file
```

To sign and encrypt in one step:
```bash
gpg --sign --encrypt --recipient user-id file
```

### Signature Verification

To verify a signature:
```bash
gpg --verify signature.asc
```

To verify a detached signature:
```bash
gpg --verify signature.asc original-file
```

To verify and decrypt in one step:
```bash
gpg --decrypt signed-encrypted-file.gpg
```

### Advanced Verification Options

* `--verify`
    Verify a signature. With no arguments, the signature packet is assumed to be the first file and the signed material is assumed to be the second file.

* `--verify-options parameters`
    This is a space or comma delimited string that gives options used when verifying signatures. Options can be prepended with a `no-` to give the opposite meaning. The options are:

    * `show-photos`
        Display any photo IDs present on the key that issued the signature.

    * `show-policy-urls`
        Show policy URLs embedded in signatures.

    * `show-notations`
        Show all signature notations.

    * `show-std-notations`
        Show only standard signature notations.

    * `show-keyserver-urls`
        Show any preferred keyserver URL present in the signature.

* `--assume-valid-sigs`
    Skip signature verification. This is useful if you have already verified the signatures and just want to process the data.

### Signature Notation Options

* `--sig-notation name=value`
    Add a signature notation. The notation consists of a name and a value.

* `--cert-notation name=value`
    Add a certification notation. Similar to `--sig-notation` but only for key signatures.

* `--set-notation name=value`
    Add a notation to all signatures. This includes both signature notations and certification notations.

### Trust Options

* `--trust-model pgp|classic|direct|always|auto`
    Set what trust model GnuPG should follow when verifying signatures.

* `--always-trust`
    Skip key validation and assume that used keys are always valid.

* `--no-auto-check-trustdb`
    Do not automatically check the trustdb after modifications.

## Web Key Directory (WKD)

The Web Key Directory (WKD) is a method to discover OpenPGP keys through HTTPS. It provides a standardized way to distribute public keys through web servers.

### Basic WKD Usage

To fetch a key using WKD:
```bash
gpg --locate-keys user@example.com
```

To fetch and import keys for multiple email addresses:
```bash
gpg --auto-key-locate wkd --locate-keys user1@example.com user2@example.org
```

### WKD Server Setup

To create a Web Key Directory structure:
```bash
gpg -k --with-wkd user@example.com
```

The files will be created in the `.well-known/openpgpkey` directory of your web server.

### Advanced WKD Options

* `--auto-key-locate mechanisms`
    Set the list of methods to locate keys. Valid mechanisms for WKD are:
    - `wkd`: Web Key Directory
    - `dane`: DANE protocol
    - `local`: Local keyring
    - `cert`: PKA protocol
    - `kdns`: DNS CERT
    - `keyserver`: Keyserver

* `--with-wkd-hash`
    Print the Web Key Directory hash of the specified email addresses.

* `--with-wkd`
    Print the Web Key Directory submission address.

### WKD Configuration

* `--wkd-host name`
    Override the WKD host for the next operation.

* `--wkd-method {direct|advanced}`
    Select between the direct and advanced WKD method.
    - `direct`: Uses a simple URL structure
    - `advanced`: Uses a more complex but more flexible structure

### Security Considerations

* WKD requires HTTPS for secure key distribution
* The web server must be properly configured for HTTPS
* Domain validation is essential for security
* Regular key updates should be implemented
* Access controls should be in place for key submissions

### Best Practices

1. Always use HTTPS for WKD
2. Regularly update published keys
3. Implement proper access controls
4. Monitor key requests and updates
5. Keep the web server secure and updated
6. Use strong keys and maintain proper key hygiene

## Server Configuration

### Keyserver Configuration

* `--keyserver name`
    Use name as your keyserver. This is the server that gpg communicates with to receive keys, send keys, and search for keys.
    Example:
    ```bash
    gpg --keyserver hkps://keys.openpgp.org --search-keys user@example.com
    ```

* `--keyserver-options parameters`
    This is a space or comma delimited string that gives options for keyserver operations. Options can be prepended with a `no-` to give the opposite meaning. The options are:

    * `include-revoked`
        When searching for a key with `--search-keys`, include keys marked as revoked.

    * `include-disabled`
        When searching for a key with `--search-keys`, include keys marked as disabled.

    * `honor-keyserver-url`
        When using `--refresh-keys`, if the key has a preferred keyserver URL, then use that preferred keyserver to refresh the key.

    * `honor-pka-record`
        If `--auto-key-retrieve` is used, and the signature being verified has a PKA record, then use the PKA information to fetch the key.

### Network Settings

* `--http-proxy host[:port]`
    Set the proxy to use for HTTP and HKP keyservers.

* `--disable-http`
    Disable the ability to use HTTP/HTTPS for keyserver access.

* `--disable-ldap`
    Disable the ability to use LDAP for keyserver access.

### Connection Options

* `--connect-timeout seconds`
    Set the timeout for network operations.

* `--connect-quick`
    Do not try too hard to connect to keyservers.

* `--max-cert-depth n`
    When building the trust path for a key, limit the depth to n steps.

### Security Options

* `--no-allow-non-selfsigned-uid`
    Do not allow non-selfsigned user IDs on certificates retrieved from keyservers.

* `--no-allow-weak-digest-algos`
    Do not allow the use of weak digest algorithms when verifying signatures.

* `--require-cert-checks`
    Require certificate checks when accessing HTTPS URLs.

## Configuration Files

GnuPG uses several configuration files to store its settings and preferences. Here are the main configuration files and their purposes:

### Main Configuration File

The main configuration file is `gpg.conf`. Its default location depends on your system:
- Unix-like systems: `~/.gnupg/gpg.conf`
- Windows: `%APPDATA%\GnuPG\gpg.conf`

Common settings in `gpg.conf`:
```bash
# Default key to use for signing
default-key 0123456789ABCDEF

# Preferred algorithms
personal-cipher-preferences AES256 AES192 AES
personal-digest-preferences SHA512 SHA384 SHA256
personal-compress-preferences ZLIB BZIP2 ZIP

# Display preferences
keyid-format 0xlong
with-fingerprint
with-keygrip

# Key server settings
keyserver hkps://keys.openpgp.org
keyserver-options auto-key-retrieve
```

### Agent Configuration

The GnuPG agent configuration file is `gpg-agent.conf`. Default locations:
- Unix-like systems: `~/.gnupg/gpg-agent.conf`
- Windows: `%APPDATA%\GnuPG\gpg-agent.conf`

Example `gpg-agent.conf`:
```bash
# Set the default cache time to 1 hour
default-cache-ttl 3600
max-cache-ttl 7200

# Enable SSH support
enable-ssh-support

# Set PIN entry program
pinentry-program /usr/bin/pinentry-gtk-2
```

### Directory Structure

The GnuPG home directory contains several important files:
```
~/.gnupg/
├── gpg.conf           # Main configuration
├── gpg-agent.conf     # Agent configuration
├── trustdb.gpg        # Trust database
├── pubring.kbx        # Public keyring
├── private-keys-v1.d/ # Private keys
└── sshcontrol        # SSH key control file
```

### Configuration Options

#### Key Management
```bash
# Always show long key IDs
keyid-format 0xlong

# Show fingerprints with key listings
with-fingerprint

# Display key grips
with-keygrip

# Default key for signing
default-key 0123456789ABCDEF
```

#### Algorithm Preferences
```bash
# Cipher algorithms
personal-cipher-preferences AES256 AES192 AES
cipher-algo AES256

# Digest algorithms
personal-digest-preferences SHA512 SHA384 SHA256
digest-algo SHA512

# Compression algorithms
personal-compress-preferences ZLIB BZIP2 ZIP
compress-algo ZLIB
```

#### Security Settings
```bash
# Require strong digests
require-secmem
require-cross-certification
no-allow-weak-digest-algos

# Display all keys and user IDs
list-options show-uid-validity
verify-options show-uid-validity
```

### Environment Variables

Important environment variables that affect GnuPG:

* `GNUPGHOME`
    Sets the home directory for GnuPG

* `GPG_TTY`
    Tells gpg which terminal to use

* `GPG_AGENT_INFO`
    Contains information about the running gpg-agent

Example usage:
```bash
export GNUPGHOME=~/.my-gpg
export GPG_TTY=$(tty)
```

### Best Practices

1. Always back up your configuration files
2. Use strong algorithm preferences
3. Keep your home directory secure
4. Regularly update your configuration
5. Document your custom settings
6. Use version control for tracking changes

## Troubleshooting and Common Issues

### Common Error Messages

#### Key-Related Issues

* "No public key"
    ```
    gpg: decryption failed: No public key
    ```
    Solution:
    1. Import the sender's public key:
    ```bash
    gpg --import sender-public-key.asc
    ```
    2. Or retrieve it from a keyserver:
    ```bash
    gpg --keyserver keys.openpgp.org --recv-keys KEY_ID
    ```
* "No secret key"
    ```
    gpg: decryption failed: No secret key
    ```
    Solution:
    1. Check if you have the private key:
    ```bash
    gpg -K
    ```
    2. Import your private key if needed:
    ```bash
    gpg --import private-key.asc
    ```
* "Unusable public key"
    ```
    gpg: unusable public key
    ```
    Solution:
    1. Check key validity:
    ```bash
    gpg --check-sigs KEY_ID
    ```
    2. Update the key from keyserver:
    ```bash
    gpg --refresh-keys KEY_ID
    ```
### Permission Issues
* "Permission denied"
    ```
    gpg: can't open '/home/user/.gnupg/gpg.conf': Permission denied
    ```
    Solution:
    ```bash
    # Fix permissions on .gnupg directory
    chmod 700 ~/.gnupg
    chmod 600 ~/.gnupg/*
    ```
* "Unsafe directory permissions"
    ```
    gpg: WARNING: unsafe permissions on homedir '/home/user/.gnupg'
    ```
    Solution:
    ```bash
    # Set correct permissions
    chmod 700 ~/.gnupg
    find ~/.gnupg -type f -exec chmod 600 {} \;
    find ~/.gnupg -type d -exec chmod 700 {} \;
    ```
### Agent Issues
* "gpg-agent not running"
    ```
    gpg: agent_genkey failed: No agent running
    ```
    Solution:
    ```bash
    # Start gpg-agent
    gpg-agent --daemon

    # Or restart it
    gpgconf --kill gpg-agent
    gpg-agent --daemon
    ```
* "PIN entry dialog not appearing"
    Solution:
    1. Check pinentry program configuration:
    ```bash
    echo "pinentry-program /usr/bin/pinentry-gtk-2" >> ~/.gnupg/gpg-agent.conf
    ```
    2. Restart gpg-agent:
    ```bash
    gpgconf --kill gpg-agent
    gpg-agent --daemon
    ```
### Network Issues
* "Keyserver connection failed"
    ```
    gpg: keyserver receive failed: No route to host
    ```
    Solution:
    1. Check internet connection
    2. Try a different keyserver:
    ```bash
    gpg --keyserver hkps://keys.openpgp.org --recv-keys KEY_ID
    ```
    3. Check proxy settings if needed:
    ```bash
    gpg --keyserver-options http-proxy=http://proxy:8080 --recv-keys KEY_ID
    ```
### Trust Database Issues
* "Trust database needs rebuild"
    ```
    gpg: trustdb: trust database needs rebuild
    ```
    Solution:
    ```bash
    gpg --update-trustdb
    # Or for a complete rebuild
    gpg --rebuild-keydb-caches
    ```
### Performance Issues
* Slow key generation
    Solution:
    1. Install rng-tools:
    ```bash
    sudo apt-get install rng-tools  # For Debian/Ubuntu
    ```
    2. Or use an entropy generator:
    ```bash
    sudo rngd -r /dev/urandom
    ```
### Best Practices for Troubleshooting
1. Check the GnuPG version:
```bash
gpg --version
```
2. Enable debug output:
```bash
gpg --debug-all --verbose
```
3. Check system logs:
```bash
journalctl -f
```
4. Verify configuration:
```bash
gpgconf --check-config
```
5. Test basic functionality:
```bash
echo "test" | gpg --clearsign
```
### Common Solutions
1. Reset to default configuration:
```bash
mv ~/.gnupg ~/.gnupg.bak
gpg --list-keys  # This creates a new .gnupg directory
```
2. Clean and rebuild the keyring:
```bash
gpg --check-trustdb
gpg --update-trustdb
```
3. Fix common permission issues:
```bash
chmod 700 ~/.gnupg
chmod 600 ~/.gnupg/*
chmod 700 ~/.gnupg/private-keys-v1.d
```
4. Reset the agent:
```bash
gpgconf --kill gpg-agent
gpg-agent --daemon
```
5. Clear the key cache:
```bash
gpgconf --reload gpg-agent
```
## Security Best Practices
### Key Management
1. **Key Generation**
   - Use strong key sizes (minimum 2048 bits for RSA)
   - Set reasonable expiration dates
   - Generate keys on a secure system
   - Use strong passphrases
   ```bash
   gpg --full-gen-key
   # Choose RSA and RSA (default)
   # Use 4096 bits
   # Set expiration to 2 years
   ```
2. **Key Storage**
   - Keep private keys offline when possible
   - Use encrypted storage for backup
   - Never share private keys
   - Consider using a hardware security module (HSM)
   ```bash
   # Export private key for backup
   gpg --export-secret-keys --armor KEY_ID > private.key.asc
   
   # Store securely and encrypted
   gpg --symmetric private.key.asc
   ```
3. **Key Protection**
   - Use strong passphrases
   - Change passphrases periodically
   - Protect your keyring directory
   ```bash
   # Change passphrase
   gpg --change-passphrase KEY_ID
   
   # Set correct permissions
   chmod 700 ~/.gnupg
   chmod 600 ~/.gnupg/*
   ```
### System Security
1. **File System Security**
   - Secure permissions on GnuPG directory
   - Use encrypted file systems
   - Regular backups of keys and configuration
   ```bash
   # Set secure permissions
   find ~/.gnupg -type f -exec chmod 600 {} \;
   find ~/.gnupg -type d -exec chmod 700 {} \;
   ```
2. **Memory Security**
   - Use secure memory for sensitive operations
   - Clear memory after use
   ```bash
   # Enable secure memory
   echo "require-secmem" >> ~/.gnupg/gpg.conf
   
   # Clear agent cache
   gpgconf --reload gpg-agent
   ```
### Network Security
1. **Keyserver Usage**
   - Use HTTPS keyservers
   - Verify key fingerprints
   - Be cautious with automatic key retrieval
   ```bash
   # Use secure keyserver
   keyserver hkps://keys.openpgp.org
   
   # Verify fingerprints
   gpg --fingerprint KEY_ID
   ```
2. **Web Key Directory**
   - Use HTTPS for WKD
   - Implement proper access controls
   - Regular monitoring of key requests
   ```bash
   # Configure WKD
   gpg --list-options show-only-fpr-mbox
   ```
### Operational Security
1. **Daily Operations**
   - Regular key rotation
   - Monitoring of key usage
   - Regular security audits
   ```bash
   # Check key expiration
   gpg --list-keys --with-colons | grep "^pub"
   
   # List recent signatures
   gpg --list-sigs
   ```
2. **Incident Response**
   - Have a key revocation certificate ready
   - Plan for key compromise
   - Document recovery procedures
   ```bash
   # Generate revocation certificate
   gpg --gen-revoke KEY_ID > revoke.asc
   
   # Store securely
   chmod 600 revoke.asc
   ```
### Configuration Hardening
1. **Algorithm Selection**
   ```bash
   # In gpg.conf
   personal-cipher-preferences AES256 AES192 AES
   personal-digest-preferences SHA512 SHA384 SHA256
   personal-compress-preferences ZLIB BZIP2 ZIP
   
   default-preference-list SHA512 SHA384 SHA256 AES256 AES192 AES ZLIB BZIP2 ZIP
   cert-digest-algo SHA512
   s2k-digest-algo SHA512
   ```
2. **Agent Configuration**
   ```bash
   # In gpg-agent.conf
   default-cache-ttl 600
   max-cache-ttl 7200
   enforce-passphrase-constraints
   min-passphrase-len 12
   ```
### Regular Maintenance
1. **Key Maintenance**
   ```bash
   # Update keys
   gpg --refresh-keys
   
   # Check signatures
   gpg --check-sigs
   
   # Clean unused keys
   gpg --delete-keys UNUSED_KEY_ID
   ```
2. **System Maintenance**
   ```bash
   # Check trustdb
   gpg --check-trustdb
   
   # Update configuration
   gpg --update-trustdb
   ```
### Compliance and Auditing
1. **Logging and Monitoring**
   ```bash
   # Enable verbose logging
   echo "verbose" >> ~/.gnupg/gpg.conf
   echo "log-file ~/.gnupg/gpg.log" >> ~/.gnupg/gpg.conf
   ```
2. **Regular Audits**
   - Review key usage
   - Check access logs
   - Verify configurations
   ```bash
   # List all keys and their trust levels
   gpg --list-keys --with-colons
   
   # Check configuration
   gpg --gpgconf-list
   ```
   
## Command List

This is a list of all gpg commands documented in this file and used by the accompanying helper programmes and database:

- `gpg --gen-key`
- `gpg --full-gen-key`
- `gpg --list-keys`
- `gpg -k`
- `gpg --list-secret-keys`
- `gpg -K`
- `gpg --fingerprint`
- `gpg --armor --export user-id > public.key`
- `gpg --armor --export-secret-keys user-id > private.key`
- `gpg --armor --export-secret-subkeys user-id > subkey.key`
- `gpg --import public.key`
- `gpg --import private.key`
- `gpg --fingerprint user-id`
- `gpg --sign-key user-id`
- `gpg --armor --export user-id > signed.key`
- `gpg --gen-revoke user-id > revoke.asc`
- `gpg --import revoke.asc`
- `gpg --edit-key user-id`
- `gpg --edit-key user-id trust`
- `gpg --keyserver keyserver.ubuntu.com --send-keys key-id`
- `gpg --keyserver keyserver.ubuntu.com --recv-keys key-id`
- `gpg --keyserver keyserver.ubuntu.com --search-keys search-string`
- `gpg --keyserver keyserver.ubuntu.com --refresh-keys`
- `gpg --encrypt --recipient user-id file`
- `gpg --armor --encrypt --recipient user-id file`
- `gpg --encrypt --recipient user1-id --recipient user2-id file`
- `gpg --symmetric file`
- `gpg --decrypt file.gpg > decrypted-file`
- `gpg --decrypt signed-encrypted-file.gpg`
- `gpg --clearsign file`
- `gpg --detach-sign file`
- `gpg --armor --detach-sign file`
- `gpg --sign --encrypt --recipient user-id file`
- `gpg --verify signature.asc`
- `gpg --verify signature.asc original-file`
- `gpg --decrypt signed-encrypted-file.gpg`
- `gpg --locate-keys user@example.com`
- `gpg --auto-key-locate wkd --locate-keys user1@example.com user2@example.org`
- `gpg -k --with-wkd user@example.com`
- `gpg --keyserver hkps://keys.openpgp.org --search-keys user@example.com`
