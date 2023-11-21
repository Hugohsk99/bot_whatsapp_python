from flask import Flask, request, render_template
from flask_socketio import SocketIO
import requests
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import wikipediaapi
import randfacts
import qrcode
from io import BytesIO
import base64
import os

# Configuração do Twilio
account_sid = os.getenv('ACca6846c8dc72fc593bf4e8f2a3820b5a', '9f29b25b71634a1507f1e519ced8aa77')
auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'seu_auth_token')
twilio_number = 'whatsapp:+18502132818'

# Inicialização do cliente Twilio
twilio_client = Client(account_sid, auth_token)

app = Flask(__nome__, static_folder='static', template_folder='templates')
socketio = SocketIO(app)
def gerar_qrcode_para_whatsapp():
    dados_twilio = 'https://wa.me/14155238886?text=Converse:TwilioLink'

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(dados_twilio)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffered = BytesIO()
    img.save(buffered)
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()

    return f"data:image/png;base64,{qr_code_base64}"


@app.route("/")
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    qr_code_image = gerar_qrcode_para_whatsapp()
    socketio.emit('qr', {'src': qr_code_image})


@app.route("/sms", methods=["POST"])
def sms():
    msgEnviada = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

#Respostas do chat
    if 'Bom dia' in msgEnviada:
        msg.body('Bom dia..\nTudo bem?..')

    elif 'Boa tarde' in msgEnviada:

        msg.body('Boa tarde..')

    elif 'Boa noite' in msgEnviada:

        msg.body('Boa noite!..\nComo foi seu dia?')

    elif 'fine' in msgEnviada:
        msg.body('Nice to hear that..\nWhat can I do for you master?')

    elif 'Quem te vez' in msgEnviada:
        msg.body('Hugo Santana')

    elif '#piada' in msgEnviada:
        url = ''
        r = requests.get(url)
        rj = r.json()
        try:
            for piada in rj:
                setup = piada['setup']
                punch = piada['punchline']
                msg.body(f'{setup}\n{punch}')
        except:
            msg.body('Desculpe.. Não encontrei nenhuma piada!!')

    elif '#news' in msgEnviada:
        #! Função de noticias
        url = 'http://newsapi.org/v2/top-headlines?country=in&apiKey=<Your Api Key>'
        r = requests.get(url)
        rj = r.json()
        try:
            articles = rj['articles']
            for news in articles[:5]:
                titulo = news['titulo']
                link = news['url']
                msg.body(f"\ntitulo: {titulo}\n{link}\n")
        except:
            msg.body('Desculpe.. Não encontrei notícias!!')

    elif '#fact' in msgEnviada:
        #!Fatos interessantes
        try:
            facts = randfacts.getFact()
            msg.body(facts)
        except:
            msg.body('Sorry.. No Facts Found!!')

    elif '#coronastats' in msgEnviada:
        #!Situação da covid
        url = 'https://https://covid.saude.gov.br/'
        r = requests.get(url)
        rj = r.json()
        try:
            totaldecasos = rj['cases']
            totalRecovered = rj['recovered']
            totalDeaths = rj['deaths']
            active = rj['active']
            critical = rj['critical']
            todaysCases = rj['todayCases']
            todaysDeaths = rj['todayDeaths']
            msg.body(f"A situação da covid-19 no Brasil:\n\nTotal Cases: {totaldecasos}\nTotal recuperado: {totalRecovered}\nTotal Deaths: {totalDeaths}\nActive Cases: {active}\nCritical Cases: {critical}\nNew Cases Today: {todaysCases}\nNew Deaths: {todaysDeaths}\n\nYou can get the latest stats by sending #coronastats")
        except:
            msg.body('Desculpe estou sem informações sobre a covid no momento!.')

    elif "#sinonimo" in msgEnviada:
        #!Sinonimos.
        palavra = msgEnviada.replace('#sinonimo ', '')
        url = f'https://www.dicio.com.br/{palavra}'
        r = requests.get(url)
        sinonimo = []
        rj = r.json()
        try:
            for i in rj:
                s = i['significados']
                for j in s:
                    y = j['denid']
                    for k in y:
                        try:
                            n = k['sinonimos']
                            for syn in n:
                                sinonimo.append(syn)
                        except:
                            pass
        except:
            sinonimo.append('Desculpe...Palavra não encontrada!')

        msg.body('sinonimos: \n\n')
        for mean in sinonimo[:10]:
            msg.body(mean + ', ')

    elif '#significado' in msgEnviada:
        #! Significados.
        palavra = msgEnviada.replace('#significado ', '')
        url = f'https://www.dicio.com.br/{palavra}'

        Exemplos = []
        defs = []
        try:
            r = requests.get(url)
            rj = r.json()

            for data in rj:
                significado = data['significados']
                for data1 in significado:
                    denid = data1['denid']
                    for data2 in denid:
                        # print(data2)
                        definition = data2['definition']
                        defs.append(definition)
                        try:

                            example = data2['example']
                            Exemplos.append(example)
                        except:
                            pass
            msg.body('*significado:*\n')
            for i in defs:
                msg.body(i + ',\n')
            msg.body('*Exemplos:*\n')
            for j in Exemplos:
                msg.body(j + ', ')
        except:
            msg.body('Sorry.. No palavras Found!!')

    elif '#book' in msgEnviada:
        #! Detalhes de livro
        nome = msgEnviada.replace('#book ', '')
        url = f'https://books.google.com.br/q={nome}'
        r = requests.get(url)
        try:
            rj = r.json()
            top = rj['items']
            vinfo = []
            for i in top:
                for j in i:
                    if(j=='volumeInfo'):
                        vinfo.append(i[j])
            titulo = []
            sub = []
            autor = []
            avalicao = []
            public = []
            buylink = []

            for i in vinfo:
                for j in i:
                    try:
                        if j == 'titulo':
                            titulo.append(i[j])
                        elif j == 'sub':
                            sub.append(i[j])
                        elif j == 'autores':
                            autor.append(i[j])
                        elif j == 'avalicao':
                            avalicao.append(i[j])
                        elif j == 'public':
                            public.append(i[j])
                        elif j =='canonicalVolumeLink':
                            buylink.append(i[j])
                    except:
                        if j == 'titulo':
                            titulo.append(i[j])
                        elif j == 'autores':
                            autor.append(i[j])
                        elif j == 'avalicao':
                            avalicao.append(i[j])
                        elif j == 'public':
                            public.append(i[j])
                        elif j =='canonicalVolumeLink':
                            buylink.append(i[j])

            try:
                msg.body(f"titulo: {titulo[0]}\nsub: {sub[0]}\nautor: {autor[0][0]}\nRating: {avalicao[0]}\npublic: {public[0]}\n\n{buylink[0]}")
            except:
                msg.body(f"titulo: {titulo[0]}\nautor: {autor[0][0]}Rating: {avalicao[0]}\npublic: {public[0]}\n\n{buylink[0]}")
        except:
            msg.body(f"Desculpe...não encontrei o livro {nome}..\nTente outro livro.")



    elif '#filme' in msgEnviada:
        nome = msgEnviada.replace('#filme ', '')
        ids = []
        try:
            try:
                url = f'https://play.google.com/store/movies?hl=pt_BR&gl=US&pli=1={nome}'
                r = requests.get(url)
                rj = r.json()
                pesquisar = rj['pesquisar']
                for data in pesquisar:
                    ID = data['imdbID']
                    ids.append(ID)
            except:
                url = f'https://play.google.com/store/movies?hl=pt_BR&gl=US&pli=1/{nome}'
                r = requests.get(url)
                rj = r.json()
                results = rj['results']
                for data in results:
                    ID = data['id']
                    ids.append(ID)
            iD = ids[0]

            url2 = f'https://play.google.com/store/movies?hl=pt_BR&gl=US&pli=1{iD}&apikey=<Your Api Key>'
            req = requests.get(url2)
            rjson = req.json()
            titulo = rjson['titulo']
            year = rjson['Year']
            release = rjson['Released']
            rtime = rjson['Runtime']
            actor = rjson['Actors']
            lang = rjson['Language']
            rating = rjson['imdavalicao']
            genre = rjson['Genre']
            poster = rjson['Poster']

            msg.body(f'Informações do filme:\n\ntitulo: {titulo}({year})\nLançamento: {release}\nAvaliação: {rating}\nTempo: {rtime}\nLanguage: {lang}\nGenero: {genre}\nAtores: {actor}\n\nPostagem:\n{poster}')
        except:
            msg.body(f"Não encontrei o filme {nome}")


    elif '#tempo' in msgEnviada:
        #! Reporte do tempo
        city_nome = msgEnviada.replace('#tempo ', '')
        r = requests.get(f'https://api.opentempomap.org/data/2.5/tempo?q={city_nome}&appid=<Your Api Key>&units=metric')
        try:
            data = r.json()
            nome = data['nome']
            sensacao = data['main']['sensacao']
            humidity = data['main']['humidity']
            latitude = data['coord']['lat']
            longitude = data['coord']['lon']
            country = data['sys']['country']
            temp = data['main']['temp']
            wind_speed = data['wind']['speed']
            msg.body(f"Nome da cidade: {nome} - {country}\nLongitude: {longitude}°\nLatitude: {latitude}°\nSensação: {sensacao}°C\nTemperature: {temp}°C\nHumidade: {humidity}%\nVentos Há: {wind_speed}m/s")
        except:
            titulonome = city_nome.titulo()
            msg.body(f"Desculpe... não encontrei nada *{titulonome}*..\nDigite o  Nome da cidade..\n*#tempo*")

    elif '#wiki' in msgEnviada:
        #! Wikepedia busca
        query = msgEnviada.replace('#wiki ', '')
        wiki = wikipediaapi.Wikipedia('en')
        try:
            page = wiki.page(query)
            url = page.fullurl
            summary = page.summary[0:1500]
            msg.body(f'De acordo com o Wikipedia..\n\n{summary}...\n{url}')
        except:
            msg.body("Desculpe não encontrei nada.\nTente outra pesquisar..")

    elif '#citacao' in msgEnviada:
        #! citacoes
        r = requests.get('http://api.quotable.io/random')
        if r.status_code == 200:
            data = r.json()
            citacao = f'{data["content"]} ({data["autor"]})'
        else:
            citacao = 'Desculpe não consegui entender o conteúdo.'
        msg.body(citacao)

    else:
        msg.body("Desculpe não encontrei nada..\n try later")

    return str(resp)


if __nome__ == "__main__":
   socketio.run(app)



