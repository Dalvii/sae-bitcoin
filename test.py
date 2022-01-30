import requests
from getpass import getpass

username = str(input("Entrez votre identifiant : "))       # id connexion ENT
password = getpass("Entrez votre motdepasse : ")      # mdp connexion ENT
semestre = "TDFTS3"         # le semestre à télécharger
fichier = "semestre.pdf"    # le nom du fichier des notes


while True:
    try:
        semestre1 = str(input("Etes vous du semestre 1 ? (y, n) : "))
        break
    except ValueError:
        print("Veuillez réessayer. Entrez bien 'y' ou 'n'")


if semestre1 == 'y':
    S1 = True              # Mettre à True si vous êtes au S1
else:
    S1 = False

print("Telechargement de note ENT - MissingNo.#9660")
s = requests.session()

r = s.get("https://login.unice.fr/login?service=https://ent.unice.fr/uPortal/Login")
html = r.text

post_req = html.split('<form id="fm1" action="')[1].split('"')[0]
lt = html.split('type="hidden" name="lt" value="')[1].split('"')[0]
execution = html.split('type="hidden" name="execution" value="')[1].split('"')[0]

payload = {'username': username, 'password': password, 'lt': lt, 'execution': execution, '_eventId':'submit', 'submit': 'SE CONNECTER'}
r = s.post('https://login.unice.fr' + post_req, data=payload, allow_redirects=False)

if not "Location" in r.headers:
    print("-> Connexion: Erreur (Mauvais identifiant)")
    quit()

url = r.headers['Location']
r = s.get(url)

ticket = url.split('ticket=')[1]
print("-> Ticket récupéré: " + ticket)

s.cookies.set('SESSID', ticket, domain="planier.unice.fr")
url = r.text.split('valign="top" class="uportal-text"><a href="')[2].split('"')[0]
s.get("https://login.unice.fr/uPortal/" + url)
print("-> Connexion: OK")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.3'}
r = s.get("https://ent.unice.fr/uPortal/tag.idempotent.render.userLayoutRootNode.uP", headers=headers)
print("-> Direction page d'accueil")

url = r.text.split('class="uportal-background-semidark" nowrap="nowrap"><a href="')[3].split('"')[0]
r = s.get("https://ent.unice.fr/uPortal/" + url, headers=headers)

url = r.text.split("if 	(tabName=='Mes Infos') {")[1].split('this.location.href="')[1].split('";')[0]
r = s.get("https://ent.unice.fr/uPortal/" + url, headers=headers)
print("-> Direction page 'Mes Infos'")

code = r.text.split('<span class="uportal-navigation-category">')[2].split('href="')[1].split('"')[0].split('tag.')[1].split('.render')[0]
s.get("https://ent.unice.fr/uPortal/tag." + code + ".render.userLayoutRootNode.uP?uP_tcattr=minimized&minimized_channelId=3149-8&minimized_3149-8_value=false", headers=headers)
print("-> Direction page 'Intracursus'")

s.get('https://login.unice.fr/login?service=https%3A%2F%2Fintracursus2.unice.fr%2Fic%2Fdlogin%2Fcas.php')
print("-> Connexion à Intracursus")

payload = {'idautreinscription': semestre, 'telreleveanterieur': 'Télécharger le relevé du parcours sélectionné'}
if S1: 
    payload = {'telrelevepresences': 'Télécharger le relevé des notes et absences de ' + semestre}

r = s.post('https://intracursus2.unice.fr/ic/etudiant/ic-notes-presences.php', data=payload, headers=headers)

a = open(fichier, 'wb')
a.write(r.content)
a.close()

print("-> Note récupéré (" + fichier + ")")