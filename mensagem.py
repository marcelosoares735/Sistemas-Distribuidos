import json

# classe com a padronização das mensagens json
class Mensagem:
	
	def __init__(self):
		self.lista = []
	
	# adiciona mensagem na lista
	# de espera (além de separar)
	# mensagens que se concatenaram
	# critical TODO
	def add(self,next,jsn):
		c = 0
		msg = ""
		for i in jsn :
			if i == '{' : c = c + 1
			if i == '}' :
				c = c - 1
				if c == 0 : msg = msg + i
			if c > 0 : msg = msg + i
			else :
				if self.isValid(msg) :
					self.lista.append([next,msg])
					msg = ""
	
	# mensagem de login
	def login(self,client,senha=""):
		x = {
			"id" : "1" ,
			"ip" : 	client.host,
			"porta" : str(client.port),
			"nome" : client.nome
		#  "senha": senha
		}
		return json.dumps(x)
	
	# mensagem de logout
	def logout(self,client):
		x = {
			"id" : "0" ,
			"ip" : 	client.host,
			"porta" : str(client.port),
			"nome" : client.nome
		}
		return json.dumps(x)
	
	# mensagem de confirmação
	def confirm(self,act,res = 1):
		x = {
			"id" : "2" ,
			"acao" :str(act),
			"res": str(res) 
		}
		return json.dumps(x)

	# mensagem de chat
	def chatMsg(self, nomeReceb, nomeEnvi, msg):
		x = {
			"id" : "3",
			"nomeenv" : nomeEnvi,
			"nomereceb": nomeReceb,
			"msg" : str(msg)
		}
		print("zxcc")
		return json.dumps(x)

	def isMsg(self, jsn):
		if self.getInJson(jsn, "id") == "3":
			return True
		return False


	# verifica se o json pode ser convertido
	def isValid(self,jsn):
		x = True
		try: json.loads(jsn)
		except: x = False
		return x
	
	# obtém um campo dentro do json
	def getInJson(self,jsn,campo):
		try: x = json.loads(jsn)
		except: return -1
		try: x = x[campo]
		except: return -1
		return x
	
	# verifica se é json de login
	def isLogin(self,jsn):
		if self.getInJson(jsn,"id") == "1" :
			return True
		return False	
	
	# verifica se é json de logout
	def isLogout(self,jsn):
		if self.getInJson(jsn,"id") == "0" :
			return True
		return False	
	
	# verifica se é json de confirmação
	def isConfirm(self,jsn):
		if self.getInJson(jsn,"id") == "2" :
			return True
		return False	

	
	# verifica se o json é de login ok
	def confLogin(self,jsn):
		x = self.isConfirm(jsn)
		x = x and (self.getInJson(jsn,"acao") == "1")
		x = x and (self.getInJson(jsn,"res") == "1")
		return x
	
	# verifica se o json é de login fail
	def confLogout(self,jsn):
		x = self.isConfirm(jsn)
		x = x and (self.getInJson(jsn,"acao") == "0")
		x = x and (self.getInJson(jsn,"res") == "1")
		return x
