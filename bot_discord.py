import requests
import os
from dotenv import load_dotenv
import sys
import webbrowser
import discord
from datetime import datetime
import random


import asyncio
# NOTES --------------------------------------
# le but est de récupérer l'identifiant puuid du mec que je veux stalk, avec celui-ci je pourrais récuperer les données de la game
# et en extraire les kda le nombre de ses morts afin de déclencher une alerte en dessous d'un certain seuil.


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# https://developer.riotgames.com/apis#match-v5/GET_getMatch ==> avoir les endpoints 


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



# je met dans cette liste les requêtes a utiliser dans l'ordre 
# premiere requete pour avoir le puuid du boug
# deuxieme requete pour avoir une liste de ses dernieres games ranked
# troisieme requete pour avoir les détails de son match, dedans ya le nombre de kills et de morts
load_dotenv()

bot = discord.Client(intents=discord.Intents.all())

# @bot.event
# async def on_ready():
#     print(f"Connecté en tant que {bot.user}")
#     channel = bot.get_channel(1387849860748939408)
#     if channel:
#         await channel.send("^^")
#     else:
#         print("Canal introuvable.")


# Charger le .env


# je récupère  la clé API depuis les variables d'environnement d'un fichier .env car apparament
# cest plus sécurisé
api_key = os.getenv("RIOT_API_KEY")

# créer le header pour la requête url
headers = { 'X-Riot-Token': api_key }


#définit une fonction qui vérifie la validité de ma clé api riot
dictionnaire_joueur= {"Teo" : ["Ekkotton%20picker","EKKO"], "Matmixels" : ["matmixels","EUW"], "Demignis":  ["Demignis","EUW",] ,"djulo" : ["L9 DJULO","EUW"],"william":["Prout2Rue","PET"] , "Zbarbesss" : ["CalPass","EUW"] , "Zbarbesss" :["EHPAD Fiora","clown"], "Daiki" : ["Daiki","4529"], "Marstonks" : ["Gougnafier","Drive"],"Louis": ["AHAHHAHAHAHAHAHA","GOLRI"]}
def verifier_clef_api():
    test_url = 'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Ekkotton%20picker/EKKO'

    try:
        response = requests.get(test_url, headers=headers)
        if response.status_code == 200:
            print("clé API valide")
            return True
        elif response.status_code == 401:
            print(" clé API invalide ou expirée, aller en chercher une nouvelle et la metrtre dans le .env ")
            webbrowser.open("https://developer.riotgames.com/")
            return False
        else:
            print(f"erreur autre qui est {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"erreur réseau  {e}")
        return False

if not verifier_clef_api():
    sys.exit(1)  # arrête le script si clé invalide


async def stalking(joueur):
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            liste_ragebait= ["🚨🚨🚨\n Nouvelle Masterclass de {joueur} \n sublime kda de {kills_cible}/ {death_cible} sur {nom_champ}",
                             "@{joueur} \n ba alors mon cochon tu penses qu'on a pas vu ton {kills_cible}/ {death_cible} sur {nom_champ}?",
                            "xddddd fin le  {kills_cible}/ {death_cible} de @{joueur} sur {nom_champ} est ridicule",
                            "@{joueur} bien joué pour ton {kills_cible}/ {death_cible} sur {nom_champ} ig ^^"]
                            
            heure_actuelle = datetime.now().strftime("%H:%M:%S")
            liste_endpoints = [
                'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{nom}/{hashtag}',
                'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids',
                'https://europe.api.riotgames.com/lol/match/v5/matches/{matchId}'
            ]
            #cette partie envoie une requete pour avoir le puuid du joueur
            url = liste_endpoints[0]\
                .replace("{nom}", dictionnaire_joueur[joueur][0])\
                .replace("{hashtag}", dictionnaire_joueur[joueur][1])
            response = requests.get(url, headers=headers)

            data = response.json()
            puuid = data["puuid"]
            await asyncio.sleep(2)

        #cett partie recois une liste des 20 dernieres games de la cible et les met dans liste_games
            url2 = liste_endpoints[1].replace("{puuid}", puuid)
            response_liste_game = requests.get(url2, headers=headers)
            liste_games = response_liste_game.json()
            await asyncio.sleep(2)



        #cette partie s'occupe de la logique, si les parties recues sont nouvelles, alors on les analyse,
        # sinn on les analyse pas pour eviter les doublons de notifications
            liste_nouvelle_games = []
            chemin_fichier = os.path.join("bot_discord_surveillance", f"base_de_donnees{joueur}")
            if not os.path.exists(chemin_fichier):
                open(chemin_fichier, "w").close()

            with open(chemin_fichier, "r") as fichier:
                contenu = fichier.read().splitlines()  

            for x in liste_games:
                if x not in contenu:
                    liste_nouvelle_games.append(x)
                

            if len(liste_nouvelle_games)== 0:
                print(f"{heure_actuelle} --- > pas de nouvelle game de {joueur}")
            else:
                for x in liste_nouvelle_games:
                
                #on charge le detail de la game dans data_game et on en extrait les morts et les kills
                    url3 = liste_endpoints[2].replace("{matchId}",x )
                    response_details_game = requests.get(url3, headers=headers)
                    data_game = response_details_game.json()

                    for i in range(len(data_game["info"]["participants"])):
                        if(data_game["info"]["participants"][i]["puuid"] == puuid):
                            index_cible = i
                            break
                    nom_champ= data_game["info"]["participants"][index_cible]["championName"]
                    death_cible= data_game["info"]["participants"][index_cible]["deaths"]
                    kills_cible= data_game["info"]["participants"][index_cible]["kills"]

                    if joueur == "Louis" and kills_cible - death_cible >= 5:
                        channel = bot.get_channel(1387849860748939408)
                        await channel.send(f"wtf Louis \n game de fou sur {nom_champ} \n felicitations")
                        print(f"notification envoyée ^^ -> {joueur}")

                    elif death_cible - kills_cible >= 5:
                        channel = bot.get_channel(1387849860748939408)
                        taunt_choisi = liste_ragebait[random.randint(0,3)]\
                            .replace("{joueur}", joueur)\
                            .replace("{kills_cible}", str(kills_cible))\
                            .replace("{death_cible}", str(death_cible) )\
                            .replace("{nom_champ}",nom_champ)

                        await channel.send(f"{taunt_choisi}")
                        print(f"notification envoyée ^^ pour {joueur}")
                    else :
                        print(f"{heure_actuelle} ---> game tout a fait correcte de {joueur}")

                
            # on finit pas ecrire ces games dans la base de donnees pour ne pas prendre en compte 
            # ces games dans la prochaine execution
                with open(chemin_fichier,"a") as fichier:
                    for x in liste_nouvelle_games:
                        fichier.write(x + "\n")
            
            
            await asyncio.sleep(300)
        except Exception as e:
            print(f"Erreur lors du stalking de {joueur}: {e}")
            await asyncio.sleep(120)


@bot.event
async def on_ready():
    for joueur in dictionnaire_joueur.keys():
        bot.loop.create_task(stalking(joueur))  # lance la logique en tâche asynchrone


bot.run(os.getenv("DISCORD_BOT_KEY"))
    


