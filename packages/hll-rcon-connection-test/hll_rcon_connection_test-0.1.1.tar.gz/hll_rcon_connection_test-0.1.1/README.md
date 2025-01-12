# hll-rcon-connection-test

A very simple CLI tool to test RCON connections to Hell Let Loose Servers

# Installation

Create and activate a [Virtual Environment](https://docs.python.org/3/library/venv.html) so you don't install this package globally.

```
pip install hll_rcon_connection_test
```

# Usage

```
python -m hll_rcon_connection_test IP:port password
```

For example:

```
❯ python -m hll_rcon_connection_test.main  127.0.0.1:26000 sOmEpassWorD
Connection/login successful
Server name: The Draft [HAUS] |US EAST-FL|
```

# Troubleshooting

If you get any sort of error messages, you are either not connected to the Internet, your game server is offline or having other network problems, or **most likely** you didn't provide the IP:port and password in the correct format, or you passed invalid credentials.